"""
OKX API - TradeMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.orders.okx_order import OkxOrderData
from bt_api_okx.containers.trades.okx_trade import OkxRequestTradeData
from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.index_candles_mixin import IndexCandlesMixin


class ConvertMixin:
    """ConvertMixin 方法集合。"""

    def _get_account_rate_limit(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get account rate limit"""
        request_type = "get_account_rate_limit"
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

    def get_account_rate_limit(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get account rate limit"""
        path, params, extra_data = self._get_account_rate_limit(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_account_rate_limit(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get account rate limit"""
        path, params, extra_data = self._get_account_rate_limit(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_easy_convert_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get easy convert currency list"""
        request_type = "get_easy_convert_currency_list"
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

    def get_easy_convert_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get easy convert currency list"""
        path, params, extra_data = self._get_easy_convert_currency_list(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_easy_convert_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get easy convert currency list"""
        path, params, extra_data = self._get_easy_convert_currency_list(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _easy_convert(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Easy convert"""
        request_type = "easy_convert"
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
            "amt": str(amt),
        }
        if client_order_id:
            params["clientOrderId"] = client_order_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": from_ccy,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def easy_convert(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Easy convert"""
        path, params, extra_data = self._easy_convert(
            from_ccy, to_ccy, amt, client_order_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_easy_convert(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async easy convert"""
        path, params, extra_data = self._easy_convert(
            from_ccy, to_ccy, amt, client_order_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_easy_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get easy convert history"""
        request_type = "get_easy_convert_history"
        params: dict[str, Any] = {}
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

    def get_easy_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get easy convert history"""
        path, params, extra_data = self._get_easy_convert_history(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_easy_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get easy convert history"""
        path, params, extra_data = self._get_easy_convert_history(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_one_click_repay_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get one click repay currency list"""
        request_type = "get_one_click_repay_currency_list"
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

    def get_one_click_repay_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get one click repay currency list"""
        path, params, extra_data = self._get_one_click_repay_currency_list(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_one_click_repay_currency_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get one click repay currency list"""
        path, params, extra_data = self._get_one_click_repay_currency_list(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _one_click_repay(
        self,
        ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """One click repay"""
        request_type = "one_click_repay"
        params = {
            "ccy": ccy,
            "amt": str(amt),
        }
        if client_order_id:
            params["clientOrderId"] = client_order_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def one_click_repay(
        self,
        ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """One click repay"""
        path, params, extra_data = self._one_click_repay(
            ccy, amt, client_order_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_one_click_repay(
        self,
        ccy: Any,
        amt: Any,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async one click repay"""
        path, params, extra_data = self._one_click_repay(
            ccy, amt, client_order_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_one_click_repay_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get one click repay history"""
        request_type = "get_one_click_repay_history"
        params: dict[str, Any] = {}
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

    def get_one_click_repay_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get one click repay history"""
        path, params, extra_data = self._get_one_click_repay_history(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_one_click_repay_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get one click repay history"""
        path, params, extra_data = self._get_one_click_repay_history(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _mass_cancel(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Mass cancel orders"""
        request_type = "mass_cancel"
        params: dict[str, Any] = {}
        if inst_id:
            request_symbol = self._params.get_symbol(inst_id)
            params["instId"] = request_symbol
        if uly:
            params["instFamily"] = uly
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def mass_cancel(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Mass cancel orders"""
        path, params, extra_data = self._mass_cancel(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_mass_cancel(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async mass cancel orders"""
        path, params, extra_data = self._mass_cancel(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _order_precheck(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any,
        side: Any,
        order_type: Any = None,
        sz: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Order precheck"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "order_precheck"
        params = {
            "instId": request_symbol,
            "tdMode": td_mode,
            "ccy": ccy,
            "side": side,
        }
        if order_type:
            params["ordType"] = order_type
        if sz is not None:
            params["sz"] = str(sz)
        if px is not None:
            params["px"] = str(px)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def order_precheck(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any,
        side: Any,
        order_type: Any = None,
        sz: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Order precheck"""
        path, params, extra_data = self._order_precheck(
            symbol, td_mode, ccy, side, order_type, sz, px, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_order_precheck(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any,
        side: Any,
        order_type: Any = None,
        sz: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async order precheck"""
        path, params, extra_data = self._order_precheck(
            symbol, td_mode, ccy, side, order_type, sz, px, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

