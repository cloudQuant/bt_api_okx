from __future__ import annotations

from importlib.util import find_spec

import pytest

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


def test_base_lazy_gateway_adapter_export_is_retired() -> None:
    from bt_api_base.gateway import adapters

    with pytest.raises(AttributeError, match="OkxGatewayAdapter"):
        getattr(adapters, "OkxGatewayAdapter")
