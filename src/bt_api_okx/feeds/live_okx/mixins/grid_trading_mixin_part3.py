"""
OKX API - GridTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class GridTradingMixinPart3:
    """GridTradingMixinPart3 方法集合。"""

    def grid_compute_margin_balance(
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
    ) -> Any:
        """Compute margin balance - """
        path, params, extra_data = self._grid_compute_margin_balance(
            inst_id,
            td_mode,
            ccy,
            algo_ords_type,
            sz,
            max_px,
            min_px,
            grid_num,
            trigger_px,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_compute_margin_balance(
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
    ) -> None:
        """Async compute margin balance"""
        path, params, extra_data = self._grid_compute_margin_balance(
            inst_id,
            td_mode,
            ccy,
            algo_ords_type,
            sz,
            max_px,
            min_px,
            grid_num,
            trigger_px,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_margin_balance(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Adjust margin - """
        request_type = "grid_margin_balance"
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

    def grid_margin_balance(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Adjust margin - """
        path, params, extra_data = self._grid_margin_balance(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_margin_balance(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async adjust margin"""
        path, params, extra_data = self._grid_margin_balance(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_add_investment(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Add investment - """
        request_type = "grid_add_investment"
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

    def grid_add_investment(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Add investment - """
        path, params, extra_data = self._grid_add_investment(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_add_investment(
        self,
        algo_id: Any,
        inst_id: Any,
        amt: Any,
        ccy: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async add investment"""
        path, params, extra_data = self._grid_add_investment(
            algo_id, inst_id, amt, ccy, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_get_ai_param(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any = None,
        min_px: Any = None,
        grid_num: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get grid AI parameters - AI"""
        request_type = "grid_get_ai_param"
        params = {
            "instId": inst_id,
            "algoAlgoType": algo_algo_type,
        }
        if max_px is not None:
            params["maxPx"] = max_px
        if min_px is not None:
            params["minPx"] = min_px
        if grid_num is not None:
            params["gridNum"] = grid_num
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

    def grid_get_ai_param(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any = None,
        min_px: Any = None,
        grid_num: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get grid AI parameters - AI"""
        path, params, extra_data = self._grid_get_ai_param(
            inst_id, algo_algo_type, max_px, min_px, grid_num, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_get_ai_param(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any = None,
        min_px: Any = None,
        grid_num: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get grid AI parameters"""
        path, params, extra_data = self._grid_get_ai_param(
            inst_id, algo_algo_type, max_px, min_px, grid_num, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_compute_min_investment(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Compute minimum investment - """
        request_type = "grid_compute_min_investment"
        params = {
            "instId": inst_id,
            "algoAlgoType": algo_algo_type,
            "maxPx": max_px,
            "minPx": min_px,
            "gridNum": grid_num,
        }
        if run_type is not None:
            params["runType"] = run_type
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

    def grid_compute_min_investment(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Compute minimum investment - """
        path, params, extra_data = self._grid_compute_min_investment(
            inst_id,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            run_type,
            trigger_px,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_grid_compute_min_investment(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        run_type: Any = None,
        trigger_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async compute minimum investment"""
        path, params, extra_data = self._grid_compute_min_investment(
            inst_id,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            run_type,
            trigger_px,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_rsi_back_testing(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        time_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """RSI back testing - RSI"""
        request_type = "grid_rsi_back_testing"
        params = {
            "instId": inst_id,
            "algoAlgoType": algo_algo_type,
            "maxPx": max_px,
            "minPx": min_px,
            "gridNum": grid_num,
        }
        if time_type is not None:
            params["timeType"] = time_type
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

    def grid_rsi_back_testing(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        time_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """RSI back testing - RSI"""
        path, params, extra_data = self._grid_rsi_back_testing(
            inst_id,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            time_type,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_rsi_back_testing(
        self,
        inst_id: Any,
        algo_algo_type: Any,
        max_px: Any,
        min_px: Any,
        grid_num: Any,
        time_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async RSI back testing"""
        path, params, extra_data = self._grid_rsi_back_testing(
            inst_id,
            algo_algo_type,
            max_px,
            min_px,
            grid_num,
            time_type,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _grid_max_grid_quantity(
        self, inst_id: Any, algo_algo_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get max grid quantity - """
        request_type = "grid_max_grid_quantity"
        params = {
            "instId": inst_id,
            "algoAlgoType": algo_algo_type,
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

    def grid_max_grid_quantity(
        self, inst_id: Any, algo_algo_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get max grid quantity - """
        path, params, extra_data = self._grid_max_grid_quantity(
            inst_id, algo_algo_type, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_grid_max_grid_quantity(
        self, inst_id: Any, algo_algo_type: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get max grid quantity"""
        path, params, extra_data = self._grid_max_grid_quantity(
            inst_id, algo_algo_type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

