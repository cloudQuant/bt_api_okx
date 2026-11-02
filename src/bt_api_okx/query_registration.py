"""Register OKX's provider-neutral query capability with ``bt_api_py``."""

from __future__ import annotations

from bt_api_base.query_provider_protocol import (
    QueryProviderRegistryPort,
    SelectedQueryRoute,
)

from .provider_configuration_registration import EXCHANGE_NAME
from .query_service import create_okx_provider_query_service


def _create_okx_query_port(route: SelectedQueryRoute):
    if type(route) is not SelectedQueryRoute or route.exchange_name != EXCHANGE_NAME:
        raise ValueError("okx_query_route_invalid")
    return create_okx_provider_query_service(route)


def register_okx_query_provider(registry: QueryProviderRegistryPort) -> None:
    """Register exactly the selected OKX SWAP query route."""

    if not isinstance(registry, QueryProviderRegistryPort):
        raise TypeError("registry must implement QueryProviderRegistryPort")
    registry.register(EXCHANGE_NAME, _create_okx_query_port)


__all__ = ["register_okx_query_provider"]
