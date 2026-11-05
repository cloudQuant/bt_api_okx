"""OKX SWAP direct write provider (iteration 62, no execution session).

Registered for ``bt_api.direct_write_providers`` / ``OKX___SWAP``.  The SDK
(``bt_api_py.direct_write``) owns write admission and the pre-dispatch commit
ordering; this module owns only OKX facts and native REST calls:

* **Identity.**  The native identity is the request's ``client_order_id`` sent
  unchanged as ``clOrdId`` (OKX: 1-32 ASCII letters/digits) plus the native
  ``instId``.  An id that violates the venue rule is refused, never rewritten.
  ``fields`` carry ``inst_id``, ``trading_day`` (UTC date of the reservation)
  and, once the venue returns it, ``ord_id``.
* **Requests.**  The request is validated and mapped *before* any reservation
  by the provider-owned ``map_order_request`` and the feed's own ``_make_order``
  builder (no network).  Only native symbols (``BTC-USDT-SWAP``) and contract
  quantities (``quantity_unit`` ``contracts``/``native``) are accepted: OKX SWAP
  ``sz`` is a contract count, and the feed's base-to-contract path is not a
  verified conversion.
* **Sends.**  ``submit_order``/``cancel_order`` consume the SDK one-shot grant
  immediately before the single ``POST`` (one HTTP attempt).  A venue error code
  that the provider classification marks as a definite rejection returns
  ``sent=False``; every other failure after the grant was consumed raises
  :class:`OkxDirectOutcomeUnknown`, which is deliberately *not* a
  ``DirectWriteError`` so the SDK coordinator reports the outcome as unknown.
* **Returns.**  OKX REST has no push here, so returns are polled: on
  ``drain_execution_events`` each watched order is queried at most once per
  ``poll_interval`` (bounded per drain), and its fills (``/trade/fills`` rows with
  ``tradeId``) are read when the cumulative fill grows.  Events are emitted only
  on change; terminal orders stop being watched once their fills are complete.
* **Account facts.**  Positions and balance reuse the provider-owned signed
  reads in :mod:`bt_api_okx.account_read_state`; working orders, the day's
  orders and fills are paged ``GET`` reads.  A section is complete only when
  every page was read.

OKX has no settlement-confirmation step; nothing here decides admission, and
credentials are never logged or returned (``account_reference`` is a hash).
"""

from __future__ import annotations

import hashlib
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Iterable, Mapping, Optional
from uuid import uuid4

from bt_api_base.direct_write_protocol import (
    DirectAccountFacts,
    DirectBalanceFact,
    DirectExecutionEvent,
    DirectExecutionEventKind,
    DirectOrderReservation,
    DirectOrderStatus,
    DirectPositionFact,
    DirectSubmitResult,
    DirectWriteError,
    NativeOrderIdentity,
    SettlementStatus,
    WriteGrant,
    WriteGrantVerifier,
    WriteOperation,
)

from bt_api_okx.provider_configuration_registration import EXCHANGE_NAME

__all__ = (
    "OKX_DIRECT_WRITE_EXCHANGE",
    "OkxDirectOutcomeUnknown",
    "OkxDirectWriteProvider",
    "create_okx_direct_write_provider",
    "register_okx_direct_write_provider",
)

OKX_DIRECT_WRITE_EXCHANGE = EXCHANGE_NAME
_SESSION_GENERATION = 1
_CLIENT_ORDER_ID = re.compile(r"[A-Za-z0-9]{1,32}\Z", re.ASCII)
_VENUE_ID = re.compile(r"[0-9]{1,24}\Z", re.ASCII)
_ORDER_TYPES = frozenset({"limit", "market", "post_only", "ioc", "fok"})
_STATUS = {
    "live": DirectOrderStatus.ACCEPTED,
    "partially_filled": DirectOrderStatus.PARTIALLY_FILLED,
    "filled": DirectOrderStatus.FILLED,
    "canceled": DirectOrderStatus.CANCELLED,
    "mmp_canceled": DirectOrderStatus.CANCELLED,
}
_TERMINAL_STATES = frozenset({"filled", "canceled", "mmp_canceled"})
_ORDER_NOT_FOUND_CODE = "51603"
_PAGE_LIMIT = 100
_MAX_PAGES = 20
_MAX_FILL_PAGES = 10
_MAX_EVENTS = 50_000
_MAX_NOT_FOUND_BACKOFF = 30.0
_TERMINAL_FILL_GRACE = 60.0
# GET /api/v5/trade/fills serves the last three days.
_FILLS_WINDOW_MS = 3 * 86_400_000
_FILL_RETRY_FAST = 5
_MAX_FILL_BACKOFF = 30.0
_SERVER_TIME_PATH = "GET /api/v5/public/time"
_SERVER_TIME_TTL = 60.0
_SERVER_TIME_RETRY = 5.0
_MAX_AUTO_WATCHED = 64
_MAX_FACTS_TIMEOUT = 10.0


class OkxDirectOutcomeUnknown(RuntimeError):
    """The native call may have reached OKX; whether it took effect is unknown.

    Not a ``DirectWriteError`` on purpose: the SDK coordinator maps every
    ``DirectWriteError`` outside its unknown-outcome code set to "not sent",
    and maps any other exception to an unknown outcome.  ``code`` is one of
    ``okx_direct_submit_outcome_unknown`` / ``okx_direct_cancel_outcome_unknown``.
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else f"{code}: {detail}")


class _OrderNotFound(Exception):
    pass


# ---------------------------------------------------------------------------
# small pure helpers
# ---------------------------------------------------------------------------
def _decimal(value: Any) -> Optional[Decimal]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        value = repr(value)
    if type(value) is not str:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def _float(value: Any) -> Optional[float]:
    number = _decimal(value)
    return None if number is None else float(number)


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _utc_day(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime("%Y%m%d")


def _utc_day_start_ms(epoch_seconds: float) -> int:
    moment = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    start = moment.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(start.timestamp() * 1000)


def _ms(value: Any) -> Optional[int]:
    text = _text(value)
    if text is None or not _VENUE_ID.fullmatch(text):
        return None
    return int(text)


def _iso_from_ms(value: Any) -> Optional[str]:
    milliseconds = _ms(value)
    if milliseconds is None or not 0 < milliseconds <= 253402300799999:
        return None
    return (
        datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _day_from_ms(value: Any) -> Optional[str]:
    milliseconds = _ms(value)
    if milliseconds is None or not 0 < milliseconds <= 253402300799999:
        return None
    return _utc_day(milliseconds / 1000)


def _detail(exc: BaseException) -> str:
    detail = getattr(exc, "detail", None)
    text = detail if isinstance(detail, str) and detail else str(exc)
    return text[:200]


def _offset(pos_side: Optional[str], side: Optional[str], reduce_only: Optional[bool]) -> Optional[str]:
    """Open/close as OKX states it; ``None`` when the venue does not say.

    Long/short mode: ``posSide`` with the side decides.  Net mode cannot state
    whether a fill opened or closed, except for reduce-only orders, which OKX
    only lets reduce a position.
    """

    if pos_side == "long" and side in ("buy", "sell"):
        return "open" if side == "buy" else "close"
    if pos_side == "short" and side in ("buy", "sell"):
        return "open" if side == "sell" else "close"
    if reduce_only is True:
        return "close"
    return None


def _reduce_only(value: Any) -> Optional[bool]:
    if value is True or value == "true":
        return True
    if value is False or value == "false":
        return False
    return None


def _payload(result: Any) -> Any:
    getter = getattr(result, "get_input_data", None)
    return getter() if callable(getter) else None


def _rows(result: Any) -> list[dict[str, Any]]:
    payload = _payload(result)
    if (
        type(payload) is not dict
        or str(payload.get("code")) != "0"
        or type(payload.get("data")) is not list
    ):
        raise ValueError("okx_response_shape_invalid")
    rows = payload["data"]
    if any(type(row) is not dict for row in rows):
        raise ValueError("okx_response_row_invalid")
    return rows


def _native_error_code(exc: BaseException) -> Optional[str]:
    """OKX error code carried by a translated venue error, if any."""

    try:
        raw = getattr(exc, "raw_response", None)
    except Exception:
        return None
    if not isinstance(raw, Mapping):
        return None
    data = raw.get("data")
    if isinstance(data, list) and data and isinstance(data[0], Mapping):
        s_code = _text(data[0].get("sCode"))
        if s_code is not None and s_code != "0":
            return s_code
    code = _text(raw.get("code"))
    return None if code in (None, "0") else code


def _definite_reject_code(exc: BaseException) -> Optional[str]:
    """Native code when OKX definitely refused the request, else ``None``.

    Only a translated venue reply whose code the provider classification
    (:mod:`bt_api_okx.error_classification`) marks as a definite rejection
    qualifies.  HTTP 5xx, timeouts, transport errors and unclassified codes
    leave the outcome unknown.
    """

    from bt_api_base.error import ServerError, UnifiedError

    from bt_api_okx.error_classification import classify_error

    if isinstance(exc, ServerError) or not isinstance(exc, UnifiedError):
        return None
    code = _native_error_code(exc)
    if code is None:
        return None
    _category, _environment, definite = classify_error(code)
    return code if definite is True else None


@dataclass
class _Reserved:
    reservation: DirectOrderReservation
    path: str
    params: dict[str, Any]
    extra_data: dict[str, Any]
    reduce_only: Optional[bool]


@dataclass
class _Watch:
    identity: NativeOrderIdentity
    inst_id: str
    client_order_id: Optional[str]
    ord_id: Optional[str]
    reduce_only: Optional[bool]
    fills_since_ms: Optional[int]
    origin: str
    next_due: float = 0.0
    last_key: Optional[tuple[Any, ...]] = None
    trade_ids: set[str] = field(default_factory=set)
    trade_qty: Decimal = Decimal(0)
    not_found: int = 0
    terminal_since: Optional[float] = None
    terminal_state: Optional[str] = None
    terminal_filled: Optional[Decimal] = None
    created_ms: Optional[int] = None
    fill_attempts: int = 0


class OkxDirectWriteProvider:
    """Direct write port for one ``OKX___SWAP`` route (one ``OkxRequestDataSwap``)."""

    def __init__(
        self,
        feed: Any,
        *,
        poll_interval: float = 1.0,
        max_queries_per_drain: int = 4,
        drain_time_budget: float = 2.0,
        query_timeout: float = 3.0,
        submit_timeout: float = 10.0,
        settlement_currency: str = "USDT",
        clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], float] = time.time,
        time_ns: Callable[[], int] = time.time_ns,
    ) -> None:
        from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap

        if (
            type(feed) is not OkxRequestDataSwap
            or getattr(feed, "exchange_name", None) != EXCHANGE_NAME
            or getattr(feed, "asset_type", None) != "SWAP"
        ):
            raise DirectWriteError("okx_direct_write_feed_invalid")
        for value in (poll_interval, drain_time_budget, query_timeout, submit_timeout):
            if type(value) not in (int, float) or not 0 < value <= 60:
                raise DirectWriteError("okx_direct_write_config_invalid")
        if type(max_queries_per_drain) is not int or not 1 <= max_queries_per_drain <= 64:
            raise DirectWriteError("okx_direct_write_config_invalid")
        if type(settlement_currency) is not str or not re.fullmatch(
            r"[A-Z0-9]{1,16}", settlement_currency
        ):
            raise DirectWriteError("okx_direct_write_config_invalid")
        self._feed = feed
        self._poll_interval = float(poll_interval)
        self._max_queries = max_queries_per_drain
        self._drain_budget = float(drain_time_budget)
        self._query_timeout = float(query_timeout)
        self._submit_timeout = float(submit_timeout)
        self._settlement_currency = settlement_currency
        self._clock = clock
        self._wall_clock = wall_clock
        self._lock = threading.RLock()
        self._events_lock = threading.Lock()
        self._events: deque[DirectExecutionEvent] = deque()
        self._sequence = 0
        self._dropped_events = 0
        self._reservations: dict[str, _Reserved] = {}
        self._watches: list[_Watch] = []
        self._counters: dict[str, int] = {}
        self._time_ns = time_ns
        self._time_lock = threading.Lock()
        self._server_time: Optional[tuple[float, dict[str, int]]] = None
        self._server_time_failed_at: Optional[float] = None

    # ------------------------------------------------------------------
    # session
    # ------------------------------------------------------------------
    def _environment(self) -> Optional[str]:
        from bt_api_okx.account_read_state import route_is_current

        try:
            proof = self._feed.get_environment_info()
        except Exception:
            return None
        if type(proof) is not dict:
            return None
        environment = proof.get("environment")
        if environment not in ("demo", "production"):
            return None
        return environment if route_is_current(EXCHANGE_NAME, self._feed, environment) else None

    def _credentials_present(self) -> bool:
        binding = getattr(self._feed, "_credential_binding", None)
        values = (
            getattr(binding, "api_key", None),
            getattr(binding, "api_secret", None),
            getattr(binding, "passphrase", None),
        )
        return all(isinstance(value, str) and value.strip() for value in values)

    def session_generation(self) -> Optional[int]:
        """``1`` while the signed REST route is usable, else ``None``.

        OKX REST is stateless and the feed's credentials are fixed at
        construction, so one route has one session generation.
        """

        if not self._credentials_present() or self._environment() is None:
            return None
        return _SESSION_GENERATION

    def trading_day(self) -> Optional[str]:
        """UTC calendar date ``YYYYMMDD`` (OKX SWAP trades continuously)."""

        return _utc_day(self._wall_clock())

    def settlement_status(self) -> SettlementStatus:
        """OKX has no settlement-statement confirmation step."""

        return SettlementStatus.CONFIRMED

    def confirm_settlement(
        self, grant: WriteGrant, verifier: WriteGrantVerifier
    ) -> SettlementStatus:
        del grant, verifier  # never sends: there is nothing to confirm
        return SettlementStatus.CONFIRMED

    # ------------------------------------------------------------------
    # venue clock (public REST server time)
    # ------------------------------------------------------------------
    def server_time_observation(self) -> Optional[dict[str, int]]:
        """One venue server-time observation for SDK clock cross-checks.

        ``{"venue_epoch_ms", "local_sent_ns", "local_received_ns",
        "granularity_ms"}`` from the public ``GET /api/v5/public/time`` through
        the feed's configured host (demo requests keep the simulated-trading
        header).  ``local_*`` are wall-clock ``time.time_ns()`` taken
        immediately before the request and right after the reply.  A success
        is cached for 60 s; any failure returns ``None`` (retried after 5 s).
        """

        now = self._clock()
        with self._time_lock:
            cached = self._server_time
            if cached is not None and 0 <= now - cached[0] < _SERVER_TIME_TTL:
                return dict(cached[1])
            failed = self._server_time_failed_at
            if failed is not None and 0 <= now - failed < _SERVER_TIME_RETRY:
                return None
            try:
                observation = self._read_server_time()
            except Exception:
                observation = None
            if observation is None:
                self._server_time_failed_at = now
                return None
            self._server_time = (now, observation)
            self._server_time_failed_at = None
            return dict(observation)

    def _read_server_time(self) -> Optional[dict[str, int]]:
        if self._environment() is None:
            return None
        path, params, extra_data = self._feed._get_system_time()
        if path != _SERVER_TIME_PATH or params:
            return None
        sent_ns = self._time_ns()
        result = self._feed.request(
            path, params=params, extra_data=extra_data, timeout=self._query_timeout, max_retries=1
        )
        received_ns = self._time_ns()
        rows = _rows(result)
        venue_ms = _ms(rows[0].get("ts")) if len(rows) == 1 else None
        if (
            venue_ms is None
            or not 10**12 <= venue_ms < 10**14
            or type(sent_ns) is not int
            or type(received_ns) is not int
            or received_ns < sent_ns
        ):
            return None
        return {
            "venue_epoch_ms": venue_ms,
            "local_sent_ns": sent_ns,
            "local_received_ns": received_ns,
            "granularity_ms": 1,
        }

    # ------------------------------------------------------------------
    # request validation and mapping (no network)
    # ------------------------------------------------------------------
    def _build_order(
        self, request: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any], Optional[bool]]:
        from bt_api_okx.order_quantity_units import validate_order_quantity_units
        from bt_api_okx.order_request_mapping import map_order_request

        client_order_id = getattr(request, "client_order_id", None)
        if type(client_order_id) is not str or not _CLIENT_ORDER_ID.fullmatch(client_order_id):
            raise DirectWriteError(
                "okx_direct_client_order_id_invalid", "clOrdId must be 1-32 ASCII letters/digits"
            )
        try:
            validate_order_quantity_units(EXCHANGE_NAME, request)
            if getattr(request, "quantity_unit", None) not in ("contracts", "native"):
                raise ValueError("OKX SWAP sz is a contract count; quantity_unit must be contracts")
            mapped = map_order_request(request)
            symbol = mapped["symbol"]
            if type(symbol) is not str or self._feed._params.get_symbol(symbol) != symbol:
                raise ValueError("symbol must be the native OKX instId (for example BTC-USDT-SWAP)")
            positional = (
                "symbol",
                "vol",
                "price",
                "order_type",
                "offset",
                "post_only",
                "client_order_id",
            )
            options = {key: value for key, value in mapped.items() if key not in positional}
            path, params, extra_data = self._feed._make_order(
                symbol,
                mapped["vol"],
                mapped["price"],
                mapped["order_type"],
                mapped["offset"],
                mapped["post_only"],
                mapped["client_order_id"],
                None,
                **options,
            )
        except DirectWriteError:
            raise
        except Exception as exc:
            raise DirectWriteError("okx_direct_request_unrepresentable", _detail(exc)) from None
        if (
            params.get("clOrdId") != client_order_id
            or params.get("instId") != symbol
            or params.get("sz") != mapped["vol"]
            or params.get("ordType") not in _ORDER_TYPES
            or (params.get("ordType") != "market" and not params.get("px"))
            or any(value is None for value in params.values())
        ):
            raise DirectWriteError("okx_direct_request_unrepresentable", "native_params_invalid")
        return path, params, extra_data, _reduce_only(params.get("reduceOnly"))

    # ------------------------------------------------------------------
    # orders
    # ------------------------------------------------------------------
    def reserve_order(self, request: Any) -> DirectOrderReservation:
        # Unrepresentable requests fail here, before any identity or host marker.
        path, params, extra_data, reduce_only = self._build_order(request)
        with self._lock:
            generation = self.session_generation()
            if generation is None:
                raise DirectWriteError("okx_direct_session_unavailable")
            client_order_id = params["clOrdId"]
            if any(
                held.reservation.identity.client_order_id == client_order_id
                for held in self._reservations.values()
            ) or self._find_watch(client_order_id, None) is not None:
                raise DirectWriteError("okx_direct_client_order_id_in_use")
            identity = NativeOrderIdentity(
                exchange_name=EXCHANGE_NAME,
                client_order_id=client_order_id,
                fields={"inst_id": params["instId"], "trading_day": self.trading_day()},
                session_generation=generation,
            )
            reservation = DirectOrderReservation(
                identity=identity, symbol=params["instId"], reservation_id=uuid4().hex
            )
            self._reservations[reservation.reservation_id] = _Reserved(
                reservation, path, params, extra_data, reduce_only
            )
            return reservation

    def release_reservation(self, reservation: DirectOrderReservation) -> None:
        with self._lock:
            self._reservations.pop(reservation.reservation_id, None)

    def submit_order(
        self,
        reservation: DirectOrderReservation,
        request: Any,
        grant: WriteGrant,
        verifier: WriteGrantVerifier,
    ) -> DirectSubmitResult:
        with self._lock:
            held = self._reservations.pop(reservation.reservation_id, None)
            if held is None or held.reservation != reservation:
                raise DirectWriteError("okx_direct_reservation_unknown")
            path, params, extra_data, reduce_only = self._build_order(request)
            if path != held.path or params != held.params:
                raise DirectWriteError("okx_direct_reservation_request_mismatch")
            generation = self.session_generation()
            if generation is None or generation != reservation.identity.session_generation:
                raise DirectWriteError("okx_direct_reservation_session_changed")
            verifier.consume(
                grant,
                exchange_name=EXCHANGE_NAME,
                operation=WriteOperation.PLACE,
                session_generation=generation,
            )
            watch = self._add_watch(
                reservation.identity,
                inst_id=params["instId"],
                ord_id=None,
                reduce_only=reduce_only,
                fills_since_ms=None,
                origin="placed",
            )
            try:
                result = self._feed.request(
                    path, body=params, extra_data=extra_data, timeout=self._submit_timeout
                )
            except Exception as exc:
                code = _definite_reject_code(exc)
                if code is not None:
                    self._drop_watch(watch)
                    return DirectSubmitResult(
                        sent=False,
                        identity=reservation.identity,
                        error_code="okx_order_rejected",
                        detail=code,
                    )
                watch.next_due = 0.0
                raise OkxDirectOutcomeUnknown(
                    "okx_direct_submit_outcome_unknown", type(exc).__name__
                ) from None
            ord_id = self._ack_ord_id(result, params["clOrdId"])
            if ord_id is None:
                watch.next_due = 0.0
                raise OkxDirectOutcomeUnknown(
                    "okx_direct_submit_outcome_unknown", "acknowledgement_invalid"
                )
            watch.ord_id = ord_id
            watch.next_due = 0.0
            fields = dict(reservation.identity.fields)
            fields["ord_id"] = ord_id
            identity = NativeOrderIdentity(
                exchange_name=EXCHANGE_NAME,
                client_order_id=reservation.identity.client_order_id,
                fields=fields,
                session_generation=reservation.identity.session_generation,
            )
            watch.identity = identity
            return DirectSubmitResult(sent=True, identity=identity)

    @staticmethod
    def _ack_ord_id(result: Any, client_order_id: Optional[str]) -> Optional[str]:
        try:
            rows = _rows(result)
        except ValueError:
            return None
        if len(rows) != 1:
            return None
        row = rows[0]
        ord_id = _text(row.get("ordId"))
        if (
            _text(row.get("sCode")) != "0"
            or ord_id is None
            or not _VENUE_ID.fullmatch(ord_id)
            or (client_order_id is not None and _text(row.get("clOrdId")) != client_order_id)
        ):
            return None
        return ord_id

    def cancel_order(
        self,
        target: NativeOrderIdentity,
        symbol: str,
        grant: WriteGrant,
        verifier: WriteGrantVerifier,
    ) -> DirectSubmitResult:
        with self._lock:
            if type(target) is not NativeOrderIdentity or target.exchange_name != EXCHANGE_NAME:
                raise DirectWriteError("okx_direct_cancel_identity_foreign")
            fields = target.fields
            inst_id = _text(fields.get("inst_id")) or _text(symbol)
            if (
                inst_id is None
                or inst_id != symbol
                or self._feed._params.get_symbol(inst_id) != inst_id
            ):
                raise DirectWriteError("okx_direct_cancel_symbol_mismatch")
            ord_id = _text(fields.get("ord_id"))
            client_order_id = target.client_order_id
            if ord_id is not None and not _VENUE_ID.fullmatch(ord_id):
                raise DirectWriteError("okx_direct_cancel_identity_incomplete")
            if client_order_id is not None and not _CLIENT_ORDER_ID.fullmatch(client_order_id):
                raise DirectWriteError("okx_direct_cancel_identity_incomplete")
            if ord_id is None and client_order_id is None:
                raise DirectWriteError("okx_direct_cancel_identity_incomplete")
            generation = self.session_generation()
            if generation is None:
                raise DirectWriteError("okx_direct_session_unavailable")
            # One identity only: the venue order id when known, else clOrdId.
            if ord_id is not None:
                path, params, extra_data = self._feed._cancel_order(inst_id, ord_id)
            else:
                path, params, extra_data = self._feed._cancel_order(
                    inst_id, None, client_order_id=client_order_id
                )
            verifier.consume(
                grant,
                exchange_name=EXCHANGE_NAME,
                operation=WriteOperation.CANCEL,
                session_generation=generation,
            )
            watch = self._find_watch(client_order_id, ord_id)
            if watch is None:
                watch = self._add_watch(
                    target,
                    inst_id=inst_id,
                    ord_id=ord_id,
                    reduce_only=None,
                    fills_since_ms=_utc_day_start_ms(self._wall_clock()),
                    origin="cancel_target",
                )
            try:
                result = self._feed.request(
                    path, body=params, extra_data=extra_data, timeout=self._submit_timeout
                )
            except Exception as exc:
                code = _definite_reject_code(exc)
                if code is not None:
                    return DirectSubmitResult(
                        sent=False, identity=target, error_code="okx_cancel_rejected", detail=code
                    )
                watch.next_due = 0.0
                raise OkxDirectOutcomeUnknown(
                    "okx_direct_cancel_outcome_unknown", type(exc).__name__
                ) from None
            watch.next_due = 0.0
            if self._ack_ord_id(result, None) is None:
                raise OkxDirectOutcomeUnknown(
                    "okx_direct_cancel_outcome_unknown", "acknowledgement_invalid"
                )
            return DirectSubmitResult(sent=True, identity=target)

    # ------------------------------------------------------------------
    # watched orders (returns by bounded polling)
    # ------------------------------------------------------------------
    def _find_watch(self, client_order_id: Optional[str], ord_id: Optional[str]) -> Optional[_Watch]:
        for watch in self._watches:
            if client_order_id is not None and watch.client_order_id == client_order_id:
                return watch
            if ord_id is not None and watch.ord_id == ord_id:
                return watch
        return None

    def _add_watch(
        self,
        identity: NativeOrderIdentity,
        *,
        inst_id: str,
        ord_id: Optional[str],
        reduce_only: Optional[bool],
        fills_since_ms: Optional[int],
        origin: str,
    ) -> _Watch:
        watch = _Watch(
            identity=identity,
            inst_id=inst_id,
            client_order_id=identity.client_order_id,
            ord_id=ord_id,
            reduce_only=reduce_only,
            fills_since_ms=fills_since_ms,
            origin=origin,
        )
        self._watches.append(watch)
        return watch

    def _drop_watch(self, watch: _Watch) -> None:
        try:
            self._watches.remove(watch)
        except ValueError:
            pass

    def watch_order(self, identity: NativeOrderIdentity, symbol: str) -> None:
        """Watch an order this provider did not place (restored host marker).

        Only fills from the current UTC day are returned for such an order, the
        same horizon as a trading-day replay.
        """

        if type(identity) is not NativeOrderIdentity or identity.exchange_name != EXCHANGE_NAME:
            raise DirectWriteError("okx_direct_watch_identity_invalid")
        inst_id = _text(identity.fields.get("inst_id")) or _text(symbol)
        ord_id = _text(identity.fields.get("ord_id"))
        if inst_id is None or (identity.client_order_id is None and ord_id is None):
            raise DirectWriteError("okx_direct_watch_identity_invalid")
        with self._lock:
            if self._find_watch(identity.client_order_id, ord_id) is None:
                self._add_watch(
                    identity,
                    inst_id=inst_id,
                    ord_id=ord_id,
                    reduce_only=None,
                    fills_since_ms=_utc_day_start_ms(self._wall_clock()),
                    origin="restored",
                )

    @property
    def watched_count(self) -> int:
        with self._lock:
            return len(self._watches)

    @property
    def counters(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)

    @property
    def dropped_events(self) -> int:
        return self._dropped_events

    def _bump(self, name: str) -> None:
        self._counters[name] = self._counters.get(name, 0) + 1

    def _enqueue(self, events: Iterable[DirectExecutionEvent]) -> None:
        with self._events_lock:
            for event in events:
                if len(self._events) >= _MAX_EVENTS:
                    self._events.popleft()
                    self._dropped_events += 1
                self._events.append(event)

    def _next_sequence(self) -> int:
        with self._events_lock:
            self._sequence += 1
            return self._sequence

    def drain_execution_events(self, max_events: int) -> tuple[DirectExecutionEvent, ...]:
        """Return queued returns; poll due watched orders when the queue is short.

        Polling performs bounded signed ``GET`` reads: at most
        ``max_queries_per_drain`` orders, each at most once per
        ``poll_interval``, within ``drain_time_budget`` seconds.
        """

        limit = max(1, int(max_events))
        with self._events_lock:
            short = len(self._events) < limit
        if short:
            with self._lock:
                self._poll_due()
        out: list[DirectExecutionEvent] = []
        with self._events_lock:
            while self._events and len(out) < limit:
                out.append(self._events.popleft())
        return tuple(out)

    def _poll_due(self) -> None:
        start = self._clock()
        due = [watch for watch in self._watches if watch.next_due <= start]
        due.sort(key=lambda watch: watch.next_due)
        for watch in due[: self._max_queries]:
            remaining = self._drain_budget - (self._clock() - start)
            if remaining <= 0:
                break
            self._poll_watch(watch, min(self._query_timeout, remaining))

    def _query_order_row(self, watch: _Watch, timeout: float) -> dict[str, Any]:
        if watch.ord_id is not None:
            path, params, extra_data = self._feed._query_order(watch.inst_id, watch.ord_id)
        else:
            path, params, extra_data = self._feed._query_order(
                watch.inst_id, None, client_order_id=watch.client_order_id
            )
        try:
            result = self._feed.request(
                path, params=params, extra_data=extra_data, timeout=timeout, max_retries=1
            )
        except Exception as exc:
            if _native_error_code(exc) == _ORDER_NOT_FOUND_CODE:
                raise _OrderNotFound() from None
            raise
        rows = _rows(result)
        if len(rows) != 1:
            raise ValueError("okx_order_query_rows_invalid")
        return rows[0]

    def _fail(self, name: str, exc: BaseException) -> None:
        """Count a failed read with a finite reason (native code or error class)."""

        self._bump(name)
        reason = _native_error_code(exc) or type(exc).__name__
        self._bump(f"{name}:{reason[:64]}")

    def _poll_watch(self, watch: _Watch, timeout: float) -> None:
        now = self._clock()
        watch.next_due = now + self._poll_interval
        first = False
        order_event: Optional[DirectExecutionEvent] = None
        if watch.terminal_state is not None:
            # Terminal status never changes: only the fills are still owed.
            state, filled = watch.terminal_state, watch.terminal_filled
        else:
            try:
                row = self._query_order_row(watch, timeout)
            except _OrderNotFound:
                # Not (yet) known to OKX: keep watching with backoff; an unknown
                # send outcome is never turned into a rejection here.
                watch.not_found += 1
                backoff = self._poll_interval * (2 ** min(watch.not_found, 5))
                watch.next_due = now + min(backoff, _MAX_NOT_FOUND_BACKOFF)
                self._bump("order_not_found")
                return
            except Exception as exc:
                self._fail("order_query_failed", exc)
                return
            client_order_id = _text(row.get("clOrdId"))
            ord_id = _text(row.get("ordId"))
            if (
                ord_id is None
                or not _VENUE_ID.fullmatch(ord_id)
                or _text(row.get("instId")) != watch.inst_id
                or (watch.client_order_id is not None and client_order_id != watch.client_order_id)
                or (watch.ord_id is not None and ord_id != watch.ord_id)
            ):
                self._bump("order_identity_mismatch")
                return
            if watch.ord_id is None:
                watch.ord_id = ord_id
                fields = dict(watch.identity.fields)
                fields["ord_id"] = ord_id
                watch.identity = NativeOrderIdentity(
                    exchange_name=EXCHANGE_NAME,
                    client_order_id=watch.identity.client_order_id,
                    fields=fields,
                    session_generation=watch.identity.session_generation,
                )
            watch.not_found = 0
            created = _ms(row.get("cTime"))
            if created is not None:
                watch.created_ms = created
            reduce_only = _reduce_only(row.get("reduceOnly"))
            if reduce_only is not None:
                watch.reduce_only = reduce_only
            state = _text(row.get("state"))
            filled = _decimal(row.get("accFillSz"))
            first = watch.last_key is None
            key = (state, filled)
            if key != watch.last_key:
                order_event = self._order_event(row, watch.identity, watch.reduce_only)
                watch.last_key = key
            if state in _TERMINAL_STATES:
                watch.terminal_state, watch.terminal_filled = state, filled
                watch.terminal_since = now
        trades: list[DirectExecutionEvent] = []
        # Fills follow ANY filled quantity not yet covered by emitted trades,
        # including an order already filled at its first observation.
        if filled is not None and filled > watch.trade_qty:
            try:
                trades = self._new_fills(watch, timeout)
            except Exception as exc:
                self._fail("fills_query_failed", exc)
        events: list[DirectExecutionEvent] = []
        if order_event is not None and first:
            events.append(order_event)
        events.extend(trades)
        if order_event is not None and not first:
            events.append(order_event)
        self._enqueue(events)
        if watch.terminal_state is None:
            return
        if filled is None or watch.trade_qty >= filled:
            self._drop_watch(watch)
            return
        # Terminal with fills still owed: keep polling the fills (they lag the
        # order status).  Only an order older than the venue fill window, whose
        # fills can no longer be read, is released after a grace period.
        watch.fill_attempts += 1
        now_ms = int(self._wall_clock() * 1000)
        outside = watch.created_ms is not None and now_ms - watch.created_ms > _FILLS_WINDOW_MS
        if outside and now - (watch.terminal_since or now) >= _TERMINAL_FILL_GRACE:
            self._bump("fills_incomplete_outside_window")
            self._drop_watch(watch)
            return
        if watch.fill_attempts > _FILL_RETRY_FAST:
            backoff = self._poll_interval * (2 ** min(watch.fill_attempts - _FILL_RETRY_FAST, 5))
            watch.next_due = now + min(backoff, _MAX_FILL_BACKOFF)

    def _new_fills(self, watch: _Watch, timeout: float) -> list[DirectExecutionEvent]:
        rows: list[dict[str, Any]] = []
        after: Optional[str] = None
        for _page in range(_MAX_FILL_PAGES):
            path, params, extra_data = self._feed._get_fills(
                inst_type="SWAP",
                inst_id=watch.inst_id,
                order_id=watch.ord_id,
                after=after,
                limit=str(_PAGE_LIMIT),
            )
            page = _rows(
                self._feed.request(
                    path, params=params, extra_data=extra_data, timeout=timeout, max_retries=1
                )
            )
            rows.extend(page)
            if len(page) < _PAGE_LIMIT:
                break
            after = _text(page[-1].get("billId"))
            if after is None:
                raise ValueError("okx_fill_page_cursor_invalid")
        else:
            raise ValueError("okx_fill_pages_exceeded")
        fresh: list[tuple[int, str, dict[str, Any], Decimal]] = []
        for row in rows:
            trade_id = _text(row.get("tradeId"))
            quantity = _decimal(row.get("fillSz"))
            # The request is scoped by instId and ordId: a row that omits them
            # is attributed by the request, one that states others never is.
            if (
                row.get("ordId") not in (None, "", watch.ord_id)
                or row.get("instId") not in (None, "", watch.inst_id)
                or trade_id is None
                or quantity is None
                or quantity <= 0
            ):
                continue
            if trade_id in watch.trade_ids:
                continue
            scoped = dict(row)
            scoped["ordId"] = watch.ord_id
            scoped["instId"] = watch.inst_id
            fresh.append((_ms(row.get("ts")) or 0, trade_id, scoped, quantity))
        fresh.sort(key=lambda item: (item[0], item[1]))
        events = []
        for timestamp, trade_id, row, quantity in fresh:
            watch.trade_ids.add(trade_id)
            watch.trade_qty += quantity
            if watch.fills_since_ms is not None and timestamp < watch.fills_since_ms:
                continue  # before this watch's horizon: counted, not replayed
            events.append(self._trade_event(row, watch.identity, watch.reduce_only))
        return events

    # ------------------------------------------------------------------
    # projection
    # ------------------------------------------------------------------
    def _order_event(
        self, row: Mapping[str, Any], identity: NativeOrderIdentity, reduce_only: Optional[bool]
    ) -> DirectExecutionEvent:
        state = _text(row.get("state"))
        side = _text(row.get("side"))
        size = _decimal(row.get("sz"))
        filled = _decimal(row.get("accFillSz"))
        return DirectExecutionEvent(
            kind=DirectExecutionEventKind.ORDER,
            exchange_name=EXCHANGE_NAME,
            symbol=_text(row.get("instId")) or "",
            identity=identity,
            exchange_order_id=_text(row.get("ordId")),
            status=_STATUS.get(state or "", DirectOrderStatus.UNKNOWN),
            side=side if side in ("buy", "sell") else None,
            offset=_offset(_text(row.get("posSide")), side, reduce_only),
            order_qty=None if size is None else float(size),
            filled_qty=None if filled is None else float(filled),
            remaining_qty=(
                None if size is None or filled is None else float(max(size - filled, Decimal(0)))
            ),
            limit_price=_float(row.get("px")),
            trading_day=identity.fields.get("trading_day"),
            raw_status=state,
            session_generation=identity.session_generation,
            sequence=self._next_sequence(),
        )

    def _trade_event(
        self, row: Mapping[str, Any], identity: NativeOrderIdentity, reduce_only: Optional[bool]
    ) -> DirectExecutionEvent:
        side = _text(row.get("side"))
        return DirectExecutionEvent(
            kind=DirectExecutionEventKind.TRADE,
            exchange_name=EXCHANGE_NAME,
            symbol=_text(row.get("instId")) or "",
            identity=identity,
            exchange_order_id=_text(row.get("ordId")),
            side=side if side in ("buy", "sell") else None,
            offset=_offset(_text(row.get("posSide")), side, reduce_only),
            trade_id=_text(row.get("tradeId")),
            trade_price=_float(row.get("fillPx")),
            trade_qty=_float(row.get("fillSz")),
            trade_time=_iso_from_ms(row.get("ts")),
            trading_day=_day_from_ms(row.get("ts")),
            session_generation=identity.session_generation,
            sequence=self._next_sequence(),
        )

    def _row_identity(
        self, row: Mapping[str, Any], client_order_id: Optional[str], day: Optional[str]
    ) -> NativeOrderIdentity:
        if client_order_id is not None and not _CLIENT_ORDER_ID.fullmatch(client_order_id):
            client_order_id = None
        ord_id = _text(row.get("ordId"))
        watch = self._find_watch(client_order_id, ord_id)
        if watch is not None and watch.ord_id in (None, ord_id):
            fields = dict(watch.identity.fields)
            if ord_id is not None:
                fields["ord_id"] = ord_id
            return NativeOrderIdentity(
                exchange_name=EXCHANGE_NAME,
                client_order_id=watch.identity.client_order_id,
                fields=fields,
                session_generation=watch.identity.session_generation,
            )
        fields: dict[str, Any] = {"inst_id": _text(row.get("instId"))}
        if day is not None:
            fields["trading_day"] = day
        if ord_id is not None:
            fields["ord_id"] = ord_id
        return NativeOrderIdentity(
            exchange_name=EXCHANGE_NAME,
            client_order_id=client_order_id,
            fields=fields,
            session_generation=_SESSION_GENERATION,
        )

    # ------------------------------------------------------------------
    # read-only account facts (D62-05/13/16/22)
    # ------------------------------------------------------------------
    def _paged_rows(
        self,
        build: Callable[[Optional[str]], tuple[str, dict[str, Any], dict[str, Any]]],
        cursor_field: str,
        timeout: float,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        after: Optional[str] = None
        for _page in range(_MAX_PAGES):
            path, params, extra_data = build(after)
            params = {key: value for key, value in params.items() if value not in (None, "")}
            page = _rows(
                self._feed.request(
                    path, params=params, extra_data=extra_data, timeout=timeout, max_retries=1
                )
            )
            rows.extend(page)
            if len(page) < _PAGE_LIMIT:
                return rows
            after = _text(page[-1].get(cursor_field))
            if after is None:
                raise ValueError("okx_page_cursor_invalid")
        raise ValueError("okx_page_limit_exceeded")

    def account_facts(
        self,
        *,
        positions: bool = True,
        active_orders: bool = True,
        trades: bool = False,
        balance: bool = True,
        all_orders: bool = False,
        timeout: float = 5.0,
        symbols: Optional[Iterable[str]] = None,
    ) -> DirectAccountFacts:
        """One read-only observation of the SWAP account (never raises for reads).

        ``orders`` (``all_orders``) is every SWAP order pending now plus every
        order in ``orders-history`` created since 00:00 UTC.  OKX keeps
        cancelled orders that never filled in that history for about two hours
        only; such an order is absent afterwards.  ``symbols`` is accepted for
        signature parity and ignored (OKX reads are account-wide).
        """

        del symbols
        from bt_api_okx.account_read_state import (
            account_read_state_for_route,
            read_full_account_balance,
            read_full_swap_positions,
        )

        bounded = float(timeout) if type(timeout) in (int, float) and timeout > 0 else 5.0
        bounded = min(bounded, _MAX_FACTS_TIMEOUT)
        now = self._wall_clock()
        day = _utc_day(now)
        day_start_ms = _utc_day_start_ms(now)
        observed = (
            datetime.fromtimestamp(now, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
        blockers: list[str] = []
        generation = self.session_generation()
        environment = self._environment()
        state = (
            None
            if generation is None or environment is None
            else account_read_state_for_route(EXCHANGE_NAME, self._feed, environment)
        )
        if state is None:
            return DirectAccountFacts(
                exchange_name=EXCHANGE_NAME,
                trading_day=day,
                session_generation=None,
                observed_at_utc=observed,
                positions=None,
                active_orders=None,
                trades=None,
                balance=None,
                complete=False,
                blockers=("session_unavailable",),
                orders=None,
            )

        with self._lock:
            position_facts: Optional[tuple[DirectPositionFact, ...]] = None
            if positions:
                result = read_full_swap_positions(self._feed, state, timeout_seconds=bounded)
                try:
                    if result is None:
                        raise ValueError("positions_read_failed")
                    position_facts = self._position_facts(_rows(result))
                except Exception:
                    blockers.append("positions_query_incomplete")

            working: Optional[list[dict[str, Any]]] = None
            if active_orders or all_orders:
                try:
                    working = self._paged_rows(
                        lambda after: self._feed._get_open_orders(
                            None, instType="SWAP", limit=str(_PAGE_LIMIT), after=after or ""
                        ),
                        "ordId",
                        bounded,
                    )
                except Exception:
                    blockers.append("orders_query_incomplete")
            order_index: dict[str, tuple[Optional[str], Optional[str], Optional[bool]]] = {}

            def _index(rows: Iterable[dict[str, Any]]) -> None:
                for row in rows:
                    ord_id = _text(row.get("ordId"))
                    if ord_id is not None:
                        order_index[ord_id] = (
                            _text(row.get("clOrdId")),
                            _day_from_ms(row.get("cTime")),
                            _reduce_only(row.get("reduceOnly")),
                        )

            order_facts: Optional[tuple[DirectExecutionEvent, ...]] = None
            if active_orders and working is not None:
                try:
                    order_facts = tuple(self._account_order_events(working, watch_working=True))
                except Exception:
                    blockers.append("orders_projection_invalid")
            _index(working or ())
            every_order: Optional[tuple[DirectExecutionEvent, ...]] = None
            if all_orders and working is not None:
                try:
                    history = self._paged_rows(
                        lambda after: self._history_request(day_start_ms, after),
                        "ordId",
                        bounded,
                    )
                    merged: dict[str, dict[str, Any]] = {}
                    for row in list(history) + list(working):
                        ord_id = _text(row.get("ordId"))
                        if ord_id is not None:
                            merged[ord_id] = row  # the pending row is the newer view
                    _index(merged.values())
                    every_order = tuple(
                        self._account_order_events(merged.values(), watch_working=False)
                    )
                except Exception:
                    blockers.append("orders_history_query_incomplete")

            trade_facts: Optional[tuple[DirectExecutionEvent, ...]] = None
            if trades:
                try:
                    fills = self._paged_rows(
                        lambda after: self._fills_request(day_start_ms, after),
                        "billId",
                        bounded,
                    )
                    trade_facts = tuple(self._account_trade_events(fills, order_index))
                except Exception:
                    blockers.append("trades_query_incomplete")

            balance_fact: Optional[DirectBalanceFact] = None
            if balance:
                result = read_full_account_balance(self._feed, state, timeout_seconds=bounded)
                try:
                    if result is None:
                        raise ValueError("balance_read_failed")
                    balance_fact = self._balance_fact(_rows(result))
                    if balance_fact is None:
                        blockers.append("balance_currency_absent")
                except Exception:
                    blockers.append("account_query_incomplete")

        return DirectAccountFacts(
            exchange_name=EXCHANGE_NAME,
            trading_day=day,
            session_generation=generation,
            observed_at_utc=observed,
            positions=position_facts,
            active_orders=order_facts,
            trades=trade_facts,
            balance=balance_fact,
            complete=not blockers,
            blockers=tuple(blockers),
            orders=every_order,
        )

    def _history_request(
        self, day_start_ms: int, after: Optional[str]
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        path, params, extra_data = self._feed._get_order_history(
            inst_type="SWAP", after=after, limit=str(_PAGE_LIMIT)
        )
        params = dict(params)
        params["begin"] = str(day_start_ms)
        return path, params, extra_data

    def _fills_request(
        self, day_start_ms: int, after: Optional[str]
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        path, params, extra_data = self._feed._get_fills(
            inst_type="SWAP", after=after, limit=str(_PAGE_LIMIT)
        )
        params = dict(params)
        params["begin"] = str(day_start_ms)
        return path, params, extra_data

    @staticmethod
    def _position_facts(rows: list[dict[str, Any]]) -> tuple[DirectPositionFact, ...]:
        totals: dict[tuple[str, str], Decimal] = {}
        for row in rows:
            inst_id = _text(row.get("instId"))
            pos_side = _text(row.get("posSide"))
            quantity = _decimal(row.get("pos"))
            if inst_id is None or quantity is None:
                raise ValueError("okx_position_row_invalid")
            if _text(row.get("instType")) not in (None, "SWAP"):
                raise ValueError("okx_position_scope_invalid")
            if quantity == 0:
                continue
            if pos_side in ("long", "short"):
                key = (inst_id, pos_side)
                totals[key] = totals.get(key, Decimal(0)) + abs(quantity)
            elif pos_side == "net":
                key = (inst_id, "net")
                totals[key] = totals.get(key, Decimal(0)) + quantity  # signed: + long, - short
            else:
                raise ValueError("okx_position_side_invalid")
        return tuple(
            DirectPositionFact(symbol=symbol, venue=None, side=side, total=float(total))
            for (symbol, side), total in sorted(totals.items())
            if total != 0
        )

    def _balance_fact(self, rows: list[dict[str, Any]]) -> Optional[DirectBalanceFact]:
        if len(rows) != 1 or type(rows[0].get("details")) is not list:
            raise ValueError("okx_balance_shape_invalid")
        matches = [
            detail
            for detail in rows[0]["details"]
            if type(detail) is dict and detail.get("ccy") == self._settlement_currency
        ]
        if len(matches) > 1:
            raise ValueError("okx_balance_currency_duplicated")
        if not matches:
            return None
        detail = matches[0]
        available = _float(detail.get("availEq"))
        if available is None:
            available = _float(detail.get("availBal"))
        return DirectBalanceFact(
            currency=self._settlement_currency,
            balance=_float(detail.get("eq")),
            available=available,
            margin=_float(detail.get("imr")),
            frozen=_float(detail.get("frozenBal")),
            position_profit=_float(detail.get("upl")),
        )

    def _account_order_events(
        self, rows: Iterable[dict[str, Any]], *, watch_working: bool
    ) -> list[DirectExecutionEvent]:
        events = []
        auto = sum(1 for watch in self._watches if watch.origin == "account_facts")
        for row in rows:
            inst_id = _text(row.get("instId"))
            ord_id = _text(row.get("ordId"))
            if inst_id is None or ord_id is None or not _VENUE_ID.fullmatch(ord_id):
                raise ValueError("okx_order_row_invalid")
            identity = self._row_identity(
                row, _text(row.get("clOrdId")), _day_from_ms(row.get("cTime"))
            )
            reduce_only = _reduce_only(row.get("reduceOnly"))
            events.append(self._order_event(row, identity, reduce_only))
            if (
                watch_working
                and _text(row.get("state")) not in _TERMINAL_STATES
                and self._find_watch(identity.client_order_id, ord_id) is None
            ):
                if auto >= _MAX_AUTO_WATCHED:
                    self._bump("auto_watch_overflow")
                    continue
                watch = self._add_watch(
                    identity,
                    inst_id=inst_id,
                    ord_id=ord_id,
                    reduce_only=reduce_only,
                    fills_since_ms=_utc_day_start_ms(self._wall_clock()),
                    origin="account_facts",
                )
                watch.last_key = (_text(row.get("state")), _decimal(row.get("accFillSz")))
                watch.created_ms = _ms(row.get("cTime"))
                watch.next_due = self._clock() + self._poll_interval
                auto += 1
        return events

    def _account_trade_events(
        self,
        rows: Iterable[dict[str, Any]],
        orders: Mapping[str, tuple[Optional[str], Optional[str], Optional[bool]]],
    ) -> list[DirectExecutionEvent]:
        """Project fills; ``orders`` maps ordId to (clOrdId, creation day, reduceOnly).

        The order's creation day and reduce-only flag come from an order row
        read in the same observation or from a watched order; otherwise they
        stay unknown.
        """

        events = []
        for row in rows:
            ord_id = _text(row.get("ordId"))
            if _text(row.get("tradeId")) is None or ord_id is None or _text(row.get("instId")) is None:
                raise ValueError("okx_fill_row_invalid")
            known_client, day, reduce_only = orders.get(ord_id, (None, None, None))
            client_order_id = _text(row.get("clOrdId")) or known_client
            watch = self._find_watch(client_order_id, ord_id)
            if watch is not None and watch.reduce_only is not None:
                reduce_only = watch.reduce_only
            identity = self._row_identity(row, client_order_id, day)
            events.append(self._trade_event(row, identity, reduce_only))
        return events

    def account_reference(self) -> Optional[str]:
        """Secret-free account reference: a hash of the environment and API key.

        Never the key itself; the secret and passphrase are not used.
        """

        binding = getattr(self._feed, "_credential_binding", None)
        api_key = getattr(binding, "api_key", None)
        environment = self._environment()
        if not isinstance(api_key, str) or not api_key.strip() or environment is None:
            return None
        material = f"okx-direct-account-reference.v1|{environment}|{api_key}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]

    def close(self) -> None:
        with self._lock:
            self._watches.clear()
            self._reservations.clear()


def create_okx_direct_write_provider(feed: Any) -> OkxDirectWriteProvider:
    """Factory for ``bt_api.direct_write_providers``: wrap the selected OKX SWAP feed."""

    return OkxDirectWriteProvider(feed)


def register_okx_direct_write_provider(registry: Any) -> None:
    """Register the OKX SWAP direct write provider factory."""

    register = getattr(registry, "register", None)
    if not callable(register):
        raise TypeError("registry must expose register(exchange_name, factory)")
    register(OKX_DIRECT_WRITE_EXCHANGE, create_okx_direct_write_provider)
