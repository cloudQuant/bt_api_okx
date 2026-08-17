"""
OKX API - TradeMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.orders.okx_order import OkxOrderData
from bt_api_okx.containers.trades.okx_trade import OkxRequestTradeData
from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.algo_mixin import AlgoMixin
from bt_api_okx.feeds.live_okx.mixins.batch_mixin import BatchMixin
from bt_api_okx.feeds.live_okx.mixins.convert_mixin import ConvertMixin
from bt_api_okx.feeds.live_okx.mixins.misc_trade_mixin import MiscTradeMixin
from bt_api_okx.feeds.live_okx.mixins.index_candles_mixin import IndexCandlesMixin


class TradeMixin(IndexCandlesMixin, AlgoMixin, BatchMixin, ConvertMixin, MiscTradeMixin):
    """Mixin providing OKX API methods."""

    _params: Any
    asset_type: str
    exchange_name: str
    request: Callable[..., Any]
    submit: Callable[..., Any]
    async_request: Callable[..., Any]
    async_callback: Callable[..., Any]
    request_logger: Any

    # ==================== Trade APIs ====================

    def _make_order(
        self,
        symbol: Any,
        vol: Any,
        price: Any = None,
        order_type: Any = "buy-limit",
        offset: Any = "open",
        post_only: Any = False,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_symbol = self._params.get_symbol(symbol)
        request_type = "make_order"
        if not kwargs.get("size_in_contracts") and not kwargs.get("skip_size_conversion"):
            try:
                vol = round(vol * self._params.symbol_leverage_dict[symbol])
            except Exception as e:
                self.request_logger.warning(f"_make_order:{e}")
        side, ord_type = order_type.split("-")
        if post_only:
            ord_type = "post_only"
        asset_type = str(getattr(self, "asset_type", "") or "").strip().upper()
        td_mode = kwargs.get("td_mode") or kwargs.get("tdMode")
        if not td_mode:
            td_mode = "cash" if asset_type in {"SPOT"} else "cross"
        params = {
            "instId": request_symbol,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": str(vol),
        }
        ccy = kwargs.get("ccy")
        if ccy not in (None, ""):
            params["ccy"] = ccy
        if client_order_id is not None:
            params["clOrdId"] = client_order_id
        if ord_type != "market" and price not in (None, ""):
            params["px"] = str(price)
        if asset_type == "SPOT" and ord_type == "market":
            params["tgtCcy"] = kwargs.get("tgt_ccy") or kwargs.get("tgtCcy") or "base_ccy"
        for param_key, aliases in {
            "posSide": ("posSide", "pos_side", "position_side", "positionSide"),
            "reduceOnly": ("reduceOnly", "reduce_only"),
            "tgtCcy": ("tgtCcy", "tgt_ccy"),
            "tag": ("tag",),
        }.items():
            for alias in aliases:
                value = kwargs.get(alias)
                if value in (None, ""):
                    continue
                params[param_key] = str(value).lower() if isinstance(value, bool) else str(value)
                break
        path = self._params.get_rest_path(request_type)
        path = path.replace("<instrument_id>", request_symbol)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "offset": offset,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._make_order_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _make_order_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        if extra_data is None:
            pass
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = [
            {
                "client_order_id": i["clOrdId"],
                "order_id": i["ordId"],
                "tag": i["tag"],
                "s_code": i["sCode"],
                "s_msg": i["sMsg"],
                "in_server_time": input_data.get("inTime"),
                "out_server_time": input_data.get("outTime"),
            }
            for i in input_data["data"]
        ]
        return data, status

    # noinspection PyBroadException
    def make_order(
        self,
        symbol: Any,
        vol: Any,
        price: Any = None,
        order_type: Any = "buy-limit",
        offset: Any = "open",
        post_only: Any = False,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """make_order method"""
        path, params, extra_data = self._make_order(
            symbol,
            vol,
            price,
            order_type,
            offset,
            post_only,
            client_order_id,
            extra_data,
            **kwargs,
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    # noinspection PyBroadException
    def async_make_order(
        self,
        symbol: Any,
        vol: Any,
        price: Any = None,
        order_type: Any = "buy-limit",
        offset: Any = "open",
        post_only: Any = False,
        client_order_id: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """async_make_order method"""
        path, params, extra_data = self._make_order(
            symbol,
            vol,
            price,
            order_type,
            offset,
            post_only,
            client_order_id,
            extra_data,
            **kwargs,
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _amend_order(
        self,
        symbol: Any,
        order_id: Any = None,
        client_order_id: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Amend an incomplete order"""
        request_symbol = self._params.get_symbol(symbol)
        request_type = "amend_order"
        params = {
            "instId": request_symbol,
        }
        if order_id:
            params["ordId"] = order_id
        if client_order_id:
            params["clOrdId"] = client_order_id
        if new_sz is not None:
            params["newSz"] = str(new_sz)
        if new_px is not None:
            params["newPx"] = str(new_px)
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._amend_order_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    @staticmethod
    def _amend_order_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        if extra_data is None:
            pass
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = [
            {
                "client_order_id": i.get("clOrdId", ""),
                "order_id": i.get("ordId", ""),
                "req_id": i.get("reqId", ""),
                "s_code": i.get("sCode", ""),
                "s_msg": i.get("sMsg", ""),
            }
            for i in input_data["data"]
        ]
        return data, status

    def amend_order(
        self,
        symbol: Any,
        order_id: Any = None,
        client_order_id: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """amend_order method"""
        path, params, extra_data = self._amend_order(
            symbol, order_id, client_order_id, new_sz, new_px, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_amend_order(
        self,
        symbol: Any,
        order_id: Any = None,
        client_order_id: Any = None,
        new_sz: Any = None,
        new_px: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """async_amend_order method"""
        path, params, extra_data = self._amend_order(
            symbol, order_id, client_order_id, new_sz, new_px, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _cancel_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_symbol = self._params.get_symbol(symbol)
        request_type = "cancel_order"
        path = self._params.get_rest_path(request_type)
        params = {"instId": request_symbol}
        if order_id:
            params["ordId"] = order_id
        if "client_order_id" in kwargs:
            params["clOrdId"] = kwargs["client_order_id"]
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._cancel_order_normalize_function,
            },
        )
        return path, params, extra_data

    @staticmethod
    def _cancel_order_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        if extra_data:
            pass
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                {
                    "client_order_id": i["clOrdId"],
                    "order_id": i["ordId"],
                    "s_code": i["sCode"],
                    "s_msg": i["sMsg"],
                }
                for i in data
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    def cancel_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """cancel_order method"""
        path, params, extra_data = self._cancel_order(
            symbol, order_id, extra_data, **kwargs
        )
        data = self.request(path, body=params, extra_data=extra_data)
        return data

    def async_cancel_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_cancel_order method"""
        path, params, extra_data = self._cancel_order(
            symbol, order_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, body=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # noinspection PyBroadException
    def _query_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_symbol = self._params.get_symbol(symbol)
        request_type = "query_order"
        path = self._params.get_rest_path(request_type)
        params: dict[str, Any] = {}
        if order_id is not None:
            params["ordId"] = order_id
        if "client_order_id" in kwargs:
            params["clOrdId"] = kwargs["client_order_id"]
        params["instId"] = request_symbol
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._query_order_normalize_function,
            },
        )
        return path, params, extra_data

    @staticmethod
    def _query_order_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxOrderData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            data = data_list
        else:
            data = []
        return data, status

    # noinspection PyBroadException
    def query_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """query_order method"""
        path, params, extra_data = self._query_order(
            symbol, order_id, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_query_order(
        self, symbol: Any, order_id: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_query_order method"""
        path, params, extra_data = self._query_order(
            symbol, order_id, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_open_orders(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        request_symbol = self._params.get_symbol(symbol) if symbol is not None else ""
        request_type = "get_open_orders"
        uly = kwargs.get("uly", "")
        inst_type = kwargs.get("instType", "")
        ord_type = kwargs.get("ordType", "")
        state = kwargs.get("state", "")
        after = kwargs.get("after", "")
        before = kwargs.get("before", "")
        limit = kwargs.get("limit", "")
        inst_family = kwargs.get("instFamily", "")
        params = {
            "instType": inst_type,
            "uly": uly,
            "instId": request_symbol,
            "ordType": ord_type,
            "state": state,
            "after": after,
            "before": before,
            "limit": limit,
            "instFamily": inst_family,
        }

        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._get_open_orders_normalize_function,
            },
        )
        return path, params, extra_data

    @staticmethod
    def _get_open_orders_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if isinstance(data, list):
            data_list = [
                OkxOrderData(
                    i, extra_data["symbol_name"], extra_data["asset_type"], True
                )
                for i in data
            ]
            target_data = data_list
        elif isinstance(data, dict):
            data_list = [
                OkxOrderData(
                    data, extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    # noinspection PyBroadException
    def get_open_orders(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """get_open_orders method"""
        path, params, extra_data = self._get_open_orders(symbol, extra_data, **kwargs)
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    # noinspection PyBroadException
    def async_get_open_orders(
        self, symbol: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """async_get_open_orders method"""
        path, params, extra_data = self._get_open_orders(symbol, extra_data, **kwargs)
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    def _get_order_history(
        self,
        inst_type: Any = "SWAP",
        symbol: Any = None,
        ord_type: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get order history (last 7 days)"""
        request_type = "get_order_history"
        params = {"instType": inst_type}
        if symbol:
            params["instId"] = self._params.get_symbol(symbol)
        if ord_type:
            params["ordType"] = ord_type
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
                "symbol_name": symbol or "ALL",
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": TradeMixin._get_open_orders_normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def get_order_history(
        self,
        inst_type: Any = "SWAP",
        symbol: Any = None,
        ord_type: Any = None,
        state: Any = None,
        after: Any = None,
        before: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_order_history method"""
        path, params, extra_data = self._get_order_history(
            inst_type,
            symbol,
            ord_type,
            state,
            after,
            before,
            limit,
            extra_data,
            **kwargs,
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def _get_deals(
        self,
        symbol: Any = None,
        count: Any = 100,
        start_time: Any = "",
        end_time: Any = "",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        if symbol is not None:
            request_symbol = self._params.get_symbol(symbol)
        else:
            request_symbol = ""
            symbol = ""
        request_type = "get_deals"
        params = {
            "instType": self.asset_type,
            "instId": request_symbol,
            "limit": str(count),
            "uly": kwargs.get("underlying", ""),
            "ordId": kwargs.get("ordId", ""),
            "instFamily": kwargs.get("instFamily", ""),
            "before": "",
            "after": "",
            "start": start_time,
            "end": end_time,
        }
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol,
                "exchange_name": self.exchange_name,
                "asset_type": self.asset_type,
                "normalize_function": TradeMixin._get_deals_normalize_function,
            },
        )
        return path, params, extra_data

    @staticmethod
    def _get_deals_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        status = input_data["code"] == "0"
        if "data" not in input_data:
            return [], status
        data = input_data["data"]
        if len(data) > 0:
            data_list = [
                OkxRequestTradeData(
                    data[0], extra_data["symbol_name"], extra_data["asset_type"], True
                )
            ]
            target_data = data_list
        else:
            target_data = []
        return target_data, status

    # noinspection PyBroadException
    def get_deals(
        self,
        symbol: Any = None,
        count: Any = 100,
        start_time: Any = "",
        end_time: Any = "",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """get_deals method"""
        path, params, extra_data = self._get_deals(
            symbol, count, start_time, end_time, extra_data, **kwargs
        )
        data = self.request(path, params=params, extra_data=extra_data)
        return data

    def async_get_deals(
        self,
        symbol: Any = None,
        count: Any = 100,
        start_time: Any = "",
        end_time: Any = "",
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """async_get_deals method"""
        path, params, extra_data = self._get_deals(
            symbol, count, start_time, end_time, extra_data, **kwargs
        )
        self.submit(
            self.async_request(path, params=params, extra_data=extra_data),
            callback=self.async_callback,
        )

    # ==================== Algo Trading APIs ====================













