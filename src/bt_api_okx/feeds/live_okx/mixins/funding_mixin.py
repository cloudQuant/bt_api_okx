"""
OKX API - FundingMixin

由机械切分的 ``*_partN`` 模块合并而来（迭代07 结构治理）。
"""

from __future__ import annotations

from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_okx.feeds.live_okx.mixins.rest_call_mixin import RestCallMixin


class FundingMixin(RestCallMixin):
    """FundingMixin 方法集合（OKX REST 端点）。"""
    def _get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get currencies"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_currencies",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get currencies"""
        return self._rest("get_currencies", ccy, extra_data, **kwargs)

    def async_get_currencies(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get currencies"""
        return self._rest_async("get_currencies", ccy, extra_data, **kwargs)

    def _get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset balances"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_asset_balances",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get asset balances"""
        return self._rest("get_asset_balances", ccy, extra_data, **kwargs)

    def async_get_asset_balances(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get asset balances"""
        return self._rest_async("get_asset_balances", ccy, extra_data, **kwargs)

    def _get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get non-tradable assets"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_non_tradable_assets",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get non-tradable assets"""
        return self._rest("get_non_tradable_assets", ccy, extra_data, **kwargs)

    def async_get_non_tradable_assets(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get non-tradable assets"""
        return self._rest_async("get_non_tradable_assets", ccy, extra_data, **kwargs)

    def _get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get asset valuation"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_asset_valuation",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get asset valuation"""
        return self._rest("get_asset_valuation", ccy, extra_data, **kwargs)

    def async_get_asset_valuation(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get asset valuation"""
        return self._rest_async("get_asset_valuation", ccy, extra_data, **kwargs)

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
        return self._finish(
            "transfer",
            params,
            extra_data,
            ccy,
            generic_normalize_function,
            kwargs,
        )

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
        params: dict[str, Any] = {}
        if transfer_id:
            params["transId"] = transfer_id
        if client_bill_id:
            params["clientBillId"] = client_bill_id
        if type:
            params["type"] = type
        return self._finish(
            "get_transfer_state",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_transfer_state(
        self,
        transfer_id: Any = None,
        client_bill_id: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get transfer state"""
        return self._rest("get_transfer_state", transfer_id, client_bill_id, type, extra_data, **kwargs)

    def async_get_transfer_state(
        self,
        transfer_id: Any = None,
        client_bill_id: Any = None,
        type: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get transfer state"""
        return self._rest_async("get_transfer_state", transfer_id, client_bill_id, type, extra_data, **kwargs)

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
        return self._finish(
            "get_asset_bills",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_asset_bills", ccy, type, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_asset_bills", ccy, type, after, before, limit, extra_data, **kwargs)

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
        return self._finish(
            "get_asset_bills_history",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_asset_bills_history", ccy, type, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_asset_bills_history", ccy, type, after, before, limit, extra_data, **kwargs)

    def _get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit address"""
        params = {"ccy": ccy}
        if to:
            params["to"] = to
        if chain:
            params["chain"] = chain
        return self._finish(
            "get_deposit_address",
            params,
            extra_data,
            ccy,
            generic_normalize_function,
            kwargs,
        )

    def get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get deposit address"""
        return self._rest("get_deposit_address", ccy, to, chain, extra_data, **kwargs)

    def async_get_deposit_address(
        self,
        ccy: Any,
        to: Any = None,
        chain: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get deposit address"""
        return self._rest_async("get_deposit_address", ccy, to, chain, extra_data, **kwargs)

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
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_deposit_history",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_deposit_history", ccy, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_deposit_history", ccy, after, before, limit, extra_data, **kwargs)

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
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_deposit_withdraw_status",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_deposit_withdraw_status", ccy, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_deposit_withdraw_status", ccy, after, before, limit, extra_data, **kwargs)

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
        return self._finish(
            "withdrawal",
            params,
            extra_data,
            ccy,
            generic_normalize_function,
            kwargs,
        )

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
        params = {"wdId": wd_id}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "cancel_withdrawal",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_withdrawal_history",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_withdrawal_history", ccy, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_withdrawal_history", ccy, after, before, limit, extra_data, **kwargs)

    def _get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get exchange list"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_exchange_list",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get exchange list"""
        return self._rest("get_exchange_list", ccy, extra_data, **kwargs)

    def async_get_exchange_list(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get exchange list"""
        return self._rest_async("get_exchange_list", ccy, extra_data, **kwargs)

    def _apply_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Apply for monthly statement (last year)"""
        params: dict[str, Any] = {}
        if month:
            params["month"] = month
        return self._finish(
            "apply_monthly_statement",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        params: dict[str, Any] = {}
        if month:
            params["month"] = month
        return self._finish(
            "get_monthly_statement",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get monthly statement (last year)"""
        return self._rest("get_monthly_statement", month, extra_data, **kwargs)

    def async_get_monthly_statement(
        self, month: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get monthly statement (last year)"""
        return self._rest_async("get_monthly_statement", month, extra_data, **kwargs)

    def _get_convert_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get convert currencies list"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_convert_currencies",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_convert_currencies(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get convert currencies list"""
        return self._rest("get_convert_currencies", extra_data, **kwargs)

    def async_get_convert_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get convert currencies list"""
        return self._rest_async("get_convert_currencies", extra_data, **kwargs)

    def _get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get convert currency pair"""
        params: dict[str, Any] = {}
        if from_ccy:
            params["fromCcy"] = from_ccy
        if to_ccy:
            params["toCcy"] = to_ccy
        return self._finish(
            "get_convert_currency_pair",
            params,
            extra_data,
            f"{from_ccy or 'ALL'}-{to_ccy or 'ALL'}",
            generic_normalize_function,
            kwargs,
        )

    def get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get convert currency pair"""
        return self._rest("get_convert_currency_pair", from_ccy, to_ccy, extra_data, **kwargs)

    def async_get_convert_currency_pair(
        self,
        from_ccy: Any = None,
        to_ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get convert currency pair"""
        return self._rest_async("get_convert_currency_pair", from_ccy, to_ccy, extra_data, **kwargs)

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
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
            "amount": str(amount),
            "type": type,
        }
        return self._finish(
            "convert_estimate_quote",
            params,
            extra_data,
            f"{from_ccy}-{to_ccy}",
            generic_normalize_function,
            kwargs,
        )

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
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
            "amount": str(amount),
            "type": type,
        }
        return self._finish(
            "convert_trade",
            params,
            extra_data,
            f"{from_ccy}-{to_ccy}",
            generic_normalize_function,
            kwargs,
        )

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
        params: dict[str, Any] = {}
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_convert_history",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get convert history"""
        return self._rest("get_convert_history", after, before, limit, extra_data, **kwargs)

    def async_get_convert_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get convert history"""
        return self._rest_async("get_convert_history", after, before, limit, extra_data, **kwargs)

    def _get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit payment methods"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_deposit_payment_methods",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get deposit payment methods"""
        return self._rest("get_deposit_payment_methods", ccy, extra_data, **kwargs)

    def async_get_deposit_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get deposit payment methods"""
        return self._rest_async("get_deposit_payment_methods", ccy, extra_data, **kwargs)

    def _get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal payment methods"""
        params: dict[str, Any] = {}
        if ccy:
            params["ccy"] = ccy
        return self._finish(
            "get_withdrawal_payment_methods",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get withdrawal payment methods"""
        return self._rest("get_withdrawal_payment_methods", ccy, extra_data, **kwargs)

    def async_get_withdrawal_payment_methods(
        self, ccy: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get withdrawal payment methods"""
        return self._rest_async("get_withdrawal_payment_methods", ccy, extra_data, **kwargs)

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
        return self._finish(
            "create_withdrawal_order",
            params,
            extra_data,
            ccy,
            generic_normalize_function,
            kwargs,
        )

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
        params = {
            "wdId": wd_id,
        }
        return self._finish(
            "cancel_withdrawal_order",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._finish(
            "get_withdrawal_order_history",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_withdrawal_order_history", ccy, wd_id, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_withdrawal_order_history", ccy, wd_id, after, before, limit, extra_data, **kwargs)

    def _get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get withdrawal order detail"""
        params = {
            "wdId": wd_id,
        }
        return self._finish(
            "get_withdrawal_order_detail",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get withdrawal order detail"""
        return self._rest("get_withdrawal_order_detail", wd_id, extra_data, **kwargs)

    def async_get_withdrawal_order_detail(
        self, wd_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get withdrawal order detail"""
        return self._rest_async("get_withdrawal_order_detail", wd_id, extra_data, **kwargs)

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
        return self._finish(
            "get_deposit_order_history",
            params,
            extra_data,
            ccy or "ALL",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_deposit_order_history", ccy, dep_id, after, before, limit, extra_data, **kwargs)

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
        return self._rest_async("get_deposit_order_history", ccy, dep_id, after, before, limit, extra_data, **kwargs)

    def _get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get deposit order detail"""
        params = {
            "depId": dep_id,
        }
        return self._finish(
            "get_deposit_order_detail",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get deposit order detail"""
        return self._rest("get_deposit_order_detail", dep_id, extra_data, **kwargs)

    def async_get_deposit_order_detail(
        self, dep_id: Any, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get deposit order detail"""
        return self._rest_async("get_deposit_order_detail", dep_id, extra_data, **kwargs)

    def _get_buy_sell_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell currencies list"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_buy_sell_currencies",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_buy_sell_currencies(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get buy/sell currencies list"""
        return self._rest("get_buy_sell_currencies", extra_data, **kwargs)

    def async_get_buy_sell_currencies(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get buy/sell currencies list"""
        return self._rest_async("get_buy_sell_currencies", extra_data, **kwargs)

    def _get_buy_sell_currency_pair(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get buy/sell currency pair"""
        params: dict[str, Any] = {}
        return self._finish(
            "get_buy_sell_currency_pair",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_buy_sell_currency_pair(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get buy/sell currency pair"""
        return self._rest("get_buy_sell_currency_pair", extra_data, **kwargs)

    def async_get_buy_sell_currency_pair(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get buy/sell currency pair"""
        return self._rest_async("get_buy_sell_currency_pair", extra_data, **kwargs)

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
        params = {
            "side": side,
            "quoteCcy": quote_ccy,
            "baseCcy": base_ccy,
        }
        if amount is not None:
            params["amount"] = str(amount)
        return self._finish(
            "get_buy_sell_quote",
            params,
            extra_data,
            f"{base_ccy}-{quote_ccy}",
            generic_normalize_function,
            kwargs,
        )

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
        return self._rest("get_buy_sell_quote", side, quote_ccy, base_ccy, amount, extra_data, **kwargs)

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
        return self._rest_async("get_buy_sell_quote", side, quote_ccy, base_ccy, amount, extra_data, **kwargs)

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
        params = {
            "side": side,
            "quoteCcy": quote_ccy,
            "baseCcy": base_ccy,
            "amount": str(amount),
        }
        if quote_id:
            params["quoteId"] = quote_id
        return self._finish(
            "buy_sell_trade",
            params,
            extra_data,
            f"{base_ccy}-{quote_ccy}",
            generic_normalize_function,
            kwargs,
        )

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
        params: dict[str, Any] = {}
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return self._finish(
            "get_buy_sell_history",
            params,
            extra_data,
            "ALL",
            generic_normalize_function,
            kwargs,
        )

    def get_buy_sell_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get buy/sell history"""
        return self._rest("get_buy_sell_history", after, before, limit, extra_data, **kwargs)

    def async_get_buy_sell_history(
        self,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get buy/sell history"""
        return self._rest_async("get_buy_sell_history", after, before, limit, extra_data, **kwargs)

