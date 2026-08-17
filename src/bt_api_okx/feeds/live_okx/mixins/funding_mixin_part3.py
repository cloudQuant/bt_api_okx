"""
OKX API - FundingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class FundingMixinPart3:
    """FundingMixinPart3 方法集合。"""

    def get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get withdrawal payment methods"""
        path, params, extra_data = self._get_withdrawal_payment_methods(
            ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get withdrawal payment methods"""
        path, params, extra_data = self._get_withdrawal_payment_methods(
            ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _create_withdrawal_order(
        self,
        ccy: Any,
        amt: Any,
        dest: Any,
        to_addr: Any = None,
        pwd: Any = None,
        fee: Any = None,
        chain: Any = None,
        area_code: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create withdrawal order"""
        request_type = "create_withdrawal_order"
        params = {
            "ccy": ccy,
            "amt": str(amt),
            "dest": dest,
        }
        if to_addr:
            params["toAddr"] = to_addr
        if pwd:
            params["pwd"] = pwd
        if fee is not None:
            params["fee"] = str(fee)
        if chain:
            params["chain"] = chain
        if area_code:
            params["areaCode"] = area_code
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": ccy,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def create_withdrawal_order(
        self,
        ccy: Any,
        amt: Any,
        dest: Any,
        to_addr: Any = None,
        pwd: Any = None,
        fee: Any = None,
        chain: Any = None,
        area_code: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Create withdrawal order"""
        path, params, extra_data = self._create_withdrawal_order(
            ccy, amt, dest, to_addr, pwd, fee, chain, area_code, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_create_withdrawal_order(
        self,
        ccy: Any,
        amt: Any,
        dest: Any,
        to_addr: Any = None,
        pwd: Any = None,
        fee: Any = None,
        chain: Any = None,
        area_code: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async create withdrawal order"""
        path, params, extra_data = self._create_withdrawal_order(
            ccy, amt, dest, to_addr, pwd, fee, chain, area_code, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_withdrawal_order(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Cancel withdrawal order"""
        request_type = "cancel_withdrawal_order"
        params = {
            "wdId": wd_id,
        }
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

    def cancel_withdrawal_order(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Cancel withdrawal order"""
        path, params, extra_data = self._cancel_withdrawal_order(
            wd_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_withdrawal_order(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async cancel withdrawal order"""
        path, params, extra_data = self._cancel_withdrawal_order(
            wd_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_withdrawal_order_history(
        self,
        ccy: Any = None,
        wd_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal order history"""
        request_type = "get_withdrawal_order_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if wd_id:
            params["wdId"] = wd_id
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

    def get_withdrawal_order_history(
        self,
        ccy: Any = None,
        wd_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get withdrawal order history"""
        path, params, extra_data = self._get_withdrawal_order_history(
            ccy, wd_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_withdrawal_order_history(
        self,
        ccy: Any = None,
        wd_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get withdrawal order history"""
        path, params, extra_data = self._get_withdrawal_order_history(
            ccy, wd_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal order detail"""
        request_type = "get_withdrawal_order_detail"
        params = {
            "wdId": wd_id,
        }
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

    def get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get withdrawal order detail"""
        path, params, extra_data = self._get_withdrawal_order_detail(
            wd_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get withdrawal order detail"""
        path, params, extra_data = self._get_withdrawal_order_detail(
            wd_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_order_history(
        self,
        ccy: Any = None,
        dep_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit order history"""
        request_type = "get_deposit_order_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if dep_id:
            params["depId"] = dep_id
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

    def get_deposit_order_history(
        self,
        ccy: Any = None,
        dep_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get deposit order history"""
        path, params, extra_data = self._get_deposit_order_history(
            ccy, dep_id, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_order_history(
        self,
        ccy: Any = None,
        dep_id: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get deposit order history"""
        path, params, extra_data = self._get_deposit_order_history(
            ccy, dep_id, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit order detail"""
        request_type = "get_deposit_order_detail"
        params = {
            "depId": dep_id,
        }
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

    def get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get deposit order detail"""
        path, params, extra_data = self._get_deposit_order_detail(
            dep_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get deposit order detail"""
        path, params, extra_data = self._get_deposit_order_detail(
            dep_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_buy_sell_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell currencies list"""
        request_type = "get_buy_sell_currencies"
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

    def get_buy_sell_currencies(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get buy/sell currencies list"""
        path, params, extra_data = self._get_buy_sell_currencies(extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_buy_sell_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get buy/sell currencies list"""
        path, params, extra_data = self._get_buy_sell_currencies(extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_buy_sell_currency_pair(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell currency pair"""
        request_type = "get_buy_sell_currency_pair"
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

    def get_buy_sell_currency_pair(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get buy/sell currency pair"""
        path, params, extra_data = self._get_buy_sell_currency_pair(
            extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_buy_sell_currency_pair(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get buy/sell currency pair"""
        path, params, extra_data = self._get_buy_sell_currency_pair(
            extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_buy_sell_quote(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell quote"""
        request_type = "get_buy_sell_quote"
        params = {
            "side": side,
            "quoteCcy": quote_ccy,
            "baseCcy": base_ccy,
        }
        if amount is not None:
            params["amount"] = str(amount)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": f"{base_ccy}-{quote_ccy}",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_buy_sell_quote(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get buy/sell quote"""
        path, params, extra_data = self._get_buy_sell_quote(
            side, quote_ccy, base_ccy, amount, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_buy_sell_quote(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get buy/sell quote"""
        path, params, extra_data = self._get_buy_sell_quote(
            side, quote_ccy, base_ccy, amount, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _buy_sell_trade(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any,
        quote_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Buy/sell trade"""
        request_type = "buy_sell_trade"
        params = {
            "side": side,
            "quoteCcy": quote_ccy,
            "baseCcy": base_ccy,
            "amount": str(amount),
        }
        if quote_id:
            params["quoteId"] = quote_id
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": f"{base_ccy}-{quote_ccy}",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def buy_sell_trade(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any,
        quote_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Buy/sell trade"""
        path, params, extra_data = self._buy_sell_trade(
            side, quote_ccy, base_ccy, amount, quote_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_buy_sell_trade(
        self,
        side: Any,
        quote_ccy: Any,
        base_ccy: Any,
        amount: Any,
        quote_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async buy/sell trade"""
        path, params, extra_data = self._buy_sell_trade(
            side, quote_ccy, base_ccy, amount, quote_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_buy_sell_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell history"""
        request_type = "get_buy_sell_history"
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

    def get_buy_sell_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get buy/sell history"""
        path, params, extra_data = self._get_buy_sell_history(
            after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_buy_sell_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get buy/sell history"""
        path, params, extra_data = self._get_buy_sell_history(
            after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

