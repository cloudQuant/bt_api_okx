"""Module-level docstring."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bt_api_base.balance_utils import nested_balance_handler

from bt_api_okx.environment import configure_environment
from bt_api_okx.exchange_data import OkxExchangeDataSpot, OkxExchangeDataSwap
from bt_api_okx.feeds import (
    OkxAccountWssDataSpot,
    OkxAccountWssDataSwap,
    OkxMarketWssDataSpot,
    OkxMarketWssDataSwap,
    OkxRequestDataSpot,
    OkxRequestDataSwap,
)

if TYPE_CHECKING:
    from bt_api_base.registry import ExchangeRegistry


def _cleanup_started_streams(streams):
    survivors = []
    for stream in reversed(streams):
        stop = getattr(stream, "stop", None)
        if not callable(stop):
            survivors.append(stream)
            continue
        try:
            stop()
        except Exception:
            survivors.append(stream)
    return list(reversed(survivors))


def _commit_started_streams(bt_api, streams):
    retained = getattr(bt_api, "_subscription_streams", None)
    if retained is None:
        retained = bt_api._subscription_streams = []
    retained.extend(streams)


def _credential_alias(exchange_params, names):
    supplied = []
    for name in names:
        if name not in exchange_params or exchange_params[name] is None:
            continue
        value = exchange_params[name]
        if value == "":
            continue
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError("OKX credentials must be non-empty trimmed strings")
        supplied.append(value)
    if len(set(supplied)) > 1:
        raise ValueError("OKX credential aliases conflict")
    return supplied[0] if supplied else None


def _private_credentials(exchange_params):
    key = _credential_alias(exchange_params, ("public_key", "api_key"))
    secret = _credential_alias(exchange_params, ("private_key", "secret_key", "api_secret"))
    passphrase = _credential_alias(exchange_params, ("passphrase",))
    values = (key, secret, passphrase)
    if any(value is not None for value in values) and not all(
        value is not None for value in values
    ):
        raise ValueError("OKX private websocket requires API key, secret and passphrase")
    return key is not None


def _okx_swap_subscribe_handler(data_queue, exchange_params, topics, bt_api):
    cleanup_flag = "OKX___SWAP_subscription_cleanup_failed"
    if bt_api._subscription_flags.get(cleanup_flag, False):
        raise RuntimeError("Close BtApi before retrying the failed OKX swap subscription")
    exchange_data = configure_environment(OkxExchangeDataSwap(), exchange_params)
    kwargs = dict(exchange_params)
    kwargs.update(
        wss_name="okx_swap_market_data",
        stream_role="market",
        wss_url=exchange_data.wss_url,
        exchange_data=exchange_data,
        topics=topics,
    )
    event_bus = getattr(bt_api, "event_bus", None)
    if event_bus is not None:
        kwargs["event_bus"] = event_bus
    has_credentials = _private_credentials(exchange_params)
    start_account = (
        has_credentials
        and kwargs.get("subscribe_account", True)
        and not bt_api._subscription_flags.get("OKX___SWAP_account", False)
    )
    started = []
    try:
        market = OkxMarketWssDataSwap(data_queue, **kwargs)
        started.append(market)
        market.start()
        if start_account:
            account_kwargs = dict(kwargs)
            account_kwargs["wss_name"] = "okx_swap_account_data"
            account_kwargs["stream_role"] = "account"
            account_kwargs["wss_url"] = exchange_data.account_wss_url
            account_kwargs["topics"] = [{"topic": "account"}, {"topic": "orders"}]
            account_kwargs["message_idle_timeout"] = exchange_params.get(
                "account_message_idle_timeout", 0.0
            )
            account = OkxAccountWssDataSwap(data_queue, **account_kwargs)
            started.append(account)
            account.start()
    except Exception as start_error:
        survivors = _cleanup_started_streams(started)
        if survivors:
            _commit_started_streams(bt_api, survivors)
            bt_api._subscription_flags[cleanup_flag] = True
            raise RuntimeError(
                "OKX swap subscription startup failed and "
                f"{len(survivors)} stream(s) could not be stopped; close BtApi before retrying"
            ) from start_error
        raise
    _commit_started_streams(bt_api, started)
    if start_account:
        bt_api._subscription_flags["OKX___SWAP_account"] = True


def _okx_spot_subscribe_handler(data_queue, exchange_params, topics, bt_api):
    cleanup_flag = "OKX___SPOT_subscription_cleanup_failed"
    if bt_api._subscription_flags.get(cleanup_flag, False):
        raise RuntimeError("Close BtApi before retrying the failed OKX spot subscription")
    exchange_data = configure_environment(OkxExchangeDataSpot(), exchange_params)
    kwargs = dict(exchange_params)
    kwargs.update(
        wss_name="okx_spot_market_data",
        stream_role="market",
        wss_url=exchange_data.wss_url,
        exchange_data=exchange_data,
        topics=topics,
    )
    event_bus = getattr(bt_api, "event_bus", None)
    if event_bus is not None:
        kwargs["event_bus"] = event_bus
    has_credentials = _private_credentials(exchange_params)
    start_account = (
        has_credentials
        and kwargs.get("subscribe_account", True)
        and not bt_api._subscription_flags.get("OKX___SPOT_account", False)
    )
    started = []
    try:
        market = OkxMarketWssDataSpot(data_queue, **kwargs)
        started.append(market)
        market.start()
        if start_account:
            account_kwargs = dict(kwargs)
            account_kwargs["wss_name"] = "okx_spot_account_data"
            account_kwargs["stream_role"] = "account"
            account_kwargs["wss_url"] = exchange_data.account_wss_url
            account_kwargs["topics"] = [{"topic": "account"}, {"topic": "orders"}]
            account_kwargs["message_idle_timeout"] = exchange_params.get(
                "account_message_idle_timeout", 0.0
            )
            account = OkxAccountWssDataSpot(data_queue, **account_kwargs)
            started.append(account)
            account.start()
    except Exception as start_error:
        survivors = _cleanup_started_streams(started)
        if survivors:
            _commit_started_streams(bt_api, survivors)
            bt_api._subscription_flags[cleanup_flag] = True
            raise RuntimeError(
                "OKX spot subscription startup failed and "
                f"{len(survivors)} stream(s) could not be stopped; close BtApi before retrying"
            ) from start_error
        raise
    _commit_started_streams(bt_api, started)
    if start_account:
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
