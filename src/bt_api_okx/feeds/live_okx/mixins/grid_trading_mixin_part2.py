"""
OKX API - GridTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class GridTradingMixinPart2:
    """GridTradingMixinPart2 方法集合。"""

    def async_grid_close_position(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        margin: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async close futures grid position"""
        path, params, extra_data = self._grid_close_position(
            algo_id, inst_id, ccy, margin, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_cancel_close_order(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel futures grid close order - """
        request_type = "grid_cancel_close_order"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_cancel_close_order(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel futures grid close order - """
        path, params, extra_data = self._grid_cancel_close_order(
            algo_id, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_cancel_close_order(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel futures grid close order"""
        path, params, extra_data = self._grid_cancel_close_order(
            algo_id, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_order_instant_trigger(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Grid order instant trigger - """
        request_type = "grid_order_instant_trigger"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        if trigger_px is not None:
            params["triggerPx"] = trigger_px
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_order_instant_trigger(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Grid order instant trigger - """
        path, params, extra_data = self._grid_order_instant_trigger(
            algo_id, inst_id, trigger_px, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_order_instant_trigger(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async grid order instant trigger"""
        path, params, extra_data = self._grid_order_instant_trigger(
            algo_id, inst_id, trigger_px, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_orders_algo_details(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid order details - """
        request_type = "grid_orders_algo_details"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_orders_algo_details(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get grid order details - """
        path, params, extra_data = self._grid_orders_algo_details(
            algo_id, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_orders_algo_details(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get grid order details"""
        path, params, extra_data = self._grid_orders_algo_details(
            algo_id, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_sub_orders(
        self,
        algo_id: Any,
        inst_id: Any,
        type: Any = None,
        ord_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid sub orders - """
        request_type = "grid_sub_orders"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        if type is not None:
            params["type"] = type
        if ord_id:
            params["ordId"] = ord_id
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
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_sub_orders(
        self,
        algo_id: Any,
        inst_id: Any,
        type: Any = None,
        ord_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get grid sub orders - """
        path, params, extra_data = self._grid_sub_orders(
            algo_id, inst_id, type, ord_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_sub_orders(
        self,
        algo_id: Any,
        inst_id: Any,
        type: Any = None,
        ord_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get grid sub orders"""
        path, params, extra_data = self._grid_sub_orders(
            algo_id, inst_id, type, ord_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_positions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid positions - """
        request_type = "grid_positions"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        if algo_id:
            params["algoId"] = algo_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_positions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get grid positions - """
        path, params, extra_data = self._grid_positions(
            inst_type, inst_id, algo_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_positions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get grid positions"""
        path, params, extra_data = self._grid_positions(
            inst_type, inst_id, algo_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_withdraw_income(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Spot grid withdraw income - """
        request_type = "grid_withdraw_income"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
            "amt": amt,
        }
        if ccy:
            params["ccy"] = ccy
        if type is not None:
            params["type"] = type
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_withdraw_income(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Spot grid withdraw income - """
        path, params, extra_data = self._grid_withdraw_income(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_withdraw_income(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async spot grid withdraw income"""
        path, params, extra_data = self._grid_withdraw_income(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_compute_margin_balance(
        self,
        inst_id: Any,
        td_mode: Any,
        ccy: Any,
        algo_ords_type: Any,
        sz: Any,
        max_px: Any = None,
        min_px: Any = None,
        grid_num: Any = None,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Compute margin balance - """
        request_type = "grid_compute_margin_balance"
        params = {
            "instId": inst_id,
            "tdMode": td_mode,
            "ccy": ccy,
            "algoOrdsType": algo_ords_type,
            "sz": sz,
        }
        if max_px is not None:
            params["maxPx"] = max_px
        if min_px is not None:
            params["minPx"] = min_px
        if grid_num is not None:
            params["gridNum"] = grid_num
        if trigger_px is not None:
            params["triggerPx"] = trigger_px
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

