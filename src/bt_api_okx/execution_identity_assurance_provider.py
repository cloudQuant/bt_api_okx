"""Provider-issued execution-credential assurance for OKX SWAP routes.

The provider binds its proof to the SDK-issued execution identity route and
then performs a fresh, signed account-configuration read on that exact feed.
The account reference comes only from the trusted SDK ledger route. Provider
account identifiers and response payloads are not projected to the caller.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.execution_identity_protocol import (
    ExecutionCredentialRequestContextPort,
    ExecutionIdentityAssurance,
    ExecutionIdentityAssurancePort,
    ExecutionIdentityAssuranceProviderRegistryPort,
    ExecutionIdentityAssuranceUnavailable,
    SelectedExecutionIdentityRoute,
)
from bt_api_base.execution_request_receipt_protocol import (
    ExecutionCredentialRequestAttemptContext,
    ExecutionCredentialRequestOpaqueRef,
    ExecutionCredentialRequestReceipt,
    ExecutionCredentialRequestReceiptIssuerPort,
    ExecutionCredentialRequestReceiptUnavailable,
    ExecutionCredentialRequestSuccessCategory,
    ExecutionCredentialRequestTransport,
    ExecutionCredentialRequestTransportObservation,
)

from .feeds.live_okx.swap import OkxRequestDataSwap
from .provider_configuration_registration import EXCHANGE_NAME

_PROVIDER = "okx"
_ENVIRONMENTS = frozenset({"demo", "production"})
_ACCOUNT_CONFIG_PATH = "GET /api/v5/account/config"
_IDENTITY_TTL = timedelta(seconds=30)
_REQUEST_RECEIPT_TTL = timedelta(seconds=30)
_MAX_RECEIPTS = 128


class _OkxExecutionIdentityAssurancePort(
    ExecutionIdentityAssurancePort,
    ExecutionCredentialRequestReceiptIssuerPort,
):
    """One exact selected feed, receipt issuer, and SDK owner context."""

    __slots__ = (
        "__route",
        "__source_ref",
        "__lineage_ref",
        "__issuer_ref",
        "__expiry_policy_ref",
        "__issued",
        "__pending_observations",
        "__receipts",
        "__lock",
    )

    def __init__(self, route: SelectedExecutionIdentityRoute) -> None:
        self.__route = route
        self.__source_ref = "okx-rest-account-config"
        try:
            self.__lineage_ref = route.client.execution_credential_lineage_ref()
        except Exception:
            raise _unavailable() from None
        if type(self.__lineage_ref) is not ExecutionCredentialRequestOpaqueRef:
            raise _unavailable()
        self.__issuer_ref = ExecutionCredentialRequestOpaqueRef()
        self.__expiry_policy_ref = ExecutionCredentialRequestOpaqueRef()
        self.__issued: OrderedDict[
            int,
            tuple[
                ExecutionIdentityAssurance,
                str,
                ExecutionCredentialRequestReceipt,
                ExecutionCredentialRequestTransportObservation,
            ],
        ] = OrderedDict()
        self.__pending_observations: OrderedDict[
            int,
            tuple[
                ExecutionCredentialRequestTransportObservation,
                RequestData,
                int,
                ExecutionCredentialRequestAttemptContext,
                ExecutionCredentialRequestContextPort,
            ],
        ] = OrderedDict()
        self.__receipts: OrderedDict[
            int,
            tuple[
                ExecutionCredentialRequestReceipt,
                ExecutionCredentialRequestTransportObservation,
                ExecutionCredentialRequestAttemptContext,
                float,
            ],
        ] = OrderedDict()
        self.__lock = threading.RLock()

    def assure_execution_identity(self) -> ExecutionIdentityAssurance:
        self.__require_exact_route()
        observation, receipt = self.__request_authenticated_account_configuration()
        observed_at = receipt.issued_at_utc
        expires_at = min(receipt.expires_at_utc, observed_at + _IDENTITY_TTL)
        if expires_at <= observed_at:
            raise _unavailable()
        assurance = ExecutionIdentityAssurance(
            exchange_name=self.__route.exchange_name,
            provider=self.__route.provider,
            environment=self.__route.environment,
            account_ref=self.__route.account_ref,
            identity_binding="authenticated_credential",
            source_ref=self.__source_ref,
            session_generation=self.__route.session_generation,
            observed_at_utc=observed_at,
            expires_at_utc=expires_at,
            receipt_ref="okx-auth-" + uuid.uuid4().hex,
        )
        try:
            digest = _assurance_digest(assurance)
        except Exception:
            raise _unavailable() from None
        with self.__lock:
            self.__issued[id(assurance)] = (assurance, digest, receipt, observation)
            self.__issued.move_to_end(id(assurance))
            while len(self.__issued) > _MAX_RECEIPTS:
                self.__issued.popitem(last=False)
        return assurance

    def validate_execution_identity(
        self,
        assurance: ExecutionIdentityAssurance,
        *,
        now_utc: datetime,
    ) -> bool:
        if type(assurance) is not ExecutionIdentityAssurance or not _is_utc(now_utc):
            return False
        with self.__lock:
            issued = self.__issued.get(id(assurance))
        if issued is None or issued[0] is not assurance:
            return False
        try:
            ExecutionIdentityAssurance.__post_init__(assurance)
            if (
                _assurance_digest(assurance) != issued[1]
                or not _assurance_matches_route(assurance, self.__route)
                or now_utc < assurance.observed_at_utc
                or now_utc >= assurance.expires_at_utc
            ):
                return False
            self.__require_exact_route()
            observation, receipt = issued[3], issued[2]
            context = self.__route.request_receipt_context
            attempt = self.__receipt_attempt(receipt, observation)
            if context.validate_current(
                self.__route,
                selected_client=self.__route.client,
                credential_lineage_ref=self.__lineage_ref,
                context=attempt,
            ) is not True:
                return False
            valid = self.validate_execution_credential_request_receipt(
                receipt,
                expected_observation=observation,
                expected_exchange_name=self.__route.exchange_name,
                expected_provider=self.__route.provider,
                expected_environment=self.__route.environment,
                expected_transport=ExecutionCredentialRequestTransport.REST,
                expected_operation="get_config",
                expected_credential_lineage_ref=self.__lineage_ref,
                expected_selected_route_ref=attempt.selected_route_ref,
                expected_owner_generation_ref=attempt.owner_generation_ref,
                expected_owner_lease_ref=attempt.owner_lease_ref,
                expected_session_generation=self.__route.session_generation,
                expected_fencing_epoch=self.__route.fencing_epoch,
            )
            return type(valid) is bool and valid is True
        except Exception:
            return False

    def __require_exact_route(self) -> None:
        route = self.__route
        try:
            SelectedExecutionIdentityRoute.__post_init__(route)
        except Exception:
            raise _unavailable() from None
        context = getattr(route, "request_receipt_context", None)
        if (
            type(route) is not SelectedExecutionIdentityRoute
            or route.exchange_name != EXCHANGE_NAME
            or route.provider != _PROVIDER
            or route.environment not in _ENVIRONMENTS
            or route.identity_binding != "authenticated_credential"
            or type(route.client) is not OkxRequestDataSwap
            or route.fencing_epoch <= 0
            or route.ledger_binding is None
            or not route.account_ref
            or not route.session_generation
            or not isinstance(context, ExecutionCredentialRequestContextPort)
        ):
            raise _unavailable()
        try:
            marker = route.client.execution_credential_lineage_ref()
            environment = route.client.get_environment_info()
        except Exception:
            raise _unavailable() from None
        if (
            type(marker) is not ExecutionCredentialRequestOpaqueRef
            or marker is not self.__lineage_ref
            or type(environment) is not dict
            or environment.get("verified") is not True
            or environment.get("environment") != route.environment
        ):
            raise _unavailable()

    def __request_authenticated_account_configuration(
        self,
    ) -> tuple[
        ExecutionCredentialRequestTransportObservation,
        ExecutionCredentialRequestReceipt,
    ]:
        self.__require_exact_route()
        route = self.__route
        client = route.client
        context = route.request_receipt_context
        try:
            marker = client.execution_credential_lineage_ref()
            attempt = context.begin_request(
                route,
                selected_client=client,
                credential_lineage_ref=marker,
                transport=ExecutionCredentialRequestTransport.REST,
                operation="get_config",
            )
            if (
                type(attempt) is not ExecutionCredentialRequestAttemptContext
                or not _attempt_matches_route(attempt, route, marker)
                or context.validate_current(
                    route,
                    selected_client=client,
                    credential_lineage_ref=marker,
                    context=attempt,
                )
                is not True
            ):
                raise ValueError("session request attempt unavailable")

            request_parts = client._get_config()
            if (
                type(request_parts) is not tuple
                or len(request_parts) != 3
                or type(request_parts[0]) is not str
                or request_parts[0] != _ACCOUNT_CONFIG_PATH
                or type(request_parts[1]) is not dict
                or request_parts[1]
                or type(request_parts[2]) is not dict
                or request_parts[2].get("request_type") != "get_config"
                or request_parts[2].get("exchange_name") != EXCHANGE_NAME
            ):
                raise ValueError("account configuration request is not exact")
            response_result = client.request(
                request_parts[0],
                params=request_parts[1],
                extra_data=request_parts[2],
                timeout=10,
                max_retries=1,
                _include_http_status=True,
                _include_execution_credential_lineage=True,
            )
            if (
                type(response_result) is not tuple
                or len(response_result) != 6
                or type(response_result[0]) is not RequestData
                or type(response_result[1]) is not int
                or response_result[1] != 200
                or response_result[2] is not marker
                or type(response_result[3]) is not str
                or response_result[3] != response_result[3].strip()
                or not response_result[3].startswith("okx-rest-attempt-")
                or type(response_result[4]) is not ExecutionCredentialRequestOpaqueRef
                or type(response_result[5]) is not ExecutionCredentialRequestOpaqueRef
                or client.execution_credential_lineage_ref() is not marker
                or not _is_accepted_config_response(response_result[0])
                or context.validate_current(
                    route,
                    selected_client=client,
                    credential_lineage_ref=marker,
                    context=attempt,
                )
                is not True
            ):
                raise ValueError("authenticated account configuration response unavailable")

            response, status_code, _, request_ref, physical_request_ref, physical_response_ref = (
                response_result
            )
            observation = ExecutionCredentialRequestTransportObservation(
                exchange_name=route.exchange_name,
                provider=route.provider,
                environment=route.environment,
                transport=ExecutionCredentialRequestTransport.REST,
                operation="get_config",
                request_ref=request_ref,
                physical_request_ref=physical_request_ref,
                physical_response_ref=physical_response_ref,
                credential_lineage_ref=marker,
                selected_route_ref=attempt.selected_route_ref,
                owner_generation_ref=attempt.owner_generation_ref,
                owner_lease_ref=attempt.owner_lease_ref,
                session_generation=attempt.session_generation,
                fencing_epoch=attempt.fencing_epoch,
                success_category=(
                    ExecutionCredentialRequestSuccessCategory.AUTHENTICATED_RESPONSE_ACCEPTED
                ),
            )
            with self.__lock:
                self.__pending_observations[id(observation)] = (
                    observation,
                    response,
                    status_code,
                    attempt,
                    context,
                )
                self.__pending_observations.move_to_end(id(observation))
                while len(self.__pending_observations) > _MAX_RECEIPTS:
                    self.__pending_observations.popitem(last=False)
            receipt = self.issue_execution_credential_request_receipt(observation)
            if context.validate_current(
                route,
                selected_client=client,
                credential_lineage_ref=marker,
                context=attempt,
            ) is not True:
                self.__revoke_receipt(receipt)
                raise ValueError("session request attempt expired")
            if self.validate_execution_credential_request_receipt(
                receipt,
                expected_observation=observation,
                expected_exchange_name=route.exchange_name,
                expected_provider=route.provider,
                expected_environment=route.environment,
                expected_transport=ExecutionCredentialRequestTransport.REST,
                expected_operation="get_config",
                expected_credential_lineage_ref=marker,
                expected_selected_route_ref=attempt.selected_route_ref,
                expected_owner_generation_ref=attempt.owner_generation_ref,
                expected_owner_lease_ref=attempt.owner_lease_ref,
                expected_session_generation=route.session_generation,
                expected_fencing_epoch=route.fencing_epoch,
            ) is not True:
                self.__revoke_receipt(receipt)
                raise ValueError("provider receipt validation failed")
            return observation, receipt
        except ExecutionCredentialRequestReceiptUnavailable:
            raise _unavailable() from None
        except Exception:
            raise _unavailable() from None

    def issue_execution_credential_request_receipt(
        self,
        observation: ExecutionCredentialRequestTransportObservation,
        /,
    ) -> ExecutionCredentialRequestReceipt:
        if type(observation) is not ExecutionCredentialRequestTransportObservation:
            raise ExecutionCredentialRequestReceiptUnavailable(
                "execution_credential_request_transport_observation_invalid"
            )
        with self.__lock:
            pending = self.__pending_observations.pop(id(observation), None)
        if pending is None or pending[0] is not observation:
            raise ExecutionCredentialRequestReceiptUnavailable(
                "execution_credential_request_transport_observation_invalid"
            )
        _, response, status_code, attempt, context = pending
        route = self.__route
        marker = self.__lineage_ref
        if (
            status_code != 200
            or not _is_accepted_config_response(response)
            or observation.exchange_name != route.exchange_name
            or observation.provider != route.provider
            or observation.environment != route.environment
            or observation.transport is not ExecutionCredentialRequestTransport.REST
            or observation.operation != "get_config"
            or observation.credential_lineage_ref is not marker
            or not _attempt_matches_route(attempt, route, marker)
            or context.validate_current(
                route,
                selected_client=route.client,
                credential_lineage_ref=marker,
                context=attempt,
            )
            is not True
        ):
            raise ExecutionCredentialRequestReceiptUnavailable(
                "execution_credential_request_transport_observation_invalid"
            )
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + _REQUEST_RECEIPT_TTL
        receipt = ExecutionCredentialRequestReceipt(
            observation=observation,
            receipt_ref=ExecutionCredentialRequestOpaqueRef(),
            provider_issuer_ref=self.__issuer_ref,
            expiry_policy_ref=self.__expiry_policy_ref,
            issued_at_utc=issued_at,
            expires_at_utc=expires_at,
        )
        deadline = time.monotonic() + _REQUEST_RECEIPT_TTL.total_seconds()
        with self.__lock:
            self.__receipts[id(receipt)] = (receipt, observation, attempt, deadline)
            self.__receipts.move_to_end(id(receipt))
            while len(self.__receipts) > _MAX_RECEIPTS:
                self.__receipts.popitem(last=False)
        return receipt

    def validate_execution_credential_request_receipt(
        self,
        receipt: ExecutionCredentialRequestReceipt,
        *,
        expected_observation: ExecutionCredentialRequestTransportObservation,
        expected_exchange_name: str,
        expected_provider: str,
        expected_environment: str,
        expected_transport: ExecutionCredentialRequestTransport,
        expected_operation: str,
        expected_credential_lineage_ref: ExecutionCredentialRequestOpaqueRef,
        expected_selected_route_ref: ExecutionCredentialRequestOpaqueRef,
        expected_owner_generation_ref: ExecutionCredentialRequestOpaqueRef,
        expected_owner_lease_ref: ExecutionCredentialRequestOpaqueRef,
        expected_session_generation: str,
        expected_fencing_epoch: int,
    ) -> bool:
        if (
            type(receipt) is not ExecutionCredentialRequestReceipt
            or type(expected_observation) is not ExecutionCredentialRequestTransportObservation
        ):
            return False
        with self.__lock:
            issued = self.__receipts.get(id(receipt))
        if issued is None or issued[0] is not receipt or issued[1] is not expected_observation:
            return False
        observation, attempt, deadline = issued[1], issued[2], issued[3]
        route = self.__route
        if (
            receipt.observation is not observation
            or receipt.provider_issuer_ref is not self.__issuer_ref
            or receipt.expiry_policy_ref is not self.__expiry_policy_ref
            or expected_exchange_name != route.exchange_name
            or expected_provider != route.provider
            or expected_environment != route.environment
            or expected_transport is not ExecutionCredentialRequestTransport.REST
            or expected_operation != "get_config"
            or expected_credential_lineage_ref is not self.__lineage_ref
            or expected_selected_route_ref is not attempt.selected_route_ref
            or expected_owner_generation_ref is not attempt.owner_generation_ref
            or expected_owner_lease_ref is not attempt.owner_lease_ref
            or expected_session_generation != route.session_generation
            or type(expected_fencing_epoch) is not int
            or expected_fencing_epoch != route.fencing_epoch
            or time.monotonic() >= deadline
            or datetime.now(timezone.utc) >= receipt.expires_at_utc
            or not _observation_matches_attempt(observation, route, attempt)
        ):
            return False
        try:
            context = route.request_receipt_context
            current = context.validate_current(
                route,
                selected_client=route.client,
                credential_lineage_ref=self.__lineage_ref,
                context=attempt,
            )
        except Exception:
            return False
        return type(current) is bool and current is True

    def __receipt_attempt(
        self,
        receipt: ExecutionCredentialRequestReceipt,
        observation: ExecutionCredentialRequestTransportObservation,
    ) -> ExecutionCredentialRequestAttemptContext:
        with self.__lock:
            issued = self.__receipts.get(id(receipt))
        if issued is None or issued[0] is not receipt or issued[1] is not observation:
            raise _unavailable()
        return issued[2]

    def __revoke_receipt(self, receipt: ExecutionCredentialRequestReceipt) -> None:
        with self.__lock:
            issued = self.__receipts.get(id(receipt))
            if issued is not None and issued[0] is receipt:
                self.__receipts.pop(id(receipt), None)


class _OkxExecutionIdentityAssuranceFactory:
    def __call__(
        self,
        route: SelectedExecutionIdentityRoute,
        /,
    ) -> ExecutionIdentityAssurancePort | None:
        if type(route) is not SelectedExecutionIdentityRoute:
            return None
        try:
            SelectedExecutionIdentityRoute.__post_init__(route)
        except Exception:
            return None
        if (
            route.exchange_name != EXCHANGE_NAME
            or route.provider != _PROVIDER
            or route.environment not in _ENVIRONMENTS
            or route.identity_binding != "authenticated_credential"
            or type(route.client) is not OkxRequestDataSwap
            or route.fencing_epoch <= 0
            or route.ledger_binding is None
            or not isinstance(
                route.request_receipt_context, ExecutionCredentialRequestContextPort
            )
        ):
            return None
        try:
            if (
                type(route.client.execution_credential_lineage_ref())
                is not ExecutionCredentialRequestOpaqueRef
            ):
                return None
        except Exception:
            return None
        return _OkxExecutionIdentityAssurancePort(route)


def register_okx_execution_identity_assurance_provider(
    registry: ExecutionIdentityAssuranceProviderRegistryPort,
) -> None:
    """Register the exact OKX SWAP execution-identity provider."""

    if not isinstance(registry, ExecutionIdentityAssuranceProviderRegistryPort):
        raise ExecutionIdentityAssuranceUnavailable(
            "execution_identity_assurance_provider_unavailable"
        )
    try:
        registry.register(EXCHANGE_NAME, _OkxExecutionIdentityAssuranceFactory())
    except ExecutionIdentityAssuranceUnavailable:
        raise
    except Exception:
        raise ExecutionIdentityAssuranceUnavailable(
            "execution_identity_assurance_provider_unavailable"
        ) from None


def _assurance_matches_route(
    assurance: ExecutionIdentityAssurance,
    route: SelectedExecutionIdentityRoute,
) -> bool:
    return (
        assurance.exchange_name == route.exchange_name
        and assurance.provider == route.provider
        and assurance.environment == route.environment
        and assurance.account_ref == route.account_ref
        and assurance.identity_binding == "authenticated_credential"
        and assurance.session_generation == route.session_generation
        and assurance.source_ref != ""
        and assurance.receipt_ref != ""
    )


def _attempt_matches_route(
    attempt: ExecutionCredentialRequestAttemptContext,
    route: SelectedExecutionIdentityRoute,
    lineage_ref: ExecutionCredentialRequestOpaqueRef,
) -> bool:
    if type(attempt) is not ExecutionCredentialRequestAttemptContext:
        return False
    try:
        ExecutionCredentialRequestAttemptContext.__post_init__(attempt)
    except Exception:
        return False
    return (
        type(attempt) is ExecutionCredentialRequestAttemptContext
        and attempt.credential_lineage_ref is lineage_ref
        and all(
            type(reference) is ExecutionCredentialRequestOpaqueRef
            for reference in (
                attempt.selected_route_ref,
                attempt.owner_generation_ref,
                attempt.owner_lease_ref,
            )
        )
        and attempt.session_generation == route.session_generation
        and type(attempt.fencing_epoch) is int
        and attempt.fencing_epoch == route.fencing_epoch
    )


def _observation_matches_attempt(
    observation: ExecutionCredentialRequestTransportObservation,
    route: SelectedExecutionIdentityRoute,
    attempt: ExecutionCredentialRequestAttemptContext,
) -> bool:
    if type(observation) is not ExecutionCredentialRequestTransportObservation:
        return False
    try:
        ExecutionCredentialRequestTransportObservation.__post_init__(observation)
    except Exception:
        return False
    return (
        type(observation) is ExecutionCredentialRequestTransportObservation
        and observation.exchange_name == route.exchange_name
        and observation.provider == route.provider
        and observation.environment == route.environment
        and observation.transport is ExecutionCredentialRequestTransport.REST
        and observation.operation == "get_config"
        and observation.credential_lineage_ref is attempt.credential_lineage_ref
        and observation.selected_route_ref is attempt.selected_route_ref
        and observation.owner_generation_ref is attempt.owner_generation_ref
        and observation.owner_lease_ref is attempt.owner_lease_ref
        and observation.session_generation == attempt.session_generation
        and type(observation.fencing_epoch) is int
        and observation.fencing_epoch == attempt.fencing_epoch
    )


def _is_accepted_config_response(response: object) -> bool:
    if type(response) is not RequestData:
        return False
    try:
        if (
            response.get_request_type() != "get_config"
            or response.get_exchange_name() != EXCHANGE_NAME
        ):
            return False
        data = response.get_input_data()
        return (
            type(data) is dict
            and type(data.get("code")) is str
            and data.get("code") == "0"
            and type(data.get("data")) is list
            and len(data["data"]) == 1
            and type(data["data"][0]) is dict
            and type(data["data"][0].get("acctLv")) is str
            and bool(data["data"][0]["acctLv"].strip())
        )
    except Exception:
        return False


def _assurance_digest(assurance: ExecutionIdentityAssurance) -> str:
    ExecutionIdentityAssurance.__post_init__(assurance)
    payload = {
        "exchange_name": assurance.exchange_name,
        "provider": assurance.provider,
        "environment": assurance.environment,
        "account_ref": assurance.account_ref,
        "identity_binding": assurance.identity_binding,
        "source_ref": assurance.source_ref,
        "session_generation": assurance.session_generation,
        "observed_at_utc": assurance.observed_at_utc.isoformat(),
        "expires_at_utc": assurance.expires_at_utc.isoformat(),
        "receipt_ref": assurance.receipt_ref,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_utc(value: object) -> bool:
    if type(value) is not datetime or value.tzinfo is None:
        return False
    try:
        return value.utcoffset() == timedelta(0)
    except Exception:
        return False


def _unavailable() -> ExecutionIdentityAssuranceUnavailable:
    return ExecutionIdentityAssuranceUnavailable("execution_identity_assurance_unavailable")


__all__ = ["register_okx_execution_identity_assurance_provider"]
