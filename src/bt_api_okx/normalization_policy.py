"""OKX-specific normalization choices used by the unified SDK."""

from bt_api_base.normalization_policy import LegacyNormalizationPolicy


class OkxNormalizationPolicy(LegacyNormalizationPolicy):
    funding_time_fields = ("fundingTime", "nextFundingTime")
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
