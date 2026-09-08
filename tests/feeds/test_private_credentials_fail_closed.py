"""Private OKX WebSockets reject incomplete credentials before transport I/O."""

from unittest.mock import Mock

import pytest
from bt_api_okx import registry_registration as registry
from bt_api_okx.feeds.live_okx.account_wss_base import OkxAccountWssData


@pytest.mark.parametrize(
    "credentials",
    [
        {},
        {"api_key": "fixture-key"},
        {"api_key": "fixture-key", "api_secret": "fixture-secret"},
        {"api_key": "fixture-key", "passphrase": "fixture-passphrase"},
        {"api_secret": "fixture-secret", "passphrase": "fixture-passphrase"},
    ],
)
def test_private_websocket_requires_all_credentials_before_construction(credentials):
    with pytest.raises(ValueError, match="key, secret and passphrase"):
        OkxAccountWssData(None, environment="demo", **credentials)


@pytest.mark.parametrize(
    "credentials",
    [
        {"api_key": "fixture-key"},
        {"api_key": "fixture-key", "api_secret": "fixture-secret"},
        {"api_secret": "fixture-secret", "passphrase": "fixture-passphrase"},
    ],
)
def test_partial_registry_credentials_fail_before_market_stream_construction(
    monkeypatch, credentials
):
    market = Mock(side_effect=AssertionError("market transport must not be constructed"))
    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", market)
    api = type("Api", (), {"_subscription_flags": {}, "event_bus": None})()

    with pytest.raises(ValueError, match="key, secret and passphrase"):
        registry._okx_swap_subscribe_handler(None, {"environment": "demo", **credentials}, [], api)
    market.assert_not_called()


@pytest.mark.parametrize(
    "credentials",
    [
        {
            "api_key": "fixture-key",
            "api_secret": "   ",
            "passphrase": "fixture-passphrase",
        },
        {
            "api_key": "fixture-key-a",
            "public_key": "fixture-key-b",
            "api_secret": "fixture-secret",
            "passphrase": "fixture-passphrase",
        },
    ],
)
def test_malformed_or_conflicting_registry_credentials_are_zero_transport(monkeypatch, credentials):
    market = Mock(side_effect=AssertionError("market transport must not be constructed"))
    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", market)
    api = type("Api", (), {"_subscription_flags": {}, "event_bus": None})()
    with pytest.raises(ValueError):
        registry._okx_swap_subscribe_handler(None, {"environment": "demo", **credentials}, [], api)
    market.assert_not_called()
