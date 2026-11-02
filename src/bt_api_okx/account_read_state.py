"""Shared, in-process identity and freshness state for OKX private reads.

Only provider-owned REST reads may establish the state in this module. Route
labels, endpoint configuration, API-key material, and locally normalized
balances are not account identity evidence. A successful account-config read
supplies the OKX ``uid``/``mainUid`` pair; the pair is immediately reduced to
a process-keyed digest and never leaves this module.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import threading
import time
import uuid
import weakref
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from bt_api_base.containers.requestdatas.request_data import RequestData

from .provider_configuration_registration import EXCHANGE_NAME

_ENVIRONMENTS = frozenset({"demo", "production"})
_ACCOUNT_CONFIG_PATH = "GET /api/v5/account/config"
_ACCOUNT_BALANCE_PATH = "GET /api/v5/account/balance"
_ACCOUNT_POSITIONS_PATH = "GET /api/v5/account/positions"
_SESSION_CACHE_SECONDS = 0.05
_MAX_REQUEST_TIMEOUT_SECONDS = 10.0
_PROCESS_HMAC_KEY = secrets.token_bytes(32)
_ROUTE_LOCK = threading.RLock()
_ROUTE_STATES: dict[int, tuple[weakref.ReferenceType[Any], "OkxAccountReadState"]] = {}


@dataclass(frozen=True)
class OkxSessionEvidence:
    """Opaque source/session projection from one successful signed config read."""

    source_ref: str
    generation: str
    session_ref: str
    observed_at: datetime


class OkxAccountReadState:
    """State shared by query and account-session ports for one exact feed."""

    __slots__ = (
        "environment",
        "source_ref",
        "operation_lock",
        "__lock",
        "__principal_digest",
        "__generation",
        "__session_ref",
        "__observed_at",
        "__valid",
    )

    def __init__(self, environment: str) -> None:
        self.environment = environment
        self.source_ref = "okx-account-source-v1-" + uuid.uuid4().hex
        self.operation_lock = threading.RLock()
        self.__lock = threading.RLock()
        self.__principal_digest: bytes | None = None
        self.__generation: str | None = None
        self.__session_ref: str | None = None
        self.__observed_at: datetime | None = None
        self.__valid = False

    def accept_principal(
        self,
        uid: str,
        main_uid: str,
        *,
        observed_at: datetime,
    ) -> OkxSessionEvidence:
        """Bind a successful provider identity read without retaining its IDs."""

        digest = _principal_digest(uid, main_uid, self.environment)
        with self.__lock:
            if digest != self.__principal_digest or not self.__valid:
                self.__generation = "okx-account-generation-v1-" + uuid.uuid4().hex
                self.__session_ref = "okx-account-session-v1-" + uuid.uuid4().hex
                self.__principal_digest = digest
            self.__observed_at = observed_at
            self.__valid = True
            return self.__evidence_unlocked()

    def invalidate(self) -> None:
        """Invalidate currentness after a failed signed read or route check."""

        with self.__lock:
            self.__valid = False

    def current_evidence(
        self,
        *,
        now: datetime,
        max_age_seconds: float | None = None,
    ) -> OkxSessionEvidence | None:
        with self.__lock:
            if not self.__valid or self.__observed_at is None:
                return None
            if now < self.__observed_at:
                return None
            if max_age_seconds is not None:
                age = (now - self.__observed_at).total_seconds()
                if age > max_age_seconds:
                    return None
            return self.__evidence_unlocked()

    def __evidence_unlocked(self) -> OkxSessionEvidence:
        if (
            self.__generation is None
            or self.__session_ref is None
            or self.__observed_at is None
        ):
            raise RuntimeError("okx_account_session_evidence_unavailable")
        return OkxSessionEvidence(
            source_ref=self.source_ref,
            generation=self.__generation,
            session_ref=self.__session_ref,
            observed_at=self.__observed_at,
        )


def account_read_state_for_route(
    exchange_name: str,
    client: object,
    environment: object,
) -> OkxAccountReadState | None:
    """Return the state shared by exact OKX query/session factories."""

    if not _valid_route(exchange_name, client, environment):
        return None
    identity = id(client)
    with _ROUTE_LOCK:
        retained = _ROUTE_STATES.get(identity)
        if retained is not None and retained[0]() is client:
            state = retained[1]
            return state if state.environment == environment else None
        try:
            reference = weakref.ref(client, lambda item, key=identity: _drop_route_state(key, item))
        except TypeError:
            return None
        state = OkxAccountReadState(environment)
        _ROUTE_STATES[identity] = (reference, state)
        return state


def route_is_current(
    exchange_name: str,
    client: object,
    environment: object,
) -> bool:
    """Recheck the selected provider feed and its endpoint/environment seal."""

    if not _valid_route_shape(exchange_name, client, environment):
        return False
    try:
        proof = client.get_environment_info()
    except Exception:
        return False
    return bool(
        type(proof) is dict
        and proof.get("verified") is True
        and proof.get("environment") == environment
        and proof.get("simulated") is (environment == "demo")
        and type(proof.get("api_region")) is str
        and proof.get("api_region") in {"global", "eea", "us", "tr"}
        and not (proof.get("api_region") == "tr" and environment != "production")
    )


def read_authenticated_account_identity(
    client: object,
    state: OkxAccountReadState,
    *,
    timeout_seconds: float,
) -> OkxSessionEvidence | None:
    """Perform a bounded signed ``account/config`` read and issue current proof."""

    if type(state) is not OkxAccountReadState or not _valid_timeout(timeout_seconds):
        return None
    if not route_is_current(EXCHANGE_NAME, client, state.environment):
        state.invalidate()
        return None
    try:
        path, params, extra_data = client._get_config()
        if (
            path != _ACCOUNT_CONFIG_PATH
            or params != {}
            or type(extra_data) is not dict
            or extra_data.get("request_type") != "get_config"
            or extra_data.get("exchange_name") != EXCHANGE_NAME
        ):
            raise ValueError("okx_account_config_request_invalid")
        response = client.request(
            path,
            params=params,
            extra_data=extra_data,
            timeout=timeout_seconds,
            max_retries=1,
        )
        uid, main_uid = _config_principal(response)
        observed_at = datetime.now(timezone.utc)
        return state.accept_principal(uid, main_uid, observed_at=observed_at)
    except Exception:
        state.invalidate()
        return None


def read_full_account_balance(
    client: object,
    state: OkxAccountReadState,
    *,
    timeout_seconds: float,
) -> RequestData | None:
    """Read all OKX balance currencies with one bounded signed REST request."""

    if type(state) is not OkxAccountReadState or not _valid_timeout(timeout_seconds):
        return None
    if not route_is_current(EXCHANGE_NAME, client, state.environment):
        state.invalidate()
        return None
    try:
        path, params, extra_data = client._get_account(symbol=None)
        if (
            path != _ACCOUNT_BALANCE_PATH
            or params != {"ccy": ""}
            or type(extra_data) is not dict
            or extra_data.get("request_type") != "get_account"
            or extra_data.get("symbol_name") != "ALL"
            or extra_data.get("asset_type") != "SWAP"
            or extra_data.get("exchange_name") != EXCHANGE_NAME
        ):
            raise ValueError("okx_account_balance_request_invalid")
        result = client.request(
            path,
            params=params,
            extra_data=extra_data,
            timeout=timeout_seconds,
            max_retries=1,
        )
        if (
            type(result) is not RequestData
            or result.get_request_type() != "get_account"
            or result.get_exchange_name() != EXCHANGE_NAME
            or result.get_symbol_name() != "ALL"
            or result.get_asset_type() != "SWAP"
        ):
            raise ValueError("okx_account_balance_result_invalid")
        return result
    except Exception:
        state.invalidate()
        return None


def read_full_swap_positions(
    client: object,
    state: OkxAccountReadState,
    *,
    timeout_seconds: float,
) -> RequestData | None:
    """Read the full SWAP position family using one bounded signed REST call.

    The request builder is checked before dispatch so an absent instrument
    filter cannot silently broaden this route to MARGIN/FUTURES/OPTIONS. The
    caller brackets this call with authenticated account/config reads and
    binds its projected result to that source/session generation.
    """

    if type(state) is not OkxAccountReadState or not _valid_timeout(timeout_seconds):
        return None
    if not route_is_current(EXCHANGE_NAME, client, state.environment):
        state.invalidate()
        return None
    try:
        path, params, extra_data = client._get_position(None, instType="SWAP")
        if (
            path != _ACCOUNT_POSITIONS_PATH
            or params != {"instType": "SWAP"}
            or type(extra_data) is not dict
            or extra_data.get("request_type") != "get_position"
            or extra_data.get("symbol_name") is not None
            or extra_data.get("asset_type") != "SWAP"
            or extra_data.get("exchange_name") != EXCHANGE_NAME
            or extra_data.get("instType") != "SWAP"
            or "posId" in extra_data
        ):
            raise ValueError("okx_swap_positions_request_invalid")
        result = client.request(
            path,
            params=params,
            extra_data=extra_data,
            timeout=timeout_seconds,
            max_retries=1,
        )
        if (
            type(result) is not RequestData
            or result.get_request_type() != "get_position"
            or result.get_exchange_name() != EXCHANGE_NAME
            or result.get_symbol_name() != ""
            or result.get_asset_type() != "SWAP"
            or type(result.get_extra_data()) is not dict
            or result.get_extra_data().get("instType") != "SWAP"
        ):
            raise ValueError("okx_swap_positions_result_invalid")
        return result
    except Exception:
        state.invalidate()
        return None


def session_evidence_matches(
    first: OkxSessionEvidence | None,
    second: OkxSessionEvidence | None,
) -> bool:
    return bool(
        type(first) is OkxSessionEvidence
        and type(second) is OkxSessionEvidence
        and first.source_ref == second.source_ref
        and first.generation == second.generation
        and first.session_ref == second.session_ref
    )


def _config_principal(response: object) -> tuple[str, str]:
    if (
        type(response) is not RequestData
        or response.get_request_type() != "get_config"
        or response.get_exchange_name() != EXCHANGE_NAME
    ):
        raise ValueError("okx_account_config_result_invalid")
    payload = response.get_input_data()
    if (
        type(payload) is not dict
        or type(payload.get("code")) is not str
        or payload.get("code") != "0"
        or type(payload.get("data")) is not list
        or len(payload["data"]) != 1
        or type(payload["data"][0]) is not dict
    ):
        raise ValueError("okx_account_config_payload_invalid")
    row = payload["data"][0]
    uid = row.get("uid")
    main_uid = row.get("mainUid")
    account_level = row.get("acctLv")
    if (
        not _valid_provider_account_id(uid)
        or not _valid_provider_account_id(main_uid)
        or type(account_level) is not str
        or account_level not in {"1", "2", "3", "4"}
    ):
        raise ValueError("okx_account_config_identity_invalid")
    return uid, main_uid


def _valid_provider_account_id(value: object) -> bool:
    return bool(
        type(value) is str
        and 1 <= len(value) <= 32
        and value.isascii()
        and value.isdigit()
    )


def _principal_digest(uid: str, main_uid: str, environment: str) -> bytes:
    # The source/session DTOs never expose OKX account identifiers. This
    # process-local keyed digest is used only to detect an identity switch.
    payload = json.dumps(
        ["okx-account-principal.v1", EXCHANGE_NAME, environment, uid, main_uid],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hmac.new(_PROCESS_HMAC_KEY, payload, hashlib.sha256).digest()


def _valid_route(
    exchange_name: object,
    client: object,
    environment: object,
) -> bool:
    return bool(
        _valid_route_shape(exchange_name, client, environment)
        and route_is_current(exchange_name, client, environment)
    )


def _valid_route_shape(
    exchange_name: object,
    client: object,
    environment: object,
) -> bool:
    from .feeds.live_okx.swap import OkxRequestDataSwap

    return bool(
        type(exchange_name) is str
        and exchange_name == EXCHANGE_NAME
        and type(environment) is str
        and environment in _ENVIRONMENTS
        and type(client) is OkxRequestDataSwap
        and client.exchange_name == EXCHANGE_NAME
        and client.asset_type == "SWAP"
    )


def _valid_timeout(value: object) -> bool:
    return bool(
        type(value) in (int, float)
        and value > 0
        and value <= _MAX_REQUEST_TIMEOUT_SECONDS
    )


def _drop_route_state(
    identity: int,
    reference: weakref.ReferenceType[Any],
) -> None:
    with _ROUTE_LOCK:
        retained = _ROUTE_STATES.get(identity)
        if retained is not None and retained[0] is reference:
            _ROUTE_STATES.pop(identity, None)


__all__ = [
    "OkxAccountReadState",
    "OkxSessionEvidence",
    "account_read_state_for_route",
    "read_authenticated_account_identity",
    "read_full_account_balance",
    "read_full_swap_positions",
    "route_is_current",
    "session_evidence_matches",
]
