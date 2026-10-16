"""Bounded OKX SWAP history adapter for the provider-neutral market port."""

from __future__ import annotations

import math
import re
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from bt_api_base.market_history_protocol import MarketBar, MarketHistoryPage, MarketHistoryRequest
from bt_api_base.market_protocol import MarketSubscriptionKey

_SOURCE_REF = "okx-public-market-r1"
_ENTITLEMENT_REF = "public-history-r1"
_MAX_REQUEST_TIMEOUT_SECONDS = 300.0
_OKX_PAGE_LIMIT = 300
_MAX_SCAN_WINDOWS = 64
_ONE_SECOND_RETENTION = timedelta(days=90)
_MAX_DECIMAL_TEXT_BYTES = 48
_UTC = timezone.utc  # noqa: UP017 -- The package supports Python 3.9.
_EPOCH = datetime(1970, 1, 1, tzinfo=_UTC)
_TIMESTAMP_MS = re.compile(r"[0-9]{1,16}\Z", re.ASCII)
_DECIMAL_TEXT = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z", re.ASCII)

_TIMEFRAME_TO_OKX = {
    "1s": "1s",
    "1m": "1m",
    "3m": "3m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1H",
    "2h": "2H",
    "4h": "4H",
    "6h": "6H",
    "12h": "12H",
    "1d": "1D",
    "2d": "2D",
    "3d": "3D",
    "1w": "1W",
}


class OkxMarketHistoryProviderError(RuntimeError):
    """Finite, value-free diagnostics for a public OKX history request."""

    _CODES = frozenset(
        {
            "INVALID_HISTORY_REQUEST",
            "UNSUPPORTED_OKX_HISTORY_KEY",
            "UNSUPPORTED_OKX_HISTORY_TIMEFRAME",
            "OKX_HISTORY_WINDOW_TOO_OLD",
            "OKX_HISTORY_END_IN_FUTURE",
            "INVALID_HISTORY_TIMEOUT",
            "HISTORY_PROVIDER_CLOSED",
            "HISTORY_PROVIDER_SCAN_LIMIT",
            "HISTORY_PROVIDER_TIMEOUT",
            "OKX_HISTORY_REQUEST_FAILED",
            "INVALID_OKX_HISTORY_RESPONSE",
            "INVALID_OKX_HISTORY_ROW",
        }
    )

    def __init__(self, code: str) -> None:
        if type(code) is not str or code not in self._CODES:
            code = "OKX_HISTORY_REQUEST_FAILED"
        self.code = code
        super().__init__(code)


class _OkxHistoryRequestPort(Protocol):
    """The existing OKX builder and public REST request methods we need."""

    def _get_kline_his(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]: ...

    def request(
        self,
        path: Any,
        params: Any = None,
        body: Any = None,
        extra_data: Any = None,
        timeout: Any = 10,
        *,
        max_retries: Any = None,
    ) -> Any: ...


class OkxMarketHistoryProvider:
    """Fetch fixed-duration, closed-only OKX SWAP bars through existing REST code.

    The injected request client is trusted operator configuration. The adapter
    only uses the generated public ``get_kline_his`` route and caps each REST
    request at 300 rows, each request's timeout, and the total scan work.
    """

    def __init__(
        self,
        request_data: _OkxHistoryRequestPort,
        *,
        monotonic_clock: Callable[[], float] = time.monotonic,
        utc_clock: Callable[[], datetime] = lambda: datetime.now(_UTC),
    ) -> None:
        if not callable(getattr(request_data, "_get_kline_his", None)) or not callable(
            getattr(request_data, "request", None)
        ):
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED")
        if not callable(monotonic_clock) or not callable(utc_clock):
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED")
        self._request_data = request_data
        self._monotonic = monotonic_clock
        self._utc_clock = utc_clock
        self._closed = False

    def fetch(self, request: MarketHistoryRequest, timeout_seconds: float) -> MarketHistoryPage:
        if self._closed:
            raise OkxMarketHistoryProviderError("HISTORY_PROVIDER_CLOSED")
        if type(request) is not MarketHistoryRequest:
            raise OkxMarketHistoryProviderError("INVALID_HISTORY_REQUEST")
        try:
            timeout = float(timeout_seconds)
        except (OverflowError, TypeError, ValueError):
            raise OkxMarketHistoryProviderError("INVALID_HISTORY_TIMEOUT") from None
        if (
            isinstance(timeout_seconds, bool)
            or type(timeout_seconds) not in (int, float)
            or not math.isfinite(timeout)
            or not 0 < timeout <= _MAX_REQUEST_TIMEOUT_SECONDS
        ):
            raise OkxMarketHistoryProviderError("INVALID_HISTORY_TIMEOUT")

        key = request.key
        instrument = key.instrument
        if (
            type(key) is not MarketSubscriptionKey
            or key.source_ref != _SOURCE_REF
            or key.entitlement_ref != _ENTITLEMENT_REF
            or instrument.provider != "okx"
            or instrument.venue != "OKX"
            or instrument.environment != "live"
            or instrument.product_type != "SWAP"
            or instrument.instrument_id != instrument.native_symbol
            or key.channel != "bar"
            or key.depth is not None
        ):
            raise OkxMarketHistoryProviderError("UNSUPPORTED_OKX_HISTORY_KEY")
        timeframe = key.timeframe
        okx_bar = _TIMEFRAME_TO_OKX.get(timeframe or "")
        if okx_bar is None:
            raise OkxMarketHistoryProviderError("UNSUPPORTED_OKX_HISTORY_TIMEFRAME")

        start = _parse_utc(request.start_time_utc)
        end = _parse_utc(request.end_time_utc)
        now = self._clock_utc()
        if end > now:
            raise OkxMarketHistoryProviderError("OKX_HISTORY_END_IN_FUTURE")
        if timeframe == "1s" and start < now - _ONE_SECOND_RETENTION:
            raise OkxMarketHistoryProviderError("OKX_HISTORY_WINDOW_TOO_OLD")

        started = self._clock_monotonic()
        deadline = started + timeout
        duration = timedelta(seconds=request.bar_duration_seconds)
        found: dict[int, tuple[str, ...]] = {}
        cursor = start
        windows = 0
        exhausted = False

        while cursor < end and windows < _MAX_SCAN_WINDOWS:
            remaining = deadline - self._clock_monotonic()
            if not math.isfinite(remaining) or remaining <= 0:
                break
            segment_end = min(cursor + duration * _OKX_PAGE_LIMIT, end)
            after_ms = _ceil_epoch_milliseconds(segment_end)
            try:
                path, params, extra_data = self._request_data._get_kline_his(
                    instrument.native_symbol,
                    bar=okx_bar,
                    after=str(after_ms),
                    limit=str(_OKX_PAGE_LIMIT),
                )
                response = self._request_data.request(
                    path,
                    params=params,
                    extra_data=extra_data,
                    timeout=remaining,
                    max_retries=1,
                )
            except Exception:
                raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED") from None
            windows += 1
            remaining = deadline - self._clock_monotonic()
            if not math.isfinite(remaining) or remaining < 0:
                break
            rows = _response_rows(response)
            for row in rows:
                timestamp, values = _parse_row(row)
                if values is None:
                    continue
                opened = _datetime_from_milliseconds(timestamp)
                closed = opened + duration
                if cursor <= opened < segment_end and opened >= start and closed <= end:
                    previous = found.get(timestamp)
                    if previous is not None and previous != values:
                        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW")
                    found[timestamp] = values

            cursor = segment_end
            exhausted = cursor >= end
            if len(found) > request.limit:
                break

        ordered = sorted(found.items())
        has_more = len(ordered) > request.limit
        selected = ordered[: request.limit]
        bars = tuple(
            MarketBar(
                open_time_utc=_format_utc(_datetime_from_milliseconds(timestamp)),
                close_time_utc=_format_utc(_datetime_from_milliseconds(timestamp) + duration),
                open=values[0],
                high=values[1],
                low=values[2],
                close=values[3],
                volume=values[4],
            )
            for timestamp, values in selected
        )

        if has_more:
            complete = False
        elif exhausted:
            complete = True
        elif bars:
            complete = False
        else:
            raise OkxMarketHistoryProviderError(
                "HISTORY_PROVIDER_TIMEOUT"
                if self._clock_monotonic() >= deadline
                else "HISTORY_PROVIDER_SCAN_LIMIT"
            )

        observed = self._clock_utc()
        next_start = None if complete else bars[-1].close_time_utc
        if not complete and _parse_utc(next_start or "") >= end:
            complete = True
            next_start = None
        try:
            return MarketHistoryPage(
                request=request,
                bars=bars,
                complete=complete,
                next_start_time_utc=next_start,
                observed_at_utc=_format_utc(observed),
            )
        except Exception:
            raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW") from None

    def close(self) -> None:
        """Close the injected OKX request client once, without hidden retries."""
        if self._closed:
            return
        disconnect = getattr(self._request_data, "disconnect", None)
        close = getattr(self._request_data, "close", None)
        closer = disconnect if callable(disconnect) else close
        if callable(closer):
            try:
                result = closer()
            except Exception:
                raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED") from None
            if result is not None and result is not True:
                raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED")
        self._closed = True

    def _clock_utc(self) -> datetime:
        try:
            value = self._utc_clock()
        except Exception:
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED") from None
        if type(value) is not datetime or value.tzinfo is None:
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED")
        return value.astimezone(_UTC)

    def _clock_monotonic(self) -> float:
        try:
            value = self._monotonic()
            normalized = float(value)
        except Exception:
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED") from None
        if not math.isfinite(normalized):
            raise OkxMarketHistoryProviderError("OKX_HISTORY_REQUEST_FAILED")
        return normalized


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except Exception:
        raise OkxMarketHistoryProviderError("INVALID_HISTORY_REQUEST") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise OkxMarketHistoryProviderError("INVALID_HISTORY_REQUEST")
    return parsed.astimezone(_UTC)


def _format_utc(value: datetime) -> str:
    normalized = value.astimezone(_UTC)
    text = normalized.isoformat(timespec="microseconds")
    text = text.replace("+00:00", "Z")
    if "." in text:
        text = text.replace(".000000Z", "Z")
        if text.endswith("Z") and "." in text:
            fraction = text.split(".", 1)[1][:-1].rstrip("0")
            if fraction:
                text = text.split(".", 1)[0] + "." + fraction + "Z"
            else:
                text = text.split(".", 1)[0] + "Z"
    return text


def _ceil_epoch_milliseconds(value: datetime) -> int:
    delta = value - _EPOCH
    total_microseconds = ((delta.days * 86_400 + delta.seconds) * 1_000_000) + delta.microseconds
    return (total_microseconds + 999) // 1_000


def _datetime_from_milliseconds(value: int) -> datetime:
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW") from None


def _response_rows(response: Any) -> tuple[Any, ...]:
    getter = getattr(response, "get_input_data", None)
    if not callable(getter):
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_RESPONSE")
    try:
        payload = getter()
    except Exception:
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_RESPONSE") from None
    if (
        not isinstance(payload, Mapping)
        or payload.get("code") != "0"
        or type(payload.get("data")) is not list
        or len(payload["data"]) > _OKX_PAGE_LIMIT
    ):
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_RESPONSE")
    return tuple(payload["data"])


def _parse_row(row: Any) -> tuple[int, tuple[str, ...] | None]:
    if type(row) not in (list, tuple) or len(row) != 9:
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW")
    timestamp_text = row[0]
    if type(timestamp_text) is not str or _TIMESTAMP_MS.fullmatch(timestamp_text) is None:
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW")
    if any(
        type(value) is not str
        or len(value) > _MAX_DECIMAL_TEXT_BYTES
        or _DECIMAL_TEXT.fullmatch(value) is None
        for value in row[1:8]
    ):
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW")
    if row[8] not in {"0", "1"}:
        raise OkxMarketHistoryProviderError("INVALID_OKX_HISTORY_ROW")
    # Unclosed candles are intentionally ignored; no ticker/latest-bar state is inferred.
    if row[8] == "0":
        return int(timestamp_text), None
    return int(timestamp_text), (row[1], row[2], row[3], row[4], row[5])


__all__ = ["OkxMarketHistoryProvider", "OkxMarketHistoryProviderError"]
