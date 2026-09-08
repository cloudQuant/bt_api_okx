"""
OKX API - AccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from typing import Any

from bt_api_base.functions.utils import update_extra_data

from bt_api_okx.containers.positions.okx_position import OkxPositionData


class AccountMixinPart2:
    """AccountMixinPart2 方法集合。"""

    def async_get_config(self, extra_data: Any = None) -> None:
        """async_get_config method"""
        path, params, extra_data = self._get_config(extra_data=extra_data)
        self.submit(
            self.async_request(path, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_position_mode(
        self,
        position_mode: str,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Build an account-wide OKX position-mode mutation request."""
        if position_mode not in {"net_mode", "long_short_mode"}:
            raise ValueError("position_mode must be net_mode or long_short_mode")
        request_type = "set_mode"
        body = {"posMode": position_mode}
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            request_type=request_type,
            symbol_name="ALL",
            asset_type=self.asset_type,
            exchange_name=self.exchange_name,
            normalize_function=None,
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    def set_position_mode(
        self,
        position_mode: str,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set OKX net or long/short mode for the account."""
        path, body, extra_data = self._set_position_mode(
            position_mode, extra_data, **kwargs
        )
        return self.request(path, body=body, extra_data=extra_data)

    def set_mode(
        self,
        position_mode: str = "long_short_mode",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Backward-compatible alias for set_position_mode."""
        return self.set_position_mode(position_mode, extra_data, **kwargs)

    def async_set_position_mode(
        self,
        position_mode: str,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Schedule an account-wide OKX position-mode mutation."""
        path, body, extra_data = self._set_position_mode(
            position_mode, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )

    def set_lever(self, symbol: Any, lever: Any = 10, mgn_mode: Any = "cross") -> Any:
        """set_lever method"""
        symbol = self._params.get_symbol(symbol)
        params = {"instId": symbol, "lever": lever, "mgnMode": mgn_mode}
        path = self._params.get_rest_path("set_lever")
        data = self.request(path, body=params)
        return data

    def async_set_lever(
        self,
        symbol: Any,
        lever: Any = 10,
        mgn_mode: Any = "cross",
        extra_data: Any = None,
    ) -> None:
        """async_set_lever method"""
        symbol = self._params.get_symbol(symbol)
        params = {"instId": symbol, "lever": lever, "mgnMode": mgn_mode}
        path = self._params.get_rest_path("set_lever")
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_fee(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        qty: Any = None,
        extra_data: Any = None,
        inst_family: Any = None,
        group_id: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get fee rate
        :param inst_type: Instrument type, e.g. SPOT, MARGIN, SWAP, FUTURES, OPTION
        :param uly: Legacy alias for inst_family, e.g. BTC-USD
        :param inst_id: Instrument ID, only applicable to SPOT/MARGIN
        :param ccy: Currency
        :param qty: Order size
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param inst_family: Instrument family, applicable to derivatives
        :param group_id: Instrument trading fee group ID
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_fee"
        normalized_inst_type = str(inst_type).strip().upper()
        if normalized_inst_type == "FUTURE":
            normalized_inst_type = "FUTURES"
        spot_types = {"SPOT", "MARGIN"}
        derivative_types = {"SWAP", "FUTURES", "OPTION"}
        if normalized_inst_type not in spot_types | derivative_types:
            raise ValueError("unsupported_fee_instrument_type")

        legacy_family = (
            str(uly).strip().replace("/", "-").upper()
            if uly not in (None, "")
            else None
        )
        explicit_family = (
            str(inst_family).strip().replace("/", "-").upper()
            if inst_family not in (None, "")
            else None
        )
        if legacy_family and explicit_family and legacy_family != explicit_family:
            raise ValueError("conflicting_instrument_family")
        requested_family = explicit_family or legacy_family
        requested_group = str(group_id).strip() if group_id not in (None, "") else None
        requested_inst_id = str(inst_id).strip() if inst_id not in (None, "") else None
        if requested_group and (requested_inst_id or requested_family):
            raise ValueError("group_id_is_mutually_exclusive")
        if requested_inst_id and normalized_inst_type not in spot_types:
            normalized_legacy_id = requested_inst_id.replace("/", "-").upper()
            if normalized_inst_type == "SWAP" and normalized_legacy_id.endswith(
                "-SWAP"
            ):
                requested_family = normalized_legacy_id[: -len("-SWAP")]
                requested_inst_id = None
            else:
                raise ValueError("inst_id_only_applicable_to_spot_margin")
        if requested_family and normalized_inst_type not in derivative_types:
            raise ValueError("inst_family_only_applicable_to_derivatives")

        params = {"instType": normalized_inst_type}
        if requested_inst_id:
            params["instId"] = self._params.get_symbol(requested_inst_id)
        if requested_family:
            params["instFamily"] = requested_family
        if requested_group:
            params["groupId"] = requested_group
        if ccy:
            params["ccy"] = ccy
        if qty:
            params["qty"] = qty
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": requested_inst_id or requested_family or "ALL",
                "asset_type": normalized_inst_type,
                "exchange_name": self.exchange_name,
                "normalize_function": self._get_fee_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_fee_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize fee data"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        # Fee rows are account-rate metadata, not positions. Returning the
        # native mappings preserves maker/taker and currency fields for the
        # public typed FeeSchedule normalizer.
        data = input_data["data"]
        return list(data) if isinstance(data, list) else [data], status

    def get_fee(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        qty: Any = None,
        extra_data: Any = None,
        inst_family: Any = None,
        group_id: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get fee rate"""
        path, params, extra_data = self._get_fee(
            inst_type,
            uly,
            inst_id,
            ccy,
            qty,
            extra_data,
            inst_family,
            group_id,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_fee(
        self,
        inst_type: Any,
        uly: Any = None,
        inst_id: Any = None,
        ccy: Any = None,
        qty: Any = None,
        extra_data: Any = None,
        inst_family: Any = None,
        group_id: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get fee rate"""
        path, params, extra_data = self._get_fee(
            inst_type,
            uly,
            inst_id,
            ccy,
            qty,
            extra_data,
            inst_family,
            group_id,
            **kwargs,
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_max_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get maximum open position size
        :param symbol: Instrument ID, e.g. BTC-USDT
        :param td_mode: Trade mode, cross or isolated
        :param ccy: Currency (for isolated margin mode)
        :param px: Order price
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_max_size"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "tdMode": td_mode,
        }
        if ccy:
            params["ccy"] = ccy
        if px:
            params["px"] = px
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": self._get_max_size_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_max_size_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize max size data"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxPositionData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_max_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get maximum open position size"""
        path, params, extra_data = self._get_max_size(
            symbol, td_mode, ccy, px, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_max_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get maximum open position size"""
        path, params, extra_data = self._get_max_size(
            symbol, td_mode, ccy, px, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_max_avail_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Get maximum available open position size
        :param symbol: Instrument ID, e.g. BTC-USDT
        :param td_mode: Trade mode, cross or isolated
        :param ccy: Currency (for isolated margin mode)
        :param px: Order price
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, params, extra_data
        """
        request_type = "get_max_avail_size"
        request_symbol = self._params.get_symbol(symbol)
        params = {
            "instId": request_symbol,
            "tdMode": td_mode,
        }
        if ccy:
            params["ccy"] = ccy
        if px:
            params["px"] = px
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": self._get_max_avail_size_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _get_max_avail_size_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize max avail size data"""
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxPositionData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def get_max_avail_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get maximum available open position size"""
        path, params, extra_data = self._get_max_avail_size(
            symbol, td_mode, ccy, px, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_max_avail_size(
        self,
        symbol: Any,
        td_mode: Any,
        ccy: Any = None,
        px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get maximum available open position size"""
        path, params, extra_data = self._get_max_avail_size(
            symbol, td_mode, ccy, px, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _set_margin_balance(
        self,
        symbol: Any,
        pos_id: Any,
        amt: Any,
        mgn_mode: Any,
        action_type: Any = "add",
        pos_side: Any = "net",
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Set margin balance (add/reduce margin)
        :param symbol: Instrument ID, e.g. BTC-USDT
        :param pos_id: Position ID
        :param amt: Amount to add/reduce
        :param mgn_mode: Margin mode, cross or isolated
        :param action_type: add or reduce, default is add
        :param pos_side: Position side, long/short/net, default is net
        :param ccy: Currency (for isolated margin mode)
        :param extra_data: extra_data, default is None, can be a dict passed by user
        :param kwargs: pass key-worded, variable-length arguments.
        :return: path, body, extra_data
        """
        request_type = "set_margin_balance"
        request_symbol = self._params.get_symbol(symbol)
        body = {
            "instId": request_symbol,
            "posSide": pos_side,
            "type": action_type,
            "posId": pos_id,
            "amt": str(amt),
            "mgnMode": mgn_mode,
        }
        if ccy:
            body["ccy"] = ccy
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": self._generic_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, body, extra_data

    def set_margin_balance(
        self,
        symbol: Any,
        pos_id: Any,
        amt: Any,
        mgn_mode: Any,
        action_type: Any = "add",
        pos_side: Any = "net",
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Set margin balance (add/reduce margin)"""
        path, body, extra_data = self._set_margin_balance(
            symbol,
            pos_id,
            amt,
            mgn_mode,
            action_type,
            pos_side,
            ccy,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=body, extra_data=extra_data)
        return data

    def async_set_margin_balance(
        self,
        symbol: Any,
        pos_id: Any,
        amt: Any,
        mgn_mode: Any,
        action_type: Any = "add",
        pos_side: Any = "net",
        ccy: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async set margin balance (add/reduce margin)"""
        path, body, extra_data = self._set_margin_balance(
            symbol,
            pos_id,
            amt,
            mgn_mode,
            action_type,
            pos_side,
            ccy,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=body, extra_data=extra_data),
            callback=self.async_callback,
        )
