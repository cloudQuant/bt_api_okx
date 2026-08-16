"""Module-level docstring."""
from __future__ import annotations

import json
import time

from bt_api_base.containers.balances.balance import BalanceData
from bt_api_base.functions.utils import from_dict_get_float, from_dict_get_string


class OkxBalanceData(BalanceData):
    """Class OkxBalanceData"""
    def __init__(
        self, balance_info, symbol_name, asset_type, has_been_json_encoded=False
    ):
        """__init__ method"""
        super().__init__(balance_info, has_been_json_encoded)
        self.exchange_name = "OKX"
        self.symbol_name = symbol_name
        self.local_update_time = time.time()  # 
        self.asset_type = asset_type
        self.balance_data = balance_info if has_been_json_encoded else None
        self.interest = None
        self.unrealized_profit = None
        self.open_order_initial_margin = None
        self.available_margin = None
        self.position_initial_margin = None
        self.used_margin = None
        self.margin = None
        self.server_time = None
        self.all_data = None
        self.has_been_init_data = False

    def init_data(self):
        """init_data method"""
        if not self.has_been_json_encoded:
            self.balance_data = json.loads(self.balance_info)
            self.has_been_json_encoded = True
        if self.has_been_init_data:
            return self
        # print("self.balance_data = ", self.balance_data)
        self.symbol_name = from_dict_get_string(self.balance_data, "ccy")
        self.server_time = from_dict_get_float(self.balance_data, "uTime")
        self.margin = from_dict_get_float(self.balance_data, "eq")
        self.used_margin = from_dict_get_float(self.balance_data, "frozenBal")
        self.available_margin = from_dict_get_float(self.balance_data, "availBal")
        self.open_order_initial_margin = from_dict_get_float(
            self.balance_data, "frozenBal"
        )
        self.unrealized_profit = from_dict_get_float(self.balance_data, "upl")
        self.interest = from_dict_get_float(self.balance_data, "interest")
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
                "interest": self.interest,
                "unrealized_profit": self.unrealized_profit,
                "open_order_initial_margin": self.open_order_initial_margin,
                "available_margin": self.available_margin,
                "used_margin": self.used_margin,
                "margin": self.margin,
                "server_time": self.server_time,
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
        """# """
        return self.asset_type

    def get_server_time(self):
        """# """
        return self.server_time

    def get_local_update_time(self):
        """# """
        return self.local_update_time

    def get_account_id(self):
        """# id"""
        return

    def get_account_type(self):
        """# """
        return

    def get_fee_tier(self):
        """# """
        return

    def get_max_withdraw_amount(self):
        """# """
        return

    def get_margin(self):
        """# """
        return self.margin

    def get_used_margin(self):
        """# """
        return self.used_margin

    def get_maintain_margin(self):
        """# """
        return

    def get_available_margin(self):
        """# """
        return self.available_margin

    def get_open_order_initial_margin(self):
        """# """
        return self.open_order_initial_margin

    def get_position_initial_margin(self):
        """# """
        return self.position_initial_margin

    def get_unrealized_profit(self):
        """# """
        return self.unrealized_profit

    def get_interest(self):
        """# """
        return self.interest
