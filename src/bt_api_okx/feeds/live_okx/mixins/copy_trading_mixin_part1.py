"""
OKX API - CopyTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class CopyTradingMixinPart1:
    """CopyTradingMixinPart1 方法集合。"""

    def _copytrading_get_current_subpositions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get existing lead positions
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param inst_id: Instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_current_subpositions"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
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
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_current_subpositions_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_current_subpositions_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading current subpositions data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_current_subpositions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get existing lead positions"""
        path, params, extra_data = self._copytrading_get_current_subpositions(
            inst_type, inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_current_subpositions(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get existing lead positions"""
        path, params, extra_data = self._copytrading_get_current_subpositions(
            inst_type, inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_subpositions_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Lead position history
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param inst_id: Instrument ID
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_subpositions_history"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
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
                "asset_type": inst_type or self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_subpositions_history_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_subpositions_history_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading subpositions history data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_subpositions_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Lead position history"""
        path, params, extra_data = self._copytrading_get_subpositions_history(
            inst_type, inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_subpositions_history(
        self,
        inst_type: Any = None,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async lead position history"""
        path, params, extra_data = self._copytrading_get_subpositions_history(
            inst_type, inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_algo_order(
        self,
        sub_pos_id: Any,
        tp_trigger_px: Any = None,
        tp_trigger_px_type: Any = None,
        sl_trigger_px: Any = None,
        sl_trigger_px_type: Any = None,
        tp_ord_px: Any = None,
        sl_ord_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Place lead stop order
        :param sub_pos_id: Sub position ID
        :param tp_trigger_px: Take profit trigger price
        :param tp_trigger_px_type: Take profit trigger price type: last, index, mark
        :param sl_trigger_px: Stop loss trigger price
        :param sl_trigger_px_type: Stop loss trigger price type: last, index, mark
        :param tp_ord_px: Take profit order price
        :param sl_ord_px: Stop loss order price
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_algo_order"
        body = {
            "subPosId": sub_pos_id,
        }
        if tp_trigger_px is not None:
            body["tpTriggerPx"] = str(tp_trigger_px)
        if tp_trigger_px_type:
            body["tpTriggerPxType"] = tp_trigger_px_type
        if sl_trigger_px is not None:
            body["slTriggerPx"] = str(sl_trigger_px)
        if sl_trigger_px_type:
            body["slTriggerPxType"] = sl_trigger_px_type
        if tp_ord_px is not None:
            body["tpOrdPx"] = str(tp_ord_px)
        if sl_ord_px is not None:
            body["slOrdPx"] = str(sl_ord_px)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": sub_pos_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_algo_order_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_algo_order_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading algo order response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_algo_order(
        self,
        sub_pos_id: Any,
        tp_trigger_px: Any = None,
        tp_trigger_px_type: Any = None,
        sl_trigger_px: Any = None,
        sl_trigger_px_type: Any = None,
        tp_ord_px: Any = None,
        sl_ord_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Place lead stop order"""
        path, body, extra_data = self._copytrading_algo_order(
            sub_pos_id,
            tp_trigger_px,
            tp_trigger_px_type,
            sl_trigger_px,
            sl_trigger_px_type,
            tp_ord_px,
            sl_ord_px,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_algo_order(
        self,
        sub_pos_id: Any,
        tp_trigger_px: Any = None,
        tp_trigger_px_type: Any = None,
        sl_trigger_px: Any = None,
        sl_trigger_px_type: Any = None,
        tp_ord_px: Any = None,
        sl_ord_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async place lead stop order"""
        path, body, extra_data = self._copytrading_algo_order(
            sub_pos_id,
            tp_trigger_px,
            tp_trigger_px_type,
            sl_trigger_px,
            sl_trigger_px_type,
            tp_ord_px,
            sl_ord_px,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_close_subposition(
        self, sub_pos_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Close lead position
        :param sub_pos_id: Sub position ID
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_close_subposition"
        body = {
            "subPosId": sub_pos_id,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": sub_pos_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_close_subposition_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_close_subposition_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading close subposition response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_close_subposition(
        self, sub_pos_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Close lead position"""
        path, body, extra_data = self._copytrading_close_subposition(
            sub_pos_id, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_close_subposition(
        self, sub_pos_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async close lead position"""
        path, body, extra_data = self._copytrading_close_subposition(
            sub_pos_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_instruments(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Leading instruments
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_instruments"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_instruments_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_instruments_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading instruments data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_instruments(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Leading instruments"""
        path, params, extra_data = self._copytrading_get_instruments(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_instruments(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async leading instruments"""
        path, params, extra_data = self._copytrading_get_instruments(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_set_instruments(
        self,
        inst_type: Any,
        inst_ids: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Amend leading instruments
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param inst_ids: Instrument ID list
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "copytrading_set_instruments"
        body = {
            "instType": inst_type,
        }
        if inst_ids:
            body["instId"] = (
                ",".join(inst_ids) if isinstance(inst_ids, list) else inst_ids
            )
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_set_instruments_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    @staticmethod
    def _copytrading_set_instruments_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading set instruments response"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = [data[0]] if len(data) > 0 else []
        return target_data, status

    def copytrading_set_instruments(
        self,
        inst_type: Any,
        inst_ids: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Amend leading instruments"""
        path, body, extra_data = self._copytrading_set_instruments(
            inst_type, inst_ids, extra_data, **kwargs
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_copytrading_set_instruments(
        self,
        inst_type: Any,
        inst_ids: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async amend leading instruments"""
        path, body, extra_data = self._copytrading_set_instruments(
            inst_type, inst_ids, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Profit sharing details
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_profit_sharing_details"
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
                "normalize_function": CopyTradingMixin._copytrading_get_profit_sharing_details_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_profit_sharing_details_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading profit sharing details data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Profit sharing details"""
        path, params, extra_data = self._copytrading_get_profit_sharing_details(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async profit sharing details"""
        path, params, extra_data = self._copytrading_get_profit_sharing_details(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_total_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Total profit sharing
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_total_profit_sharing"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": CopyTradingMixin._copytrading_get_total_profit_sharing_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_total_profit_sharing_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading total profit sharing data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_total_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Total profit sharing"""
        path, params, extra_data = self._copytrading_get_total_profit_sharing(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_copytrading_get_total_profit_sharing(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async total profit sharing"""
        path, params, extra_data = self._copytrading_get_total_profit_sharing(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _copytrading_get_unrealized_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Unrealized profit sharing details
        :param after: Pagination (older data)
        :param before: Pagination (newer data)
        :param limit: Number of results, default 100, max 100
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "copytrading_get_unrealized_profit_sharing_details"
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
                "normalize_function": CopyTradingMixin._copytrading_get_unrealized_profit_sharing_details_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _copytrading_get_unrealized_profit_sharing_details_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize copy trading unrealized profit sharing details data"""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def copytrading_get_unrealized_profit_sharing_details(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Unrealized profit sharing details"""
        path, params, extra_data = (
            self._copytrading_get_unrealized_profit_sharing_details(
                after, before, limit, extra_data, **kwargs
            )
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

