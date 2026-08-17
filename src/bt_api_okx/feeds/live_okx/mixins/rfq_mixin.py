"""OKX API - RfqMixin
Auto-generated from request_base.py.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.rfq_mixin_part1 import RfqMixinPart1
from bt_api_okx.feeds.live_okx.mixins.rfq_mixin_part2 import RfqMixinPart2
from bt_api_okx.feeds.live_okx.mixins.rfq_mixin_part3 import RfqMixinPart3


class RfqMixin(RfqMixinPart1, RfqMixinPart2, RfqMixinPart3):
    """RfqMixin 聚合。"""
