from __future__ import annotations

from bt_api_okx.feeds.live_okx.mixins.trade_mixin import TradeMixin
from bt_api_okx.gateway import adapter as adapter_module


class _FakeFeed:
    def __init__(self) -> None:
        self.cancel_calls: list[dict[str, object]] = []

    def cancel_order(self, symbol=None, order_id=None, **kwargs):
        self.cancel_calls.append(
            {"symbol": symbol, "order_id": order_id, "kwargs": dict(kwargs)}
        )
        return {"status": "ok", "order_id": order_id}


def test_cancel_order_accepts_gateway_order_ref_and_instrument_alias(monkeypatch) -> None:
    feed = _FakeFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter._ensure_account_stream = lambda: None

    result = adapter.cancel_order(
        {"instrument": "BTC-USDT-SWAP", "order_ref": "okx-987"}
    )

    assert result == {"status": "ok", "order_id": "okx-987"}
    assert feed.cancel_calls == [
        {"symbol": "BTC-USDT-SWAP", "order_id": "okx-987", "kwargs": {}}
    ]


class _FakeResult:
    def __init__(self, data, input_data=None):
        self._data = data
        self._input_data = data if input_data is None else input_data

    def get_data(self):
        return self._data

    def get_input_data(self):
        return self._input_data


class _OrderParams:
    symbol_leverage_dict = {"BTC-USDT-SWAP": 100}

    @staticmethod
    def get_symbol(symbol):
        return symbol

    @staticmethod
    def get_rest_path(_request_type):
        return "/api/v5/trade/order"


class _NoopLogger:
    @staticmethod
    def warning(_message):
        return None


class _GatewayOrderFeed(_FakeFeed, TradeMixin):
    exchange_name = "OKX"

    def __init__(self, asset_type="SWAP") -> None:
        super().__init__()
        self.asset_type = asset_type
        self._params = _OrderParams()
        self.request_logger = _NoopLogger()
        self.last_body = None

    def request(self, path, body=None, extra_data=None):
        self.last_body = dict(body or {})
        return _FakeResult([{"ordId": "okx-order-1", "path": path}])


def test_gateway_place_order_sends_okx_contract_size_without_legacy_multiplier(monkeypatch) -> None:
    feed = _GatewayOrderFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter._ensure_account_stream = lambda: None

    result = adapter.place_order(
        {
            "symbol": "BTC-USDT-SWAP",
            "size": 1,
            "price": 60000,
            "side": "buy",
            "order_type": "limit",
        }
    )

    assert result["ordId"] == "okx-order-1"
    assert feed.last_body["instId"] == "BTC-USDT-SWAP"
    assert float(feed.last_body["sz"]) == 1.0
    assert feed.last_body["px"] == "60000.0"


def test_gateway_market_order_omits_okx_price_field(monkeypatch) -> None:
    feed = _GatewayOrderFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter._ensure_account_stream = lambda: None

    adapter.place_order(
        {
            "symbol": "BTC-USDT-SWAP",
            "size": 2,
            "price": 0,
            "side": "sell",
            "order_type": "market",
        }
    )

    assert float(feed.last_body["sz"]) == 2.0
    assert feed.last_body["ordType"] == "market"
    assert "px" not in feed.last_body


def test_gateway_close_order_forwards_position_side_and_reduce_only(monkeypatch) -> None:
    feed = _GatewayOrderFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter._ensure_account_stream = lambda: None

    adapter.place_order(
        {
            "symbol": "BTC-USDT-SWAP",
            "size": 3,
            "price": 0,
            "side": "sell",
            "order_type": "market",
            "offset": "close",
            "position_side": "long",
            "reduce_only": True,
            "td_mode": "isolated",
        }
    )

    assert feed.last_body["side"] == "sell"
    assert feed.last_body["ordType"] == "market"
    assert feed.last_body["posSide"] == "long"
    assert feed.last_body["reduceOnly"] == "true"
    assert feed.last_body["tdMode"] == "isolated"


def test_gateway_spot_market_order_uses_base_quantity_and_cash_mode(monkeypatch) -> None:
    feed = _GatewayOrderFeed(asset_type="SPOT")
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SPOT")
    adapter._ensure_account_stream = lambda: None

    adapter.place_order(
        {
            "symbol": "BTC-USDT",
            "size": 0.1,
            "price": 0,
            "side": "buy",
            "order_type": "market",
        }
    )

    assert feed.last_body["instId"] == "BTC-USDT"
    assert float(feed.last_body["sz"]) == 0.1
    assert feed.last_body["tdMode"] == "cash"
    assert feed.last_body["tgtCcy"] == "base_ccy"
    assert "px" not in feed.last_body


class _LazyOrder:
    def __init__(self) -> None:
        self.initialized = False

    def init_data(self):
        self.initialized = True
        return self

    def get_all_data(self):
        if not self.initialized:
            return {"order_id": None}
        return {
            "instId": "BTC-USDT-SWAP",
            "ordId": "okx-order-1",
            "clOrdId": "okx-client-1",
            "state": "live",
            "sz": "2",
            "accFillSz": "0.5",
        }


class _FakeOpenOrdersFeed(_FakeFeed):
    def get_open_orders(self):
        return _FakeResult(
            {
                "data": [
                    _LazyOrder(),
                    {
                        "instId": "ETH-USDT-SWAP",
                        "ordId": "okx-order-2",
                        "clOrdId": "okx-client-2",
                        "state": "partially_filled",
                        "sz": "1",
                        "accFillSz": "0.25",
                    },
                ]
            }
        )


def test_get_open_orders_initializes_and_normalizes_order_rows(monkeypatch) -> None:
    feed = _FakeOpenOrdersFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")

    orders = adapter.get_open_orders()

    assert orders[0]["symbol"] == "BTC-USDT-SWAP"
    assert orders[0]["order_id"] == "okx-order-1"
    assert orders[0]["external_order_id"] == "okx-order-1"
    assert orders[0]["client_order_id"] == "okx-client-1"
    assert orders[0]["status"] == "live"
    assert orders[0]["remaining"] == 1.5
    assert orders[1]["order_id"] == "okx-order-2"
    assert orders[1]["client_order_id"] == "okx-client-2"
    assert orders[1]["remaining"] == 0.75


class _LazyPosition:
    def __init__(self) -> None:
        self.initialized = False

    def init_data(self):
        self.initialized = True
        return self

    def get_all_data(self):
        if not self.initialized:
            return {"position_symbol_name": None}
        return {
            "position_symbol_name": "BTC-USDT-SWAP",
            "position_volume": 1.0,
            "position_side": "long",
            "avg_price": 60000.0,
            "mark_price": 60005.0,
            "position_fee": -0.25,
            "position_unrealized_pnl": 5.0,
        }


class _FakePositionFeed(_FakeFeed):
    def get_position(self, symbol=None):
        return _FakeResult([_LazyPosition()])


def test_get_positions_initializes_position_containers(monkeypatch) -> None:
    feed = _FakePositionFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter._ensure_account_stream = lambda: None

    positions = adapter.get_positions()

    assert positions == [
        {
            "position_symbol_name": "BTC-USDT-SWAP",
            "position_volume": 1.0,
            "position_side": "long",
            "avg_price": 60000.0,
            "mark_price": 60005.0,
            "position_fee": -0.25,
            "position_unrealized_pnl": 5.0,
        }
    ]


class _LazyInstrument:
    def __init__(self) -> None:
        self.initialized = False

    def init_data(self):
        self.initialized = True
        return self

    def get_all_data(self):
        if not self.initialized:
            return {"symbol_name": None}
        return {
            "symbol_name": "BTC-USDT-SWAP",
            "asset_type": "SWAP",
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "contract_notional_value": "0.01",
            "contract_value_currency": "BTC",
            "contract_multiplier": "1",
            "contract_type": "linear",
            "price_unit": "0.1",
            "qty_unit": "0.01",
            "min_qty": "0.01",
            "max_limit_qty": "1000",
            "max_market_qty": "500",
            "max_leverage": "100",
        }


class _FakeSymbolFeed(_FakeFeed):
    def get_instruments(self, asset_type=None, inst_id=None):
        assert asset_type == "SWAP"
        assert inst_id == "BTC-USDT-SWAP"
        return _FakeResult([_LazyInstrument()])

    def get_fee(self, inst_type=None, inst_id=None):
        assert inst_type == "SWAP"
        assert inst_id == "BTC-USDT-SWAP"
        return _FakeResult(
            [],
            input_data={
                "code": "0",
                "data": [
                    {
                        "instId": "BTC-USDT-SWAP",
                        "maker": "-0.0002",
                        "taker": "-0.0005",
                        "makerU": "-0.00018",
                        "takerU": "-0.00045",
                    }
                ],
            },
        )


def test_get_symbol_info_merges_okx_contract_and_fee_rates(monkeypatch) -> None:
    feed = _FakeSymbolFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")

    spec = adapter.get_symbol_info("BTC-USDT-SWAP")

    assert spec["symbol"] == "BTC-USDT-SWAP"
    assert spec["multiplier"] == 0.01
    assert spec["contract_value_currency"] == "BTC"
    assert spec["ctValCcy"] == "BTC"
    assert spec["contract_multiplier_raw"] == 1.0
    assert spec["price_tick"] == "0.1"
    assert spec["order_size_step"] == "0.01"
    assert spec["maker_commission_rate"] == 0.00018
    assert spec["taker_commission_rate"] == 0.00045
    assert spec["commission_rate"] == 0.00045
    assert spec["open_commission_rate"] == 0.00045
    assert spec["max_leverage"] == "100"
    assert spec["leverage"] == "100"
    assert spec["fee_source"] == "okx_get_fee"


class _FakeTradesFeed(_FakeFeed):
    def get_fills(self, inst_type=None, inst_id=None, limit=None):
        assert inst_type == "SWAP"
        assert inst_id == "BTC-USDT-SWAP"
        assert limit == 50
        return _FakeResult(
            [],
            input_data={
                "code": "0",
                "data": [
                    {
                        "instId": "BTC-USDT-SWAP",
                        "tradeId": "fill-1",
                        "side": "buy",
                        "fillSz": "2",
                        "fillPx": "60000",
                        "fillFee": "-0.5",
                        "fillFeeCcy": "USDT",
                        "fillTime": "1710000000000",
                    }
                ],
            },
        )


def test_get_trades_reads_okx_fills(monkeypatch) -> None:
    feed = _FakeTradesFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")

    trades = adapter.get_trades(symbol="BTC-USDT-SWAP", limit=50)

    assert trades == [
        {
            "instId": "BTC-USDT-SWAP",
            "tradeId": "fill-1",
            "side": "buy",
            "fillSz": "2",
            "fillPx": "60000",
            "fillFee": "-0.5",
            "fillFeeCcy": "USDT",
            "fillTime": "1710000000000",
        }
    ]


class _FakeTrade:
    def init_data(self):
        return self

    @staticmethod
    def get_symbol_name():
        return "BTC-USDT-SWAP"

    @staticmethod
    def get_trade_id():
        return "trade-1"

    @staticmethod
    def get_order_id():
        return "order-1"

    @staticmethod
    def get_trade_price():
        return 60000.0

    @staticmethod
    def get_trade_volume():
        return 1.0

    @staticmethod
    def get_trade_side():
        return "buy"

    @staticmethod
    def get_trade_type():
        return "taker"

    @staticmethod
    def get_trade_fee():
        return -0.25

    @staticmethod
    def get_trade_fee_symbol():
        return "USDT"


def test_emit_trade_includes_fee_and_liquidity_role(monkeypatch) -> None:
    feed = _FakeFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")

    adapter._emit_trade(_FakeTrade())
    channel, payload = adapter.poll_output()

    assert channel == adapter_module.CHANNEL_EVENT
    assert payload["kind"] == "trade"
    assert payload["trade_fee"] == -0.25
    assert payload["trade_commission"] == -0.25
    assert payload["fee"] == -0.25
    assert payload["fee_currency"] == "USDT"
    assert payload["trade_type"] == "taker"
    assert payload["liquidity"] == "taker"


class _FakeTicker:
    def init_data(self):
        return self

    @staticmethod
    def get_symbol_name():
        return "BTC-USDT-SWAP"

    @staticmethod
    def get_server_time():
        return 1700000000000

    @staticmethod
    def get_bid_price():
        return 60999.0

    @staticmethod
    def get_ask_price():
        return 61001.0

    @staticmethod
    def get_last_price():
        return 61000.5

    @staticmethod
    def get_bid_volume():
        return 1.0

    @staticmethod
    def get_ask_volume():
        return 2.0

    @staticmethod
    def get_vol_24h():
        return 100.0

    @staticmethod
    def get_vol_ccy_24h():
        return 6100000.0

    @staticmethod
    def get_high_24h():
        return 62000.0

    @staticmethod
    def get_low_24h():
        return 60000.0

    @staticmethod
    def get_open_24h():
        return 60500.0


def test_emit_ticker_updates_latest_price_cache(monkeypatch) -> None:
    feed = _FakeFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")

    adapter._emit_ticker(_FakeTicker())
    channel, payload = adapter.poll_output()

    assert channel == adapter_module.CHANNEL_MARKET
    assert adapter.last_price["BTC-USDT-SWAP"] == 61000.5
    assert adapter._latest_ticks["BTC-USDT-SWAP"]["price"] == 61000.5
    assert adapter._latest_ticks["BTC-USDT-SWAP"]["last_price"] == 61000.5
    assert payload.price == 61000.5


def test_disconnect_clears_latest_price_cache(monkeypatch) -> None:
    feed = _FakeFeed()
    monkeypatch.setattr(adapter_module, "_create_feed", lambda _queue, _kwargs: feed)
    adapter = adapter_module.OkxGatewayAdapter(asset_type="SWAP")
    adapter.last_price = {"BTC-USDT-SWAP": 61000.5}
    adapter._latest_ticks = {"BTC-USDT-SWAP": {"price": 61000.5}}

    adapter.disconnect()

    assert adapter.last_price == {}
    assert adapter._latest_ticks == {}
