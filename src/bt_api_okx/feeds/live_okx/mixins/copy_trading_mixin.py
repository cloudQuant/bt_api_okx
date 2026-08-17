"""
OKX API - CopyTradingMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.copy_trading_mixin_part1 import CopyTradingMixinPart1
from bt_api_okx.feeds.live_okx.mixins.copy_trading_mixin_part2 import CopyTradingMixinPart2
from bt_api_okx.feeds.live_okx.mixins.copy_trading_mixin_part3 import CopyTradingMixinPart3


class CopyTradingMixin(CopyTradingMixinPart1, CopyTradingMixinPart2, CopyTradingMixinPart3):
    """CopyTradingMixin 聚合。"""
