"""OKX API - RfqMixin
Auto-generated from request_base.py.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


class RfqMixinPart2:
    """RfqMixinPart2 方法集合。"""

    def async_set_quote_products(
        self, products: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async set quote products."""
        path, params, extra_data = self._set_quote_products(
            products, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _rfq_mmp_reset(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Reset MMP status for RFQ."""
        request_type = "rfq_mmp_reset"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id}
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._rfq_mmp_reset_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _rfq_mmp_reset_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize RFQ MMP reset response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def rfq_mmp_reset(self, inst_id: Any, extra_data: Any = None, **kwargs: Any) -> Any:
        """Reset MMP status for RFQ."""
        path, params, extra_data = self._rfq_mmp_reset(inst_id, extra_data, **kwargs)
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_rfq_mmp_reset(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async reset MMP status for RFQ."""
        path, params, extra_data = self._rfq_mmp_reset(inst_id, extra_data, **kwargs)
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _rfq_mmp_config(
        self,
        inst_id: Any,
        mode: Any,
        tier: Any,
        quote_limit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Set MMP for RFQ."""
        request_type = "rfq_mmp_config"
        path = self._params.get_rest_path(request_type)
        params = {
            "instId": inst_id,
            "mode": mode,
            "tier": str(tier),
            "quoteLimit": str(quote_limit),
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._rfq_mmp_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _rfq_mmp_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize RFQ MMP config response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def rfq_mmp_config(
        self,
        inst_id: Any,
        mode: Any,
        tier: Any,
        quote_limit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set MMP for RFQ."""
        path, params, extra_data = self._rfq_mmp_config(
            inst_id, mode, tier, quote_limit, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_rfq_mmp_config(
        self,
        inst_id: Any,
        mode: Any,
        tier: Any,
        quote_limit: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set MMP for RFQ."""
        path, params, extra_data = self._rfq_mmp_config(
            inst_id, mode, tier, quote_limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_rfq_mmp_config(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get MMP configuration for RFQ."""
        request_type = "get_rfq_mmp_config"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id}
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._get_rfq_mmp_config_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_rfq_mmp_config_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize get RFQ MMP config response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def get_rfq_mmp_config(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get MMP configuration for RFQ."""
        path, params, extra_data = self._get_rfq_mmp_config(
            inst_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_rfq_mmp_config(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get MMP configuration for RFQ."""
        path, params, extra_data = self._get_rfq_mmp_config(
            inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _create_quote(
        self,
        inst_id: Any,
        side: Any,
        px: Any,
        sz: Any,
        cl_ord_id: Any,
        tif: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create RFQ quote."""
        request_type = "create_quote"
        path = self._params.get_rest_path(request_type)
        params = {
            "instId": inst_id,
            "side": side,
            "px": str(px),
            "sz": str(sz),
            "clOrdId": cl_ord_id,
            "tif": tif,
        }
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._create_quote_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _create_quote_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize create quote response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def create_quote(
        self,
        inst_id: Any,
        side: Any,
        px: Any,
        sz: Any,
        cl_ord_id: Any,
        tif: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Create RFQ quote."""
        path, params, extra_data = self._create_quote(
            inst_id, side, px, sz, cl_ord_id, tif, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_create_quote(
        self,
        inst_id: Any,
        side: Any,
        px: Any,
        sz: Any,
        cl_ord_id: Any,
        tif: Any,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async create RFQ quote."""
        path, params, extra_data = self._create_quote(
            inst_id, side, px, sz, cl_ord_id, tif, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_quote(
        self,
        inst_id: Any,
        quote_id: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel RFQ quote."""
        request_type = "cancel_quote"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id, "quoteId": quote_id}
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_quote_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_quote_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel quote response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_quote(
        self,
        inst_id: Any,
        quote_id: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Cancel RFQ quote."""
        path, params, extra_data = self._cancel_quote(
            inst_id, quote_id, cl_ord_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_quote(
        self,
        inst_id: Any,
        quote_id: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async cancel RFQ quote."""
        path, params, extra_data = self._cancel_quote(
            inst_id, quote_id, cl_ord_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_multiple_quotes(
        self,
        inst_id: Any,
        quote_ids: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel multiple RFQ quotes."""
        request_type = "cancel_multiple_quotes"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id}
        if isinstance(quote_ids, list):
            params["quoteIds"] = ",".join(quote_ids)
        else:
            params["quoteIds"] = quote_ids
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_multiple_quotes_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_multiple_quotes_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel multiple quotes response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_multiple_quotes(
        self,
        inst_id: Any,
        quote_ids: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Cancel multiple RFQ quotes."""
        path, params, extra_data = self._cancel_multiple_quotes(
            inst_id, quote_ids, cl_ord_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_multiple_quotes(
        self,
        inst_id: Any,
        quote_ids: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async cancel multiple RFQ quotes."""
        path, params, extra_data = self._cancel_multiple_quotes(
            inst_id, quote_ids, cl_ord_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_all_quotes(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel all RFQ quotes."""
        request_type = "cancel_all_quotes"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id}
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._cancel_all_quotes_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _cancel_all_quotes_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize cancel all quotes response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

    def cancel_all_quotes(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel all RFQ quotes."""
        path, params, extra_data = self._cancel_all_quotes(
            inst_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_all_quotes(
        self, inst_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel all RFQ quotes."""
        path, params, extra_data = self._cancel_all_quotes(
            inst_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _rfq_cancel_all_after(
        self,
        inst_id: Any,
        cancel_after: Any,
        cl_ord_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Set timer to cancel all RFQ quotes."""
        request_type = "rfq_cancel_all_after"
        path = self._params.get_rest_path(request_type)
        params = {"instId": inst_id, "cancelAfter": str(cancel_after)}
        if cl_ord_id:
            params["clOrdId"] = cl_ord_id
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": inst_id,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": RfqMixin._rfq_cancel_all_after_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _rfq_cancel_all_after_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize RFQ cancel all after response."""
        status = input_data.get("code") == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        target_data = data if len(data) > 0 else []
        return target_data, status

