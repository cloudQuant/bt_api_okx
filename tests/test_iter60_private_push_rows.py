"""Iteration 60: OKX private pushes keep every row (no silent data loss).

An OKX push carries rows in ``data``: an ``orders``/``positions`` subscription by
``instType`` batches several instruments in one message and its ``arg`` has no
``instId``. The handlers used to forward ``data[0]`` only (and read
``arg["instId"]``), dropping later order updates, fills and position rows.
Offline fakes only.
"""

from __future__ import annotations

import queue

from bt_api_okx.feeds.live_okx.market_wss_base import OkxWssData


def _wss():
    wss = object.__new__(OkxWssData)
    wss.data_queue = queue.Queue()
    wss.asset_type = "SWAP"
    return wss


def _drain(wss):
    items = []
    while not wss.data_queue.empty():
        items.append(wss.data_queue.get_nowait())
    return items


def _order(inst, ord_id):
    return {"instId": inst, "ordId": ord_id, "clOrdId": "c" + ord_id, "state": "filled",
            "side": "buy", "sz": "1", "accFillSz": "1", "avgPx": "100", "px": "100",
            "ordType": "limit", "fillSz": "1", "fillPx": "100", "tradeId": "t" + ord_id,
            "fee": "-0.01", "feeCcy": "USDT", "uTime": "1700000000000", "cTime": "1700000000000"}


def test_every_order_row_of_an_insttype_push_is_forwarded():
    wss = _wss()
    content = {"arg": {"channel": "orders", "instType": "SWAP", "uid": "u"},
               "data": [_order("BTC-USDT-SWAP", "1"), _order("ETH-USDT-SWAP", "2")]}
    wss.push_order(content)
    items = _drain(wss)
    assert len(items) == 2
    assert [item.symbol_name for item in items] == ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]


def test_every_position_row_of_a_snapshot_push_is_forwarded():
    wss = _wss()
    rows = [{"instId": name, "pos": "1", "posSide": "net", "avgPx": "100", "uTime": "1"}
            for name in ("BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP")]
    wss.push_position({"arg": {"channel": "positions", "instType": "SWAP"}, "data": rows})
    assert [item.symbol_name for item in _drain(wss)] == [
        "BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"
    ]


def test_every_fill_and_trade_row_is_forwarded_and_empty_pushes_are_harmless():
    wss = _wss()
    fills = [{"instId": "BTC-USDT-SWAP", "tradeId": str(i), "fillPx": "1", "fillSz": "1",
              "side": "buy", "ordId": "o", "ts": "1"} for i in range(3)]
    wss.push_fills({"arg": {"channel": "fills"}, "data": fills})
    trades = [{"instId": "BTC-USDT-SWAP", "tradeId": str(i), "px": "1", "sz": "1",
               "side": "buy", "ts": "1"} for i in range(2)]
    wss.push_trade({"arg": {"channel": "trades", "instId": "BTC-USDT-SWAP"}, "data": trades})
    assert len(_drain(wss)) == 5
    for handler in (wss.push_order, wss.push_position, wss.push_fills, wss.push_trade,
                    wss.push_account):
        handler({"arg": {"channel": "x"}, "data": []})
    assert _drain(wss) == []
