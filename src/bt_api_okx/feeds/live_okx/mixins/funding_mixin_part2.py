"""
OKX API - FundingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class FundingMixinPart2:
    """FundingMixinPart2 方法集合。"""

    def async_withdrawal(
        self,
        ccy: Any,
        amt: Any,
        dest: Any,
        to_addr: Any,
        fee: Any = None,
        chain: Any = None,
        area_code: Any = None,
        client_chain_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async withdrawal"""
        path, params, extra_data = self._withdrawal(
            ccy,
            amt,
            dest,
            to_addr,
            fee,
            chain,
            area_code,
            client_chain_id,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_withdrawal(
        self, wd_id: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel withdrawal"""
        request_type = "cancel_withdrawal"
        params = {"wdId": wd_id}
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def cancel_withdrawal(
        self, wd_id: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel withdrawal"""
        path, params, extra_data = self._cancel_withdrawal(
            wd_id, ccy, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_withdrawal(
        self, wd_id: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel withdrawal"""
        path, params, extra_data = self._cancel_withdrawal(
            wd_id, ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_withdrawal_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal history"""
        request_type = "get_withdrawal_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
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
                "symbol_name": ccy or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_withdrawal_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get withdrawal history"""
        path, params, extra_data = self._get_withdrawal_history(
            ccy, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_withdrawal_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get withdrawal history"""
        path, params, extra_data = self._get_withdrawal_history(
            ccy, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Funding Account (P2) - Remaining Interfaces ====================

    def _get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get exchange list"""
        request_type = "get_exchange_list"
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get exchange list"""
        path, params, extra_data = self._get_exchange_list(ccy, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get exchange list"""
        path, params, extra_data = self._get_exchange_list(ccy, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _apply_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Apply for monthly statement (last year)"""
        request_type = "apply_monthly_statement"
        params: dict[str, Any] = {}
        if month:
            params["month"] = month
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def apply_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Apply for monthly statement (last year)"""
        path, params, extra_data = self._apply_monthly_statement(
            month, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_apply_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async apply for monthly statement (last year)"""
        path, params, extra_data = self._apply_monthly_statement(
            month, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get monthly statement (last year)"""
        request_type = "get_monthly_statement"
        params: dict[str, Any] = {}
        if month:
            params["month"] = month
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get monthly statement (last year)"""
        path, params, extra_data = self._get_monthly_statement(
            month, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get monthly statement (last year)"""
        path, params, extra_data = self._get_monthly_statement(
            month, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_convert_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get convert currencies list"""
        request_type = "get_convert_currencies"
        params: dict[str, Any] = {}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_convert_currencies(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get convert currencies list"""
        path, params, extra_data = self._get_convert_currencies(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_convert_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get convert currencies list"""
        path, params, extra_data = self._get_convert_currencies(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get convert currency pair"""
        request_type = "get_convert_currency_pair"
        params: dict[str, Any] = {}
        if from_ccy:
            params["fromCcy"] = from_ccy
        if to_ccy:
            params["toCcy"] = to_ccy
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": f"{from_ccy or 'ALL'}-{to_ccy or 'ALL'}",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get convert currency pair"""
        path, params, extra_data = self._get_convert_currency_pair(
            from_ccy, to_ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get convert currency pair"""
        path, params, extra_data = self._get_convert_currency_pair(
            from_ccy, to_ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _convert_estimate_quote(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Convert estimate quote"""
        request_type = "convert_estimate_quote"
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
            "amount": str(amount),
            "type": type,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": f"{from_ccy}-{to_ccy}",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def convert_estimate_quote(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Convert estimate quote"""
        path, params, extra_data = self._convert_estimate_quote(
            from_ccy, to_ccy, amount, type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_convert_estimate_quote(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async convert estimate quote"""
        path, params, extra_data = self._convert_estimate_quote(
            from_ccy, to_ccy, amount, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _convert_trade(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Convert trade"""
        request_type = "convert_trade"
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
            "amount": str(amount),
            "type": type,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": f"{from_ccy}-{to_ccy}",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def convert_trade(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Convert trade"""
        path, params, extra_data = self._convert_trade(
            from_ccy, to_ccy, amount, type, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_convert_trade(
        self,
        from_ccy: Any,
        to_ccy: Any,
        amount: Any,
        type: Any = "buy",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async convert trade"""
        path, params, extra_data = self._convert_trade(
            from_ccy, to_ccy, amount, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get convert history"""
        request_type = "get_convert_history"
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get convert history"""
        path, params, extra_data = self._get_convert_history(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get convert history"""
        path, params, extra_data = self._get_convert_history(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit payment methods"""
        request_type = "get_deposit_payment_methods"
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get deposit payment methods"""
        path, params, extra_data = self._get_deposit_payment_methods(
            ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get deposit payment methods"""
        path, params, extra_data = self._get_deposit_payment_methods(
            ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal payment methods"""
        request_type = "get_withdrawal_payment_methods"
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
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

