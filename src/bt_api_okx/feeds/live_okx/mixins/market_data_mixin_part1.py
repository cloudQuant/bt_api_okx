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


class MarketDataMixinPart1:
    """MarketDataMixinPart1 方法集合。"""

    def _get_tick(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_tick"
        path = self._params.get_rest_path(request_type)
        params = {
            "instId": self._params.get_symbol(symbol),
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_tick_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_tick_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"][0]
        if len(data) > 0:
            data_list = [
                OkxTickerData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_tick(self, symbol: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        """get_tick method"""
        path, params, extra_data = self._get_tick(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_tick(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_tick method"""
        path, params, extra_data = self._get_tick(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_depth(
        self, symbol: Any, size: Any = 20, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_depth"
        request_symbol = self._params.get_symbol(symbol)
        params = {"instId": request_symbol, "sz": size}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_depth_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_depth_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"][0]
        if len(data) > 0:
            data_list = [
                OkxOrderBookData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_depth(
        self, symbol: Any, size: Any = 20, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """get_depth method"""
        path, params, extra_data = self._get_depth(symbol, size, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_depth(
        self, symbol: Any, size: Any = 20, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_depth method"""
        path, params, extra_data = self._get_depth(symbol, size, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_kline(
        self,
        symbol: Any,
        period: Any,
        count: Any = 100,
        start_time: Any = 0,
        end_time: Any = 0,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_kline"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "bar": self._params.get_period(period),
        }
        if count and count != 100:
            params["limit"] = count
        if end_time:
            params.update({"after": end_time})
        if start_time:
            params.update({"before": start_time})
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_kline_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_kline_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = sorted(input_data["data"], key=lambda x: x[0])
        if len(data) > 0:
            data_list = [
                OkxBarData(i, extra_data["symbol_name"], extra_data["asset_type"], True)
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_kline(
        self,
        symbol: Any,
        period: Any,
        count: Any = 100,
        start_time: Any = None,
        end_time: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_kline method"""
        path, params, extra_data = self._get_kline(
            symbol, period, count, start_time, end_time, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    # noinspection PyMethodMayBeStatic
    def async_get_kline(
        self,
        symbol: Any,
        period: Any,
        count: Any = 100,
        before: Any = 0,
        after: Any = 0,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """async_get_kline method"""
        path, params, extra_data = self._get_kline(
            symbol, period, count, before, after, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Public Data APIs ====================

    def _get_funding_rate(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_funding_rate"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_funding_rate_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_funding_rate_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"][0]
        if len(data) > 0:
            data_list = [
                OkxFundingRateData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_funding_rate(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """get_funding_rate method"""
        path, params, extra_data = self._get_funding_rate(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_funding_rate(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_funding_rate method"""
        path, params, extra_data = self._get_funding_rate(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_funding_rate_history(
        self,
        symbol: Any,
        before: Any = "",
        after: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get funding rate history"""
        request_type = "get_funding_rate_history"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
        }
        if before:
            params["before"] = before
        if after:
            params["after"] = after
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
                "normalize_function": MarketDataMixin._get_funding_rate_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_funding_rate_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxFundingRateData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_funding_rate_history(
        self,
        symbol: Any,
        before: Any = "",
        after: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_funding_rate_history method"""
        path, params, extra_data = self._get_funding_rate_history(
            symbol, before, after, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def _get_instruments(
        self,
        asset_type: Any = None,
        underlying: Any = None,
        inst_family: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_instruments"
        params: dict[str, Any] = {}
        if asset_type:
            params["instType"] = asset_type
        if underlying:
            params["uly"] = underlying
        if inst_family:
            params["instFamily"] = inst_family
        if inst_id:
            params["instId"] = inst_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_instruments_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_instruments_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if isinstance(data, list):
            target_data = [OkxSymbolData(i, True) for i in data]
        elif isinstance(data, dict):
            target_data = [OkxSymbolData(data, True)]
        else:
            target_data = []
        return target_data, status

    def get_instruments(
        self,
        asset_type: Any = None,
        underlying: Any = None,
        inst_family: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_instruments method"""
        path, params, extra_data = self._get_instruments(
            asset_type, underlying, inst_family, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def _get_mark_price(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_type = "get_mark_price"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": "SPOT",
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_mark_price_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_mark_price_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        data = input_data["data"][0]
        if len(data) > 0:
            data_list = [
                OkxMarkPriceData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_mark_price(self, symbol: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        """get_mark_price method"""
        path, params, extra_data = self._get_mark_price(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_mark_price(
        self, symbol: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_mark_price method"""
        path, params, extra_data = self._get_mark_price(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_open_interest(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_family: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get open interest data"""
        request_type = "get_open_interest"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_family:
            params["instFamily"] = inst_family
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

    def get_open_interest(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_family: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_open_interest method"""
        path, params, extra_data = self._get_open_interest(
            inst_type, uly, inst_family, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_open_interest(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_family: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get open interest data"""
        path, params, extra_data = self._get_open_interest(
            inst_type, uly, inst_family, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

