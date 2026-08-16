"""
OKX Market Trade Data Container - Public trade data from trades/trades-all channels.
"""

from __future__ import annotations

import json
import time

from bt_api_base.containers.trades.trade import TradeData
from bt_api_base.functions.utils import from_dict_get_float, from_dict_get_string


class OkxMarketTradeData(TradeData):
    """OKX market trade data from public trades channel.

    This is for public market trades, not account-specific trades.
    The data structure differs from account trades.
    """

    def __init__(
        self, trade_info, symbol_name, asset_type, has_been_json_encoded=False
    ):
        """__init__ method"""
        super().__init__(trade_info, has_been_json_encoded)
        self.exchange_name = "OKX"
        self.local_update_time = time.time()
        self.asset_type = asset_type
        self.symbol_name = symbol_name
        self.trade_data = trade_info if has_been_json_encoded else None
        self.has_been_init_data = False

    def init_data(self):
        """init_data method"""
        if not self.has_been_json_encoded:
            self.trade_data = json.loads(self.trade_info)
            self.has_been_json_encoded = True
        if self.has_been_init_data:
            return self

        # Public trade format: [tradeId, price, size, side, timestamp]
        # Or in some cases a dict with keys
        if isinstance(self.trade_data, list):
            self.trade_id = from_dict_get_float(self.trade_data, 0)  # tradeId
            self.trade_price = from_dict_get_float(self.trade_data, 1)  # price
            self.trade_volume = from_dict_get_float(self.trade_data, 2)  # size
            self.trade_side = from_dict_get_string(
                self.trade_data, 3
            )  # side (buy/sell)
            self.server_time = from_dict_get_float(self.trade_data, 4)  # timestamp
            self.trade_symbol_name = None  # Not in the trade data itself
        else:
            # Dict format
            self.trade_id = from_dict_get_float(self.trade_data, "tradeId")
            self.trade_price = from_dict_get_float(self.trade_data, "px")
            self.trade_volume = from_dict_get_float(self.trade_data, "sz")
            self.trade_side = from_dict_get_string(self.trade_data, "side")
            self.server_time = from_dict_get_float(self.trade_data, "ts")
            self.trade_symbol_name = from_dict_get_string(self.trade_data, "instId")

        self.order_id = None  # Public trades don't have order ID
        self.client_order_id = None
        self.trade_type = None  # Not applicable for public trades
        self.trade_time = self.server_time
        self.trade_fee = None  # Not applicable for public trades
        self.trade_fee_symbol = None
        self.trade_accumulate_volume = self.trade_volume

        self.has_been_init_data = True
        return self

    def get_all_data(self):
        """get_all_data method"""
        if self.all_data is None:
            self.all_data = {
                "exchange_name": self.exchange_name,
                "symbol_name": self.symbol_name,
                "local_update_time": self.local_update_time,
                "asset_type": self.asset_type,
                "server_time": self.server_time,
                "trade_symbol_name": self.trade_symbol_name,
                "trade_side": self.trade_side,
                "trade_price": self.trade_price,
                "trade_volume": self.trade_volume,
                "trade_type": self.trade_type,
                "trade_time": self.trade_time,
                "trade_id": self.trade_id,
                "order_id": self.order_id,
                "client_order_id": self.client_order_id,
            }
        return self.all_data

    def get_exchange_name(self):
        """get_exchange_name method"""
        return self.exchange_name

    def get_asset_type(self):
        """get_asset_type method"""
        return self.asset_type

    def get_server_time(self):
        """get_server_time method"""
        return self.server_time

    def get_local_update_time(self):
        """get_local_update_time method"""
        return self.local_update_time

    def get_trade_id(self):
        """get_trade_id method"""
        return self.trade_id

    def get_trade_symbol_name(self):
        """get_trade_symbol_name method"""
        return self.trade_symbol_name

    def get_order_id(self):
        """get_order_id method"""
        return self.order_id

    def get_client_order_id(self):
        """get_client_order_id method"""
        return self.client_order_id

    def get_trade_side(self):
        """get_trade_side method"""
        return self.trade_side

    def get_trade_offset(self):
        """get_trade_offset method"""
        return None

    def get_trade_price(self):
        """get_trade_price method"""
        return self.trade_price

    def get_trade_volume(self):
        """get_trade_volume method"""
        return self.trade_volume

    def get_trade_accumulate_volume(self):
        """get_trade_accumulate_volume method"""
        return self.trade_accumulate_volume

    def get_trade_type(self):
        """get_trade_type method"""
        return self.trade_type

    def get_trade_time(self):
        """get_trade_time method"""
        return self.trade_time

    def get_trade_fee(self):
        """get_trade_fee method"""
        return self.trade_fee

    def get_trade_fee_symbol(self):
        """get_trade_fee_symbol method"""
        return self.trade_fee_symbol

    def __str__(self):
        self.init_data()
        return json.dumps(self.get_all_data())

    def __repr__(self):
        return self.__str__()
