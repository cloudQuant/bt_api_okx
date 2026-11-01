"""OKX swap direct order quantity-unit projection."""

from __future__ import annotations

from typing import Any

from bt_api_base.contract_errors import CapabilityNotSupportedError


def validate_order_quantity_units(exchange_name: str, request: Any) -> None:
    """Preserve the former OKX swap contract-unit and lot restrictions."""
    del exchange_name
    if request.quantity_unit == "lots":
        raise CapabilityNotSupportedError(
            "make_order",
            detail="lots require a supported lot-based backend",
            definite_reject=True,
        )


__all__ = ("validate_order_quantity_units",)
