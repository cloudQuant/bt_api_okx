"""Module-level docstring."""
from unittest.mock import AsyncMock
import pytest
from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_okx.feeds.live_okx.request_base import OkxRequestData


def test_okx_defaults_exchange_name() -> None:
    """test_okx_defaults_exchange_name function"""
    request_data = OkxRequestData(
        None,
        public_key="public-key",
        private_key="secret-key",
        passphrase="passphrase",
    )

    assert request_data.exchange_name == "OKX___SWAP"


def test_okx_request_allows_missing_extra_data(monkeypatch) -> None:
    """test_okx_request_allows_missing_extra_data function"""
    request_data = OkxRequestData(
        None,
        public_key="public-key",
        private_key="secret-key",
        passphrase="passphrase",
        exchange_name="OKX___SWAP",
    )

    monkeypatch.setattr(
        request_data,
        "http_request",
        lambda method, url, headers, body, timeout: {"code": "0", "data": []},
    )

    result = request_data.request("GET /api/v5/public/time")

    assert isinstance(result, RequestData)
    assert result.get_extra_data() == {}
    assert result.get_input_data() == {"code": "0", "data": []}


def test_okx_accepts_api_key_and_api_secret_aliases() -> None:
    """test_okx_accepts_api_key_and_api_secret_aliases function"""
    request_data = OkxRequestData(
        None,
        api_key="public-key",
        api_secret="secret-key",
        passphrase="passphrase",
    )

    assert request_data.public_key == "public-key"
    assert request_data.private_key == "secret-key"


def test_okx_sign_golden_vector() -> None:
    """OKX V5 签名黄金向量：Base64(HMAC-SHA256(timestamp+method+path+body, secret))。

    复算命令：
    python3 -c "import hmac,hashlib,base64; s='F0E1D2C3B4A5968778695A4B3C2D1E0F'; pre='2020-12-08T09:08:57.715ZGET/api/v5/account/balance'; print(base64.b64encode(hmac.new(s.encode(),pre.encode(),hashlib.sha256).digest()).decode())"
    """
    from bt_api_okx.feeds.live_okx.request_base import _sign

    secret = "F0E1D2C3B4A5968778695A4B3C2D1E0F"
    timestamp = "2020-12-08T09:08:57.715Z"
    assert _sign(secret, timestamp, "GET", "/api/v5/account/balance", "") == (
        "ymzav0cu8v4AhecjpRnt8sRQ8vOk/6+BT89eeU/sIjQ="
    )


def test_okx_timestamp_is_iso8601() -> None:
    """OK-ACCESS-TIMESTAMP 必须是 ISO 8601 毫秒格式（非 epoch 浮点）。"""
    import re

    from bt_api_okx.feeds.live_okx.request_base import _utc_now_iso8601

    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", _utc_now_iso8601())
