"""Swap quantity conversion and local order validation semantics.

Regression tests for two silent-failure paths in OKX order placement:

1. A base-quantity order for a symbol missing from the conversion table must
   raise ``InvalidOrderError`` instead of silently sending the base size as a
   contract count (notional off by ``ctVal``).
2. Local parameter validation failures (post_only + IOC/FOK, unsupported
   time_in_force) must raise ``InvalidOrderError`` so the normalized layer
   classifies them as ``definite_reject`` instead of ``execution_unknown``.
"""

from __future__ import annotations

import pytest
from bt_api_base.exceptions import InvalidOrderError
from bt_api_okx.feeds.live_okx.mixins.trade_mixin import TradeMixin


class _SwapOrderParams:
    # Deliberately empty: BTC-USDT-SWAP has no base->contract multiplier here,
    # mirroring the production table which only carries spot symbols.
    symbol_leverage_dict: dict[str, float] = {}

    @staticmethod
    def get_symbol(symbol):
        return symbol

    @staticmethod
    def get_rest_path(_request_type):
        return "/api/v5/trade/order"


class _SpotOrderParams(_SwapOrderParams):
    symbol_leverage_dict = {"BTC-USDT": 100}


class _NoopLogger:
    @staticmethod
    def warning(_message):
        return None


class _OrderFeed(TradeMixin):
    exchange_name = "OKX"

    def __init__(self, params) -> None:
        self.asset_type = "SWAP"
        self._params = params
        self.request_logger = _NoopLogger()


def test_base_unit_swap_without_conversion_table_raises_invalid_order():
    feed = _OrderFeed(_SwapOrderParams())

    with pytest.raises(InvalidOrderError):
        feed._make_order("BTC-USDT-SWAP", 0.002, 60000, "buy-limit")


def test_base_unit_swap_error_carries_symbol_context():
    feed = _OrderFeed(_SwapOrderParams())

    with pytest.raises(InvalidOrderError) as excinfo:
        feed._make_order("BTC-USDT-SWAP", 0.002, 60000, "buy-limit")

    assert "BTC-USDT-SWAP" in str(excinfo.value)


def test_base_unit_spot_still_converts_via_table():
    feed = _OrderFeed(_SpotOrderParams())

    _path, params, _extra = feed._make_order("BTC-USDT", 1, 60000, "buy-limit")

    assert float(params["sz"]) == 100.0


def test_size_in_contracts_skips_conversion():
    feed = _OrderFeed(_SwapOrderParams())

    _path, params, _extra = feed._make_order(
        "BTC-USDT-SWAP", 0.2, 60000, "buy-limit", size_in_contracts=True
    )

    assert float(params["sz"]) == 0.2


def test_post_only_with_ioc_is_invalid_order_error():
    feed = _OrderFeed(_SwapOrderParams())

    with pytest.raises(InvalidOrderError):
        feed._make_order(
            "BTC-USDT-SWAP",
            1,
            60000,
            "buy-limit",
            size_in_contracts=True,
            post_only=True,
            time_in_force="IOC",
        )


def test_unsupported_time_in_force_is_invalid_order_error():
    feed = _OrderFeed(_SwapOrderParams())

    with pytest.raises(InvalidOrderError):
        feed._make_order(
            "BTC-USDT-SWAP",
            1,
            60000,
            "buy-limit",
            size_in_contracts=True,
            time_in_force="GTX",
        )
