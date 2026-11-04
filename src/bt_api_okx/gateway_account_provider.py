"""Read-only OKX SWAP Demo provider for the Gateway account-session protocol.

This is the provider object ``bt_api_gateway.GatewayAccountSessionWorker``
drives (``connect`` / ``read_account`` / ``close``); it is unrelated to the
direct-mode ``AccountSessionPort`` in :mod:`bt_api_okx.account_session_provider`.

* **Origin and routes.** Demo trading only: the fixed origin
  ``https://www.okx.com`` with ``x-simulated-trading: 1``. Every request is a
  ``GET`` of a fixed route table (signed with OKX v5 HMAC-SHA256 base64 of
  ``timestamp + method + requestPath + body``); there is no order, cancel,
  transfer or other mutating route. Redirects are never followed and response
  bodies are bounded. Errors are finite, value-free codes; credentials never
  appear in ``repr`` or errors.
* **Account facts.** ``read_account`` requires OKX account mode ``acctLv=2``
  (spot and futures mode, per-currency balances) and returns per-currency
  balances (``eq``/``availBal``/``frozenBal``, the same mapping as the OKX query
  service) under the account resource, and cross-margin SWAP positions and
  regular open orders (contracts) under the ``SWAP``/``cross`` resource.
  Isolated-margin SWAP rows are outside that coverage. Algo orders are not
  read, so ``open_orders_complete`` is ``False``. Average prices are omitted:
  their denomination differs between linear and inverse SWAPs.
* **Execution observations.** With an explicit ``OkxSwapExecutionScope`` the
  provider implements the worker's optional capability
  ``read_execution_observations`` / ``confirm_execution_observations``; see
  :mod:`bt_api_okx.gateway_execution_observations`.

The provider is one-shot: ``close`` drops the credentials and a closed instance
never connects again, so a new generation is a new instance.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import re
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bt_api_base.account_protocol import (
    MAX_ACCOUNT_OBSERVATION_BYTES,
    MAX_ACCOUNT_ROWS,
    AccountBalance,
    AccountKey,
    AccountObservation,
    AccountOpenOrder,
    AccountPosition,
    AccountResourceKey,
)
from bt_api_base.market_protocol import MarketInstrumentKey

from bt_api_okx import gateway_execution_observations as _execution

_HOST = "www.okx.com"
_BASE_URL = "https://" + _HOST
_MAX_TIMEOUT_SECONDS = 30.0
_SERVER_TIME_MAX_AGE_SECONDS = 60.0
_SESSION_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z", re.ASCII)
_DECIMAL = re.compile(r"-?[0-9]{1,40}(?:\.[0-9]{1,40})?\Z", re.ASCII)
_DIGITS = re.compile(r"[0-9]{1,20}\Z", re.ASCII)
_CURRENCY = re.compile(r"[A-Z0-9]{1,16}\Z", re.ASCII)
_ORDER_TYPE = re.compile(r"[a-z][a-z_]{0,31}\Z", re.ASCII)
_PRODUCT_TYPE = "SWAP"
ACCOUNT_RESOURCE = AccountResourceKey(product_type="account", margin_pool="account")
SWAP_CROSS_RESOURCE = _execution.SWAP_CROSS_RESOURCE
_QTY_UNIT = _execution.QTY_UNIT
_PAGE_LIMIT = 100
_MAX_OPEN_ORDER_PAGES = 20
_ROUTES = {
    "server_time": "/api/v5/public/time",
    "account_config": "/api/v5/account/config",
    "balance": "/api/v5/account/balance",
    "positions": "/api/v5/account/positions",
    "orders_pending": "/api/v5/trade/orders-pending",
    "orders_history": "/api/v5/trade/orders-history",
    "fills": "/api/v5/trade/fills",
    "order": "/api/v5/trade/order",
}
_ROUTE_PARAMS = {
    "account_config": frozenset(),
    "balance": frozenset(),
    "positions": frozenset({"instType"}),
    "orders_pending": frozenset({"instType", "instId", "limit", "after"}),
    "orders_history": frozenset({"instType", "instId", "begin", "limit", "after"}),
    "fills": frozenset({"instType", "instId", "begin", "limit", "after"}),
    "order": frozenset({"instId", "ordId"}),
}


class _NoRedirectHandler(HTTPRedirectHandler):
    """Never forward a signed request beyond its fixed origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OkxSwapProviderError(RuntimeError):
    """Finite provider error that never carries HTTP or credential content."""

    _CODES = frozenset(
        {
            "INVALID_CREDENTIALS",
            "INVALID_ACCOUNT_IDENTITY",
            "INVALID_GENERATION",
            "INVALID_TIMEOUT",
            "INVALID_LIMIT",
            "INVALID_EXECUTION_SCOPE",
            "PROVIDER_SESSION_NOT_ACTIVE",
            "PROVIDER_SESSION_CLOSED",
            "PROVIDER_SESSION_ALREADY_CONNECTED",
            "PROVIDER_THREAD_MISMATCH",
            "PROVIDER_GENERATION_MISMATCH",
            "SERVER_TIME_READ_FAILED",
            "SERVER_TIME_INVALID",
            "SERVER_TIME_PROBE_REQUIRED",
            "ACCOUNT_SNAPSHOT_READ_FAILED",
            "ACCOUNT_SNAPSHOT_INVALID",
            "ACCOUNT_COVERAGE_UNSUPPORTED",
            "ACCOUNT_ROWS_EXCEEDED",
            "OPEN_ORDER_SHAPE_UNSUPPORTED",
            "VENUE_ERROR_RESPONSE",
            "REQUEST_TIMEOUT",
            "RESPONSE_TOO_LARGE",
            "TRANSPORT_FAILED",
            "INVALID_JSON_RESPONSE",
            "EXECUTION_OBSERVATIONS_NOT_CONFIGURED",
            "EXECUTION_READ_FAILED",
            "EXECUTION_ROW_INVALID",
            "EXECUTION_LOOKBACK_TRUNCATED",
            "EXECUTION_BACKLOG_EXCEEDED",
            "EXECUTION_TRACKED_ORDERS_EXCEEDED",
            "EXECUTION_IDENTITY_UNAVAILABLE",
            "EXECUTION_CONFIRM_INVALID",
        }
    )

    def __init__(self, code: str) -> None:
        self.code = code if type(code) is str and code in self._CODES else "PROVIDER_FAILED"
        super().__init__(self.code)


def _printable_secret(value: Any) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and len(value) <= 512
        and value.isascii()
        and value.isprintable()
    )


@dataclass(frozen=True)
class OkxSwapApiCredentials:
    """Opaque trusted-owner Demo credential material; repr reveals nothing."""

    api_key: str = field(repr=False)
    api_secret: str = field(repr=False)
    passphrase: str = field(repr=False)

    def __post_init__(self) -> None:
        if not all(
            _printable_secret(getattr(self, name))
            for name in ("api_key", "api_secret", "passphrase")
        ):
            raise OkxSwapProviderError("INVALID_CREDENTIALS")

    def __repr__(self) -> str:
        return "OkxSwapApiCredentials(<redacted>)"


@dataclass(frozen=True)
class OkxSwapExecutionScope:
    """Explicit execution-observation scope of one Gateway provider session.

    ``inst_ids`` are the SWAP instruments (``BTC-USDT-SWAP``) whose orders and
    fills are read; other products are refused at construction. The other
    fields mean the same as for the Binance provider: ``lookback_seconds`` is
    re-read after each ``connect``; ``observation_issuer`` issues the stable
    opaque ids (``issue_order_observation_id``/``issue_trade_observation_id``
    of ``bt_api_base``'s ``ManagedOrderObservationIssuer``; it must be durable);
    ``poll_interval_seconds`` throttles venue queries.
    """

    inst_ids: tuple[str, ...]
    lookback_seconds: int
    observation_issuer: object = field(repr=False, compare=False)
    poll_interval_seconds: float = 5.0

    def __post_init__(self) -> None:
        inst_ids = self.inst_ids
        if (
            type(inst_ids) is not tuple
            or not 1 <= len(inst_ids) <= _execution.MAX_INSTRUMENTS
            or len(set(inst_ids)) != len(inst_ids)
            or any(type(item) is not str or not _execution.INST_ID.fullmatch(item) for item in inst_ids)
        ):
            raise OkxSwapProviderError("INVALID_EXECUTION_SCOPE")
        lookback = self.lookback_seconds
        if type(lookback) is not int or not (
            _execution.MIN_LOOKBACK_SECONDS <= lookback <= _execution.MAX_LOOKBACK_SECONDS
        ):
            raise OkxSwapProviderError("INVALID_EXECUTION_SCOPE")
        interval = self.poll_interval_seconds
        if type(interval) not in (int, float) or not math.isfinite(interval) or not (
            0 <= interval <= _execution.MAX_POLL_INTERVAL_SECONDS
        ):
            raise OkxSwapProviderError("INVALID_EXECUTION_SCOPE")
        if not all(
            callable(getattr(self.observation_issuer, name, None))
            for name in ("issue_order_observation_id", "issue_trade_observation_id")
        ):
            raise OkxSwapProviderError("INVALID_EXECUTION_SCOPE")


class OkxSwapDemoAccountSessionProvider:
    """One-shot, owner-thread OKX SWAP Demo reader compatible with Gateway.

    ``transport(method, url, headers, timeout, max_bytes) -> bytes`` exists for
    deterministic source tests; the default is a fixed-origin HTTPS GET. The
    origin and route table are module constants, not deployment metadata.
    """

    def __init__(
        self,
        credentials: OkxSwapApiCredentials | Mapping[str, Any],
        *,
        environment: str = "demo",
        transport: Callable[[str, str, Mapping[str, str], float, int], bytes] | None = None,
        wall_clock: Callable[[], float] = time.time,
        monotonic_clock: Callable[[], float] = time.monotonic,
        execution: OkxSwapExecutionScope | None = None,
    ) -> None:
        if environment != "demo":
            raise OkxSwapProviderError("INVALID_ACCOUNT_IDENTITY")
        if execution is not None and type(execution) is not OkxSwapExecutionScope:
            raise OkxSwapProviderError("INVALID_EXECUTION_SCOPE")
        self._credentials = _credentials(credentials)
        self._transport = transport or _https_get
        if not callable(self._transport) or not callable(wall_clock) or not callable(
            monotonic_clock
        ):
            self._credentials = None
            raise OkxSwapProviderError("INVALID_CREDENTIALS")
        self._wall_clock = wall_clock
        self._monotonic_clock = monotonic_clock
        self._execution_scope = execution
        self._execution_reader: _execution.OkxSwapExecutionReader | None = None
        self._owner_thread: int | None = None
        self._account_key: AccountKey | None = None
        self._generation: str | None = None
        self._closed = False
        self._server_time_offset_ms: int | None = None
        self._server_time_observed_monotonic: float | None = None

    def __repr__(self) -> str:
        state = "closed" if self._closed else "active" if self._generation else "new"
        return f"OkxSwapDemoAccountSessionProvider(environment=demo, state={state})"

    def connect(self, *, account_key: AccountKey, generation: str, timeout: float) -> None:
        """Bind this instance to one Demo account, generation and owner thread."""

        if self._closed:
            raise OkxSwapProviderError("PROVIDER_SESSION_CLOSED")
        if self._generation is not None:
            raise OkxSwapProviderError("PROVIDER_SESSION_ALREADY_CONNECTED")
        _validate_timeout(timeout)
        if (
            type(account_key) is not AccountKey
            or account_key.provider != "okx"
            or account_key.venue != "OKX"
            or account_key.environment != "demo"
            or account_key.subaccount_id is not None
        ):
            raise OkxSwapProviderError("INVALID_ACCOUNT_IDENTITY")
        _validate_generation(generation)
        self._owner_thread = threading.get_ident()
        self._account_key = account_key
        self._generation = generation
        if self._execution_scope is not None:
            # One pending queue per generation; nothing carries over.
            self._execution_reader = self._new_execution_reader(account_key)
        self._fetch_server_time(_deadline(self._monotonic_clock, timeout))

    def read_account(self, *, generation: str, timeout: float) -> AccountObservation:
        """Read balances, cross-margin SWAP positions and regular open orders."""

        self._assert_active(generation)
        deadline = _deadline(self._monotonic_clock, timeout)
        self._ensure_server_time(deadline)
        started = _utc_now(self._wall_clock)
        try:
            config = _single(self._request_data("account_config", {}, deadline))
            if config.get("acctLv") != "2":
                # Other account modes share margin across currencies; their
                # per-currency balances are not this observation's facts.
                raise OkxSwapProviderError("ACCOUNT_COVERAGE_UNSUPPORTED")
            balance = _single(self._request_data("balance", {}, deadline))
            details = balance.get("details")
            positions = self._request_data("positions", {"instType": _PRODUCT_TYPE}, deadline)
            orders = self._open_order_rows(deadline)
            if type(details) is not list:
                raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
            if len(details) > MAX_ACCOUNT_ROWS or len(positions) > MAX_ACCOUNT_ROWS:
                raise OkxSwapProviderError("ACCOUNT_ROWS_EXCEEDED")
            completed = _utc_now(self._wall_clock)
            key = self._account_key
            assert key is not None
            observation = AccountObservation(
                account_key=key,
                observation_id="okx-swap-" + uuid.uuid4().hex,
                coverage=(ACCOUNT_RESOURCE, SWAP_CROSS_RESOURCE),
                balances=tuple(_balance(_dict(row), completed) for row in details),
                positions=tuple(
                    _position(row, key, completed)
                    for row in (_dict(item) for item in positions)
                    if _margin_mode(row.get("mgnMode")) == "cross"
                ),
                valuation=None,
                started_at_utc=started,
                completed_at_utc=completed,
                consistency="multi_query",
                balances_complete=True,
                positions_complete=True,
                open_orders=tuple(
                    _open_order(row, key, completed)
                    for row in orders
                    if _margin_mode(row.get("tdMode")) == "cross"
                ),
                # Algo (trigger/conditional) orders are not read.
                open_orders_complete=False,
            )
        except OkxSwapProviderError:
            raise
        except Exception:
            raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_READ_FAILED") from None
        return observation

    @property
    def execution_counters(self) -> Mapping[str, int]:
        """Finite refusal/diagnostic counters of the current execution queue."""

        reader = self._execution_reader
        return {} if reader is None else reader.counters

    def read_execution_observations(
        self, *, generation: str, timeout: float, limit: int
    ) -> tuple[Any, ...]:
        """Return (without removing) up to ``limit`` pending execution observations."""

        self._assert_active(generation)
        reader = self._execution_reader
        if reader is None:
            raise OkxSwapProviderError("EXECUTION_OBSERVATIONS_NOT_CONFIGURED")
        deadline = _deadline(self._monotonic_clock, timeout)
        try:
            return reader.read(limit=limit, deadline=deadline)
        except OkxSwapProviderError:
            raise
        except _execution.ExecutionReadIssue as issue:
            raise OkxSwapProviderError(issue.code) from None
        except Exception:
            raise OkxSwapProviderError("EXECUTION_READ_FAILED") from None

    def confirm_execution_observations(self, *, generation: str, count: int) -> None:
        """Remove the first ``count`` observations handed out by the last read."""

        self._assert_active(generation)
        reader = self._execution_reader
        if reader is None:
            raise OkxSwapProviderError("EXECUTION_OBSERVATIONS_NOT_CONFIGURED")
        try:
            reader.confirm(count)
        except _execution.ExecutionReadIssue as issue:
            raise OkxSwapProviderError(issue.code) from None

    def close(self) -> bool:
        """Drop credentials and the unconfirmed queue; no remote session exists."""

        if self._closed:
            return True
        if self._owner_thread is not None and threading.get_ident() != self._owner_thread:
            raise OkxSwapProviderError("PROVIDER_THREAD_MISMATCH")
        self._credentials = None
        self._server_time_offset_ms = None
        self._server_time_observed_monotonic = None
        self._execution_reader = None
        self._closed = True
        return True

    # -- internals ----------------------------------------------------------------

    def _new_execution_reader(self, account_key: AccountKey) -> _execution.OkxSwapExecutionReader:
        scope = self._execution_scope
        assert scope is not None

        def request(route: str, params: Mapping[str, str], deadline: float) -> list[Any]:
            self._ensure_server_time(deadline)
            return self._request_data(route, params, deadline)

        def exchange_now_ms(deadline: float) -> int:
            self._ensure_server_time(deadline)
            offset = self._server_time_offset_ms
            if offset is None:
                raise OkxSwapProviderError("SERVER_TIME_PROBE_REQUIRED")
            return int(_clock_value(self._wall_clock) * 1000) + offset

        return _execution.OkxSwapExecutionReader(
            account_key=account_key,
            inst_ids=scope.inst_ids,
            lookback_seconds=scope.lookback_seconds,
            poll_interval_seconds=scope.poll_interval_seconds,
            observation_issuer=scope.observation_issuer,
            request=request,
            exchange_now_ms=exchange_now_ms,
            utc_now=lambda: _utc_now(self._wall_clock),
            monotonic=lambda: _clock_value(self._monotonic_clock),
        )

    def _open_order_rows(self, deadline: float) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        params = {"instType": _PRODUCT_TYPE, "limit": str(_PAGE_LIMIT)}
        for _page in range(_MAX_OPEN_ORDER_PAGES):
            page = [_dict(item) for item in self._request_data("orders_pending", params, deadline)]
            if len(page) > _PAGE_LIMIT:
                raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
            rows.extend(page)
            if len(rows) > MAX_ACCOUNT_ROWS:
                raise OkxSwapProviderError("ACCOUNT_ROWS_EXCEEDED")
            if len(page) < _PAGE_LIMIT:
                return rows
            params = {**params, "after": str(min(_digits(row.get("ordId")) for row in page))}
        raise OkxSwapProviderError("ACCOUNT_ROWS_EXCEEDED")

    def _fetch_server_time(self, deadline: float) -> None:
        mono_before = _clock_value(self._monotonic_clock)
        wall_before = _clock_value(self._wall_clock)
        try:
            data = self._request_data("server_time", {}, deadline, signed=False)
            row = _single(data)
            server_ms = _digits(row.get("ts"))
        except OkxSwapProviderError as error:
            if error.code in {"REQUEST_TIMEOUT", "TRANSPORT_FAILED", "RESPONSE_TOO_LARGE"}:
                raise
            raise OkxSwapProviderError("SERVER_TIME_INVALID") from None
        except Exception:
            raise OkxSwapProviderError("SERVER_TIME_READ_FAILED") from None
        wall_after = _clock_value(self._wall_clock)
        mono_after = _clock_value(self._monotonic_clock)
        if not 0 < server_ms <= 253402300799999 or mono_after < mono_before or wall_after < wall_before:
            raise OkxSwapProviderError("SERVER_TIME_INVALID")
        if mono_after - mono_before > _MAX_TIMEOUT_SECONDS:
            raise OkxSwapProviderError("REQUEST_TIMEOUT")
        midpoint_ms = int(round((wall_before + wall_after) * 500))
        self._server_time_offset_ms = server_ms - midpoint_ms
        self._server_time_observed_monotonic = mono_after

    def _ensure_server_time(self, deadline: float) -> None:
        observed = self._server_time_observed_monotonic
        if observed is None or self._server_time_offset_ms is None:
            self._fetch_server_time(deadline)
            return
        now = _clock_value(self._monotonic_clock)
        if now < observed:
            raise OkxSwapProviderError("SERVER_TIME_INVALID")
        if now - observed > _SERVER_TIME_MAX_AGE_SECONDS:
            self._fetch_server_time(deadline)

    def _request_data(
        self,
        route: str,
        params: Mapping[str, str],
        deadline: float,
        *,
        signed: bool = True,
    ) -> list[Any]:
        path = _ROUTES.get(route)
        allowed = _ROUTE_PARAMS.get(route, frozenset())
        if path is None or signed != (route != "server_time") or (not signed and params):
            raise OkxSwapProviderError("TRANSPORT_FAILED")
        if any(
            type(key) is not str
            or key not in allowed
            or type(value) is not str
            or not value
            or len(value) > 64
            or not all(char.isalnum() or char in "-_" for char in value)
            or not value.isascii()
            for key, value in params.items()
        ):
            raise OkxSwapProviderError("TRANSPORT_FAILED")
        remaining = deadline - _clock_value(self._monotonic_clock)
        if remaining <= 0:
            raise OkxSwapProviderError("REQUEST_TIMEOUT")
        query = urlencode(sorted(params.items()))
        request_path = path + ("?" + query if query else "")
        headers = {"Accept": "application/json", "x-simulated-trading": "1"}
        if signed:
            credentials = self._credentials
            offset = self._server_time_offset_ms
            if credentials is None or offset is None:
                raise OkxSwapProviderError("SERVER_TIME_PROBE_REQUIRED")
            timestamp_ms = int(_clock_value(self._wall_clock) * 1000) + offset
            if timestamp_ms <= 0:
                raise OkxSwapProviderError("SERVER_TIME_INVALID")
            timestamp = _iso_ms(timestamp_ms)
            message = timestamp + "GET" + request_path
            signature = base64.b64encode(
                hmac.new(
                    credentials.api_secret.encode("ascii"),
                    message.encode("ascii"),
                    hashlib.sha256,
                ).digest()
            ).decode("ascii")
            headers.update(
                {
                    "OK-ACCESS-KEY": credentials.api_key,
                    "OK-ACCESS-SIGN": signature,
                    "OK-ACCESS-TIMESTAMP": timestamp,
                    "OK-ACCESS-PASSPHRASE": credentials.passphrase,
                }
            )
        try:
            body = self._transport(
                "GET", _BASE_URL + request_path, headers, remaining, MAX_ACCOUNT_OBSERVATION_BYTES
            )
        except OkxSwapProviderError:
            raise
        except Exception:
            raise OkxSwapProviderError("TRANSPORT_FAILED") from None
        if _clock_value(self._monotonic_clock) > deadline:
            raise OkxSwapProviderError("REQUEST_TIMEOUT")
        if type(body) is not bytes:
            raise OkxSwapProviderError("INVALID_JSON_RESPONSE")
        if len(body) > MAX_ACCOUNT_OBSERVATION_BYTES:
            raise OkxSwapProviderError("RESPONSE_TOO_LARGE")
        try:
            response = json.loads(body.decode("utf-8", errors="strict"))
        except Exception:
            raise OkxSwapProviderError("INVALID_JSON_RESPONSE") from None
        if type(response) is not dict or response.get("code") != "0":
            raise OkxSwapProviderError("VENUE_ERROR_RESPONSE")
        data = response.get("data")
        if type(data) is not list:
            raise OkxSwapProviderError("INVALID_JSON_RESPONSE")
        return data

    def _assert_active(self, generation: str) -> None:
        if self._closed:
            raise OkxSwapProviderError("PROVIDER_SESSION_CLOSED")
        if self._generation is None or self._owner_thread is None or self._account_key is None:
            raise OkxSwapProviderError("PROVIDER_SESSION_NOT_ACTIVE")
        if threading.get_ident() != self._owner_thread:
            raise OkxSwapProviderError("PROVIDER_THREAD_MISMATCH")
        _validate_generation(generation)
        if generation != self._generation:
            raise OkxSwapProviderError("PROVIDER_GENERATION_MISMATCH")


def make_okx_swap_demo_provider(
    session_ref: str,
    credential_obj: object,
    *,
    execution: OkxSwapExecutionScope | None = None,
) -> OkxSwapDemoAccountSessionProvider:
    """GatewaySessionOwner-compatible factory for trusted Demo credentials.

    A composition that publishes execution events binds ``execution`` (for
    example with ``functools.partial``); the default stays account-only.
    """

    if type(session_ref) is not str or _SESSION_REF.fullmatch(session_ref) is None:
        raise OkxSwapProviderError("INVALID_ACCOUNT_IDENTITY")
    return OkxSwapDemoAccountSessionProvider(
        credential_obj, execution=execution  # type: ignore[arg-type]
    )


def _credentials(value: object) -> OkxSwapApiCredentials:
    if type(value) is OkxSwapApiCredentials:
        return value
    if isinstance(value, Mapping):
        try:
            if set(value) != {"api_key", "api_secret", "passphrase"}:
                raise OkxSwapProviderError("INVALID_CREDENTIALS")
            return OkxSwapApiCredentials(
                api_key=value["api_key"],
                api_secret=value["api_secret"],
                passphrase=value["passphrase"],
            )
        except OkxSwapProviderError:
            raise
        except Exception:
            raise OkxSwapProviderError("INVALID_CREDENTIALS") from None
    raise OkxSwapProviderError("INVALID_CREDENTIALS")


def _https_get(
    method: str, url: str, headers: Mapping[str, str], timeout: float, max_bytes: int
) -> bytes:
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        raise OkxSwapProviderError("TRANSPORT_FAILED") from None
    if (
        method != "GET"
        or parsed.scheme != "https"
        or parsed.netloc != _HOST
        or parsed.path not in _ROUTES.values()
        or parsed.fragment
        or headers.get("x-simulated-trading") != "1"
    ):
        raise OkxSwapProviderError("TRANSPORT_FAILED")
    request = Request(  # noqa: S310 - exact HTTPS origin and route; redirects are disabled
        url, headers=dict(headers), method="GET"
    )
    try:
        opener = build_opener(_NoRedirectHandler())
        with opener.open(request, timeout=timeout) as response:
            payload = response.read(max_bytes + 1)
    except Exception:
        raise OkxSwapProviderError("TRANSPORT_FAILED") from None
    if len(payload) > max_bytes:
        raise OkxSwapProviderError("RESPONSE_TOO_LARGE")
    return payload


def _deadline(clock: Callable[[], float], timeout: float) -> float:
    _validate_timeout(timeout)
    return _clock_value(clock) + timeout


def _validate_timeout(timeout: float) -> None:
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or not (
        0 < timeout <= _MAX_TIMEOUT_SECONDS
    ):
        raise OkxSwapProviderError("INVALID_TIMEOUT")


def _validate_generation(generation: str) -> None:
    if type(generation) is not str or not generation or generation != generation.strip():
        raise OkxSwapProviderError("INVALID_GENERATION")


def _clock_value(clock: Callable[[], float]) -> float:
    try:
        value = clock()
    except Exception:
        raise OkxSwapProviderError("REQUEST_TIMEOUT") from None
    if type(value) not in (int, float) or not math.isfinite(value):
        raise OkxSwapProviderError("REQUEST_TIMEOUT")
    return float(value)


def _utc_now(clock: Callable[[], float]) -> str:
    try:
        value = datetime.fromtimestamp(_clock_value(clock), tz=timezone.utc)
    except OkxSwapProviderError:
        raise
    except Exception:
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID") from None
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _iso_ms(milliseconds: int) -> str:
    return (
        datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _dict(value: Any) -> dict[str, Any]:
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    return value


def _single(data: list[Any]) -> dict[str, Any]:
    if len(data) != 1:
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    return _dict(data[0])


def _digits(value: Any) -> int:
    if type(value) is not str or not _DIGITS.fullmatch(value):
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    return int(value)


def _decimal_text(value: Any) -> str:
    if type(value) is not str or not _DECIMAL.fullmatch(value):
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    try:
        text = format(Decimal(value), "f")
    except InvalidOperation:
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID") from None
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def _optional_decimal(value: Any) -> str | None:
    return None if value in (None, "") else _decimal_text(value)


def _margin_mode(value: Any) -> str:
    if value in {"cross", "isolated"}:
        return value
    raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")


def _instrument(key: AccountKey, inst_id: Any) -> MarketInstrumentKey:
    if type(inst_id) is not str or not _execution.INST_ID.fullmatch(inst_id):
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    return MarketInstrumentKey(
        provider=key.provider,
        venue=key.venue,
        environment=key.environment,
        product_type=_PRODUCT_TYPE,
        instrument_id=inst_id,
        native_symbol=inst_id,
    )


def _balance(row: dict[str, Any], observed: str) -> AccountBalance:
    currency = row.get("ccy")
    if type(currency) is not str or not _CURRENCY.fullmatch(currency):
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    # eq: this currency's equity; availBal: available balance; frozenBal:
    # frozen balance (the OKX query service uses the same mapping).
    return AccountBalance(
        resource=ACCOUNT_RESOURCE,
        currency=currency,
        total=_optional_decimal(row.get("eq")),
        available=_optional_decimal(row.get("availBal")),
        locked=_optional_decimal(row.get("frozenBal")),
        observed_at_utc=observed,
    )


def _position(row: dict[str, Any], key: AccountKey, observed: str) -> AccountPosition:
    if row.get("instType") != _PRODUCT_TYPE:
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    side = row.get("posSide")
    if side not in {"net", "long", "short"}:
        raise OkxSwapProviderError("ACCOUNT_SNAPSHOT_INVALID")
    return AccountPosition(
        resource=SWAP_CROSS_RESOURCE,
        instrument=_instrument(key, row.get("instId")),
        side=side,
        # Contracts; net mode keeps the sign, long/short sizes are non-negative.
        quantity=_decimal_text(row.get("pos")),
        qty_unit=_QTY_UNIT,
        average_price=None,
        price_currency=None,
        observed_at_utc=observed,
    )


def _open_order(row: dict[str, Any], key: AccountKey, observed: str) -> AccountOpenOrder:
    if row.get("instType") != _PRODUCT_TYPE:
        raise OkxSwapProviderError("OPEN_ORDER_SHAPE_UNSUPPORTED")
    state = row.get("state")
    order_type = row.get("ordType")
    if state not in {"live", "partially_filled"} or type(order_type) is not str or not (
        _ORDER_TYPE.fullmatch(order_type)
    ):
        raise OkxSwapProviderError("OPEN_ORDER_SHAPE_UNSUPPORTED")
    side = row.get("side")
    position_side = row.get("posSide")
    if side not in {"buy", "sell"} or position_side not in {"net", "long", "short"}:
        raise OkxSwapProviderError("OPEN_ORDER_SHAPE_UNSUPPORTED")
    reduce_only = row.get("reduceOnly")
    if reduce_only not in (None, "", "true", "false"):
        raise OkxSwapProviderError("OPEN_ORDER_SHAPE_UNSUPPORTED")
    client = row.get("clOrdId")
    if client not in (None, "") and (
        type(client) is not str or len(client) > 64 or not client.isascii() or not client.isprintable()
    ):
        raise OkxSwapProviderError("OPEN_ORDER_SHAPE_UNSUPPORTED")
    price = _optional_decimal(row.get("px"))
    return AccountOpenOrder(
        resource=SWAP_CROSS_RESOURCE,
        instrument=_instrument(key, row.get("instId")),
        order_id=str(_digits(row.get("ordId"))),
        side=side,
        position_side=position_side,
        order_type=order_type,
        status="open" if state == "live" else "partially_filled",
        quantity=_decimal_text(row.get("sz")),
        filled_quantity=_decimal_text(row.get("accFillSz")),
        qty_unit=_QTY_UNIT,
        created_at_utc=_iso_ms(_digits(row.get("cTime"))),
        observed_at_utc=observed,
        client_order_id=None if client in (None, "") else client,
        limit_price=None if price is None or Decimal(price) == 0 else price,
        stop_price=None,
        price_currency=None,
        reduce_only=None if reduce_only in (None, "") else reduce_only == "true",
    )


__all__ = [
    "ACCOUNT_RESOURCE",
    "OkxSwapApiCredentials",
    "OkxSwapDemoAccountSessionProvider",
    "OkxSwapExecutionScope",
    "OkxSwapProviderError",
    "SWAP_CROSS_RESOURCE",
    "make_okx_swap_demo_provider",
]
