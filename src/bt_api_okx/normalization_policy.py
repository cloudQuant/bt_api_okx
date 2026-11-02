"""OKX-specific normalization choices used by the unified SDK."""

from types import MappingProxyType

from bt_api_base.normalization_policy import LegacyNormalizationPolicy
from bt_api_base.order_identity_fields import NEUTRAL_ORDER_IDENTITY_FIELDS
from bt_api_base.provider_order_source_aliases import build_provider_order_source_aliases
from bt_api_base.order_provenance_fields import (
    NEUTRAL_ORDER_SOURCE_FIELDS,
    PROVIDER_SCOPED_ORDER_PROVENANCE_SCHEMAS,
)


class OkxNormalizationPolicy(LegacyNormalizationPolicy):
    trade_id_fields = ("trade_id", "fill_id", "deal_id", "tradeId")
    tick_trading_day_fields = ("trading_day",)
    tick_action_day_fields = ("action_day",)
    risk_position_dimensions_require_projection = False
    # Preserve the prior non-swap acknowledgement pending venue review.
    position_mode_ack_code = "200"
    position_mode_placement_guard_required = True
    # Preserve the previous common aliases until venue-specific coverage is reviewed.
    order_status_fields = ("status", "order_status", "state")
    trade_fee_fields = ("fee_amount", "fee", "trade_fee", "commission")
    identity_fields = MappingProxyType({
        **NEUTRAL_ORDER_IDENTITY_FIELDS,
        'position_side': ('position_side', 'posSide'),
        'position_mode': ('position_mode', 'posMode'),
    })
    order_provenance_schemas = PROVIDER_SCOPED_ORDER_PROVENANCE_SCHEMAS
    order_provenance_source_fields = NEUTRAL_ORDER_SOURCE_FIELDS | frozenset({
        'accFillSz',
        'clOrdId',
        'fillPx',
        'fillSz',
        'instId',
        'ordId',
        'posSide',
        'sz',
    })
    (
        risk_order_source_aliases,
        group_order_source_aliases,
        group_fill_source_aliases,
    ) = build_provider_order_source_aliases(
        order_provenance_source_fields,
        risk_order_native_aliases={
            "provider_order_id": ("ordId",),
            "client_order_id": ("clOrdId",),
            "status": ("state",),
            "filled_quantity": ("accFillSz",),
            "quantity": ("sz",),
            "instrument": ("instId",),
            "side": ("side",),
            "position_side": ("posSide",),
        },
        group_order_native_aliases={
            "order_id": ("ordId",),
            "client_order_id": ("clOrdId",),
            "status": ("state",),
            "filled": ("accFillSz",),
            "quantity": ("sz",),
            "instrument": ("instId",),
            "side": ("side",),
        },
        group_fill_native_aliases={
            "order_id": ("ordId",),
            "client_order_id": ("clOrdId",),
            "instrument": ("instId",),
            "side": ("side",),
            "quantity": ("fillSz",),
            "price": ("fillPx",),
        },
    )
    response_error_item_fields = ("sCode",)
    # CTP/OKX source uses the neutral data collection.
    result_collection_fields = ("data",)
    exchange_time_fields = (
        "exchange_time", "timestamp", "server_time", "ts", "uTime", "event_time",
        "event_time_utc", "timestamp_ms",
    )
    funding_rate_fields = ("funding_rate", "fundingRate", "lastFundingRate", "rate")
    funding_interval_hours_fields = ("fundingIntervalHours",)
    funding_interval_start_fields = ("fundingTime",)
    funding_interval_end_fields = ("nextFundingTime",)
    funding_raw_fields = (
        "funding_rate", "fundingRate", "lastFundingRate", "rate", "next_funding_time",
        "fundingTime", "nextFundingTime", "settlement_interval_seconds",
        "funding_interval_seconds", "fundingIntervalHours",
    )
    base_symbol_fields = (
        "symbol", "symbol_name", "instrument", "instrument_id", "data_name", "instId",
        "trade_symbol",
    )
    funding_time_fields = ("fundingTime", "nextFundingTime")
    permission_fields = ("trading_permissions", "perm")
    can_trade_fields = ("can_trade",)
    order_statuses = MappingProxyType({
        "open": "accepted", "live": "accepted", "submitted": "submitted",
        "accepted": "accepted", "pending": "submitted", "partial": "partial",
        "partially_filled": "partial", "filled": "completed", "completed": "completed",
        "cancelled": "canceled", "canceled": "canceled", "mmp_canceled": "canceled",
        "expired": "expired", "rejected": "rejected", "unknown": "unknown",
        "local_pending": "submitted",
    })
    position_mode_boolean_field = None
    position_mode_fields = ("position_mode", "posMode")
    position_mode_aliases = MappingProxyType({"net_mode": "net", "long_short_mode": "dual_side"})
    order_fields = MappingProxyType({
        "order_id": ("order_id", "external_order_id", "ordId"),
        "client_id": ("client_order_id", "clOrdId", "order_ref"),
        "filled": ("filled", "filled_quantity", "executed_qty", "accFillSz"),
        "average": ("avg_price", "average_price", "order_avg_price", "avgPx"),
        "cum_quote": ("cum_quote",), "size": ("quantity", "size", "order_size", "sz"),
        "order_ref": ("order_ref",), "exchange_id": ("exchange_id",),
        "front_id": ("front_id",), "session_id": ("session_id",),
        "account_id": ("account_id",), "trading_day": ("trading_day",),
        "fee_currency": ("fee_currency", "feeCcy"),
        "commission_currency": ("commission_currency", "fee_currency", "feeCcy"),
    })
    trade_fields = MappingProxyType({
        "order_id": ("order_id", "external_order_id", "ordId"),
        "client_id": ("client_order_id", "clOrdId"),
        "size": ("quantity", "size", "trade_volume", "fillSz", "volume"),
        "price": ("trade_price", "price", "fillPx"), "exchange_id": ("exchange_id",),
        "account_id": ("account_id",), "trading_day": ("trading_day",),
        "fee_currency": ("fee_currency", "trade_fee_symbol", "feeCcy"),
    })
    signed_fee_currency_field = "feeCcy"
    position_fields = MappingProxyType({
        "quantity": ("quantity", "position_volume", "volume", "size", "pos", "trade_volume"),
        "side": ("position_side", "direction", "position_direction", "posSide", "side"),
        "position_id": ("position_id",),
        "price": ("average_price", "avg_price", "price", "avgPx"),
        "today": ("today", "today_position", "today_volume"),
        "yesterday": ("yesterday", "yesterday_position", "yd_position"),
        "multiplier": ("multiplier", "contract_size", "volume_multiple"),
        "exchange_id": ("exchange_id",),
    })
    balance_nested_fields = ("details", "balances")
    balance_fields = MappingProxyType({
        "currency": ("currency", "ccy", "account_type", "symbol_name", "symbol"),
        "cash": (
            "available_cash", "availEq", "availBal", "available", "cash", "available_margin",
            "margin_free", "free_margin", "free",
        ),
        "value": ("equity", "eq", "value"),
        "wallet": ("balance", "cashBal", "margin", "total_wallet_balance"),
        "unrealized": ("unrealized_profit",),
        "margin_used": ("margin_used", "used_margin"),
        "account_id": ("account_id",),
    })
    instrument_spec_fields = MappingProxyType({
        "symbol": ("symbol", "symbol_name", "instId"),
        "base_currency": ("base_currency", "baseCcy", "ctValCcy"),
        "quote_currency": ("quote_currency", "quoteCcy", "settleCcy"),
        "asset_type": ("asset_type", "instType"),
        "contract_type": ("contract_type", "instType"),
    })
    instrument_spec_linear_type_field = "ctType"
    instrument_fields = MappingProxyType({
        "multiplier": ("multiplier", "contract_size", "ctVal"),
        "step": ("lot_size", "order_size_step", "volume_step", "lotSz"),
        "min_size": ("min_size", "volume_min", "minSz"),
        "max_size": ("max_size", "volume_max", "maxLmtSz"),
        "tick_size": ("tick_size", "price_tick", "tickSz"),
        "settlement_currency": ("settlement_currency", "settleCcy", "currency"),
        "base_currency": ("base_currency", "ctValCcy", "baseCcy"),
        "margin_rate": ("margin_rate", "long_margin_rate"),
        "commission_rate": ("commission_rate", "taker_commission_rate"),
        "exchange_id": ("exchange_id",),
    })
    instrument_contract_value_field = "ctVal"
    instrument_contract_multiplier_field = "ctMult"
    instrument_linear_type_field = "ctType"
    instrument_perpetual_type_field = None
    event_id_fields = ("event_id", "trade_id", "fill_id", "order_id", "ordId")
    event_audit_fields = (
        "sequence", "sequence_id", "previous_sequence", "prevSeqId", "checksum", "action", "ts",
    )
    orderbook_sequence_fields = ("sequence", "sequence_id", "update_id")
    orderbook_previous_fields = ("previous_sequence", "prev_sequence", "prevSeqId")
    orderbook_delta_predecessor_fields = ()


class OkxSwapNormalizationPolicy(OkxNormalizationPolicy):
    quantity_unit = "contracts"
    position_mode_ack_code = "0"


def normalization_policy(exchange_name):
    if exchange_name == "OKX___SWAP":
        return OkxSwapNormalizationPolicy()
    return OkxNormalizationPolicy()


__all__ = ("normalization_policy",)
