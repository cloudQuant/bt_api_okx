"""OKX-specific normalization choices used by the unified SDK."""

from types import MappingProxyType

from bt_api_base.normalization_policy import LegacyNormalizationPolicy


class OkxNormalizationPolicy(LegacyNormalizationPolicy):
    funding_time_fields = ("fundingTime", "nextFundingTime")
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
    instrument_uses_filters = False
    instrument_perpetual_type_field = None
    event_id_fields = ("event_id", "trade_id", "fill_id", "order_id", "ordId")
    event_audit_fields = (
        "sequence", "sequence_id", "previous_sequence", "prevSeqId", "checksum", "action", "ts",
    )
    orderbook_sequence_fields = ("sequence", "sequence_id", "update_id")
    orderbook_previous_fields = ("previous_sequence", "prev_sequence", "prevSeqId")
    orderbook_delta_predecessor_fields = ()
    tick_bid_fields = ("bid_price", "bid")
    tick_ask_fields = ("ask_price", "ask")
    tick_price_fields = ("price", "last_price", "last")
    tick_volume_fields = ("volume", "last_volume")
    tick_cumulative_fields = ("cum_volume", "cumulative_volume")


class OkxSwapNormalizationPolicy(OkxNormalizationPolicy):
    quantity_unit = "contracts"
    position_mode_ack_code = "0"


def normalization_policy(exchange_name):
    if exchange_name == "OKX___SWAP":
        return OkxSwapNormalizationPolicy()
    return OkxNormalizationPolicy()


__all__ = ("normalization_policy",)
