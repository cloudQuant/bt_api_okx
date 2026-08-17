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


from bt_api_okx.feeds.live_okx.mixins.algo_mixin import AlgoMixin
from bt_api_okx.feeds.live_okx.mixins.batch_mixin import BatchMixin
from bt_api_okx.feeds.live_okx.mixins.convert_mixin import ConvertMixin
from bt_api_okx.feeds.live_okx.mixins.index_candles_mixin import IndexCandlesMixin


class MiscTradeMixin:
    """杂项交易方法集合。"""

    def async_get_clear_price(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_clear_price method"""
        data_type = "get_clear_price"
        path = self._params.get_rest_path(data_type)
        params = {"instId": self._params.get_symbol(symbol)}
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Option Instrument Family Trades ====================







    def _get_24h_volume(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get platform 24h total volume
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_24h_volume"
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

    def get_24h_volume(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get platform 24h total volume"""
        path, params, extra_data = self._get_24h_volume(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_24h_volume(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get platform 24h total volume"""
        path, params, extra_data = self._get_24h_volume(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Call Auction Details ====================

    def _get_call_auction_details(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get call auction details
        :param inst_type: Instrument type: `FUTURES`, `OPTION`
        :param uly: Underlying, required for `FUTURES`/`OPTION`
        :param inst_id: Instrument ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_call_auction_details"
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
                "symbol_name": inst_id or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_call_auction_details(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get call auction details"""
        path, params, extra_data = self._get_call_auction_details(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_call_auction_details(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get call auction details"""
        path, params, extra_data = self._get_call_auction_details(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Index Price ====================










































    def _cancel_all(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        """Cancel all orders"""
        request_type = "cancel_all"
        order_item = {"instType": inst_type}
        if inst_id:
            request_symbol = self._params.get_symbol(inst_id)
            order_item["instId"] = request_symbol
        params = [order_item]
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

    def cancel_all(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Cancel all orders"""
        path, params, extra_data = self._cancel_all(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_all(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async cancel all orders"""
        path, params, extra_data = self._cancel_all(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )




























