"""
OKX API - FundingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


class FundingMixinPart1:
    """FundingMixinPart1 方法集合。"""

    def _get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get currencies"""
        request_type = "get_currencies"
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

    def get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get currencies"""
        path, params, extra_data = self._get_currencies(ccy, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get currencies"""
        path, params, extra_data = self._get_currencies(ccy, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset balances"""
        request_type = "get_asset_balances"
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

    def get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get asset balances"""
        path, params, extra_data = self._get_asset_balances(ccy, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get asset balances"""
        path, params, extra_data = self._get_asset_balances(ccy, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get non-tradable assets"""
        request_type = "get_non_tradable_assets"
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

    def get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get non-tradable assets"""
        path, params, extra_data = self._get_non_tradable_assets(
            ccy, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get non-tradable assets"""
        path, params, extra_data = self._get_non_tradable_assets(
            ccy, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset valuation"""
        request_type = "get_asset_valuation"
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

    def get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get asset valuation"""
        path, params, extra_data = self._get_asset_valuation(ccy, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get asset valuation"""
        path, params, extra_data = self._get_asset_valuation(ccy, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _transfer(
        self,
        ccy: Any,
        amt: Any,
        from_acct: Any = None,
        to_acct: Any = None,
        type: Any = None,
        client_bill_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Asset transfer"""
        request_type = "transfer"
        params = {
            "ccy": ccy,
            "amt": str(amt),
        }
        if from_acct:
            params["from"] = from_acct
        if to_acct:
            params["to"] = to_acct
        if type:
            params["type"] = type
        if client_bill_id:
            params["clientBillId"] = client_bill_id
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

    def transfer(
        self,
        ccy: Any,
        amt: Any,
        from_acct: Any = None,
        to_acct: Any = None,
        type: Any = None,
        client_bill_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Asset transfer"""
        path, params, extra_data = self._transfer(
            ccy, amt, from_acct, to_acct, type, client_bill_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_transfer(
        self,
        ccy: Any,
        amt: Any,
        from_acct: Any = None,
        to_acct: Any = None,
        type: Any = None,
        client_bill_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async asset transfer"""
        path, params, extra_data = self._transfer(
            ccy, amt, from_acct, to_acct, type, client_bill_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_transfer_state(
        self,
        transfer_id: Any = None,
        client_bill_id: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get transfer state"""
        request_type = "get_transfer_state"
        params: dict[str, Any] = {}
        if transfer_id:
            params["transId"] = transfer_id
        if client_bill_id:
            params["clientBillId"] = client_bill_id
        if type:
            params["type"] = type
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

    def get_transfer_state(
        self,
        transfer_id: Any = None,
        client_bill_id: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get transfer state"""
        path, params, extra_data = self._get_transfer_state(
            transfer_id, client_bill_id, type, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_transfer_state(
        self,
        transfer_id: Any = None,
        client_bill_id: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get transfer state"""
        path, params, extra_data = self._get_transfer_state(
            transfer_id, client_bill_id, type, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_asset_bills(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset bills"""
        request_type = "get_asset_bills"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if type:
            params["type"] = type
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

    def get_asset_bills(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get asset bills"""
        path, params, extra_data = self._get_asset_bills(
            ccy, type, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_asset_bills(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get asset bills"""
        path, params, extra_data = self._get_asset_bills(
            ccy, type, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_asset_bills_history(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset bills history"""
        request_type = "get_asset_bills_history"
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if type:
            params["type"] = type
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

    def get_asset_bills_history(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get asset bills history"""
        path, params, extra_data = self._get_asset_bills_history(
            ccy, type, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_asset_bills_history(
        self,
        ccy: Any = None,
        type: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get asset bills history"""
        path, params, extra_data = self._get_asset_bills_history(
            ccy, type, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit address"""
        request_type = "get_deposit_address"
        params = {"ccy": ccy}
        if to:
            params["to"] = to
        if chain:
            params["chain"] = chain
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

    def get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get deposit address"""
        path, params, extra_data = self._get_deposit_address(
            ccy, to, chain, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get deposit address"""
        path, params, extra_data = self._get_deposit_address(
            ccy, to, chain, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit history"""
        request_type = "get_deposit_history"
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

    def get_deposit_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get deposit history"""
        path, params, extra_data = self._get_deposit_history(
            ccy, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_history(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get deposit history"""
        path, params, extra_data = self._get_deposit_history(
            ccy, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_deposit_withdraw_status(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit withdraw status"""
        request_type = "get_deposit_withdraw_status"
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

    def get_deposit_withdraw_status(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get deposit withdraw status"""
        path, params, extra_data = self._get_deposit_withdraw_status(
            ccy, after, before, limit, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deposit_withdraw_status(
        self,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get deposit withdraw status"""
        path, params, extra_data = self._get_deposit_withdraw_status(
            ccy, after, before, limit, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _withdrawal(
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
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Withdrawal"""
        request_type = "withdrawal"
        params = {
            "ccy": ccy,
            "amt": str(amt),
            "dest": dest,
            "toAddr": to_addr,
        }
        if fee is not None:
            params["fee"] = str(fee)
        if chain:
            params["chain"] = chain
        if area_code:
            params["areaCode"] = area_code
        if client_chain_id:
            params["clientChainId"] = client_chain_id
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

    def withdrawal(
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
    ) -> Any:
        """Withdrawal"""
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
        data = self.request(path, body=params, extra_data=extra_data)
        return data

