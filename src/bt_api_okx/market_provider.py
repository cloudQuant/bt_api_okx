"""Provider-neutral owner-thread adapter for the existing OKX ticker stream."""

from __future__ import annotations

import math
import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from bt_api_base.market_protocol import MarketProviderEvent, MarketSubscriptionKey

from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.environment import configure_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap

DEFAULT_OKX_TICKER_QUEUE_CAPACITY = 1_024
MAX_OKX_TICKER_QUEUE_CAPACITY = 65_536
MAX_OKX_PROVIDER_POLL_LIMIT = 256
_OKX_SOURCE_REF = "okx-public-market-r1"
_OKX_ENTITLEMENT_REF = "public-ticker-r1"


class BoundedOkxTickerQueue:
    """Thread-safe nonblocking sink compatible with the OKX WSS ``put`` call."""

    def __init__(self, capacity: int = DEFAULT_OKX_TICKER_QUEUE_CAPACITY) -> None:
        if type(capacity) is not int or not 1 <= capacity <= MAX_OKX_TICKER_QUEUE_CAPACITY:
            raise ValueError("INVALID_OKX_TICKER_QUEUE_CAPACITY")
        self._capacity = capacity
        self._items: deque[object] = deque()
        self._lock = threading.Lock()
        self._dropped_oldest = 0

    @property
    def dropped_oldest(self) -> int:
        with self._lock:
            return self._dropped_oldest

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._items)

    def put(self, item: object, block: bool = True, timeout: Optional[float] = None) -> None:
        """Append without waiting; discard the oldest ticker at capacity."""
        del block, timeout
        with self._lock:
            if len(self._items) == self._capacity:
                self._items.popleft()
                self._dropped_oldest += 1
            self._items.append(item)

    def drain(self, limit: int) -> tuple[object, ...]:
        if type(limit) is not int or not 1 <= limit <= MAX_OKX_PROVIDER_POLL_LIMIT:
            raise ValueError("INVALID_OKX_PROVIDER_POLL_LIMIT")
        with self._lock:
            count = min(limit, len(self._items))
            return tuple(self._items.popleft() for _ in range(count))

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


@dataclass
class OkxTickerMarketHandle:
    """One acquired WSS stream, its bounded callback queue and Hub generation."""

    key: MarketSubscriptionKey
    generation: str
    queue: BoundedOkxTickerQueue
    stream: object
    active: bool = True


def _build_default_swap_stream(
    key: MarketSubscriptionKey, ticker_queue: BoundedOkxTickerQueue
) -> object:
    """Construct, but do not start, the existing public OKX SWAP ticker feed."""
    from bt_api_okx.feeds.live_okx.swap import OkxMarketWssDataSwap

    params = configure_environment(OkxExchangeDataSwap(), {"environment": "production"})
    return OkxMarketWssDataSwap(
        ticker_queue,
        exchange_data=params,
        wss_url=params.wss_url,
        topics=[{"topic": "ticker", "symbol": key.instrument.native_symbol}],
        asset_type="SWAP",
        stream_role="market",
        wss_name="service_okx_swap_ticker",
    )


class OkxTickerQueueMarketProvider:
    """Adapt the existing OKX ticker WebSocket feed to the Hub provider port.

    The optional factory constructs a stream around the supplied queue but must
    not start it. This class owns start/stop and only returns a handle after the
    stream reports ready. If startup cleanup is uncertain, the exact stream is
    retained internally and every later acquisition first retries its stop.
    """

    def __init__(
        self,
        *,
        stream_factory: Optional[Callable[[MarketSubscriptionKey, BoundedOkxTickerQueue], object]] = None,
        queue_capacity: int = DEFAULT_OKX_TICKER_QUEUE_CAPACITY,
        connect_timeout: float = 30.0,
    ) -> None:
        if type(queue_capacity) is not int or not 1 <= queue_capacity <= MAX_OKX_TICKER_QUEUE_CAPACITY:
            raise ValueError("INVALID_OKX_TICKER_QUEUE_CAPACITY")
        if isinstance(connect_timeout, bool) or not isinstance(connect_timeout, (int, float)):
            raise ValueError("INVALID_OKX_CONNECT_TIMEOUT")
        normalized_timeout = float(connect_timeout)
        if not math.isfinite(normalized_timeout) or normalized_timeout < 0:
            raise ValueError("INVALID_OKX_CONNECT_TIMEOUT")
        if stream_factory is not None and not callable(stream_factory):
            raise ValueError("INVALID_OKX_STREAM_FACTORY")
        self._stream_factory = stream_factory or _build_default_swap_stream
        self._queue_capacity = queue_capacity
        self._connect_timeout = normalized_timeout
        self._pending_start_cleanup: list[object] = []
        self._invalid_ticker_events = 0

    @property
    def diagnostics(self) -> dict[str, int]:
        return {
            "pending_start_cleanup": len(self._pending_start_cleanup),
            "invalid_ticker_events": self._invalid_ticker_events,
        }

    def subscribe(self, key: MarketSubscriptionKey, *, generation: str) -> OkxTickerMarketHandle:
        _validate_supported_key(key)
        if type(generation) is not str or not generation.strip():
            raise ValueError("INVALID_SOURCE_GENERATION")
        self._retry_pending_start_cleanup()
        ticker_queue = BoundedOkxTickerQueue(self._queue_capacity)
        stream = self._stream_factory(key, ticker_queue)
        start = getattr(stream, "start", None)
        stop = getattr(stream, "stop", None)
        if not callable(start) or not callable(stop):
            raise TypeError("OKX stream factory must return a startable and stoppable stream")
        try:
            start(connect_timeout=self._connect_timeout)
        except Exception:
            try:
                stopped = stop()
            except Exception:
                stopped = False
            if stopped is False:
                self._pending_start_cleanup.append(stream)
            raise
        return OkxTickerMarketHandle(key, generation, ticker_queue, stream)

    def unsubscribe(self, handle: object) -> bool:
        if type(handle) is not OkxTickerMarketHandle:
            return False
        if not handle.active:
            return True
        try:
            stopped = handle.stream.stop()
        except Exception:
            return False
        if stopped is False:
            return False
        handle.active = False
        handle.queue.clear()
        return True

    def poll(
        self, handle: object, *, limit: int
    ) -> tuple[MarketProviderEvent, ...]:
        if type(handle) is not OkxTickerMarketHandle or not handle.active:
            return ()
        raw_items = handle.queue.drain(limit)
        events = []
        for raw_item in raw_items:
            if not isinstance(raw_item, OkxTickerData):
                self._invalid_ticker_events += 1
                raise ValueError("INVALID_OKX_TICKER_EVENT")
            projection = raw_item.get_market_projection()
            if (
                projection.get("exchange_name") != "OKX"
                or projection.get("asset_type") != "SWAP"
                or projection.get("symbol") != handle.key.instrument.native_symbol
                or projection.get("instrument_id") != handle.key.instrument.instrument_id
            ):
                self._invalid_ticker_events += 1
                raise ValueError("OKX_TICKER_KEY_MISMATCH")
            timestamp = projection.get("timestamp")
            if (
                isinstance(timestamp, bool)
                or not isinstance(timestamp, (int, float))
                or not math.isfinite(float(timestamp))
            ):
                self._invalid_ticker_events += 1
                raise ValueError("INVALID_OKX_TICKER_TIMESTAMP")
            try:
                observed_at_utc = (
                    datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
                    .isoformat(timespec="microseconds")
                    .replace("+00:00", "Z")
                )
            except (OverflowError, OSError, ValueError):
                self._invalid_ticker_events += 1
                raise ValueError("INVALID_OKX_TICKER_TIMESTAMP") from None
            events.append(
                MarketProviderEvent(
                    generation=handle.generation,
                    observed_at_utc=observed_at_utc,
                    data=projection,
                )
            )
        return tuple(events)

    def _retry_pending_start_cleanup(self) -> None:
        pending: list[object] = []
        for stream in self._pending_start_cleanup:
            try:
                stopped = stream.stop()
            except Exception:
                stopped = False
            if stopped is False:
                pending.append(stream)
        self._pending_start_cleanup = pending
        if pending:
            raise RuntimeError("OKX_STARTUP_CLEANUP_PENDING")


def _validate_supported_key(key: MarketSubscriptionKey) -> None:
    if type(key) is not MarketSubscriptionKey:
        raise TypeError("INVALID_OKX_MARKET_KEY")
    instrument = key.instrument
    if (
        key.source_ref != _OKX_SOURCE_REF
        or key.entitlement_ref != _OKX_ENTITLEMENT_REF
        or instrument.provider != "okx"
        or instrument.venue != "OKX"
        or instrument.environment != "live"
        or instrument.product_type != "SWAP"
        or key.channel != "tickers"
        or key.depth is not None
        or key.timeframe is not None
    ):
        raise ValueError("UNSUPPORTED_OKX_MARKET_KEY")


__all__ = [
    "BoundedOkxTickerQueue",
    "OkxTickerMarketHandle",
    "OkxTickerQueueMarketProvider",
]
