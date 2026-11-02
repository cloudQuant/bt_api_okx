"""Provider-neutral, source-bound account queries for OKX SWAP.

This service publishes full account-balance, account-valuation, and SWAP
position families. Each family is projected from its own successful signed
REST response; account identity reads bracket the requested reads on the same
exact OKX feed, and all complete snapshots in a batch share that source and
generation. Unsupported query families remain explicitly unavailable.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from bt_api_base.account_protocol import (
    MAX_ACCOUNT_ROWS,
    AccountBalance,
    AccountPosition,
    AccountResourceKey,
    AccountValuation,
)
from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.market_protocol import MarketInstrumentKey
from bt_api_base.query_protocol import (
    MAX_QUERY_BATCH_REQUESTS,
    ProviderQueryPort,
    QueryBatchReceipt,
    QueryCompleteness,
    QueryRequest,
    QuerySnapshot,
    QuerySnapshotLease,
)
from bt_api_base.query_provider_protocol import SelectedQueryRoute

from .account_read_state import (
    OkxAccountReadState,
    OkxSessionEvidence,
    account_read_state_for_route,
    read_authenticated_account_identity,
    read_full_account_balance,
    read_full_swap_positions,
    route_is_current,
    session_evidence_matches,
)
from .provider_configuration_registration import EXCHANGE_NAME

_ACCOUNT_FAMILY = "account"
_VALUATION_FAMILY = "account_valuation"
_POSITIONS_FAMILY = "positions"
_SUPPORTED_FAMILIES = frozenset({_ACCOUNT_FAMILY, _VALUATION_FAMILY, _POSITIONS_FAMILY})
_ACCOUNT_RESOURCE = AccountResourceKey(product_type="account", margin_pool="account")
_POSITION_PRODUCT_TYPE = "SWAP"
_QUERY_EVIDENCE_TTL = timedelta(seconds=2)
_MAX_RETAINED_RECEIPTS = 64
_MAX_RETAINED_LEASES = 64
_MAX_REQUEST_TIMEOUT_SECONDS = 10.0
_UTC = timezone.utc


@dataclass(frozen=True)
class _SnapshotEvidence:
    snapshot: QuerySnapshot
    session: OkxSessionEvidence
    expires_at_utc: datetime
    expires_at_monotonic: float


@dataclass(frozen=True)
class _ReceiptEvidence:
    receipt: QueryBatchReceipt
    session: OkxSessionEvidence
    snapshot_refs: tuple[str, ...]


@dataclass(frozen=True)
class _LeaseEvidence:
    lease: QuerySnapshotLease
    receipt: QueryBatchReceipt
    session: OkxSessionEvidence
    expires_at_monotonic: float


class OkxProviderQueryService(ProviderQueryPort):
    """One exact OKX selected feed and its neutral query evidence authority."""

    def __init__(
        self,
        route: SelectedQueryRoute,
        state: OkxAccountReadState,
    ) -> None:
        if type(route) is not SelectedQueryRoute or type(state) is not OkxAccountReadState:
            raise TypeError("route and account state must use exact SDK provider types")
        self.__client = route.client
        self.__environment = route.environment
        self.__state = state
        self.__lock = threading.RLock()
        self.__receipts: OrderedDict[int, _ReceiptEvidence] = OrderedDict()
        self.__snapshots: OrderedDict[str, _SnapshotEvidence] = OrderedDict()
        self.__leases: OrderedDict[int, _LeaseEvidence] = OrderedDict()

    def query_batch(
        self,
        requests: Sequence[QueryRequest],
        *,
        deadline: datetime,
    ) -> QueryBatchReceipt:
        selected = _validate_requests(requests)
        _require_utc(deadline, "deadline")
        started_at = datetime.now(_UTC)
        supported = tuple(
            request
            for request in selected
            if request.family in _SUPPORTED_FAMILIES and not request.filters
        )
        unsupported = {
            request.request_ref: (
                "okx_query_family_unavailable"
                if request.family not in _SUPPORTED_FAMILIES
                else "okx_full_scope_required"
            )
            for request in selected
            if request not in supported
        }

        evidence: OkxSessionEvidence | None = None
        wants_account = any(
            request.family in {_ACCOUNT_FAMILY, _VALUATION_FAMILY}
            for request in supported
        )
        wants_positions = any(
            request.family == _POSITIONS_FAMILY for request in supported
        )
        account_rows: tuple[Mapping[str, Any], ...] | None = None
        account_blockers: tuple[str, ...] = ()
        valuation_record: Mapping[str, Any] | None = None
        valuation_blocker: str | None = None
        account_started_at: datetime | None = None
        account_completed_at: datetime | None = None
        position_rows: tuple[Mapping[str, Any], ...] | None = None
        position_blockers: tuple[str, ...] = ()
        positions_started_at: datetime | None = None
        positions_completed_at: datetime | None = None
        deadline_elapsed = False

        if supported:
            with self.__state.operation_lock:
                if not route_is_current(EXCHANGE_NAME, self.__client, self.__environment):
                    self.__state.invalidate()
                else:
                    remaining = _remaining_seconds(deadline)
                    before = (
                        read_authenticated_account_identity(
                            self.__client,
                            self.__state,
                            timeout_seconds=min(remaining, _MAX_REQUEST_TIMEOUT_SECONDS),
                        )
                        if remaining > 0
                        else None
                    )
                    if before is not None and datetime.now(_UTC) <= deadline:
                        balance_result: RequestData | None = None
                        positions_result: RequestData | None = None
                        if wants_account:
                            remaining = _remaining_seconds(deadline)
                            account_started_at = datetime.now(_UTC)
                            balance_result = (
                                read_full_account_balance(
                                    self.__client,
                                    self.__state,
                                    timeout_seconds=min(
                                        remaining, _MAX_REQUEST_TIMEOUT_SECONDS
                                    ),
                                )
                                if remaining > 0
                                else None
                            )
                            account_completed_at = datetime.now(_UTC)
                            if balance_result is None:
                                account_blockers = (
                                    "okx_account_balance_read_unavailable",
                                )
                            elif account_completed_at > deadline:
                                deadline_elapsed = True
                                account_blockers = ("okx_query_deadline_elapsed",)

                        if wants_positions and not deadline_elapsed:
                            remaining = _remaining_seconds(deadline)
                            if remaining > 0:
                                positions_started_at = datetime.now(_UTC)
                                positions_result = read_full_swap_positions(
                                    self.__client,
                                    self.__state,
                                    timeout_seconds=min(
                                        remaining, _MAX_REQUEST_TIMEOUT_SECONDS
                                    ),
                                )
                                positions_completed_at = datetime.now(_UTC)
                                if positions_result is None:
                                    position_blockers = (
                                        "okx_swap_positions_read_unavailable",
                                    )
                                elif positions_completed_at > deadline:
                                    deadline_elapsed = True
                                    position_blockers = (
                                        "okx_query_deadline_elapsed",
                                    )
                            else:
                                deadline_elapsed = True
                                position_blockers = ("okx_query_deadline_elapsed",)

                        remaining = _remaining_seconds(deadline)
                        after = (
                            read_authenticated_account_identity(
                                self.__client,
                                self.__state,
                                timeout_seconds=min(
                                    remaining, _MAX_REQUEST_TIMEOUT_SECONDS
                                ),
                            )
                            if remaining > 0
                            else None
                        )
                        if after is None:
                            if remaining <= 0:
                                deadline_elapsed = True
                                blocker = "okx_query_deadline_elapsed"
                            else:
                                blocker = "okx_account_identity_revalidation_unavailable"
                            account_blockers = account_blockers or (blocker,)
                            position_blockers = position_blockers or (blocker,)
                        elif not session_evidence_matches(before, after):
                            account_blockers = account_blockers or (
                                "okx_account_identity_changed_during_query",
                            )
                            position_blockers = position_blockers or (
                                "okx_account_identity_changed_during_query",
                            )
                        elif datetime.now(_UTC) > deadline:
                            deadline_elapsed = True
                            account_blockers = account_blockers or (
                                "okx_query_deadline_elapsed",
                            )
                            position_blockers = position_blockers or (
                                "okx_query_deadline_elapsed",
                            )
                        else:
                            evidence = after
                            if wants_account and balance_result is not None:
                                account_rows, account_blockers = _project_account_rows(
                                    balance_result,
                                    observed_at=account_completed_at,
                                )
                                valuation_record, valuation_blocker = (
                                    _project_account_valuation(
                                        balance_result,
                                        observed_at=account_completed_at,
                                    )
                                )
                            if wants_positions and positions_result is not None:
                                position_rows, position_blockers = _project_swap_positions(
                                    positions_result,
                                    environment=self.__environment,
                                    observed_at=positions_completed_at,
                                )
                    elif before is None:
                        blocker = (
                            "okx_account_identity_unavailable"
                            if _remaining_seconds(deadline) > 0
                            else "okx_query_deadline_elapsed"
                        )
                        account_blockers = (blocker,)
                        position_blockers = (blocker,)
                        deadline_elapsed = _remaining_seconds(deadline) <= 0

        # Recheck after projection and receipt preparation. A projection that
        # runs past its caller deadline must never retain complete evidence.
        if datetime.now(_UTC) > deadline:
            deadline_elapsed = True
        snapshots: list[QuerySnapshot] = []
        snapshot_evidence: list[_SnapshotEvidence] = []
        for request in selected:
            if request.request_ref in unsupported:
                snapshots.append(
                    _unavailable_snapshot(
                        request,
                        unsupported[request.request_ref],
                        source_ref=evidence.source_ref if evidence else None,
                        generation=evidence.generation if evidence else None,
                    )
                )
                continue
            if deadline_elapsed:
                snapshots.append(
                    _unknown_snapshot(request, "okx_query_deadline_elapsed")
                )
                continue
            if evidence is None:
                family_blockers = (
                    position_blockers
                    if request.family == _POSITIONS_FAMILY
                    else account_blockers
                )
                blocker = family_blockers[0] if family_blockers else "okx_query_unavailable"
                snapshots.append(_unknown_snapshot(request, blocker))
                continue

            if request.family == _ACCOUNT_FAMILY:
                if account_rows is None:
                    blocker = (
                        account_blockers[0]
                        if account_blockers
                        else "okx_account_query_unavailable"
                    )
                    snapshots.append(_unknown_snapshot(request, blocker))
                    continue
                blockers = account_blockers
                records = account_rows
                is_complete = not blockers
                snapshot = QuerySnapshot(
                    request=request,
                    source_ref=evidence.source_ref,
                    generation=evidence.generation,
                    snapshot_ref="okx-account-snapshot-v1-" + uuid.uuid4().hex,
                    completeness=(
                        QueryCompleteness.COMPLETE
                        if is_complete
                        else QueryCompleteness.PARTIAL
                    ),
                    started_at=account_started_at,
                    completed_at=account_completed_at,
                    observed_at=account_completed_at,
                    scope_complete=is_complete,
                    records=records,
                    blockers=blockers,
                )
            elif request.family == _VALUATION_FAMILY:
                if valuation_record is None:
                    snapshots.append(
                        _unavailable_snapshot(
                            request,
                            valuation_blocker or "okx_account_valuation_unavailable",
                            source_ref=evidence.source_ref,
                            generation=evidence.generation,
                        )
                    )
                    continue
                snapshot = QuerySnapshot(
                    request=request,
                    source_ref=evidence.source_ref,
                    generation=evidence.generation,
                    snapshot_ref="okx-account-valuation-snapshot-v1-" + uuid.uuid4().hex,
                    completeness=QueryCompleteness.COMPLETE,
                    started_at=account_started_at,
                    completed_at=account_completed_at,
                    observed_at=account_completed_at,
                    scope_complete=True,
                    records=(valuation_record,),
                )
            else:
                if position_rows is None:
                    blocker = (
                        position_blockers[0]
                        if position_blockers
                        else "okx_swap_positions_unavailable"
                    )
                    snapshots.append(_unknown_snapshot(request, blocker))
                    continue
                is_complete = not position_blockers
                snapshot = QuerySnapshot(
                    request=request,
                    source_ref=evidence.source_ref,
                    generation=evidence.generation,
                    snapshot_ref="okx-swap-positions-snapshot-v1-" + uuid.uuid4().hex,
                    completeness=(
                        QueryCompleteness.COMPLETE
                        if is_complete
                        else QueryCompleteness.PARTIAL
                    ),
                    started_at=positions_started_at,
                    completed_at=positions_completed_at,
                    observed_at=positions_completed_at,
                    scope_complete=is_complete,
                    records=position_rows,
                    blockers=position_blockers,
                )
            snapshots.append(snapshot)
            if snapshot.completeness is QueryCompleteness.COMPLETE:
                snapshot_completed_at = snapshot.completed_at
                if snapshot_completed_at is None:
                    raise RuntimeError("okx_complete_snapshot_missing_completion_time")
                expires_at_utc = snapshot_completed_at + _QUERY_EVIDENCE_TTL
                snapshot_evidence.append(
                    _SnapshotEvidence(
                        snapshot=snapshot,
                        session=evidence,
                        expires_at_utc=expires_at_utc,
                        expires_at_monotonic=time.monotonic()
                        + max(0.0, (expires_at_utc - datetime.now(_UTC)).total_seconds()),
                    )
                )

        if deadline_elapsed:
            snapshots = [
                _unknown_snapshot(request, "okx_query_deadline_elapsed")
                if snapshot.completeness is QueryCompleteness.COMPLETE
                else snapshot
                for request, snapshot in zip(selected, snapshots)
            ]
            snapshot_evidence.clear()
        receipt = QueryBatchReceipt(
            batch_ref="okx-query-batch-v1-" + uuid.uuid4().hex,
            source_ref=evidence.source_ref if evidence else None,
            generation=evidence.generation if evidence else None,
            started_at=started_at,
            completed_at=max(started_at, datetime.now(_UTC)),
            requests=selected,
            snapshots=tuple(snapshots),
            blockers=("okx_query_deadline_elapsed",) if deadline_elapsed else (),
        )
        if not deadline_elapsed and datetime.now(_UTC) > deadline:
            # Receipt hashing and immutable DTO validation happen after the
            # earlier projection deadline check. If that work crosses the
            # caller's deadline, revoke every complete snapshot before return.
            snapshot_evidence.clear()
            snapshots = [
                _unknown_snapshot(request, "okx_query_deadline_elapsed")
                if snapshot.completeness is QueryCompleteness.COMPLETE
                else snapshot
                for request, snapshot in zip(selected, snapshots)
            ]
            receipt = QueryBatchReceipt(
                batch_ref=receipt.batch_ref,
                source_ref=receipt.source_ref,
                generation=receipt.generation,
                started_at=receipt.started_at,
                completed_at=max(receipt.started_at, datetime.now(_UTC)),
                requests=selected,
                snapshots=tuple(snapshots),
                blockers=("okx_query_deadline_elapsed",),
            )
        self._remember_receipt(receipt, evidence, snapshot_evidence)
        return receipt

    def acquire_snapshot_lease(
        self,
        receipt: QueryBatchReceipt,
        *,
        purpose: str,
        expires_at: datetime,
    ) -> QuerySnapshotLease:
        if type(receipt) is not QueryBatchReceipt:
            raise TypeError("receipt must be an exact QueryBatchReceipt")
        _require_utc(expires_at, "expires_at")
        if type(purpose) is not str or not purpose or purpose != purpose.strip():
            raise ValueError("purpose must be non-empty trimmed text")
        now_utc = datetime.now(_UTC)
        now_monotonic = time.monotonic()
        with self.__lock:
            self.__prune(now_utc, now_monotonic)
            retained = self.__receipts.get(id(receipt))
            if (
                retained is None
                or retained.receipt is not receipt
                or retained.receipt.receipt_digest != receipt.receipt_digest
                or not receipt.complete
                or retained.snapshot_refs != receipt.complete_snapshot_refs
                or receipt.source_ref != retained.session.source_ref
                or receipt.generation != retained.session.generation
            ):
                raise ValueError("okx_query_receipt_not_current_or_complete")
            snapshots = tuple(self.__snapshots.get(ref) for ref in retained.snapshot_refs)
            if (
                not snapshots
                or any(item is None for item in snapshots)
                or any(
                    item.snapshot not in receipt.snapshots
                    or now_monotonic >= item.expires_at_monotonic
                    for item in snapshots
                    if item is not None
                )
            ):
                raise ValueError("okx_query_snapshot_evidence_expired")
            current = self.__state.current_evidence(
                now=now_utc,
                max_age_seconds=_QUERY_EVIDENCE_TTL.total_seconds(),
            )
            if not session_evidence_matches(current, retained.session):
                raise ValueError("okx_query_session_not_current")
            latest_expiry = min(item.expires_at_utc for item in snapshots if item is not None)
            effective_expiry = min(expires_at, latest_expiry)
            if effective_expiry <= now_utc:
                raise ValueError("okx_query_lease_expiry_outside_evidence_window")
            refs = receipt.complete_snapshot_refs
            lease = QuerySnapshotLease(
                lease_ref="okx-query-lease-v1-" + uuid.uuid4().hex,
                receipt_digest=receipt.receipt_digest,
                source_ref=receipt.source_ref,
                generation=receipt.generation,
                snapshot_refs=refs,
                issued_at=now_utc,
                expires_at=effective_expiry,
                purpose=purpose,
            )
            self.__leases[id(lease)] = _LeaseEvidence(
                lease=lease,
                receipt=receipt,
                session=retained.session,
                expires_at_monotonic=now_monotonic
                + (effective_expiry - now_utc).total_seconds(),
            )
            self.__leases.move_to_end(id(lease))
            while len(self.__leases) > _MAX_RETAINED_LEASES:
                self.__leases.popitem(last=False)
            return lease

    def validate_lease(
        self,
        lease: QuerySnapshotLease,
        receipt: QueryBatchReceipt,
        *,
        now: datetime,
    ) -> bool:
        if type(lease) is not QuerySnapshotLease or type(receipt) is not QueryBatchReceipt:
            raise TypeError("lease and receipt must use exact query protocol types")
        _require_utc(now, "now")
        with self.__lock:
            real_now = datetime.now(_UTC)
            now_monotonic = time.monotonic()
            self.__prune(real_now, now_monotonic)
            retained = self.__leases.get(id(lease))
            receipt_evidence = self.__receipts.get(id(receipt))
            if (
                retained is None
                or retained.lease is not lease
                or retained.receipt is not receipt
                or receipt_evidence is None
                or receipt_evidence.receipt is not receipt
                or not receipt.complete
                or now < lease.issued_at
                or now >= lease.expires_at
                or real_now >= lease.expires_at
                or now_monotonic >= retained.expires_at_monotonic
                or lease.receipt_digest != receipt.receipt_digest
                or lease.source_ref != receipt.source_ref
                or lease.generation != receipt.generation
                or lease.snapshot_refs != receipt.complete_snapshot_refs
                or receipt_evidence.snapshot_refs != lease.snapshot_refs
            ):
                return False
            for reference in lease.snapshot_refs:
                evidence = self.__snapshots.get(reference)
                if (
                    evidence is None
                    or evidence.snapshot not in receipt.snapshots
                    or now_monotonic >= evidence.expires_at_monotonic
                    or real_now >= evidence.expires_at_utc
                    or not session_evidence_matches(evidence.session, retained.session)
                ):
                    return False

        remaining = (lease.expires_at - datetime.now(_UTC)).total_seconds()
        if remaining <= 0:
            return False
        with self.__state.operation_lock:
            timeout = min(_MAX_REQUEST_TIMEOUT_SECONDS, remaining)
            current = read_authenticated_account_identity(
                self.__client,
                self.__state,
                timeout_seconds=timeout,
            )
        if not session_evidence_matches(current, retained.session):
            return False
        return datetime.now(_UTC) < lease.expires_at

    def _remember_receipt(
        self,
        receipt: QueryBatchReceipt,
        session: OkxSessionEvidence | None,
        snapshot_evidence: Sequence[_SnapshotEvidence],
    ) -> None:
        with self.__lock:
            self.__prune(datetime.now(_UTC), time.monotonic())
            if session is not None:
                refs = receipt.complete_snapshot_refs
                retained_snapshots = {item.snapshot.snapshot_ref: item for item in snapshot_evidence}
                if all(reference in retained_snapshots for reference in refs):
                    self.__receipts[id(receipt)] = _ReceiptEvidence(receipt, session, refs)
                    self.__receipts.move_to_end(id(receipt))
                    for reference in refs:
                        self.__snapshots[reference] = retained_snapshots[reference]
                        self.__snapshots.move_to_end(reference)
                    while len(self.__receipts) > _MAX_RETAINED_RECEIPTS:
                        _, removed = self.__receipts.popitem(last=False)
                        for reference in removed.snapshot_refs:
                            self.__snapshots.pop(reference, None)
            while len(self.__snapshots) > _MAX_RETAINED_RECEIPTS * 2:
                self.__snapshots.popitem(last=False)

    def __prune(self, now_utc: datetime, now_monotonic: float) -> None:
        for identity, evidence in tuple(self.__leases.items()):
            if now_utc >= evidence.lease.expires_at or now_monotonic >= evidence.expires_at_monotonic:
                self.__leases.pop(identity, None)
        for reference, evidence in tuple(self.__snapshots.items()):
            if now_utc >= evidence.expires_at_utc or now_monotonic >= evidence.expires_at_monotonic:
                self.__snapshots.pop(reference, None)
        for identity, evidence in tuple(self.__receipts.items()):
            if any(reference not in self.__snapshots for reference in evidence.snapshot_refs):
                self.__receipts.pop(identity, None)


def create_okx_provider_query_service(route: SelectedQueryRoute) -> OkxProviderQueryService:
    """Create the exact route-bound provider query service without network I/O."""

    if type(route) is not SelectedQueryRoute or route.exchange_name != EXCHANGE_NAME:
        raise ValueError("okx_query_route_invalid")
    state = account_read_state_for_route(route.exchange_name, route.client, route.environment)
    if state is None:
        raise ValueError("okx_query_route_unavailable")
    return OkxProviderQueryService(route, state)


def _project_account_rows(
    result: RequestData,
    *,
    observed_at: datetime,
) -> tuple[tuple[Mapping[str, Any], ...] | None, tuple[str, ...]]:
    account, blocker = _account_result_row(result)
    if account is None:
        return None, (blocker or "okx_account_response_invalid",)
    details = account.get("details")
    if type(details) is not list:
        return None, ("okx_account_details_unavailable",)

    observed_text = observed_at.astimezone(_UTC).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )
    records: list[Mapping[str, Any]] = []
    blockers: set[str] = set()
    seen_currencies: set[str] = set()
    if len(details) > MAX_ACCOUNT_ROWS:
        blockers.add("okx_account_balance_row_limit_exceeded")
    for row in details[:MAX_ACCOUNT_ROWS]:
        if type(row) is not dict:
            blockers.add("okx_account_balance_row_invalid")
            continue
        currency = row.get("ccy")
        if type(currency) is not str or not currency or currency != currency.strip():
            blockers.add("okx_account_balance_currency_invalid")
            continue
        if currency in seen_currencies:
            blockers.add("okx_account_balance_currency_duplicate")
            continue
        balance_fields = ("eq", "availBal", "frozenBal")
        if any(
            type(row.get(field)) is not str or not row.get(field)
            for field in balance_fields
        ):
            # Preserve any usable per-currency facts below, but do not claim
            # complete account coverage when OKX omits a published measure.
            blockers.add("okx_account_balance_measure_unavailable")
        try:
            # OKX defines eq as this currency's equity, availBal as this
            # currency's available balance, and frozenBal as frozen balance.
            # The resource labels denote the account-wide endpoint scope; they
            # do not assert the account's OKX margin mode.
            record = AccountBalance(
                resource=_ACCOUNT_RESOURCE,
                currency=currency,
                total=_optional_decimal_text(row, "eq"),
                available=_optional_decimal_text(row, "availBal"),
                locked=_optional_decimal_text(row, "frozenBal"),
                observed_at_utc=observed_text,
            ).to_dict()
        except Exception:
            blockers.add("okx_account_balance_row_invalid")
            continue
        seen_currencies.add(currency)
        records.append(record)
    return tuple(records), tuple(sorted(blockers))


def _project_account_valuation(
    result: RequestData,
    *,
    observed_at: datetime,
) -> tuple[Mapping[str, Any] | None, str | None]:
    account, blocker = _account_result_row(result)
    if account is None:
        return None, blocker or "okx_account_valuation_source_unavailable"
    try:
        total_equity_usd = _required_decimal_text(account, "totalEq")
        record = AccountValuation(
            currency="USD",
            available_cash=None,
            equity=total_equity_usd,
            observed_at_utc=observed_at.astimezone(_UTC)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z"),
        ).to_dict()
    except Exception:
        return None, "okx_account_usd_valuation_unavailable"
    # OKX documents totalEq as account-level USD equity. available_cash is
    # deliberately absent; per-currency available balances are never mixed
    # into the USD valuation.
    return record, None


def _project_swap_positions(
    result: RequestData,
    *,
    environment: str,
    observed_at: datetime | None,
) -> tuple[tuple[Mapping[str, Any], ...] | None, tuple[str, ...]]:
    """Project only the exact full-scope OKX SWAP position response.

    OKX reports SWAP size in contracts. Net-mode ``pos`` remains signed;
    long/short-mode rows retain the provider's explicit side and nonnegative
    size. ``avgPx`` is intentionally omitted because its denomination differs
    between linear and inverse contracts and this query does not resolve that
    contract metadata.
    """

    if type(result) is not RequestData or observed_at is None:
        return None, ("okx_swap_positions_result_unavailable",)
    extra = result.get_extra_data()
    if (
        result.get_request_type() != "get_position"
        or result.get_exchange_name() != EXCHANGE_NAME
        or result.get_symbol_name() != ""
        or result.get_asset_type() != _POSITION_PRODUCT_TYPE
        or type(extra) is not dict
        or extra.get("request_type") != "get_position"
        or extra.get("symbol_name") is not None
        or extra.get("asset_type") != _POSITION_PRODUCT_TYPE
        or extra.get("exchange_name") != EXCHANGE_NAME
        or extra.get("instType") != _POSITION_PRODUCT_TYPE
        or "posId" in extra
    ):
        return None, ("okx_swap_positions_result_route_invalid",)

    payload = result.get_input_data()
    if (
        type(payload) is not dict
        or type(payload.get("code")) is not str
        or payload.get("code") != "0"
        or type(payload.get("data")) is not list
    ):
        return None, ("okx_swap_positions_response_invalid",)

    data = payload["data"]
    blockers: set[str] = set()
    if len(data) > MAX_ACCOUNT_ROWS:
        blockers.add("okx_swap_positions_row_limit_exceeded")
    observed_text = (
        observed_at.astimezone(_UTC)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )
    records: list[Mapping[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in data[:MAX_ACCOUNT_ROWS]:
        if type(row) is not dict:
            blockers.add("okx_swap_positions_row_invalid")
            continue
        instrument_id = row.get("instId")
        margin_mode = row.get("mgnMode")
        side = row.get("posSide")
        quantity = row.get("pos")
        if (
            row.get("instType") != _POSITION_PRODUCT_TYPE
            or type(instrument_id) is not str
            or not instrument_id
            or instrument_id != instrument_id.strip()
            or type(margin_mode) is not str
            or margin_mode not in {"cross", "isolated"}
            or type(side) is not str
            or side not in {"net", "long", "short"}
            or type(quantity) is not str
        ):
            blockers.add("okx_swap_positions_row_scope_or_measure_invalid")
            continue
        identity = (instrument_id, margin_mode, side)
        if identity in seen:
            # The neutral position DTO has one row for each product/margin
            # resource, instrument and side. If OKX supplies colliding rows,
            # the current neutral schema cannot represent them losslessly.
            blockers.add("okx_swap_positions_identity_ambiguous")
            continue
        seen.add(identity)
        try:
            instrument = MarketInstrumentKey(
                provider="okx",
                venue="OKX",
                environment=environment,
                product_type=_POSITION_PRODUCT_TYPE,
                instrument_id=instrument_id,
                native_symbol=instrument_id,
            )
            record = AccountPosition(
                resource=AccountResourceKey(
                    product_type=_POSITION_PRODUCT_TYPE,
                    margin_pool=margin_mode,
                ),
                instrument=instrument,
                side=side,
                quantity=quantity,
                qty_unit="contract",
                average_price=None,
                price_currency=None,
                observed_at_utc=observed_text,
            ).to_dict()
        except Exception:
            blockers.add("okx_swap_positions_row_invalid")
            continue
        records.append(record)
    return tuple(records), tuple(sorted(blockers))


def _account_result_row(
    result: object,
) -> tuple[dict[str, Any] | None, str | None]:
    if (
        type(result) is not RequestData
        or result.get_request_type() != "get_account"
        or result.get_exchange_name() != EXCHANGE_NAME
        or result.get_symbol_name() != "ALL"
        or result.get_asset_type() != "SWAP"
    ):
        return None, "okx_account_response_route_invalid"
    payload = result.get_input_data()
    if (
        type(payload) is not dict
        or type(payload.get("code")) is not str
        or payload.get("code") != "0"
        or type(payload.get("data")) is not list
        or len(payload["data"]) != 1
        or type(payload["data"][0]) is not dict
    ):
        return None, "okx_account_response_shape_invalid"
    return payload["data"][0], None


def _optional_decimal_text(row: Mapping[str, Any], field: str) -> str | None:
    value = row.get(field)
    if value in (None, ""):
        return None
    if type(value) is not str:
        raise ValueError("okx_account_decimal_invalid")
    # Account DTO validation enforces the published finite, non-exponent form.
    return value


def _required_decimal_text(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if type(value) is not str or not value:
        raise ValueError("okx_account_decimal_invalid")
    return value


def _validate_requests(requests: Sequence[QueryRequest]) -> tuple[QueryRequest, ...]:
    if isinstance(requests, (str, bytes, bytearray)) or not isinstance(requests, Sequence):
        raise TypeError("requests must be a sequence of QueryRequest values")
    selected = tuple(requests)
    if not 1 <= len(selected) <= MAX_QUERY_BATCH_REQUESTS:
        raise ValueError("requests exceed the published query batch bounds")
    if any(type(request) is not QueryRequest for request in selected):
        raise TypeError("requests must contain exact QueryRequest values")
    refs = tuple(request.request_ref for request in selected)
    if len(set(refs)) != len(refs):
        raise ValueError("request_ref values must be unique within a query batch")
    return selected


def _unavailable_snapshot(
    request: QueryRequest,
    blocker: str,
    *,
    source_ref: str | None = None,
    generation: str | None = None,
) -> QuerySnapshot:
    return QuerySnapshot(
        request=request,
        source_ref=source_ref,
        generation=generation,
        snapshot_ref=None,
        completeness=QueryCompleteness.UNAVAILABLE,
        started_at=None,
        completed_at=None,
        observed_at=None,
        scope_complete=None,
        blockers=(blocker,),
    )


def _unknown_snapshot(request: QueryRequest, blocker: str) -> QuerySnapshot:
    return QuerySnapshot(
        request=request,
        source_ref=None,
        generation=None,
        snapshot_ref=None,
        completeness=QueryCompleteness.UNKNOWN,
        started_at=None,
        completed_at=None,
        observed_at=None,
        scope_complete=None,
        blockers=(blocker,),
    )


def _remaining_seconds(deadline: datetime) -> float:
    return max(0.0, (deadline - datetime.now(_UTC)).total_seconds())


def _require_utc(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must be timezone-aware UTC")
    return value


__all__ = ["OkxProviderQueryService", "create_okx_provider_query_service"]
