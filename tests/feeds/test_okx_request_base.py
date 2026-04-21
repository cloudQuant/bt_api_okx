from unittest.mock import AsyncMock
import pytest
from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_okx.feeds.live_okx.request_base import OkxRequestData


def test_okx_defaults_exchange_name() -> None:
    request_data = OkxRequestData(
        None,
        public_key="public-key",
        private_key="secret-key",
        passphrase="passphrase",
    )

    assert request_data.exchange_name == "OKX___SWAP"


def test_okx_request_allows_missing_extra_data(monkeypatch) -> None:
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
    request_data = OkxRequestData(
        None,
        api_key="public-key",
        api_secret="secret-key",
        passphrase="passphrase",
    )

    assert request_data.public_key == "public-key"
    assert request_data.private_key == "secret-key"
