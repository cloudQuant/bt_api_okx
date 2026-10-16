"""
OKX REST API request base class.
Handles authentication, signing, and all REST API methods.
API methods are organized into Mixin classes under the mixins/ package.
"""

from __future__ import annotations

import base64
import hmac
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from urllib import parse

from bt_api_base.containers.requestdatas.request_data import RequestData
from bt_api_base.error import OKXErrorTranslator
from bt_api_base.exceptions import QueueNotInitializedError
from bt_api_base.feeds.capability import Capability
from bt_api_base.feeds.feed import Feed
from bt_api_base.feeds.transport_safety import sanitize_text
from bt_api_base.logging_factory import get_logger
from bt_api_base.rate_limiter import (
    RateLimiter,
    RateLimitRule,
    RateLimitScope,
    RateLimitType,
)

from bt_api_okx.environment import configure_environment, verify_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap
from bt_api_okx.feeds.live_okx.mixins.account_mixin import AccountMixin
from bt_api_okx.feeds.live_okx.mixins.copy_trading_mixin import CopyTradingMixin
from bt_api_okx.feeds.live_okx.mixins.funding_mixin import FundingMixin
from bt_api_okx.feeds.live_okx.mixins.grid_trading_mixin import GridTradingMixin
from bt_api_okx.feeds.live_okx.mixins.market_data_mixin import MarketDataMixin
from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_okx.feeds.live_okx.mixins.rfq_mixin import RfqMixin
from bt_api_okx.feeds.live_okx.mixins.spread_trading_mixin import SpreadTradingMixin
from bt_api_okx.feeds.live_okx.mixins.statistics_mixin import StatisticsMixin
from bt_api_okx.feeds.live_okx.mixins.status_mixin import StatusMixin
from bt_api_okx.feeds.live_okx.mixins.sub_account_mixin import SubAccountMixin
from bt_api_okx.feeds.live_okx.mixins.trade_mixin import TradeMixin
from bt_api_okx.feeds.live_okx.mixins.trading_account_mixin import TradingAccountMixin

if TYPE_CHECKING:  # pragma: no cover
    from bt_api_base.error import UnifiedError


def strict_credential_alias(parameters, names):
    supplied = []
    for name in names:
        if name not in parameters or parameters[name] is None:
            continue
        value = parameters[name]
        if value == "":
            continue
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError("OKX credentials must be non-empty trimmed strings")
        supplied.append(value)
    if len(set(supplied)) > 1:
        raise ValueError("OKX credential aliases conflict")
    return supplied[0] if supplied else None


def _utc_now_iso8601() -> str:
    """按 OKX V5 规范生成 ISO 8601 毫秒时间戳(UTC)。"""
    now = datetime.now(timezone.utc)  # noqa: UP017 - package supports Python 3.9
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}" + "Z"


def _sign(secret: str, timestamp: str, method: str, request_path: str, body: str) -> str:
    """OKX V5 签名: Base64(HMAC-SHA256(timestamp+method+requestPath+body, secret))。"""
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), digestmod="sha256")
    return base64.b64encode(mac.digest()).decode()


class OkxRequestData(
    AccountMixin,
    CopyTradingMixin,
    FundingMixin,
    GridTradingMixin,
    MarketDataMixin,
    RfqMixin,
    SpreadTradingMixin,
    StatisticsMixin,
    StatusMixin,
    SubAccountMixin,
    TradeMixin,
    TradingAccountMixin,
    Feed,
):
    """Class OkxRequestData"""

    @classmethod
    def _capabilities(cls: Any) -> set[Capability]:
        return {
            Capability.GET_TICK,
            Capability.GET_DEPTH,
            Capability.GET_KLINE,
            Capability.GET_FUNDING_RATE,
            Capability.GET_MARK_PRICE,
            Capability.MAKE_ORDER,
            Capability.CANCEL_ORDER,
            Capability.QUERY_ORDER,
            Capability.QUERY_OPEN_ORDERS,
            Capability.GET_DEALS,
            Capability.GET_BALANCE,
            Capability.GET_ACCOUNT,
            Capability.GET_POSITION,
            Capability.MARKET_STREAM,
            Capability.ACCOUNT_STREAM,
            Capability.CROSS_MARGIN,
            Capability.ISOLATED_MARGIN,
            Capability.HEDGE_MODE,
            Capability.BATCH_ORDER,
            Capability.CONDITIONAL_ORDER,
            Capability.TRAILING_STOP,
            Capability.OCO_ORDER,
            Capability.GET_EXCHANGE_INFO,
            Capability.GET_SERVER_TIME,
        }

    def __init__(self, data_queue: Any, **kwargs: Any) -> None:
        """__init__ method"""
        self._environment_options = dict(kwargs)
        super().__init__(data_queue, **kwargs)
        self.data_queue = data_queue
        self.public_key = strict_credential_alias(kwargs, ("public_key", "api_key"))
        self.private_key = strict_credential_alias(
            kwargs, ("private_key", "secret_key", "api_secret")
        )
        self.passphrase = strict_credential_alias(kwargs, ("passphrase",))
        self.topics = kwargs.get("topics", {})
        self.exchange_name = kwargs.get("exchange_name", "OKX___SWAP")
        self.asset_type = kwargs.get("asset_type", "SWAP")
        self.logger_name = kwargs.get("logger_name", "okx_swap_feed.log")
        self._params = self._configure_exchange_data(OkxExchangeDataSwap())
        self.request_logger = get_logger("okx_swap_feed")
        self.async_logger = get_logger("okx_swap_feed")
        self._error_translator = OKXErrorTranslator()
        self._rate_limiter = kwargs.get("rate_limiter", self._create_default_rate_limiter())
        self._symbol_info_cache: dict[str, dict[str, Any]] = {}

    def get_exchange_info(self, symbol=None, extra_data=None, **kwargs):
        """Return the exchange's instrument rules, including contract value and lot size."""
        inst_id = self._params.get_symbol(symbol) if symbol else None
        return self.get_public_instruments(
            inst_type=self.asset_type, inst_id=inst_id, extra_data=extra_data, **kwargs
        )

    def get_symbol_info(self, symbol: Any) -> dict[str, Any]:
        """Return a direct instrument projection merged with available fee rates."""
        requested = str(symbol or "").strip()
        if not requested:
            return {}
        cache_key = f"{str(self.asset_type or '').upper()}:{requested.upper()}"
        cached = self._symbol_info_cache.get(cache_key)
        if cached is not None:
            return dict(cached)
        try:
            instrument_result = self.get_instruments(
                asset_type=self.asset_type, inst_id=requested
            )
            rows = _okx_projection_rows(_okx_request_data_value(instrument_result))
        except Exception:
            rows = []
        candidates = _okx_symbol_candidates(requested)
        selected = next(
            (
                row
                for row in rows
                if _okx_symbol_matches(
                    _okx_text(row, "symbol_name", "symbol", "instId"), candidates
                )
            ),
            rows[0] if len(rows) == 1 else None,
        )
        if selected is None:
            return {}

        asset_type = _okx_text(selected, "asset_type", "instType") or str(self.asset_type or "")
        normalized_type = asset_type.upper()
        contract_value = _okx_float(selected, "contract_notional_value", "ctVal")
        raw_multiplier = _okx_float(
            selected,
            "contract_multiplier_raw",
            "contract_multiplier",
            "ctMult",
        )
        derivative = normalized_type in {"SWAP", "FUTURES", "FUTURE", "OPTION"}
        multiplier = contract_value if derivative and contract_value else raw_multiplier
        if multiplier is None and normalized_type == "SPOT":
            multiplier = 1.0
        symbol_name = _okx_text(selected, "symbol_name", "symbol", "instId") or requested
        contract_value_currency = _okx_value(
            selected, "contract_value_currency", "contract_value_ccy", "ctValCcy"
        )
        spec: dict[str, Any] = {
            "source": "okx_get_instruments",
            "exchange": "OKX",
            "exchange_id": "OKX",
            "symbol": symbol_name,
            "asset_type": asset_type,
            "base_asset": _okx_value(selected, "base_asset", "baseCcy"),
            "quote_asset": _okx_value(selected, "quote_asset", "quoteCcy"),
            "fee_currency": _okx_value(selected, "fee_currency", "settleCcy"),
            "contract_type": _okx_value(selected, "contract_type", "ctType"),
            "contract_value_currency": contract_value_currency,
            "contract_value_ccy": contract_value_currency,
            "ctValCcy": contract_value_currency,
            "contract_notional_value": contract_value,
            "okx_contract_value": contract_value,
            "contract_multiplier_raw": raw_multiplier,
            "contract_multiplier": multiplier,
            "contract_size": multiplier,
            "multiplier": multiplier,
            "price_tick": _okx_value(selected, "price_unit", "tickSz"),
            "tick_size": _okx_value(selected, "price_unit", "tickSz"),
            "min_order_size": _okx_value(selected, "min_qty", "minSz"),
            "max_order_size": _okx_value(selected, "max_limit_qty", "maxLmtSz", "max_qty"),
            "order_size_step": _okx_value(selected, "qty_unit", "lotSz"),
            "market_max_order_size": _okx_value(selected, "max_market_qty", "maxMktSz"),
            "min_notional": _okx_value(selected, "min_amount", "notional"),
            "max_leverage": _okx_value(selected, "max_leverage", "lever"),
            "leverage": _okx_value(selected, "leverage", "lever", "max_leverage"),
            "symbol_status": _okx_value(selected, "symbol_status", "state"),
        }
        spec = {key: value for key, value in spec.items() if value not in (None, "")}
        fee_family = _okx_text(selected, "underlying_symbol_name", "instFamily")
        if derivative and not fee_family and normalized_type == "SWAP" and symbol_name.upper().endswith("-SWAP"):
            fee_family = symbol_name[:-5]
        try:
            if normalized_type in {"SPOT", "MARGIN"}:
                fee_result = self.get_fee(inst_type=asset_type, inst_id=symbol_name)
            elif derivative and fee_family:
                fee_result = self.get_fee(inst_type=asset_type, inst_family=fee_family)
            else:
                fee_result = None
            if fee_result is not None:
                fee_rows = _okx_projection_rows(_okx_request_data_value(fee_result, prefer_input=True))
                fee_row = next((item for item in fee_rows if item), None)
                if fee_row is not None:
                    maker_key = "makerU" if derivative and _okx_value(fee_row, "makerU") is not None else "maker"
                    taker_key = "takerU" if derivative and _okx_value(fee_row, "takerU") is not None else "taker"
                    maker = _okx_fee_rate(_okx_value(fee_row, maker_key))
                    taker = _okx_fee_rate(_okx_value(fee_row, taker_key))
                    spec["fee_source"] = "okx_get_fee"
                    if maker is not None:
                        spec["maker_commission_rate"] = maker
                    if taker is not None:
                        spec["taker_commission_rate"] = taker
                        spec["commission_rate"] = taker
                        spec["open_commission_rate"] = taker
                    elif maker is not None:
                        spec["commission_rate"] = maker
                        spec["open_commission_rate"] = maker
        except Exception:
            pass
        if spec:
            self._symbol_info_cache[cache_key] = dict(spec)
        return spec

    def get_account_instruments(self, symbol, extra_data=None, **kwargs):
        """Return instruments enabled for this account without changing account state."""
        inst_id = self._params.get_symbol(symbol)
        return self.get_instruments(
            asset_type=self.asset_type,
            inst_id=inst_id,
            extra_data=extra_data,
            **kwargs,
        )

    def get_leverage_info(self, symbol, margin_mode="cross", extra_data=None, **kwargs):
        """Return configured leverage rows for an account instrument."""
        inst_id = self._params.get_symbol(symbol)
        path, params, request_extra = self._get_lever(
            self.asset_type,
            inst_id=inst_id,
            mgn_mode=margin_mode,
            extra_data=extra_data,
            **kwargs,
        )
        # Unlike several other account endpoints, leverage-info does not accept
        # instType.  Keep using the generated request builder for normalization
        # metadata, but send only the parameters in the OKX V5 contract.
        params.pop("instType", None)
        return self.request(path, params=params, extra_data=request_extra)

    def _configure_exchange_data(self, params):
        return configure_environment(params, self._environment_options)

    def get_environment_info(self):
        """Return the plugin's current endpoint proof without credentials."""
        return verify_environment(self._params)

    @staticmethod
    def _create_default_rate_limiter() -> RateLimiter:
        rules = [
            RateLimitRule(
                name="okx_general",
                limit=20,
                interval=2,
                type=RateLimitType.SLIDING_WINDOW,
                scope=RateLimitScope.ENDPOINT,
                endpoint="/api/v5/market/*",
            ),
            RateLimitRule(
                name="okx_trade",
                limit=60,
                interval=2,
                type=RateLimitType.SLIDING_WINDOW,
                scope=RateLimitScope.ENDPOINT,
                endpoint="/api/v5/trade/order",
            ),
            RateLimitRule(
                name="okx_account",
                limit=10,
                interval=2,
                type=RateLimitType.SLIDING_WINDOW,
                scope=RateLimitScope.ENDPOINT,
                endpoint="/api/v5/account/*",
            ),
        ]
        return RateLimiter(rules)

    def translate_error(self, raw_response: Any) -> UnifiedError | None:
        """OKX API  UnifiedError（）， None"""
        if isinstance(raw_response, dict):
            code = raw_response.get("code", raw_response.get("sCode", "0"))
            if str(code) != "0":
                return self._error_translator.translate(raw_response, self.exchange_name)
        return None

    def _raise_if_error(self, raw_response: Any) -> None:
        """API 响应含错误(code != "0")时抛出翻译后的 UnifiedError。"""
        error = self.translate_error(raw_response)
        if error is not None:
            raise error

    def push_data_to_queue(self, data: Any) -> None:
        """push_data_to_queue method"""
        if self.data_queue is not None:
            self.data_queue.put(data)
        else:
            raise QueueNotInitializedError("data_queue not initialized")

    # noinspection PyMethodMayBeStatic
    def signature(
        self,
        timestamp: Any,
        method: Any,
        request_path: Any,
        secret_key: Any,
        body: Any = None,
    ) -> str:
        """signature method"""
        body = "" if body is None else str(body)
        message = str(timestamp) + str.upper(method) + request_path + body
        mac = hmac.new(
            bytes(secret_key, encoding="utf8"),
            bytes(message, encoding="utf-8"),
            digestmod="sha256",
        )
        d = mac.digest()
        return base64.b64encode(d).decode()

    # noinspection PyMethodMayBeStatic
    def get_header(self, api_key: Any, sign: Any, timestamp: Any, passphrase: Any) -> dict[str, Any]:
        """get_header method"""
        header = {}
        header["Content-Type"] = "application/json"
        header["OK-ACCESS-KEY"] = api_key
        header["OK-ACCESS-SIGN"] = sign
        header["OK-ACCESS-TIMESTAMP"] = str(timestamp)
        header["OK-ACCESS-PASSPHRASE"] = passphrase
        header["x-simulated-trading"] = "1" if self._params.simulated_trading else "0"
        return header

    def request(
        self,
        path: Any,
        params: Any = None,
        body: Any = None,
        extra_data: Any = None,
        timeout: Any = 10,
        *,
        max_retries: Any = None,
    ) -> None:
        """http request function
        Args: path (TYPE): request url
            params (dict, optional): in url
            body (dict, optional): in request body
            extra_data(dict,None): extra_data, generate by user
            timeout (int, optional): request timeout(s)
        """
        if params is None:
            params: dict[str, Any] = {}
        if extra_data is None:
            extra_data = {}
        if max_retries is not None and (
            type(max_retries) is not int or not 1 <= max_retries <= 3
        ):
            raise ValueError("max_retries must be between one and three")
        method, path = path.split(" ", 1)
        req = parse.urlencode(params)
        url = f"{self._params.rest_url}{path}" + (f"?{req}" if req else "")
        if params:
            path = f"{path}?{req}"
        public = path.startswith(("/api/v5/public/", "/api/v5/market/", "/api/v5/system/"))
        if not public and not all(
            isinstance(value, str) and value.strip()
            for value in (self.public_key, self.private_key, self.passphrase)
        ):
            raise ValueError("OKX private requests require API key, secret and passphrase")
        timestamp = _utc_now_iso8601()
        body_str = (
            json.dumps(body, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
            if body is not None
            else None
        )
        signature_ = self.signature(
            timestamp,
            method,
            path,
            self.private_key or "",
            body_str,
        )
        headers = self.get_header(self.public_key, signature_, timestamp, self.passphrase)
        if public:
            headers = {
                key: value for key, value in headers.items() if not key.startswith("OK-ACCESS-")
            }
        if method.upper() == "GET":
            if max_retries is None:
                res = self.http_request(method, url, headers, body, timeout)
            else:
                res = self.http_request(
                    method, url, headers, body, timeout, max_retries=max_retries
                )
        else:
            res = self.http_request(
                method,
                url,
                headers,
                body,
                timeout,
                max_retries=1 if max_retries is None else max_retries,
            )
        self._raise_if_error(res)
        return RequestData(res, extra_data)

    async def async_request(
        self, path, params=None, body=None, extra_data=None, timeout=5
    ) -> RequestData:
        """http request function
        Args: path (TYPE): request url
            params (dict, optional): in url
            body (dict, optional): in request body
            timeout (int, optional): request timeout(s)
            extra_data(dict,None): extra_data, generate by user
        """
        if params is None:
            params: dict[str, Any] = {}
        if extra_data is None:
            extra_data = {}
        method, path = path.split(" ", 1)
        req = parse.urlencode(params)
        url = f"{self._params.rest_url}{path}" + (f"?{req}" if req else "")
        if params:
            path = f"{path}?{req}"
        public = path.startswith(("/api/v5/public/", "/api/v5/market/", "/api/v5/system/"))
        if not public and not all(
            isinstance(value, str) and value.strip()
            for value in (self.public_key, self.private_key, self.passphrase)
        ):
            raise ValueError("OKX private requests require API key, secret and passphrase")
        timestamp = _utc_now_iso8601()
        body_str = (
            json.dumps(body, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
            if body is not None
            else None
        )
        signature_ = self.signature(
            timestamp,
            method,
            path,
            self.private_key or "",
            body_str,
        )
        headers = self.get_header(self.public_key, signature_, timestamp, self.passphrase)
        if public:
            headers = {
                key: value for key, value in headers.items() if not key.startswith("OK-ACCESS-")
            }
        res = await self.async_http_request(method, url, headers, body_str, timeout)
        self._raise_if_error(res)
        return RequestData(res, extra_data)

    def async_callback(self, future: Any) -> None:
        """
        callback function for async requests, push result to data_queue
        :param future: asyncio future object
        :return: None
        """
        try:
            result = future.result()
            self.push_data_to_queue(result)
        except Exception as e:
            self.async_logger.warning(
                "async_callback::%s",
                sanitize_text(
                    e,
                    sensitive_values=(self.public_key, self.private_key, self.passphrase),
                ),
            )

    @staticmethod
    def _generic_normalize_function(input_data: Any, extra_data: Any) -> None:
        """Generic normalize function for OKX API responses.
        Extracts 'data' list and checks 'code' for status.
        Delegates to the shared normalizers module."""
        return generic_normalize_function(input_data, extra_data)


def _okx_request_data_value(result: Any, *, prefer_input: bool = False) -> Any:
    if prefer_input and callable(getattr(result, "get_input_data", None)):
        raw = result.get_input_data()
        if raw not in (None, ""):
            return raw
    if callable(getattr(result, "get_data", None)):
        return result.get_data()
    return result


def _okx_projection_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        nested = payload.get("data")
        if isinstance(nested, list):
            payload = nested
        elif isinstance(nested, dict):
            payload = [nested]
        else:
            payload = [payload]
    elif not isinstance(payload, list):
        payload = []
    rows: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            rows.append(dict(item))
            continue
        initializer = getattr(item, "init_data", None)
        if callable(initializer):
            initializer()
        getter = getattr(item, "get_all_data", None)
        if callable(getter):
            row = getter()
            if isinstance(row, dict):
                rows.append(dict(row))
    return rows


def _okx_value(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def _okx_text(payload: dict[str, Any], *keys: str) -> str:
    value = _okx_value(payload, *keys)
    return str(value).strip() if value is not None else ""


def _okx_float(payload: dict[str, Any], *keys: str) -> float | None:
    value = _okx_value(payload, *keys)
    if isinstance(value, bool):
        return None
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _okx_symbol_candidates(symbol: str) -> set[str]:
    dashed = symbol.replace("/", "-")
    compact = "".join(character for character in dashed if character.isalnum())
    return {candidate.upper() for candidate in (symbol, dashed, compact) if candidate}


def _okx_symbol_matches(symbol: str, candidates: set[str]) -> bool:
    compact = "".join(character for character in symbol if character.isalnum()).upper()
    return symbol.upper() in candidates or compact in candidates


def _okx_fee_rate(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return None
    if abs(rate) > 1:
        rate /= 100.0
    return -rate
