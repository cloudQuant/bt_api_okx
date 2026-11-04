"""Gateway execution observations for the OKX SWAP Demo provider (iteration 60).

``OkxSwapDemoAccountSessionProvider`` uses this reader to implement the
optional Gateway account-session capability ``read_execution_observations`` /
``confirm_execution_observations``. Everything here is read-only and comes from
the provider's signed ``GET`` routes for the explicitly configured SWAP
instruments (``instType=SWAP`` only):

* **Fills** come only from ``/api/v5/trade/fills`` rows (one row, one fill).
  Pages are newest first; the reader follows ``after`` (``billId``) down to its
  cursor, so the processed fills are contiguous. An order's cumulative
  quantity is never turned into a fill.
* **Orders** come from ``/api/v5/trade/orders-pending`` (the open set), a
  recent ``/api/v5/trade/orders-history`` window and ``/api/v5/trade/order``
  (query one order whose fill arrived first, or that left the open set). The
  first observation of an order in a session is queued before any of its
  fills, so the Gateway can route the fill by its order.
* **Identity.** ``order_id``/``trade_id`` are opaque ids issued by the injected
  observation issuer (the SDK's durable ``DurableOrderCorrelationIssuer`` is a
  ``bt_api_base`` ``ManagedOrderObservationIssuer``) from a transient private
  identity bound to the account; the same venue fact has the same id in every
  read and after a restart with the same issuer. A fill's identity is its
  instrument, order and ``tradeId`` (not ``billId``).
* **Units.** OKX states SWAP ``sz``/``accFillSz``/``fillSz`` in contracts:
  ``qty_unit`` is ``contract``. Prices stay without a currency (linear and
  inverse SWAPs differ; this reader resolves no contract metadata).
* **Fees.** OKX reports a charged fee as a negative ``fee``: the Base fee is
  ``-fee`` in ``feeCcy``. A positive ``fee`` is a rebate, which the Base
  non-negative fee cannot represent: the fee is unknown (``None``) and counted.
* **Scope.** Rows of another instrument or product type, or of an
  isolated-margin order, are refused with a finite counter code; malformed
  rows fail the read closed instead.

A reader belongs to one provider ``connect`` generation; nothing is confirmed
until the worker confirms it, and unconfirmed observations are returned again.
"""

from __future__ import annotations

import json
import re
from collections import OrderedDict, deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from itertools import islice
from types import MappingProxyType
from typing import Any

from bt_api_base.account_protocol import AccountKey, AccountResourceKey
from bt_api_base.execution_query_protocol import ExecutionOrderRecord, ExecutionTradeRecord
from bt_api_base.execution_row_observation_protocol import (
    AccountExecutionOrderObservation,
    AccountExecutionTradeObservation,
    execution_observation_fact_digest,
    execution_observation_fact_id,
)
from bt_api_base.market_protocol import MarketInstrumentKey

PROVIDER_NAME = "okx"
PRODUCT_TYPE = "SWAP"
SWAP_CROSS_RESOURCE = AccountResourceKey(product_type=PRODUCT_TYPE, margin_pool="cross")
QTY_UNIT = "contract"

PAGE_LIMIT = 100
MAX_HISTORY_PAGES = 10
MAX_PENDING_PAGES = 5
MAX_PENDING = 8192
MAX_INSTRUMENTS = 10
MAX_TRACKED_ORDERS_PER_INSTRUMENT = 500
MAX_LOOKUPS_PER_INSTRUMENT = 32
WINDOW_OVERLAP_MS = 60_000
MIN_LOOKBACK_SECONDS = 60
# /api/v5/trade/fills covers the last three days.
MAX_LOOKBACK_SECONDS = 3 * 86_400 - 3_600
MAX_POLL_INTERVAL_SECONDS = 300.0
_MAX_REMEMBERED = 65_536

COUNTER_CODES = frozenset(
    {
        "EXECUTION_ROW_INSTRUMENT_OUT_OF_SCOPE",
        "EXECUTION_ROW_PRODUCT_OUT_OF_SCOPE",
        "EXECUTION_ROW_MARGIN_POOL_OUT_OF_SCOPE",
        "EXECUTION_FEE_REBATE_UNREPRESENTABLE",
        "EXECUTION_FEE_UNAVAILABLE",
        "EXECUTION_POLL_INTERRUPTED",
    }
)

INST_ID = re.compile(r"[A-Z0-9]{1,16}-[A-Z0-9]{1,16}-SWAP\Z", re.ASCII)
_ORDER_ID = re.compile(r"sdk-order-observation-v1-[0-9a-f]{64}\Z", re.ASCII)
_TRADE_ID = re.compile(r"sdk-trade-observation-v1-[0-9a-f]{64}\Z", re.ASCII)
_VENUE_DECIMAL = re.compile(r"-?[0-9]{1,40}(?:\.[0-9]{1,40})?\Z", re.ASCII)
_VENUE_ID = re.compile(r"[0-9]{1,20}\Z", re.ASCII)
_ORDER_TYPE = re.compile(r"[a-z][a-z_]{0,31}\Z", re.ASCII)
_CURRENCY = re.compile(r"[A-Z0-9]{1,16}\Z", re.ASCII)
_TERMINAL = frozenset({"filled", "canceled", "partially_filled_canceled"})


class ExecutionReadIssue(Exception):
    """Internal finite failure; the provider re-raises it as its own error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _invalid() -> ExecutionReadIssue:
    return ExecutionReadIssue("EXECUTION_ROW_INVALID")


def _venue_id(value: Any) -> int:
    if type(value) is not str or not _VENUE_ID.fullmatch(value):
        raise _invalid()
    return int(value)


def _decimal_text(value: Any, *, positive: bool = False, signed: bool = False) -> str:
    if type(value) is not str or not _VENUE_DECIMAL.fullmatch(value):
        raise _invalid()
    if value.startswith("-") and not signed:
        raise _invalid()
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise _invalid() from None
    if positive and number <= 0:
        raise _invalid()
    text = format(number, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        text = "0"
    return text


def _utc_from_ms_text(value: Any) -> str:
    milliseconds = _venue_id(value)
    if not 0 < milliseconds <= 253402300799999:
        raise _invalid()
    return (
        datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _side(value: Any) -> str:
    if value in {"buy", "sell"}:
        return value
    raise _invalid()


def _position(value: Any, side: str) -> tuple[str, str | None]:
    # Net mode cannot state whether a row opened or closed a position.
    if value == "net":
        return "unavailable", None
    if value == "long":
        return ("open" if side == "buy" else "close"), "long"
    if value == "short":
        return ("open" if side == "sell" else "close"), "short"
    raise _invalid()


def _status(value: Any, filled_positive: bool) -> str:
    if value == "live":
        return "open"
    if value == "partially_filled":
        return "partially_filled"
    if value == "filled":
        return "filled"
    if value in {"canceled", "mmp_canceled"}:
        return "partially_filled_canceled" if filled_positive else "canceled"
    raise _invalid()


def _client_order_id(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if (
        type(value) is not str
        or len(value) > 64
        or value != value.strip()
        or not value.isascii()
        or not value.isprintable()
    ):
        raise _invalid()
    return value


def _row(value: Any) -> dict[str, Any]:
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise _invalid()
    return value


def _private_identity(kind: str, **fields: str) -> str:
    return json.dumps(
        {"schema": f"bt_api_okx.swap_{kind}_observation_identity.v1", **fields},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


@dataclass
class _InstrumentCursor:
    initialized: bool = False
    order_window_start_ms: int | None = None
    fill_bill_id: int | None = None
    fill_window_start_ms: int | None = None
    tracked: dict[int, None] = field(default_factory=dict)


@dataclass
class _OrderView:
    native: int
    observation: AccountExecutionOrderObservation | None
    terminal: bool
    margin: str | None
    refusal: str | None = None
    filled: Decimal = Decimal(0)


@dataclass
class _InstrumentBatch:
    first_orders: list[AccountExecutionOrderObservation]
    fills: list[AccountExecutionTradeObservation]
    later_orders: list[AccountExecutionOrderObservation]
    margins: dict[int, str | None]
    cursor: _InstrumentCursor
    counts: dict[str, int]

    @property
    def items(self) -> list[Any]:
        return [*self.first_orders, *self.fills, *self.later_orders]


class OkxSwapExecutionReader:
    """Pending execution observations of one provider generation."""

    def __init__(
        self,
        *,
        account_key: AccountKey,
        inst_ids: tuple[str, ...],
        lookback_seconds: int,
        poll_interval_seconds: float,
        observation_issuer: Any,
        request: Callable[[str, Mapping[str, str], float], list[Any]],
        exchange_now_ms: Callable[[float], int],
        utc_now: Callable[[], str],
        monotonic: Callable[[], float],
    ) -> None:
        self._account_key = account_key
        self._inst_ids = inst_ids
        self._lookback_ms = lookback_seconds * 1000
        self._poll_interval = float(poll_interval_seconds)
        self._issuer = observation_issuer
        self._request = request
        self._exchange_now_ms = exchange_now_ms
        self._utc_now = utc_now
        self._monotonic = monotonic
        self._pending: deque[Any] = deque()
        self._outstanding = 0
        self._next_poll: float | None = None
        self._rotation = 0
        self._cursors = {inst_id: _InstrumentCursor() for inst_id in inst_ids}
        self._queued: OrderedDict[str, str] = OrderedDict()
        # (instId, ordId) -> margin pool of each order seen in this session.
        self._known: OrderedDict[tuple[str, int], str | None] = OrderedDict()
        self._refused: OrderedDict[tuple[str, ...], None] = OrderedDict()
        self._counters: dict[str, int] = {}

    @property
    def counters(self) -> Mapping[str, int]:
        return MappingProxyType(dict(self._counters))

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    def read(self, *, limit: int, deadline: float) -> tuple[Any, ...]:
        if type(limit) is not int or not 1 <= limit <= MAX_PENDING:
            raise ExecutionReadIssue("INVALID_LIMIT")
        self._outstanding = 0
        if not self._pending:
            now = self._monotonic()
            if self._next_poll is None or now >= self._next_poll:
                self._next_poll = now + self._poll_interval
                self._poll(deadline)
        items = tuple(islice(self._pending, limit))
        self._outstanding = len(items)
        return items

    def confirm(self, count: int) -> None:
        if type(count) is not int or not 1 <= count <= self._outstanding:
            raise ExecutionReadIssue("EXECUTION_CONFIRM_INVALID")
        for _ in range(count):
            self._pending.popleft()
        self._outstanding -= count

    # -- polling --------------------------------------------------------------

    def _poll(self, deadline: float) -> None:
        now_ms = self._exchange_now_ms(deadline)
        observed = self._utc_now()
        count = len(self._inst_ids)
        start = self._rotation
        self._rotation = (start + 1) % count
        for offset in range(count):
            inst_id = self._inst_ids[(start + offset) % count]
            try:
                batch = self._poll_instrument(
                    inst_id, now_ms=now_ms, observed=observed, deadline=deadline
                )
            except Exception:
                if self._pending:
                    self._bump("EXECUTION_POLL_INTERRUPTED")
                    return
                raise
            if len(self._pending) + len(batch.items) > MAX_PENDING:
                return
            self._commit(inst_id, batch)

    def _commit(self, inst_id: str, batch: _InstrumentBatch) -> None:
        for item in batch.items:
            self._remember(self._queued, execution_observation_fact_id(item), _digest(item))
            self._pending.append(item)
        for native, margin in batch.margins.items():
            self._remember(self._known, (inst_id, native), margin)
        self._cursors[inst_id] = batch.cursor
        for code, amount in batch.counts.items():
            self._counters[code] = self._counters.get(code, 0) + amount

    def _pages(
        self,
        route: str,
        params: dict[str, str],
        *,
        id_field: str,
        max_pages: int,
        overflow: str,
        deadline: float,
        stop_at: int | None = None,
    ) -> list[dict[str, Any]]:
        """Follow newest-first pages with ``after`` until a short page or ``stop_at``."""

        rows: list[dict[str, Any]] = []
        after: int | None = None
        for _page in range(max_pages):
            query = dict(params)
            query["limit"] = str(PAGE_LIMIT)
            if after is not None:
                query["after"] = str(after)
            data = self._request(route, query, deadline)
            if type(data) is not list or len(data) > PAGE_LIMIT:
                raise _invalid()
            page = [_row(item) for item in data]
            rows.extend(page)
            if len(page) < PAGE_LIMIT:
                return rows
            ids = [_venue_id(item.get(id_field)) for item in page]
            if stop_at is not None and min(ids) <= stop_at:
                return rows
            after = min(ids)
        raise ExecutionReadIssue(overflow)

    def _poll_instrument(
        self, inst_id: str, *, now_ms: int, observed: str, deadline: float
    ) -> _InstrumentBatch:
        cursor = self._cursors[inst_id]
        counts: dict[str, int] = {}
        refused_now: set[tuple[str, ...]] = set()

        def refuse(code: str, key: tuple[str, ...]) -> None:
            if key in self._refused or key in refused_now:
                return
            refused_now.add(key)
            self._remember(self._refused, key, None)
            counts[code] = counts.get(code, 0) + 1

        lookback_start = now_ms - self._lookback_ms
        scope = {"instType": PRODUCT_TYPE, "instId": inst_id}
        open_rows = self._pages(
            "orders_pending",
            dict(scope),
            id_field="ordId",
            max_pages=MAX_PENDING_PAGES,
            overflow="EXECUTION_TRACKED_ORDERS_EXCEEDED",
            deadline=deadline,
        )
        window_start = cursor.order_window_start_ms if cursor.initialized else lookback_start
        assert window_start is not None
        history_rows = self._pages(
            "orders_history",
            {**scope, "begin": str(window_start)},
            id_field="ordId",
            max_pages=MAX_HISTORY_PAGES,
            overflow="EXECUTION_LOOKBACK_TRUNCATED",
            deadline=deadline,
        )
        if cursor.fill_bill_id is None:
            fill_start = cursor.fill_window_start_ms
            if fill_start is None:
                fill_start = lookback_start
            fill_rows = self._pages(
                "fills",
                {**scope, "begin": str(fill_start)},
                id_field="billId",
                max_pages=MAX_HISTORY_PAGES,
                overflow="EXECUTION_LOOKBACK_TRUNCATED",
                deadline=deadline,
            )
        else:
            fill_start = None
            fill_rows = self._pages(
                "fills",
                dict(scope),
                id_field="billId",
                max_pages=MAX_HISTORY_PAGES,
                overflow="EXECUTION_BACKLOG_EXCEEDED",
                deadline=deadline,
                stop_at=cursor.fill_bill_id,
            )

        views: list[_OrderView] = [
            self._order_view(row, inst_id, observed) for row in [*open_rows, *history_rows]
        ]
        present: dict[int, str | None] = {view.native: view.margin for view in views}
        lookups = MAX_LOOKUPS_PER_INSTRUMENT
        for native in list(cursor.tracked):
            if native in present:
                continue
            if lookups == 0:
                break
            lookups -= 1
            view = self._lookup(inst_id, native, observed, deadline)
            views.append(view)
            present[native] = view.margin

        parsed: list[tuple[int, int, dict[str, Any]]] = []
        for row in fill_rows:
            refusal = self._scope_refusal(row, inst_id)
            if refusal is not None:
                refuse(refusal, ("fill", inst_id, repr(row.get("billId"))))
                continue
            bill = _venue_id(row.get("billId"))
            if cursor.fill_bill_id is not None and bill <= cursor.fill_bill_id:
                continue
            parsed.append((bill, _venue_id(row.get("ordId")), row))
        # Ascending billId: duplicate or out-of-order pages give the same facts.
        parsed.sort(key=lambda entry: (entry[0], entry[1]))
        trades: list[tuple[AccountExecutionTradeObservation, str | None]] = []
        next_bill = cursor.fill_bill_id
        last_processed: int | None = None
        stopped_bill: int | None = None
        for bill, order_native, row in parsed:
            known = self._known.get((inst_id, order_native), ...)
            margin = present.get(order_native, known)
            if margin is ...:
                if lookups == 0:
                    stopped_bill = bill
                    break
                lookups -= 1
                view = self._lookup(inst_id, order_native, observed, deadline)
                views.append(view)
                present[order_native] = margin = view.margin
            last_processed = bill
            if margin != "cross":
                refuse(
                    "EXECUTION_ROW_MARGIN_POOL_OUT_OF_SCOPE",
                    ("fill", inst_id, str(order_native), str(row.get("tradeId"))),
                )
                continue
            trades.append(self._trade(row, inst_id, order_native, observed))
        # The cursor is the last processed billId; an early stop resumes at the
        # first unprocessed fill (also in the initial window).
        resume_after = None if stopped_bill is None else stopped_bill - 1
        if resume_after is None:
            resume_after = last_processed
        if resume_after is not None:
            next_bill = resume_after if next_bill is None else max(next_bill, resume_after)

        views.sort(key=lambda view: (view.native, view.terminal, view.filled))
        first_orders: list[AccountExecutionOrderObservation] = []
        later_orders: list[AccountExecutionOrderObservation] = []
        seen_facts: set[str] = set()
        first_seen: set[int] = set()
        tracked = dict(cursor.tracked)
        margins: dict[int, str | None] = {}
        for view in views:
            margins[view.native] = view.margin
            if view.refusal is not None:
                refuse(view.refusal, ("order", inst_id, str(view.native)))
                tracked.pop(view.native, None)
                continue
            if view.terminal:
                tracked.pop(view.native, None)
            elif view.native not in tracked:
                tracked[view.native] = None
            observation = view.observation
            assert observation is not None
            fact = execution_observation_fact_id(observation)
            digest = _digest(observation)
            if fact in seen_facts or self._queued.get(fact) == digest:
                continue
            seen_facts.add(fact)
            # The first observation of an order new to this session goes ahead
            # of the fills (it carries the route); the rest follow them.
            if (inst_id, view.native) in self._known or view.native in first_seen:
                later_orders.append(observation)
            else:
                first_seen.add(view.native)
                first_orders.append(observation)
        if len(tracked) > MAX_TRACKED_ORDERS_PER_INSTRUMENT:
            raise ExecutionReadIssue("EXECUTION_TRACKED_ORDERS_EXCEEDED")
        trade_facts: set[str] = set()
        unique_trades: list[AccountExecutionTradeObservation] = []
        for trade, fee_note in trades:
            fact = execution_observation_fact_id(trade)
            if fact in trade_facts or self._queued.get(fact) == _digest(trade):
                continue
            trade_facts.add(fact)
            unique_trades.append(trade)
            if fee_note is not None:
                counts[fee_note] = counts.get(fee_note, 0) + 1

        next_cursor = _InstrumentCursor(
            initialized=True,
            order_window_start_ms=max(window_start, now_ms - WINDOW_OVERLAP_MS),
            fill_bill_id=next_bill,
            fill_window_start_ms=(
                None if next_bill is not None or fill_start is None
                else max(fill_start, now_ms - WINDOW_OVERLAP_MS)
            ),
            tracked=tracked,
        )
        return _InstrumentBatch(
            first_orders, unique_trades, later_orders, margins, next_cursor, counts
        )

    def _lookup(self, inst_id: str, native: int, observed: str, deadline: float) -> _OrderView:
        data = self._request("order", {"instId": inst_id, "ordId": str(native)}, deadline)
        if type(data) is not list or len(data) != 1:
            raise _invalid()
        view = self._order_view(_row(data[0]), inst_id, observed)
        if view.native != native:
            raise _invalid()
        return view

    # -- projection -----------------------------------------------------------

    @staticmethod
    def _scope_refusal(row: dict[str, Any], inst_id: str) -> str | None:
        if row.get("instType") != PRODUCT_TYPE:
            return "EXECUTION_ROW_PRODUCT_OUT_OF_SCOPE"
        if row.get("instId") != inst_id:
            return "EXECUTION_ROW_INSTRUMENT_OUT_OF_SCOPE"
        return None

    def _order_view(self, row: dict[str, Any], inst_id: str, observed: str) -> _OrderView:
        native = _venue_id(row.get("ordId"))
        refusal = self._scope_refusal(row, inst_id)
        if refusal is not None:
            return _OrderView(native, None, True, None, refusal)
        margin = row.get("tdMode")
        if margin not in {"cross", "isolated"}:
            raise _invalid()
        if margin == "isolated":
            return _OrderView(native, None, True, margin, "EXECUTION_ROW_MARGIN_POOL_OUT_OF_SCOPE")
        side = _side(row.get("side"))
        effect, position_side = _position(row.get("posSide"), side)
        order_type = row.get("ordType")
        if type(order_type) is not str or not _ORDER_TYPE.fullmatch(order_type):
            raise _invalid()
        quantity = _decimal_text(row.get("sz"), positive=True)
        filled = _decimal_text(row.get("accFillSz"))
        if Decimal(filled) > Decimal(quantity):
            raise _invalid()
        status = _status(row.get("state"), Decimal(filled) > 0)
        price = row.get("px")
        limit_price = None if price in (None, "") else _decimal_text(price)
        if limit_price is not None and Decimal(limit_price) == 0:
            limit_price = None
        client = _client_order_id(row.get("clOrdId"))
        try:
            record = ExecutionOrderRecord(
                resource=SWAP_CROSS_RESOURCE,
                instrument=self._instrument(inst_id),
                order_id=self._order_id(inst_id, native),
                client_order_id=client,
                intent_binding="unresolved" if client is None else "verified",
                side=side,
                position_effect=effect,
                position_side=position_side,
                position_side_status="unavailable" if position_side is None else "verified",
                order_type=order_type,
                status=status,
                quantity=quantity,
                filled_quantity=filled,
                qty_unit=QTY_UNIT,
                limit_price=limit_price,
                price_currency=None,
                price_currency_status="unavailable",
                created_at_utc=_utc_from_ms_text(row.get("cTime")),
                created_at_status="verified",
                observed_at_utc=observed,
            )
            observation = AccountExecutionOrderObservation(self._account_key, record)
        except (TypeError, ValueError):
            raise _invalid() from None
        return _OrderView(native, observation, status in _TERMINAL, margin, filled=Decimal(filled))

    def _trade(
        self, row: dict[str, Any], inst_id: str, order_native: int, observed: str
    ) -> tuple[AccountExecutionTradeObservation, str | None]:
        side = _side(row.get("side"))
        effect, position_side = _position(row.get("posSide"), side)
        trade_native = _venue_id(row.get("tradeId"))
        quantity = _decimal_text(row.get("fillSz"), positive=True)
        price = _decimal_text(row.get("fillPx"), positive=True)
        traded = row.get("fillTime")
        if traded in (None, ""):
            traded = row.get("ts")
        fee: str | None = None
        currency: str | None = None
        note: str | None = None
        raw_fee = row.get("fee")
        raw_currency = row.get("feeCcy")
        if raw_fee in (None, "") or raw_currency in (None, ""):
            note = "EXECUTION_FEE_UNAVAILABLE"
        else:
            amount = Decimal(_decimal_text(raw_fee, signed=True))
            if type(raw_currency) is not str or not _CURRENCY.fullmatch(raw_currency):
                raise _invalid()
            if amount > 0:
                # A positive OKX fee is a rebate: not a non-negative fee.
                note = "EXECUTION_FEE_REBATE_UNREPRESENTABLE"
            else:
                # OKX charges are negative; the Base fee is the charged amount.
                fee = "0" if amount == 0 else _decimal_text(format(-amount, "f"))
                currency = raw_currency
        try:
            record = ExecutionTradeRecord(
                resource=SWAP_CROSS_RESOURCE,
                instrument=self._instrument(inst_id),
                trade_id=self._trade_id(inst_id, order_native, trade_native),
                order_id=self._order_id(inst_id, order_native),
                order_binding="provider_order_identity",
                side=side,
                position_effect=effect,
                position_side=position_side,
                position_side_status="unavailable" if position_side is None else "verified",
                quantity=quantity,
                qty_unit=QTY_UNIT,
                price=price,
                price_currency=None,
                price_currency_status="unavailable",
                traded_at_utc=_utc_from_ms_text(traded),
                traded_at_status="verified",
                observed_at_utc=observed,
            )
            observation = AccountExecutionTradeObservation(self._account_key, record, fee, currency)
        except (TypeError, ValueError):
            raise _invalid() from None
        return observation, note

    def _instrument(self, inst_id: str) -> MarketInstrumentKey:
        key = self._account_key
        return MarketInstrumentKey(
            provider=key.provider,
            venue=key.venue,
            environment=key.environment,
            product_type=PRODUCT_TYPE,
            instrument_id=inst_id,
            native_symbol=inst_id,
        )

    def _order_id(self, inst_id: str, native: int) -> str:
        identity = _private_identity("order", inst_id=inst_id, ord_id=str(native))
        return self._issue("issue_order_observation_id", identity, _ORDER_ID)

    def _trade_id(self, inst_id: str, order_native: int, trade_native: int) -> str:
        identity = _private_identity(
            "trade", inst_id=inst_id, ord_id=str(order_native), trade_id=str(trade_native)
        )
        return self._issue("issue_trade_observation_id", identity, _TRADE_ID)

    def _issue(self, method: str, identity: str, pattern: re.Pattern[str]) -> str:
        key = self._account_key
        try:
            issued = getattr(self._issuer, method)(
                PROVIDER_NAME, key.environment, key.account_key_id, identity
            )
        except Exception:
            raise ExecutionReadIssue("EXECUTION_IDENTITY_UNAVAILABLE") from None
        if type(issued) is not str or not pattern.fullmatch(issued):
            raise ExecutionReadIssue("EXECUTION_IDENTITY_UNAVAILABLE")
        return issued

    def _bump(self, code: str) -> None:
        self._counters[code] = self._counters.get(code, 0) + 1

    @staticmethod
    def _remember(store: OrderedDict, key: Any, value: Any) -> None:
        store[key] = value
        store.move_to_end(key)
        while len(store) > _MAX_REMEMBERED:
            store.popitem(last=False)


def _digest(observation: Any) -> str:
    return execution_observation_fact_digest(observation)


__all__ = [
    "COUNTER_CODES",
    "ExecutionReadIssue",
    "INST_ID",
    "MAX_INSTRUMENTS",
    "MAX_LOOKBACK_SECONDS",
    "MAX_POLL_INTERVAL_SECONDS",
    "MIN_LOOKBACK_SECONDS",
    "OkxSwapExecutionReader",
    "PAGE_LIMIT",
    "QTY_UNIT",
    "SWAP_CROSS_RESOURCE",
]
