"""Module-level docstring."""
from __future__ import annotations

import pytest
from bt_api_okx.containers.tickers import OkxTickerData


@pytest.mark.ticker
def test_okx_ticker():
    """test_okx_ticker function"""
    data = {
        "instType": "SWAP",
        "instId": "LTC-USD-200327",
        "last": "9999.99",
        "lastSz": "0.1",
        "askPx": "9999.99",
        "askSz": "11",
        "bidPx": "8888.88",
        "bidSz": "5",
        "open24h": "9000",
        "high24h": "10000",
        "low24h": "8888.88",
        "volCcy24h": "2222",
        "vol24h": "2222",
        "sodUtc0": "2222",
        "sodUtc8": "2222",
        "ts": "1597026383085",
    }
    bt = OkxTickerData(data, "LTC-USD-200327", "PERPETUAL", has_been_json_encoded=True)
    bt.init_data()
    assert bt.get_server_time() == 1597026383085.0
    assert bt.get_exchange_name() == "OKX"
    assert bt.get_symbol_name() == "LTC-USD-200327"
    assert bt.get_bid_price() == 8888.88
    assert bt.get_bid_volume() == 5.0
    assert bt.get_ask_price() == 9999.99
    assert bt.get_ask_volume() == 11.0
    assert bt.get_last_price() == 9999.99
    assert bt.get_last_volume() == 0.1


def test_direct_market_projection_maps_ticker_fields_without_stream_cache():
    ticker = OkxTickerData(
        {
            "instType": "SWAP",
            "instId": "BTC-USDT-SWAP",
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
        "BTC-USDT-SWAP",
        "SWAP",
        has_been_json_encoded=True,
    )

    projected = ticker.get_market_projection()

    assert projected["instrument_id"] == projected["symbol"] == "BTC-USDT-SWAP"
    assert projected["timestamp"] == 1597026383.085
    assert projected["price"] == projected["last_price"] == 30000.0
    assert projected["bid_price"] == 29999.0
    assert projected["ask_price"] == 30001.0
    assert projected["bid_volume"] == 3.0
    assert projected["ask_volume"] == 4.0
    assert projected["volume"] == 12.5
    assert projected["turnover"] == 375000.0
    assert projected["open"] == 29800.0
    assert projected["high"] == 30500.0
    assert projected["low"] == 29000.0


if __name__ == "__main__":
    test_okx_ticker()
