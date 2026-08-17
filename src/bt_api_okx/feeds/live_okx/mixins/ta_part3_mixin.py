"""
OKX API - TradingAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class TradingAccountPart3Mixin:
    """TradingAccountPart3Mixin 方法集合。"""

    def get_collateral_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get collateral assets"""
        path, params, extra_data = self._get_collateral_assets(
            ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_collateral_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get collateral assets"""
        path, params, extra_data = self._get_collateral_assets(
            ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_risk_offset_amt(
        self,
        amt_type: Any,
        uly: Any = None,
        ccy: Any = None,
        inst_type: Any = None,
        offset_amt: Any = None,
        inst_id: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set risk offset amount
        :param amt_type: Offset amount type: `1` Add, `2` Reduce
        :param uly: Underlying
        :param ccy: Currency
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param offset_amt: Offset amount
        :param inst_id: Instrument ID
        :param td_mode: Trade mode: `cross`, `isolated`, `cash`
        :param pos_side: Position side: `long`, `short`, `net`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body (params), extra_data
        """
        request_type = "set_risk_offset_amt"
        body = {"amtType": str(amt_type)}
        if uly:
            body["uly"] = uly
        if ccy:
            body["ccy"] = ccy
        if inst_type:
            body["instType"] = inst_type
        if offset_amt:
            body["offsetAmt"] = str(offset_amt)
        if inst_id:
            request_inst_id = self._params.get_symbol(inst_id)
            body["instId"] = request_inst_id
        if td_mode:
            body["tdMode"] = td_mode
        if pos_side:
            body["posSide"] = pos_side
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_risk_offset_amt_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in body})
        return path, body, extra_data

    @staticmethod
    def _set_risk_offset_amt_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_risk_offset_amt(
        self,
        amt_type: Any,
        uly: Any = None,
        ccy: Any = None,
        inst_type: Any = None,
        offset_amt: Any = None,
        inst_id: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set risk offset amount"""
        path, body, extra_data = self._set_risk_offset_amt(
            amt_type,
            uly,
            ccy,
            inst_type,
            offset_amt,
            inst_id,
            td_mode,
            pos_side,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_risk_offset_amt(
        self,
        amt_type: Any,
        uly: Any = None,
        ccy: Any = None,
        inst_type: Any = None,
        offset_amt: Any = None,
        inst_id: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set risk offset amount"""
        path, body, extra_data = self._set_risk_offset_amt(
            amt_type,
            uly,
            ccy,
            inst_type,
            offset_amt,
            inst_id,
            td_mode,
            pos_side,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Additional Trading Account APIs ====================

    def _activate_option(
        self,
        uly: Any,
        inst_id: Any = None,
        cnt: Any = None,
        amend_px_on: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Activate option trading
        :param uly: Underlying, e.g. `BTC-USD`
        :param inst_id: Instrument ID
        :param cnt: Exercise quantity
        :param amend_px_on: Whether to modify exercise price: `true` or `false`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "activate_option"
        params = {
            "uly": uly,
        }
        if inst_id:
            params["instId"] = inst_id
        if cnt:
            params["cnt"] = cnt
        if amend_px_on:
            params["amendPxOn"] = amend_px_on
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": uly,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._activate_option_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _activate_option_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def activate_option(
        self,
        uly: Any,
        inst_id: Any = None,
        cnt: Any = None,
        amend_px_on: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Activate option trading"""
        path, params, extra_data = self._activate_option(
            uly, inst_id, cnt, amend_px_on, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_activate_option(
        self,
        uly: Any,
        inst_id: Any = None,
        cnt: Any = None,
        amend_px_on: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async activate option trading"""
        path, params, extra_data = self._activate_option(
            uly, inst_id, cnt, amend_px_on, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _move_positions(
        self,
        symbol: Any,
        pos_id: Any,
        ccy: Any,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        """
        Move positions between currencies
        :param symbol: Instrument ID
        :param pos_id: Position ID
        :param ccy: Currency to move to
        :param algo_id: Algo order ID (for pending algo orders)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "move_positions"
        request_symbol = self._params.get_symbol(symbol)
        params = [
            {
                "instId": request_symbol,
                "posId": pos_id,
                "ccy": ccy,
            }
        ]
        if algo_id:
            params[0]["algoId"] = algo_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._move_positions_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _move_positions_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def move_positions(
        self,
        symbol: Any,
        pos_id: Any,
        ccy: Any,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Move positions between currencies"""
        path, params, extra_data = self._move_positions(
            symbol, pos_id, ccy, algo_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_move_positions(
        self,
        symbol: Any,
        pos_id: Any,
        ccy: Any,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async move positions between currencies"""
        path, params, extra_data = self._move_positions(
            symbol, pos_id, ccy, algo_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_move_positions_history(
        self,
        symbol: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get move positions history
        :param symbol: Instrument ID
        :param ccy: Currency
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_move_positions_history"
        params: dict[str, Any] = {}
        if symbol:
            params["instId"] = symbol
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
                "symbol_name": symbol or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_move_positions_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_move_positions_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_move_positions_history(
        self,
        symbol: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get move positions history"""
        path, params, extra_data = self._get_move_positions_history(
            symbol, ccy, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_move_positions_history(
        self,
        symbol: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get move positions history"""
        path, params, extra_data = self._get_move_positions_history(
            symbol, ccy, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_auto_earn(
        self,
        ccy: Any,
        auto_earn: Any,
        auto_earn_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set auto earn (automatic savings)
        :param ccy: Currency, e.g. `USDT`
        :param auto_earn: Auto earn status: `true` or `false`
        :param auto_earn_type: Auto earn type: `1` manual, `2` fast
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "set_auto_earn"
        params = {
            "ccy": ccy,
            "autoEarn": auto_earn,
        }
        if auto_earn_type:
            params["autoEarnType"] = auto_earn_type
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_auto_earn_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_auto_earn_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_auto_earn(
        self,
        ccy: Any,
        auto_earn: Any,
        auto_earn_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set auto earn (automatic savings)"""
        path, params, extra_data = self._set_auto_earn(
            ccy, auto_earn, auto_earn_type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_set_auto_earn(
        self,
        ccy: Any,
        auto_earn: Any,
        auto_earn_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set auto earn (automatic savings)"""
        path, params, extra_data = self._set_auto_earn(
            ccy, auto_earn, auto_earn_type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_settle_currency(
        self, symbol: Any, ccy: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set settlement currency
        :param symbol: Instrument ID
        :param ccy: Settlement currency
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "set_settle_currency"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "ccy": ccy,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_settle_currency_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_settle_currency_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_settle_currency(
        self, symbol: Any, ccy: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Set settlement currency"""
        path, params, extra_data = self._set_settle_currency(
            symbol, ccy, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_set_settle_currency(
        self, symbol: Any, ccy: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set settlement currency"""
        path, params, extra_data = self._set_settle_currency(
            symbol, ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_trading_config(
        self,
        symbol: Any,
        pos_mode: Any = None,
        auto_loan: Any = None,
        auto_margin: Any = None,
        auto_mul: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set trading config
        :param symbol: Instrument ID
        :param pos_mode: Position mode: `net_mode` or `dual_side`
        :param auto_loan: Auto loan: `true` or `false`
        :param auto_margin: Auto margin: `true` or `false`
        :param auto_mul: Auto multiplier
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "set_trading_config"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
        }
        if pos_mode:
            params["posMode"] = pos_mode
        if auto_loan is not None:
            params["autoLoan"] = auto_loan
        if auto_margin is not None:
            params["autoMargin"] = auto_margin
        if auto_mul is not None:
            params["autoMul"] = auto_mul
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_trading_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_trading_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_trading_config(
        self,
        symbol: Any,
        pos_mode: Any = None,
        auto_loan: Any = None,
        auto_margin: Any = None,
        auto_mul: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set trading config"""
        path, params, extra_data = self._set_trading_config(
            symbol, pos_mode, auto_loan, auto_margin, auto_mul, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_set_trading_config(
        self,
        symbol: Any,
        pos_mode: Any = None,
        auto_loan: Any = None,
        auto_margin: Any = None,
        auto_mul: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set trading config"""
        path, params, extra_data = self._set_trading_config(
            symbol, pos_mode, auto_loan, auto_margin, auto_mul, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_delta_neutral_precheck(
        self,
        symbol: Any,
        delta_neutral_precheck: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set delta neutral precheck
        :param symbol: Instrument ID
        :param delta_neutral_precheck: Delta neutral precheck: `true` or `false`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "set_delta_neutral_precheck"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "deltaNeutralPrecheck": delta_neutral_precheck,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_delta_neutral_precheck_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_delta_neutral_precheck_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_delta_neutral_precheck(
        self,
        symbol: Any,
        delta_neutral_precheck: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set delta neutral precheck"""
        path, params, extra_data = self._set_delta_neutral_precheck(
            symbol, delta_neutral_precheck, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_set_delta_neutral_precheck(
        self,
        symbol: Any,
        delta_neutral_precheck: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set delta neutral precheck"""
        path, params, extra_data = self._set_delta_neutral_precheck(
            symbol, delta_neutral_precheck, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Missing Trading Account APIs ====================

    def _get_account_position_risk(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get account position risk"""
        request_type = "get_account_position_risk"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

