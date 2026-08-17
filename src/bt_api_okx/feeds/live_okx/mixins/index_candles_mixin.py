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


class IndexCandlesMixin:
    """指数/标记价格 K 线方法集合。"""

    def _get_index_price(
        self, index: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get index ticker data
        :param index: Index, e.g. `BTC-USD`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_index_price"
        params: dict[str, Any] = {}
        if index:
            params["instId"] = index
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": index or "ALL",
                "asset_type": "INDEX",
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_index_price(
        self, index: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get index ticker data"""
        path, params, extra_data = self._get_index_price(index, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_index_price(
        self, index: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get index ticker data"""
        path, params, extra_data = self._get_index_price(index, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Index Candles ====================

    def _get_index_candles(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get index candlestick charts
        :param index: Index, e.g. `BTC-USD`
        :param bar: Bar size, default `1m`. Options: `1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M`
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_index_candles"
        params = {
            "instId": index,
            "bar": self._params.get_period(bar),
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
                "symbol_name": index,
                "asset_type": "INDEX",
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._get_index_candles_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_index_candles_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize index candles data - API returns 6 elements, OkxBarData expects 9"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = sorted(input_data["data"], key=lambda x: x[0])
        if len(data) > 0:
            # Pad data from 6-7 elements to 9 elements for OkxBarData
            # API format: [ts, o, h, l, c, vol] or [ts, o, h, l, c, vol, vol_ccy]
            # OkxBarData expects: [ts, o, h, l, c, vol, base_vol, quote_vol, confirm]
            padded_data = []
            for row in data:
                padded = list(row)
                # Ensure we have at least 6 elements
                while len(padded) < 6:
                    padded.append("0")
                # Add missing elements to reach 9
                # Index 6: base_asset_volume (use vol if not present)
                if len(padded) < 7:
                    padded.append(padded[5])  # vol as base_vol
                else:
                    padded.append(padded[5])  # vol as base_vol
                # Index 7: quote_asset_volume (use vol_ccy or '0')
                if len(padded) < 8:
                    padded.append("0")  # no quote_vol for index
                # Index 8: confirm status
                if len(padded) < 9:
                    padded.append("1")
                padded_data.append(padded)

            data_list = [
                OkxBarData(i, extra_data["symbol_name"], extra_data["asset_type"], True)
                for i in padded_data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_index_candles(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get index candlestick charts"""
        path, params, extra_data = self._get_index_candles(
            index, bar, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_index_candles(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get index candlestick charts"""
        path, params, extra_data = self._get_index_candles(
            index, bar, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Mark Price Candles ====================

    def _get_mark_price_candles(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get mark price candlestick charts
        :param symbol: Instrument ID, e.g. `BTC-USDT`
        :param bar: Bar size, default `1m`. Options: `1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M`
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_mark_price_candles"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "bar": self._params.get_period(bar),
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
                "normalize_function": TradeMixin._get_mark_price_candles_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_mark_price_candles_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize mark price candles data - API returns 6-7 elements, OkxBarData expects 9"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = sorted(input_data["data"], key=lambda x: x[0])
        if len(data) > 0:
            # Pad data from 6-7 elements to 9 elements for OkxBarData
            # API format: [ts, o, h, l, c, vol] or [ts, o, h, l, c, vol, vol_ccy]
            # OkxBarData expects: [ts, o, h, l, c, vol, base_vol, quote_vol, confirm]
            padded_data = []
            for row in data:
                padded = list(row)
                # Ensure we have at least 6 elements
                while len(padded) < 6:
                    padded.append("0")
                # Add missing elements to reach 9
                # Index 6: base_asset_volume (use vol if not present)
                if len(padded) < 7:
                    padded.append(padded[5])  # vol as base_vol
                else:
                    padded.append(padded[5])  # vol as base_vol
                # Index 7: quote_asset_volume (use vol_ccy or '0')
                if len(padded) < 8:
                    padded.append("0")  # no quote_vol
                # Index 8: confirm status
                if len(padded) < 9:
                    padded.append("1")
                padded_data.append(padded)

            data_list = [
                OkxBarData(i, extra_data["symbol_name"], extra_data["asset_type"], True)
                for i in padded_data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_mark_price_candles(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get mark price candlestick charts"""
        path, params, extra_data = self._get_mark_price_candles(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_mark_price_candles(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get mark price candlestick charts"""
        path, params, extra_data = self._get_mark_price_candles(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Index Candles History ====================

    def _get_index_candles_history(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get historical index candlestick charts
        :param index: Index, e.g. `BTC-USD`
        :param bar: Bar size, default `1m`. Options: `1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M`
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_index_candles_history"
        params = {
            "instId": index,
            "bar": self._params.get_period(bar),
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
                "symbol_name": index,
                "asset_type": "INDEX",
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_index_candles_history(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get historical index candlestick charts"""
        path, params, extra_data = self._get_index_candles_history(
            index, bar, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_index_candles_history(
        self,
        index: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get historical index candlestick charts"""
        path, params, extra_data = self._get_index_candles_history(
            index, bar, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Mark Price Candles History ====================

    def _get_mark_price_candles_history(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get historical mark price candlestick charts
        :param symbol: Instrument ID, e.g. `BTC-USD-SWAP`
        :param bar: Bar size, default `1m`. Options: `1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M`
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_mark_price_candles_history"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "bar": self._params.get_period(bar),
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

    def get_mark_price_candles_history(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get historical mark price candlestick charts"""
        path, params, extra_data = self._get_mark_price_candles_history(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_mark_price_candles_history(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get historical mark price candlestick charts"""
        path, params, extra_data = self._get_mark_price_candles_history(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Missing Trade APIs ====================

