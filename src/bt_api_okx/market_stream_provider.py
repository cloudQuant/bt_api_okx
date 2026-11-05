"""Unified neutral market-stream provider backed by the OKX public WSS.

The provider owns one WSS connection for the exact selected OKX SWAP route
and instrument. Iteration 62 advertises the ``tick`` channel (public
``tickers`` push, see :mod:`bt_api_okx.market_tick_stream`). The ``orderbook``
session below stays implemented but unadvertised: OKX's existing depth
callback validates ``seqId`` / ``prevSeqId`` and a CRC32 checksum that the
current books-l2-tbt channel no longer provides. Neither channel qualifies
clock quality or freshness.
"""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from bt_api_base.market_orderbook_protocol import MarketOrderBookEvent, MarketOrderBookLevel
from bt_api_base.market_protocol import (
    MarketInstrumentKey,
    MarketSourceDescriptor,
    MarketSubscriptionKey,
)
from bt_api_base.market_stream_provider_protocol import (
    MarketStreamChannelCapability,
    MarketStreamProviderBinding,
    MarketStreamProviderChannelBinding,
    MarketStreamProviderContractError,
    MarketStreamProviderRegistryPort,
    SelectedMarketStreamRoute,
)
from bt_api_base.market_stream_protocol import MarketStreamEvent, MarketStreamRequest
from bt_api_base.market_tick_protocol import (
    DataClockBinding,
    MarketClockQuality,
    MarketEventCursor,
    MarketFreshnessStatus,
)

from bt_api_okx.environment import configure_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap
from bt_api_okx.feeds.live_okx.swap import OkxMarketWssDataSwap, OkxRequestDataSwap
from bt_api_base.containers.auto_init_mixin import container_class
from bt_api_okx.containers.orderbooks.okx_l2_orderbook import OkxL2OrderBookData


OKX_MARKET_STREAM_EXCHANGE = "OKX___SWAP"
OKX_ORDERBOOK_MAX_DEPTH = 400
OKX_PUBLIC_ORDERBOOK_SOURCE_REF = "okx-public-orderbook-v1"
OKX_PUBLIC_ORDERBOOK_ENTITLEMENT_REF = "okx-public-market-data"
_OKX_SOURCE = "okx-public-wss-v5-books-l2-tbt"
_OKX_CLOCK_DOMAIN = "unix-epoch-milliseconds-utc"
_OKX_CLOCK_SOURCE = "okx-reported-ts"
_OKX_CONNECT_TIMEOUT_SECONDS = 30.0
_OKX_RESYNC_TIMEOUT_SECONDS = 30.0
_MAX_PROVIDER_BATCH = 4096
_MAX_QUEUE_CAPACITY = 65536


@dataclass(frozen=True)
class _IngressRecord:
    """One callback item tagged with its actual WSS open generation."""

    kind: str
    connection_generation: int
    value: object | None = None
    # Wall-clock / monotonic nanoseconds when the WSS frame was received.
    received_ns: int | None = None
    received_monotonic_ns: int | None = None


class _BoundedOkxIngressQueue:
    """Bounded WSS callback sink that records generation at callback ingress."""

    def __init__(self, capacity: int, wake_callback: Callable[[], None]) -> None:
        if (
            type(capacity) is not int
            or not 1 <= capacity <= _MAX_QUEUE_CAPACITY
            or not callable(wake_callback)
        ):
            raise ValueError("INVALID_OKX_MARKET_STREAM_QUEUE_CAPACITY")
        self._capacity = capacity
        self._wake_callback = wake_callback
        self._stream: _OwnedOkxMarketWssDataSwap | None = None
        self._items: deque[_IngressRecord] = deque()
        self._condition = threading.Condition()
        self._overflowed = False
        self._wake_failed = False

    def bind_stream(self, stream: "_OwnedOkxMarketWssDataSwap") -> None:
        if self._stream is not None or type(stream) is not _OwnedOkxMarketWssDataSwap:
            raise ValueError("INVALID_OKX_MARKET_STREAM_BINDING")
        self._stream = stream

    def put(self, value: object, block: bool = True, timeout: float | None = None) -> None:
        del block, timeout
        stream = self._stream
        generation = getattr(stream, "_connection_generation", 0)
        if type(generation) is not int or generation <= 0:
            with self._condition:
                self._overflowed = True
                self._condition.notify_all()
            try:
                self._wake_callback()
            except Exception:
                with self._condition:
                    self._wake_failed = True
                    self._condition.notify_all()
            return
        receipt = getattr(stream, "_message_receipt", None)
        if type(receipt) is tuple and len(receipt) == 2:
            self._append(_IngressRecord("data", generation, value, receipt[0], receipt[1]))
        else:
            self._append(_IngressRecord("data", generation, value))

    def lifecycle(self, kind: str, generation: int) -> None:
        if kind not in {"opened", "closed"} or type(generation) is not int or generation <= 0:
            return
        self._append(_IngressRecord(kind, generation))

    def _append(self, record: _IngressRecord) -> None:
        with self._condition:
            if len(self._items) >= self._capacity:
                # A missing delta makes the current book unusable. Do not
                # overwrite old events or silently continue the sequence.
                self._overflowed = True
                self._condition.notify_all()
            else:
                self._items.append(record)
                self._condition.notify_all()
        try:
            self._wake_callback()
        except Exception:
            # Surface a failed waiter notification as recovery-required on
            # the next bounded poll without escaping into the WSS callback.
            with self._condition:
                self._wake_failed = True
                self._condition.notify_all()

    def take(self, *, timeout: float) -> tuple[_IngressRecord | None, bool]:
        with self._condition:
            if not self._items and not self._overflowed and timeout > 0:
                self._condition.wait(timeout)
            overflowed = self._overflowed or self._wake_failed
            self._overflowed = False
            self._wake_failed = False
            if overflowed:
                self._items.clear()
                return None, True
            if not self._items:
                return None, False
            return self._items.popleft(), False

    def drain(self, limit: int) -> tuple[tuple[_IngressRecord, ...], bool]:
        with self._condition:
            overflowed = self._overflowed or self._wake_failed
            self._overflowed = False
            self._wake_failed = False
            if overflowed:
                self._items.clear()
                return (), True
            count = min(limit, len(self._items))
            return tuple(self._items.popleft() for _ in range(count)), False


class _OwnedOkxMarketWssDataSwap(OkxMarketWssDataSwap):
    """Existing OKX WSS depth processor with bounded lifecycle receipts."""

    def on_message(self, ws: Any, message: Any) -> None:
        # Receipt time of the frame, before parsing; read by the ingress queue
        # on this same WSS callback thread.
        self._message_receipt = (time.time_ns(), time.monotonic_ns())
        super().on_message(ws, message)

    def push_market_trades(self, content: Any) -> None:
        # Hand the rows of one push over in tradeId order, so trade-id
        # continuity is judged in venue order.
        data = content.get("data") if isinstance(content, dict) else None
        if isinstance(data, list) and all(
            isinstance(row, dict) and str(row.get("tradeId", "")).isdigit() for row in data
        ):
            content = dict(content, data=sorted(data, key=lambda row: int(row["tradeId"])))
        super().push_market_trades(content)

    def on_open(self, ws: Any) -> None:
        super().on_open(ws)
        queue = self.data_queue
        if type(queue) is _BoundedOkxIngressQueue:
            queue.lifecycle("opened", self._connection_generation)

    def on_close(self, ws: Any, status_code: Any, close_message: Any) -> None:
        generation = self._connection_generation
        super().on_close(ws, status_code, close_message)
        queue = self.data_queue
        if type(queue) is _BoundedOkxIngressQueue:
            queue.lifecycle("closed", generation)


@dataclass(frozen=True)
class _BookState:
    connection_generation: int
    provider_sequence: int
    provider_previous_sequence: int | None
    snapshot_or_delta: str
    continuity_status: str
    bids: tuple[MarketOrderBookLevel, ...]
    asks: tuple[MarketOrderBookLevel, ...]
    provider_event_time_utc: str | None
    received_at_utc: str | None
    received_monotonic_ns: int | None


@dataclass
class _ChannelState:
    binding: MarketStreamProviderChannelBinding
    cursor_sequence: int
    latest_book: _BookState
    recovery_required: bool = False
    stale_emitted: bool = False


class OkxMarketStreamAdapter:
    """Pure route-bound adapter for the existing OKX SWAP Feed object."""

    def __init__(self, route: SelectedMarketStreamRoute) -> None:
        if type(route) is not SelectedMarketStreamRoute:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID")
        _validate_route(route)
        self._route = route

    def capabilities(self) -> tuple[MarketStreamChannelCapability, ...]:
        """Declare the public ``tickers`` tick channel only (no I/O).

        ``orderbook`` stays unadvertised: current OKX public guidance fixes the
        books-l2-tbt checksum to zero and requires seqId/prevSeqId continuity,
        while the inherited WSS depth validator still compares that zero with
        a CRC32 checksum. It returns once the separately accepted repair lands.
        """
        return (MarketStreamChannelCapability(channel="tick", max_depth=None),)

    def open_session(
        self,
        *,
        wake_callback: Callable[[], None],
    ) -> Any:
        """Create an unstarted tick session shell; the first subscribe starts WSS."""
        from bt_api_okx.market_tick_stream import OkxTickMarketStreamSession

        if not callable(wake_callback):
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
        return OkxTickMarketStreamSession(self._route, wake_callback=wake_callback)


class OkxMarketStreamSession:
    """One WSS owner multiplexing depth subscriptions for one route/instrument."""

    def __init__(
        self,
        route: SelectedMarketStreamRoute,
        *,
        wake_callback: Callable[[], None],
    ) -> None:
        if type(route) is not SelectedMarketStreamRoute:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID")
        if not callable(wake_callback):
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
        self._route = route
        self._wake_callback = wake_callback
        self._owner_thread = threading.get_ident()
        self._lock = threading.RLock()
        self._queue: _BoundedOkxIngressQueue | None = None
        self._stream: _OwnedOkxMarketWssDataSwap | None = None
        self._states_by_token: dict[object, _ChannelState] = {}
        self._states_by_key: dict[MarketSubscriptionKey, _ChannelState] = {}
        self._pending_events: deque[MarketOrderBookEvent] = deque()
        self._latest_book: _BookState | None = None
        self._closed = False
        self._cleanup_unverified = False
        self._last_ingress_generation = 0
        self._validate_route_current()

    def subscribe(
        self,
        request: MarketStreamRequest,
        /,
    ) -> MarketStreamProviderChannelBinding:
        self._check_owner()
        self._validate_request(request)
        with self._lock:
            if self._closed or self._cleanup_unverified:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
            key = self._key_for(request)
            if key in self._states_by_key:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_BINDING_INVALID")
            self._validate_route_current()
            self._start_if_needed(request.queue_capacity)
            deadline = time.monotonic() + _OKX_CONNECT_TIMEOUT_SECONDS
            while True:
                if self._cleanup_unverified:
                    raise MarketStreamProviderContractError(
                        "MARKET_STREAM_PROVIDER_SESSION_INVALID"
                    )
                latest = self._latest_book
                stream = self._stream
                current_generation = getattr(stream, "_connection_generation", 0)
                if (
                    latest is not None
                    and type(current_generation) is int
                    and current_generation == latest.connection_generation
                    and latest.continuity_status == "snapshot"
                    and getattr(stream, "_running_flag", False) is True
                    and getattr(stream, "_stop_event", None) is not None
                    and not stream._stop_event.is_set()
                ):
                    source = _source_for(key, latest.connection_generation)
                    event = _event_for(
                        key,
                        source,
                        MarketEventCursor(source.stream_id, source.epoch, 1),
                        latest,
                        recovery_snapshot=False,
                    )
                    binding = MarketStreamProviderChannelBinding(
                        token=object(),
                        request=request,
                        key=key,
                        source=source,
                        initial_cursor=event.cursor,
                        initial_events=(event,),
                        recovery_required=False,
                    )
                    state = _ChannelState(binding, 1, latest)
                    self._states_by_token[binding.token] = state
                    self._states_by_key[key] = state
                    return binding
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise MarketStreamProviderContractError(
                        "MARKET_STREAM_PROVIDER_SESSION_INVALID"
                    )
                self._ingest_one(min(0.1, remaining))

    def poll(
        self,
        *,
        timeout_ms: int,
        max_events: int,
    ) -> tuple[MarketStreamEvent, ...]:
        self._check_owner()
        if (
            type(timeout_ms) is not int
            or not 0 <= timeout_ms <= 60_000
            or type(max_events) is not int
            or not 1 <= max_events <= _MAX_PROVIDER_BATCH
        ):
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_EVENT_INVALID")
        with self._lock:
            if self._closed or self._cleanup_unverified:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
            if not self._states_by_token:
                return ()
            self._validate_route_current()
            self._fill_pending(max_events)
            deadline = time.monotonic() + timeout_ms / 1000.0
            while not self._pending_events and timeout_ms and time.monotonic() < deadline:
                self._ingest_one(max(0.0, deadline - time.monotonic()))
                self._fill_pending(max_events)
            events = tuple(self._pending_events.popleft() for _ in range(min(max_events, len(self._pending_events))))
            return events

    def resync(
        self,
        binding: MarketStreamProviderChannelBinding,
        *,
        acknowledge_data_loss: bool,
    ) -> MarketStreamProviderChannelBinding:
        self._check_owner()
        if type(acknowledge_data_loss) is not bool or acknowledge_data_loss is not True:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        with self._lock:
            state = self._state_for(binding)
            if not state.recovery_required:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_BINDING_INVALID")
            self._validate_route_current()
            old_generation = state.binding.source.connection_generation
            stream = self._stream
            if stream is None:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
            current_generation = getattr(stream, "_connection_generation", 0)
            if type(current_generation) is not int or current_generation <= old_generation:
                self._force_reconnect()

            deadline = time.monotonic() + _OKX_RESYNC_TIMEOUT_SECONDS
            while True:
                latest = self._latest_book
                current_generation = getattr(stream, "_connection_generation", 0)
                if (
                    latest is not None
                    and type(current_generation) is int
                    and latest.connection_generation > old_generation
                    and latest.connection_generation == current_generation
                    and latest.continuity_status == "snapshot"
                    and getattr(stream, "_running_flag", False) is True
                    and not stream._stop_event.is_set()
                ):
                    source = _source_for(state.binding.key, latest.connection_generation)
                    cursor = MarketEventCursor(source.stream_id, source.epoch, 1)
                    event = _event_for(
                        state.binding.key,
                        source,
                        cursor,
                        latest,
                        recovery_snapshot=True,
                        continuity_status="recovered",
                    )
                    new_binding = MarketStreamProviderChannelBinding(
                        token=object(),
                        request=state.binding.request,
                        key=state.binding.key,
                        source=source,
                        initial_cursor=cursor,
                        initial_events=(event,),
                        recovery_required=False,
                    )
                    self._states_by_token.pop(state.binding.token, None)
                    state.binding = new_binding
                    state.cursor_sequence = 1
                    state.latest_book = latest
                    state.recovery_required = False
                    state.stale_emitted = False
                    self._states_by_token[new_binding.token] = state
                    return new_binding
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise MarketStreamProviderContractError(
                        "MARKET_STREAM_PROVIDER_SESSION_INVALID"
                    )
                self._ingest_one(min(0.1, remaining))

    def unsubscribe(self, binding: MarketStreamProviderChannelBinding, /) -> bool:
        self._check_owner()
        with self._lock:
            self._state_for(binding)
            self._states_by_token.pop(binding.token, None)
            self._states_by_key.pop(binding.key, None)
            if self._states_by_token:
                return True
            self._pending_events.clear()
            return self._stop_stream()

    def close(self) -> bool:
        self._check_owner()
        with self._lock:
            if self._closed and not self._cleanup_unverified:
                return True
            self._states_by_token.clear()
            self._states_by_key.clear()
            self._pending_events.clear()
            closed = self._stop_stream()
            if closed:
                self._closed = True
                self._cleanup_unverified = False
            else:
                self._cleanup_unverified = True
            return closed

    def _validate_request(self, request: MarketStreamRequest) -> None:
        if (
            type(request) is not MarketStreamRequest
            or request.exchange_name != self._route.exchange_name
            or request.instrument != self._route.instrument
            or request.channel != "orderbook"
            or type(request.depth) is not int
            or not 1 <= request.depth <= OKX_ORDERBOOK_MAX_DEPTH
        ):
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_CHANNEL_UNAVAILABLE")

    @staticmethod
    def _key_for(request: MarketStreamRequest) -> MarketSubscriptionKey:
        return MarketSubscriptionKey(
            source_ref=OKX_PUBLIC_ORDERBOOK_SOURCE_REF,
            entitlement_ref=OKX_PUBLIC_ORDERBOOK_ENTITLEMENT_REF,
            instrument=request.instrument,
            channel=request.channel,
            depth=request.depth,
            timeframe=None,
        )

    def _start_if_needed(self, queue_capacity: int) -> None:
        if self._stream is not None:
            if self._cleanup_unverified:
                raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")
            return
        try:
            info = self._environment_info()
            params = configure_environment(
                OkxExchangeDataSwap(),
                {"environment": info["environment"], "api_region": info["api_region"]},
            )
            queue = _BoundedOkxIngressQueue(queue_capacity, self._wake_callback)
            stream = _OwnedOkxMarketWssDataSwap(
                queue,
                exchange_data=params,
                environment=info["environment"],
                api_region=info["api_region"],
                wss_url=params.wss_url,
                topics=[
                    {
                        "topic": "books_l2_tbt",
                        "symbol": self._route.instrument.native_symbol,
                    }
                ],
                asset_type="SWAP",
                exchange_name=OKX_MARKET_STREAM_EXCHANGE,
                stream_role="market",
                wss_name="okx_sdk_market_orderbook",
                message_idle_timeout=0.0,
            )
            queue.bind_stream(stream)
            self._queue = queue
            self._stream = stream
            stream.start(connect_timeout=_OKX_CONNECT_TIMEOUT_SECONDS)
            if (
                type(getattr(stream, "_connection_generation", None)) is not int
                or stream._connection_generation <= 0
                or stream._running_flag is not True
                or stream._stop_event.is_set()
            ):
                raise RuntimeError("OKX provider stream did not reach a verified ready state")
        except Exception:
            if self._stream is not None and not self._stop_stream():
                self._cleanup_unverified = True
            raise MarketStreamProviderContractError(
                "MARKET_STREAM_PROVIDER_SESSION_INVALID"
            ) from None

    def _ingest_one(self, timeout_seconds: float) -> None:
        queue = self._queue
        if queue is None:
            return
        record, overflowed = queue.take(timeout=max(0.0, timeout_seconds))
        if overflowed:
            self._mark_all_stale("queue_overflow")
            self._force_reconnect()
            return
        if record is None:
            return
        self._process_record(record)

    def _process_record(self, record: _IngressRecord) -> None:
        if type(record.connection_generation) is not int or record.connection_generation <= 0:
            self._mark_all_stale("connection_changed")
            return
        if record.kind == "opened":
            if record.connection_generation != self._last_ingress_generation:
                if self._last_ingress_generation:
                    self._mark_all_stale("connection_changed")
                self._last_ingress_generation = record.connection_generation
            return
        if record.kind == "closed":
            self._mark_all_stale("disconnected")
            return
        if record.kind != "data":
            self._mark_all_stale("invalid_event")
            return
        raw = record.value
        if isinstance(raw, dict) and raw.get("kind") == "orderbook" and raw.get("stale") is True:
            reason = _finite_stale_reason(raw.get("stale_reason"))
            self._mark_all_stale(reason)
            return
        try:
            # Exact class, also for a published (frozen) container.
            if container_class(raw) is not OkxL2OrderBookData:
                raise ValueError
            book = _project_book_state(raw, record.connection_generation)
        except Exception:
            self._mark_all_stale("invalid_event")
            return
        previous = self._latest_book
        if (
            previous is not None
            and book.connection_generation != previous.connection_generation
            and book.continuity_status != "snapshot"
        ):
            self._mark_all_stale("connection_changed")
            return
        self._latest_book = book
        if book.connection_generation != self._last_ingress_generation:
            if self._last_ingress_generation:
                self._mark_all_stale("connection_changed")
            self._last_ingress_generation = book.connection_generation

        for state in tuple(self._states_by_token.values()):
            if state.recovery_required:
                continue
            if book.connection_generation != state.binding.source.connection_generation:
                self._emit_stale(state, "connection_changed")
                continue
            event = self._normal_event(state, book)
            self._enqueue_event(event)
            state.cursor_sequence = event.cursor.sequence
            state.latest_book = book

    def _normal_event(self, state: _ChannelState, book: _BookState) -> MarketOrderBookEvent:
        sequence = state.cursor_sequence + 1
        cursor = MarketEventCursor(
            state.binding.source.stream_id,
            state.binding.source.epoch,
            sequence,
        )
        return _event_for(
            state.binding.key,
            state.binding.source,
            cursor,
            book,
            recovery_snapshot=False,
            continuity_status="snapshot" if snapshot else "continuous",
        )

    def _emit_stale(self, state: _ChannelState, reason: str) -> None:
        if state.recovery_required:
            return
        state.recovery_required = True
        state.stale_emitted = True
        previous = state.latest_book
        if previous is None:
            return
        cursor = MarketEventCursor(
            state.binding.source.stream_id,
            state.binding.source.epoch,
            state.cursor_sequence + 1,
        )
        event = _event_for(
            state.binding.key,
            state.binding.source,
            cursor,
            previous,
            recovery_snapshot=False,
            continuity_status="disconnected" if reason == "disconnected" else "gap",
            stale=True,
            stale_reason=reason,
        )
        state.cursor_sequence = cursor.sequence
        self._enqueue_event(event)

    def _mark_all_stale(self, reason: str) -> None:
        normalized = _finite_stale_reason(reason)
        for state in tuple(self._states_by_token.values()):
            self._emit_stale(state, normalized)

    def _fill_pending(self, max_events: int) -> None:
        queue = self._queue
        if queue is None:
            return
        records, overflowed = queue.drain(min(max_events, 256))
        if overflowed:
            self._mark_all_stale("queue_overflow")
            self._force_reconnect()
            return
        for record in records:
            self._process_record(record)

    def _enqueue_event(self, event: MarketOrderBookEvent) -> None:
        if len(self._pending_events) >= _MAX_QUEUE_CAPACITY:
            self._pending_events.clear()
            self._mark_all_stale("queue_overflow")
            self._force_reconnect()
            return
        self._pending_events.append(event)

    def _force_reconnect(self) -> None:
        stream = self._stream
        ws = getattr(stream, "ws", None)
        if ws is not None:
            try:
                ws.close()
            except Exception:
                self._cleanup_unverified = True

    def _stop_stream(self) -> bool:
        stream = self._stream
        if stream is None:
            self._closed = True
            return True
        try:
            stream.stop()
        except Exception:
            self._cleanup_unverified = True
            return False
        workers = (
            stream.process,
            stream._restart_process,
            stream._watchdog_process,
            stream._readiness_watchdog_process,
        )
        if (
            any(worker is not None and worker.is_alive() for worker in workers)
            or stream._running_flag is not False
            or not stream._stop_event.is_set()
        ):
            self._cleanup_unverified = True
            return False
        self._stream = None
        self._queue = None
        self._latest_book = None
        self._cleanup_unverified = False
        return True

    def _state_for(self, binding: MarketStreamProviderChannelBinding) -> _ChannelState:
        if type(binding) is not MarketStreamProviderChannelBinding:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        state = self._states_by_token.get(binding.token)
        if state is None or state.binding is not binding:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        return state

    def _validate_route_current(self) -> None:
        _validate_route(self._route)

    def _environment_info(self) -> dict[str, Any]:
        feed = self._route.client
        try:
            info = feed.get_environment_info()
        except Exception:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID") from None
        if (
            type(info) is not dict
            or info.get("verified") is not True
            or info.get("environment") != self._route.environment
            or info.get("api_region") not in {"global", "eea", "us", "tr"}
            or type(info.get("simulated")) is not bool
            or info.get("simulated") != (self._route.environment == "demo")
        ):
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID")
        return info

    def _check_owner(self) -> None:
        if threading.get_ident() != self._owner_thread:
            raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_SESSION_INVALID")


def register_okx_market_stream_provider(
    registry: MarketStreamProviderRegistryPort,
) -> None:
    """Register the exact OKX SWAP market-stream provider route."""
    if not isinstance(registry, MarketStreamProviderRegistryPort):
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ADAPTER_INVALID")
    registry.register(OKX_MARKET_STREAM_EXCHANGE, _create_okx_market_stream_binding)


def _create_okx_market_stream_binding(
    route: SelectedMarketStreamRoute,
) -> MarketStreamProviderBinding:
    adapter = OkxMarketStreamAdapter(route)
    return MarketStreamProviderBinding(instrument=route.instrument, adapter=adapter)


def _validate_route(route: SelectedMarketStreamRoute) -> None:
    instrument = getattr(route, "instrument", None)
    if (
        type(route) is not SelectedMarketStreamRoute
        or route.exchange_name != OKX_MARKET_STREAM_EXCHANGE
        or type(route.client) is not OkxRequestDataSwap
        or route.environment not in {"production", "demo"}
        or type(instrument) is not MarketInstrumentKey
        or instrument.provider != "okx"
        or instrument.venue != "OKX"
        or instrument.environment != route.environment
        or instrument.product_type != "SWAP"
    ):
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID")
    try:
        info = route.client.get_environment_info()
    except Exception:
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID") from None
    if (
        type(info) is not dict
        or info.get("verified") is not True
        or info.get("environment") != route.environment
        or info.get("api_region") not in {"global", "eea", "us", "tr"}
        or type(info.get("simulated")) is not bool
        or info.get("simulated") != (route.environment == "demo")
    ):
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_ROUTE_INVALID")


def _project_book_state(raw: OkxL2OrderBookData, generation: int) -> _BookState:
    if type(generation) is not int or generation <= 0:
        raise ValueError("INVALID_CONNECTION_GENERATION")
    row = getattr(raw, "order_book_data", None)
    # A published (frozen) container holds read-only views: a Mapping row and
    # tuple levels. Both are only read here.
    if not isinstance(row, Mapping):
        raise ValueError("INVALID_ORDERBOOK_ROW")
    provider_sequence = _provider_sequence(row.get("seqId"), positive=True)
    native_action = row.get("native_action")
    if native_action not in {"snapshot", "update"}:
        raise ValueError("INVALID_ORDERBOOK_ACTION")
    if native_action == "snapshot":
        previous_value = row.get("prevSeqId")
        if previous_value is None:
            provider_previous = None
        else:
            parsed_previous = _provider_sequence(
                previous_value,
                positive=False,
                allow_negative=True,
            )
            provider_previous = (
                parsed_previous
                if parsed_previous is not None and parsed_previous >= 0
                else None
            )
    else:
        provider_previous = _provider_sequence(row.get("prevSeqId"), positive=False)
    continuity = row.get("continuity_status")
    if native_action == "snapshot":
        if continuity != "snapshot":
            raise ValueError("INVALID_SNAPSHOT_CONTINUITY")
        snapshot_or_delta = "snapshot"
    else:
        if continuity != "continuous":
            raise ValueError("INVALID_DELTA_CONTINUITY")
        snapshot_or_delta = "delta"
    bids = _project_levels(row.get("bids"), reverse=True)
    asks = _project_levels(row.get("asks"), reverse=False)
    provider_event_time = _utc_from_epoch_milliseconds(row.get("ts"))
    received_at = _utc_from_seconds(getattr(raw, "local_update_time", None))
    monotonic = getattr(raw, "received_monotonic_ns", None)
    if type(monotonic) is not int or monotonic < 0:
        monotonic = None
    return _BookState(
        connection_generation=generation,
        provider_sequence=provider_sequence,
        provider_previous_sequence=provider_previous,
        snapshot_or_delta=snapshot_or_delta,
        continuity_status=continuity,
        bids=bids,
        asks=asks,
        provider_event_time_utc=provider_event_time,
        received_at_utc=received_at,
        received_monotonic_ns=monotonic,
    )


def _project_levels(rows: object, *, reverse: bool) -> tuple[MarketOrderBookLevel, ...]:
    if type(rows) not in (list, tuple) or not rows:
        raise ValueError("EMPTY_ORDERBOOK_SIDE")
    levels: list[MarketOrderBookLevel] = []
    for row in rows:
        if type(row) not in (list, tuple) or len(row) < 2:
            raise ValueError("INVALID_ORDERBOOK_LEVEL")
        price = _positive_decimal(row[0])
        quantity = _positive_decimal(row[1])
        levels.append(MarketOrderBookLevel(price, quantity))
    prices = tuple(level.price for level in levels)
    if any(
        prices[index] <= prices[index + 1]
        if reverse
        else prices[index] >= prices[index + 1]
        for index in range(len(prices) - 1)
    ):
        raise ValueError("UNSORTED_ORDERBOOK_LEVELS")
    return tuple(levels)


def _event_for(
    key: MarketSubscriptionKey,
    source: MarketSourceDescriptor,
    cursor: MarketEventCursor,
    book: _BookState,
    *,
    recovery_snapshot: bool,
    continuity_status: str | None = None,
    stale: bool = False,
    stale_reason: str = "",
) -> MarketOrderBookEvent:
    if book.connection_generation != source.connection_generation:
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_EVENT_INVALID")
    depth = key.depth
    if type(depth) is not int or not 1 <= depth <= OKX_ORDERBOOK_MAX_DEPTH:
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_EVENT_INVALID")
    if book.bids[0].price >= book.asks[0].price:
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_EVENT_INVALID")
    clock = DataClockBinding(
        source=source,
        cursor=cursor,
        provider_event_time_utc=book.provider_event_time_utc,
        received_at_utc=book.received_at_utc,
        received_monotonic_ns=book.received_monotonic_ns,
        source_clock_quality=MarketClockQuality.UNKNOWN,
        receive_clock_quality=MarketClockQuality.UNKNOWN,
        source_clock_error_ms=None,
        receive_clock_error_ms=None,
        freshness_status=MarketFreshnessStatus.UNAVAILABLE,
        freshness_reason_codes=(
            "OKX_SOURCE_CLOCK_UNCALIBRATED",
            "OKX_RECEIVE_CLOCK_UNQUALIFIED",
        ),
    )
    return MarketOrderBookEvent(
        source=source,
        cursor=cursor,
        instrument=key.instrument,
        clock=clock,
        bids=book.bids[:depth],
        asks=book.asks[:depth],
        provider_sequence=book.provider_sequence,
        provider_previous_sequence=(
            book.provider_previous_sequence if book.snapshot_or_delta == "delta" else None
        ),
        snapshot_or_delta=book.snapshot_or_delta,
        continuity_status=continuity_status or book.continuity_status,
        stale=stale,
        stale_reason=stale_reason,
        recovery_snapshot=recovery_snapshot,
        complete_state=True,
    )


def _source_for(key: MarketSubscriptionKey, generation: int) -> MarketSourceDescriptor:
    if type(generation) is not int or generation <= 0:
        raise MarketStreamProviderContractError("MARKET_STREAM_PROVIDER_EVENT_INVALID")
    epoch = f"okx-wss-connection-{generation}"
    return MarketSourceDescriptor(
        key=key,
        stream_id=key.stream_id,
        epoch=epoch,
        provider="okx",
        source=_OKX_SOURCE,
        connection_generation=generation,
        clock_domain_id=_OKX_CLOCK_DOMAIN,
        clock_source_session_id=epoch,
        clock_source=_OKX_CLOCK_SOURCE,
    )


def _provider_sequence(
    value: object,
    *,
    positive: bool,
    optional: bool = False,
    allow_negative: bool = False,
) -> int | None:
    if value is None and optional:
        return None
    if type(value) is bool or type(value) not in {int, str}:
        raise ValueError("INVALID_PROVIDER_SEQUENCE")
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("INVALID_PROVIDER_SEQUENCE") from None
    if not decimal.is_finite() or decimal != decimal.to_integral_value():
        raise ValueError("INVALID_PROVIDER_SEQUENCE")
    result = int(decimal)
    if (result < 0 and not allow_negative) or (positive and result <= 0):
        raise ValueError("INVALID_PROVIDER_SEQUENCE")
    return result


def _positive_decimal(value: object) -> Decimal:
    if type(value) not in {str, int} or type(value) is bool:
        raise ValueError("INVALID_ORDERBOOK_DECIMAL")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("INVALID_ORDERBOOK_DECIMAL") from None
    if not result.is_finite() or result <= 0:
        raise ValueError("INVALID_ORDERBOOK_DECIMAL")
    return result


def _utc_from_epoch_milliseconds(value: object) -> str | None:
    try:
        timestamp_ms = _provider_sequence(value, positive=False)
        if timestamp_ms is None:
            return None
        seconds, milliseconds = divmod(timestamp_ms, 1000)
        observed = datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(
            milliseconds=milliseconds
        )
    except (OverflowError, OSError, ValueError):
        return None
    return observed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _utc_from_seconds(value: object) -> str | None:
    if type(value) not in {int, float} or type(value) is bool:
        return None
    try:
        seconds = float(value)
        if not math.isfinite(seconds):
            return None
        observed = datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    return observed.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _finite_stale_reason(value: object) -> str:
    allowed = {
        "sequence_gap",
        "checksum_mismatch",
        "snapshot_required",
        "missing_sequence_or_checksum",
        "incomplete_snapshot",
        "invalid_snapshot_depth",
        "malformed_depth_payload",
        "queue_overflow",
        "disconnected",
        "connection_changed",
        "invalid_event",
    }
    return value if type(value) is str and value in allowed else "invalid_event"


__all__ = [
    "OKX_MARKET_STREAM_EXCHANGE",
    "OKX_ORDERBOOK_MAX_DEPTH",
    "OkxMarketStreamAdapter",
    "OkxMarketStreamSession",
    "register_okx_market_stream_provider",
]
