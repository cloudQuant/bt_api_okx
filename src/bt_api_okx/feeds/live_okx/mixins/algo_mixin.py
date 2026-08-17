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


class AlgoMixin:
    """AlgoMixin 方法集合。"""

    def _make_algo_order(
        self,
        symbol: Any,
        side: Any,
        ord_type: Any,
        sz: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Place algo order (trigger, conditional, oco, iceberg, twap, trailing)"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "make_algo_order"
        params = {
            "instId": request_symbol,
            "tdMode": kwargs.get("tdMode", "cross"),
            "side": side,
            "ordType": ord_type,
            "sz": str(sz),
        }
        # Add optional algo-specific parameters
        for key in [
            "triggerPx",
            "orderPx",
            "triggerPxType",
            "tpTriggerPx",
            "tpOrdPx",
            "slTriggerPx",
            "slOrdPx",
            "tpTriggerPxType",
            "slTriggerPxType",
            "ccy",
            "posSide",
            "clOrdId",
            "reduceOnly",
            "tgtCcy",
        ]:
            if key in kwargs:
                params[key] = str(kwargs[key])
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._make_order_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update({k: v for k, v in kwargs.items() if k not in params})
        return path, params, extra_data

    def make_algo_order(
        self,
        symbol: Any,
        side: Any,
        ord_type: Any,
        sz: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """make_algo_order method"""
        path, params, extra_data = self._make_algo_order(
            symbol, side, ord_type, sz, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def cancel_algo_order(
        self, algo_id: Any, inst_id: Any, extra_data: Any = None
    ) -> Any:
        """Cancel algo order"""
        path = self._params.get_rest_path("cancel_algo_order")
        params = [{"algoId": algo_id, "instId": inst_id}]
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": "cancel_algo_order",
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def _amend_algo_order(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        amend_px_on_trigger_type: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        new_tp_trigger_px: Any = None,
        new_tp_ord_px: Any = None,
        new_sl_trigger_px: Any = None,
        new_sl_ord_px: Any = None,
        trigger_px: Any = None,
        order_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Amend algo order"""
        request_symbol = self._params.get_symbol(inst_id)
        request_type = "amend_algo_order"
        params = {
            "algoId": algo_id,
            "instId": request_symbol,
        }
        if ccy:
            params["ccy"] = ccy
        if amend_px_on_trigger_type:
            params["amendPxOnTriggerType"] = amend_px_on_trigger_type
        if new_sz is not None:
            params["newSz"] = str(new_sz)
        if new_px is not None:
            params["newPx"] = str(new_px)
        if new_tp_trigger_px is not None:
            params["newTpTriggerPx"] = str(new_tp_trigger_px)
        if new_tp_ord_px is not None:
            params["newTpOrdPx"] = str(new_tp_ord_px)
        if new_sl_trigger_px is not None:
            params["newSlTriggerPx"] = str(new_sl_trigger_px)
        if new_sl_ord_px is not None:
            params["newSlOrdPx"] = str(new_sl_ord_px)
        if trigger_px is not None:
            params["triggerPx"] = str(trigger_px)
        if order_type:
            params["algoOrdType"] = order_type
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

    def amend_algo_order(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        amend_px_on_trigger_type: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        new_tp_trigger_px: Any = None,
        new_tp_ord_px: Any = None,
        new_sl_trigger_px: Any = None,
        new_sl_ord_px: Any = None,
        trigger_px: Any = None,
        order_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Amend algo order"""
        path, params, extra_data = self._amend_algo_order(
            algo_id,
            inst_id,
            ccy,
            amend_px_on_trigger_type,
            new_sz,
            new_px,
            new_tp_trigger_px,
            new_tp_ord_px,
            new_sl_trigger_px,
            new_sl_ord_px,
            trigger_px,
            order_type,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_amend_algo_order(
        self,
        algo_id: Any,
        inst_id: Any,
        ccy: Any = None,
        amend_px_on_trigger_type: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        new_tp_trigger_px: Any = None,
        new_tp_ord_px: Any = None,
        new_sl_trigger_px: Any = None,
        new_sl_ord_px: Any = None,
        trigger_px: Any = None,
        order_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async amend algo order"""
        path, params, extra_data = self._amend_algo_order(
            algo_id,
            inst_id,
            ccy,
            amend_px_on_trigger_type,
            new_sz,
            new_px,
            new_tp_trigger_px,
            new_tp_ord_px,
            new_sl_trigger_px,
            new_sl_ord_px,
            trigger_px,
            order_type,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_algo_orders_pending(
        self,
        inst_type: Any = None,
        ord_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get pending algo orders"""
        request_type = "get_algo_orders_pending"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if ord_type:
            params["ordType"] = ord_type
        if uly:
            params["uly"] = uly
        if inst_id:
            request_symbol = self._params.get_symbol(inst_id)
            params["instId"] = request_symbol
        if algo_id:
            params["algoId"] = algo_id
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

    def get_algo_orders_pending(
        self,
        inst_type: Any = None,
        ord_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get pending algo orders"""
        path, params, extra_data = self._get_algo_orders_pending(
            inst_type, ord_type, uly, inst_id, algo_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_algo_orders_pending(
        self,
        inst_type: Any = None,
        ord_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get pending algo orders"""
        path, params, extra_data = self._get_algo_orders_pending(
            inst_type, ord_type, uly, inst_id, algo_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_algo_order_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get algo order history"""
        request_type = "get_algo_order_history"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if uly:
            params["uly"] = uly
        if inst_id:
            request_symbol = self._params.get_symbol(inst_id)
            params["instId"] = request_symbol
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
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_algo_order_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get algo order history"""
        path, params, extra_data = self._get_algo_order_history(
            inst_type, uly, inst_id, algo_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_algo_order_history(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        algo_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get algo order history"""
        path, params, extra_data = self._get_algo_order_history(
            inst_type, uly, inst_id, algo_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_algo_order(
        self,
        algo_id: Any = None,
        symbol: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get algo order details"""
        request_type = "get_algo_order"
        params: dict[str, Any] = {}
        if algo_id:
            params["algoId"] = algo_id
        if symbol:
            request_symbol = self._params.get_symbol(symbol)
            params["instId"] = request_symbol
        if inst_type:
            params["instType"] = inst_type
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_algo_order(
        self,
        algo_id: Any = None,
        symbol: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get algo order details"""
        path, params, extra_data = self._get_algo_order(
            algo_id, symbol, inst_type, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_algo_order(
        self,
        algo_id: Any = None,
        symbol: Any = None,
        inst_type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get algo order details"""
        path, params, extra_data = self._get_algo_order(
            algo_id, symbol, inst_type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_instrument_family_trades(
        self,
        inst_family: Any,
        uly: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get option instrument family trades data
        :param inst_family: Instrument family, e.g. `BTC-USD`
        :param uly: Underlying index
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_option_instrument_family_trades"
        params = {"instFamily": inst_family}
        if uly:
            params["uly"] = uly
        if limit:
            params["limit"] = limit
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_family,
                "asset_type": "OPTION",
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_option_instrument_family_trades(
        self,
        inst_family: Any,
        uly: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get option instrument family trades data"""
        path, params, extra_data = self._get_option_instrument_family_trades(
            inst_family, uly, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_instrument_family_trades(
        self,
        inst_family: Any,
        uly: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get option instrument family trades data"""
        path, params, extra_data = self._get_option_instrument_family_trades(
            inst_family, uly, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Option Trades ====================

    def _get_option_trades(
        self, inst_id: Any, limit: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get option trades data
        :param inst_id: Instrument ID, e.g. `BTC-USD-231229-40000-C`
        :param limit: Default 100, max 500
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_option_trades"
        params = {"instId": inst_id}
        if limit:
            params["limit"] = limit
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": "OPTION",
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_option_trades(
        self, inst_id: Any, limit: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get option trades data"""
        path, params, extra_data = self._get_option_trades(
            inst_id, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_trades(
        self, inst_id: Any, limit: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get option trades data"""
        path, params, extra_data = self._get_option_trades(
            inst_id, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== 24h Volume ====================

