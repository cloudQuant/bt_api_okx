"""Module-level docstring."""
from __future__ import annotations

import json
import time

from bt_api_base.containers.trades.trade import TradeData
from bt_api_base.functions.utils import from_dict_get_float, from_dict_get_string


class OkxTradeData(TradeData):
    """，"""

    def __init__(
        self, trade_info, symbol_name, asset_type, has_been_json_encoded=False
    ):
        """__init__ method"""
        super().__init__(trade_info, has_been_json_encoded)
        self.exchange_name = "OKX"
        self.local_update_time = time.time()  # 
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
        self.server_time = self._get_server_time()
        self.trade_id = from_dict_get_float(self.trade_data, "tradeId")
        self.trade_symbol_name = from_dict_get_string(self.trade_data, "instId")
        self.order_id = from_dict_get_string(self.trade_data, "ordId")
        self.client_order_id = from_dict_get_string(self.trade_data, "clOrdId")
        self.trade_side = from_dict_get_string(self.trade_data, "side")
        self.trade_price = from_dict_get_float(self.trade_data, "fillPx")
        self.trade_volume = from_dict_get_float(self.trade_data, "fillSz")
        trade_type = from_dict_get_string(self.trade_data, "execType")
        self.trade_type = "maker" if trade_type == "M" else "taker"
        self.trade_time = from_dict_get_float(self.trade_data, "fillTime")
        self.trade_fee = from_dict_get_float(self.trade_data, "fee")
        self.trade_fee_symbol = from_dict_get_string(self.trade_data, "feeCcy")
        self.has_been_init_data = True
        return self

    def _get_server_time(self):
        raise NotImplementedError

    def get_exchange_name(self):
        """# """
        return self.exchange_name

    def get_symbol_name(self):
        """# symbol"""
        return self.symbol_name

    def get_asset_type(self):
        """# """
        return self.asset_type

    def get_server_time(self):
        """# """
        return self.server_time

    def get_local_update_time(self):
        """# """
        return self.local_update_time

    def get_trade_id(self):
        """# id"""
        return self.trade_id

    def get_trade_symbol_name(self):
        """# symbol"""
        return self.trade_symbol_name

    def get_order_id(self):
        """# id"""
        return self.order_id

    def get_client_order_id(self):
        """# Id"""
        return self.client_order_id

    def get_trade_side(self):
        """# """
        return self.trade_side

    def get_trade_offset(self):
        """# offset"""
        return

    def get_trade_price(self):
        """# """
        return self.trade_price

    def get_trade_volume(self):
        """# """
        return self.trade_volume

    def get_trade_accumulate_volume(self):
        """# """
        return self.trade_accumulate_volume

    def get_trade_type(self):
        """# ，makertaker"""
        return self.trade_type

    def get_trade_time(self):
        """# """
        return self.trade_time

    def get_trade_fee(self):
        """# """
        return self.trade_fee

    def get_trade_fee_symbol(self):
        """"""
        return self.trade_fee_symbol

    def __str__(self):
        self.init_data()
        return json.dumps(self.get_all_data())

    def __repr__(self):
        return self.__str__()


class OkxRequestTradeData(OkxTradeData):
    """，"""

    def _get_server_time(self):
        return from_dict_get_float(self.trade_data, "ts")


class OkxWssTradeData(OkxTradeData):
    """，order"""

    def _get_server_time(self):
        return from_dict_get_float(self.trade_data, "uTime")


class OkxWssFillsData(OkxTradeData):
    """Fills channel data container.

    WebSocket channel: fills
    Pushes when a trade is filled.

    Example data:
    {
        "arg": {"channel": "fills", "instType": "SWAP", "instId": "BTC-USDT-SWAP"},
        "data": [{
            "tradeId": "123",
            "instId": "BTC-USDT-SWAP",
            "ordId": "312269865356374016",
            "clOrdId": "b16",
            "billId": "1111",
            "tag": "",
            "fillPx": "999",
            "fillSz": "3",
            "side": "buy",
            "posSide": "long",
            "execType": "M",
            "feeCcy": "USDT",
            "fee": "-0.02522168",
            "ts": "1597026383085",
            "fillTime": "1597026383084"
        }]
    }
    """

    def _get_server_time(self):
        return from_dict_get_float(self.trade_data, "fillTime")
