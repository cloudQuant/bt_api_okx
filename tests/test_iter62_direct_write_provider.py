"""Iteration 62: OKX SWAP direct write provider (fakes only, no network).

Every test drives a real ``OkxRequestDataSwap`` whose ``request`` is replaced by
a scripted venue and whose HTTP layer raises if anything tries to reach the
network.  Evidence level: UNIT/FAKE (the coordinator test is INTEGRATION_SIM
against the in-process SDK coordinator).
"""

from __future__ import annotations

import time
import tomllib
from collections import deque
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.direct_write_protocol import (
    DirectExecutionEventKind,
    DirectOrderStatus,
    DirectWriteError,
    NativeOrderIdentity,
    SettlementStatus,
    WriteAdmissionDenied,
    WriteGrant,
    WriteOperation,
)
from bt_api_base.error import ServerError
from bt_api_base.exceptions import RequestTimeoutError
from bt_api_okx.direct_write_provider import (
    OkxDirectOutcomeUnknown,
    OkxDirectWriteProvider,
    create_okx_direct_write_provider,
)
from bt_api_okx.feeds.live_okx.spot import OkxRequestDataSpot
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap

ROUTE = "OKX___SWAP"
INST = "BTC-USDT-SWAP"
ORD_ID = "312269865356374016"
API_KEY = "unit-okx-key-3f9a"
API_SECRET = "unit-okx-secret-77c1"
PASSPHRASE = "unit-okx-pass-0b2e"
WALL = datetime(2026, 11, 6, 3, 0, tzinfo=timezone.utc).timestamp()
DAY_START_MS = int(datetime(2026, 11, 6, tzinfo=timezone.utc).timestamp() * 1000)
PLACE = "POST /api/v5/trade/order"
CANCEL = "POST /api/v5/trade/cancel-order"
QUERY = "GET /api/v5/trade/order"
FILLS = "GET /api/v5/trade/fills"
PENDING = "GET /api/v5/trade/orders-pending"
HISTORY = "GET /api/v5/trade/orders-history"
POSITIONS = "GET /api/v5/account/positions"
BALANCE = "GET /api/v5/account/balance"
SERVER_TIME = "GET /api/v5/public/time"


def _no_network(*_args, **_kwargs):
    raise AssertionError("network access is forbidden in these tests")


def _feed(**credentials) -> OkxRequestDataSwap:
    values = {"api_key": API_KEY, "secret_key": API_SECRET, "passphrase": PASSPHRASE}
    values.update(credentials)
    feed = OkxRequestDataSwap(None, environment="demo", **values)
    feed.http_request = _no_network
    return feed


class Venue:
    """Scripted OKX signed REST replies; records every call in ``calls``."""

    def __init__(self, feed, calls):
        self.feed = feed
        self.calls = calls
        self.handlers: dict[str, object] = {}
        feed.request = self.request

    def on(self, route, *replies):
        self.handlers[route] = deque(replies)

    def request(self, path, params=None, body=None, extra_data=None, timeout=10, **kwargs):
        self.calls.append(("request", path, dict(params or {}), dict(body or {})))
        replies = self.handlers.get(path)
        if not replies:
            raise AssertionError(f"unexpected request {path}")
        reply = replies.popleft() if len(replies) > 1 else replies[0]
        if callable(reply):
            reply = reply(dict(params or {}), dict(body or {}))
        if isinstance(reply, BaseException):
            raise reply
        if isinstance(reply, dict) and str(reply.get("code", "0")) != "0":
            raise self.feed.translate_error(reply)
        return RequestData(reply, extra_data)


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class Verifier:
    def __init__(self, calls, deny=False):
        self.calls = calls
        self.deny = deny

    def consume(self, grant, *, exchange_name, operation, session_generation):
        self.calls.append(("consume", exchange_name, operation, session_generation))
        if self.deny:
            raise WriteAdmissionDenied("write_grant_invalid_or_consumed")


def _grant(operation=WriteOperation.PLACE):
    return WriteGrant(ROUTE, operation, 1, "grant-unit", 1)


def _req(**overrides):
    values = dict(
        symbol=INST,
        side=SimpleNamespace(value="buy"),
        order_type=SimpleNamespace(value="limit"),
        quantity=Decimal("2"),
        price=Decimal("60000"),
        time_in_force="GTC",
        reduce_only=False,
        quantity_unit="contracts",
        position_side=None,
        offset=None,
        position_id=None,
        position_mode=None,
        client_order_id="bt0a1b2c3d4e5fs1",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def _ok(*rows):
    return {"code": "0", "msg": "", "data": list(rows)}


def _ack(cid, ord_id=ORD_ID):
    return _ok({"clOrdId": cid, "ordId": ord_id, "tag": "", "sCode": "0", "sMsg": ""})


def _order(state="live", filled="0", cid="bt0a1b2c3d4e5fs1", pos_side="long", reduce_only="false",
           ord_id=ORD_ID, size="2"):
    return {
        "instType": "SWAP",
        "instId": INST,
        "ordId": ord_id,
        "clOrdId": cid,
        "state": state,
        "side": "buy",
        "posSide": pos_side,
        "sz": size,
        "accFillSz": filled,
        "px": "60000",
        "reduceOnly": reduce_only,
        "cTime": str(DAY_START_MS + 3_600_000),
    }


def _fill(trade_id, qty, bill_id, side="buy", pos_side="long", ord_id=ORD_ID, ts_offset=0):
    return {
        "instType": "SWAP",
        "instId": INST,
        "tradeId": trade_id,
        "ordId": ord_id,
        "clOrdId": "bt0a1b2c3d4e5fs1",
        "billId": bill_id,
        "side": side,
        "posSide": pos_side,
        "fillPx": "60001.5",
        "fillSz": qty,
        "ts": str(DAY_START_MS + 3_700_000 + ts_offset),
    }


@pytest.fixture
def env():
    calls: list = []
    feed = _feed()
    venue = Venue(feed, calls)
    clock = Clock()
    provider = OkxDirectWriteProvider(feed, clock=clock, wall_clock=lambda: WALL)
    yield SimpleNamespace(feed=feed, venue=venue, calls=calls, clock=clock, provider=provider)
    feed._http_client.close()


def _requests(calls):
    return [call for call in calls if call[0] == "request"]


# ----------------------------------------------------------------- factory


def test_factory_wraps_only_the_exact_swap_feed():
    feed = _feed()
    try:
        assert isinstance(create_okx_direct_write_provider(feed), OkxDirectWriteProvider)
    finally:
        feed._http_client.close()
    spot = OkxRequestDataSpot(None, environment="demo")
    try:
        for wrong in (object(), spot):
            with pytest.raises(DirectWriteError) as info:
                create_okx_direct_write_provider(wrong)
            assert info.value.code == "okx_direct_write_feed_invalid"
    finally:
        spot._http_client.close()


def test_entry_point_is_declared_for_the_swap_route():
    pyproject = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )
    group = pyproject["project"]["entry-points"]["bt_api.direct_write_providers"]
    assert group == {ROUTE: "bt_api_okx.direct_write_provider:create_okx_direct_write_provider"}


def test_session_trading_day_and_settlement(env):
    assert env.provider.session_generation() == 1
    assert env.provider.trading_day() == "20261106"
    assert env.provider.settlement_status() is SettlementStatus.CONFIRMED
    bare = _feed(passphrase=None)
    try:
        provider = OkxDirectWriteProvider(bare)
        assert provider.session_generation() is None
        with pytest.raises(DirectWriteError) as info:
            provider.reserve_order(_req())
        assert info.value.code == "okx_direct_session_unavailable"
        assert provider._reservations == {}
    finally:
        bare._http_client.close()


# ----------------------------------------------------------------- reserve


def test_reserve_binds_client_order_id_inst_id_and_utc_day(env):
    reservation = env.provider.reserve_order(_req())
    identity = reservation.identity
    assert identity.exchange_name == ROUTE
    assert identity.client_order_id == "bt0a1b2c3d4e5fs1"
    assert dict(identity.fields) == {"inst_id": INST, "trading_day": "20261106"}
    assert identity.session_generation == 1
    assert reservation.symbol == INST
    assert _requests(env.calls) == []  # reserving never touches the venue


@pytest.mark.parametrize(
    "overrides",
    [
        {"quantity_unit": "base"},  # OKX sz is a contract count
        {"quantity_unit": "lots"},
        {"symbol": "BTC-USDT"},  # not the native instId
        {"time_in_force": "GFD"},
        {"offset": "close_today", "reduce_only": True, "side": SimpleNamespace(value="sell")},
        {"position_id": "ticket-1"},
        {"price": None},  # limit without a price
        {"time_in_force": "post_only", "order_type": SimpleNamespace(value="market"), "price": None},
        {"position_mode": "dual_side"},  # dual side without a position side
    ],
)
def test_unrepresentable_request_fails_before_any_reservation(env, overrides):
    with pytest.raises(DirectWriteError) as info:
        env.provider.reserve_order(_req(**overrides))
    assert info.value.code == "okx_direct_request_unrepresentable"
    assert env.provider._reservations == {}
    assert env.calls == []


def test_base_quantity_is_refused_even_when_the_feed_has_a_conversion_entry(env):
    # With a table entry the feed multiplies the string size, swallows the
    # TypeError and would send the base quantity as a contract count.
    env.feed._params.symbol_leverage_dict[INST] = 100
    with pytest.raises(DirectWriteError) as info:
        env.provider.reserve_order(_req(quantity_unit="base"))
    assert info.value.code == "okx_direct_request_unrepresentable"
    assert "contract" in info.value.detail
    assert env.provider._reservations == {} and env.calls == []


@pytest.mark.parametrize("bad", ["has-dash", "under_score", "x" * 33, "café", "", " a1"])
def test_client_order_id_rules_refuse_instead_of_rewriting(env, bad):
    with pytest.raises(DirectWriteError) as info:
        env.provider.reserve_order(_req(client_order_id=bad))
    assert info.value.code == "okx_direct_client_order_id_invalid"
    assert env.provider._reservations == {}


def test_client_order_id_is_sent_unchanged_and_not_reused(env):
    cid = "A" * 31 + "9"
    env.venue.on(PLACE, _ack(cid))
    reservation = env.provider.reserve_order(_req(client_order_id=cid))
    with pytest.raises(DirectWriteError) as info:
        env.provider.reserve_order(_req(client_order_id=cid))
    assert info.value.code == "okx_direct_client_order_id_in_use"
    result = env.provider.submit_order(
        reservation, _req(client_order_id=cid), _grant(), Verifier(env.calls)
    )
    assert result.sent is True
    (_, path, _params, body) = _requests(env.calls)[0]
    assert path == PLACE and body["clOrdId"] == cid and body["instId"] == INST
    assert body["sz"] == "2" and body["px"] == "60000" and body["ordType"] == "limit"


# ------------------------------------------------------------------ submit


def test_verifier_is_consumed_immediately_before_the_single_send(env):
    env.venue.on(PLACE, _ack("bt0a1b2c3d4e5fs1"))
    reservation = env.provider.reserve_order(_req())
    result = env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls))
    assert [call[0] for call in env.calls] == ["consume", "request"]
    assert env.calls[0][1:] == (ROUTE, WriteOperation.PLACE, 1)
    assert result.sent is True
    assert result.identity.fields["ord_id"] == ORD_ID
    assert result.identity.client_order_id == "bt0a1b2c3d4e5fs1"


def test_denied_grant_never_reaches_the_venue(env):
    env.venue.on(PLACE, _ack("bt0a1b2c3d4e5fs1"))
    reservation = env.provider.reserve_order(_req())
    with pytest.raises(WriteAdmissionDenied):
        env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls, deny=True))
    assert _requests(env.calls) == []
    assert env.provider.watched_count == 0


def test_request_changed_after_reservation_is_not_sent(env):
    reservation = env.provider.reserve_order(_req())
    with pytest.raises(DirectWriteError) as info:
        env.provider.submit_order(
            reservation, _req(price=Decimal("1")), _grant(), Verifier(env.calls)
        )
    assert info.value.code == "okx_direct_reservation_request_mismatch"
    assert env.calls == []
    with pytest.raises(DirectWriteError) as info:
        env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls))
    assert info.value.code == "okx_direct_reservation_unknown"


def test_definite_venue_rejection_is_not_sent(env):
    env.venue.on(
        PLACE,
        {
            "code": "1",
            "msg": "All operations failed",
            "data": [{"clOrdId": "bt0a1b2c3d4e5fs1", "ordId": "", "sCode": "51008", "sMsg": "x"}],
        },
    )
    reservation = env.provider.reserve_order(_req())
    result = env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls))
    assert result.sent is False
    assert result.error_code == "okx_order_rejected" and result.detail == "51008"
    assert env.provider.watched_count == 0


@pytest.mark.parametrize(
    "failure",
    [
        RequestTimeoutError(ROUTE, timeout=10),
        ServerError(venue=ROUTE, status=503, response={"code": "51008"}),
        {"code": "50001", "msg": "Service temporarily unavailable", "data": []},
        ConnectionResetError("reset after write"),
    ],
)
def test_failure_after_send_is_an_unknown_outcome(env, failure):
    env.venue.on(PLACE, failure)
    reservation = env.provider.reserve_order(_req())
    with pytest.raises(OkxDirectOutcomeUnknown) as info:
        env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls))
    assert info.value.code == "okx_direct_submit_outcome_unknown"
    assert not isinstance(info.value, DirectWriteError)
    assert env.provider.watched_count == 1  # recovered later by identity


def test_sdk_coordinator_reports_sent_true_false_and_unknown():
    direct_write = pytest.importorskip("bt_api_py.direct_write")
    write_admission = pytest.importorskip("bt_api_py.write_admission")
    calls: list = []
    feed = _feed()
    try:
        venue = Venue(feed, calls)
        provider = OkxDirectWriteProvider(feed, clock=Clock(), wall_clock=lambda: WALL)
        coordinator = direct_write.DirectWriteCoordinator(
            write_admission.WriteAdmission({ROUTE: True}), lambda _name: provider
        )
        port = SimpleNamespace(commit=lambda record: f"marker-{record.identity.client_order_id}")
        venue.on(PLACE, RequestTimeoutError(ROUTE, timeout=10))
        unknown = coordinator.place(ROUTE, _req(client_order_id="u1"), commit_port=port, host_scope="t")
        assert unknown.sent is None and unknown.error_code == "direct_submit_outcome_unknown"
        venue.on(PLACE, {"code": "1", "data": [{"sCode": "51008", "sMsg": "x"}]})
        rejected = coordinator.place(ROUTE, _req(client_order_id="r1"), commit_port=port, host_scope="t")
        assert rejected.sent is False and rejected.error_code == "okx_order_rejected"
        venue.on(PLACE, _ack("s1"))
        sent = coordinator.place(ROUTE, _req(client_order_id="s1"), commit_port=port, host_scope="t")
        assert sent.sent is True and sent.marker_id == "marker-s1"
        assert sent.identity.fields["ord_id"] == ORD_ID
        venue.on(QUERY, lambda params, _body: (
            _ok(_order(cid="s1"))
            if params.get("ordId") == ORD_ID
            else {"code": "51603", "msg": "Order does not exist", "data": []}
        ))
        polled = coordinator.poll_events(ROUTE)
        assert len(polled) == 1
        assert polled[0].matched is True and polled[0].evidence == "direct_identity_match"
        assert polled[0].marker_id == "marker-s1"
        assert polled[0].event.status is DirectOrderStatus.ACCEPTED
    finally:
        feed._http_client.close()


# ------------------------------------------------------------------ cancel


def _target(**fields):
    base = {"inst_id": INST, "trading_day": "20261106"}
    base.update(fields)
    return NativeOrderIdentity(ROUTE, "bt0a1b2c3d4e5fs1", base, 1)


def test_cancel_uses_the_venue_order_id_when_known_else_the_client_id(env):
    env.venue.on(CANCEL, _ack("bt0a1b2c3d4e5fs1"))
    result = env.provider.cancel_order(
        _target(ord_id=ORD_ID), INST, _grant(WriteOperation.CANCEL), Verifier(env.calls)
    )
    assert result.sent is True
    assert [call[0] for call in env.calls] == ["consume", "request"]
    assert env.calls[0][2] is WriteOperation.CANCEL
    assert env.calls[1][3] == {"instId": INST, "ordId": ORD_ID}
    env.calls.clear()
    env.provider.cancel_order(_target(), INST, _grant(WriteOperation.CANCEL), Verifier(env.calls))
    assert env.calls[1][3] == {"instId": INST, "clOrdId": "bt0a1b2c3d4e5fs1"}


def test_cancel_refusals_happen_before_consume(env):
    cases = [
        (NativeOrderIdentity(ROUTE, None, {"inst_id": INST}), INST, "okx_direct_cancel_identity_incomplete"),
        (_target(), "ETH-USDT-SWAP", "okx_direct_cancel_symbol_mismatch"),
        (NativeOrderIdentity("CTP___FUTURE", "1", {}), INST, "okx_direct_cancel_identity_foreign"),
    ]
    for target, symbol, code in cases:
        with pytest.raises(DirectWriteError) as info:
            env.provider.cancel_order(target, symbol, _grant(WriteOperation.CANCEL), Verifier(env.calls))
        assert info.value.code == code
    assert env.calls == []
    with pytest.raises(WriteAdmissionDenied):
        env.provider.cancel_order(
            _target(), INST, _grant(WriteOperation.CANCEL), Verifier(env.calls, deny=True)
        )
    assert _requests(env.calls) == []


def test_cancel_outcomes(env):
    env.venue.on(CANCEL, {"code": "1", "data": [{"sCode": "51000", "sMsg": "bad"}]})
    rejected = env.provider.cancel_order(
        _target(), INST, _grant(WriteOperation.CANCEL), Verifier(env.calls)
    )
    assert rejected.sent is False and rejected.error_code == "okx_cancel_rejected"
    env.venue.on(CANCEL, RequestTimeoutError(ROUTE, timeout=10))
    with pytest.raises(OkxDirectOutcomeUnknown) as info:
        env.provider.cancel_order(_target(), INST, _grant(WriteOperation.CANCEL), Verifier(env.calls))
    assert info.value.code == "okx_direct_cancel_outcome_unknown"


# ----------------------------------------------------------------- returns


def _place(env, cid="bt0a1b2c3d4e5fs1", ord_id=ORD_ID, **overrides):
    env.venue.on(PLACE, _ack(cid, ord_id))
    reservation = env.provider.reserve_order(_req(client_order_id=cid, **overrides))
    return env.provider.submit_order(
        reservation, _req(client_order_id=cid, **overrides), _grant(), Verifier(env.calls)
    )


def test_polling_projects_orders_and_fills_once_and_stops_at_terminal(env):
    _place(env)
    env.venue.on(QUERY, _ok(_order("live", "0")))
    (accepted,) = env.provider.drain_execution_events(10)
    assert accepted.kind is DirectExecutionEventKind.ORDER
    assert accepted.status is DirectOrderStatus.ACCEPTED and accepted.offset == "open"
    assert accepted.identity.client_order_id == "bt0a1b2c3d4e5fs1"
    assert accepted.identity.fields["trading_day"] == "20261106"
    assert accepted.exchange_order_id == ORD_ID and accepted.order_qty == 2.0

    queries = len(_requests(env.calls))
    assert env.provider.drain_execution_events(10) == ()  # not due before poll_interval
    assert len(_requests(env.calls)) == queries

    env.clock.now += 1.0
    env.venue.on(QUERY, _ok(_order("partially_filled", "1")))
    env.venue.on(FILLS, _ok(_fill("901", "1", "5001")))
    trade, partial = env.provider.drain_execution_events(10)
    assert trade.kind is DirectExecutionEventKind.TRADE
    assert (trade.trade_id, trade.trade_qty, trade.trade_price) == ("901", 1.0, 60001.5)
    assert trade.side == "buy" and trade.offset == "open"
    assert trade.trade_time == "2026-11-06T01:01:40.000Z"
    assert partial.status is DirectOrderStatus.PARTIALLY_FILLED and partial.filled_qty == 1.0

    env.clock.now += 1.0
    assert env.provider.drain_execution_events(10) == ()  # unchanged: no event

    env.clock.now += 1.0
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    env.venue.on(FILLS, _ok(_fill("902", "1", "5002", ts_offset=5), _fill("901", "1", "5001")))
    second, filled = env.provider.drain_execution_events(10)
    assert second.trade_id == "902" and filled.status is DirectOrderStatus.FILLED
    assert env.provider.watched_count == 0  # terminal with complete fills

    keys = {event.dedup_key() for event in (accepted, trade, partial, second, filled)}
    assert len(keys) == 5
    env.clock.now += 10.0
    before = len(_requests(env.calls))
    assert env.provider.drain_execution_events(10) == ()
    assert len(_requests(env.calls)) == before  # stopped watching


def test_terminal_order_waits_for_lagging_fills(env):
    _place(env)
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    env.venue.on(FILLS, _ok())
    (filled,) = env.provider.drain_execution_events(10)
    assert filled.status is DirectOrderStatus.FILLED
    assert env.provider.watched_count == 1  # fills not visible yet
    env.clock.now += 1.0
    env.venue.on(FILLS, _ok(_fill("901", "2", "5001")))
    (trade,) = env.provider.drain_execution_events(10)
    assert trade.trade_qty == 2.0
    assert env.provider.watched_count == 0


def test_offset_comes_from_pos_side_or_reduce_only_never_guessed(env):
    _place(env)
    env.venue.on(QUERY, _ok(_order("partially_filled", "1", pos_side="net")))
    env.venue.on(FILLS, _ok(_fill("901", "1", "5001", pos_side="net")))
    events = env.provider.drain_execution_events(10)
    assert {event.offset for event in events} == {None}
    reduce_cid = "reduce1"
    _place(env, cid=reduce_cid, ord_id="7", side=SimpleNamespace(value="sell"), reduce_only=True)
    env.venue.on(QUERY, _ok(_order("live", "0", cid=reduce_cid, pos_side="net", reduce_only="true",
                                     ord_id="7")))
    env.clock.now += 1.0
    events = [e for e in env.provider.drain_execution_events(10) if e.identity.client_order_id == reduce_cid]
    assert len(events) == 1 and events[0].offset == "close"


def test_unknown_outcome_not_found_keeps_watching_without_inventing_events(env):
    env.venue.on(PLACE, RequestTimeoutError(ROUTE, timeout=10))
    reservation = env.provider.reserve_order(_req())
    with pytest.raises(OkxDirectOutcomeUnknown):
        env.provider.submit_order(reservation, _req(), _grant(), Verifier(env.calls))
    env.venue.on(QUERY, {"code": "51603", "msg": "Order does not exist", "data": []})
    assert env.provider.drain_execution_events(10) == ()
    assert env.provider.watched_count == 1
    assert env.provider.counters["order_not_found"] == 1
    query = _requests(env.calls)[-1]
    assert query[1] == QUERY and query[2] == {"clOrdId": "bt0a1b2c3d4e5fs1", "instId": INST}
    env.clock.now += 1.0
    assert env.provider.drain_execution_events(10) == ()  # backed off: not yet due
    assert env.provider.counters["order_not_found"] == 1


def test_queries_per_drain_are_bounded(env):
    for index in range(6):
        _place(env, cid=f"c{index}", ord_id=str(100 + index))
    env.venue.on(QUERY, lambda params, _body: _ok(
        _order("live", "0", cid=f"c{int(params['ordId']) - 100}", ord_id=params["ordId"])
    ))
    before = len(_requests(env.calls))
    env.provider.drain_execution_events(100)
    assert len(_requests(env.calls)) - before == 4  # max_queries_per_drain


def test_watch_order_registers_a_restored_identity(env):
    env.provider.watch_order(_target(ord_id=ORD_ID), INST)
    env.venue.on(QUERY, _ok(_order("live", "0")))
    (event,) = env.provider.drain_execution_events(10)
    assert event.identity.fields["trading_day"] == "20261106"
    with pytest.raises(DirectWriteError):
        env.provider.watch_order(NativeOrderIdentity(ROUTE, None, {}), INST)


# ----------------------------------------------------------- account facts


def _script_account(venue):
    venue.on(POSITIONS, _ok(
        {"instType": "SWAP", "instId": INST, "posSide": "long", "pos": "3"},
        {"instType": "SWAP", "instId": INST, "posSide": "short", "pos": "1"},
        {"instType": "SWAP", "instId": "ETH-USDT-SWAP", "posSide": "net", "pos": "-5"},
        {"instType": "SWAP", "instId": "SOL-USDT-SWAP", "posSide": "net", "pos": "0"},
    ))
    venue.on(PENDING, _ok(_order("live", "0", cid="w1", ord_id="11")))
    venue.on(HISTORY, _ok(_order("canceled", "0", cid="h1", ord_id="12")))
    venue.on(FILLS, _ok(_fill("901", "1", "5001", ord_id="13")))
    venue.on(BALANCE, _ok({"details": [
        {"ccy": "BTC", "eq": "1"},
        {"ccy": "USDT", "eq": "1000.5", "availEq": "800", "frozenBal": "200", "upl": "3.5",
         "imr": "150"},
    ]}))


def test_account_facts_complete_observation(env):
    _script_account(env.venue)
    facts = env.provider.account_facts(trades=True, all_orders=True, timeout=30)
    assert facts.complete is True and facts.blockers == ()
    assert facts.exchange_name == ROUTE and facts.trading_day == "20261106"
    assert facts.session_generation == 1
    assert [(p.symbol, p.side, p.total) for p in facts.positions] == [
        (INST, "long", 3.0),
        (INST, "short", 1.0),
        ("ETH-USDT-SWAP", "net", -5.0),
    ]
    assert all(p.today is None and p.yesterday is None for p in facts.positions)
    (working,) = facts.active_orders
    assert working.identity.client_order_id == "w1" and working.status is DirectOrderStatus.ACCEPTED
    assert {e.exchange_order_id for e in facts.orders} == {"11", "12"}
    (trade,) = facts.trades
    assert trade.trade_id == "901" and trade.kind is DirectExecutionEventKind.TRADE
    assert facts.balance.currency == "USDT" and facts.balance.balance == 1000.5
    assert facts.balance.available == 800.0 and facts.balance.frozen == 200.0
    history = [c for c in _requests(env.calls) if c[1] == HISTORY][0]
    assert history[2]["begin"] == str(DAY_START_MS) and history[2]["instType"] == "SWAP"
    assert env.provider.watched_count == 1  # the working order is now watched


def test_account_facts_incomplete_sections_are_named(env):
    _script_account(env.venue)
    env.venue.on(FILLS, RequestTimeoutError(ROUTE, timeout=5))
    env.venue.on(BALANCE, _ok({"details": [{"ccy": "BTC", "eq": "1"}]}))
    facts = env.provider.account_facts(trades=True, all_orders=True)
    assert facts.complete is False
    assert facts.blockers == ("trades_query_incomplete", "balance_currency_absent")
    assert facts.trades is None and facts.balance is None
    assert facts.positions is not None


def test_account_facts_page_overflow_is_incomplete(env):
    _script_account(env.venue)
    page = [_order("live", "0", cid=f"p{index}", ord_id=str(1000 + index)) for index in range(100)]
    env.venue.on(PENDING, _ok(*page))
    facts = env.provider.account_facts(positions=False, balance=False)
    assert facts.complete is False and facts.blockers == ("orders_query_incomplete",)


def test_account_facts_without_session_is_incomplete_and_sends_nothing():
    calls: list = []
    feed = _feed(api_key=None)
    try:
        Venue(feed, calls)
        facts = OkxDirectWriteProvider(feed).account_facts()
        assert facts.complete is False and facts.blockers == ("session_unavailable",)
        assert calls == []
    finally:
        feed._http_client.close()


def test_account_reference_is_a_stable_hash_without_key_material(env):
    reference = env.provider.account_reference()
    assert reference == env.provider.account_reference()
    assert len(reference) == 16 and all(ch in "0123456789abcdef" for ch in reference)
    for secret in (API_KEY, API_SECRET, PASSPHRASE):
        assert secret not in reference
        assert secret[:6] not in reference
    other = _feed(api_key="unit-okx-key-other")
    try:
        assert OkxDirectWriteProvider(other).account_reference() != reference
    finally:
        other._http_client.close()
    assert API_KEY not in repr(env.provider.__dict__.get("_counters"))


# ------------------------------------------- fills after FILLED (demo regression)


def test_fills_follow_an_order_already_filled_at_its_first_poll(env):
    _place(env, position_side="long", position_mode="dual_side")
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    env.venue.on(FILLS, _ok(_fill("4585765484", "1", "5002", ts_offset=2), _fill("4585765483", "1", "5001")))
    filled, first, second = env.provider.drain_execution_events(10)
    assert filled.status is DirectOrderStatus.FILLED
    assert [t.trade_id for t in (first, second)] == ["4585765483", "4585765484"]
    assert all(t.offset == "open" and t.side == "buy" for t in (first, second))
    assert env.provider.watched_count == 0


def test_fills_lagging_behind_filled_keep_being_polled_beyond_the_old_grace(env):
    _place(env)
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    env.venue.on(FILLS, _ok())
    (filled,) = env.provider.drain_execution_events(10)
    assert filled.status is DirectOrderStatus.FILLED
    for _ in range(8):
        env.clock.now += 31.0
        assert env.provider.drain_execution_events(10) == ()
    assert env.provider.watched_count == 1
    assert len([c for c in _requests(env.calls) if c[1] == QUERY]) == 1
    env.clock.now += 31.0
    env.venue.on(FILLS, _ok(_fill("901", "2", "5001")))
    (trade,) = env.provider.drain_execution_events(10)
    assert trade.trade_id == "901" and env.provider.watched_count == 0


def test_fill_rows_are_attributed_by_the_request_scope(env):
    _place(env)
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    bare = {k: v for k, v in _fill("901", "1", "5001").items() if k not in ("instId", "ordId")}
    foreign = dict(_fill("902", "1", "5002"), ordId="777")
    env.venue.on(FILLS, _ok(bare, foreign))
    _filled, trade = env.provider.drain_execution_events(10)
    assert trade.trade_id == "901" and trade.symbol == INST and trade.exchange_order_id == ORD_ID
    assert env.provider.watched_count == 1  # one contract still owed


@pytest.mark.parametrize(
    "failure,reason",
    [
        ({"code": "50011", "msg": "Too Many Requests", "data": []}, "50011"),
        (RequestTimeoutError(ROUTE, timeout=3), "RequestTimeoutError"),
    ],
)
def test_fill_query_failures_are_counted_with_a_finite_reason(env, failure, reason):
    _place(env)
    env.venue.on(QUERY, _ok(_order("filled", "2")))
    env.venue.on(FILLS, failure)
    env.provider.drain_execution_events(10)
    assert env.provider.counters["fills_query_failed"] == 1
    assert env.provider.counters[f"fills_query_failed:{reason}"] == 1
    assert env.provider.watched_count == 1


def test_terminal_order_outside_the_fill_window_is_released_after_grace(env):
    env.provider.watch_order(_target(ord_id=ORD_ID), INST)
    old = dict(_order("filled", "2"), cTime=str(DAY_START_MS - 4 * 86_400_000))
    env.venue.on(QUERY, _ok(old))
    env.venue.on(FILLS, _ok())
    env.provider.drain_execution_events(10)
    env.clock.now += 61.0
    env.provider.drain_execution_events(10)
    assert env.provider.watched_count == 0
    assert env.provider.counters["fills_incomplete_outside_window"] == 1


def test_account_facts_accepts_a_symbols_scope_and_reads_account_wide(env):
    _script_account(env.venue)
    scoped = env.provider.account_facts(symbols=["ETH-USDT-SWAP"], all_orders=True, trades=True)
    assert scoped.complete is True
    assert [p.symbol for p in scoped.positions] == [INST, INST, "ETH-USDT-SWAP"]
    pending = [c for c in _requests(env.calls) if c[1] == PENDING][0]
    assert "instId" not in pending[2]


# -------------------------------------------------------------- venue clock


class Ns:
    def __init__(self):
        self.value = 1_794_020_400_000_000_000

    def __call__(self):
        self.value += 5_000_000
        return self.value


def test_server_time_observation_is_bracketed_cached_and_fails_closed():
    calls: list = []
    feed = _feed()
    try:
        venue = Venue(feed, calls)
        clock, ns = Clock(), Ns()
        provider = OkxDirectWriteProvider(feed, clock=clock, wall_clock=lambda: WALL, time_ns=ns)
        venue.on(SERVER_TIME, _ok({"ts": "1794020400123"}))
        observation = provider.server_time_observation()
        assert observation == {
            "venue_epoch_ms": 1794020400123,
            "local_sent_ns": 1_794_020_400_005_000_000,
            "local_received_ns": 1_794_020_400_010_000_000,
            "granularity_ms": 1,
        }
        assert feed.get_header("k", "s", "t", "p")["x-simulated-trading"] == "1"  # demo header
        clock.now += 59.0
        assert provider.server_time_observation() == observation
        assert len(_requests(calls)) == 1
        clock.now += 2.0
        venue.on(SERVER_TIME, RequestTimeoutError(ROUTE, timeout=3))
        assert provider.server_time_observation() is None
        clock.now += 1.0
        assert provider.server_time_observation() is None
        assert len(_requests(calls)) == 2
        clock.now += 5.0
        for bad in (_ok({"ts": "abc"}), _ok({"ts": "12"}), _ok(), {"code": "50001", "data": []}):
            venue.on(SERVER_TIME, bad)
            assert provider.server_time_observation() is None
            clock.now += 5.0
        venue.on(SERVER_TIME, _ok({"ts": "1794020460000"}))
        assert provider.server_time_observation()["venue_epoch_ms"] == 1794020460000
    finally:
        feed._http_client.close()


def test_server_time_local_stamps_default_to_the_wall_clock():
    calls: list = []
    feed = _feed()
    try:
        venue = Venue(feed, calls)
        venue.on(SERVER_TIME, lambda *_args: _ok({"ts": str(int(time.time() * 1000))}))
        before = time.time_ns()
        observation = OkxDirectWriteProvider(feed).server_time_observation()
        after = time.time_ns()
        assert before <= observation["local_sent_ns"] <= observation["local_received_ns"] <= after
    finally:
        feed._http_client.close()
