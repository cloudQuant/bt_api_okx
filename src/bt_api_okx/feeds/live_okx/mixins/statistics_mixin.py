"""
OKX API - StatisticsMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.statistics_mixin_part1 import StatisticsMixinPart1
from bt_api_okx.feeds.live_okx.mixins.statistics_mixin_part2 import StatisticsMixinPart2
from bt_api_okx.feeds.live_okx.mixins.statistics_mixin_part3 import StatisticsMixinPart3


class StatisticsMixin(StatisticsMixinPart1, StatisticsMixinPart2, StatisticsMixinPart3):
    """StatisticsMixin 聚合。"""
