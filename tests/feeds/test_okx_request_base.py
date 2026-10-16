"""Module-level docstring."""

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


def _make_okx_request_data() -> OkxRequestData:
    return OkxRequestData(None, public_key="pk", private_key="sk", passphrase="pp")


def test_okx_error_response_raises_translated_error() -> None:
    """API 错误(code != "0")必须翻译为 UnifiedError 并抛出。"""
    from bt_api_base.error import UnifiedError

    request_data = _make_okx_request_data()
    with pytest.raises(UnifiedError):
        request_data._raise_if_error({"code": "1", "msg": "Operation failed."})


def test_okx_error_response_raises_rate_limit() -> None:
    from bt_api_base.error import UnifiedError

    request_data = _make_okx_request_data()
    with pytest.raises(UnifiedError):
        request_data._raise_if_error({"code": "50011", "msg": "Rate limit exceeded."})


def test_okx_success_response_does_not_raise() -> None:
    """成功响应(code == "0")不抛异常。"""
    request_data = _make_okx_request_data()
    request_data._raise_if_error({"code": "0", "data": []})


def test_direct_symbol_info_merges_swap_contract_and_fee_metadata(monkeypatch) -> None:
    from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData

    request_data = OkxRequestData(
        None,
        public_key="pk",
        private_key="sk",
        passphrase="pp",
        asset_type="SWAP",
    )
    instrument = OkxSymbolData(
        {
            "instId": "BTC-USDT-SWAP",
            "instType": "SWAP",
            "baseCcy": "BTC",
            "quoteCcy": "USDT",
            "ctMult": "100",
            "ctVal": "0.01",
            "ctValCcy": "BTC",
            "ctType": "linear",
            "instFamily": "BTC-USDT",
            "tickSz": "0.1",
            "lotSz": "0.01",
            "minSz": "0.01",
            "lever": "20",
            "state": "live",
        },
        True,
    )
    fee_calls = []
    monkeypatch.setattr(
        request_data,
        "get_instruments",
        lambda **kwargs: [instrument],
    )
    monkeypatch.setattr(
        request_data,
        "get_fee",
        lambda **kwargs: fee_calls.append(kwargs)
        or {"code": "0", "data": [{"makerU": "0.0002", "takerU": "0.0005"}]},
    )

    spec = request_data.get_symbol_info("BTC-USDT-SWAP")

    assert spec["source"] == "okx_get_instruments"
    assert spec["symbol"] == "BTC-USDT-SWAP"
    assert spec["base_asset"] == "BTC"
    assert spec["quote_asset"] == "USDT"
    assert spec["contract_value_currency"] == "BTC"
    assert spec["contract_notional_value"] == spec["multiplier"] == 0.01
    assert spec["contract_multiplier_raw"] == 100.0
    assert spec["price_tick"] == spec["tick_size"] == 0.1
    assert spec["min_order_size"] == 0.01
    assert spec["order_size_step"] == 0.01
    assert spec["max_leverage"] == 20.0
    assert spec["symbol_status"] == "live"
    assert spec["maker_commission_rate"] == -0.0002
    assert spec["taker_commission_rate"] == spec["commission_rate"] == -0.0005
    assert spec["fee_source"] == "okx_get_fee"
    assert fee_calls == [{"inst_type": "SWAP", "inst_family": "BTC-USDT"}]


def test_direct_symbol_info_spot_defaults_multiplier_and_normalizes_fee_sign(monkeypatch) -> None:
    from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData

    request_data = OkxRequestData(
        None,
        public_key="pk",
        private_key="sk",
        passphrase="pp",
        asset_type="SPOT",
    )
    instrument = OkxSymbolData(
        {
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "baseCcy": "BTC",
            "quoteCcy": "USDT",
            "tickSz": "0.1",
            "lotSz": "0.001",
            "minSz": "0.001",
            "state": "live",
        },
        True,
    )
    monkeypatch.setattr(request_data, "get_instruments", lambda **_kwargs: [instrument])
    monkeypatch.setattr(
        request_data,
        "get_fee",
        lambda **kwargs: {"code": "0", "data": [{"maker": "0.001", "taker": "0.002"}]},
    )

    spec = request_data.get_symbol_info("BTC/USDT")

    assert spec["symbol"] == "BTC-USDT"
    assert spec["multiplier"] == spec["contract_multiplier"] == 1.0
    assert spec["maker_commission_rate"] == -0.001
    assert spec["taker_commission_rate"] == -0.002
