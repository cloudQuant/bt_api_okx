"""
OKX API - GridTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.grid_trading_mixin_part1 import GridTradingMixinPart1
from bt_api_okx.feeds.live_okx.mixins.grid_trading_mixin_part2 import GridTradingMixinPart2
from bt_api_okx.feeds.live_okx.mixins.grid_trading_mixin_part3 import GridTradingMixinPart3


class GridTradingMixin(GridTradingMixinPart1, GridTradingMixinPart2, GridTradingMixinPart3):
    """GridTradingMixin 聚合。"""
