"""OKX SWAP public ``tickers`` + ``trades`` channels as a neutral tick stream.

Iteration 62.  The session hosts the existing OKX public market WSS
(``OkxMarketWssDataSwap``, topics ``tickers`` and ``trades`` on the route's own
environment host: ``wspap.okx.com`` for demo) inside the SDK's direct
``MarketStreamPort`` owner and projects every push into a neutral
:class:`~bt_api_base.market_tick_protocol.MarketTickPayload` bound to the
subscription's source and cursor.

Facts and their provenance:

* A ``tickers`` push is a quote tick: ``last``/``bidPx``/``bidSz``/``askPx``/
  ``askSz`` verbatim, ``delta_volume`` 0 (no trade carried).
* A ``trades`` row is a trade tick: last = ``px``, ``delta_volume`` = ``sz``
  (OKX SWAP contracts, the venue's native unit; the payload has no unit
  field), bid/ask from the latest ``tickers`` push of the same epoch.
* Volume accounting (delta semantics): the first trade after subscribe or
  resync is the baseline (delta 0, ``volume_quality="baseline"``,
  ``volume_complete=False``).  A row whose ``tradeId`` equals the previous
  ``tradeId`` plus its ``count`` (OKX: ``tradeId`` is the last id of ``count``
  aggregated trades) is ``continuous``/complete; a larger jump is
  ``discontinuous``/incomplete (the row's own ``sz`` is still reported); a
  repeated or older ``tradeId`` is ignored.  Quote ticks are complete once the
  accounting is anchored, otherwise ``baseline``.
* ``provider_event_time_utc`` is each push's ``ts`` (venue milliseconds,
  ``provider_reported``); ``received_at_utc``/``received_monotonic_ns`` are
  taken when the WSS frame is received, before parsing.
* Clock qualities stay UNKNOWN and freshness UNAVAILABLE; the SDK qualifies
  ticks separately (venue clock cross-check via ``server_time_observation``).
* ``continuity_status`` is ``gap`` for the first tick of a binding, after a
  dropped/malformed frame and on a trade-id gap, otherwise ``continuous``.

A reconnect (new WSS generation), a disconnect or an ingress overflow marks
the channel recovery-required: ``poll`` raises once so the SDK owner moves the
channel to RECOVERY_REQUIRED, and ``resync`` binds a new source epoch (and a
new volume baseline) on the current connection.  Every session call must
happen on the opening thread.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from uuid import uuid4

from bt_api_base.containers.auto_init_mixin import container_class
from bt_api_base.market_protocol import MarketSourceDescriptor, MarketSubscriptionKey
from bt_api_base.market_stream_protocol import MarketStreamRequest
from bt_api_base.market_stream_provider_protocol import (
    MarketStreamProviderChannelBinding,
    MarketStreamProviderContractError,
    SelectedMarketStreamRoute,
)
from bt_api_base.market_tick_protocol import (
    MarketClockQuality,
    MarketEventCursor,
    MarketFreshnessStatus,
    MarketTickEvent,
    MarketTickPayload,
    bind_market_tick_event,
)

OKX_TICK_SOURCE_REF = "okx-public-tickers-v1"
OKX_TICK_ENTITLEMENT_REF = "okx-public-market-data"
OKX_TICK_SOURCE = "okx-public-wss-v5-tickers-trades"
_CLOCK_DOMAIN = "unix-epoch-milliseconds-utc"
_CLOCK_SOURCE = "okx-reported-ts"
_FRESHNESS_REASONS = ("OKX_SOURCE_CLOCK_UNCALIBRATED", "OKX_RECEIVE_CLOCK_UNQUALIFIED")
_CONNECT_TIMEOUT_SECONDS = 30.0
_MAX_PROVIDER_BATCH = 4096
_MAX_POLL_TIMEOUT_MS = 60_000


def _invalid(code: str = "MARKET_STREAM_PROVIDER_SESSION_INVALID") -> MarketStreamProviderContractError:
    return MarketStreamProviderContractError(code)


def _venue_number(value: Any, *, positive: bool) -> Optional[float]:
    """Exact venue decimal text as a float; ``""``/``None`` stays ``None``."""

    if value is None or value == "":
        return None
    if type(value) is not str:
        raise ValueError("okx_tick_number_invalid")
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError("okx_tick_number_invalid") from None
    if not number.is_finite() or number < 0 or (positive and number == 0):
        raise ValueError("okx_tick_number_invalid")
    return float(number)


def _utc_from_ms_text(value: Any) -> Optional[str]:
    if type(value) is not str or not value.isdigit() or len(value) > 15:
        return None
    milliseconds = int(value)
    if not 0 < milliseconds <= 253402300799999:
        return None
    return (
        datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _utc_from_ns(value: Any) -> Optional[str]:
    if type(value) is not int or value <= 0:
        return None
    seconds, nanoseconds = divmod(value, 1_000_000_000)
    moment = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
        microsecond=nanoseconds // 1000
    )
    return moment.isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass
class _TickChannel:
    binding: MarketStreamProviderChannelBinding
    subscription_epoch: int
    cursor: int = 0
    gap_pending: bool = True
    recovery_required: bool = False
    # Latest tickers quote (bid, ask, bid size, ask size) of this epoch.
    quote: Optional[tuple[Optional[float], Optional[float], Optional[float], Optional[float]]] = None
    # tradeId anchoring the delta-volume accounting of this epoch.
    trade_anchor: Optional[int] = None


def trade_volume(channel: _TickChannel, trade_id: int, count: int, quantity: float):
    """Delta-volume facts of one trade row, or ``None`` for a repeated/older id.

    Returns ``(delta, complete, volume_quality, gap)``.
    """

    anchor = channel.trade_anchor
    if anchor is None:
        channel.trade_anchor = trade_id
        return 0.0, False, "baseline", False
    if trade_id <= anchor:
        return None
    channel.trade_anchor = trade_id
    if trade_id == anchor + count:
        return quantity, True, "continuous", False
    return quantity, False, "discontinuous", True


def _payload(
    source: MarketSourceDescriptor,
    channel: _TickChannel,
    *,
    last_price: Optional[float],
    quote: Optional[tuple],
    event_ms: Any,
    delta_volume: float,
    volume_complete: bool,
    volume_quality: str,
    continuity_status: str,
    sequence: int,
    received_ns: Optional[int],
    received_monotonic_ns: Optional[int],
) -> MarketTickPayload:
    event_time = _utc_from_ms_text(event_ms)
    bid, ask, bid_size, ask_size = quote if quote is not None else (None, None, None, None)
    monotonic = (
        received_monotonic_ns
        if type(received_monotonic_ns) is int and received_monotonic_ns >= 0
        else None
    )
    return MarketTickPayload(
        instrument=source.key.instrument,
        last_price=last_price,
        bid_price=bid,
        ask_price=ask,
        bid_size=bid_size,
        ask_size=ask_size,
        lower_limit=None,
        upper_limit=None,
        turnover=None,
        open_interest=None,
        delta_volume=delta_volume,
        cumulative_volume=None,
        volume_complete=volume_complete,
        volume_quality=volume_quality,
        continuity_status=continuity_status,
        trading_date=None,
        event_session_date=None,
        provider_event_time_utc=event_time,
        event_time_provenance="provider_reported" if event_time is not None else "unavailable",
        received_at_utc=_utc_from_ns(received_ns),
        received_monotonic_ns=monotonic,
        provider_source=source.source,
        quality_contract_ref=None,
        provider_connection_generation=source.connection_generation,
        provider_sequence=sequence,
        provider_subscription_epoch=channel.subscription_epoch,
        clock_domain_id=source.clock_domain_id,
        clock_source_session_id=source.clock_source_session_id,
        clock_source=source.clock_source,
        source_clock_quality=MarketClockQuality.UNKNOWN,
        receive_clock_quality=MarketClockQuality.UNKNOWN,
        source_clock_error_ms=None,
        receive_clock_error_ms=None,
        freshness_status=MarketFreshnessStatus.UNAVAILABLE,
        freshness_reason_codes=_FRESHNESS_REASONS,
        execution_eligible=False,
        quality_flags=(),
    )


def project_okx_quote(
    raw: Mapping[str, Any],
    channel: _TickChannel,
    *,
    sequence: int,
    received_ns: Optional[int],
    received_monotonic_ns: Optional[int],
) -> MarketTickPayload:
    """Quote tick from one ``tickers`` row (no traded volume carried)."""

    source = channel.binding.source
    if not isinstance(raw, Mapping) or raw.get("instId") != source.key.instrument.native_symbol:
        raise ValueError("okx_tick_instrument_mismatch")
    quote = (
        _venue_number(raw.get("bidPx"), positive=True),
        _venue_number(raw.get("askPx"), positive=True),
        _venue_number(raw.get("bidSz"), positive=False),
        _venue_number(raw.get("askSz"), positive=False),
    )
    anchored = channel.trade_anchor is not None
    payload = _payload(
        source,
        channel,
        last_price=_venue_number(raw.get("last"), positive=True),
        quote=quote,
        event_ms=raw.get("ts"),
        delta_volume=0.0,
        volume_complete=anchored,
        volume_quality="continuous" if anchored else "baseline",
        continuity_status="gap" if channel.gap_pending else "continuous",
        sequence=sequence,
        received_ns=received_ns,
        received_monotonic_ns=received_monotonic_ns,
    )
    channel.quote = quote
    return payload


def project_okx_trade(
    raw: Mapping[str, Any],
    channel: _TickChannel,
    *,
    sequence: int,
    received_ns: Optional[int],
    received_monotonic_ns: Optional[int],
) -> Optional[MarketTickPayload]:
    """Trade tick from one ``trades`` row, or ``None`` for a repeated/older id."""

    source = channel.binding.source
    if not isinstance(raw, Mapping) or raw.get("instId") != source.key.instrument.native_symbol:
        raise ValueError("okx_trade_instrument_mismatch")
    trade_id = raw.get("tradeId")
    count = raw.get("count", "1")
    if (
        type(trade_id) is not str
        or not trade_id.isdigit()
        or len(trade_id) > 24
        or type(count) is not str
        or not count.isdigit()
        or int(count) < 1
    ):
        raise ValueError("okx_trade_identity_invalid")
    price = _venue_number(raw.get("px"), positive=True)
    quantity = _venue_number(raw.get("sz"), positive=True)
    if price is None or quantity is None:
        raise ValueError("okx_trade_values_missing")
    volume = trade_volume(channel, int(trade_id), int(count), quantity)
    if volume is None:
        return None
    delta, complete, quality, gap = volume
    return _payload(
        source,
        channel,
        last_price=price,
        quote=channel.quote,
        event_ms=raw.get("ts"),
        delta_volume=delta,
        volume_complete=complete,
        volume_quality=quality,
        continuity_status="gap" if channel.gap_pending or gap else "continuous",
        sequence=sequence,
        received_ns=received_ns,
        received_monotonic_ns=received_monotonic_ns,
    )


class OkxTickMarketStreamSession:
    """One OKX public WSS ``tickers`` source for one route/instrument."""

    def __init__(
        self,
        route: SelectedMarketStreamRoute,
        *,
        wake_callback: Callable[[], None],
        stream_factory: Optional[Callable[..., Any]] = None,
    ) -> None:
        from bt_api_okx.market_stream_provider import _validate_route

        _validate_route(route)
        if not callable(wake_callback):
            raise _invalid()
        self._route = route
        self._wake_callback = wake_callback
        self._stream_factory = stream_factory or self._default_stream
        self._owner_thread = threading.get_ident()
        self._queue: Any = None
        self._stream: Any = None
        self._channels: dict[object, _TickChannel] = {}
        self._session_ref = uuid4().hex[:16]
        self._epoch_ordinal = 0
        self._ingest_sequence = 0
        self._raise_pending = False
        self._closed = False
        self._cleanup_unverified = False
        self.counters: dict[str, int] = {}

    # -- MarketStreamProviderSession ----------------------------------------
    def subscribe(self, request: MarketStreamRequest, /) -> MarketStreamProviderChannelBinding:
        self._check_owner()
        self._validate_request(request)
        if self._closed or self._cleanup_unverified:
            raise _invalid()
        if any(channel.binding.request == request for channel in self._channels.values()):
            raise _invalid("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        self._start_if_needed(request.queue_capacity)
        generation = self._current_generation()
        if generation is None:
            raise _invalid()
        binding, epoch = self._new_binding(request, generation)
        self._channels[binding.token] = _TickChannel(binding, epoch)
        return binding

    def poll(self, *, timeout_ms: int, max_events: int) -> tuple[MarketTickEvent, ...]:
        self._check_owner()
        if (
            type(timeout_ms) is not int
            or not 0 <= timeout_ms <= _MAX_POLL_TIMEOUT_MS
            or type(max_events) is not int
            or not 1 <= max_events <= _MAX_PROVIDER_BATCH
        ):
            raise _invalid("MARKET_STREAM_PROVIDER_EVENT_INVALID")
        if self._closed or self._cleanup_unverified:
            raise _invalid()
        self._raise_if_pending()
        if not self._channels or self._queue is None:
            return ()
        self._check_connection()
        events: list[MarketTickEvent] = []
        deadline = time.monotonic() + timeout_ms / 1000.0
        while True:
            records, overflowed = self._queue.drain(max_events - len(events))
            if overflowed:
                self._recover_all("queue_overflow")
                self._force_reconnect()
            for record in records:
                self._process(record, events)
            remaining = deadline - time.monotonic()
            if events or self._raise_pending or remaining <= 0 or len(events) >= max_events:
                break
            record, overflowed = self._queue.take(timeout=min(remaining, 0.05))
            if overflowed:
                self._recover_all("queue_overflow")
                self._force_reconnect()
            elif record is not None:
                self._process(record, events)
        if self._raise_pending and not events:
            self._raise_if_pending()
        return tuple(events)

    def resync(
        self,
        binding: MarketStreamProviderChannelBinding,
        *,
        acknowledge_data_loss: bool,
    ) -> MarketStreamProviderChannelBinding:
        """Bind a new source epoch on the current connection after a loss."""

        self._check_owner()
        if acknowledge_data_loss is not True:
            raise _invalid("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        channel = self._channel_for(binding)
        if not channel.recovery_required or self._closed or self._cleanup_unverified:
            raise _invalid("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        if self._stream is None:
            self._start_if_needed(binding.request.queue_capacity)
        deadline = time.monotonic() + _CONNECT_TIMEOUT_SECONDS
        generation = self._current_generation()
        while generation is None:
            if time.monotonic() >= deadline:
                raise _invalid()
            time.sleep(0.05)
            generation = self._current_generation()
        # Everything queued before this point belongs to the lost epoch.
        records, _overflowed = self._queue.drain(_MAX_PROVIDER_BATCH)
        while records:
            records, _overflowed = self._queue.drain(_MAX_PROVIDER_BATCH)
        self._raise_pending = False
        new_binding, epoch = self._new_binding(binding.request, generation)
        del self._channels[binding.token]
        self._channels[new_binding.token] = _TickChannel(new_binding, epoch)
        return new_binding

    def unsubscribe(self, binding: MarketStreamProviderChannelBinding, /) -> bool:
        self._check_owner()
        channel = self._channels.pop(getattr(binding, "token", None), None)
        if channel is None or channel.binding is not binding:
            if channel is not None:
                self._channels[channel.binding.token] = channel
            return False
        if self._channels:
            return True
        return self._stop_stream()

    def close(self) -> bool:
        self._check_owner()
        self._channels.clear()
        closed = self._stop_stream()
        if closed:
            self._closed = True
            self._cleanup_unverified = False
        else:
            self._cleanup_unverified = True
        return closed

    # -- internals ----------------------------------------------------------
    def _bump(self, name: str) -> None:
        self.counters[name] = self.counters.get(name, 0) + 1

    def _raise_if_pending(self) -> None:
        if self._raise_pending:
            self._raise_pending = False
            raise _invalid("MARKET_STREAM_PROVIDER_EVENT_INVALID")

    def _recover_all(self, reason: str) -> None:
        for channel in self._channels.values():
            if not channel.recovery_required:
                channel.recovery_required = True
                self._raise_pending = True
                self._bump(f"recovery:{reason}")

    def _check_connection(self) -> None:
        stream = self._stream
        generation = getattr(stream, "_connection_generation", None)
        stopped = getattr(getattr(stream, "_stop_event", None), "is_set", lambda: True)()
        for channel in self._channels.values():
            if channel.recovery_required:
                continue
            if stopped:
                self._recover_all("stream_stopped")
            elif generation != channel.binding.source.connection_generation:
                self._recover_all("connection_changed")

    def _process(self, record: Any, events: list[MarketTickEvent]) -> None:
        kind = getattr(record, "kind", None)
        generation = getattr(record, "connection_generation", None)
        if kind == "opened":
            if any(
                generation != channel.binding.source.connection_generation
                for channel in self._channels.values()
                if not channel.recovery_required
            ):
                self._recover_all("connection_changed")
            return
        if kind == "closed":
            self._recover_all("disconnected")
            return
        if kind != "data":
            self._recover_all("invalid_event")
            return
        value = record.value
        try:
            from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
            from bt_api_okx.containers.trades.okx_market_trade import OkxMarketTradeData

            kind_of = container_class(value)
            if kind_of is OkxTickerData:
                raw, project = value.ticker_data, project_okx_quote
            elif kind_of is OkxMarketTradeData:
                raw, project = value.trade_data, project_okx_trade
            else:
                self._bump("non_tick_frame_ignored")
                return
        except Exception:
            self._bump("tick_frame_invalid")
            return
        for channel in self._channels.values():
            if channel.recovery_required:
                self._bump("tick_dropped_recovery_required")
                continue
            source = channel.binding.source
            if generation != source.connection_generation:
                self._recover_all("connection_changed")
                continue
            try:
                payload = project(
                    raw,
                    channel,
                    sequence=self._ingest_sequence + 1,
                    received_ns=getattr(record, "received_ns", None),
                    received_monotonic_ns=getattr(record, "received_monotonic_ns", None),
                )
            except Exception:
                channel.gap_pending = True  # a lost push: the next tick is not continuous
                self._bump("tick_frame_invalid")
                continue
            if payload is None:
                self._bump("trade_repeated_or_out_of_order")
                continue
            if payload.volume_quality == "discontinuous":
                self._bump("trade_id_gap")
            self._ingest_sequence += 1
            channel.cursor += 1
            channel.gap_pending = False
            events.append(
                bind_market_tick_event(
                    payload, source, MarketEventCursor(source.stream_id, source.epoch, channel.cursor)
                )
            )

    def _new_binding(
        self, request: MarketStreamRequest, generation: int
    ) -> tuple[MarketStreamProviderChannelBinding, int]:
        self._epoch_ordinal += 1
        key = MarketSubscriptionKey(
            source_ref=OKX_TICK_SOURCE_REF,
            entitlement_ref=OKX_TICK_ENTITLEMENT_REF,
            instrument=request.instrument,
            channel="tick",
            depth=None,
            timeframe=None,
        )
        epoch = f"okx-tick-{self._session_ref}-g{generation}-e{self._epoch_ordinal}"
        source = MarketSourceDescriptor(
            key=key,
            stream_id=key.stream_id,
            epoch=epoch,
            provider="okx",
            source=OKX_TICK_SOURCE,
            connection_generation=generation,
            clock_domain_id=_CLOCK_DOMAIN,
            clock_source_session_id=epoch,
            clock_source=_CLOCK_SOURCE,
        )
        binding = MarketStreamProviderChannelBinding(
            token=object(),
            request=request,
            key=key,
            source=source,
            initial_cursor=None,
            initial_events=(),
            recovery_required=False,
        )
        return binding, self._epoch_ordinal

    def _current_generation(self) -> Optional[int]:
        stream = self._stream
        generation = getattr(stream, "_connection_generation", None)
        if (
            type(generation) is not int
            or generation <= 0
            or getattr(stream, "_running_flag", False) is not True
            or getattr(stream, "_stop_event", None) is None
            or stream._stop_event.is_set()
        ):
            return None
        return generation

    def _default_stream(self, queue: Any, params: Any, info: Mapping[str, Any]) -> Any:
        from bt_api_okx.market_stream_provider import (
            OKX_MARKET_STREAM_EXCHANGE,
            _OwnedOkxMarketWssDataSwap,
        )

        return _OwnedOkxMarketWssDataSwap(
            queue,
            exchange_data=params,
            environment=info["environment"],
            api_region=info["api_region"],
            wss_url=params.wss_url,
            topics=[
                {"topic": "tickers", "symbol": self._route.instrument.native_symbol},
                {"topic": "trades", "symbol": self._route.instrument.native_symbol},
            ],
            asset_type="SWAP",
            exchange_name=OKX_MARKET_STREAM_EXCHANGE,
            stream_role="market",
            wss_name="okx_sdk_market_tick",
            message_idle_timeout=0.0,
        )

    def _start_if_needed(self, queue_capacity: int) -> None:
        from bt_api_okx.environment import configure_environment
        from bt_api_okx.exchange_data import OkxExchangeDataSwap
        from bt_api_okx.market_stream_provider import _BoundedOkxIngressQueue

        if self._stream is not None:
            return
        try:
            info = self._environment_info()
            params = configure_environment(
                OkxExchangeDataSwap(),
                {"environment": info["environment"], "api_region": info["api_region"]},
            )
            queue = _BoundedOkxIngressQueue(
                max(1, min(int(queue_capacity), 65536)), self._wake_callback
            )
            stream = self._stream_factory(queue, params, info)
            queue.bind_stream(stream)
            self._queue = queue
            self._stream = stream
            stream.start(connect_timeout=_CONNECT_TIMEOUT_SECONDS)
            if self._current_generation() is None:
                raise RuntimeError("okx_tick_stream_not_ready")
        except Exception:
            if self._stream is not None and not self._stop_stream():
                self._cleanup_unverified = True
            raise _invalid() from None

    def _environment_info(self) -> dict[str, Any]:
        try:
            info = self._route.client.get_environment_info()
        except Exception:
            raise _invalid("MARKET_STREAM_PROVIDER_ROUTE_INVALID") from None
        if (
            type(info) is not dict
            or info.get("verified") is not True
            or info.get("environment") != self._route.environment
            or info.get("api_region") not in {"global", "eea", "us", "tr"}
            or info.get("simulated") is not (self._route.environment == "demo")
        ):
            raise _invalid("MARKET_STREAM_PROVIDER_ROUTE_INVALID")
        return info

    def _force_reconnect(self) -> None:
        ws = getattr(self._stream, "ws", None)
        if ws is not None:
            try:
                ws.close()
            except Exception:
                self._bump("reconnect_close_failed")

    def _stop_stream(self) -> bool:
        stream = self._stream
        if stream is None:
            return True
        try:
            stream.stop()
        except Exception:
            return False
        workers = tuple(
            getattr(stream, name, None)
            for name in (
                "process",
                "_restart_process",
                "_watchdog_process",
                "_readiness_watchdog_process",
            )
        )
        if (
            any(worker is not None and worker.is_alive() for worker in workers)
            or getattr(stream, "_running_flag", False) is not False
            or not stream._stop_event.is_set()
        ):
            return False
        self._stream = None
        self._queue = None
        return True

    def _validate_request(self, request: object) -> None:
        if (
            type(request) is not MarketStreamRequest
            or request.exchange_name != self._route.exchange_name
            or request.instrument != self._route.instrument
            or request.channel != "tick"
            or request.depth is not None
        ):
            raise _invalid("MARKET_STREAM_PROVIDER_CHANNEL_UNAVAILABLE")

    def _channel_for(self, binding: object) -> _TickChannel:
        channel = self._channels.get(getattr(binding, "token", None))
        if channel is None or channel.binding is not binding:
            raise _invalid("MARKET_STREAM_PROVIDER_BINDING_INVALID")
        return channel

    def _check_owner(self) -> None:
        if threading.get_ident() != self._owner_thread:
            raise _invalid()


__all__ = [
    "OKX_TICK_ENTITLEMENT_REF",
    "OKX_TICK_SOURCE",
    "OKX_TICK_SOURCE_REF",
    "OkxTickMarketStreamSession",
    "project_okx_quote",
    "project_okx_trade",
    "trade_volume",
]
