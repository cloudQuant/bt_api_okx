"""
OKX API - TradingAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class TradingAccountPart1Mixin:
    """TradingAccountPart1Mixin 方法集合。"""

    def _get_interest_limits(
        self,
        ccy: str | None = None,
        inst_type: str | None = None,
        mgn_mode: str | None = None,
        uly: str | None = None,
        inst_family: str | None = None,
        extra_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get interest limit and interest rate
        :param ccy: Currency
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param mgn_mode: Margin mode: `cross`, `isolated`
        :param uly: Underlying
        :param inst_family: Instrument family
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_interest_limits"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if inst_type:
            params["instType"] = inst_type
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        if uly:
            params["uly"] = uly
        if inst_family:
            params["instFamily"] = inst_family
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_interest_limits_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_interest_limits_normalize_function(
        input_data: dict[str, Any], extra_data: dict[str, Any]
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_interest_limits(
        self,
        ccy: str | None = None,
        inst_type: str | None = None,
        mgn_mode: str | None = None,
        uly: str | None = None,
        inst_family: str | None = None,
        extra_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        """Get interest limit and interest rate"""
        path, params, extra_data = self._get_interest_limits(
            ccy, inst_type, mgn_mode, uly, inst_family, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_interest_limits(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        mgn_mode: Any = None,
        uly: Any = None,
        inst_family: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get interest limit and interest rate"""
        path, params, extra_data = self._get_interest_limits(
            ccy, inst_type, mgn_mode, uly, inst_family, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_fee_type(
        self, fee_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set fee rate tier
        :param fee_type: Fee rate tier, default is 1, 2, 3, 4, 5
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "set_fee_type"
        body = {
            "feeType": str(fee_type),
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_fee_type_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _set_fee_type_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_fee_type(self, fee_type: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        """Set fee rate tier"""
        path, body, extra_data = self._set_fee_type(fee_type, extra_data, **kwargs)
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_fee_type(
        self, fee_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set fee rate tier"""
        path, body, extra_data = self._set_fee_type(fee_type, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_greeks(
        self, greeks_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set Greeks display type
        :param greeks_type: Greeks display type: `PA` PA price, `IV` IV
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "set_greeks"
        body = {
            "greeksType": greeks_type,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_greeks_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _set_greeks_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_greeks(
        self, greeks_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Set Greeks display type"""
        path, body, extra_data = self._set_greeks(greeks_type, extra_data, **kwargs)
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_greeks(
        self, greeks_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set Greeks display type"""
        path, body, extra_data = self._set_greeks(greeks_type, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_isolated_mode(
        self, symbol: Any, iso_mode: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set isolated margin mode
        :param symbol: Instrument ID, e.g. "BTC-USDT"
        :param iso_mode: Isolated margin mode: `automatic`, `non-automatic`, `autonomy`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "set_isolated_mode"
        request_symbol = self._params.get_symbol(symbol)
        body = {
            "instId": request_symbol,
            "isoMode": iso_mode,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_isolated_mode_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _set_isolated_mode_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_isolated_mode(
        self, symbol: Any, iso_mode: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Set isolated margin mode"""
        path, body, extra_data = self._set_isolated_mode(
            symbol, iso_mode, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_isolated_mode(
        self, symbol: Any, iso_mode: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set isolated margin mode"""
        path, body, extra_data = self._set_isolated_mode(
            symbol, iso_mode, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _borrow_repay(
        self,
        ccy: Any,
        side: Any,
        amt: Any,
        mgn_mode: Any = None,
        symbol: Any = None,
        auto: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Manual borrow or repay for cross/isolated margin
        :param ccy: Currency, e.g. `BTC`
        :param side: Side: `borrow`, `repay`
        :param amt: The amount to borrow or repay
        :param mgn_mode: Margin mode: `cross`, `isolated`
        :param symbol: Instrument ID, required for isolated margin
        :param auto: Auto loan repayment: `true`, `false`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "borrow_repay"
        body = {
            "ccy": ccy,
            "side": side,
            "amt": str(amt),
        }
        if mgn_mode:
            body["mgnMode"] = mgn_mode
        if symbol:
            request_symbol = self._params.get_symbol(symbol)
            body["instId"] = request_symbol
        if auto is not None:
            body["auto"] = auto
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._borrow_repay_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _borrow_repay_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def borrow_repay(
        self,
        ccy: Any,
        side: Any,
        amt: Any,
        mgn_mode: Any = None,
        symbol: Any = None,
        auto: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Manual borrow or repay for cross/isolated margin"""
        path, body, extra_data = self._borrow_repay(
            ccy, side, amt, mgn_mode, symbol, auto, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_borrow_repay(
        self,
        ccy: Any,
        side: Any,
        amt: Any,
        mgn_mode: Any = None,
        symbol: Any = None,
        auto: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async manual borrow or repay for cross/isolated margin"""
        path, body, extra_data = self._borrow_repay(
            ccy, side, amt, mgn_mode, symbol, auto, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_auto_repay(
        self, auto_repay: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set auto loan repayment
        :param auto_repay: Auto loan repayment: `true`, `false`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "set_auto_repay"
        body = {
            "autoRepay": auto_repay,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_auto_repay_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _set_auto_repay_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_auto_repay(
        self, auto_repay: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Set auto loan repayment"""
        path, body, extra_data = self._set_auto_repay(auto_repay, extra_data, **kwargs)
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_auto_repay(
        self, auto_repay: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set auto loan repayment"""
        path, body, extra_data = self._set_auto_repay(auto_repay, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_borrow_repay_history(
        self,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get borrowing and repayment history (last 3 months)
        :param ccy: Currency, e.g. `BTC`
        :param mgn_mode: Margin mode: `cross`, `isolated`
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_borrow_repay_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if mgn_mode:
            params["mgnMode"] = mgn_mode
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
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_borrow_repay_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_borrow_repay_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_borrow_repay_history(
        self,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get borrowing and repayment history (last 3 months)"""
        path, params, extra_data = self._get_borrow_repay_history(
            ccy, mgn_mode, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_borrow_repay_history(
        self,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get borrowing and repayment history (last 3 months)"""
        path, params, extra_data = self._get_borrow_repay_history(
            ccy, mgn_mode, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== MMP (Market Maker Protection) APIs ====================

    def _mmp_reset(
        self, inst_type: Any, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Reset MMP (Market Maker Protection) status
        :param inst_type: Instrument type, e.g. `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param symbol: Instrument ID (optional)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "mmp_reset"
        params = {
            "instType": inst_type,
        }
        if symbol:
            params["instId"] = symbol
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._mmp_reset_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _mmp_reset_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def mmp_reset(
        self, inst_type: Any, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Reset MMP (Market Maker Protection) status"""
        path, params, extra_data = self._mmp_reset(
            inst_type, symbol, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_mmp_reset(
        self, inst_type: Any, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async reset MMP (Market Maker Protection) status"""
        path, params, extra_data = self._mmp_reset(
            inst_type, symbol, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_mmp_config(
        self,
        inst_type: Any,
        symbol: Any = None,
        time_interval_frozen: Any = None,
        algo_orders_frozen: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set MMP (Market Maker Protection) configuration
        :param inst_type: Instrument type, e.g. `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param symbol: Instrument ID (optional)
        :param time_interval_frozen: Frozen period in milliseconds after triggered
        :param algo_orders_frozen: Whether to freeze algo orders: `true` or `false`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "set_mmp_config"
        params = {
            "instType": inst_type,
        }
        if symbol:
            params["instId"] = symbol
        if time_interval_frozen is not None:
            params["timeIntervalFrozen"] = time_interval_frozen
        if algo_orders_frozen is not None:
            params["algoOrdersFrozen"] = str(algo_orders_frozen).lower()
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_mmp_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_mmp_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_mmp_config(
        self,
        inst_type: Any,
        symbol: Any = None,
        time_interval_frozen: Any = None,
        algo_orders_frozen: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set MMP (Market Maker Protection) configuration"""
        path, params, extra_data = self._set_mmp_config(
            inst_type,
            symbol,
            time_interval_frozen,
            algo_orders_frozen,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

