"""
OKX API - AccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.accounts.okx_account import OkxAccountData
from bt_api_okx.containers.positions.okx_position import OkxPositionData
from bt_api_base.functions.utils import update_extra_data


class AccountMixinPart1:
    """AccountMixinPart1 方法集合。"""

    def _get_account(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        get account info using async
        :param symbol: default None, get all the currency, can be string, e.g. "BTC-USDT".
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: RequestData
        """
        request_type = "get_account"
        path = self._params.get_rest_path(request_type)
        if symbol is None:
            params = {"ccy": ""}
            extra_data = update_extra_data(
                extra_data,
                **{
                    "request_type": request_type,
                    "symbol_name": "ALL",
                    "asset_type": self.asset_type,
                    "exchange_name": self.exchange_name,
                    "normalize_function": AccountMixin._get_account_normalize_function,
                },
            )
        else:
            params = {"ccy": symbol}
            extra_data = update_extra_data(
                extra_data,
                **{
                    "request_type": request_type,
                    "symbol_name": symbol,
                    "asset_type": self.asset_type,
                    "exchange_name": self.exchange_name,
                    "normalize_function": self._get_account_normalize_function,
                },
            )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_account_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"][0]
        if len(data) > 0:
            data_list = [
                OkxAccountData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_account(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """get_account method"""
        path, params, extra_data = self._get_account(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def get_balance(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """get_balance method"""
        return self.get_account(symbol, extra_data, **kwargs)

    def async_get_account(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_account method"""
        path, params, extra_data = self._get_account(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, extra_data=extra_data),
            callback=self.async_callback,
        )

    def async_get_balance(self, extra_data: Any = None, **kwargs: Any) -> None:
        """async_get_balance method"""
        path = self._params.get_rest_path("get_balance_assert")
        self.submit(
            self.async_request(path, extra_data=extra_data),
            callback=self.async_callback,
        )

    def async_sub_account(self, extra_data: Any = None) -> None:
        """async_sub_account method"""
        path = self._params.get_rest_path("sub_account")
        params = {"subAcct": "xxx"}
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Position APIs ====================

    def _get_position(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        get position info from okx by symbol
        :param symbol: default None, get all the currency, can be string, e.g. "BTC-USDT".
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: RequestData
        """
        _request_symbol = self._params.get_symbol(symbol)
        request_type = "get_position"
        path = self._params.get_rest_path(request_type)
        params = {"instType": "", "instId": symbol, "posId": ""}
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": AccountMixin._get_position_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_position_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxPositionData(
                    data[0], extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_position(self, symbol: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        """get_position method"""
        path, params, extra_data = self._get_position(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_position(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_position method"""
        path, params, extra_data = self._get_position(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_positions_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get positions history
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param uly: Underlying, e.g. BTC-USD
        :param inst_id: Instrument ID
        :param mgn_mode: Margin mode, cross or isolated
        :param ccy: Currency
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_positions_history"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": AccountMixin._get_positions_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_positions_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize positions history data"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxPositionData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_positions_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get positions history"""
        path, params, extra_data = self._get_positions_history(
            inst_type,
            uly,
            inst_id,
            mgn_mode,
            ccy,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_positions_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get positions history"""
        path, params, extra_data = self._get_positions_history(
            inst_type,
            uly,
            inst_id,
            mgn_mode,
            ccy,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Config APIs ====================

    def _get_config(
        self, extra_data: Any = None
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        params: dict[str, Any] = {}
        path = self._params.get_rest_path("get_config")
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": "get_config",
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": AccountMixin._get_config_normalize_function,
            },
        )
        return path, params, extra_data

    @staticmethod
    def _generic_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Generic normalize function for OKX API responses.
        Extracts 'data' list and checks 'code' for status."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if isinstance(data, list):
            return data, status
        return [data] if data else [], status

    @staticmethod
    def _get_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        if extra_data is None:
            pass
        data = input_data["data"]
        data = data if len(data) > 0 else []
        return data, status

    def get_config(self, extra_data: Any = None) -> Any:
        """get_config method"""
        path, params, extra_data = self._get_config(extra_data=extra_data)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

