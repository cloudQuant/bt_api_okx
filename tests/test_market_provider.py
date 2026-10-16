"""Owner-thread provider queue coverage using the existing OKX ticker container."""

from __future__ import annotations

import pytest
from bt_api_base.market_protocol import MarketInstrumentKey, MarketSubscriptionKey
from bt_api_okx.containers.tickers import OkxTickerData
from bt_api_okx.market_provider import (
    BoundedOkxTickerQueue,
    OkxTickerQueueMarketProvider,
)


def _key(**changes: object) -> MarketSubscriptionKey:
    instrument_fields: dict[str, str] = {
        "provider": "okx",
        "venue": "OKX",
        "environment": "live",
        "product_type": "SWAP",
        "instrument_id": "BTC-USDT-SWAP",
        "native_symbol": "BTC-USDT-SWAP",
    }
    instrument_fields.update(changes.pop("instrument", {}))  # type: ignore[arg-type]
    values: dict[str, object] = {
        "source_ref": "okx-public-market-r1",
        "entitlement_ref": "public-ticker-r1",
        "instrument": MarketInstrumentKey(**instrument_fields),
        "channel": "tickers",
    }
    values.update(changes)
    return MarketSubscriptionKey(**values)  # type: ignore[arg-type]


def _ticker(symbol: str = "BTC-USDT-SWAP") -> OkxTickerData:
    return OkxTickerData(
        {
            "instType": "SWAP",
            "instId": symbol,
            "last": "30000",
            "bidPx": "29999",
            "askPx": "30001",
            "bidSz": "3",
            "askSz": "4",
            "vol24h": "12.5",
            "volCcy24h": "375000",
            "open24h": "29800",
            "high24h": "30500",
            "low24h": "29000",
            "ts": "1597026383085",
        },
        symbol,
        "SWAP",
        has_been_json_encoded=True,
    )


class _Stream:
    def __init__(self) -> None:
        self.started_with: list[float] = []
        self.stop_calls = 0
        self.start_error: Exception | None = None
        self.stop_error: Exception | None = None

    def start(self, *, connect_timeout: float) -> None:
        self.started_with.append(connect_timeout)
        if self.start_error is not None:
            raise self.start_error

    def stop(self) -> None:
        self.stop_calls += 1
        if self.stop_error is not None:
            raise self.stop_error


def test_bounded_queue_drops_oldest_without_blocking_the_wss_callback() -> None:
    queue = BoundedOkxTickerQueue(capacity=2)

    queue.put("first", block=True)
    queue.put("second", block=True)
    queue.put("third", block=True)

    assert queue.dropped_oldest == 1
    assert queue.size == 2
    assert queue.drain(2) == ("second", "third")


def test_okx_ticker_provider_maps_existing_queue_to_market_provider_event() -> None:
    key = _key()
    stream = _Stream()
    captured: list[BoundedOkxTickerQueue] = []

    def factory(received_key: MarketSubscriptionKey, queue: BoundedOkxTickerQueue) -> _Stream:
        assert received_key == key
        captured.append(queue)
        return stream

    provider = OkxTickerQueueMarketProvider(stream_factory=factory, connect_timeout=2.5)
    handle = provider.subscribe(key, generation="hub-generation-1")
    captured[0].put(_ticker())

    (event,) = provider.poll(handle, limit=1)
    projection = _ticker().get_market_projection()

    assert stream.started_with == [2.5]
    assert event.generation == "hub-generation-1"
    assert event.observed_at_utc == "2020-08-10T02:26:23.085000Z"
    assert dict(event.data) == projection
    assert provider.unsubscribe(handle) is True
    assert stream.stop_calls == 1
    assert provider.poll(handle, limit=1) == ()


def test_provider_refuses_keys_outside_the_configured_okx_swap_ticker_contract() -> None:
    created: list[object] = []
    provider = OkxTickerQueueMarketProvider(
        stream_factory=lambda _key, _queue: created.append(object())
    )

    with pytest.raises(ValueError, match="UNSUPPORTED_OKX_MARKET_KEY"):
        provider.subscribe(_key(channel="trades"), generation="generation-1")

    assert created == []


def test_failed_start_retains_uncertain_stream_and_blocks_duplicate_acquisition() -> None:
    key = _key()
    stream = _Stream()
    stream.start_error = RuntimeError("start did not become ready")
    stream.stop_error = RuntimeError("stop outcome uncertain")
    creations = 0

    def factory(_key: MarketSubscriptionKey, _queue: BoundedOkxTickerQueue) -> _Stream:
        nonlocal creations
        creations += 1
        return stream

    provider = OkxTickerQueueMarketProvider(stream_factory=factory)
    with pytest.raises(RuntimeError, match="start did not become ready"):
        provider.subscribe(key, generation="generation-1")
    assert provider.diagnostics["pending_start_cleanup"] == 1
    with pytest.raises(RuntimeError, match="OKX_STARTUP_CLEANUP_PENDING"):
        provider.subscribe(key, generation="generation-2")
    assert creations == 1

    stream.stop_error = None
    stream.start_error = None
    handle = provider.subscribe(key, generation="generation-2")
    assert creations == 2
    assert provider.diagnostics["pending_start_cleanup"] == 0
    assert provider.unsubscribe(handle) is True
