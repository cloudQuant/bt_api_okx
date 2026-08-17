"""
OKX API - StatisticsMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class StatisticsMixinPart3:
    """StatisticsMixinPart3 方法集合。"""

    def get_support_coin(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get support coin"""
        path, params, extra_data = self._get_support_coin(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_support_coin(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get support coin"""
        path, params, extra_data = self._get_support_coin(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_contract_oi_history(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get contract open interest history"""
        request_type = "get_contract_oi_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        if period:
            params["period"] = period
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_contract_oi_history(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get contract open interest history"""
        path, params, extra_data = self._get_contract_oi_history(
            ccy, uly, inst_id, after, before, limit, period, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_contract_oi_history(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get contract open interest history"""
        path, params, extra_data = self._get_contract_oi_history(
            ccy, uly, inst_id, after, before, limit, period, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_taker_volume(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get taker volume"""
        request_type = "get_taker_volume"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        if period:
            params["period"] = period
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_taker_volume(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get taker volume"""
        path, params, extra_data = self._get_taker_volume(
            ccy, uly, inst_id, begin, end, period, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_taker_volume(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get taker volume"""
        path, params, extra_data = self._get_taker_volume(
            ccy, uly, inst_id, begin, end, period, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_long_short_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get long short ratio"""
        request_type = "get_long_short_ratio"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        if period:
            params["period"] = period
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

    def get_long_short_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get long short ratio"""
        path, params, extra_data = self._get_long_short_ratio(
            ccy, begin, end, period, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_long_short_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get long short ratio"""
        path, params, extra_data = self._get_long_short_ratio(
            ccy, begin, end, period, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_long_short_ratio_top_trader(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get long short ratio (top trader)"""
        request_type = "get_long_short_ratio_top_trader"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        if period:
            params["period"] = period
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

    def get_long_short_ratio_top_trader(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get long short ratio (top trader)"""
        path, params, extra_data = self._get_long_short_ratio_top_trader(
            ccy, begin, end, period, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_long_short_ratio_top_trader(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get long short ratio (top trader)"""
        path, params, extra_data = self._get_long_short_ratio_top_trader(
            ccy, begin, end, period, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_contract_long_short_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get contract long short ratio"""
        request_type = "get_contract_long_short_ratio"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        if period:
            params["period"] = period
        if limit:
            params["limit"] = limit
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or uly or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_contract_long_short_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get contract long short ratio"""
        path, params, extra_data = self._get_contract_long_short_ratio(
            ccy, uly, inst_id, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_contract_long_short_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get contract long short ratio"""
        path, params, extra_data = self._get_contract_long_short_ratio(
            ccy, uly, inst_id, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_put_call_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get put call ratio"""
        request_type = "get_put_call_ratio"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if uly:
            params["uly"] = uly
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        if period:
            params["period"] = period
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": uly or ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_put_call_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get put call ratio"""
        path, params, extra_data = self._get_put_call_ratio(
            ccy, uly, begin, end, period, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_put_call_ratio(
        self,
        ccy: Any = None,
        uly: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get put call ratio"""
        path, params, extra_data = self._get_put_call_ratio(
            ccy, uly, begin, end, period, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

