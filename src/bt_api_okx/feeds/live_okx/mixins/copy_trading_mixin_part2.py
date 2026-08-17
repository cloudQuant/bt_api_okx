"""
OKX API - CopyTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class CopyTradingMixinPart2:
    """CopyTradingMixinPart2 方法集合。"""

    def async_copytrading_get_unrealized_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async unrealized profit sharing details"""
        path, params, extra_data = (
            self._copytrading_get_unrealized_profit_sharing_details(
                after, before, limit, extra_data, **kwargs
            )
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_total_unrealized_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Total unrealized profit sharing
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_total_unrealized_profit_sharing"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_total_unrealized_profit_sharing_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_total_unrealized_profit_sharing_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading total unrealized profit sharing data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_total_unrealized_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Total unrealized profit sharing"""
        path, params, extra_data = (
            self._copytrading_get_total_unrealized_profit_sharing(extra_data, **kwargs)
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_total_unrealized_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async total unrealized profit sharing"""
        path, params, extra_data = (
            self._copytrading_get_total_unrealized_profit_sharing(extra_data, **kwargs)
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_set_profit_sharing_ratio(
        self, profit_sharing_ratio: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Amend profit sharing ratio
        :param profit_sharing_ratio: Profit sharing ratio, e.g. 10 means 10%
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_set_profit_sharing_ratio"
        body = {
            "profitSharingRatio": str(profit_sharing_ratio),
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_set_profit_sharing_ratio_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_set_profit_sharing_ratio_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading set profit sharing ratio response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_set_profit_sharing_ratio(
        self, profit_sharing_ratio: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Amend profit sharing ratio"""
        path, body, extra_data = self._copytrading_set_profit_sharing_ratio(
            profit_sharing_ratio, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_set_profit_sharing_ratio(
        self, profit_sharing_ratio: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async amend profit sharing ratio"""
        path, body, extra_data = self._copytrading_set_profit_sharing_ratio(
            profit_sharing_ratio, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_config(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Account configuration
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_config"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading config data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_config(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Account configuration"""
        path, params, extra_data = self._copytrading_get_config(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_config(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async account configuration"""
        path, params, extra_data = self._copytrading_get_config(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_first_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        First copy settings
        :param copy_inst_id: Copy instrument ID, unique identifier for the lead trader
        :param lever: Leverage
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_first_copy_settings"
        body = {
            "copyInstId": copy_inst_id,
        }
        if lever is not None:
            body["lever"] = str(lever)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_first_copy_settings_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_first_copy_settings_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading first copy settings response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_first_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """First copy settings"""
        path, body, extra_data = self._copytrading_first_copy_settings(
            copy_inst_id, lever, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_first_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async first copy settings"""
        path, body, extra_data = self._copytrading_first_copy_settings(
            copy_inst_id, lever, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_amend_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Amend copy settings
        :param copy_inst_id: Copy instrument ID, unique identifier for the lead trader
        :param lever: Leverage
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_amend_copy_settings"
        body = {
            "copyInstId": copy_inst_id,
        }
        if lever is not None:
            body["lever"] = str(lever)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": copy_inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_amend_copy_settings_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_amend_copy_settings_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading amend copy settings response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_amend_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Amend copy settings"""
        path, body, extra_data = self._copytrading_amend_copy_settings(
            copy_inst_id, lever, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_amend_copy_settings(
        self,
        copy_inst_id: Any,
        lever: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async amend copy settings"""
        path, body, extra_data = self._copytrading_amend_copy_settings(
            copy_inst_id, lever, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_stop_copy_trading(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Stop copying
        :param copy_inst_id: Copy instrument ID, unique identifier for the lead trader
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_stop_copy_trading"
        body = {
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
                "normalize_function": CopyTradingMixin._copytrading_stop_copy_trading_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_stop_copy_trading_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading stop copy trading response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_stop_copy_trading(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Stop copying"""
        path, body, extra_data = self._copytrading_stop_copy_trading(
            copy_inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_stop_copy_trading(
        self, copy_inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async stop copying"""
        path, body, extra_data = self._copytrading_stop_copy_trading(
            copy_inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_copy_settings(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get copy settings
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_copy_settings"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_copy_settings_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_copy_settings_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading copy settings data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_copy_settings(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get copy settings"""
        path, params, extra_data = self._copytrading_get_copy_settings(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_copy_settings(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get copy settings"""
        path, params, extra_data = self._copytrading_get_copy_settings(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_batch_leverage_info(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        My lead traders
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_batch_leverage_info"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_batch_leverage_info_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_batch_leverage_info_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading batch leverage info data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_batch_leverage_info(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """My lead traders"""
        path, params, extra_data = self._copytrading_get_batch_leverage_info(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_batch_leverage_info(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async my lead traders"""
        path, params, extra_data = self._copytrading_get_batch_leverage_info(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_copy_trading_configuration(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Copy trading configuration
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_copy_trading_configuration"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_copy_trading_configuration_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_copy_trading_configuration_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading configuration data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

