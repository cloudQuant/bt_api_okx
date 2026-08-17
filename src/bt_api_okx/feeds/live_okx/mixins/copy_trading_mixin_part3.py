"""
OKX API - CopyTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class CopyTradingMixinPart3:
    """CopyTradingMixinPart3 方法集合。"""

    def copytrading_get_copy_trading_configuration(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Copy trading configuration"""
        path, params, extra_data = self._copytrading_get_copy_trading_configuration(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_copy_trading_configuration(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async copy trading configuration"""
        path, params, extra_data = self._copytrading_get_copy_trading_configuration(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Copy Trading Public APIs ====================

    def _copytrading_public_lead_traders(
        self,
        inst_type: Any = None,
        sort_by: Any = None,
        uly: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader ranks (public)
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param sort_by: Sort by, e.g. totalProfitSharing
        :param uly: Underlying
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_lead_traders"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if sort_by:
            params["sortBy"] = sort_by
        if uly:
            params["uly"] = uly
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
                "symbol_name": "PUBLIC",
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_lead_traders_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_lead_traders_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public lead traders data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_lead_traders(
        self,
        inst_type: Any = None,
        sort_by: Any = None,
        uly: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead trader ranks (public)"""
        path, params, extra_data = self._copytrading_public_lead_traders(
            inst_type, sort_by, uly, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_lead_traders(
        self,
        inst_type: Any = None,
        sort_by: Any = None,
        uly: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead trader ranks (public)"""
        path, params, extra_data = self._copytrading_public_lead_traders(
            inst_type, sort_by, uly, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_weekly_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader weekly PnL (public)
        :param copy_inst_id: Copy instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_weekly_pnl"
        params = {
            "copyInstId": copy_inst_id,
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
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_weekly_pnl_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_weekly_pnl_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public weekly PnL data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_weekly_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead trader weekly PnL (public)"""
        path, params, extra_data = self._copytrading_public_weekly_pnl(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_weekly_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead trader weekly PnL (public)"""
        path, params, extra_data = self._copytrading_public_weekly_pnl(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader daily PnL (public)
        :param copy_inst_id: Copy instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_pnl"
        params = {
            "copyInstId": copy_inst_id,
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
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_pnl_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_pnl_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public PnL data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead trader daily PnL (public)"""
        path, params, extra_data = self._copytrading_public_pnl(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_pnl(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead trader daily PnL (public)"""
        path, params, extra_data = self._copytrading_public_pnl(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_stats(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader stats (public)
        :param copy_inst_id: Copy instrument ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_stats"
        params = {
            "copyInstId": copy_inst_id,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_stats_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_stats_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public stats data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_stats(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Lead trader stats (public)"""
        path, params, extra_data = self._copytrading_public_stats(
            copy_inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_stats(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async lead trader stats (public)"""
        path, params, extra_data = self._copytrading_public_stats(
            copy_inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_preference_currency(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader currency preferences (public)
        :param copy_inst_id: Copy instrument ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_preference_currency"
        params = {
            "copyInstId": copy_inst_id,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_preference_currency_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_preference_currency_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public preference currency data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_preference_currency(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Lead trader currency preferences (public)"""
        path, params, extra_data = self._copytrading_public_preference_currency(
            copy_inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_preference_currency(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async lead trader currency preferences (public)"""
        path, params, extra_data = self._copytrading_public_preference_currency(
            copy_inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_current_subpositions(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader current positions (public)
        :param copy_inst_id: Copy instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_current_subpositions"
        params = {
            "copyInstId": copy_inst_id,
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
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_current_subpositions_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_current_subpositions_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public current subpositions data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_current_subpositions(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead trader current positions (public)"""
        path, params, extra_data = self._copytrading_public_current_subpositions(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_current_subpositions(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead trader current positions (public)"""
        path, params, extra_data = self._copytrading_public_current_subpositions(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_subpositions_history(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead trader position history (public)
        :param copy_inst_id: Copy instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_subpositions_history"
        params = {
            "copyInstId": copy_inst_id,
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
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_subpositions_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_subpositions_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public subpositions history data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_subpositions_history(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead trader position history (public)"""
        path, params, extra_data = self._copytrading_public_subpositions_history(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_subpositions_history(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead trader position history (public)"""
        path, params, extra_data = self._copytrading_public_subpositions_history(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_public_copy_traders(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Copy traders (public)
        :param copy_inst_id: Copy instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_public_copy_traders"
        params = {
            "copyInstId": copy_inst_id,
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
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_public_copy_traders_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_public_copy_traders_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading public copy traders data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_public_copy_traders(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Copy traders (public)"""
        path, params, extra_data = self._copytrading_public_copy_traders(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_public_copy_traders(
        self,
        copy_inst_id: Any,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async copy traders (public)"""
        path, params, extra_data = self._copytrading_public_copy_traders(
            copy_inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

