"""Synthetic public-REST coverage for the typed OKX market-history adapter."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from bt_api_base.market_history_protocol import MarketHistoryRequest
from bt_api_base.market_protocol import MarketInstrumentKey, MarketSubscriptionKey
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap
from bt_api_okx.market_history_provider import (
    OkxMarketHistoryProvider,
    OkxMarketHistoryProviderError,
)

UTC = timezone.utc  # noqa: UP017 -- The package supports Python 3.9.


def _key(timeframe: str = "1m", **changes: Any) -> MarketSubscriptionKey:
    fields: dict[str, Any] = {
        "source_ref": "okx-public-market-r1",
        "entitlement_ref": "public-history-r1",
        "instrument": MarketInstrumentKey(
            provider="okx",
            venue="OKX",
            environment="live",
            product_type="SWAP",
            instrument_id="BTC-USDT-SWAP",
            native_symbol="BTC-USDT-SWAP",
        ),
        "channel": "bar",
        "depth": None,
        "timeframe": timeframe,
    }
    fields.update(changes)
    return MarketSubscriptionKey(**fields)


def _request(
    *,
    key: MarketSubscriptionKey | None = None,
    start: datetime = datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
    end: datetime = datetime(2026, 1, 1, 0, 3, tzinfo=UTC),
    limit: int = 100,
) -> MarketHistoryRequest:
    return MarketHistoryRequest(
        key=_key() if key is None else key,
        start_time_utc=start.isoformat().replace("+00:00", "Z"),
        end_time_utc=end.isoformat().replace("+00:00", "Z"),
        limit=limit,
    )


def _row(opened: datetime, *, confirm: str = "1") -> list[str]:
    timestamp = str(int(opened.timestamp() * 1_000))
    return [timestamp, "100.0", "101.0", "99.0", "100.5", "12", "4", "5", confirm]


class _SyntheticOkxRequestData(OkxRequestDataSwap):
    def __init__(self, responses: list[list[list[str]]]) -> None:
        super().__init__(None, environment="production")
        self.responses = list(responses)
        self.http_calls: list[dict[str, Any]] = []
        self.disconnect_calls = 0

    def http_request(
        self,
        method: str,
        url: str,
        headers: Any = None,
        body: Any = None,
        timeout: float = 10,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        self.http_calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers or {}),
                "timeout": timeout,
                "max_retries": max_retries,
                "body": body,
            }
        )
        if not self.responses:
            raise AssertionError("unexpected extra HTTP request")
        return {"code": "0", "msg": "", "data": self.responses.pop(0)}

    def disconnect(self) -> None:
        self.disconnect_calls += 1
        super().disconnect()


def _provider(
    client: _SyntheticOkxRequestData,
    *,
    observed: datetime = datetime(2026, 1, 1, 0, 10, tzinfo=UTC),
) -> OkxMarketHistoryProvider:
    return OkxMarketHistoryProvider(
        client,
        monotonic_clock=lambda: 10.0,
        utc_clock=lambda: observed,
    )


def test_existing_okx_request_builder_uses_bounded_public_history_route() -> None:
    opened = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    rows = [
        _row(opened + timedelta(minutes=2)),
        _row(opened + timedelta(minutes=1), confirm="0"),
        _row(opened + timedelta(minutes=1)),
        _row(opened),
        _row(opened + timedelta(minutes=3)),
    ]
    request_data = _SyntheticOkxRequestData([rows])
    provider = _provider(request_data)

    page = provider.fetch(_request(), timeout_seconds=3.0)

    assert page.complete is True
    assert page.next_start_time_utc is None
    assert [bar.open_time_utc for bar in page.bars] == [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:01:00Z",
        "2026-01-01T00:02:00Z",
    ]
    assert [bar.volume for bar in page.bars] == ["12", "12", "12"]
    assert request_data.http_calls == [
        {
            "method": "GET",
            "url": "https://openapi.okx.com/api/v5/market/history-candles?instId=BTC-USDT-SWAP&bar=1m&after=1767225780000&limit=300",
            "headers": {"Content-Type": "application/json", "x-simulated-trading": "0"},
            "timeout": 3.0,
            "max_retries": 1,
            "body": None,
        }
    ]
    provider.close()
    provider.close()
    assert request_data.disconnect_calls == 1


def test_history_page_is_ascending_bounded_and_uses_last_closed_bar_cursor() -> None:
    start = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    end = start + timedelta(minutes=4)
    request = _request(start=start, end=end, limit=2)
    client = _SyntheticOkxRequestData(
        [[_row(start + timedelta(minutes=minute)) for minute in range(4)]]
    )
    page = _provider(client).fetch(request, timeout_seconds=2.0)

    assert page.complete is False
    assert [bar.open_time_utc for bar in page.bars] == [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:01:00Z",
    ]
    assert page.next_start_time_utc == "2026-01-01T00:02:00Z"
    assert len(client.http_calls) == 1


def test_failed_client_close_remains_retryable() -> None:
    client = _SyntheticOkxRequestData([])
    disconnect = client.disconnect
    attempts = 0

    def fail_once() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("synthetic close uncertainty")
        disconnect()

    client.disconnect = fail_once  # type: ignore[method-assign]
    provider = _provider(client)

    with pytest.raises(OkxMarketHistoryProviderError, match="OKX_HISTORY_REQUEST_FAILED"):
        provider.close()
    assert attempts == 1
    provider.close()

    assert attempts == 2
    assert client.disconnect_calls == 1


def test_okx_max_page_and_provider_scan_bounds_prove_more_data() -> None:
    start = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    first_window = [_row(start + timedelta(minutes=index)) for index in range(300)]
    second_window = [_row(start + timedelta(minutes=300))]
    client = _SyntheticOkxRequestData([first_window, second_window])
    request_end = start + timedelta(minutes=301)
    request = _request(start=start, end=request_end, limit=300)

    page = _provider(client, observed=request_end + timedelta(minutes=1)).fetch(
        request, timeout_seconds=5.0
    )

    assert len(page.bars) == 300
    assert page.complete is False
    assert page.next_start_time_utc == "2026-01-01T05:00:00Z"
    assert len(client.http_calls) == 2
    assert all("limit=300" in call["url"] for call in client.http_calls)
    assert all(call["max_retries"] == 1 for call in client.http_calls)


@pytest.mark.parametrize(
    ("key", "start", "end", "code"),
    [
        (
            _key("10m"),
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 1, 2, tzinfo=UTC),
            "UNSUPPORTED_OKX_HISTORY_TIMEFRAME",
        ),
        (
            _key(entitlement_ref="public-ticker-r1"),
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 1, 2, tzinfo=UTC),
            "UNSUPPORTED_OKX_HISTORY_KEY",
        ),
        (
            _key("1s"),
            datetime(2025, 9, 30, tzinfo=UTC),
            datetime(2026, 1, 1, tzinfo=UTC),
            "OKX_HISTORY_WINDOW_TOO_OLD",
        ),
    ],
)
def test_key_timeframe_and_retention_are_checked_before_http(
    key: MarketSubscriptionKey,
    start: datetime,
    end: datetime,
    code: str,
) -> None:
    client = _SyntheticOkxRequestData([])
    with pytest.raises(OkxMarketHistoryProviderError, match=code):
        _provider(client).fetch(_request(key=key, start=start, end=end), 1.0)
    assert not client.http_calls


def test_future_end_timeout_and_malformed_rows_fail_with_finite_codes() -> None:
    client = _SyntheticOkxRequestData([])
    provider = _provider(client)
    with pytest.raises(OkxMarketHistoryProviderError, match="OKX_HISTORY_END_IN_FUTURE"):
        provider.fetch(
            _request(end=datetime(2026, 1, 1, 0, 11, tzinfo=UTC)),
            timeout_seconds=1.0,
        )
    with pytest.raises(OkxMarketHistoryProviderError, match="INVALID_HISTORY_TIMEOUT"):
        provider.fetch(_request(), timeout_seconds=True)

    malformed = _SyntheticOkxRequestData([[[_row(datetime(2026, 1, 1, tzinfo=UTC))[0], "bad"]]])
    with pytest.raises(OkxMarketHistoryProviderError, match="INVALID_OKX_HISTORY_ROW"):
        _provider(malformed).fetch(_request(), timeout_seconds=1.0)
    assert len(malformed.http_calls) == 1
