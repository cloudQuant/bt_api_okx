"""
OKX API - FundingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.funding_mixin_part1 import FundingMixinPart1
from bt_api_okx.feeds.live_okx.mixins.funding_mixin_part2 import FundingMixinPart2
from bt_api_okx.feeds.live_okx.mixins.funding_mixin_part3 import FundingMixinPart3


class FundingMixin(FundingMixinPart1, FundingMixinPart2, FundingMixinPart3):
    """FundingMixin 聚合。"""
