"""OKX WSS 登录回执后订阅测试（B-14）。"""

from __future__ import annotations

import json
from unittest.mock import Mock

import websocket
from bt_api_base.logging_factory import _LoggerProxy


class _FakeExchangeData:
    exchange_name = "OKX"

    def get_wss_path(self, **kwargs):
        return json.dumps({"op": "subscribe", "args": [{"channel": kwargs["topic"]}]})


class _FakeWs:
    def __init__(self):
        self.sent = []
        self.closed = False

    def send(self, data):
        self.sent.append(json.loads(data))

    def close(self):
        self.closed = True


def _make_client() -> tuple:
    from bt_api_okx.feeds.live_okx.account_wss_base import OkxAccountWssData

    fake = _FakeWs()
    client = OkxAccountWssData(
        None,
        public_key="pk",
        private_key="sk",
        passphrase="pp",  # noqa: S106 - inert test fixture
        wss_url="wss://ws.okx.com:8443/ws/v5/private",
        exchange_data=_FakeExchangeData(),
    )
    client.ws = fake
    client.topics = [{"topic": "ticker", "symbol": "BTC-USDT"}]
    return client, fake


def test_open_rsp_does_not_subscribe_before_login_ack() -> None:
    """私有 WSS：open_rsp 先发 login，收到 login 回执后才订阅（不再 sleep(0.3)）。"""
    client, fake = _make_client()

    client.open_rsp()

    assert fake.sent[0]["op"] == "login"  # 先发 login
    assert len(fake.sent) == 1  # 登录回执前不订阅


def test_login_ack_triggers_subscribe() -> None:
    """收到 login 成功回执后触发订阅。"""
    client, fake = _make_client()

    client.open_rsp()
    client.message_rsp(json.dumps({"event": "login", "code": "0"}))

    assert len(fake.sent) >= 2
    assert fake.sent[1]["op"] == "subscribe"


def test_login_ack_still_subscribes_when_logging_sink_fails() -> None:
    class _FailingSink:
        @staticmethod
        def info(_message: str) -> None:
            raise OSError("log volume unavailable")

    client, fake = _make_client()
    client.wss_logger = _LoggerProxy(_FailingSink())

    client.open_rsp()
    client.message_rsp(json.dumps({"event": "login", "code": "0"}))

    assert fake.sent[1]["op"] == "subscribe"
    assert client.wss_logger.sink_failure_count >= 1


def test_login_failure_closes_real_websocket_app_contract() -> None:
    """login 失败回执触发 restart。"""
    client, _fake = _make_client()
    socket = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/private")
    socket.close = Mock()
    client.ws = socket

    client.message_rsp(json.dumps({"event": "login", "code": "60003"}))

    assert not hasattr(socket, "restart")
    socket.close.assert_called_once_with()
    assert client._running_flag is False
    assert client._stop_event.is_set()
