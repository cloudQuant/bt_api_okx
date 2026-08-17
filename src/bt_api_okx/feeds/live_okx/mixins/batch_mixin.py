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


class BatchMixin:
    """BatchMixin 方法集合。"""

    def _make_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Make multiple orders (batch)"""
        request_type = "make_orders"
        params = orders_data
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "BATCH",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def make_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Make multiple orders (batch)"""
        path, params, extra_data = self._make_orders(orders_data, extra_data, **kwargs)
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_make_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async make multiple orders (batch)"""
        path, params, extra_data = self._make_orders(orders_data, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel multiple orders (batch)"""
        request_type = "cancel_orders"
        params = orders_data
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "BATCH",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def cancel_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel multiple orders (batch)"""
        path, params, extra_data = self._cancel_orders(
            orders_data, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel multiple orders (batch)"""
        path, params, extra_data = self._cancel_orders(
            orders_data, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _amend_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Amend multiple orders (batch)"""
        request_type = "amend_orders"
        params = orders_data
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "BATCH",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def amend_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Amend multiple orders (batch)"""
        path, params, extra_data = self._amend_orders(orders_data, extra_data, **kwargs)
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_amend_orders(
        self, orders_data: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async amend multiple orders (batch)"""
        path, params, extra_data = self._amend_orders(orders_data, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_fills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get fills"""
        request_type = "get_fills"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if order_id:
            params["ordId"] = order_id
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

    def get_fills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get fills"""
        path, params, extra_data = self._get_fills(
            inst_type,
            uly,
            inst_id,
            order_id,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_fills(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get fills"""
        path, params, extra_data = self._get_fills(
            inst_type,
            uly,
            inst_id,
            order_id,
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

    def _close_position(
        self,
        symbol: Any,
        pos_side: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        auto_cxl: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Close position"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "close_position"
        params = {
            "instId": request_symbol,
        }
        if pos_side:
            params["posSide"] = pos_side
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        if ccy:
            params["ccy"] = ccy
        if auto_cxl:
            params["autoCxl"] = True
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

    def close_position(
        self,
        symbol: Any,
        pos_side: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        auto_cxl: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Close position"""
        path, params, extra_data = self._close_position(
            symbol, pos_side, mgn_mode, ccy, auto_cxl, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_close_position(
        self,
        symbol: Any,
        pos_side: Any = None,
        mgn_mode: Any = None,
        ccy: Any = None,
        auto_cxl: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async close position"""
        path, params, extra_data = self._close_position(
            symbol, pos_side, mgn_mode, ccy, auto_cxl, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_fills_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get fills history"""
        request_type = "get_fills_history"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if order_id:
            params["ordId"] = order_id
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

    def get_fills_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get fills history"""
        path, params, extra_data = self._get_fills_history(
            inst_type,
            uly,
            inst_id,
            order_id,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_fills_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        order_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get fills history"""
        path, params, extra_data = self._get_fills_history(
            inst_type,
            uly,
            inst_id,
            order_id,
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

    def _get_order_history_archive(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get order history archive"""
        request_type = "get_order_history_archive"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
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

    def get_order_history_archive(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get order history archive"""
        path, params, extra_data = self._get_order_history_archive(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_order_history_archive(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get order history archive"""
        path, params, extra_data = self._get_order_history_archive(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_all_after(
        self, time_slug: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel all orders after time"""
        request_type = "cancel_all_after"
        params = {"timeOut": str(time_slug)}
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

    def cancel_all_after(
        self, time_slug: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel all orders after time"""
        path, params, extra_data = self._cancel_all_after(
            time_slug, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_all_after(
        self, time_slug: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel all orders after time"""
        path, params, extra_data = self._cancel_all_after(
            time_slug, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )













