"""Offline requests capture verifies demo routing and signed bytes without credentials."""
import asyncio
import base64
import hashlib
import hmac
import json
import threading
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from bt_api_base.feeds.my_websocket_app import WebSocketSubscriptionError
from bt_api_okx.environment import configure_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap
from bt_api_okx.feeds.live_okx.account_wss_base import OkxAccountWssData
from bt_api_okx.feeds.live_okx.spot import OkxRequestDataSpot
from bt_api_okx.feeds.live_okx.swap import OkxMarketWssDataSwap, OkxRequestDataSwap


class _EventBus:
    def __init__(self):
        self.events = []

    def emit(self, event_type, payload):
        self.events.append((event_type, payload))


@pytest.mark.parametrize("cls", [OkxRequestDataSpot, OkxRequestDataSwap])
def test_environment_and_header_survive_subclass_initialization(cls):
    demo = cls(None, environment="demo")
    live = cls(None)
    assert demo._params.environment == "demo"
    assert demo.get_header("k", "s", "t", "p")["x-simulated-trading"] == "1"
    assert live.get_header("k", "s", "t", "p")["x-simulated-trading"] == "0"
    assert "wspap.okx.com" in demo._params.account_wss_url
    assert "wspap.okx.com" in demo._params.kline_wss_url
    assert "wspap.okx.com" not in live._params.account_wss_url


@pytest.mark.parametrize("options", [{"environment": "demmo"}, {"testnet": "false"},
                                    {"environment": "production", "demo": True},
                                    {"environment": "demo", "wss_url": "wss://ws.okx.com/ws/v5/public"}])
def test_invalid_or_conflicting_environment_is_rejected(options):
    with pytest.raises(ValueError):
        OkxRequestDataSwap(None, **options)


def test_demo_config_does_not_mutate_shared_exchange_data():
    original = OkxExchangeDataSwap()
    demo = configure_environment(original, {"testnet": True})
    assert demo.environment == "demo"
    assert original.account_wss_url == "wss://ws.okx.com:8443/ws/v5/private"


def test_public_metadata_and_depth_need_no_keys(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock(return_value={"code": "0", "data": []})
    monkeypatch.setattr(feed, "http_request", request)
    feed.get_exchange_info("BTC-USDT-SWAP")
    assert "instType=SWAP" in request.call_args.args[1]
    assert "instId=BTC-USDT-SWAP" in request.call_args.args[1]
    headers = request.call_args.args[2]
    assert headers == {"Content-Type": "application/json", "x-simulated-trading": "1"}
    feed.get_depth("BTC-USDT-SWAP", count=5)
    assert "instId=BTC-USDT-SWAP" in request.call_args.args[1]


def test_private_missing_keys_fails_before_network(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock()
    monkeypatch.setattr(feed, "http_request", request)
    with pytest.raises(ValueError, match="private requests require"):
        feed.get_account()
    request.assert_not_called()


def test_ioc_contract_quantity_reduce_only_and_signed_wire_bytes():
    feed = OkxRequestDataSwap(None, environment="demo", api_key="fixture-key",
                             api_secret="fixture-secret", passphrase="fixture-phrase")
    captured = []
    def respond(request):
        captured.append(request)
        return httpx.Response(200, json={"code": "0", "data": [{"sCode": "0", "ordId": "1"}]})
    feed._http_client._sync_client.close()
    feed._http_client._sync_client = httpx.Client(transport=httpx.MockTransport(respond))
    feed.make_order("BTC-USDT-SWAP", 2, price=60000, order_type="buy-limit",
                    size_in_contracts=True, time_in_force="IOC", reduce_only=True)
    req = captured[0]
    body = json.loads(req.content)
    assert body["sz"] == "2" and body["ordType"] == "ioc"
    assert body["reduceOnly"] == "true"
    assert req.headers["x-simulated-trading"] == "1"
    content = req.headers["OK-ACCESS-TIMESTAMP"] + "POST" + req.url.raw_path.decode() + req.content.decode()
    expected = base64.b64encode(hmac.new(b"fixture-secret", content.encode(), hashlib.sha256).digest()).decode()
    assert req.headers["OK-ACCESS-SIGN"] == expected
    feed._http_client.close()


def test_mutating_order_timeout_is_not_retried():
    feed = OkxRequestDataSwap(None, environment="demo", api_key="fixture-key",
                             api_secret="fixture-secret", passphrase="fixture-phrase")
    captured = []
    def timeout(request):
        captured.append(request)
        raise httpx.ReadTimeout("simulated response loss", request=request)
    feed._http_client._sync_client.close()
    feed._http_client._sync_client = httpx.Client(transport=httpx.MockTransport(timeout))
    with pytest.raises(Exception):
        feed.make_order("BTC-USDT-SWAP", 1, price=60000, size_in_contracts=True)
    assert len(captured) == 1
    feed._http_client.close()


def test_async_demo_header_and_signature_match_transmitted_body(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo", api_key="fixture-key",
                             api_secret="fixture-secret", passphrase="fixture-phrase")
    request = AsyncMock(return_value={"code": "0", "data": []})
    monkeypatch.setattr(feed, "async_http_request", request)
    asyncio.run(feed.async_request("POST /api/v5/trade/order", body={"instId": "BTC-USDT-SWAP", "sz": "1"}))
    method, url, headers, body, timeout = request.call_args.args
    expected = feed.signature(headers["OK-ACCESS-TIMESTAMP"], method, "/api/v5/trade/order", "fixture-secret", body)
    assert headers["OK-ACCESS-SIGN"] == expected
    assert headers["x-simulated-trading"] == "1" and not url.endswith("?")


def test_websocket_login_uses_epoch_seconds_and_demo_private_channel(monkeypatch):
    feed = OkxAccountWssData(None, environment="demo", api_key="fixture-key",
                            api_secret="fixture-secret", passphrase="fixture-phrase")
    feed.ws = Mock()
    monkeypatch.setattr("bt_api_okx.feeds.live_okx.market_wss_base.time.time", lambda: 1788000000.123)
    feed.author()
    assert feed.wss_url == "wss://wspap.okx.com:8443/ws/v5/private"
    payload = json.loads(feed.ws.send.call_args.args[0])["args"][0]
    assert payload["timestamp"] == "1788000000"
    assert payload["sign"] == feed.sign("1788000000GET/users/self/verify")


def test_swap_account_subscription_uses_okx_account_channel_schema():
    request = json.loads(
        OkxExchangeDataSwap().get_wss_path(topic="account", currency="USDT")
    )

    assert request == {
        "op": "subscribe",
        "args": [{"channel": "account", "ccy": "USDT"}],
    }


def test_subscription_routes_public_private_separately_and_retains_streams(monkeypatch):
    from bt_api_okx import registry_registration as registry
    instances = []
    class Stream:
        def __init__(self, queue, **kwargs):
            self.options = kwargs
            instances.append(self)
        def start(self):
            pass
    monkeypatch.setattr(registry, "OkxMarketWssDataSwap", Stream)
    monkeypatch.setattr(registry, "OkxAccountWssDataSwap", Stream)
    event_bus = object()
    api = SimpleNamespace(_subscription_flags={}, event_bus=event_bus)
    registry._okx_swap_subscribe_handler(
        None,
        {
            "environment": "demo",
            "api_key": "fixture-key",
            "api_secret": "fixture-secret",
            "passphrase": "fixture-passphrase",
            "message_idle_timeout": 5,
        },
        [],
        api,
    )
    assert instances[0].options["wss_url"].endswith("/public")
    assert instances[1].options["wss_url"].endswith("/private")
    assert all("wspap.okx.com" in item.options["wss_url"] for item in instances)
    assert all(item.options["event_bus"] is event_bus for item in instances)
    assert instances[0].options["message_idle_timeout"] == 5
    assert instances[1].options["message_idle_timeout"] == 0
    assert [item.options["wss_name"] for item in instances] == [
        "okx_swap_market_data",
        "okx_swap_account_data",
    ]
    assert [item.options["stream_role"] for item in instances] == [
        "market",
        "account",
    ]
    assert api._subscription_streams == instances


def test_subscription_start_failure_stops_all_new_streams_without_retaining(monkeypatch):
    from bt_api_okx import registry_registration as registry

    instances = []

    class Stream:
        def __init__(self, queue, *, fail=False, **kwargs):
            self.fail = fail
            self.stopped = False
            instances.append(self)

        def start(self):
            if self.fail:
                raise RuntimeError("account start failed")

        def stop(self):
            self.stopped = True

    monkeypatch.setattr(
        registry,
        "OkxMarketWssDataSwap",
        lambda queue, **kwargs: Stream(queue, **kwargs),
    )
    monkeypatch.setattr(
        registry,
        "OkxAccountWssDataSwap",
        lambda queue, **kwargs: Stream(queue, fail=True, **kwargs),
    )
    api = SimpleNamespace(_subscription_flags={}, _subscription_streams=[], event_bus=object())

    with pytest.raises(RuntimeError, match="account start failed"):
        registry._okx_swap_subscribe_handler(
            None,
            {
                "environment": "demo",
                "api_key": "fixture-key",
                "api_secret": "fixture-secret",
                "passphrase": "fixture-passphrase",
            },
            [],
            api,
        )

    assert len(instances) == 2
    assert all(stream.stopped for stream in instances)
    assert api._subscription_streams == []
    assert "OKX___SWAP_account" not in api._subscription_flags


def test_subscription_cleanup_failure_retains_survivor_and_blocks_retry(monkeypatch):
    from bt_api_okx import registry_registration as registry

    instances = []

    class Stream:
        def __init__(self, queue, *, fail_start=False, fail_stop=False, **kwargs):
            self.fail_start = fail_start
            self.fail_stop = fail_stop
            instances.append(self)

        def start(self):
            if self.fail_start:
                raise RuntimeError("account start failed")

        def stop(self):
            if self.fail_stop:
                raise RuntimeError("market stop failed")

    monkeypatch.setattr(
        registry,
        "OkxMarketWssDataSwap",
        lambda queue, **kwargs: Stream(queue, fail_stop=True, **kwargs),
    )
    monkeypatch.setattr(
        registry,
        "OkxAccountWssDataSwap",
        lambda queue, **kwargs: Stream(queue, fail_start=True, **kwargs),
    )
    api = SimpleNamespace(_subscription_flags={}, _subscription_streams=[], event_bus=object())
    options = {
        "environment": "demo",
        "api_key": "fixture-key",
        "api_secret": "fixture-secret",
        "passphrase": "fixture-passphrase",
    }

    with pytest.raises(RuntimeError, match="could not be stopped"):
        registry._okx_swap_subscribe_handler(None, options, [], api)

    assert api._subscription_streams == [instances[0]]
    assert api._subscription_flags["OKX___SWAP_subscription_cleanup_failed"] is True
    with pytest.raises(RuntimeError, match="Close BtApi"):
        registry._okx_swap_subscribe_handler(None, options, [], api)
    assert len(instances) == 2


def test_market_stream_becomes_ready_only_after_okx_subscription_ack():
    event_bus = _EventBus()
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
        event_bus=event_bus,
    )
    feed.ws = Mock()

    assert feed.open_rsp() is False
    assert feed._pending_subscription_acks == 1
    assert not feed._running_flag

    argument = json.loads(feed.ws.send.call_args.args[0])["args"][0]
    feed.message_rsp(json.dumps({"event": "subscribe", "code": "0", "arg": argument}))

    assert feed._running_flag
    assert feed._pending_subscription_acks == 0
    assert [event for event, _ in event_bus.events] == ["ws.connected"]


def test_market_stream_accepts_okx_ack_without_optional_swap_inst_type():
    event_bus = _EventBus()
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
        event_bus=event_bus,
    )
    feed.ws = Mock()

    assert feed.open_rsp() is False
    argument = json.loads(feed.ws.send.call_args.args[0])["args"][0]
    assert argument["instType"] == "SWAP"
    del argument["instType"]

    feed.message_rsp(json.dumps({"event": "subscribe", "code": "0", "arg": argument}))

    assert feed._running_flag
    assert feed._pending_subscription_acks == 0
    assert [event for event, _ in event_bus.events] == ["ws.connected"]


@pytest.mark.parametrize(
    ("field", "value", "omit_inst_type"),
    [
        ("channel", "books50-l2-tbt", True),
        ("instId", "ETH-USDT-SWAP", True),
        ("instType", "SPOT", False),
    ],
)
def test_okx_subscribe_ack_with_mismatched_argument_is_ignored(field, value, omit_inst_type):
    event_bus = _EventBus()
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
        event_bus=event_bus,
    )
    feed.ws = Mock()
    assert feed.open_rsp() is False

    argument = json.loads(feed.ws.send.call_args.args[0])["args"][0]
    if omit_inst_type:
        del argument["instType"]
    argument[field] = value
    feed.message_rsp(json.dumps({"event": "subscribe", "code": "0", "arg": argument}))

    assert not feed._running_flag
    assert feed._pending_subscription_acks == 1
    assert [event for event, _ in event_bus.events] == ["ws.subscription_ack_ignored"]


def test_okx_duplicate_pending_subscription_is_still_rejected():
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
    )
    feed.ws = Mock()
    assert feed.open_rsp() is False

    with pytest.raises(WebSocketSubscriptionError, match="Duplicate OKX WebSocket subscription"):
        feed.subscribe(topic="depth", symbol="BTC-USDT-SWAP")

    assert feed.ws.send.call_count == 1


def test_okx_subscribe_ack_without_exact_argument_is_ignored():
    event_bus = _EventBus()
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
        event_bus=event_bus,
    )
    feed.ws = Mock()
    assert feed.open_rsp() is False

    feed.message_rsp(json.dumps({"event": "subscribe", "code": "0"}))

    assert not feed._running_flag
    assert feed._pending_subscription_acks == 1
    assert [event for event, _ in event_bus.events] == ["ws.subscription_ack_ignored"]


def test_okx_account_application_ping_pong_keeps_current_generation_open():
    event_bus = _EventBus()
    feed = OkxAccountWssData(
        None,
        environment="demo",
        api_key="fixture-key",
        api_secret="fixture-secret",
        passphrase="fixture-passphrase",
        event_bus=event_bus,
        okx_application_ping_interval=0.2,
        okx_application_pong_timeout=0.04,
    )
    socket = Mock()
    feed.ws = socket
    feed._connection_generation = 1
    feed._running_flag = True
    feed._last_message_at = time.monotonic() - 1.0
    worker = threading.Thread(target=feed._okx_application_heartbeat, daemon=True)
    worker.start()

    deadline = time.monotonic() + 1.0
    while not socket.send.called and time.monotonic() < deadline:
        time.sleep(0.01)
    socket.send.assert_called_once_with("ping")
    feed.on_message(socket, "pong")
    time.sleep(0.06)
    feed._stop_event.set()
    worker.join(1.0)

    socket.close.assert_not_called()
    assert feed._okx_ping_sent_at is None


def test_okx_account_missing_application_pong_closes_only_current_generation():
    event_bus = _EventBus()
    feed = OkxAccountWssData(
        None,
        environment="demo",
        api_key="fixture-key",
        api_secret="fixture-secret",
        passphrase="fixture-passphrase",
        event_bus=event_bus,
        okx_application_ping_interval=0.03,
        okx_application_pong_timeout=0.03,
    )
    socket = Mock()
    feed.ws = socket
    feed._connection_generation = 2
    feed._running_flag = True
    feed._last_message_at = time.monotonic() - 1.0
    worker = threading.Thread(target=feed._okx_application_heartbeat, daemon=True)
    worker.start()

    deadline = time.monotonic() + 1.0
    while not socket.close.called and time.monotonic() < deadline:
        time.sleep(0.01)
    feed._stop_event.set()
    worker.join(1.0)

    socket.send.assert_called_once_with("ping")
    socket.close.assert_called_once_with()
    event, payload = event_bus.events[-1]
    assert event == "ws.application_pong_timeout"
    assert payload["heartbeat_generation"] == 2


def test_duplicate_okx_ack_does_not_make_multi_topic_stream_ready():
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[
            {"topic": "depth", "symbol": "BTC-USDT-SWAP"},
            {"topic": "funding_rate", "symbol": "BTC-USDT-SWAP"},
        ],
    )
    feed.ws = Mock()

    assert feed.open_rsp() is False
    arguments = [json.loads(call.args[0])["args"][0] for call in feed.ws.send.call_args_list]
    assert len(arguments) == 2

    first_ack = json.dumps({"event": "subscribe", "arg": arguments[0]})
    feed.message_rsp(first_ack)
    feed.message_rsp(first_ack)

    assert feed._pending_subscription_acks == 1
    assert not feed._running_flag

    feed.message_rsp(json.dumps({"event": "subscribe", "arg": arguments[1]}))
    assert feed._running_flag


def test_unsupported_okx_topic_never_becomes_ready():
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "unsupported_fixture"}],
    )
    feed.ws = Mock()

    with pytest.raises(RuntimeError, match="Unsupported or incomplete"):
        feed.open_rsp()

    feed.ws.send.assert_not_called()
    assert not feed._running_flag


def test_empty_okx_market_subscription_never_becomes_ready():
    feed = OkxMarketWssDataSwap(None, environment="demo", topics=[])
    feed.ws = Mock()

    with pytest.raises(RuntimeError, match="at least one topic"):
        feed.open_rsp()

    feed.ws.send.assert_not_called()
    assert not feed._running_flag


def test_okx_subscription_error_closes_stream_and_emits_failure():
    event_bus = _EventBus()
    feed = OkxMarketWssDataSwap(
        None,
        environment="demo",
        topics=[{"topic": "depth", "symbol": "BTC-USDT-SWAP"}],
        event_bus=event_bus,
    )
    feed.ws = Mock()
    feed.open_rsp()

    feed.on_message(
        feed.ws,
        json.dumps({"event": "error", "code": "60012", "msg": "invalid request"}),
    )

    assert not feed._running_flag
    feed.ws.close.assert_called_once_with()
    assert feed._stop_event.is_set()
    assert [event for event, _ in event_bus.events] == ["ws.subscription_error"]


def test_all_account_positions_and_orders_omit_symbol_filter(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo", api_key="fixture-key",
                             api_secret="fixture-secret", passphrase="fixture-phrase")
    response = {"code": "0", "data": []}
    request = Mock(return_value=response)
    monkeypatch.setattr(feed, "http_request", request)
    feed.get_position(None)
    assert "instId=" not in request.call_args.args[1]
    assert "None" not in request.call_args.args[1]
    feed.get_open_orders(None)
    assert "ALL" not in request.call_args.args[1] and "None" not in request.call_args.args[1]
    extra = {"symbol_name": None, "asset_type": "SWAP"}
    raw = {"code": "0", "data": [{"instId": "BTC-USDT-SWAP"}, {"instId": "ETH-USDT-SWAP"}]}
    positions, ok = feed._get_position_normalize_function(raw, extra)
    assert ok and len(positions) == 2
    assert [position.symbol_name for position in positions] == ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]
