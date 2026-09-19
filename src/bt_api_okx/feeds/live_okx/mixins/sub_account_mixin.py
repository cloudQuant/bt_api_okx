"""
OKX API - SubAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_okx.feeds.live_okx.mixins.rest_call_mixin import RestCallMixin


class SubAccountMixin(RestCallMixin):
    """Mixin providing OKX API methods.

    Expects host class to provide: _params, asset_type, exchange_name,
    request, submit, async_request, async_callback.
    """

    # Declare for mypy; host class provides these
    _params: Any
    asset_type: str
    exchange_name: str
    request: Callable[..., Any]
    submit: Callable[..., Any]
    async_request: Callable[..., Any]
    async_callback: Callable[..., Any]

    # ==================== Missing Sub-account APIs ====================

    def _get_sub_account_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get sub account list"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_sub_account_list",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_sub_account_list(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get sub account list"""
        return self._rest("get_sub_account_list", extra_data, **kwargs)

    def async_get_sub_account_list(self, extra_data: Any = None, **kwargs: Any) -> None:
        """Async get sub account list"""
        return self._rest_async("get_sub_account_list", extra_data, **kwargs)

    def _create_sub_account(
        self, sub_acct: Any, tag: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create sub account"""
        params: dict[str, Any] = {"subAcct": sub_acct}
        if tag:
            params["tag"] = tag
        return self._finish(
            "create_sub_account",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def create_sub_account(
        self, sub_acct: Any, tag: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Create sub account"""
        path, params, extra_data = self._create_sub_account(
            sub_acct, tag, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_create_sub_account(
        self, sub_acct: Any, tag: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async create sub account"""
        path, params, extra_data = self._create_sub_account(
            sub_acct, tag, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _create_sub_account_api_key(
        self,
        sub_acct: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Create sub account API key"""
        params: dict[str, Any] = {
            "subAcct": sub_acct,
        }
        if label:
            params["label"] = label
        if ip:
            params["ip"] = ip
        if perm:
            params["perm"] = perm
        return self._finish(
            "create_sub_account_api_key",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def create_sub_account_api_key(
        self,
        sub_acct: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Create sub account API key"""
        path, params, extra_data = self._create_sub_account_api_key(
            sub_acct, label, ip, perm, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_create_sub_account_api_key(
        self,
        sub_acct: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async create sub account API key"""
        path, params, extra_data = self._create_sub_account_api_key(
            sub_acct, label, ip, perm, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_sub_account_api_key(
        self, sub_acct: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get sub account API key"""
        params: dict[str, Any] = {"subAcct": sub_acct}
        return self._finish(
            "get_sub_account_api_key",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def get_sub_account_api_key(
        self, sub_acct: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get sub account API key"""
        return self._rest("get_sub_account_api_key", sub_acct, extra_data, **kwargs)

    def async_get_sub_account_api_key(
        self, sub_acct: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get sub account API key"""
        return self._rest_async("get_sub_account_api_key", sub_acct, extra_data, **kwargs)

    def _reset_sub_account_api_key(
        self,
        sub_acct: Any,
        api_key: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Reset sub account API key"""
        params: dict[str, Any] = {
            "subAcct": sub_acct,
            "apiKey": api_key,
        }
        if label:
            params["label"] = label
        if ip:
            params["ip"] = ip
        if perm:
            params["perm"] = perm
        return self._finish(
            "reset_sub_account_api_key",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def reset_sub_account_api_key(
        self,
        sub_acct: Any,
        api_key: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Reset sub account API key"""
        path, params, extra_data = self._reset_sub_account_api_key(
            sub_acct, api_key, label, ip, perm, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_reset_sub_account_api_key(
        self,
        sub_acct: Any,
        api_key: Any,
        label: Any = None,
        ip: Any = None,
        perm: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async reset sub account API key"""
        path, params, extra_data = self._reset_sub_account_api_key(
            sub_acct, api_key, label, ip, perm, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _delete_sub_account_api_key(
        self, sub_acct: Any, api_key: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Delete sub account API key"""
        params: dict[str, Any] = {
            "subAcct": sub_acct,
            "apiKey": api_key,
        }
        return self._finish(
            "delete_sub_account_api_key",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def delete_sub_account_api_key(
        self, sub_acct: Any, api_key: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Delete sub account API key"""
        path, params, extra_data = self._delete_sub_account_api_key(
            sub_acct, api_key, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_delete_sub_account_api_key(
        self, sub_acct: Any, api_key: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async delete sub account API key"""
        path, params, extra_data = self._delete_sub_account_api_key(
            sub_acct, api_key, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_sub_account_funding_balance(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get sub account funding balance"""
        params: dict[str, Any] = {"subAcct": sub_acct}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_sub_account_funding_balance",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def get_sub_account_funding_balance(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get sub account funding balance"""
        return self._rest("get_sub_account_funding_balance", sub_acct, ccy, extra_data, **kwargs)

    def async_get_sub_account_funding_balance(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get sub account funding balance"""
        return self._rest_async("get_sub_account_funding_balance", sub_acct, ccy, extra_data, **kwargs)

    def _get_sub_account_max_withdrawal(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get sub account max withdrawal"""
        params: dict[str, Any] = {"subAcct": sub_acct}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_sub_account_max_withdrawal",
            params,
            extra_data,
            sub_acct,
            generic_normalize_function,
            kwargs,
        )

    def get_sub_account_max_withdrawal(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get sub account max withdrawal"""
        return self._rest("get_sub_account_max_withdrawal", sub_acct, ccy, extra_data, **kwargs)

    def async_get_sub_account_max_withdrawal(
        self, sub_acct: Any, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get sub account max withdrawal"""
        return self._rest_async("get_sub_account_max_withdrawal", sub_acct, ccy, extra_data, **kwargs)

    # ==================== Sub-account (P2) - Remaining Interfaces ====================

    def _get_sub_account_transfer_history(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get sub-account transfer history"""
        params: dict[str, Any] = {}
        if sub_acct:
            params["subAcct"] = sub_acct
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_sub_account_transfer_history",
            params,
            extra_data,
            sub_acct or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_sub_account_transfer_history(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get sub-account transfer history"""
        return self._rest("get_sub_account_transfer_history", sub_acct, ccy, after, before, limit, extra_data, **kwargs)

    def async_get_sub_account_transfer_history(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get sub-account transfer history"""
        return self._rest_async("get_sub_account_transfer_history", sub_acct, ccy, after, before, limit, extra_data, **kwargs)

    def _get_managed_sub_account_bills(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get managed sub-account bills"""
        params: dict[str, Any] = {}
        if sub_acct:
            params["subAcct"] = sub_acct
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_managed_sub_account_bills",
            params,
            extra_data,
            sub_acct or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_managed_sub_account_bills(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get managed sub-account bills"""
        return self._rest("get_managed_sub_account_bills", sub_acct, ccy, after, before, limit, extra_data, **kwargs)

    def async_get_managed_sub_account_bills(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get managed sub-account bills"""
        return self._rest_async("get_managed_sub_account_bills", sub_acct, ccy, after, before, limit, extra_data, **kwargs)

    def _sub_account_transfer(
        self,
        ccy: Any,
        amount: Any,
        from_acct: Any,
        to_acct: Any,
        from_acc_type: Any = 6,
        to_acc_type: Any = 6,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Sub-account transfer"""
        params: dict[str, Any] = {
            "ccy": ccy,
            "amt": str(amount),
            "fromAcct": from_acct,
            "toAcct": to_acct,
            "type": "1",  # 1: master account transfer to sub-account, 2: sub-account transfer to master account
            "fromAccType": str(from_acc_type),  # 6: master account
            "toAccType": str(to_acc_type),  # 6: master account
        }
        return self._finish(
            "sub_account_transfer",
            params,
            extra_data,
            ccy,
            generic_normalize_function,
            kwargs,
        )

    def sub_account_transfer(
        self,
        ccy: Any,
        amount: Any,
        from_acct: Any,
        to_acct: Any,
        from_acc_type: Any = 6,
        to_acc_type: Any = 6,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Sub-account transfer"""
        path, params, extra_data = self._sub_account_transfer(
            ccy,
            amount,
            from_acct,
            to_acct,
            from_acc_type,
            to_acc_type,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_sub_account_transfer(
        self,
        ccy: Any,
        amount: Any,
        from_acct: Any,
        to_acct: Any,
        from_acc_type: Any = 6,
        to_acc_type: Any = 6,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async sub-account transfer"""
        path, params, extra_data = self._sub_account_transfer(
            ccy,
            amount,
            from_acct,
            to_acct,
            from_acc_type,
            to_acc_type,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_sub_account_transfer_out(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        allow: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Set sub-account transfer out permission"""
        params: dict[str, Any] = {
            "subAcct": sub_acct or "",
            "ccy": ccy or "",
            "allow": "true" if allow else "false",
        }
        return self._finish(
            "set_sub_account_transfer_out",
            params,
            extra_data,
            sub_acct or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def set_sub_account_transfer_out(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        allow: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set sub-account transfer out permission"""
        path, params, extra_data = self._set_sub_account_transfer_out(
            sub_acct, ccy, allow, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_set_sub_account_transfer_out(
        self,
        sub_acct: Any = None,
        ccy: Any = None,
        allow: Any = False,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set sub-account transfer out permission"""
        path, params, extra_data = self._set_sub_account_transfer_out(
            sub_acct, ccy, allow, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_custody_sub_account_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get custody sub-account list"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_custody_sub_account_list",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_custody_sub_account_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get custody sub-account list"""
        return self._rest("get_custody_sub_account_list", extra_data, **kwargs)

    def async_get_custody_sub_account_list(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get custody sub-account list"""
        return self._rest_async("get_custody_sub_account_list", extra_data, **kwargs)
