"""OKX-owned collection and projection of read-only order readiness."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from bt_api_okx.order_request_mapping import build_order_readiness_normalizer


def collect_order_readiness(backend: Any, exchange_name: str, symbol: str, quantity_native: Any, *,
                            margin_mode: str, position_mode: str | None, account_config: Any,
                            extra_data: Any, normalizers: dict[str, Any]) -> dict[str, Any]:
    normalize = build_order_readiness_normalizer(
        rows=normalizers["rows"], pick=normalizers["pick"],
        _trading_permissions=normalizers["trading_permissions"], number=normalizers["number"],
    )
    def options() -> Any:
        return deepcopy(extra_data)

    account_instruments = backend.get_account_instruments(exchange_name, symbol, extra_data=options())
    snapshot = normalize(
        exchange_name, symbol, quantity_native, margin_mode=margin_mode,
        expected_position_mode=position_mode, account_config=account_config,
        account_instruments=account_instruments,
    )
    if snapshot["definite_failure"]:
        return snapshot
    leverage_info = backend.get_leverage_info(
        exchange_name, symbol, margin_mode=margin_mode, extra_data=options()
    )
    max_size = backend.get_max_size(
        exchange_name, symbol, margin_mode=margin_mode, extra_data=options()
    )
    return normalize(
        exchange_name, symbol, quantity_native, margin_mode=margin_mode,
        expected_position_mode=position_mode, account_config=account_config,
        account_instruments=account_instruments, leverage_info=leverage_info, max_size=max_size,
    )
