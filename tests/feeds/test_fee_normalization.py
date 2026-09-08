"""OKX fee endpoint must preserve rate rows rather than build positions."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from bt_api_okx.feeds.live_okx.mixins.account_mixin_part2 import AccountMixinPart2


def _fee_harness():
    harness = AccountMixinPart2()
    harness.exchange_name = "OKX___SWAP"
    harness._params = SimpleNamespace(
        get_rest_path=lambda request_type: f"/{request_type}",
        get_symbol=lambda symbol: str(symbol).replace("/", "-").upper(),
    )
    return harness


def test_fee_normalizer_preserves_native_maker_and_taker_rates():
    row = {
        "instType": "SWAP",
        "instId": "BTC-USDT-SWAP",
        "maker": "-0.0002",
        "taker": "-0.0005",
        "makerU": "-0.0001",
        "takerU": "-0.0004",
    }

    result, status = AccountMixinPart2._get_fee_normalize_function(
        {"code": "0", "data": [row]},
        {"symbol_name": "BTC-USDT-SWAP", "asset_type": "SWAP"},
    )

    assert status is True
    assert result == [row]


def test_spot_fee_builder_normalizes_inst_id_without_derivative_scope():
    harness = _fee_harness()

    path, params, extra_data = harness._get_fee("SPOT", inst_id="btc/usdt")

    assert path == "/get_fee"
    assert params == {"instType": "SPOT", "instId": "BTC-USDT"}
    assert extra_data["symbol_name"] == "btc/usdt"


@pytest.mark.parametrize(
    ("selector", "expected"),
    [
        ({"inst_family": "btc/usdt"}, {"instFamily": "BTC-USDT"}),
        ({"group_id": 2}, {"groupId": "2"}),
        ({"uly": "btc/usdt"}, {"instFamily": "BTC-USDT"}),
    ],
)
def test_derivative_fee_builder_supports_family_or_group(selector, expected):
    harness = _fee_harness()

    _, params, _ = harness._get_fee("SWAP", **selector)

    assert params == {"instType": "SWAP", **expected}
    assert "instId" not in params
    assert "uly" not in params


@pytest.mark.parametrize(
    "kwargs,error",
    [
        (
            {"inst_type": "FUTURES", "inst_id": "BTC-USDT-261225"},
            "inst_id_only_applicable_to_spot_margin",
        ),
        (
            {"inst_type": "SWAP", "inst_family": "BTC-USDT", "group_id": "2"},
            "group_id_is_mutually_exclusive",
        ),
        (
            {"inst_type": "SPOT", "inst_family": "BTC-USDT"},
            "inst_family_only_applicable_to_derivatives",
        ),
    ],
)
def test_fee_builder_rejects_invalid_selector_combinations(kwargs, error):
    harness = _fee_harness()

    with pytest.raises(ValueError, match=error):
        harness._get_fee(**kwargs)


def test_legacy_swap_inst_id_is_sent_as_family_never_as_inst_id():
    harness = _fee_harness()

    _, params, _ = harness._get_fee("SWAP", inst_id="btc-usdt-swap")

    assert params == {"instType": "SWAP", "instFamily": "BTC-USDT"}
    assert "instId" not in params


def test_sync_and_async_fee_methods_forward_new_selectors():
    harness = _fee_harness()
    harness.request = Mock(return_value={"code": "0", "data": []})
    harness.async_request = Mock(return_value="pending")
    harness.submit = Mock()
    harness.async_callback = Mock()

    harness.get_fee("SWAP", group_id="2")
    harness.request.assert_called_once_with(
        "/get_fee",
        params={"instType": "SWAP", "groupId": "2"},
        extra_data=harness.request.call_args.kwargs["extra_data"],
    )

    harness.async_get_fee("SWAP", inst_family="BTC-USDT")
    harness.async_request.assert_called_once_with(
        "/get_fee",
        params={"instType": "SWAP", "instFamily": "BTC-USDT"},
        extra_data=harness.async_request.call_args.kwargs["extra_data"],
    )
    harness.submit.assert_called_once_with(
        "pending",
        callback=harness.async_callback,
    )
