"""Module-level docstring."""
from __future__ import annotations

import json
import time
from typing import Any

from bt_api_base.containers.orders.order import OrderData, OrderStatus
from bt_api_base.functions.utils import (
    from_dict_get_bool,
    from_dict_get_float,
    from_dict_get_string,
)


class OkxOrderData(OrderData):
    """，"""

    def __init__(
        self, order_info, symbol_name, asset_type, has_been_json_encoded=False
    ) -> None:
        """__init__ method"""
        super().__init__(order_info, has_been_json_encoded)
        self.exchange_name = "OKX"
        self.symbol_name = symbol_name
        self.local_update_time = time.time()  # 
        self.asset_type = asset_type
        self.order_data = self.order_info if has_been_json_encoded else None
        self.server_time = None
        self.trade_id = None
        self.client_order_id = None
        self.executed_qty = None
        self.order_id = None
        self.order_size = None
        self.order_price = None
        self.reduce_only = None
        self.order_side = None
        self.order_status = None
        self.order_symbol_name = None
        self.order_type = None
        self.order_avg_price = None
        self.position_side = None
        self.take_profit_price = None
        self.take_profit_trigger_price = None
        self.take_profit_trigger_price_type = None
        self.stop_loss_price = None
        self.stop_loss_trigger_price = None
        self.stop_loss_trigger_price_type = None
        self.all_data: dict[str, Any] | None = None
        self.has_been_init_data = False

    def init_data(self) -> OkxOrderData:
        """init_data method"""
        if not self.has_been_json_encoded:
            self.order_info = json.loads(self.order_info)
            self.order_data = self.order_info["data"]
            self.has_been_json_encoded = True
        if self.has_been_init_data:
            return self
        self.server_time = from_dict_get_float(self.order_data, "uTime")
        self.trade_id = from_dict_get_float(self.order_data, "tradeId")
        self.client_order_id = from_dict_get_string(self.order_data, "clOrdId")
        self.executed_qty = from_dict_get_float(self.order_data, "accFillSz")
        self.order_id = from_dict_get_string(self.order_data, "ordId")
        self.order_size = from_dict_get_float(self.order_data, "sz")
        self.order_price = from_dict_get_float(self.order_data, "px")
        self.reduce_only = from_dict_get_bool(self.order_data, "reduceOnly")
        self.order_side = from_dict_get_string(self.order_data, "side")
        okx_order_status = from_dict_get_string(self.order_data, "state")
        self.order_status = OrderStatus.from_value(okx_order_status)
        self.order_symbol_name = from_dict_get_string(self.order_data, "instId")
        self.order_type = from_dict_get_string(self.order_data, "ordType")
        self.order_avg_price = from_dict_get_float(self.order_data, "avgPx")
        self.position_side = from_dict_get_string(self.order_data, "posSide")
        self.take_profit_price = from_dict_get_float(self.order_data, "tpOrdPx")
        self.take_profit_trigger_price = from_dict_get_float(
            self.order_data, "tpTriggerPx"
        )
        self.take_profit_trigger_price_type = from_dict_get_string(
            self.order_data, "tpTriggerPxType"
        )
        self.stop_loss_price = from_dict_get_float(self.order_data, "slOrdPx")
        self.stop_loss_trigger_price = from_dict_get_float(
            self.order_data, "slTriggerPx"
        )
        self.stop_loss_trigger_price_type = from_dict_get_string(
            self.order_data, "slTriggerPxType"
        )
        self.has_been_init_data = True
        return self

    def get_all_data(self) -> dict[str, Any]:
        """get_all_data method"""
        if self.all_data is None:
            order_status_val = ""
            if self.order_status is not None:
                order_status_val = self.order_status.value
            self.all_data = {
                "exchange_name": self.exchange_name,
                "symbol_name": self.symbol_name,
                "server_time": self.server_time,
                "local_update_time": self.local_update_time,
                "asset_type": self.asset_type,
                "order_id": self.order_id,
                "client_order_id": self.client_order_id,
                "order_symbol_name": self.order_symbol_name,
                "order_type": self.order_type,
                "order_status": order_status_val,
                "order_size": self.order_size,
                "order_price": self.order_price,
                "trade_id": self.trade_id,
                "position_side": self.position_side,
                "executed_qty": self.executed_qty,
                "order_avg_price": self.order_avg_price,
                "reduce_only": self.reduce_only,
                "take_profit_price": self.take_profit_price,
                "take_profit_trigger_price": self.take_profit_trigger_price,
                "take_profit_trigger_price_type": self.take_profit_trigger_price_type,
                "stop_loss_price": self.stop_loss_price,
                "stop_loss_trigger_price": self.stop_loss_trigger_price,
                "stop_loss_trigger_price_type": self.stop_loss_trigger_price_type,
            }
        return self.all_data

    def __str__(self):
        self.init_data()
        return json.dumps(self.get_all_data())

    def __repr__(self):
        return self.__str__()

    def get_exchange_name(self):
        """# """
        return self.exchange_name

    def get_symbol_name(self):
        """# """
        return self.symbol_name

    def get_asset_type(self):
        """get_asset_type method"""
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

    def get_client_order_id(self):
        """# ID"""
        return self.client_order_id

    def get_cum_quote(self):
        """# ?"""
        return

    def get_executed_qty(self):
        """# """
        return self.executed_qty

    def get_order_id(self):
        """# id"""
        return self.order_id

    def get_order_size(self):
        """# """
        return self.order_size

    def get_order_price(self):
        """# """
        return self.order_price

    def get_reduce_only(self):
        """# """
        return self.reduce_only

    def get_order_side(self):
        """# """
        return self.order_side

    def get_order_status(self):
        """# """
        return self.order_status

    def get_trailing_stop_price(self):
        """get_trailing_stop_price method"""
        return None

    def get_trailing_stop_trigger_price(self):
        """get_trailing_stop_trigger_price method"""
        return None

    def get_trailing_stop_trigger_price_type(self):
        """get_trailing_stop_trigger_price_type method"""
        return None

    def get_trailing_stop_callback_rate(self):
        """# """
        return

    def get_order_symbol_name(self):
        """# """
        return self.order_symbol_name

    def get_order_time_in_force(self):
        """# """
        return self.get_order_type()

    def get_order_type(self):
        """# """
        return self.order_type

    def get_order_avg_price(self):
        """# """
        return self.order_avg_price

    def get_origin_order_type(self):
        """# """
        return

    def get_position_side(self):
        """# """
        return self.position_side

    def get_close_position(self):
        """# ; """
        return

    def get_take_profit_price(self):
        """# get_take_profit_price"""
        return self.take_profit_price

    def get_take_profit_trigger_price(self):
        """# get take profit trigger_price"""
        return self.take_profit_trigger_price

    def get_take_profit_trigger_price_type(self):
        """# get take profit trigger_price_type"""
        return self.take_profit_trigger_price_type

    def get_stop_loss_price(self):
        """# """
        return self.stop_loss_price

    def get_stop_loss_trigger_price(self):
        """# """
        return self.stop_loss_trigger_price

    def get_stop_loss_trigger_price_type(self):
        """# """
        return self.stop_loss_trigger_price_type
