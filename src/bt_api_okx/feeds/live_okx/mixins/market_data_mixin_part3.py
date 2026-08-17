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


class MarketDataMixinPart3:
    """MarketDataMixinPart3 方法集合。"""

    def get_interest_rate(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        mgn_mode: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get interest rate for borrowing"""
        path, params, extra_data = self._get_interest_rate(
            ccy, inst_type, mgn_mode, uly, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_interest_rate(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        mgn_mode: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get interest rate for borrowing"""
        path, params, extra_data = self._get_interest_rate(
            ccy, inst_type, mgn_mode, uly, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_underlying(
        self, inst_type: Any, uly: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get underlying index
        :param inst_type: Instrument type: `FUTURES`, `SWAP`, `OPTION` (required)
        :param uly: Underlying
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_underlying"
        params = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": uly or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_underlying_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_underlying_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_underlying(
        self, inst_type: Any, uly: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get underlying index"""
        path, params, extra_data = self._get_underlying(
            inst_type, uly, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_underlying(
        self, inst_type: Any, uly: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get underlying index"""
        path, params, extra_data = self._get_underlying(
            inst_type, uly, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_insurance_fund(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get insurance fund balance
        :param inst_type: Instrument type: `MARGIN`, `FUTURES`, `SWAP`, `OPTION` (required)
        :param uly: Underlying
        :param inst_id: Instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_insurance_fund"
        params = {"instType": inst_type}
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
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_insurance_fund_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_insurance_fund_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_insurance_fund(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get insurance fund balance"""
        path, params, extra_data = self._get_insurance_fund(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_insurance_fund(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get insurance fund balance"""
        path, params, extra_data = self._get_insurance_fund(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _convert_contract_coin(
        self,
        inst_type: Any,
        uly: Any,
        inst_id: Any,
        amount: Any,
        unit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Convert contract unit
        :param inst_type: Instrument type: `FUTURES`, `SWAP` (required)
        :param uly: Underlying (required)
        :param inst_id: Instrument ID (required)
        :param amount: Quantity to be converted (required)
        :param unit: Unit of amount to be converted: `ccy`, `ct` (required)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "convert_contract_coin"
        params = {
            "instType": inst_type,
            "uly": uly,
            "instId": inst_id,
            "amount": amount,
            "unit": unit,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._convert_contract_coin_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _convert_contract_coin_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def convert_contract_coin(
        self,
        inst_type: Any,
        uly: Any,
        inst_id: Any,
        amount: Any,
        unit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Convert contract unit"""
        path, params, extra_data = self._convert_contract_coin(
            inst_type, uly, inst_id, amount, unit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_convert_contract_coin(
        self,
        inst_type: Any,
        uly: Any,
        inst_id: Any,
        amount: Any,
        unit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async convert contract unit"""
        path, params, extra_data = self._convert_contract_coin(
            inst_type, uly, inst_id, amount, unit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_instrument_tick_bands(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get instrument minimum tick size
        :param inst_type: Instrument type: `SPOT`, `MARGIN`, `FUTURES`, `SWAP`, `OPTION` (required)
        :param uly: Underlying
        :param inst_id: Instrument ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_instrument_tick_bands"
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
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_instrument_tick_bands_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_instrument_tick_bands_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_instrument_tick_bands(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get instrument minimum tick size"""
        path, params, extra_data = self._get_instrument_tick_bands(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_instrument_tick_bands(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get instrument minimum tick size"""
        path, params, extra_data = self._get_instrument_tick_bands(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Missing Critical Public APIs ====================

    def _get_system_time(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get system time"""
        request_type = "get_system_time"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "SYSTEM",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_system_time(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get system time"""
        path, params, extra_data = self._get_system_time(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_system_time(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get system time"""
        path, params, extra_data = self._get_system_time(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_tickers(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get tickers for all instruments"""
        request_type = "get_tickers"
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
                "symbol_name": inst_id or "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_tickers(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get tickers for all instruments"""
        path, params, extra_data = self._get_tickers(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_tickers(
        self,
        inst_type: Any = "SWAP",
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get tickers for all instruments"""
        path, params, extra_data = self._get_tickers(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_depth_full(
        self, symbol: Any, sz: Any = 100, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get full depth order book"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "get_depth_full"
        params = {"instId": request_symbol, "sz": sz}
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

    def get_depth_full(
        self, symbol: Any, sz: Any = 100, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get full depth order book"""
        path, params, extra_data = self._get_depth_full(
            symbol, sz, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_depth_full(
        self, symbol: Any, sz: Any = 100, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get full depth order book"""
        path, params, extra_data = self._get_depth_full(
            symbol, sz, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_kline_his(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get historical kline data"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "get_kline_his"
        params = {
            "instId": request_symbol,
            "bar": bar,
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
                "normalize_function": MarketDataMixin._get_kline_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_kline_his(
        self,
        symbol: Any,
        bar: Any = "1m",
        after: Any = "",
        before: Any = "",
        limit: Any = "100",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get historical kline data"""
        path, params, extra_data = self._get_kline_his(
            symbol, bar, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

