"""
OKX API - TradingAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class TradingAccountPart2Mixin:
    """TradingAccountPart2Mixin 方法集合。"""

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
        request_type = "get_mmp_config"
        params = {
            "instType": inst_type,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_mmp_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

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
        path, params, extra_data = self._get_mmp_config(inst_type, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_mmp_config(
        self, inst_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get MMP (Market Maker Protection) configuration"""
        path, params, extra_data = self._get_mmp_config(inst_type, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Bills History Archive APIs ====================

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
        request_type = "apply_bills_history_archive"
        params = {
            "year": str(year),
        }
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._apply_bills_history_archive_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

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
        request_type = "get_bills_history_archive"
        params = {
            "year": str(year),
        }
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradingAccountMixin._get_bills_history_archive_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

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
        path, params, extra_data = self._get_bills_history_archive(
            year, ccy, after, before, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_bills_history_archive(
            year, ccy, after, before, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Trading Account Configuration APIs ====================

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
        path, params, extra_data = self._account_level_switch_precheck(
            acct_lv, inst_type, uly, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_account_level_switch_precheck(
        self,
        acct_lv: Any,
        inst_type: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async account level switch precheck"""
        path, params, extra_data = self._account_level_switch_precheck(
            acct_lv, inst_type, uly, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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

