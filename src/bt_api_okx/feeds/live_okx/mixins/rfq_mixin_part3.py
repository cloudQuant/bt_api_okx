"""OKX API - RfqMixin
Auto-generated from request_base.py.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class RfqMixinPart3:
    """RfqMixinPart3 方法集合。"""

    def rfq_cancel_all_after(
        self,
        inst_id: Any,
        cancel_after: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set timer to cancel all RFQ quotes."""
        path, params, extra_data = self._rfq_cancel_all_after(
            inst_id, cancel_after, cl_ord_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_rfq_cancel_all_after(
        self,
        inst_id: Any,
        cancel_after: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set timer to cancel all RFQ quotes."""
        path, params, extra_data = self._rfq_cancel_all_after(
            inst_id, cancel_after, cl_ord_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_rfqs(
        self,
        inst_type: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get RFQs list."""
        request_type = "get_rfqs"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
        if state:
            params["state"] = state
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
                "normalize_function": RfqMixin._get_rfqs_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_rfqs_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get RFQs response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_rfqs(
        self,
        inst_type: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get RFQs list."""
        path, params, extra_data = self._get_rfqs(
            inst_type, state, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_rfqs(
        self,
        inst_type: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get RFQs list."""
        path, params, extra_data = self._get_rfqs(
            inst_type, state, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_rfq_quotes(
        self,
        rfq_id: Any = None,
        inst_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get RFQ quotes list."""
        request_type = "get_rfq_quotes"
        params: dict[str, Any] = {}
        if rfq_id:
            params["rfqId"] = rfq_id
        if inst_id:
            params["instId"] = inst_id
        if state:
            params["state"] = state
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_rfq_quotes_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_rfq_quotes_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get RFQ quotes response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_rfq_quotes(
        self,
        rfq_id: Any = None,
        inst_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get RFQ quotes list."""
        path, params, extra_data = self._get_rfq_quotes(
            rfq_id, inst_id, state, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_rfq_quotes(
        self,
        rfq_id: Any = None,
        inst_id: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get RFQ quotes list."""
        path, params, extra_data = self._get_rfq_quotes(
            rfq_id, inst_id, state, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_rfq_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get RFQ trades."""
        request_type = "get_rfq_trades"
        params: dict[str, Any] = {}
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_rfq_trades_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_rfq_trades_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get RFQ trades response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_rfq_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get RFQ trades."""
        path, params, extra_data = self._get_rfq_trades(
            inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_rfq_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get RFQ trades."""
        path, params, extra_data = self._get_rfq_trades(
            inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_public_rfq_trades(
        self,
        inst_type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get public RFQ trades (multi-leg)."""
        request_type = "get_public_rfq_trades"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
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
                "normalize_function": RfqMixin._get_public_rfq_trades_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_public_rfq_trades_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get public RFQ trades response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_public_rfq_trades(
        self,
        inst_type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get public RFQ trades (multi-leg)."""
        path, params, extra_data = self._get_public_rfq_trades(
            inst_type, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_public_rfq_trades(
        self,
        inst_type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get public RFQ trades (multi-leg)."""
        path, params, extra_data = self._get_public_rfq_trades(
            inst_type, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_block_tickers(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get block tickers."""
        request_type = "get_block_tickers"
        params: dict[str, Any] = {}
        if inst_type:
            params["instType"] = inst_type
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_block_tickers_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_block_tickers_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get block tickers response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_block_tickers(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get block tickers."""
        path, params, extra_data = self._get_block_tickers(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_block_tickers(
        self,
        inst_type: Any = None,
        uly: Any = None,
        inst_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get block tickers."""
        path, params, extra_data = self._get_block_tickers(
            inst_type, uly, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_block_ticker(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get single block ticker."""
        request_type = "get_block_ticker"
        params = {"instId": inst_id}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_block_ticker_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_block_ticker_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get block ticker response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_block_ticker(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get single block ticker."""
        path, params, extra_data = self._get_block_ticker(inst_id, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_block_ticker(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get single block ticker."""
        path, params, extra_data = self._get_block_ticker(inst_id, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_public_block_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get public block trades (single-leg)."""
        request_type = "get_public_block_trades"
        params: dict[str, Any] = {}
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
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_public_block_trades_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_public_block_trades_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get public block trades response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_public_block_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get public block trades (single-leg)."""
        path, params, extra_data = self._get_public_block_trades(
            inst_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_public_block_trades(
        self,
        inst_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get public block trades (single-leg)."""
        path, params, extra_data = self._get_public_block_trades(
            inst_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

