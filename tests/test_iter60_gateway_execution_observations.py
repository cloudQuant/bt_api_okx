"""Iteration 60: OKX SWAP Demo Gateway account provider (fake transport only).

Covers the read-only account snapshot (``connect``/``read_account``/``close``)
and the execution capability: per-fill rows of ``/api/v5/trade/fills`` and
order rows of ``orders-pending``/``orders-history``/``order``, signed GETs of
the fixed Demo origin. Evidence: UNIT/FAKE; no network, account or venue.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import re
from urllib.parse import parse_qs, urlsplit

import pytest
from bt_api_base.account_protocol import AccountKey
from bt_api_base.execution_row_observation_protocol import (
    AccountExecutionOrderObservation,
    AccountExecutionTradeObservation,
    execution_observation_fact_digest,
    execution_observation_fact_id,
)

import bt_api_okx.gateway_execution_observations as execution_module
from bt_api_okx.gateway_account_provider import (
    ACCOUNT_RESOURCE,
    SWAP_CROSS_RESOURCE,
    OkxSwapApiCredentials,
    OkxSwapDemoAccountSessionProvider,
    OkxSwapExecutionScope,
    OkxSwapProviderError,
    make_okx_swap_demo_provider,
)

SECRET = "fixture-api-secret"
NOW_MS = 1_800_000_000_000
GEN = "generation-01"
INST = "BTC-USDT-SWAP"


class FakeIssuer:
    """Stand-in for the SDK's durable issuer: keyed digest, stable across instances."""

    def __init__(self, key: bytes = b"k" * 32) -> None:
        self.key = key

    def _digest(self, kind, *parts):
        material = json.dumps([kind, *parts])
        return hmac.new(self.key, material.encode(), hashlib.sha256).hexdigest()

    def issue_order_observation_id(self, provider_name, environment, account_ref, identity):
        return "sdk-order-observation-v1-" + self._digest(
            "order", provider_name, environment, account_ref, identity
        )

    def issue_trade_observation_id(self, provider_name, environment, account_ref, identity):
        return "sdk-trade-observation-v1-" + self._digest(
            "trade", provider_name, environment, account_ref, identity
        )


def order_row(ord_id, *, inst=INST, state="filled", sz="2", acc=None, client="client1",
              side="buy", pos_side="long", px="40000.0", c_time=NOW_MS - 60_000,
              td_mode="cross", ord_type="limit", inst_type="SWAP"):
    if acc is None:
        acc = sz if state == "filled" else "0"
    return {
        "instType": inst_type, "instId": inst, "ordId": str(ord_id), "clOrdId": client,
        "side": side, "posSide": pos_side, "ordType": ord_type, "state": state, "sz": sz,
        "accFillSz": acc, "px": px, "avgPx": px, "cTime": str(c_time),
        "uTime": str(c_time + 1_000), "tdMode": td_mode, "reduceOnly": "false",
    }


def fill_row(bill_id, ord_id, *, inst=INST, trade_id=None, sz="1", px="40000.1",
             fee="-0.02", fee_ccy="USDT", side="buy", pos_side="long", ts=NOW_MS - 50_000,
             inst_type="SWAP"):
    row = {
        "instType": inst_type, "instId": inst, "tradeId": str(trade_id or bill_id + 100),
        "ordId": str(ord_id), "clOrdId": "", "billId": str(bill_id), "fillPx": px,
        "fillSz": sz, "side": side, "posSide": pos_side, "execType": "T",
        "fee": fee, "feeCcy": fee_ccy, "ts": str(ts), "fillTime": str(ts),
    }
    if fee is None:
        del row["fee"]
    return row


class FakeOkxVenue:
    """A deterministic OKX Demo venue answering only signed v5 read routes."""

    def __init__(self, *, clock=None, acct_lv="2"):
        self.clock = clock
        self.acct_lv = acct_lv
        self.orders: dict[str, dict] = {}
        self.fills: list[dict] = []
        self.positions: list[dict] = []
        self.calls: list[tuple[str, dict[str, str]]] = []
        self.fill_page_hook = None

    def now_ms(self):
        return int(self.clock.wall * 1000) if self.clock else NOW_MS

    def add_order(self, row):
        self.orders[row["ordId"]] = dict(row)

    def __call__(self, method, url, headers, timeout, max_bytes):
        assert method == "GET" and timeout > 0
        parsed = urlsplit(url)
        assert parsed.scheme == "https" and parsed.netloc == "www.okx.com"
        assert headers["x-simulated-trading"] == "1"
        params = {key: values[0] for key, values in parse_qs(parsed.query).items()}
        path = parsed.path
        if path != "/api/v5/public/time":
            request_path = path + ("?" + parsed.query if parsed.query else "")
            message = headers["OK-ACCESS-TIMESTAMP"] + "GET" + request_path
            expected = base64.b64encode(
                hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).digest()
            ).decode()
            assert hmac.compare_digest(headers["OK-ACCESS-SIGN"], expected)
            assert headers["OK-ACCESS-KEY"] == "fixture-api-key"
            assert headers["OK-ACCESS-PASSPHRASE"] == "fixture-passphrase"
            assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z", headers["OK-ACCESS-TIMESTAMP"])
        else:
            assert "OK-ACCESS-KEY" not in headers
        self.calls.append((path, params))
        return json.dumps({"code": "0", "msg": "", "data": self._answer(path, params)}).encode()

    @staticmethod
    def _page(rows, params, id_field):
        rows = sorted(rows, key=lambda row: int(row[id_field]), reverse=True)
        if "after" in params:
            rows = [row for row in rows if int(row[id_field]) < int(params["after"])]
        return [dict(row) for row in rows[: int(params.get("limit", "100"))]]

    def _answer(self, path, params):
        if path == "/api/v5/public/time":
            return [{"ts": str(self.now_ms())}]
        if path == "/api/v5/account/config":
            return [{"acctLv": self.acct_lv, "posMode": "long_short_mode", "uid": "1"}]
        if path == "/api/v5/account/balance":
            return [{"details": [{"ccy": "USDT", "eq": "100.50", "availBal": "90", "frozenBal": "10.0"}]}]
        if path == "/api/v5/account/positions":
            return [dict(row) for row in self.positions]
        selected = [
            row for row in self.orders.values()
            if row["instType"] == params["instType"] and params.get("instId", row["instId"]) == row["instId"]
        ] if "instType" in params else []
        if path == "/api/v5/trade/orders-pending":
            rows = [row for row in selected if row["state"] in {"live", "partially_filled"}]
            return self._page(rows, params, "ordId")
        if path == "/api/v5/trade/orders-history":
            rows = [
                row for row in selected
                if row["state"] in {"filled", "canceled", "mmp_canceled"}
                and int(row["cTime"]) >= int(params["begin"])
            ]
            return self._page(rows, params, "ordId")
        if path == "/api/v5/trade/fills":
            rows = [row for row in self.fills if row["instId"] == params["instId"]]
            if "begin" in params:
                rows = [row for row in rows if int(row["ts"]) >= int(params["begin"])]
            page = self._page(rows, params, "billId")
            return self.fill_page_hook(page) if self.fill_page_hook else page
        if path == "/api/v5/trade/order":
            return [dict(self.orders[params["ordId"]])]
        raise AssertionError(f"unexpected route {path}")


def account_key():
    return AccountKey(provider="okx", venue="OKX", environment="demo", account_id="configured-account")


class Clock:
    def __init__(self, wall=NOW_MS / 1000, mono=10.0):
        self.wall = wall
        self.mono = mono

    def advance(self, seconds):
        self.wall += seconds
        self.mono += seconds


def credentials():
    return OkxSwapApiCredentials("fixture-api-key", SECRET, "fixture-passphrase")


def scope(issuer, inst_ids=(INST,), lookback=3_600, interval=0.0):
    return OkxSwapExecutionScope(
        inst_ids=inst_ids, lookback_seconds=lookback, observation_issuer=issuer,
        poll_interval_seconds=interval,
    )


def provider(venue, issuer=None, *, clock=None, generation=GEN, **scope_kwargs):
    clock = clock or Clock()
    built = OkxSwapDemoAccountSessionProvider(
        credentials(),
        transport=venue,
        wall_clock=lambda: clock.wall,
        monotonic_clock=lambda: clock.mono,
        execution=None if issuer is None else scope(issuer, **scope_kwargs),
    )
    built.connect(account_key=account_key(), generation=generation, timeout=2.0)
    return built


def read(built, limit=1000, generation=GEN):
    return built.read_execution_observations(generation=generation, timeout=2.0, limit=limit)


def facts(items):
    return [(execution_observation_fact_id(i), execution_observation_fact_digest(i)) for i in items]


def basic_venue(clock=None):
    venue = FakeOkxVenue(clock=clock)
    venue.add_order(order_row(1001, sz="1", client="s1234abcd-0001"))
    venue.fills.append(fill_row(9001, 1001))
    return venue


# -- account snapshot ----------------------------------------------------------------


def test_read_account_projects_balances_cross_positions_and_open_orders():
    venue = FakeOkxVenue()
    venue.positions = [
        {"instType": "SWAP", "instId": INST, "mgnMode": "cross", "posSide": "long", "pos": "3"},
        {"instType": "SWAP", "instId": "ETH-USDT-SWAP", "mgnMode": "isolated", "posSide": "short", "pos": "1"},
    ]
    venue.add_order(order_row(1001, state="partially_filled", sz="3", acc="1"))
    venue.add_order(order_row(1002, state="live", td_mode="isolated"))
    built = provider(venue)
    observation = built.read_account(generation=GEN, timeout=2.0)
    assert observation.coverage == (ACCOUNT_RESOURCE, SWAP_CROSS_RESOURCE)
    assert [(b.currency, b.total, b.available, b.locked) for b in observation.balances] == [
        ("USDT", "100.5", "90", "10")
    ]
    assert [(p.instrument.instrument_id, p.side, p.quantity, p.qty_unit) for p in observation.positions] == [
        (INST, "long", "3", "contract")
    ]
    assert [(o.order_id, o.status, o.filled_quantity) for o in observation.open_orders] == [
        ("1001", "partially_filled", "1")
    ]
    assert observation.open_orders_complete is False  # algo orders are not read
    assert {path for path, _ in venue.calls} == {
        "/api/v5/public/time", "/api/v5/account/config", "/api/v5/account/balance",
        "/api/v5/account/positions", "/api/v5/trade/orders-pending",
    }


def test_account_mode_identity_and_credentials_fail_closed():
    with pytest.raises(OkxSwapProviderError) as mode:
        provider(FakeOkxVenue(acct_lv="3")).read_account(generation=GEN, timeout=2.0)
    assert mode.value.code == "ACCOUNT_COVERAGE_UNSUPPORTED"
    venue = FakeOkxVenue()
    built = OkxSwapDemoAccountSessionProvider(credentials(), transport=venue)
    for key in (
        AccountKey("okx", "OKX", "live", "configured-account"),
        AccountKey("binance", "OKX", "demo", "configured-account"),
        AccountKey("okx", "OKX", "demo", "configured-account", "sub"),
    ):
        with pytest.raises(OkxSwapProviderError) as identity:
            built.connect(account_key=key, generation=GEN, timeout=2.0)
        assert identity.value.code == "INVALID_ACCOUNT_IDENTITY"
    assert venue.calls == []
    assert "fixture" not in repr(credentials()) + repr(built)
    with pytest.raises(OkxSwapProviderError) as bad:
        make_okx_swap_demo_provider("session", {"api_key": "a", "api_secret": "secret"})
    assert bad.value.code == "INVALID_CREDENTIALS" and "secret" not in str(bad.value)
    with pytest.raises(OkxSwapProviderError):
        OkxSwapDemoAccountSessionProvider(credentials(), environment="production")


# -- execution projection ------------------------------------------------------------


def test_fill_and_terminal_order_are_projected_from_documented_rows():
    venue, issuer = basic_venue(), FakeIssuer()
    built = provider(venue, issuer)
    items = read(built)
    assert [type(i) for i in items] == [AccountExecutionOrderObservation, AccountExecutionTradeObservation]
    order, fill = items[0].order, items[1].trade
    assert items[0].account_key == items[1].account_key == account_key()
    assert (order.status, order.quantity, order.filled_quantity, order.qty_unit) == ("filled", "1", "1", "contract")
    assert (order.client_order_id, order.intent_binding, order.order_type) == ("s1234abcd-0001", "verified", "limit")
    assert (order.position_effect, order.position_side, order.limit_price) == ("open", "long", "40000")
    assert order.resource == fill.resource == SWAP_CROSS_RESOURCE
    assert (fill.quantity, fill.price, fill.qty_unit) == ("1", "40000.1", "contract")
    assert fill.order_id == order.order_id and fill.traded_at_utc == "2027-01-15T07:59:10.000Z"
    assert (items[1].fee, items[1].fee_currency) == ("0.02", "USDT")  # -fee: charged
    assert re.fullmatch(r"sdk-order-observation-v1-[0-9a-f]{64}", order.order_id)
    assert re.fullmatch(r"sdk-trade-observation-v1-[0-9a-f]{64}", fill.trade_id)
    fills_calls = [p for path, p in venue.calls if path == "/api/v5/trade/fills"]
    assert fills_calls[0]["instType"] == "SWAP" and fills_calls[0]["instId"] == INST


def test_fee_charged_zero_absent_and_rebate():
    venue, issuer = FakeOkxVenue(), FakeIssuer()
    venue.add_order(order_row(1001, sz="4"))
    venue.fills += [
        fill_row(9001, 1001, fee="-0.0100"),
        fill_row(9002, 1001, fee="0"),
        fill_row(9003, 1001, fee=None),
        fill_row(9004, 1001, fee="0.005"),
    ]
    built = provider(venue, issuer)
    fills = [i for i in read(built) if type(i) is AccountExecutionTradeObservation]
    assert [(i.fee, i.fee_currency) for i in fills] == [
        ("0.01", "USDT"), ("0", "USDT"), (None, None), (None, None)
    ]
    assert built.execution_counters["EXECUTION_FEE_UNAVAILABLE"] == 1
    assert built.execution_counters["EXECUTION_FEE_REBATE_UNREPRESENTABLE"] == 1


def test_fills_never_come_from_order_quantities():
    venue, issuer = FakeOkxVenue(), FakeIssuer()
    venue.add_order(order_row(1001, state="partially_filled", sz="3", acc="2"))
    items = read(provider(venue, issuer))
    assert [i.order.status for i in items] == ["partially_filled"]


@pytest.mark.parametrize(
    ("state", "acc", "expected"),
    [("canceled", "0", "canceled"), ("mmp_canceled", "1", "partially_filled_canceled"), ("live", "0", "open")],
)
def test_order_state_mapping(state, acc, expected):
    venue = FakeOkxVenue()
    venue.add_order(order_row(1001, state=state, acc=acc, pos_side="net"))
    (item,) = read(provider(venue, FakeIssuer()))
    assert item.order.status == expected
    assert (item.order.position_effect, item.order.position_side) == ("unavailable", None)


# -- dedupe, order and paging ---------------------------------------------------------


def _many_fills_venue():
    venue = FakeOkxVenue()
    venue.add_order(order_row(1001, sz="5"))
    venue.add_order(order_row(1002, sz="2", side="sell", pos_side="long"))
    venue.fills += [fill_row(9000 + n, 1001, ts=NOW_MS - 40_000 + n) for n in range(5)]
    venue.fills += [fill_row(9100 + n, 1002, side="sell") for n in range(2)]
    return venue


def test_duplicate_and_out_of_order_pages_give_the_same_facts():
    ordered = read(provider(_many_fills_venue(), FakeIssuer()))
    venue = _many_fills_venue()

    def shuffle_and_duplicate(rows):
        rows = rows + [dict(rows[0]), dict(rows[2])]
        random.Random(3).shuffle(rows)
        return rows

    venue.fill_page_hook = shuffle_and_duplicate
    assert facts(read(provider(venue, FakeIssuer()))) == facts(ordered)
    assert len(ordered) == 2 + 7


def test_backward_cursor_paging_delivers_each_fill_once(monkeypatch):
    monkeypatch.setattr(execution_module, "PAGE_LIMIT", 2)
    venue, issuer = FakeOkxVenue(), FakeIssuer()
    venue.add_order(order_row(1001, state="partially_filled", sz="20", acc="3"))
    venue.fills += [fill_row(9001 + n, 1001) for n in range(3)]
    built = provider(venue, issuer)
    delivered = []
    for step in range(3):
        if step == 1:
            venue.fills += [fill_row(9004 + n, 1001, ts=NOW_MS + n) for n in range(5)]
        items = read(built)
        delivered += [i for i in items if type(i) is AccountExecutionTradeObservation]
        if items:
            built.confirm_execution_observations(generation=GEN, count=len(items))
    afters = [p.get("after") for path, p in venue.calls if path == "/api/v5/trade/fills"]
    assert afters[:2] == [None, "9002"]  # initial window, newest first, then older
    assert len({i.trade.trade_id for i in delivered}) == len(delivered) == 8


def test_a_truncated_initial_window_and_backlog_fail_closed(monkeypatch):
    monkeypatch.setattr(execution_module, "PAGE_LIMIT", 2)
    monkeypatch.setattr(execution_module, "MAX_HISTORY_PAGES", 2)
    venue = FakeOkxVenue()
    venue.add_order(order_row(1001, state="partially_filled", sz="20", acc="4"))
    venue.fills += [fill_row(9001 + n, 1001) for n in range(4)]
    with pytest.raises(OkxSwapProviderError) as error:
        read(provider(venue, FakeIssuer()))
    assert error.value.code == "EXECUTION_LOOKBACK_TRUNCATED"


def test_malformed_rows_fail_closed_and_lose_nothing():
    venue = basic_venue()
    venue.fills[0]["fillSz"] = "1e-3"
    built = provider(venue, FakeIssuer())
    with pytest.raises(OkxSwapProviderError) as error:
        read(built)
    assert error.value.code == "EXECUTION_ROW_INVALID"
    venue.fills[0]["fillSz"] = "1"
    assert len(read(built)) == 2


# -- generations, confirm, restart ----------------------------------------------------


def test_stale_generation_closed_session_and_one_shot_reconnect_are_refused():
    built = provider(basic_venue(), FakeIssuer())
    read(built)
    for call in (
        lambda: read(built, generation="generation-00"),
        lambda: built.confirm_execution_observations(generation="generation-00", count=1),
    ):
        with pytest.raises(OkxSwapProviderError) as error:
            call()
        assert error.value.code == "PROVIDER_GENERATION_MISMATCH"
    built.close()
    with pytest.raises(OkxSwapProviderError) as closed:
        read(built)
    assert closed.value.code == "PROVIDER_SESSION_CLOSED"
    with pytest.raises(OkxSwapProviderError) as again:
        built.connect(account_key=account_key(), generation="generation-02", timeout=2.0)
    assert again.value.code == "PROVIDER_SESSION_CLOSED"


def test_unconfirmed_items_are_redelivered_and_partial_confirm_keeps_the_rest():
    venue = _many_fills_venue()
    built = provider(venue, FakeIssuer())
    first = read(built, limit=4)
    calls = len(venue.calls)
    assert facts(read(built, limit=4)) == facts(first) and len(venue.calls) == calls
    with pytest.raises(OkxSwapProviderError) as too_many:
        built.confirm_execution_observations(generation=GEN, count=5)
    assert too_many.value.code == "EXECUTION_CONFIRM_INVALID"
    built.confirm_execution_observations(generation=GEN, count=3)
    rest = read(built)
    assert facts(rest)[0] == facts(first)[3] and len(rest) == 6
    built.confirm_execution_observations(generation=GEN, count=6)
    assert read(built) == ()


def test_reconnect_with_a_new_generation_redelivers_unconfirmed_facts():
    venue, issuer = basic_venue(), FakeIssuer()
    old = provider(venue, issuer, generation="generation-01")
    unconfirmed = read(old, generation="generation-01")
    old.close()
    new = provider(venue, issuer, generation="generation-02")
    with pytest.raises(OkxSwapProviderError) as stale:
        new.confirm_execution_observations(generation="generation-01", count=1)
    assert stale.value.code == "PROVIDER_GENERATION_MISMATCH"
    with pytest.raises(OkxSwapProviderError) as fresh:
        new.confirm_execution_observations(generation="generation-02", count=1)
    assert fresh.value.code == "EXECUTION_CONFIRM_INVALID"
    assert facts(read(new, generation="generation-02")) == facts(unconfirmed)


def test_restart_reproduces_identical_facts_and_reports_fee_changes_as_is():
    venue = basic_venue()
    first = read(provider(venue, FakeIssuer()))
    assert facts(read(provider(venue, FakeIssuer()))) == facts(first)
    venue.fills[0]["fee"] = "-0.03"
    venue.fills[0]["billId"] = "9011"  # re-reported under a new bill: same fill identity
    corrected = read(provider(venue, FakeIssuer()))
    assert facts(corrected)[0] == facts(first)[0]
    assert corrected[1].trade.trade_id == first[1].trade.trade_id and corrected[1].fee == "0.03"
    venue.fills[0]["fee"] = "-0.01"
    lowered = read(provider(venue, FakeIssuer()))
    assert lowered[1].fee == "0.01" and lowered[1].trade.trade_id == first[1].trade.trade_id


# -- scope -------------------------------------------------------------------------------


def test_rows_outside_the_scope_are_refused_and_counted():
    venue = basic_venue()
    venue.add_order(order_row(1002, td_mode="isolated"))
    venue.fills.append(fill_row(9002, 1002))
    venue.fill_page_hook = lambda rows: rows + [
        fill_row(9003, 1003, inst="ETH-USDT-SWAP"), fill_row(9004, 1004, inst_type="FUTURES")
    ]
    built = provider(venue, FakeIssuer())
    items = read(built)
    assert len(items) == 2 and all(i.account_key == account_key() for i in items)
    counters = built.execution_counters
    assert counters["EXECUTION_ROW_INSTRUMENT_OUT_OF_SCOPE"] == 1
    assert counters["EXECUTION_ROW_PRODUCT_OUT_OF_SCOPE"] == 1
    assert counters["EXECUTION_ROW_MARGIN_POOL_OUT_OF_SCOPE"] == 2  # the order and its fill


def test_configuration_fails_closed():
    issuer = FakeIssuer()
    for bad in (dict(inst_ids=()), dict(inst_ids=("BTC-USDT",)), dict(inst_ids=("BTC-USDT-250328",)),
                dict(inst_ids=(INST, INST)), dict(lookback=10), dict(lookback=4 * 86_400),
                dict(interval=-1.0)):
        with pytest.raises(OkxSwapProviderError) as invalid:
            scope(issuer, **bad)
        assert invalid.value.code == "INVALID_EXECUTION_SCOPE"
    with pytest.raises(OkxSwapProviderError):
        scope(object())
    with pytest.raises(OkxSwapProviderError) as unconfigured:
        read(provider(basic_venue()))
    assert unconfigured.value.code == "EXECUTION_OBSERVATIONS_NOT_CONFIGURED"

    class EchoIssuer(FakeIssuer):
        def issue_trade_observation_id(self, provider_name, environment, account_ref, identity):
            return identity

    with pytest.raises(OkxSwapProviderError) as untrusted:
        read(provider(basic_venue(), EchoIssuer()))
    assert untrusted.value.code == "EXECUTION_IDENTITY_UNAVAILABLE"
    with pytest.raises(OkxSwapProviderError) as bad_limit:
        read(provider(basic_venue(), FakeIssuer()), limit=0)
    assert bad_limit.value.code == "INVALID_LIMIT"


# -- order routes and terminal detection ------------------------------------------------


def test_a_fill_of_an_order_outside_the_window_queues_its_order_first():
    venue = FakeOkxVenue()
    venue.add_order(order_row(1001, sz="1", c_time=NOW_MS - 10 * 3_600_000))
    venue.fills.append(fill_row(9001, 1001))
    items = read(provider(venue, FakeIssuer()))
    assert [type(i) for i in items] == [AccountExecutionOrderObservation, AccountExecutionTradeObservation]
    assert ("/api/v5/trade/order", {"instId": INST, "ordId": "1001"}) in venue.calls


def test_an_open_order_that_terminates_later_is_queried_and_reported():
    venue = FakeOkxVenue()
    venue.add_order(order_row(1001, state="live", c_time=NOW_MS - 10 * 3_600_000))
    built = provider(venue, FakeIssuer())
    assert [i.order.status for i in read(built)] == ["open"]
    built.confirm_execution_observations(generation=GEN, count=1)
    assert read(built) == ()
    venue.orders["1001"]["state"] = "canceled"
    assert [i.order.status for i in read(built)] == ["canceled"]
