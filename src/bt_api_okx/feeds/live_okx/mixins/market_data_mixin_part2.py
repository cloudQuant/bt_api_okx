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


class MarketDataMixinPart2:
    """MarketDataMixinPart2 方法集合。"""

    def _get_premium_history(
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
        Get premium history
        :param inst_type: Instrument type: `FUTURES`, `SWAP` (required)
        :param uly: Underlying
        :param inst_id: Instrument ID
        :param after: Pagination (older data), request before this timestamp
        :param before: Pagination (newer data), request after this timestamp
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_premium_history"
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
                "normalize_function": MarketDataMixin._get_premium_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_premium_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_premium_history(
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
        """Get premium history"""
        path, params, extra_data = self._get_premium_history(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_premium_history(
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
        """Async get premium history"""
        path, params, extra_data = self._get_premium_history(
            inst_type, uly, inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_economic_calendar(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get economic calendar
        :param after: Pagination (older data), request before this timestamp
        :param before: Pagination (newer data), request after this timestamp
        :param limit: Number of results, default 20, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_economic_calendar"
        params: dict[str, Any] = {}
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
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_economic_calendar_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_economic_calendar_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_economic_calendar(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get economic calendar"""
        path, params, extra_data = self._get_economic_calendar(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_economic_calendar(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get economic calendar"""
        path, params, extra_data = self._get_economic_calendar(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Market Data APIs (continued) ====================

    def _get_exchange_rate(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get exchange rate
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_exchange_rate"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_exchange_rate_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_exchange_rate_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_exchange_rate(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get exchange rate"""
        path, params, extra_data = self._get_exchange_rate(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_exchange_rate(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get exchange rate"""
        path, params, extra_data = self._get_exchange_rate(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_index_components(
        self, index: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get index components
        :param index: Index name, e.g. "BTC-USD"
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_index_components"
        params = {"index": index}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": index,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_index_components_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_index_components_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return {}, status
        data = input_data["data"]
        # The API returns a dict with 'components', 'index', 'last', 'ts' keys.
        target_data = (data[0] if isinstance(data, list) else data) if data else {}
        return target_data, status

    def get_index_components(
        self, index: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get index components"""
        path, params, extra_data = self._get_index_components(
            index, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_index_components(
        self, index: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get index components"""
        path, params, extra_data = self._get_index_components(
            index, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Public Data APIs (Additional) ====================

    def _get_estimated_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get estimated delivery/exercise price
        :param inst_type: Instrument type: `FUTURES`, `OPTION` (required)
        :param uly: Underlying
        :param inst_id: Instrument ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_estimated_price"
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
                "normalize_function": MarketDataMixin._get_estimated_price_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_estimated_price_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_estimated_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get estimated delivery/exercise price"""
        path, params, extra_data = self._get_estimated_price(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_estimated_price(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get estimated delivery/exercise price"""
        path, params, extra_data = self._get_estimated_price(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_discount_rate(
        self,
        ccy: Any = None,
        discount_level: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get discount rate and interest-free quota
        :param ccy: Currency, e.g. `BTC`
        :param discount_level: Discount level, default is `lv1`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_discount_rate"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if discount_level:
            params["discountLevel"] = discount_level
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_discount_rate_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_discount_rate_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_discount_rate(
        self,
        ccy: Any = None,
        discount_level: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get discount rate and interest-free quota"""
        path, params, extra_data = self._get_discount_rate(
            ccy, discount_level, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_discount_rate(
        self,
        ccy: Any = None,
        discount_level: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get discount rate and interest-free quota"""
        path, params, extra_data = self._get_discount_rate(
            ccy, discount_level, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_interest_rate_loan_quota(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get interest rate and loan quota
        :param ccy: Currency, e.g. `BTC`
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_interest_rate_loan_quota"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": MarketDataMixin._get_interest_rate_loan_quota_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_interest_rate_loan_quota_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_interest_rate_loan_quota(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get interest rate and loan quota"""
        path, params, extra_data = self._get_interest_rate_loan_quota(
            ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_interest_rate_loan_quota(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get interest rate and loan quota"""
        path, params, extra_data = self._get_interest_rate_loan_quota(
            ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_interest_rate(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        mgn_mode: Any = None,
        uly: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get interest rate for borrowing
        :param ccy: Currency, e.g. `BTC`
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param mgn_mode: Margin mode, cross or isolated
        :param uly: Underlying, e.g. BTC-USD
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_interest_rate"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if inst_type:
            params["instType"] = inst_type
        if mgn_mode:
            params["mgnMode"] = mgn_mode
        if uly:
            params["uly"] = uly
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy or uly or "ALL",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

