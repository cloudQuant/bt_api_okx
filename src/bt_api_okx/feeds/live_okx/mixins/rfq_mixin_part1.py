"""OKX API - RfqMixin
Auto-generated from request_base.py.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class RfqMixinPart1:
    """RfqMixinPart1 方法集合。"""

    def _get_counterparties(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get RFQ counterparties list."""
        request_type = "get_counterparties"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_counterparties_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_counterparties_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize RFQ counterparties response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_counterparties(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get RFQ counterparties list."""
        path, params, extra_data = self._get_counterparties(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_counterparties(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get RFQ counterparties list."""
        path, params, extra_data = self._get_counterparties(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _create_rfq(
        self,
        inst_id: Any,
        side: Any,
        sz: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create RFQ."""
        request_type = "create_rfq"
        path = self._params.get_rest_path(request_type)
        params = {
            "instId": inst_id,
            "side": side,
            "sz": sz,
        }
        if ccy:
            params["ccy"] = ccy
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        if tag:
            params["tag"] = tag
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._create_rfq_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _create_rfq_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize create RFQ response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def create_rfq(
        self,
        inst_id: Any,
        side: Any,
        sz: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Create RFQ."""
        path, params, extra_data = self._create_rfq(
            inst_id, side, sz, ccy, cl_ord_id, tag, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_create_rfq(
        self,
        inst_id: Any,
        side: Any,
        sz: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async create RFQ."""
        path, params, extra_data = self._create_rfq(
            inst_id, side, sz, ccy, cl_ord_id, tag, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_rfq(
        self, rfq_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel RFQ."""
        request_type = "cancel_rfq"
        path = self._params.get_rest_path(request_type)
        params = {
            "rfqId": rfq_id,
            "instId": inst_id,
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_rfq_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_rfq_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel RFQ response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_rfq(
        self, rfq_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel RFQ."""
        path, params, extra_data = self._cancel_rfq(
            rfq_id, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_rfq(
        self, rfq_id: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel RFQ."""
        path, params, extra_data = self._cancel_rfq(
            rfq_id, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_multiple_rfqs(
        self, rfq_ids: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel multiple RFQs."""
        request_type = "cancel_multiple_rfqs"
        path = self._params.get_rest_path(request_type)
        params = {
            "rfqIds": rfq_ids if isinstance(rfq_ids, str) else ",".join(rfq_ids),
            "instId": inst_id,
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_multiple_rfqs_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_multiple_rfqs_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel multiple RFQs response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_multiple_rfqs(
        self, rfq_ids: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel multiple RFQs."""
        path, params, extra_data = self._cancel_multiple_rfqs(
            rfq_ids, inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_multiple_rfqs(
        self, rfq_ids: Any, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel multiple RFQs."""
        path, params, extra_data = self._cancel_multiple_rfqs(
            rfq_ids, inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_all_rfqs(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel all RFQs."""
        request_type = "cancel_all_rfqs"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id}
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_all_rfqs_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_all_rfqs_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel all RFQs response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_all_rfqs(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel all RFQs."""
        path, params, extra_data = self._cancel_all_rfqs(inst_id, extra_data, **kwargs)
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_all_rfqs(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel all RFQs."""
        path, params, extra_data = self._cancel_all_rfqs(inst_id, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _execute_quote(
        self,
        quote_id: Any,
        inst_id: Any,
        side: Any,
        sz: Any,
        px: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Execute quote."""
        request_type = "execute_quote"
        path = self._params.get_rest_path(request_type)
        params = {
            "quoteId": quote_id,
            "instId": inst_id,
            "side": side,
            "sz": sz,
            "px": px,
        }
        if ccy:
            params["ccy"] = ccy
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        if tag:
            params["tag"] = tag
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._execute_quote_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _execute_quote_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize execute quote response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def execute_quote(
        self,
        quote_id: Any,
        inst_id: Any,
        side: Any,
        sz: Any,
        px: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Execute quote."""
        path, params, extra_data = self._execute_quote(
            quote_id, inst_id, side, sz, px, ccy, cl_ord_id, tag, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_execute_quote(
        self,
        quote_id: Any,
        inst_id: Any,
        side: Any,
        sz: Any,
        px: Any,
        ccy: Any = None,
        cl_ord_id: Any = None,
        tag: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async execute quote."""
        path, params, extra_data = self._execute_quote(
            quote_id, inst_id, side, sz, px, ccy, cl_ord_id, tag, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_quote_products(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get quote products list."""
        request_type = "get_quote_products"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_quote_products_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_quote_products_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize quote products response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_quote_products(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get quote products list."""
        path, params, extra_data = self._get_quote_products(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_quote_products(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get quote products list."""
        path, params, extra_data = self._get_quote_products(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_quote_products(
        self, products: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Set quote products."""
        request_type = "set_quote_products"
        path = self._params.get_rest_path(request_type)
        params = {
            "products": products if isinstance(products, str) else json.dumps(products)
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._set_quote_products_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _set_quote_products_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize set quote products response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def set_quote_products(
        self, products: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Set quote products."""
        path, params, extra_data = self._set_quote_products(
            products, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

