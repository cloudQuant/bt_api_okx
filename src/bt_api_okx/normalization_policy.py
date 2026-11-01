"""OKX-specific normalization choices used by the unified SDK."""

from bt_api_base.normalization_policy import LegacyNormalizationPolicy


class OkxNormalizationPolicy(LegacyNormalizationPolicy):
    funding_time_fields = ("fundingTime", "nextFundingTime")


class OkxSwapNormalizationPolicy(OkxNormalizationPolicy):
    quantity_unit = "contracts"
    position_mode_ack_code = "0"


def normalization_policy(exchange_name):
    if exchange_name == "OKX___SWAP":
        return OkxSwapNormalizationPolicy()
    return OkxNormalizationPolicy()


__all__ = ("normalization_policy",)
