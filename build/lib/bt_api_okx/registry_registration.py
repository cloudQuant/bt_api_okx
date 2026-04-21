from __future__ import annotations

from bt_api_base.balance_utils import nested_balance_handler
from bt_api_okx.exchange_data import OkxExchangeDataSpot, OkxExchangeDataSwap
from bt_api_okx.feeds import (
    OkxAccountWssDataSpot,
    OkxMarketWssDataSpot,
    OkxAccountWssDataSwap,
    OkxMarketWssDataSwap,
    OkxRequestDataSpot,
    OkxRequestDataSwap,
)
from bt_api_base.registry import ExchangeRegistry


def _okx_swap_subscribe_handler(data_queue, exchange_params, topics, bt_api):
    exchange_data = OkxExchangeDataSwap()
    kwargs = dict(exchange_params.items())
    kwargs["wss_name"] = "okx_market_data"
    kwargs["wss_url"] = "wss://ws.okx.com:8443/ws/v5/public"
    kwargs["exchange_data"] = exchange_data
    kwargs["topics"] = topics
    OkxMarketWssDataSwap(data_queue, **kwargs).start()

    if not bt_api._subscription_flags.get("OKX___SWAP_account", False):
        account_kwargs = dict(kwargs)
        account_kwargs["topics"] = [
            {"topic": "account"},
            {"topic": "orders"},
            {"topic": "positions"},
        ]
        OkxAccountWssDataSwap(data_queue, **account_kwargs).start()
        bt_api._subscription_flags["OKX___SWAP_account"] = True


def _okx_spot_subscribe_handler(data_queue, exchange_params, topics, bt_api):
    exchange_data = OkxExchangeDataSpot()
    kwargs = dict(exchange_params.items())
    kwargs["wss_name"] = "okx_market_data"
    kwargs["wss_url"] = "wss://ws.okx.com:8443/ws/v5/public"
    kwargs["exchange_data"] = exchange_data
    kwargs["topics"] = topics
    OkxMarketWssDataSpot(data_queue, **kwargs).start()

    if not bt_api._subscription_flags.get("OKX___SPOT_account", False):
        account_kwargs = dict(kwargs)
        account_kwargs["topics"] = [
            {"topic": "account"},
            {"topic": "orders"},
            {"topic": "positions"},
        ]
        OkxAccountWssDataSpot(data_queue, **account_kwargs).start()
        bt_api._subscription_flags["OKX___SPOT_account"] = True


def register_okx(registry: ExchangeRegistry) -> None:
    """Register OKX Spot and Swap interfaces into the provided registry."""
    registry.register_feed("OKX___SWAP", OkxRequestDataSwap)
    registry.register_exchange_data("OKX___SWAP", OkxExchangeDataSwap)
    registry.register_balance_handler("OKX___SWAP", nested_balance_handler)
    registry.register_stream("OKX___SWAP", "subscribe", _okx_swap_subscribe_handler)

    registry.register_feed("OKX___SPOT", OkxRequestDataSpot)
    registry.register_exchange_data("OKX___SPOT", OkxExchangeDataSpot)
    registry.register_balance_handler("OKX___SPOT", nested_balance_handler)
    registry.register_stream("OKX___SPOT", "subscribe", _okx_spot_subscribe_handler)
