"""
OKX API - TradingAccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.ta_part1_mixin import TradingAccountPart1Mixin
from bt_api_okx.feeds.live_okx.mixins.ta_part2_mixin import TradingAccountPart2Mixin
from bt_api_okx.feeds.live_okx.mixins.ta_part3_mixin import TradingAccountPart3Mixin
from bt_api_okx.feeds.live_okx.mixins.ta_part4_mixin import TradingAccountPart4Mixin


class TradingAccountMixin(TradingAccountPart1Mixin, TradingAccountPart2Mixin, TradingAccountPart3Mixin, TradingAccountPart4Mixin):
    """交易账户 mixin（聚合 4 个分组）。"""
