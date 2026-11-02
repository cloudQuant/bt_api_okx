"""Register the OKX read-only account-session provider."""

from __future__ import annotations

from bt_api_base.account_session_registry_protocol import AccountSessionProviderRegistry

from .account_session_provider import (
    register_okx_account_session_provider as _register_okx_account_session_provider,
)


def register_okx_account_session_provider(
    registry: AccountSessionProviderRegistry,
) -> None:
    """Entry-point registrar for the read-only OKX account-session port."""

    _register_okx_account_session_provider(registry)


__all__ = ["register_okx_account_session_provider"]
