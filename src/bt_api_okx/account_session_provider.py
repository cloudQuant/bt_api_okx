"""Read-only OKX account-session evidence from authenticated account config."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bt_api_base.account_session_protocol import (
    AccountPreflightRequest,
    AccountPreflightSnapshot,
    AccountSessionPort,
    AccountSessionSnapshot,
    SettlementVerificationReceipt,
)
from bt_api_base.account_session_registry_protocol import SelectedAccountSessionRoute

from .account_read_state import (
    OkxAccountReadState,
    OkxSessionEvidence,
    account_read_state_for_route,
    read_authenticated_account_identity,
    route_is_current,
)
from .provider_configuration_registration import EXCHANGE_NAME

_SESSION_CACHE_TTL_SECONDS = 0.05
_SESSION_READ_TIMEOUT_SECONDS = 5.0
_UTC = timezone.utc


class OkxAccountSessionProvider(AccountSessionPort):
    """Account session observations over one exact selected OKX feed."""

    def __init__(
        self,
        route: SelectedAccountSessionRoute,
        state: OkxAccountReadState,
    ) -> None:
        if (
            type(route) is not SelectedAccountSessionRoute
            or type(state) is not OkxAccountReadState
            or route.exchange_name != EXCHANGE_NAME
        ):
            raise TypeError("route and account state must be exact OKX provider values")
        self.__client = route.client
        self.__environment = route.environment
        self.__state = state

    def session_snapshot(self) -> AccountSessionSnapshot:
        if not route_is_current(EXCHANGE_NAME, self.__client, self.__environment):
            self.__state.invalidate()
            return _unavailable_session("okx_account_route_not_current")
        now = datetime.now(_UTC)
        evidence = self.__state.current_evidence(
            now=now,
            max_age_seconds=_SESSION_CACHE_TTL_SECONDS,
        )
        if evidence is None:
            with self.__state.operation_lock:
                if not route_is_current(EXCHANGE_NAME, self.__client, self.__environment):
                    self.__state.invalidate()
                    return _unavailable_session("okx_account_route_not_current")
                evidence = read_authenticated_account_identity(
                    self.__client,
                    self.__state,
                    timeout_seconds=_SESSION_READ_TIMEOUT_SECONDS,
                )
        if type(evidence) is not OkxSessionEvidence:
            return _unavailable_session("okx_account_authentication_unavailable")
        return AccountSessionSnapshot(
            exchange_name=EXCHANGE_NAME,
            source_ref=evidence.source_ref,
            generation=evidence.generation,
            session_ref=evidence.session_ref,
            connected=True,
            authenticated=True,
            # OKX get_config's acctLv describes account mode; it does not
            # attest the API key's trade permission, so this remains unknown.
            trading_enabled=None,
            business_day=None,
            settlement_status="unavailable",
            observed_at=evidence.observed_at,
            available=True,
        )

    def preflight(self, request: AccountPreflightRequest) -> AccountPreflightSnapshot:
        if type(request) is not AccountPreflightRequest:
            raise TypeError("request must be an AccountPreflightRequest")
        if request.exchange_name != EXCHANGE_NAME:
            return _unavailable_preflight(request, "okx_account_session_route_mismatch")
        observed_at = datetime.now(_UTC)
        if observed_at > request.deadline:
            observed_at = None
        return AccountPreflightSnapshot(
            request=request,
            source_ref=None,
            generation=None,
            observed_at=observed_at,
            ready=None,
            available=False,
            blockers=("okx_account_order_preflight_unavailable",),
        )

    def verify_settlement(self, *, deadline: datetime) -> SettlementVerificationReceipt:
        if type(deadline) is not datetime or deadline.tzinfo is None or deadline.utcoffset() != timedelta(0):
            raise ValueError("deadline must be timezone-aware UTC")
        observed_at = datetime.now(_UTC)
        if observed_at > deadline:
            observed_at = None
        return SettlementVerificationReceipt(
            exchange_name=EXCHANGE_NAME,
            source_ref=None,
            generation=None,
            business_day=None,
            status="unavailable",
            observed_at=observed_at,
            complete=False,
            read_only_safe=False,
            receipt_ref=None,
            reason_code="okx_settlement_readback_unavailable",
        )

    def validate_preflight(
        self,
        snapshot: AccountPreflightSnapshot,
        *,
        now: datetime,
    ) -> bool:
        if type(snapshot) is not AccountPreflightSnapshot:
            raise TypeError("snapshot must be an AccountPreflightSnapshot")
        if type(now) is not datetime or now.tzinfo is None or now.utcoffset() != timedelta(0):
            raise ValueError("now must be timezone-aware UTC")
        return False


class _OkxAccountSessionFactory:
    def __call__(
        self,
        route: SelectedAccountSessionRoute,
    ) -> AccountSessionPort | None:
        if (
            type(route) is not SelectedAccountSessionRoute
            or route.exchange_name != EXCHANGE_NAME
            or route.settlement_context is not None
        ):
            return None
        state = account_read_state_for_route(
            route.exchange_name,
            route.client,
            route.environment,
        )
        if state is None:
            return None
        return OkxAccountSessionProvider(route, state)


def register_okx_account_session_provider(registry: object) -> None:
    """Register the OKX read-only account session capability."""

    from bt_api_base.account_session_registry_protocol import AccountSessionProviderRegistry

    if not isinstance(registry, AccountSessionProviderRegistry):
        raise TypeError("registry must implement AccountSessionProviderRegistry")
    registry.register(EXCHANGE_NAME, _OkxAccountSessionFactory(), None)


def _unavailable_session(blocker: str) -> AccountSessionSnapshot:
    return AccountSessionSnapshot(
        exchange_name=EXCHANGE_NAME,
        source_ref=None,
        generation=None,
        session_ref=None,
        connected=None,
        authenticated=None,
        trading_enabled=None,
        business_day=None,
        settlement_status="unavailable",
        observed_at=datetime.now(_UTC),
        available=False,
        blockers=(blocker,),
    )


def _unavailable_preflight(
    request: AccountPreflightRequest,
    blocker: str,
) -> AccountPreflightSnapshot:
    observed_at = datetime.now(_UTC)
    if observed_at > request.deadline:
        observed_at = None
    return AccountPreflightSnapshot(
        request=request,
        source_ref=None,
        generation=None,
        observed_at=observed_at,
        ready=None,
        available=False,
        blockers=(blocker,),
    )


__all__ = ["OkxAccountSessionProvider", "register_okx_account_session_provider"]
