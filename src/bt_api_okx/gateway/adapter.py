"""OKX gateway adapter for SWAP and SPOT."""

from __future__ import annotations

import queue
import threading
import time
from collections import defaultdict
from typing import Any

from bt_api_base.gateway.adapters.base import BaseGatewayAdapter
from bt_api_base.gateway.models import GatewayTick
from bt_api_base.gateway.protocol import CHANNEL_EVENT, CHANNEL_MARKET

from bt_api_okx.containers.orders.okx_order import OkxOrderData
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.containers.trades.okx_trade import OkxWssFillsData, OkxWssTradeData
from bt_api_okx.exchange_data import (
    OkxExchangeDataSpot,
    OkxExchangeDataSwap,
)
from bt_api_okx.feeds.live_okx.swap import (
    OkxAccountWssDataSwap,
    OkxMarketWssDataSwap,
    OkxRequestDataSwap,
)


def _normalize_asset_type(raw: Any) -> str:
    value = str(raw or "SWAP").strip().upper()
    mapping = {"SWAP": "SWAP", "SPOT": "SPOT", "FUTURE": "SWAP", "FUT": "SWAP"}
    return mapping.get(value, value)


def _create_feed(q: queue.Queue, kwargs: dict[str, Any]):
    asset_type = kwargs.get("asset_type", "SWAP")
    if asset_type == "SPOT":
        from bt_api_okx.feeds.live_okx.spot import OkxRequestDataSpot

        return OkxRequestDataSpot(q, **kwargs)
    return OkxRequestDataSwap(q, **kwargs)


def _create_exchange_data(asset_type: str):
    if asset_type == "SPOT":
        return OkxExchangeDataSpot()
    return OkxExchangeDataSwap()


def _container_to_dict(item: Any) -> dict[str, Any]:
    init_data = getattr(item, "init_data", None)
    if callable(init_data):
        item = init_data()
    if hasattr(item, "get_all_data"):
        return dict(item.get_all_data())
    return dict(item) if isinstance(item, dict) else {"raw": str(item)}


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _first_text(row: dict[str, Any], *keys: str) -> str:
    value = _first_value(row, *keys)
    return str(value or "").strip()


def _request_data_payload(result: Any, *, prefer_input: bool = False) -> Any:
    if prefer_input:
        get_input_data = getattr(result, "get_input_data", None)
        if callable(get_input_data):
            raw = get_input_data()
            if raw not in (None, ""):
                return raw
    get_data = getattr(result, "get_data", None)
    if callable(get_data):
        return get_data()
    return result


def _payload_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            payload = data
        elif isinstance(data, dict):
            payload = [data]
        else:
            payload = [payload]
    elif not isinstance(payload, list):
        payload = []

    rows: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            rows.append(dict(item))
        else:
            rows.append(_container_to_dict(item))
    return rows


def _normalise_order_row(item: Any) -> dict[str, Any]:
    row = _container_to_dict(item)
    order_id = (
        row.get("order_id")
        or row.get("ordId")
        or row.get("orderId")
        or row.get("id")
    )
    client_order_id = (
        row.get("client_order_id")
        or row.get("clOrdId")
        or row.get("clientOrderId")
        or row.get("c")
    )
    symbol = row.get("symbol") or row.get("symbol_name") or row.get("instId")
    status = row.get("status") or row.get("order_status") or row.get("state")
    remaining = row.get("remaining")
    if remaining in (None, ""):
        try:
            size = float(row.get("sz") or row.get("size") or row.get("volume") or 0)
            filled = float(row.get("accFillSz") or row.get("filled") or 0)
            remaining = max(size - filled, 0.0)
        except (TypeError, ValueError):
            remaining = None
    if order_id not in (None, ""):
        row["order_id"] = order_id
        row.setdefault("external_order_id", order_id)
    if client_order_id not in (None, ""):
        row["client_order_id"] = client_order_id
    if symbol not in (None, ""):
        row["symbol"] = symbol
        row.setdefault("data_name", symbol)
    if status not in (None, ""):
        row["status"] = status
    if remaining not in (None, ""):
        row["remaining"] = remaining
    return row


def _symbol_candidates(symbol: str) -> set[str]:
    raw = str(symbol or "").strip()
    dashed = raw.replace("/", "-")
    compact = "".join(ch for ch in dashed if ch.isalnum())
    return {item.upper() for item in (raw, dashed, compact) if item}


def _normalise_okx_fee_rate(value: Any) -> float | None:
    rate = _safe_float(value)
    if rate is None:
        return None
    if abs(rate) > 1:
        rate = rate / 100.0
    # OKX reports positive rates as rebates and negative rates as commissions.
    return -rate


def _normalise_okx_fee_info(data: Any, *, asset_type: str) -> dict[str, Any]:
    rows = _payload_rows(data)
    row = next((item for item in rows if item), None)
    if row is None:
        return {}

    is_derivative = str(asset_type or "").upper() in {
        "SWAP",
        "FUTURES",
        "FUTURE",
        "OPTION",
    }
    maker_rate = _normalise_okx_fee_rate(
        _first_value(row, "makerU", "maker")
        if is_derivative
        else _first_value(row, "maker")
    )
    taker_rate = _normalise_okx_fee_rate(
        _first_value(row, "takerU", "taker")
        if is_derivative
        else _first_value(row, "taker")
    )
    spec: dict[str, Any] = {"fee_source": "okx_get_fee"}
    if maker_rate is not None:
        spec["maker_commission_rate"] = maker_rate
    if taker_rate is not None:
        spec["taker_commission_rate"] = taker_rate
        spec["commission_rate"] = taker_rate
        spec["open_commission_rate"] = taker_rate
    elif maker_rate is not None:
        spec["commission_rate"] = maker_rate
        spec["open_commission_rate"] = maker_rate
    return spec


def _normalise_okx_symbol_info(
    row: dict[str, Any], *, requested_symbol: str, asset_type: str
) -> dict[str, Any]:
    inst_type = _first_text(row, "asset_type", "instType") or asset_type
    symbol = _first_text(row, "symbol", "symbol_name", "instId") or requested_symbol
    contract_value = _safe_float(_first_value(row, "contract_notional_value", "ctVal"))
    contract_multiplier = _safe_float(_first_value(row, "contract_multiplier", "ctMult"))
    contract_value_currency = _first_value(
        row,
        "contract_value_currency",
        "contract_value_ccy",
        "ctValCcy",
    )
    is_derivative = str(inst_type or "").upper() in {
        "SWAP",
        "FUTURES",
        "FUTURE",
        "OPTION",
    }
    multiplier = contract_value if is_derivative and contract_value else contract_multiplier
    if multiplier is None and str(inst_type or "").upper() == "SPOT":
        multiplier = 1.0

    spec = {
        "source": "okx_get_instruments",
        "exchange": "OKX",
        "exchange_id": "OKX",
        "symbol": symbol,
        "asset_type": inst_type,
        "base_asset": _first_value(row, "base_asset", "baseCcy"),
        "quote_asset": _first_value(row, "quote_asset", "quoteCcy"),
        "fee_currency": _first_value(row, "fee_currency", "settleCcy"),
        "contract_type": _first_value(row, "contract_type", "ctType"),
        "contract_value_currency": contract_value_currency,
        "contract_value_ccy": contract_value_currency,
        "ctValCcy": contract_value_currency,
        "contract_notional_value": contract_value,
        "okx_contract_value": contract_value,
        "contract_multiplier_raw": contract_multiplier,
        "contract_multiplier": multiplier,
        "contract_size": multiplier,
        "multiplier": multiplier,
        "price_tick": _first_value(row, "price_unit", "tickSz"),
        "tick_size": _first_value(row, "price_unit", "tickSz"),
        "min_order_size": _first_value(row, "min_qty", "minSz"),
        "max_order_size": _first_value(row, "max_limit_qty", "maxLmtSz", "max_qty"),
        "order_size_step": _first_value(row, "qty_unit", "lotSz"),
        "market_max_order_size": _first_value(row, "max_market_qty", "maxMktSz"),
        "min_notional": _first_value(row, "min_amount", "notional"),
        "max_leverage": _first_value(row, "max_leverage", "lever"),
        "leverage": _first_value(row, "leverage", "lever", "max_leverage"),
        "symbol_status": _first_value(row, "symbol_status", "state"),
    }
    return {key: value for key, value in spec.items() if value not in (None, "")}


class OkxGatewayAdapter(BaseGatewayAdapter):
    """Gateway adapter wrapping OKX REST + WSS feeds."""

    def __init__(self, **kwargs: Any) -> None:
        """__init__ method"""
        normalized = dict(kwargs)
        self.asset_type = _normalize_asset_type(normalized.get("asset_type"))
        normalized["asset_type"] = self.asset_type
        normalized.setdefault("public_key", normalized.get("api_key", ""))
        normalized.setdefault("private_key", normalized.get("secret_key", ""))
        normalized.setdefault("passphrase", normalized.get("passphrase", ""))
        normalized.setdefault("exchange_name", "OKX")
        exchange_data = _create_exchange_data(self.asset_type)
        normalized["exchange_data"] = exchange_data
        super().__init__(**normalized)
        self.kwargs = normalized
        self.q: queue.Queue[Any] = queue.Queue()
        self.feed = _create_feed(self.q, normalized)
        self.market_stream = None
        self.account_stream = None
        self.aliases: dict[str, set[str]] = defaultdict(set)
        self.last_price: dict[str, float] = {}
        self._latest_ticks: dict[str, dict[str, Any]] = {}
        self.running = False
        self.thread: threading.Thread | None = None
        self.timeout = float(
            normalized.get("gateway_startup_timeout_sec", 10.0) or 10.0
        )
        self._market_connect_timeout = float(
            normalized.get("market_stream_connect_timeout_sec", 1.0) or 1.0
        )
        self._account_connect_timeout = float(
            normalized.get("account_stream_connect_timeout_sec", 1.0) or 1.0
        )

    def connect(self) -> None:
        """connect method"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info("OkxGatewayAdapter connected")

    def disconnect(self) -> None:
        """disconnect method"""
        self.running = False
        thread = self.thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self.thread = None
        self.market_stream = None
        self.account_stream = None
        self.aliases = defaultdict(set)
        self.last_price.clear()
        self._latest_ticks.clear()
        self.logger.info("OkxGatewayAdapter disconnected")

    def subscribe_symbols(self, symbols: list[str]) -> dict[str, Any]:
        """subscribe_symbols method"""
        topics = [{"topic": "ticker", "symbol": s} for s in symbols]
        wss_kwargs = dict(self.kwargs)
        wss_kwargs["topics"] = topics

        if self.market_stream is None:
            if self.asset_type == "SPOT":
                from bt_api_okx.feeds.live_okx.spot import OkxMarketWssDataSpot

                self.market_stream = OkxMarketWssDataSpot(self.q, **wss_kwargs)
            else:
                self.market_stream = OkxMarketWssDataSwap(self.q, **wss_kwargs)
            self.market_stream.start(connect_timeout=self._market_connect_timeout)
            self.logger.info(f"OKX market stream started for {symbols}")

        for symbol in symbols:
            self.aliases[symbol].add(symbol)
        return {"symbols": symbols}

    def _ensure_account_stream(self) -> None:
        if self.account_stream is not None:
            return
        account_kwargs = dict(self.kwargs)
        account_kwargs["topics"] = [
            {"topic": "account"},
            {"topic": "orders"},
            {"topic": "positions"},
        ]
        try:
            if self.asset_type == "SPOT":
                from bt_api_okx.feeds.live_okx.spot import (
                    OkxAccountWssDataSwap as OkxAccountWssDataSpot,
                )

                self.account_stream = OkxAccountWssDataSpot(self.q, **account_kwargs)
            else:
                self.account_stream = OkxAccountWssDataSwap(self.q, **account_kwargs)
            self.account_stream.start(connect_timeout=self._account_connect_timeout)
            self.logger.info("OKX account stream started")
        except Exception as exc:
            self.account_stream = None
            self.logger.warning(
                "OKX account stream unavailable; continuing with market data only: %s",
                exc,
            )

    def get_balance(self) -> dict[str, Any]:
        """get_balance method"""
        self._ensure_account_stream()
        try:
            result = self.feed.get_balance()
            data = result.get_data() if hasattr(result, "get_data") else result
            if isinstance(data, list) and len(data) > 0:
                return _container_to_dict(data[0])
            if isinstance(data, dict):
                return data
            return {"raw": str(data)}
        except Exception as exc:
            self.logger.warning(f"get_balance error: {exc}")
            return {"error": str(exc)}

    def get_positions(self) -> list[dict[str, Any]]:
        """get_positions method"""
        self._ensure_account_stream()
        try:
            result = self.feed.get_position(symbol=None)
            data = result.get_data() if hasattr(result, "get_data") else result
            if isinstance(data, list):
                return [_container_to_dict(item) for item in data]
            return []
        except Exception as exc:
            self.logger.warning(f"get_positions error: {exc}")
            return []

    def get_trades(self, symbol: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        get_fills = getattr(self.feed, "get_fills", None)
        if not callable(get_fills):
            return []
        try:
            result = get_fills(
                inst_type=self.asset_type,
                inst_id=symbol or None,
                limit=limit,
            )
            payload = _request_data_payload(result, prefer_input=True)
            return _payload_rows(payload)
        except Exception as exc:
            self.logger.debug(f"get_trades error: {exc}")
            return []

    def get_symbol_info(self, symbol: str) -> dict[str, Any]:
        spec = self._query_instrument_info(symbol)
        if not spec:
            return {}
        spec.update(self._query_symbol_fee(symbol, spec))
        return spec

    def _query_instrument_info(self, symbol: str) -> dict[str, Any]:
        get_instruments = getattr(self.feed, "get_instruments", None)
        if not callable(get_instruments):
            return {}
        try:
            result = get_instruments(asset_type=self.asset_type, inst_id=symbol)
            rows = _payload_rows(_request_data_payload(result))
        except Exception as exc:
            self.logger.warning(f"get_symbol_info instrument lookup error: {exc}")
            return {}

        candidates = _symbol_candidates(symbol)
        for row in rows:
            row_symbol = _first_text(row, "symbol", "symbol_name", "instId")
            row_compact = "".join(ch for ch in row_symbol if ch.isalnum()).upper()
            if row_symbol.upper() in candidates or row_compact in candidates:
                return _normalise_okx_symbol_info(
                    row, requested_symbol=symbol, asset_type=self.asset_type
                )
        if len(rows) == 1:
            return _normalise_okx_symbol_info(
                rows[0], requested_symbol=symbol, asset_type=self.asset_type
            )
        return {}

    def _query_symbol_fee(self, symbol: str, spec: dict[str, Any]) -> dict[str, Any]:
        get_fee = getattr(self.feed, "get_fee", None)
        if not callable(get_fee):
            return {}
        asset_type = str(spec.get("asset_type") or self.asset_type or "SWAP")
        try:
            result = get_fee(inst_type=asset_type, inst_id=symbol)
            payload = _request_data_payload(result, prefer_input=True)
            return _normalise_okx_fee_info(payload, asset_type=asset_type)
        except Exception as exc:
            self.logger.debug(f"get_symbol_info fee lookup failed: {exc}")
            return {}

    def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        """place_order method"""
        self._ensure_account_stream()
        symbol = payload.get("data_name") or payload.get("symbol") or ""
        volume = float(payload.get("volume") or payload.get("size") or 0)
        price = payload.get("price")
        if price is not None:
            price = float(price)
        side = str(payload.get("side") or "buy").lower()
        order_type = str(payload.get("order_type") or "limit").lower()
        offset = str(payload.get("offset") or "open").lower()
        order_type_str = f"{side}-{order_type}"
        client_order_id = payload.get("client_order_id")
        pos_side = _first_value(payload, "posSide", "position_side", "positionSide")
        reduce_only = _first_value(payload, "reduceOnly", "reduce_only")
        td_mode = _first_value(payload, "tdMode", "td_mode")

        result = self.feed.make_order(
            symbol=symbol,
            vol=volume,
            price=price,
            order_type=order_type_str,
            offset=offset,
            client_order_id=client_order_id,
            size_in_contracts=True,
            posSide=pos_side,
            reduceOnly=reduce_only,
            tdMode=td_mode,
        )
        data = result.get_data() if hasattr(result, "get_data") else result
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            if isinstance(item, dict):
                return item
            return {"raw": str(item)}
        if isinstance(data, dict):
            return data
        return {"raw": str(data)}

    def cancel_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        """cancel_order method"""
        self._ensure_account_stream()
        symbol = payload.get("data_name") or payload.get("symbol") or payload.get("instrument") or ""
        order_id = (
            payload.get("order_id")
            or payload.get("external_order_id")
            or payload.get("venue_order_id")
            or payload.get("id")
            or payload.get("order_ref")
        )
        client_order_id = payload.get("client_order_id")

        cancel_kwargs: dict[str, Any] = {}
        if client_order_id:
            cancel_kwargs["client_order_id"] = client_order_id

        result = self.feed.cancel_order(
            symbol=symbol,
            order_id=order_id,
            **cancel_kwargs,
        )
        data = result.get_data() if hasattr(result, "get_data") else result
        if isinstance(data, dict):
            return data
        return {"raw": str(data)}

    def get_open_orders(self) -> list[dict[str, Any]]:
        get_open_orders = getattr(self.feed, "get_open_orders", None)
        if not callable(get_open_orders):
            return []
        result = get_open_orders()
        payload = _request_data_payload(result)
        return [_normalise_order_row(item) for item in _payload_rows(payload)]

    def _run(self) -> None:
        while self.running:
            try:
                item = self.q.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self._dispatch_item(item)
            except Exception as exc:
                self.logger.warning(f"OKX adapter dispatch error: {exc}")

    def _dispatch_item(self, item: Any) -> None:
        if isinstance(item, OkxTickerData):
            self._emit_ticker(item)
        elif isinstance(item, OkxOrderData):
            self._emit_order(item)
        elif isinstance(item, (OkxWssTradeData, OkxWssFillsData)):
            self._emit_trade(item)
        else:
            event_name = getattr(item, "event", None) or type(item).__name__
            self.emit(CHANNEL_EVENT, {"kind": "raw", "type": event_name})

    def _emit_ticker(self, ticker: OkxTickerData) -> None:
        ticker.init_data()
        symbol = ticker.get_symbol_name() or ""
        server_time = ticker.get_server_time() or 0.0
        ts = server_time / 1000.0 if server_time > 1e12 else server_time
        bid = ticker.get_bid_price() or 0.0
        ask = ticker.get_ask_price() or 0.0
        last = ticker.get_last_price() or 0.0
        price = last if last else (bid + ask) / 2.0 if bid and ask else 0.0
        self._latest_ticks[symbol] = {
            "timestamp": ts,
            "price": price,
            "last_price": last,
            "bid_price": bid,
            "ask_price": ask,
            "bid_volume": ticker.get_bid_volume() or 0.0,
            "ask_volume": ticker.get_ask_volume() or 0.0,
            "volume": ticker.get_vol_24h() or 0.0,
            "turnover": ticker.get_vol_ccy_24h() or 0.0,
            "high_price": ticker.get_high_24h(),
            "low_price": ticker.get_low_24h(),
            "open_price": ticker.get_open_24h(),
        }
        if price > 0:
            self.last_price[symbol] = price
        tick = GatewayTick(
            timestamp=ts,
            symbol=symbol,
            exchange="OKX",
            asset_type=self.asset_type,
            local_time=time.time(),
            price=price,
            bid_price=bid,
            ask_price=ask,
            bid_volume=ticker.get_bid_volume() or 0.0,
            ask_volume=ticker.get_ask_volume() or 0.0,
            volume=ticker.get_vol_24h() or 0.0,
            turnover=ticker.get_vol_ccy_24h() or 0.0,
            high_price=ticker.get_high_24h(),
            low_price=ticker.get_low_24h(),
            open_price=ticker.get_open_24h(),
        )
        self.emit(CHANNEL_MARKET, tick)

    def _emit_order(self, order: OkxOrderData) -> None:
        try:
            order.init_data()
            self.emit(
                CHANNEL_EVENT,
                {
                    "kind": "order",
                    "exchange": "OKX",
                    "symbol": order.get_symbol_name(),
                    "order_id": order.get_order_id(),
                    "client_order_id": order.get_client_order_id(),
                    "status": order.get_order_status(),
                    "side": order.get_order_side(),
                    "price": order.get_order_price(),
                    "volume": order.get_order_size(),
                    "filled": order.get_executed_qty(),
                },
            )
        except Exception as exc:
            self.logger.warning(f"_emit_order error: {exc}")

    def _emit_trade(self, trade: OkxWssTradeData | OkxWssFillsData) -> None:
        try:
            trade.init_data()
            self.emit(
                CHANNEL_EVENT,
                {
                    "kind": "trade",
                    "exchange": "OKX",
                    "symbol": trade.get_symbol_name(),
                    "trade_id": trade.get_trade_id(),
                    "order_id": trade.get_order_id(),
                    "price": trade.get_trade_price(),
                    "volume": trade.get_trade_volume(),
                    "side": trade.get_trade_side(),
                    "trade_type": trade.get_trade_type(),
                    "liquidity": trade.get_trade_type(),
                    "trade_fee": trade.get_trade_fee(),
                    "trade_commission": trade.get_trade_fee(),
                    "fee": trade.get_trade_fee(),
                    "fee_currency": trade.get_trade_fee_symbol(),
                },
            )
        except Exception as exc:
            self.logger.warning(f"_emit_trade error: {exc}")
