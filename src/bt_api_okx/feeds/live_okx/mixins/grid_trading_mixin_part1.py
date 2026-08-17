"""
OKX API - GridTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class GridTradingMixinPart1:
    """GridTradingMixinPart1 方法集合。"""

    def _grid_order_algo(
        self,
        inst_id: Any,
        td_mode: Any,
        ccy: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        sz: Any = None,
        base_sz: Any = None,
        trigger_px: Any = None,
        trigger_time: Any = None,
        attach_algo_cl_or: Any = None,
        attach_algo_om_trigger_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        fast_callback_speed: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create grid strategy order"""
        request_type = "grid_order_algo"
        params = {
            "instId": inst_id,
            "tdMode": td_mode,
            "algoAlgoType": algo_algo_type,  # "grid_regular" or "grid_contract"
            "maxPx": max_px,
            "minPx": min_px,
            "gridNum": grid_num,
            "runType": run_type or "1",  # 1: single, 2: neutral
        }
        if ccy:
            params["ccy"] = ccy
        if sz is not None:
            params["sz"] = sz
        if base_sz is not None:
            params["baseSz"] = base_sz
        if trigger_px is not None:
            params["triggerPx"] = trigger_px
        if trigger_time is not None:
            params["triggerTime"] = trigger_time
        if attach_algo_cl_or is not None:
            params["attachAlgoClOrd"] = attach_algo_cl_or
        if attach_algo_om_trigger_px is not None:
            params["attachAlgoOmTriggerPx"] = attach_algo_om_trigger_px
        if tp_px is not None:
            params["tpPx"] = tp_px
        if tp_trigger_px is not None:
            params["tpTriggerPx"] = tp_trigger_px
        if sl_px is not None:
            params["slPx"] = sl_px
        if sl_trigger_px is not None:
            params["slTriggerPx"] = sl_trigger_px
        if fast_callback_speed is not None:
            params["fastCallbackSpeed"] = fast_callback_speed
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

    def grid_order_algo(
        self,
        inst_id: Any,
        td_mode: Any,
        ccy: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        sz: Any = None,
        base_sz: Any = None,
        trigger_px: Any = None,
        trigger_time: Any = None,
        attach_algo_cl_or: Any = None,
        attach_algo_om_trigger_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        fast_callback_speed: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Create grid strategy order"""
        path, params, extra_data = self._grid_order_algo(
            inst_id,
            td_mode,
            ccy,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            run_type,
            sz,
            base_sz,
            trigger_px,
            trigger_time,
            attach_algo_cl_or,
            attach_algo_om_trigger_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            fast_callback_speed,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_order_algo(
        self,
        inst_id: Any,
        td_mode: Any,
        ccy: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        sz: Any = None,
        base_sz: Any = None,
        trigger_px: Any = None,
        trigger_time: Any = None,
        attach_algo_cl_or: Any = None,
        attach_algo_om_trigger_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        fast_callback_speed: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async create grid strategy order"""
        path, params, extra_data = self._grid_order_algo(
            inst_id,
            td_mode,
            ccy,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            run_type,
            sz,
            base_sz,
            trigger_px,
            trigger_time,
            attach_algo_cl_or,
            attach_algo_om_trigger_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            fast_callback_speed,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_amend_order_algo(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Amend grid strategy order"""
        request_type = "grid_amend_order_algo"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        if trigger_px is not None:
            params["triggerPx"] = trigger_px
        if max_px is not None:
            params["maxPx"] = max_px
        if min_px is not None:
            params["minPx"] = min_px
        if tp_px is not None:
            params["tpPx"] = tp_px
        if tp_trigger_px is not None:
            params["tpTriggerPx"] = tp_trigger_px
        if sl_px is not None:
            params["slPx"] = sl_px
        if sl_trigger_px is not None:
            params["slTriggerPx"] = sl_trigger_px
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

    def grid_amend_order_algo(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Amend grid strategy order"""
        path, params, extra_data = self._grid_amend_order_algo(
            algo_id,
            inst_id,
            trigger_px,
            max_px,
            min_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_amend_order_algo(
        self,
        algo_id: Any,
        inst_id: Any,
        trigger_px: Any = None,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async amend grid strategy order"""
        path, params, extra_data = self._grid_amend_order_algo(
            algo_id,
            inst_id,
            trigger_px,
            max_px,
            min_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_stop_order_algo(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Stop grid strategy order"""
        request_type = "grid_stop_order_algo"
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

    def grid_stop_order_algo(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Stop grid strategy order"""
        path, params, extra_data = self._grid_stop_order_algo(
            algo_id, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_stop_order_algo(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async stop grid strategy order"""
        path, params, extra_data = self._grid_stop_order_algo(
            algo_id, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_orders_algo_pending(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid strategy pending orders"""
        request_type = "grid_orders_algo_pending"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        if algo_id:
            params["algoId"] = algo_id
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_orders_algo_pending(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get grid strategy pending orders"""
        path, params, extra_data = self._grid_orders_algo_pending(
            inst_type, inst_id, algo_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_orders_algo_pending(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get grid strategy pending orders"""
        path, params, extra_data = self._grid_orders_algo_pending(
            inst_type, inst_id, algo_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_orders_algo_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid strategy order history"""
        request_type = "grid_orders_algo_history"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        if algo_id:
            params["algoId"] = algo_id
        if state:
            params["state"] = state
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def grid_orders_algo_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get grid strategy order history"""
        path, params, extra_data = self._grid_orders_algo_history(
            inst_type,
            inst_id,
            algo_id,
            state,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_orders_algo_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get grid strategy order history"""
        path, params, extra_data = self._grid_orders_algo_history(
            inst_type,
            inst_id,
            algo_id,
            state,
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

    def _grid_amend_order_algo_basic(
        self,
        algo_id: Any,
        inst_id: Any,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Amend grid order (basic parameters) - ()"""
        request_type = "grid_amend_order_algo_basic"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        if max_px is not None:
            params["maxPx"] = max_px
        if min_px is not None:
            params["minPx"] = min_px
        if tp_px is not None:
            params["tpPx"] = tp_px
        if tp_trigger_px is not None:
            params["tpTriggerPx"] = tp_trigger_px
        if sl_px is not None:
            params["slPx"] = sl_px
        if sl_trigger_px is not None:
            params["slTriggerPx"] = sl_trigger_px
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

    def grid_amend_order_algo_basic(
        self,
        algo_id: Any,
        inst_id: Any,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Amend grid order (basic parameters) - ()"""
        path, params, extra_data = self._grid_amend_order_algo_basic(
            algo_id,
            inst_id,
            max_px,
            min_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_amend_order_algo_basic(
        self,
        algo_id: Any,
        inst_id: Any,
        max_px: Any = None,
        min_px: Any = None,
        tp_px: Any = None,
        tp_trigger_px: Any = None,
        sl_px: Any = None,
        sl_trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async amend grid order (basic parameters)"""
        path, params, extra_data = self._grid_amend_order_algo_basic(
            algo_id,
            inst_id,
            max_px,
            min_px,
            tp_px,
            tp_trigger_px,
            sl_px,
            sl_trigger_px,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_close_position(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        margin: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Close futures grid position - """
        request_type = "grid_close_position"
        params = {
            "algoId": algo_id,
            "instId": inst_id,
        }
        if ccy:
            params["ccy"] = ccy
        if margin is not None:
            params["margin"] = margin
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

    def grid_close_position(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        margin: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Close futures grid position - """
        path, params, extra_data = self._grid_close_position(
            algo_id, inst_id, ccy, margin, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

