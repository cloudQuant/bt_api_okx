"""OKX WSS 登录回执后订阅测试（B-14）。"""

from __future__ import annotations

import json


class _FakeExchangeData:
    exchange_name = "OKX"

    def get_wss_path(self, **kwargs):
        return json.dumps({"op": "subscribe", "args": [{"channel": kwargs["topic"]}]})


class _FakeWs:
    def __init__(self):
        self.sent = []
        self.restarted = False

    def send(self, data):
        self.sent.append(json.loads(data))

    def restart(self):
        self.restarted = True


def _make_client() -> tuple:
    from bt_api_okx.feeds.live_okx.market_wss_base import OkxWssData

    fake = _FakeWs()
    client = OkxWssData(
        None,
        public_key="pk",
        private_key="sk",
        passphrase="pp",
        wss_url="wss://example.com/private",
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


def test_login_failure_restarts() -> None:
    """login 失败回执触发 restart。"""
    client, fake = _make_client()

    client.open_rsp()
    client.message_rsp(json.dumps({"event": "login", "code": "60003"}))

    assert fake.restarted is True
