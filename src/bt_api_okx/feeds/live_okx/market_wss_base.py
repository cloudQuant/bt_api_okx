"""
OKX Market WebSocket base class.
Handles public market data channels (tickers, orderbook, kline, funding rate, mark price)
and private account channels (orders, account, positions, fills, liquidation_warning, account_greeks).
"""

from __future__ import annotations

import base64
import hmac
import json
import threading
import time
import zlib
from decimal import Decimal, InvalidOperation
from typing import Any

from bt_api_base.feeds.my_websocket_app import MyWebsocketApp, WebSocketSubscriptionError
from bt_api_base.feeds.transport_safety import sanitize_text, sanitize_value
from bt_api_base.logging_factory import get_logger

from bt_api_okx.containers.accounts.okx_account import OkxAccountData
from bt_api_okx.containers.assets.okx_asset import (
    OkxDepositInfoData,
    OkxWithdrawalInfoData,
)
from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.fundingrates.okx_funding_rate import OkxFundingRateData
from bt_api_okx.containers.greeks.okx_account_greeks import OkxAccountGreeksData
from bt_api_okx.containers.liquidations.okx_liquidation_order import (
    OkxLiquidationOrderData,
)
from bt_api_okx.containers.liquidations.okx_liquidation_warning import (
    OkxLiquidationWarningData,
)
from bt_api_okx.containers.markprices.okx_mark_price import OkxMarkPriceData
from bt_api_okx.containers.openinterests.okx_open_interest import OkxOpenInterestData
from bt_api_okx.containers.orderbooks.okx_l2_orderbook import OkxL2OrderBookData
from bt_api_okx.containers.orderbooks.okx_orderbook import OkxOrderBookData
from bt_api_okx.containers.orders.okx_order import OkxOrderData
from bt_api_okx.containers.positions.okx_position import OkxPositionData
from bt_api_okx.containers.pricelimits.okx_price_limit import OkxPriceLimitData
from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.containers.trades.okx_market_trade import OkxMarketTradeData
from bt_api_okx.containers.trades.okx_trade import OkxWssFillsData, OkxWssTradeData
from bt_api_okx.environment import configure_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap


class OkxWssData(MyWebsocketApp):
    """Class OkxWssData"""

    count = 0

    def __init__(self, data_queue: Any, **kwargs: Any) -> None:
        """__init__ method"""
        params = configure_environment(kwargs.get("exchange_data") or OkxExchangeDataSwap(), kwargs)
        kwargs["exchange_data"] = params
        kwargs.setdefault("wss_url", params.wss_url)
        super().__init__(data_queue, **kwargs)
        self.topics = kwargs.get("topics", {})
        self.public_key = kwargs.get("public_key") or kwargs.get("api_key")
        self.private_key = (
            kwargs.get("private_key") or kwargs.get("secret_key") or kwargs.get("api_secret")
        )
        self.passphrase = kwargs.get("passphrase")
        self.wss_url = kwargs.get("wss_url")
        self.asset_type = kwargs.get("asset_type", "SWAP")
        self.exchange_name = kwargs.get("exchange_name", params.exchange_name)
        self.logger = get_logger("okx_market_wss")
        self._pending_subscription_keys: set[str] = set()
        self._depth_sequences: dict[tuple[str, str], int] = {}
        self._depth_gaps: set[tuple[str, str]] = set()
        self._depth_books: dict[tuple[str, str], dict[str, Any]] = {}
        self._depth_lock = threading.RLock()
        self._depth_stale_emitted: set[tuple[str, str]] = set()
        self._depth_reseed_requested: set[tuple[str, str]] = set()

    @staticmethod
    def _subscription_key(argument: dict[str, Any]) -> str:
        # OKX may omit instType from a SWAP subscribe ACK although it was sent
        # in the request. Keep the wire argument untouched and normalize only
        # this protocol-optional field for local request/ACK correlation.
        normalized = dict(argument)
        if normalized.get("instType") == "SWAP":
            normalized.pop("instType")
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    def subscribe(self, **kwargs):
        """Send one unique subscription and retain its expected ACK argument."""
        if self._params is None:
            raise ValueError("exchange_data (params) is required for subscribe")
        request = json.loads(self._params.get_wss_path(**kwargs))
        arguments = request.get("args", [])
        if len(arguments) != 1 or not isinstance(arguments[0], dict):
            raise WebSocketSubscriptionError(
                "OKX WebSocket subscription must contain exactly one argument"
            )
        key = self._subscription_key(arguments[0])
        with self._subscription_lock:
            if key in self._pending_subscription_keys:
                raise WebSocketSubscriptionError("Duplicate OKX WebSocket subscription")
            self._pending_subscription_keys.add(key)
        try:
            return super().subscribe(**kwargs)
        except Exception:
            with self._subscription_lock:
                self._pending_subscription_keys.discard(key)
            raise

    def _uses_private_wss(self) -> bool:
        return "/private" in str(self.wss_url or "").lower()

    def sign(self, content: Any) -> str:
        """
        Args: content (TYPE): Description
        """
        sign = base64.b64encode(
            hmac.new(
                self.private_key.encode("utf-8"),
                content.encode("utf-8"),
                digestmod="sha256",
            ).digest()
        ).decode()

        return sign

    def author(self) -> None:
        """author method"""
        if not self._uses_private_wss():
            self.wss_logger.info("Skipping auth on non-private OKX websocket endpoint")
            return
        if not all((self.public_key, self.private_key, self.passphrase)):
            raise ValueError("OKX private websocket requires API key, secret and passphrase")
        timestamp = str(int(time.time()))
        sign_content = f"{timestamp}GET/users/self/verify"
        sign = self.sign(sign_content)
        auth = {
            "op": "login",
            "args": [
                {
                    "apiKey": self.public_key,
                    "passphrase": self.passphrase,
                    "timestamp": timestamp,
                    "sign": sign,
                }
            ],
        }
        self.ws.send(json.dumps(auth))

    def open_rsp(self) -> bool:
        """open_rsp method"""
        self.wss_logger.info(
            f"===== {time.strftime('%Y-%m-%d %H:%M:%S')} {self._params.exchange_name} Websocket Connected ====="
        )
        with self._subscription_lock:
            self._pending_subscription_keys.clear()
        with self._depth_lock:
            self._depth_sequences.clear()
            self._depth_gaps.clear()
            self._depth_books.clear()
            self._depth_stale_emitted.clear()
            self._depth_reseed_requested.clear()
        if self._uses_private_wss():
            # 私有 WSS：先发 login，订阅推迟到 login 成功回执（避免固定 sleep 的时序脆弱）
            self.author()
            return False
        else:
            # 公开 WSS 或无凭据：无需登录，直接订阅
            if not self.topics:
                raise WebSocketSubscriptionError("OKX market WebSocket requires at least one topic")
            self._begin_subscription_batch()
            self._init()
            return self._end_subscription_batch()

    def _init(self) -> None:
        for topics in self.topics:
            sent_before = self._subscription_batch_send_count
            self.count += 1
            if "orders" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="orders", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, orders"
                )

            # Algo order channels - check specific ones first
            if topics["topic"] == "algo_orders" or "algo_orders" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="algo_orders", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, algo_orders"
                )

            if topics["topic"] == "algo_advance" or "algo_advance" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="algo_advance", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, algo_advance"
                )

            if "fills" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="fills", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, fills"
                )

            if "liquidation_warning" in topics["topic"]:
                self.subscribe(topic="liquidation_warning")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, liquidation_warning"
                )

            if "account_greeks" in topics["topic"]:
                self.subscribe(topic="account_greeks")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, account_greeks"
                )

            if "account" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                currency = topics.get("currency", "USDT")
                self.subscribe(topic="account", symbol=symbol, currency=currency)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, account"
                )

            if "positions" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="positions", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, positions"
                )

            if "balance_position" in self.topics:
                self.subscribe(topic="balance_position")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, balance_position"
                )

            # Orderbook channels - check specific ones first to avoid substring conflicts
            if topics["topic"] == "books_l2_tbt" or topics["topic"] == "books_l2_tbt":
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="books_l2_tbt", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, books_l2_tbt"
                )
            elif (
                topics["topic"] == "books"
                or "books" in topics["topic"]
                and "_l2" not in topics["topic"]
                and "50-l2" not in topics["topic"]
            ):
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="books", symbol=symbol, type="step0")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, orderbook"
                )

            if topics["topic"] == "ticker" or "ticker" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="tick", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, ticker"
                )

            if topics["topic"] == "depth" or "depth" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="depth", symbol=symbol, type="step0")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, depth"
                )

            if topics["topic"] == "bidAsk" or "bidAsk" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="bidAsk", symbol=symbol, type="step0")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, bidAsk"
                )

            if topics["topic"] == "funding_rate" or "funding_rate" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="funding_rate", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, funding_rate"
                )

            if topics["topic"] == "mark_price" or "mark_price" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="mark_price", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, mark_price"
                )

            if topics["topic"] == "kline" or "kline" in topics["topic"]:
                period = topics.get("period", "1m")
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="kline", symbol=symbol, period=period)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, kline"
                )

            if topics["topic"] == "trades" or (
                "trades" in topics["topic"] and "trades_all" not in topics["topic"]
            ):
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="trades", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, trades"
                )

            if topics["topic"] == "trades_all" or "trades_all" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="trades_all", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, trades_all"
                )

            if topics["topic"] == "open_interest" or "open_interest" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="open_interest", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, open_interest"
                )

            if topics["topic"] == "price_limit" or "price_limit" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="price_limit", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, price_limit"
                )

            if topics["topic"] == "liquidation_orders" or "liquidation_orders" in topics["topic"]:
                self.subscribe(topic="liquidation_orders")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, liquidation_orders"
                )

            # Additional market channels
            if topics["topic"] == "books_sbe_tbt" or "books_sbe_tbt" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="books_sbe_tbt", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, books_sbe_tbt"
                )

            if topics["topic"] == "increDepthFlow" or "increDepthFlow" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="increDepthFlow", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, increDepthFlow"
                )

            if topics["topic"] == "opt_trades" or "opt_trades" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USD")
                self.subscribe(topic="opt_trades", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, opt_trades"
                )

            if (
                topics["topic"] == "call_auction_details"
                or "call_auction_details" in topics["topic"]
            ):
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="call_auction_details", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, call_auction_details"
                )

            if topics["topic"] == "opt_summary" or "opt_summary" in topics["topic"]:
                self.subscribe(topic="opt_summary")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, opt_summary"
                )

            if topics["topic"] == "estimated_price" or "estimated_price" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="estimated_price", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, estimated_price"
                )

            if topics["topic"] == "index_tickers" or "index_tickers" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USD")
                self.subscribe(topic="index_tickers", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, index_tickers"
                )

            if topics["topic"] == "instruments" or "instruments" in topics["topic"]:
                self.subscribe(topic="instruments")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, instruments"
                )

            if topics["topic"] == "adl_warning" or "adl_warning" in topics["topic"]:
                self.subscribe(topic="adl_warning")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, adl_warning"
                )

            if topics["topic"] == "status" or "status" in topics["topic"]:
                self.subscribe(topic="status")
                self.logger.info(f"subscribe {self.count} data, OKX, {self.asset_type}, status")

            if topics["topic"] == "kline_index" or "kline_index" in topics["topic"]:
                period = topics.get("period", "1m")
                symbol = topics.get("symbol", "BTC-USD")
                self.subscribe(topic="kline_index", symbol=symbol, period=period)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, kline_index"
                )

            if topics["topic"] == "kline_mark_price" or "kline_mark_price" in topics["topic"]:
                period = topics.get("period", "1m")
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="kline_mark_price", symbol=symbol, period=period)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, kline_mark_price"
                )

            if topics["topic"] == "economic_calendar" or "economic_calendar" in topics["topic"]:
                self.subscribe(topic="economic_calendar")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, economic_calendar"
                )

            if topics["topic"] == "deposit_info" or "deposit_info" in topics["topic"]:
                self.subscribe(topic="deposit_info")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, deposit_info"
                )

            if topics["topic"] == "withdrawal_info" or "withdrawal_info" in topics["topic"]:
                self.subscribe(topic="withdrawal_info")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, withdrawal_info"
                )

            # Grid trading channels
            if topics["topic"] == "grid_orders_spot" or "grid_orders_spot" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT")
                self.subscribe(topic="grid-orders-spot", instId=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, grid-orders-spot"
                )

            if (
                topics["topic"] == "grid_orders_contract"
                or "grid_orders_contract" in topics["topic"]
            ):
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                ccy = topics.get("ccy", "BTC")
                self.subscribe(topic="grid-orders-contract", instId=symbol, ccy=ccy)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, grid-orders-contract"
                )

            if topics["topic"] == "grid_positions" or "grid_positions" in topics["topic"]:
                inst_type = topics.get("instType", "SWAP")
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="grid-positions", instType=inst_type, instId=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, grid-positions"
                )

            if topics["topic"] == "grid_sub_orders" or "grid_sub_orders" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="grid-sub-orders", instId=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, grid-sub-orders"
                )

            # Spread trading channels
            if topics["topic"] == "sprd_orders" or "sprd_orders" in topics["topic"]:
                sprd_id = topics.get("sprdId", "")
                self.subscribe(topic="sprd-orders", sprdId=sprd_id)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, sprd-orders, sprdId={sprd_id}"
                )

            if topics["topic"] == "sprd_tickers" or "sprd_tickers" in topics["topic"]:
                sprd_id = topics.get("sprdId", "")
                self.subscribe(topic="sprd-tickers", sprdId=sprd_id)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, sprd-tickers, sprdId={sprd_id}"
                )

            # RFQ (Request for Quote) / Block Trading channels
            if topics["topic"] == "rfqs" or "rfqs" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="rfqs", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, rfqs"
                )

            if topics["topic"] == "quotes" or "quotes" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="quotes", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, quotes"
                )

            if topics["topic"] == "struc_block_trades" or "struc_block_trades" in topics["topic"]:
                symbol = topics.get("symbol", "BTC-USDT-SWAP")
                self.subscribe(topic="struc-block-trades", symbol=symbol)
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, {symbol}, struc-block-trades"
                )

            if (
                topics["topic"] == "public_struc_block_trades"
                or "public_struc_block_trades" in topics["topic"]
            ):
                self.subscribe(topic="public-struc-block-trades")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, public-struc-block-trades"
                )

            if topics["topic"] == "public_block_trades" or "public_block_trades" in topics["topic"]:
                self.subscribe(topic="public-block-trades")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, public-block-trades"
                )

            if topics["topic"] == "block_tickers" or "block_tickers" in topics["topic"]:
                self.subscribe(topic="block-tickers")
                self.logger.info(
                    f"subscribe {self.count} data, OKX, {self.asset_type}, block-tickers"
                )

            if self._subscription_batch_send_count == sent_before:
                raise WebSocketSubscriptionError("Unsupported or incomplete OKX WebSocket topic")

    def handle_data(self, content: Any) -> None:
        """handle_data method"""
        arg = content.get("arg", None)
        if arg is not None:
            channel = arg.get("channel", "")

            # Depth channels are mutually exclusive.  In particular, the L2
            # names contain ``books`` and must never be delivered by both the
            # regular and tick-by-tick paths.
            if channel in {"books-l2-tbt", "books50-l2-tbt", "books-sbe-tbt"}:
                self.push_l2_order_book(content)
                return
            if channel in {"books", "books5"}:
                self.push_order_book(content)
                return
            if channel.startswith(("index-candle", "mark-price-candle")):
                self.push_bar(content)
                return
            special_handlers = {
                "orders-algo": self.push_algo_order,
                "algo-advance": self.push_algo_advance,
                "bbo-tbt": self.push_ticker,
                "opt-trades": self.push_market_trades,
                "call-auction-details": self.push_market_trades,
                "opt-summary": self.push_opt_summary,
                "estimated-price": self.push_estimated_price,
                "index-tickers": self.push_index_ticker,
                "instruments": self.push_instruments,
                "adl-warning": self.push_adl_warning,
                "status": self.push_status,
                "economic-calendar": self.push_economic_calendar,
                "deposit-info": self.push_deposit_info,
                "withdrawal-info": self.push_withdrawal_info,
                "grid-orders-spot": self._push_grid_orders_spot,
                "grid-orders-contract": self._push_grid_orders_contract,
                "grid-positions": self._push_grid_positions,
                "grid-sub-orders": self._push_grid_sub_orders,
                "sprd-orders": self._push_sprd_orders,
                "sprd-tickers": self._push_sprd_tickers,
                "rfqs": self._push_rfqs,
                "quotes": self._push_quotes,
                "struc-block-trades": self._push_struc_block_trades,
                "public-struc-block-trades": self._push_public_struc_block_trades,
                "public-block-trades": self._push_public_block_trades,
                "block-tickers": self._push_block_tickers,
            }
            handler = special_handlers.get(channel)
            if handler is not None:
                handler(content)
                return

            # Check specific channels first before generic ones to avoid conflicts
            if "tickers" in channel:
                self.push_ticker(content)

            if "candle" in channel:
                self.push_bar(content)
            if "funding-rate" in channel:
                self.push_funding_rate(content)
            if "mark-price" in channel:
                self.push_mark_price(content)
            if "account" in channel:
                self.push_account(content)
            if "order" in channel:
                self.push_order(content)
            if "order" in channel and content["data"][0].get("tradeId") != "":
                self.push_trade(content)
            # Algo order channels
            if "orders-algo" in channel:
                self.push_algo_order(content)
            if "algo-advance" in channel:
                self.push_algo_advance(content)
            if "positions" in channel:
                self.push_position(content)
            if "fills" in channel:
                self.push_fills(content)
            if "liquidation-warning" in channel:
                self.push_liquidation_warning(content)
            if "account-greeks" in channel:
                self.push_account_greeks(content)
            if "trades-all" in channel or "trades" in channel:
                self.push_market_trades(content)
            if "open-interest" in channel:
                self.push_open_interest(content)
            if "price-limit" in channel:
                self.push_price_limit(content)
            if "liquidation-orders" in channel:
                self.push_liquidation_orders(content)
            if "bbo-tbt" in channel:
                self.push_ticker(content)  # BBO is essentially ticker data
            if "opt-trades" in channel:
                self.push_market_trades(content)
            if "call-auction-details" in channel:
                self.push_market_trades(content)  # Use similar handler
            if "opt-summary" in channel:
                self.push_opt_summary(content)
            if "estimated-price" in channel:
                self.push_estimated_price(content)
            if "index-tickers" in channel:
                self.push_index_ticker(content)
            if "instruments" in channel:
                self.push_instruments(content)
            if "adl-warning" in channel:
                self.push_adl_warning(content)
            if "status" in channel:
                self.push_status(content)
            if "index-candle" in channel:
                self.push_bar(content)  # Use same handler as regular candle
            if "mark-price-candle" in channel:
                self.push_bar(content)  # Use same handler as regular candle
            if "economic-calendar" in channel:
                self.push_economic_calendar(content)
            if "deposit-info" in channel:
                self.push_deposit_info(content)
            if "withdrawal-info" in channel:
                self.push_withdrawal_info(content)
            # Grid trading channels
            if "grid-orders-spot" in channel:
                self._push_grid_orders_spot(content)
            if "grid-orders-contract" in channel:
                self._push_grid_orders_contract(content)
            if "grid-positions" in channel:
                self._push_grid_positions(content)
            if "grid-sub-orders" in channel:
                self._push_grid_sub_orders(content)
            # Spread trading channels
            if "sprd-orders" in channel:
                self._push_sprd_orders(content)
            if "sprd-tickers" in channel:
                self._push_sprd_tickers(content)
            # RFQ/Block Trading channels
            if "rfqs" in channel:
                self._push_rfqs(content)
            if "quotes" in channel and "block-tickers" not in channel:
                self._push_quotes(content)
            if "struc-block-trades" in channel:
                self._push_struc_block_trades(content)
            if "public-struc-block-trades" in channel:
                self._push_public_struc_block_trades(content)
            if "public-block-trades" in channel:
                self._push_public_block_trades(content)
            if "block-tickers" in channel:
                self._push_block_tickers(content)

    def push_economic_calendar(self, content: Any) -> None:
        """Handle economic-calendar channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            calendar_info = data[0]
            # Use ticker data container as a generic wrapper for calendar data
            calendar_data = OkxTickerData(calendar_info, "ALL", self.asset_type, True)
            self.data_queue.put(calendar_data)

    def push_mark_price(self, content: Any) -> None:
        """push_mark_price method"""
        mark_price_info = content["data"][0]
        symbol = content["arg"]["instId"]
        mark_price_data = OkxMarkPriceData(mark_price_info, symbol, self.asset_type, True)
        self.data_queue.put(mark_price_data)

    def push_funding_rate(self, content: Any) -> None:
        """push_funding_rate method"""
        funding_rate_info = content["data"][0]
        symbol = content["arg"]["instId"]
        funding_rate_data = OkxFundingRateData(funding_rate_info, symbol, self.asset_type, True)
        self.data_queue.put(funding_rate_data)

    def push_ticker(self, content: Any) -> None:
        """push_ticker method"""
        ticker_info = content["data"][0]
        symbol = content["arg"]["instId"]
        ticker_data = OkxTickerData(ticker_info, symbol, self.asset_type, True)
        self.data_queue.put(ticker_data)

    @staticmethod
    def _update_depth_side(side, levels):
        for level in levels or ():
            if len(level) < 2:
                continue
            normalized = [str(item) for item in level]
            price, quantity = normalized[0], normalized[1]
            if Decimal(quantity) == 0:
                side.pop(price, None)
            else:
                side[price] = normalized

    @staticmethod
    def _sorted_depth_side(side, *, reverse):
        return [side[price] for price in sorted(side, key=Decimal, reverse=reverse)]

    @classmethod
    def _depth_checksum(cls, bids, asks):
        bid_levels = cls._sorted_depth_side(bids, reverse=True)[:25]
        ask_levels = cls._sorted_depth_side(asks, reverse=False)[:25]
        values = []
        for index in range(max(len(bid_levels), len(ask_levels))):
            if index < len(bid_levels):
                values.extend(bid_levels[index][:2])
            if index < len(ask_levels):
                values.extend(ask_levels[index][:2])
        checksum = zlib.crc32(":".join(values).encode("utf-8"))
        return checksum - 2**32 if checksum >= 2**31 else checksum

    @staticmethod
    def _is_valid_snapshot_depth(levels):
        if not isinstance(levels, list) or not levels:
            return False
        for level in levels:
            if not isinstance(level, (list, tuple)) or len(level) < 2:
                return False
            try:
                price = Decimal(str(level[0]))
                quantity = Decimal(str(level[1]))
            except (InvalidOperation, TypeError, ValueError):
                return False
            if not price.is_finite() or not quantity.is_finite() or price <= 0 or quantity <= 0:
                return False
        return True

    def _get_depth_lock(self):
        lock = getattr(self, "_depth_lock", None)
        if lock is None:
            lock = self._depth_lock = threading.RLock()
        return lock

    def _latch_depth_gap(self, key, content, reason):
        """Make a broken book unusable, emit one stale event, and reseed."""
        channel, symbol = key
        gaps = getattr(self, "_depth_gaps", None)
        if gaps is None:
            gaps = self._depth_gaps = set()
        books = getattr(self, "_depth_books", None)
        if books is None:
            books = self._depth_books = {}
        gaps.add(key)
        books.pop(key, None)
        emitted = getattr(self, "_depth_stale_emitted", None)
        if emitted is None:
            emitted = self._depth_stale_emitted = set()
        row = {}
        data = content.get("data") if isinstance(content, dict) else None
        if isinstance(data, list) and data and isinstance(data[0], dict):
            row = data[0]
        if key not in emitted:
            emitted.add(key)
            self.data_queue.put(
                {
                    "kind": "orderbook",
                    "exchange_name": getattr(self, "exchange_name", "OKX"),
                    "asset_type": self.asset_type,
                    "symbol": symbol,
                    "bids": [],
                    "asks": [],
                    "sequence": row.get("seqId"),
                    "previous_sequence": row.get("prevSeqId"),
                    "snapshot_or_delta": "delta",
                    "continuity_status": "gap",
                    "stale": True,
                    "stale_reason": reason,
                    "event_id": f"okx-depth-gap:{channel}:{symbol}:{row.get('seqId', '')}",
                }
            )
        self._request_depth_reseed(key)

    def _request_depth_reseed(self, key):
        requested = getattr(self, "_depth_reseed_requested", None)
        if requested is None:
            requested = self._depth_reseed_requested = set()
        if key in requested:
            return
        requested.add(key)
        callback = getattr(self, "_depth_reseed_callback", None)
        if callback is None:
            callback = self._close_for_depth_reseed
        threading.Thread(
            target=callback,
            args=(key,),
            daemon=True,
            name=f"okx-depth-reseed-{key[1]}",
        ).start()

    def _close_for_depth_reseed(self, _key):
        """Force MyWebsocketApp.run to reconnect and resubscribe all books."""
        stop_event = getattr(self, "_stop_event", None)
        if stop_event is not None and stop_event.is_set():
            return
        ws = getattr(self, "ws", None)
        if ws is not None:
            ws.close()

    def _rebuild_depth(self, symbol: str, content: Any) -> dict[str, Any] | None:
        """Apply one OKX update and return a checksum-verified full snapshot."""
        with self._get_depth_lock():
            return self._rebuild_depth_locked(symbol, content)

    def _rebuild_depth_locked(self, symbol: str, content: Any) -> dict[str, Any] | None:
        order_book_info = dict(content["data"][0])
        channel = str(content.get("arg", {}).get("channel") or "books")
        key = (channel, symbol)
        action = str(content.get("action") or order_book_info.get("action") or "")
        sequence = order_book_info.get("seqId")
        native_previous = order_book_info.get("prevSeqId")
        checksum = order_book_info.get("checksum")
        books = getattr(self, "_depth_books", None)
        if books is None:
            books = self._depth_books = {}
        if channel == "books5":
            try:
                sequence_number = Decimal(str(sequence))
                if (
                    sequence is None
                    or not sequence_number.is_finite()
                    or sequence_number < 0
                    or sequence_number != sequence_number.to_integral_value()
                ):
                    raise ValueError("invalid books5 sequence")
            except (InvalidOperation, TypeError, ValueError):
                self._latch_depth_gap(key, content, "incomplete_snapshot")
                return None
            if not self._is_valid_snapshot_depth(order_book_info.get("bids")) or not (
                self._is_valid_snapshot_depth(order_book_info.get("asks"))
            ):
                self._latch_depth_gap(key, content, "invalid_snapshot_depth")
                return None
            state = {
                "bids": {},
                "asks": {},
                "sequence": int(sequence_number),
            }
            self._update_depth_side(state["bids"], order_book_info["bids"])
            self._update_depth_side(state["asks"], order_book_info["asks"])
            continuity = "snapshot"
        elif action == "snapshot":
            if sequence is None or checksum is None:
                self._latch_depth_gap(key, content, "incomplete_snapshot")
                return None
            state = {"bids": {}, "asks": {}, "sequence": int(sequence)}
            self._update_depth_side(state["bids"], order_book_info.get("bids"))
            self._update_depth_side(state["asks"], order_book_info.get("asks"))
            continuity = "snapshot"
        else:
            state = books.get(key)
            if state is None or key in self._depth_gaps:
                self._latch_depth_gap(key, content, "snapshot_required")
                return None
            previous = state["sequence"]
            if sequence is None or native_previous is None or checksum is None:
                self._latch_depth_gap(key, content, "missing_sequence_or_checksum")
                return None
            if int(sequence) <= previous:
                return None
            if int(native_previous) != previous:
                self._latch_depth_gap(key, content, "sequence_gap")
                return None
            state = {
                "bids": dict(state["bids"]),
                "asks": dict(state["asks"]),
                "sequence": int(sequence),
            }
            self._update_depth_side(state["bids"], order_book_info.get("bids"))
            self._update_depth_side(state["asks"], order_book_info.get("asks"))
            continuity = "continuous"
        if channel != "books5":
            if checksum is None:
                self._latch_depth_gap(key, content, "missing_checksum")
                return None
            if self._depth_checksum(state["bids"], state["asks"]) != int(checksum):
                self._latch_depth_gap(key, content, "checksum_mismatch")
                return None
        books[key] = state
        self._depth_sequences[key] = state["sequence"]
        self._depth_gaps.discard(key)
        getattr(self, "_depth_stale_emitted", set[tuple[str, str]]()).discard(key)
        getattr(self, "_depth_reseed_requested", set[tuple[str, str]]()).discard(key)
        return {
            **order_book_info,
            "action": "snapshot",
            "native_action": action,
            "bids": self._sorted_depth_side(state["bids"], reverse=True),
            "asks": self._sorted_depth_side(state["asks"], reverse=False),
            "snapshot_or_delta": "snapshot",
            "continuity_status": continuity,
            "stale": False,
            "stale_reason": None,
        }

    def push_order_book(self, content: Any) -> None:
        """Push a regular OKX book with explicit continuity metadata."""
        try:
            symbol = content["arg"]["instId"]
            order_book_info = self._rebuild_depth(symbol, content)
        except Exception:
            arg = content.get("arg", {}) if isinstance(content, dict) else {}
            symbol = str(arg.get("instId") or "UNKNOWN")
            channel = str(arg.get("channel") or "books")
            with self._get_depth_lock():
                self._latch_depth_gap((channel, symbol), content, "malformed_depth_payload")
            return
        if order_book_info is None:
            return
        order_book_data = OkxOrderBookData(order_book_info, symbol, self.asset_type, True)
        self.data_queue.put(order_book_data)

    def push_bar(self, content: Any) -> None:
        """push_bar method"""
        bar_info = content["data"][0]
        symbol = content["arg"]["instId"]
        bar_data = OkxBarData(bar_info, symbol, self.asset_type, True)
        self.data_queue.put(bar_data)

    def push_account(self, content: Any) -> None:
        """push_account method"""
        account_info = content["data"][0]
        symbol = "ANY"
        account_data = OkxAccountData(account_info, symbol, self.asset_type, True)
        self.data_queue.put(account_data)

    def push_order(self, content: Any) -> None:
        """push_order method"""
        self.logger.info("order")
        order_info = content["data"][0]
        symbol = content["arg"]["instId"]
        order_data = OkxOrderData(order_info, symbol, self.asset_type, True)
        self.data_queue.put(order_data)
        self.logger.info("order，order_status ：", order_data.get_order_status())

    def push_trade(self, content: Any) -> None:
        """push_trade method"""
        trade_info = content["data"][0]
        symbol = content["arg"]["instId"]
        trade_data = OkxWssTradeData(trade_info, symbol, self.asset_type, True)
        self.data_queue.put(trade_data)

    def push_position(self, content: Any) -> None:
        """push_position method"""
        data = content["data"]
        if len(data) > 0:
            position_info = data[0]
            symbol = content["arg"]["instId"]
            position_data = OkxPositionData(position_info, symbol, self.asset_type, True)
            self.data_queue.put(position_data)

    def push_fills(self, content: Any) -> None:
        """Handle fills channel data."""
        data = content.get("data", [])
        if len(data) > 0:
            fills_info = data[0]
            symbol = content["arg"].get("instId", "ANY")
            fills_data = OkxWssFillsData(fills_info, symbol, self.asset_type, True)
            self.data_queue.put(fills_data)

    def push_liquidation_warning(self, content: Any) -> None:
        """Handle liquidation-warning channel data."""
        data = content.get("data", [])
        if len(data) > 0:
            warning_info = data[0]
            symbol = warning_info.get("instId", "ANY")
            warning_data = OkxLiquidationWarningData(warning_info, symbol, self.asset_type, True)
            self.data_queue.put(warning_data)

    def push_account_greeks(self, content: Any) -> None:
        """Handle account-greeks channel data."""
        data = content.get("data", [])
        if len(data) > 0:
            greeks_info = data[0]
            greeks_data = OkxAccountGreeksData(greeks_info, "ANY", self.asset_type, True)
            self.data_queue.put(greeks_data)

    def push_l2_order_book(self, content: Any) -> None:
        """Handle books-l2-tbt channel data (400 depth tick-by-tick)."""
        try:
            symbol = content["arg"]["instId"]
            order_book_info = self._rebuild_depth(symbol, content)
            if order_book_info is None:
                return
            order_book_data = OkxL2OrderBookData(order_book_info, symbol, self.asset_type, True)
            self.data_queue.put(order_book_data)
        except Exception as e:
            arg = content.get("arg", {}) if isinstance(content, dict) else {}
            symbol = str(arg.get("instId") or "UNKNOWN")
            channel = str(arg.get("channel") or "books-l2-tbt")
            with self._get_depth_lock():
                self._latch_depth_gap((channel, symbol), content, "malformed_depth_payload")
            self.wss_logger.warning("Error in push_l2_order_book: %s", self._safe_failure(e))

    def push_market_trades(self, content: Any) -> None:
        """Handle trades/trades-all channel data (public market trades)."""
        data = content.get("data", [])
        if len(data) > 0:
            # trades channel can return multiple trades in one message
            symbol = content["arg"]["instId"]
            for trade_info in data:
                trade_data = OkxMarketTradeData(trade_info, symbol, self.asset_type, True)
                self.data_queue.put(trade_data)

    def push_open_interest(self, content: Any) -> None:
        """Handle open-interest channel data."""
        open_interest_info = content["data"][0]
        symbol = content["arg"]["instId"]
        open_interest_data = OkxOpenInterestData(open_interest_info, symbol, self.asset_type, True)
        self.data_queue.put(open_interest_data)

    def push_price_limit(self, content: Any) -> None:
        """Handle price-limit channel data."""
        price_limit_info = content["data"][0]
        symbol = content["arg"]["instId"]
        price_limit_data = OkxPriceLimitData(price_limit_info, symbol, self.asset_type, True)
        self.data_queue.put(price_limit_data)

    def push_liquidation_orders(self, content: Any) -> None:
        """Handle liquidation-orders channel data (public liquidation events)."""
        data = content.get("data", [])
        if len(data) > 0:
            for liquidation_info in data:
                symbol = liquidation_info.get("instId", "ANY")
                liquidation_data = OkxLiquidationOrderData(
                    liquidation_info, symbol, self.asset_type, True
                )
                self.data_queue.put(liquidation_data)

    def push_opt_summary(self, content: Any) -> None:
        """Handle opt-summary channel data (option overview)."""
        data = content.get("data", [])
        if len(data) > 0:
            for opt_info in data:
                # Create a generic dict wrapper for option summary data
                symbol = opt_info.get("instFamily", "ANY")
                opt_data = OkxTickerData(opt_info, symbol, self.asset_type, True)
                self.data_queue.put(opt_data)

    def push_estimated_price(self, content: Any) -> None:
        """Handle estimated-price channel data (estimated delivery/exercise price)."""
        data = content.get("data", [])
        if len(data) > 0:
            price_info = data[0]
            symbol = content["arg"].get("instId", "ANY")
            # Use ticker data container as it has similar fields
            price_data = OkxTickerData(price_info, symbol, self.asset_type, True)
            self.data_queue.put(price_data)

    def push_index_ticker(self, content: Any) -> None:
        """Handle index-tickers channel data (index tickers)."""
        data = content.get("data", [])
        if len(data) > 0:
            ticker_info = data[0]
            symbol = content["arg"].get("instId", "ANY")
            ticker_data = OkxTickerData(ticker_info, symbol, self.asset_type, True)
            self.data_queue.put(ticker_data)

    def push_instruments(self, content: Any) -> None:
        """Handle instruments channel data (trading instrument updates)."""
        data = content.get("data", [])
        if len(data) > 0:
            for inst_info in data:
                symbol = inst_info.get("instId", "ANY")
                # Use symbol data container
                symbol_data = OkxSymbolData(inst_info, symbol, self.asset_type)
                self.data_queue.put(symbol_data)

    def push_adl_warning(self, content: Any) -> None:
        """Handle adl-warning channel data (ADL reduction warnings)."""
        data = content.get("data", [])
        if len(data) > 0:
            for warning_info in data:
                symbol = warning_info.get("instId", "ANY")
                # Use similar structure to liquidation warning
                warning_data = OkxLiquidationWarningData(
                    warning_info, symbol, self.asset_type, True
                )
                self.data_queue.put(warning_data)

    def push_status(self, content: Any) -> None:
        """Handle status channel data (system status updates)."""
        data = content.get("data", [])
        if len(data) > 0:
            status_info = data[0]
            # Create a simple dict for status data
            status_data = OkxTickerData(status_info, "SYSTEM", self.asset_type, True)
            self.data_queue.put(status_data)

    def push_algo_order(self, content: Any) -> None:
        """Handle algo-orders channel data (strategy order updates)."""
        data = content.get("data", [])
        if len(data) > 0:
            for algo_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxOrderData container for algo orders
                algo_order_data = OkxOrderData(algo_info, symbol, self.asset_type, True)
                self.data_queue.put(algo_order_data)

    def push_algo_advance(self, content: Any) -> None:
        """Handle algo-advance channel data (advanced strategy order updates)."""
        data = content.get("data", [])
        if len(data) > 0:
            for algo_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxOrderData container for advanced algo orders
                algo_advance_data = OkxOrderData(algo_info, symbol, self.asset_type, True)
                self.data_queue.put(algo_advance_data)

    def push_deposit_info(self, content: Any) -> None:
        """Handle deposit-info channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for deposit_info in data:
                # Use OkxDepositInfoData container for deposit information
                deposit_data = OkxDepositInfoData(deposit_info, "ANY", self.asset_type, True)
                self.data_queue.put(deposit_data)

    def push_withdrawal_info(self, content: Any) -> None:
        """Handle withdrawal-info channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for withdrawal_info in data:
                # Use OkxWithdrawalInfoData container for withdrawal information
                withdrawal_data = OkxWithdrawalInfoData(
                    withdrawal_info, "ANY", self.asset_type, True
                )
                self.data_queue.put(withdrawal_data)

    # Grid Trading Channel Handlers
    def _push_grid_orders_spot(self, content: Any) -> None:
        """Handle grid-orders-spot channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for grid_order_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxOrderData container for grid orders
                grid_order_data = OkxOrderData(grid_order_info, symbol, self.asset_type, True)
                self.data_queue.put(grid_order_data)

    def _push_grid_orders_contract(self, content: Any) -> None:
        """Handle grid-orders-contract channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for grid_order_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxOrderData container for grid orders
                grid_order_data = OkxOrderData(grid_order_info, symbol, self.asset_type, True)
                self.data_queue.put(grid_order_data)

    def _push_grid_positions(self, content: Any) -> None:
        """Handle grid-positions channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for grid_pos_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxPositionData container for grid positions
                grid_pos_data = OkxPositionData(grid_pos_info, symbol, self.asset_type, True)
                self.data_queue.put(grid_pos_data)

    def _push_grid_sub_orders(self, content: Any) -> None:
        """Handle grid-sub-orders channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for grid_sub_order_info in data:
                symbol = content["arg"].get("instId", "ANY")
                # Use OkxOrderData container for grid sub orders
                grid_sub_order_data = OkxOrderData(
                    grid_sub_order_info, symbol, self.asset_type, True
                )
                self.data_queue.put(grid_sub_order_data)

    # Spread Trading Channel Handlers
    def _push_sprd_orders(self, content: Any) -> None:
        """Handle sprd-orders channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for sprd_order_info in data:
                sprd_id = content["arg"].get("sprdId", sprd_order_info.get("sprdId", "ANY"))
                # Use OkxOrderData container for spread orders
                sprd_order_data = OkxOrderData(
                    sprd_order_info, f"SPRD-{sprd_id}", self.asset_type, True
                )
                self.data_queue.put(sprd_order_data)

    def _push_sprd_tickers(self, content: Any) -> None:
        """Handle sprd-tickers channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for sprd_ticker_info in data:
                sprd_id = content["arg"].get("sprdId", sprd_ticker_info.get("sprdId", "ANY"))
                # Use OkxTickerData container for spread tickers
                sprd_ticker_data = OkxTickerData(
                    sprd_ticker_info, f"SPRD-{sprd_id}", self.asset_type, True
                )
                self.data_queue.put(sprd_ticker_data)

    # RFQ/Block Trading Channel Handlers
    def _push_rfqs(self, content: Any) -> None:
        """Handle rfqs channel data (RFQ)."""
        data = content.get("data", [])
        if len(data) > 0:
            for rfq_info in data:
                symbol = content["arg"].get("instId", rfq_info.get("instId", "ANY"))
                # Use OkxOrderData container for RFQ data
                rfq_data = OkxOrderData(rfq_info, symbol, self.asset_type, True)
                self.data_queue.put(rfq_data)

    def _push_quotes(self, content: Any) -> None:
        """Handle quotes channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for quote_info in data:
                symbol = content["arg"].get("instId", quote_info.get("instId", "ANY"))
                # Use OkxOrderData container for quote data
                quote_data = OkxOrderData(quote_info, symbol, self.asset_type, True)
                self.data_queue.put(quote_data)

    def _push_struc_block_trades(self, content: Any) -> None:
        """Handle struc-block-trades channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for block_trade_info in data:
                symbol = content["arg"].get("instId", block_trade_info.get("instId", "ANY"))
                # Use OkxOrderData container for structured block trades
                block_trade_data = OkxOrderData(block_trade_info, symbol, self.asset_type, True)
                self.data_queue.put(block_trade_data)

    def _push_public_struc_block_trades(self, content: Any) -> None:
        """Handle public-struc-block-trades channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for block_trade_info in data:
                symbol = content["arg"].get("instId", block_trade_info.get("instId", "ANY"))
                # Use OkxOrderData container for public structured block trades
                block_trade_data = OkxOrderData(block_trade_info, symbol, self.asset_type, True)
                self.data_queue.put(block_trade_data)

    def _push_public_block_trades(self, content: Any) -> None:
        """Handle public-block-trades channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for block_trade_info in data:
                symbol = content["arg"].get("instId", block_trade_info.get("instId", "ANY"))
                # Use OkxOrderData container for public block trades
                block_trade_data = OkxOrderData(block_trade_info, symbol, self.asset_type, True)
                self.data_queue.put(block_trade_data)

    def _push_block_tickers(self, content: Any) -> None:
        """Handle block-tickers channel data ()."""
        data = content.get("data", [])
        if len(data) > 0:
            for ticker_info in data:
                symbol = content["arg"].get("instId", ticker_info.get("instId", "ANY"))
                # Use OkxTickerData container for block tickers
                ticker_data = OkxTickerData(ticker_info, symbol, self.asset_type, True)
                self.data_queue.put(ticker_data)

    def message_rsp(self, message: Any) -> None:
        """message_rsp method"""
        if message == "pong" or message == b"pong":
            return
        rsp = json.loads(message)
        if "event" in rsp:
            if rsp["event"] == "login":
                if rsp["code"] == "0":
                    with self._subscription_lock:
                        self._pending_subscription_keys.clear()
                    self._begin_subscription_batch()
                    self._init()  # 登录成功后再订阅
                    ready = self._end_subscription_batch()
                    if ready:
                        self._mark_ready()
                    self.wss_logger.info(
                        f"===== {self._params.exchange_name} Data Websocket Connected ====="
                    )
                else:
                    code = sanitize_text(rsp.get("code", "unknown"))
                    message = sanitize_text(rsp.get("msg", "login rejected"))
                    self.wss_logger.warning(f"OKX websocket login failed (code={code}): {message}")
                    self._running_flag = False
                    self._restart_flag = False
                    self._stop_event.set()
                    self._emit_event("ws.auth_failed", code=code, message=message)
                    ws = self.ws
                    if ws is not None:
                        ws.close()
                    return
            elif rsp["event"] == "subscribe":
                code = sanitize_text(rsp.get("code", "0"))
                if code != "0":
                    raise WebSocketSubscriptionError(
                        f"OKX websocket subscription rejected (code={code})",
                        code=code,
                    )
                argument = rsp.get("arg")
                with self._subscription_lock:
                    key = self._subscription_key(argument) if isinstance(argument, dict) else None
                    expected = key in self._pending_subscription_keys
                    if expected and key is not None:
                        self._pending_subscription_keys.remove(key)
                if not expected:
                    self._emit_event("ws.subscription_ack_ignored")
                    return
                self.wss_logger.info("===== Data Websocket %s =====", sanitize_value(rsp))
                self._subscription_acknowledged()
            elif rsp["event"] == "error":
                code = sanitize_text(rsp.get("code", "unknown"))
                raise WebSocketSubscriptionError(
                    f"OKX websocket subscription rejected (code={code})",
                    code=code,
                )
        elif "arg" in rsp:
            self.handle_data(rsp)
            return
        else:
            # Log unknown messages for debugging
            self.wss_logger.info(
                "===== Unknown message: %s =====",
                sanitize_text(message[:200], sensitive_values=self._credential_values()),
            )
