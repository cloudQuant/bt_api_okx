from __future__ import annotations

from bt_api_base.gateway.registrar import GatewayRuntimeRegistrar
from bt_api_base.plugins.protocol import PluginInfo
from bt_api_base.registry import ExchangeRegistry

from bt_api_okx import __version__
from bt_api_okx.gateway.adapter import OkxGatewayAdapter
from bt_api_okx.registry_registration import register_okx


def register_plugin(
    registry: type[ExchangeRegistry], runtime_factory: type[GatewayRuntimeRegistrar]
) -> PluginInfo:
    """Register OKX assets, feeds, and adapter in the plugin host."""
    register_okx(registry)
    runtime_factory.register_adapter("OKX", OkxGatewayAdapter)

    return PluginInfo(
        name="bt_api_okx",
        version=__version__,
        core_requires=">=0.15,<1.0",
        supported_exchanges=("OKX___SPOT", "OKX___SWAP"),
        supported_asset_types=("SPOT", "SWAP"),
    )
