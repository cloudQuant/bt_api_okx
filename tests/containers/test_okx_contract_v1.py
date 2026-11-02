"""OKX containers against Base container contract v1 (iteration 60, 60.04/60.05).

Every standard Base getter answers on an OKX container (unknown facts are
None, not NotImplementedError), readers cannot mutate a published container,
and ticker volume semantics are declared.
"""

from __future__ import annotations

import pytest
from bt_api_base.containers.auto_init_mixin import container_fingerprint
from bt_api_base.containers.bars.bar import BarData
from bt_api_base.containers.orders.order import OrderData
from bt_api_base.containers.positions.position import PositionData
from bt_api_base.containers.semantics import VOLUME_LAST_TRADE, normalize_position_side
from bt_api_base.containers.tickers.ticker import TickerData
from bt_api_base.containers.trades.trade import TradeData
from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.orders.okx_order import OkxOrderData
from bt_api_okx.containers.positions.okx_position import OkxPositionData
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.containers.trades.okx_market_trade import OkxMarketTradeData

TICKER = {
    "instType": "SWAP",
    "instId": "BTC-USDT-SWAP",
    "last": "65000.1",
    "lastSz": "0.1",
    "askPx": "65000.2",
    "askSz": "11",
    "bidPx": "65000.0",
    "bidSz": "5",
    "open24h": "64000",
    "high24h": "66000",
    "low24h": "63000",
    "volCcy24h": "2222",
    "vol24h": "2222",
    "ts": "1597026383085",
}
BAR = ["1597026383085", "64000", "66000", "63000", "65000", "10", "650000", "650000", "1"]
ORDER = {
    "instType": "SWAP",
    "instId": "BTC-USDT-SWAP",
    "ordId": "312269865356374016",
    "clOrdId": "b1",
    "px": "65000",
    "sz": "2",
    "ordType": "limit",
    "side": "buy",
    "posSide": "long",
    "tdMode": "cross",
    "accFillSz": "1",
    "avgPx": "65000",
    "state": "partially_filled",
    "lever": "10",
    "reduceOnly": "false",
    "uTime": "1597026383085",
    "cTime": "1597026383085",
}
POSITION = {
    "instType": "SWAP",
    "instId": "BTC-USDT-SWAP",
    "posId": "307173036051017730",
    "posSide": "long",
    "pos": "2",
    "avgPx": "65000",
    "markPx": "65100",
    "liqPx": "60000",
    "lever": "10",
    "mgnMode": "cross",
    "imr": "13000",
    "mmr": "650",
    "upl": "200",
    "realizedPnl": "5",
    "fee": "-1.5",
    "uTime": "1705315800000",
}
MARKET_TRADE = {
    "instId": "BTC-USDT-SWAP",
    "tradeId": "242720720",
    "px": "65000",
    "sz": "0.1",
    "side": "buy",
    "ts": "1597026383085",
}

CASES = [
    (TickerData, lambda: OkxTickerData(TICKER, "BTC-USDT-SWAP", "SWAP", True)),
    (BarData, lambda: OkxBarData(BAR, "BTC-USDT-SWAP", "SWAP", True)),
    (OrderData, lambda: OkxOrderData(ORDER, "BTC-USDT-SWAP", "SWAP", True)),
    (TradeData, lambda: OkxMarketTradeData(MARKET_TRADE, "BTC-USDT-SWAP", "SWAP", True)),
    (PositionData, lambda: OkxPositionData(POSITION, "BTC-USDT-SWAP", "SWAP", True)),
]
IDS = [case[0].__name__ for case in CASES]


def _standard_getters(base):
    return sorted(
        name
        for name, value in vars(base).items()
        if name.startswith("get_") and callable(value) and name != "get_all_data"
    )


@pytest.mark.parametrize("base, factory", CASES, ids=IDS)
def test_every_standard_getter_answers(base, factory):
    container = factory()
    for name in _standard_getters(base):
        getattr(container, name)()


@pytest.mark.parametrize("base, factory", CASES, ids=IDS)
def test_reading_a_frozen_container_does_not_mutate_it(base, factory):
    container = factory().freeze()
    container.get_all_data()  # first call may memoize its dict
    before = container_fingerprint(container)
    for name in _standard_getters(base):
        getattr(container, name)()
    container.get_all_data()
    assert container_fingerprint(container) == before


@pytest.mark.parametrize("base, factory", CASES, ids=IDS)
def test_get_all_data_result_cannot_corrupt_shared_state(base, factory):
    container = factory().freeze()
    first = container.get_all_data()
    snapshot = dict(first)
    first["injected_by_consumer"] = True
    for key in list(snapshot):
        first[key] = "corrupted"
    assert container.get_all_data() == snapshot


def test_ticker_volume_semantics_is_last_trade():
    ticker = OkxTickerData(TICKER, "BTC-USDT-SWAP", "SWAP", True)
    assert ticker.get_volume_semantics() == VOLUME_LAST_TRADE
    assert ticker.get_last_volume() == 0.1
    # vol24h is a rolling window, not a session cumulative: stays unknown.
    assert ticker.get_cumulative_volume() is None
    assert ticker.get_delta_volume() is None
    assert ticker.get_execution_eligible() is None


def test_bar_status_marks_confirmed_bar():
    assert OkxBarData(BAR, "BTC-USDT-SWAP", "SWAP", True).get_bar_status() is True
    open_bar = BAR[:-1] + ["0"]
    assert OkxBarData(open_bar, "BTC-USDT-SWAP", "SWAP", True).get_bar_status() is False


def test_position_side_normalizes():
    position = OkxPositionData(POSITION, "BTC-USDT-SWAP", "SWAP", True)
    assert normalize_position_side(position.get_position_side()) == "long"


def test_market_trade_symbol():
    trade = OkxMarketTradeData(MARKET_TRADE, "BTC-USDT-SWAP", "SWAP", True)
    assert trade.get_symbol_name() == "BTC-USDT-SWAP"
