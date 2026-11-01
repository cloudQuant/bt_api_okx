"""OKX-specific position-mode request projection."""

from __future__ import annotations

from typing import Any

from bt_api_base.contract_errors import CapabilityNotSupportedError


def position_mode_read_aliases() -> tuple[str, ...]:
    return ("get_config",)


def write_position_mode(feed: Any, exchange_name: str, position_mode: str, extra_data: Any, kwargs: dict[str, Any]) -> Any:
    method = getattr(feed, "set_position_mode", None)
    if not callable(method):
        method = getattr(feed, "set_mode", None)
    native_mode: Any = {"net": "net_mode", "dual_side": "long_short_mode"}[position_mode]
    if not callable(method):
        raise CapabilityNotSupportedError(
            "set_position_mode",
            detail=f"transport=direct; {exchange_name} does not implement this operation",
            definite_reject=True,
        )
    return method(native_mode, extra_data=extra_data, **kwargs)
