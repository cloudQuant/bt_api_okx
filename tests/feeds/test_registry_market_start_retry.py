"""Offline startup-retry contracts for public OKX market WebSockets."""

from types import SimpleNamespace

import pytest
from bt_api_okx import registry_registration as registry


def _api():
    return SimpleNamespace(_subscription_flags={}, _subscription_streams=[], event_bus=None)


def test_public_market_timeout_is_cleaned_before_fresh_retry(monkeypatch):
    instances = []
    first_timeout = TimeoutError("first public-market startup timeout")

    class Market:
        def __init__(self, queue, **kwargs):
            self.start_calls = 0
            self.stop_calls = 0
            instances.append(self)

        def start(self):
            self.start_calls += 1
            if self is instances[0]:
                raise first_timeout

        def stop(self):
            self.stop_calls += 1

    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", Market)
    api = _api()

    registry._okx_swap_subscribe_handler(None, {"environment": "demo"}, [], api)

    assert len(instances) == 2
    assert instances[0] is not instances[1]
    assert [stream.start_calls for stream in instances] == [1, 1]
    assert [stream.stop_calls for stream in instances] == [1, 0]
    assert api._subscription_streams == [instances[1]]
    assert "OKX___SWAP_subscription_cleanup_failed" not in api._subscription_flags


def test_two_public_market_timeouts_are_cleaned_and_final_timeout_is_preserved(monkeypatch):
    instances = []
    timeouts = [TimeoutError("first timeout"), TimeoutError("final timeout")]
    final_timeout = timeouts[-1]

    class Market:
        def __init__(self, queue, **kwargs):
            self.start_calls = 0
            self.stop_calls = 0
            instances.append(self)

        def start(self):
            self.start_calls += 1
            raise timeouts.pop(0)

        def stop(self):
            self.stop_calls += 1

    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", Market)
    api = _api()

    with pytest.raises(TimeoutError) as exc_info:
        registry._okx_swap_subscribe_handler(None, {"environment": "demo"}, [], api)

    assert exc_info.value is final_timeout
    assert len(instances) == 2
    assert [stream.start_calls for stream in instances] == [1, 1]
    assert [stream.stop_calls for stream in instances] == [1, 1]
    assert api._subscription_streams == []
    assert "OKX___SWAP_subscription_cleanup_failed" not in api._subscription_flags


def test_account_start_timeout_is_not_retried(monkeypatch):
    markets = []
    accounts = []
    account_timeout = TimeoutError("private account startup timeout")

    class Market:
        def __init__(self, queue, **kwargs):
            self.start_calls = 0
            self.stop_calls = 0
            markets.append(self)

        def start(self):
            self.start_calls += 1

        def stop(self):
            self.stop_calls += 1

    class Account:
        def __init__(self, queue, **kwargs):
            self.start_calls = 0
            self.stop_calls = 0
            accounts.append(self)

        def start(self):
            self.start_calls += 1
            raise account_timeout

        def stop(self):
            self.stop_calls += 1

    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", Market)
    monkeypatch.setattr(registry, "OkxAccountWssDataSwap", Account)
    api = _api()
    credentials = {
        "environment": "demo",
        "api_key": "fixture-key",
        "api_secret": "fixture-secret",
        "passphrase": "fixture-passphrase",
    }

    with pytest.raises(TimeoutError) as exc_info:
        registry._okx_swap_subscribe_handler(None, credentials, [], api)

    assert exc_info.value is account_timeout
    assert len(markets) == 1
    assert len(accounts) == 1
    assert markets[0].start_calls == 1
    assert accounts[0].start_calls == 1
    assert markets[0].stop_calls == accounts[0].stop_calls == 1
    assert api._subscription_streams == []
    assert "OKX___SWAP_account" not in api._subscription_flags
