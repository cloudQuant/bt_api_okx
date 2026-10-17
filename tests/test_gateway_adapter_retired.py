from __future__ import annotations

from importlib.util import find_spec

from bt_api_okx.market_history_provider import OkxMarketHistoryProvider
from bt_api_okx.market_provider import OkxTickerQueueMarketProvider


def test_legacy_gateway_module_is_absent_but_managed_market_providers_remain() -> None:
    try:
        adapter_spec = find_spec("bt_api_okx.gateway.adapter")
    except ModuleNotFoundError:
        adapter_spec = None

    assert adapter_spec is None
    assert OkxTickerQueueMarketProvider.__module__ == "bt_api_okx.market_provider"
    assert OkxMarketHistoryProvider.__module__ == "bt_api_okx.market_history_provider"


def test_retired_base_gateway_runtime_is_unavailable() -> None:
    try:
        runtime_spec = find_spec("bt_api_base.gateway.runtime")
    except ModuleNotFoundError:
        runtime_spec = None

    assert runtime_spec is None
