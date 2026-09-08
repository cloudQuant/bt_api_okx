"""Offline coverage for account-scoped order-readiness endpoints."""

from __future__ import annotations

from unittest.mock import Mock

from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap


def _feed(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock(return_value=object())
    monkeypatch.setattr(feed, "request", request)
    return feed, request


def test_account_instruments_uses_private_account_endpoint(monkeypatch):
    feed, request = _feed(monkeypatch)

    feed.get_account_instruments("BTC-USDT-SWAP")

    assert request.call_args.args[0] == "GET /api/v5/account/instruments"
    assert request.call_args.kwargs["params"] == {
        "instType": "SWAP",
        "instId": "BTC-USDT-SWAP",
    }
    assert request.call_args.kwargs["extra_data"]["request_type"] == "get_instruments"
    feed._http_client.close()


def test_leverage_info_uses_instrument_and_margin_mode(monkeypatch):
    feed, request = _feed(monkeypatch)

    feed.get_leverage_info("BTC-USDT-SWAP", margin_mode="cross")

    assert request.call_args.args[0] == "GET /api/v5/account/leverage-info"
    assert request.call_args.kwargs["params"] == {
        "instId": "BTC-USDT-SWAP",
        "mgnMode": "cross",
    }
    assert request.call_args.kwargs["extra_data"]["request_type"] == "get_lever"
    feed._http_client.close()


def test_max_size_uses_native_contract_limit_endpoint(monkeypatch):
    feed, request = _feed(monkeypatch)

    feed.get_max_size("BTC-USDT-SWAP", "cross")

    assert request.call_args.args[0] == "GET /api/v5/account/max-size"
    assert request.call_args.kwargs["params"] == {
        "instId": "BTC-USDT-SWAP",
        "tdMode": "cross",
    }
    assert request.call_args.kwargs["extra_data"]["request_type"] == "get_max_size"
    feed._http_client.close()
