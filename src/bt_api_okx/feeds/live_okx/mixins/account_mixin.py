"""
OKX API - AccountMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.accounts.okx_account import OkxAccountData
from bt_api_okx.containers.positions.okx_position import OkxPositionData
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.account_mixin_part1 import AccountMixinPart1
from bt_api_okx.feeds.live_okx.mixins.account_mixin_part2 import AccountMixinPart2


class AccountMixin(AccountMixinPart1, AccountMixinPart2):
    """AccountMixin 聚合。"""
