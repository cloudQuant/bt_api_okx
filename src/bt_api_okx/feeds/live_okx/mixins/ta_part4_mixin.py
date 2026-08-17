"""
OKX API - TradingAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class TradingAccountPart4Mixin:
    """TradingAccountPart4Mixin 方法集合。"""

    def get_account_position_risk(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get account position risk"""
        path, params, extra_data = self._get_account_position_risk(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_account_position_risk(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get account position risk"""
        path, params, extra_data = self._get_account_position_risk(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        request_type = "get_bills_archive"
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
        path, params, extra_data = self._get_bills_archive(
            year, ccy, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_bills_archive(
            year, ccy, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_adjust_leverage_info(
            inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_adjust_leverage_info(
            inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_max_loan(
            inst_type, symbol, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_max_loan(
            inst_type, symbol, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_interest_accrued(
            inst_type, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_interest_accrued(
            inst_type, uly, inst_id, mgn_mode, ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_greeks(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_greeks(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get greeks"""
        path, params, extra_data = self._get_greeks(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_position_tiers(
            inst_type, uly, inst_id, tier, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_position_tiers(
            inst_type, uly, inst_id, tier, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get max withdrawal"""
        request_type = "get_max_withdrawal"
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get max withdrawal"""
        path, params, extra_data = self._get_max_withdrawal(ccy, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_max_withdrawal(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get max withdrawal"""
        path, params, extra_data = self._get_max_withdrawal(ccy, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_risk_state(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get risk state"""
        request_type = "get_risk_state"
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

    def get_risk_state(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get risk state"""
        path, params, extra_data = self._get_risk_state(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_risk_state(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get risk state"""
        path, params, extra_data = self._get_risk_state(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

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
        path, params, extra_data = self._get_bills(
            inst_type,
            uly,
            inst_id,
            ccy,
            mgn_mode,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_bills(
            inst_type,
            uly,
            inst_id,
            ccy,
            mgn_mode,
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
        path, params, extra_data = self._get_lever(
            inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

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
        path, params, extra_data = self._get_lever(
            inst_type, uly, inst_id, mgn_mode, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

