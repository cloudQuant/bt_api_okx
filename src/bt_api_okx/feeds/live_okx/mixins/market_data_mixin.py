"""
OKX API - MarketDataMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.containers.bars.okx_bar import OkxBarData
from bt_api_okx.containers.fundingrates.okx_funding_rate import OkxFundingRateData
from bt_api_okx.containers.markprices.okx_mark_price import OkxMarkPriceData
from bt_api_okx.containers.orderbooks.okx_orderbook import OkxOrderBookData
from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
from bt_api_okx.feeds.live_okx.mixins.normalizers import generic_normalize_function
from bt_api_base.functions.utils import update_extra_data


from bt_api_okx.feeds.live_okx.mixins.market_data_mixin_part1 import MarketDataMixinPart1
from bt_api_okx.feeds.live_okx.mixins.market_data_mixin_part2 import MarketDataMixinPart2
from bt_api_okx.feeds.live_okx.mixins.market_data_mixin_part3 import MarketDataMixinPart3
from bt_api_okx.feeds.live_okx.mixins.market_data_mixin_part4 import MarketDataMixinPart4


class MarketDataMixin(MarketDataMixinPart1, MarketDataMixinPart2, MarketDataMixinPart3, MarketDataMixinPart4):
    """MarketDataMixin 聚合。"""
