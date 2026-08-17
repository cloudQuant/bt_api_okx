"""
OKX API - StatisticsMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class StatisticsMixinPart2:
    """StatisticsMixinPart2 方法集合。"""

    @staticmethod
    def _get_option_oi_volume_expiry_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_option_oi_volume_expiry(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get option open interest and volume by expiry"""
        path, params, extra_data = self._get_option_oi_volume_expiry(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_oi_volume_expiry(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get option open interest and volume by expiry"""
        path, params, extra_data = self._get_option_oi_volume_expiry(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_oi_volume_strike(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get option open interest and volume by strike price
        :param ccy: Underlying index, e.g. "BTC-USD"
        :param currency: Margin currency, only support USD
        :param begin: Begin timestamp (ms)
        :param end: End timestamp (ms)
        :param period: Time period: `8H`, `1D`
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_option_oi_volume_strike"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if currency:
            params["currency"] = currency
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
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": StatisticsMixin._get_option_oi_volume_strike_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_option_oi_volume_strike_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_option_oi_volume_strike(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get option open interest and volume by strike price"""
        path, params, extra_data = self._get_option_oi_volume_strike(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_oi_volume_strike(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get option open interest and volume by strike price"""
        path, params, extra_data = self._get_option_oi_volume_strike(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_taker_flow(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get option taker block volume (large trades)
        :param ccy: Underlying index, e.g. "BTC-USD"
        :param currency: Margin currency, only support USD
        :param begin: Begin timestamp (ms)
        :param end: End timestamp (ms)
        :param period: Time period: `8H`, `1D`
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_option_taker_flow"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if currency:
            params["currency"] = currency
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
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": StatisticsMixin._get_option_taker_flow_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_option_taker_flow_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_option_taker_flow(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get option taker block volume (large trades)"""
        path, params, extra_data = self._get_option_taker_flow(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_taker_flow(
        self,
        ccy: Any = None,
        currency: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get option taker block volume (large trades)"""
        path, params, extra_data = self._get_option_taker_flow(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Position Builder APIs ====================

    def _position_builder(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Position builder - Calculate the maximum open size
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param uly: Underlying, e.g. BTC-USD
        :param inst_id: Instrument ID, e.g. BTC-USDT-SWAP
        :param ccy: Currency, e.g. BTC
        :param max_sz: Maximum open size
        :param margin_mode: Margin mode: cross, isolated, cash
        :param pos_side: Position side: long, short, net
        :param auto_sz: Whether to automatically calculate the size: true, false
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "position_builder"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if ccy:
            params["ccy"] = ccy
        if max_sz is not None:
            params["maxSz"] = str(max_sz)
        if margin_mode:
            params["mgnMode"] = margin_mode
        if pos_side:
            params["posSide"] = pos_side
        if auto_sz is not None:
            params["autoSz"] = str(auto_sz).lower()
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": StatisticsMixin._position_builder_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _position_builder_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize position builder response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def position_builder(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Position builder - Calculate the maximum open size"""
        path, params, extra_data = self._position_builder(
            inst_type,
            uly,
            inst_id,
            ccy,
            max_sz,
            margin_mode,
            pos_side,
            auto_sz,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_position_builder(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async position builder - Calculate the maximum open size"""
        path, params, extra_data = self._position_builder(
            inst_type,
            uly,
            inst_id,
            ccy,
            max_sz,
            margin_mode,
            pos_side,
            auto_sz,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _position_builder_trend(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Position builder trend - Get position builder trend data
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param uly: Underlying, e.g. BTC-USD
        :param inst_id: Instrument ID, e.g. BTC-USDT-SWAP
        :param ccy: Currency, e.g. BTC
        :param max_sz: Maximum open size
        :param margin_mode: Margin mode: cross, isolated, cash
        :param pos_side: Position side: long, short, net
        :param auto_sz: Whether to automatically calculate the size: true, false
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "position_builder_trend"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if ccy:
            params["ccy"] = ccy
        if max_sz is not None:
            params["maxSz"] = str(max_sz)
        if margin_mode:
            params["mgnMode"] = margin_mode
        if pos_side:
            params["posSide"] = pos_side
        if auto_sz is not None:
            params["autoSz"] = str(auto_sz).lower()
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": StatisticsMixin._position_builder_trend_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _position_builder_trend_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize position builder trend response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def position_builder_trend(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Position builder trend - Get position builder trend data"""
        path, params, extra_data = self._position_builder_trend(
            inst_type,
            uly,
            inst_id,
            ccy,
            max_sz,
            margin_mode,
            pos_side,
            auto_sz,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_position_builder_trend(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        max_sz: Any = None,
        margin_mode: Any = None,
        pos_side: Any = None,
        auto_sz: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async position builder trend - Get position builder trend data"""
        path, params, extra_data = self._position_builder_trend(
            inst_type,
            uly,
            inst_id,
            ccy,
            max_sz,
            margin_mode,
            pos_side,
            auto_sz,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Missing Trading Statistics APIs ====================

    @staticmethod
    def _get_support_coin_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get_support_coin response.
        API returns data with different coin types grouped by category.
        Response format: {"code": "0", "data": {"contract": [...], "option": [...], "spot": [...]}}
        """
        status = input_data.get("code") == "0"
        if "data" not in input_data or not input_data["data"]:
            return {}, status
        # Data is already a dict with keys: contract, option, spot
        data = input_data["data"]
        # Return dict as-is with keys: contract, option, spot
        return data, status

    def _get_support_coin(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get support coin"""
        request_type = "get_support_coin"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": StatisticsMixin._get_support_coin_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

