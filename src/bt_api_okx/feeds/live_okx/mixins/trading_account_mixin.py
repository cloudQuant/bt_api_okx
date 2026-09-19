"""
OKX API - TradingAccountMixin

由机械切分的 ``*_partN`` 模块合并而来（迭代07 结构治理）。
"""

from __future__ import annotations

from typing import Any

from bt_api_base.functions.utils import update_extra_data

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_okx.feeds.live_okx.mixins.rest_call_mixin import RestCallMixin


class TradingAccountMixin(RestCallMixin):
    """TradingAccountMixin 方法集合（OKX REST 端点）。"""
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
        return self._finish(
            "get_interest_limits",
            params,
            extra_data,
            ccy or "ALL",
            TradingAccountMixin._get_interest_limits_normalize_function,
            kwargs,
        )

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
        return self._rest("get_interest_limits", ccy, inst_type, mgn_mode, uly, inst_family, extra_data, **kwargs)

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
        return self._rest_async("get_interest_limits", ccy, inst_type, mgn_mode, uly, inst_family, extra_data, **kwargs)

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
        return self._finish(
            "get_borrow_repay_history",
            params,
            extra_data,
            ccy or "ALL",
            TradingAccountMixin._get_borrow_repay_history_normalize_function,
            kwargs,
        )

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
        return self._rest("get_borrow_repay_history", ccy, mgn_mode, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_borrow_repay_history", ccy, mgn_mode, after, before, limit, extra_data, **kwargs)

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
        params = {
            "instType": inst_type,
        }
        if symbol:
            params["instId"] = symbol
        return self._finish(
            "mmp_reset",
            params,
            extra_data,
            symbol or "ALL",
            TradingAccountMixin._mmp_reset_normalize_function,
            kwargs,
        )

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
        params = {
            "instType": inst_type,
        }
        if symbol:
            params["instId"] = symbol
        if time_interval_frozen is not None:
            params["timeIntervalFrozen"] = time_interval_frozen
        if algo_orders_frozen is not None:
            params["algoOrdersFrozen"] = str(algo_orders_frozen).lower()
        return self._finish(
            "set_mmp_config",
            params,
            extra_data,
            symbol or "ALL",
            TradingAccountMixin._set_mmp_config_normalize_function,
            kwargs,
        )

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

    def async_set_mmp_config(
        self,
        inst_type: Any,
        symbol: Any = None,
        time_interval_frozen: Any = None,
        algo_orders_frozen: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set MMP (Market Maker Protection) configuration"""
        path, params, extra_data = self._set_mmp_config(
            inst_type,
            symbol,
            time_interval_frozen,
            algo_orders_frozen,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_mmp_config(
        self, inst_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get MMP (Market Maker Protection) configuration
        :param inst_type: Instrument type, e.g. `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        params = {
            "instType": inst_type,
        }
        return self._finish(
            "get_mmp_config",
            params,
            extra_data,
            "ALL",
            TradingAccountMixin._get_mmp_config_normalize_function,
            kwargs,
        )

    @staticmethod
    def _get_mmp_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_mmp_config(
        self, inst_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get MMP (Market Maker Protection) configuration"""
        return self._rest("get_mmp_config", inst_type, extra_data, **kwargs)

    def async_get_mmp_config(
        self, inst_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get MMP (Market Maker Protection) configuration"""
        return self._rest_async("get_mmp_config", inst_type, extra_data, **kwargs)

    def _apply_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Apply for historical bills archive (from 2021)
        :param year: Year, e.g. `2023`, `2024`
        :param ccy: Currency (optional)
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        params = {
            "year": str(year),
        }
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        return self._finish(
            "apply_bills_history_archive",
            params,
            extra_data,
            ccy or "ALL",
            TradingAccountMixin._apply_bills_history_archive_normalize_function,
            kwargs,
        )

    @staticmethod
    def _apply_bills_history_archive_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def apply_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Apply for historical bills archive (from 2021)"""
        path, params, extra_data = self._apply_bills_history_archive(
            year, ccy, after, before, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_apply_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async apply for historical bills archive (from 2021)"""
        path, params, extra_data = self._apply_bills_history_archive(
            year, ccy, after, before, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get historical bills archive (from 2021)
        :param year: Year, e.g. `2023`, `2024`
        :param ccy: Currency (optional)
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        params = {
            "year": str(year),
        }
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        return self._finish(
            "get_bills_history_archive",
            params,
            extra_data,
            ccy or "ALL",
            TradingAccountMixin._get_bills_history_archive_normalize_function,
            kwargs,
        )

    @staticmethod
    def _get_bills_history_archive_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get historical bills archive (from 2021)"""
        return self._rest("get_bills_history_archive", year, ccy, after, before, extra_data, **kwargs)

    def async_get_bills_history_archive(
        self,
        year: Any,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get historical bills archive (from 2021)"""
        return self._rest_async("get_bills_history_archive", year, ccy, after, before, extra_data, **kwargs)

    def _set_auto_loan(
        self,
        auto_loan: Any,
        ccy: Any = None,
        iso_mode: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set auto loan status
        :param auto_loan: Auto loan status: `true` for on, `false` for off
        :param ccy: Currency, required for isolated margin
        :param iso_mode: Isolated margin mode: `automatic`, `autonomy`, `manual`
        :param mgn_mode: Margin mode: `cross`, `isolated`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body (params), extra_data
        """
        request_type = "set_auto_loan"
        body = {"autoLoan": str(auto_loan).lower()}
        if ccy:
            body["ccy"] = ccy
        if iso_mode:
            body["isoMode"] = iso_mode
        if mgn_mode:
            body["mgnMode"] = mgn_mode
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_auto_loan_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in body})
        return path, body, extra_data

    @staticmethod
    def _set_auto_loan_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_auto_loan(
        self,
        auto_loan: Any,
        ccy: Any = None,
        iso_mode: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set auto loan status"""
        path, body, extra_data = self._set_auto_loan(
            auto_loan, ccy, iso_mode, mgn_mode, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_auto_loan(
        self,
        auto_loan: Any,
        ccy: Any = None,
        iso_mode: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set auto loan status"""
        path, body, extra_data = self._set_auto_loan(
            auto_loan, ccy, iso_mode, mgn_mode, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_account_level(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set account level
        :param acct_lv: Account level: `1` Simple mode, `2` Single-currency margin, `3` Multi-currency margin, `4` Portfolio margin
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param inst_id: Instrument ID
        :param ccy: Currency
        :param td_mode: Trade mode: `cross`, `isolated`, `cash`
        :param pos_side: Position side: `long`, `short`, `net`
        :param uly: Underlying
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body (params), extra_data
        """
        request_type = "set_account_level"
        body = {"acctLv": str(acct_lv)}
        if inst_type:
            body["instType"] = inst_type
        if inst_id:
            request_inst_id = self._params.get_symbol(inst_id)
            body["instId"] = request_inst_id
        if ccy:
            body["ccy"] = ccy
        if td_mode:
            body["tdMode"] = td_mode
        if pos_side:
            body["posSide"] = pos_side
        if uly:
            body["uly"] = uly
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_account_level_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in body})
        return path, body, extra_data

    @staticmethod
    def _set_account_level_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_account_level(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set account level"""
        path, body, extra_data = self._set_account_level(
            acct_lv,
            inst_type,
            inst_id,
            ccy,
            td_mode,
            pos_side,
            uly,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_account_level(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        td_mode: Any = None,
        pos_side: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set account level"""
        path, body, extra_data = self._set_account_level(
            acct_lv,
            inst_type,
            inst_id,
            ccy,
            td_mode,
            pos_side,
            uly,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _account_level_switch_preset(
        self,
        acct_lv: Any,
        pos_side: Any = None,
        ccy_list: Any = None,
        uly: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Account level switch preset
        :param acct_lv: Target account level: `2` Single-currency margin, `3` Multi-currency margin, `4` Portfolio margin
        :param pos_side: Position side: `long`, `short`, `net`
        :param ccy_list: Currency list, comma-separated, e.g. "BTC,USDT"
        :param uly: Underlying
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body (params), extra_data
        """
        request_type = "account_level_switch_preset"
        body = {"acctLv": str(acct_lv)}
        if pos_side:
            body["posSide"] = pos_side
        if ccy_list:
            body["ccyList"] = ccy_list
        if uly:
            body["uly"] = uly
        if inst_type:
            body["instType"] = inst_type
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._account_level_switch_preset_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in body})
        return path, body, extra_data

    @staticmethod
    def _account_level_switch_preset_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def account_level_switch_preset(
        self,
        acct_lv: Any,
        pos_side: Any = None,
        ccy_list: Any = None,
        uly: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Account level switch preset"""
        path, body, extra_data = self._account_level_switch_preset(
            acct_lv, pos_side, ccy_list, uly, inst_type, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_account_level_switch_preset(
        self,
        acct_lv: Any,
        pos_side: Any = None,
        ccy_list: Any = None,
        uly: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async account level switch preset"""
        path, body, extra_data = self._account_level_switch_preset(
            acct_lv, pos_side, ccy_list, uly, inst_type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _account_level_switch_precheck(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Account level switch precheck
        :param acct_lv: Target account level: `2` Single-currency margin, `3` Multi-currency margin, `4` Portfolio margin
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `SWAP`, `FUTURES`, `OPTION`
        :param uly: Underlying
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "account_level_switch_precheck"
        params = {"acctLv": str(acct_lv)}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._account_level_switch_precheck_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in params})
        return path, params, extra_data

    @staticmethod
    def _account_level_switch_precheck_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def account_level_switch_precheck(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Account level switch precheck"""
        return self._rest("account_level_switch_precheck", acct_lv, inst_type, uly, extra_data, **kwargs)

    def async_account_level_switch_precheck(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async account level switch precheck"""
        return self._rest_async("account_level_switch_precheck", acct_lv, inst_type, uly, extra_data, **kwargs)

    def _set_collateral_assets(
        self,
        ccy_list: Any,
        auto_loan: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set collateral assets
        :param ccy_list: Currency list, comma-separated, e.g. "BTC,USDT,ETH"
        :param auto_loan: Auto loan status: `true` for on, `false` for off
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body (params), extra_data
        """
        request_type = "set_collateral_assets"
        body = {}
        if ccy_list:
            body["ccy"] = ccy_list
        if auto_loan is not None:
            body["autoLoan"] = str(auto_loan).lower()
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy_list or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._set_collateral_assets_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in body})
        return path, body, extra_data

    @staticmethod
    def _set_collateral_assets_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def set_collateral_assets(
        self,
        ccy_list: Any,
        auto_loan: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set collateral assets"""
        path, body, extra_data = self._set_collateral_assets(
            ccy_list, auto_loan, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_collateral_assets(
        self,
        ccy_list: Any,
        auto_loan: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set collateral assets"""
        path, body, extra_data = self._set_collateral_assets(
            ccy_list, auto_loan, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_collateral_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get collateral assets
        :param ccy: Currency, e.g. `BTC`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_collateral_assets"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_collateral_assets_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in params})
        return path, params, extra_data

    @staticmethod
    def _get_collateral_assets_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_collateral_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get collateral assets"""
        return self._rest("get_collateral_assets", ccy, extra_data, **kwargs)

    def async_get_collateral_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get collateral assets"""
        return self._rest_async("get_collateral_assets", ccy, extra_data, **kwargs)

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
        params = {
            "uly": uly,
        }
        if inst_id:
            params["instId"] = inst_id
        if cnt:
            params["cnt"] = cnt
        if amend_px_on:
            params["amendPxOn"] = amend_px_on
        return self._finish(
            "activate_option",
            params,
            extra_data,
            uly,
            TradingAccountMixin._activate_option_normalize_function,
            kwargs,
        )

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
        return self._finish(
            "move_positions",
            params,
            extra_data,
            symbol,
            TradingAccountMixin._move_positions_normalize_function,
            kwargs,
        )

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
        return self._finish(
            "get_move_positions_history",
            params,
            extra_data,
            symbol or "ALL",
            TradingAccountMixin._get_move_positions_history_normalize_function,
            kwargs,
        )

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
        return self._rest("get_move_positions_history", symbol, ccy, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_move_positions_history", symbol, ccy, after, before, limit, extra_data, **kwargs)

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
        params = {
            "ccy": ccy,
            "autoEarn": auto_earn,
        }
        if auto_earn_type:
            params["autoEarnType"] = auto_earn_type
        return self._finish(
            "set_auto_earn",
            params,
            extra_data,
            ccy,
            TradingAccountMixin._set_auto_earn_normalize_function,
            kwargs,
        )

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
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "ccy": ccy,
        }
        return self._finish(
            "set_settle_currency",
            params,
            extra_data,
            symbol,
            TradingAccountMixin._set_settle_currency_normalize_function,
            kwargs,
        )

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
        return self._finish(
            "set_trading_config",
            params,
            extra_data,
            symbol,
            TradingAccountMixin._set_trading_config_normalize_function,
            kwargs,
        )

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
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "deltaNeutralPrecheck": delta_neutral_precheck,
        }
        return self._finish(
            "set_delta_neutral_precheck",
            params,
            extra_data,
            symbol,
            TradingAccountMixin._set_delta_neutral_precheck_normalize_function,
            kwargs,
        )

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

    def _get_account_position_risk(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get account position risk"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_account_position_risk",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_account_position_risk(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get account position risk"""
        return self._rest("get_account_position_risk", extra_data, **kwargs)

    def async_get_account_position_risk(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get account position risk"""
        return self._rest_async("get_account_position_risk", extra_data, **kwargs)

    def _get_bills_archive(
        self,
        year: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get bills archive"""
        params: dict[str, Any] = {}
        if year:
            params["year"] = str(year)
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_bills_archive",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_bills_archive(
        self,
        year: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get bills archive"""
        return self._rest("get_bills_archive", year, ccy, after, before, limit, extra_data, **kwargs)

    def async_get_bills_archive(
        self,
        year: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get bills archive"""
        return self._rest_async("get_bills_archive", year, ccy, after, before, limit, extra_data, **kwargs)

    def _get_adjust_leverage_info(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get adjust leverage info"""
        request_type = "get_adjust_leverage_info"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_adjust_leverage_info(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get adjust leverage info"""
        return self._rest("get_adjust_leverage_info", inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs)

    def async_get_adjust_leverage_info(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get adjust leverage info"""
        return self._rest_async("get_adjust_leverage_info", inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs)

    def _get_max_loan(
        self,
        inst_type: Any = None,
        symbol: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get max loan"""
        request_type = "get_max_loan"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if symbol:
            request_symbol = self._params.get_symbol(symbol)
            params["instId"] = request_symbol
        elif inst_id:
            params["instId"] = inst_id
        if uly:
            params["uly"] = uly
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        if ccy:
            params["ccy"] = ccy
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol or inst_id or uly or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_max_loan(
        self,
        inst_type: Any = None,
        symbol: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get max loan"""
        return self._rest("get_max_loan", inst_type, symbol, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs)

    def async_get_max_loan(
        self,
        inst_type: Any = None,
        symbol: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get max loan"""
        return self._rest_async("get_max_loan", inst_type, symbol, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs)

    def _get_interest_accrued(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get interest accrued"""
        request_type = "get_interest_accrued"
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
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_interest_accrued(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get interest accrued"""
        return self._rest("get_interest_accrued", inst_type, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs)

    def async_get_interest_accrued(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get interest accrued"""
        return self._rest_async("get_interest_accrued", inst_type, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs)

    def _get_greeks(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get greeks"""
        request_type = "get_greeks"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_greeks(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get greeks"""
        return self._rest("get_greeks", inst_type, uly, inst_id, extra_data, **kwargs)

    def async_get_greeks(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get greeks"""
        return self._rest_async("get_greeks", inst_type, uly, inst_id, extra_data, **kwargs)

    def _get_position_tiers(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get position tiers"""
        request_type = "get_position_tiers"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if tier:
            params["tier"] = tier
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_position_tiers(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get position tiers"""
        return self._rest("get_position_tiers", inst_type, uly, inst_id, tier, extra_data, **kwargs)

    def async_get_position_tiers(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get position tiers"""
        return self._rest_async("get_position_tiers", inst_type, uly, inst_id, tier, extra_data, **kwargs)

    def _get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get max withdrawal"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_max_withdrawal",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get max withdrawal"""
        return self._rest("get_max_withdrawal", ccy, extra_data, **kwargs)

    def async_get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get max withdrawal"""
        return self._rest_async("get_max_withdrawal", ccy, extra_data, **kwargs)

    def _get_risk_state(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get risk state"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_risk_state",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_risk_state(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get risk state"""
        return self._rest("get_risk_state", extra_data, **kwargs)

    def async_get_risk_state(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get risk state"""
        return self._rest_async("get_risk_state", extra_data, **kwargs)

    def _get_bills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get bills"""
        request_type = "get_bills"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
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
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_bills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get bills"""
        return self._rest("get_bills", inst_type, uly, inst_id, ccy, mgn_mode, after, before, limit, extra_data, **kwargs,)

    def async_get_bills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        mgn_mode: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get bills"""
        return self._rest_async("get_bills", inst_type, uly, inst_id, ccy, mgn_mode, after, before, limit, extra_data, **kwargs,)

    def _get_lever(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get leverage info"""
        request_type = "get_lever"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_lever(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get leverage info"""
        return self._rest("get_lever", inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs)

    def async_get_lever(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        mgn_mode: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get leverage info"""
        return self._rest_async("get_lever", inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs)

