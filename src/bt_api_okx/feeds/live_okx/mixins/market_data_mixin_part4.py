"""
OKX API - MarketDataMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.fundingrates.okx_funding_rate import OkxFundingRateData
from bt_api_okx.containers.markprices.okx_mark_price import OkxMarkPriceData
from bt_api_okx.containers.orderbooks.okx_orderbook import OkxOrderBookData
from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class MarketDataMixinPart4:
    """MarketDataMixinPart4 方法集合。"""

    def async_get_kline_his(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get historical kline data"""
        path, params, extra_data = self._get_kline_his(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_trades(
        self, symbol: Any, limit: Any = "100", extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get recent trades"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "get_trades"
        params = {"instId": request_symbol, "limit": limit}
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

    def get_trades(
        self, symbol: Any, limit: Any = "100", extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get recent trades"""
        path, params, extra_data = self._get_trades(symbol, limit, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_trades(
        self, symbol: Any, limit: Any = "100", extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get recent trades"""
        path, params, extra_data = self._get_trades(symbol, limit, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_trades_history(
        self,
        symbol: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get historical trades data"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "get_trades_history"
        params = {
            "instId": request_symbol,
        }
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
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_trades_history(
        self,
        symbol: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get historical trades data"""
        path, params, extra_data = self._get_trades_history(
            symbol, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_trades_history(
        self,
        symbol: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get historical trades data"""
        path, params, extra_data = self._get_trades_history(
            symbol, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_public_instruments(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        uly_multi: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get public instruments"""
        request_type = "get_public_instruments"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        if uly_multi:
            params["ulyMulti"] = uly_multi
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

    def get_public_instruments(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        uly_multi: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get public instruments"""
        path, params, extra_data = self._get_public_instruments(
            inst_type, uly, inst_id, uly_multi, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_public_instruments(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        uly_multi: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get public instruments"""
        path, params, extra_data = self._get_public_instruments(
            inst_type, uly, inst_id, uly_multi, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_delivery_exercise_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get delivery exercise history"""
        request_type = "get_delivery_exercise_history"
        params = {
            "instType": inst_type,
            "uly": uly,
        }
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
                "symbol_name": uly,
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_delivery_exercise_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get delivery exercise history"""
        path, params, extra_data = self._get_delivery_exercise_history(
            inst_type, uly, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_delivery_exercise_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get delivery exercise history"""
        path, params, extra_data = self._get_delivery_exercise_history(
            inst_type, uly, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_estimated_settlement_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get estimated settlement price"""
        request_type = "get_estimated_settlement_price"
        params = {"instType": inst_type}
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
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_estimated_settlement_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get estimated settlement price"""
        path, params, extra_data = self._get_estimated_settlement_price(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_estimated_settlement_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get estimated settlement price"""
        path, params, extra_data = self._get_estimated_settlement_price(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_settlement_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get settlement history"""
        request_type = "get_settlement_history"
        params = {
            "instType": inst_type,
            "uly": uly,
        }
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
                "symbol_name": uly,
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_settlement_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get settlement history"""
        path, params, extra_data = self._get_settlement_history(
            inst_type, uly, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_settlement_history(
        self,
        inst_type: Any,
        uly: Any,
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get settlement history"""
        path, params, extra_data = self._get_settlement_history(
            inst_type, uly, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_price_limit(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get price limit"""
        request_type = "get_price_limit"
        params = {"instType": inst_type}
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
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_price_limit(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get price limit"""
        path, params, extra_data = self._get_price_limit(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_price_limit(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get price limit"""
        path, params, extra_data = self._get_price_limit(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_opt_summary(
        self,
        inst_type: Any = "OPTION",
        uly: Any = None,
        exp_time: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get option summary"""
        request_type = "get_opt_summary"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if exp_time:
            params["expTime"] = exp_time
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": uly or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_opt_summary(
        self,
        inst_type: Any = "OPTION",
        uly: Any = None,
        exp_time: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get option summary"""
        path, params, extra_data = self._get_opt_summary(
            inst_type, uly, exp_time, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_opt_summary(
        self,
        inst_type: Any = "OPTION",
        uly: Any = None,
        exp_time: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get option summary"""
        path, params, extra_data = self._get_opt_summary(
            inst_type, uly, exp_time, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_position_tiers_public(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get position tiers (public)"""
        request_type = "get_position_tiers_public"
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

    def get_position_tiers_public(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get position tiers (public)"""
        path, params, extra_data = self._get_position_tiers_public(
            inst_type, uly, inst_id, tier, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_position_tiers_public(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        tier: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get position tiers (public)"""
        path, params, extra_data = self._get_position_tiers_public(
            inst_type, uly, inst_id, tier, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

