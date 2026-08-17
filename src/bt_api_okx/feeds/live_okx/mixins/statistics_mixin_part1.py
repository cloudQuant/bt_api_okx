"""
OKX API - StatisticsMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class StatisticsMixinPart1:
    """StatisticsMixinPart1 方法集合。"""

    def _get_taker_volume_contract(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get contract active buy/sell volume (taker volume)
        :param ccy: Currency, e.g. "BTC"
        :param inst_type: Instrument type: `SWAP`, `FUTURES`, `OPTION`
        :param begin: Begin timestamp (ms)
        :param end: End timestamp (ms)
        :param period: Time period: `5m`, `1H`, `1D`
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_taker_volume_contract"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if inst_type:
            params["instType"] = inst_type
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
                "normalize_function": StatisticsMixin._get_taker_volume_contract_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_taker_volume_contract_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_taker_volume_contract(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get contract active buy/sell volume (taker volume)"""
        path, params, extra_data = self._get_taker_volume_contract(
            ccy, inst_type, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_taker_volume_contract(
        self,
        ccy: Any = None,
        inst_type: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get contract active buy/sell volume (taker volume)"""
        path, params, extra_data = self._get_taker_volume_contract(
            ccy, inst_type, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_margin_loan_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get margin loan ratio (spot long/short ratio)
        :param ccy: Currency, e.g. "BTC"
        :param begin: Begin timestamp (ms)
        :param end: End timestamp (ms)
        :param period: Time period: `5m`, `1H`, `1D`
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_margin_loan_ratio"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
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
                "normalize_function": StatisticsMixin._get_margin_loan_ratio_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_margin_loan_ratio_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_margin_loan_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get margin loan ratio (spot long/short ratio)"""
        path, params, extra_data = self._get_margin_loan_ratio(
            ccy, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_margin_loan_ratio(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get margin loan ratio (spot long/short ratio)"""
        path, params, extra_data = self._get_margin_loan_ratio(
            ccy, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_long_short_ratio(
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
        Get option long/short ratio
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
        request_type = "get_option_long_short_ratio"
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
                "normalize_function": StatisticsMixin._get_option_long_short_ratio_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_option_long_short_ratio_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_option_long_short_ratio(
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
        """Get option long/short ratio"""
        path, params, extra_data = self._get_option_long_short_ratio(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_long_short_ratio(
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
        """Async get option long/short ratio"""
        path, params, extra_data = self._get_option_long_short_ratio(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_contracts_oi_volume(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get contract open interest and volume
        :param ccy: Currency, e.g. "BTC"
        :param begin: Begin timestamp (ms)
        :param end: End timestamp (ms)
        :param period: Time period: `5m`, `1H`, `1D`
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_contracts_oi_volume"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
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
                "normalize_function": StatisticsMixin._get_contracts_oi_volume_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_contracts_oi_volume_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_contracts_oi_volume(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get contract open interest and volume"""
        path, params, extra_data = self._get_contracts_oi_volume(
            ccy, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_contracts_oi_volume(
        self,
        ccy: Any = None,
        begin: Any = None,
        end: Any = None,
        period: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get contract open interest and volume"""
        path, params, extra_data = self._get_contracts_oi_volume(
            ccy, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_oi_volume(
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
        Get option open interest and volume
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
        request_type = "get_option_oi_volume"
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
                "normalize_function": StatisticsMixin._get_option_oi_volume_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_option_oi_volume_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_option_oi_volume(
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
        """Get option open interest and volume"""
        path, params, extra_data = self._get_option_oi_volume(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_option_oi_volume(
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
        """Async get option open interest and volume"""
        path, params, extra_data = self._get_option_oi_volume(
            ccy, currency, begin, end, period, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_option_oi_volume_expiry(
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
        Get option open interest and volume by expiry
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
        request_type = "get_option_oi_volume_expiry"
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
                "normalize_function": StatisticsMixin._get_option_oi_volume_expiry_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

