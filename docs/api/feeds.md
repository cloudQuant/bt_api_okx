---
title: Feeds | bt_api_okx
---

# Feeds | 数据源

OKX feeds handle all REST API requests and WebSocket subscriptions. They are organized by asset type (Spot vs Swap) and by data category (market vs account).

---

## OkxRequestData — REST Feed Base

```python
from bt_api_okx.feeds.live_okx import OkxRequestDataSpot, OkxRequestDataSwap
```

`OkxRequestData` inherits from **11 mixins**, providing a comprehensive set of REST API methods:

### Mixin Overview

| Mixin | REST Methods |
|---|---|
| `MarketDataMixin` | `get_ticker`, `get_orderbook`, `get_bars`, `get_trades`, `get_funding_rate`, `get_mark_price`, `get_open_interest`, `get_instruments` |
| `TradeMixin` | `make_order`, `amend_order`, `cancel_order`, `get_order`, `get_open_orders`, `get_order_history`, `get_deals`, `get_algo_orders`, `batch_make_orders` |
| `AccountMixin` | `get_account`, `get_balance`, `get_positions`, `get_config`, `get_max_size`, `get_fee` |
| `TradingAccountMixin` | `set_leverage`, `set_margin_type`, `set_position_mode` |
| `FundingMixin` | `get_funding_rate_history` |
| `GridTradingMixin` | Grid trading endpoints |
| `CopyTradingMixin` | Copy trading endpoints |
| `RfqMixin` | RFQ endpoints |
| `SpreadTradingMixin` | Spread trading endpoints |
| `StatisticsMixin` | Trading statistics endpoints |
| `StatusMixin` | System status endpoints |
| `SubAccountMixin` | Sub-account endpoints |

### Supported Capabilities

```python
@classmethod
def _capabilities(cls) -> set[Capability]:
    return {
        Capability.GET_TICK,
        Capability.GET_DEPTH,
        Capability.GET_KLINE,
        Capability.GET_FUNDING_RATE,
        Capability.GET_MARK_PRICE,
        Capability.MAKE_ORDER,
        Capability.CANCEL_ORDER,
        Capability.QUERY_ORDER,
        Capability.QUERY_OPEN_ORDERS,
        Capability.GET_DEALS,
        Capability.GET_BALANCE,
        Capability.GET_ACCOUNT,
        Capability.GET_POSITION,
        Capability.MARKET_STREAM,
        Capability.ACCOUNT_STREAM,
        Capability.CROSS_MARGIN,
        Capability.ISOLATED_MARGIN,
        Capability.HEDGE_MODE,
        Capability.BATCH_ORDER,
        Capability.CONDITIONAL_ORDER,
        Capability.TRAILING_STOP,
        Capability.OCO_ORDER,
        Capability.GET_EXCHANGE_INFO,
        Capability.GET_SERVER_TIME,
    }
```

### Authentication

```python
# HMAC-SHA256 signature
def signature(timestamp, method, request_path, secret_key, body=None) -> str:
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(bytes(secret_key, "utf8"), bytes(message, "utf-8"), digestmod="sha256")
    return base64.b64encode(mac.digest()).decode()

# Request headers with OKX-specific fields
def get_header(api_key, sign, timestamp, passphrase) -> dict:
    return {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": str(timestamp),
        "OK-ACCESS-PASSPHRASE": passphrase,
        "x-simulated-trading": "0",
    }
```

### Rate Limiter

```python
@staticmethod
def _create_default_rate_limiter() -> RateLimiter:
    rules = [
        RateLimitRule(name="okx_general",    limit=20, interval=2,
                      type=RateLimitType.SLIDING_WINDOW, scope=RateLimitScope.ENDPOINT,
                      endpoint="/api/v5/market/*"),
        RateLimitRule(name="okx_trade",      limit=60, interval=2,
                      type=RateLimitType.SLIDING_WINDOW, scope=RateLimitScope.ENDPOINT,
                      endpoint="/api/v5/trade/order"),
        RateLimitRule(name="okx_account",    limit=10, interval=2,
                      type=RateLimitType.SLIDING_WINDOW, scope=RateLimitScope.ENDPOINT,
                      endpoint="/api/v5/account/*"),
    ]
```

---

## Spot Feeds

### OkxRequestDataSpot

```python
class OkxRequestDataSpot(OkxRequestData):
    """REST feed for OKX Spot trading."""
```

### OkxMarketWssDataSpot

```python
class OkxMarketWssDataSpot(OkxMarketWssBase):
    """WebSocket market data feed for OKX Spot."""
    # Subscribes to: ticker, depth, trades, klines (public channels)
```

### OkxAccountWssDataSpot

```python
class OkxAccountWssDataSpot(OkxAccountWssBase):
    """WebSocket account data feed for OKX Spot."""
    # Subscribes to: account, orders, positions (private channels)
```

---

## Swap Feeds

### OkxRequestDataSwap

```python
class OkxRequestDataSwap(OkxRequestData):
    """REST feed for OKX USDT-M Perpetual Futures."""
```

### OkxMarketWssDataSwap

```python
class OkxMarketWssDataSwap(OkxMarketWssBase):
    """WebSocket market data feed for OKX USDT-M Perpetual."""
```

### OkxAccountWssDataSwap

```python
class OkxAccountWssDataSwap(OkxAccountWssBase):
    """WebSocket account data feed for OKX USDT-M Perpetual."""
```

---

## WSS Base Classes

### OkxMarketWssBase

Base class for all OKX market WebSocket feeds.

```python
class OkxMarketWssBase:
    def __init__(self, data_queue, wss_url, exchange_data, topics, **kwargs)
    def start(self, connect_timeout=1.0) -> None
    def stop(self) -> None
    def subscribe(self) -> None    # Send subscription requests
    def on_message(self, msg) -> None  # Handle incoming messages
    def _handle_ticker(self, data) -> OkxTickerData
    def _handle_depth(self, data) -> OkxOrderBookData
    def _handle_trade(self, data) -> OkxWssTradeData
    def _handle_kline(self, data) -> OkxBarData
```

### OkxAccountWssBase

Base class for all OKX account WebSocket feeds.

```python
class OkxAccountWssBase:
    def __init__(self, data_queue, wss_url, exchange_data, topics, **kwargs)
    def start(self, connect_timeout=1.0) -> None
    def stop(self) -> None
    def subscribe(self) -> None
    def on_message(self, msg) -> None
    def _handle_account(self, data) -> OkxBalanceData
    def _handle_orders(self, data) -> OkxOrderData
    def _handle_positions(self, data) -> OkxPositionData
```

---

## Mixin Methods (Key Examples)

### MarketDataMixin

```python
# Get 24hr rolling ticker
ticker = feed.get_ticker(symbol="BTC-USDT")

# Get order book depth
depth = feed.get_orderbook(symbol="BTC-USDT", depth=20)

# Get K-line / candlestick data
bars = feed.get_bars(symbol="BTC-USDT", period="1m", count=100)

# Get recent trades
trades = feed.get_trades(symbol="BTC-USDT")

# Get funding rate (futures only)
fr = feed.get_funding_rate(symbol="BTC-USDT-SWAP")

# Get mark price (futures only)
mp = feed.get_mark_price(symbol="BTC-USDT-SWAP")

# Get open interest (futures only)
oi = feed.get_open_interest(symbol="BTC-USDT-SWAP")
```

### TradeMixin

```python
# Place an order
order = feed.make_order(
    symbol="BTC-USDT",
    price=67000,
    vol=0.001,
    order_type="buy-limit",
    offset="open",      # futures only: "open" or "close"
)

# Cancel order
feed.cancel_order(symbol="BTC-USDT", order_id="123456")

# Query open orders
open_orders = feed.get_open_orders(symbol="BTC-USDT")

# Query order history
history = feed.get_order_history(symbol="BTC-USDT", limit=100)
```

### AccountMixin

```python
# Get account info
account = feed.get_account()

# Get balances
balances = feed.get_balance()

# Get positions (futures)
positions = feed.get_position(symbol="BTC-USDT-SWAP")
```

### TradingAccountMixin

```python
# Set leverage
feed.set_leverage(symbol="BTC-USDT-SWAP", leverage=10)

# Set margin type (cross/isolated)
feed.set_margin_type(symbol="BTC-USDT-SWAP", margin_type="isolated")
```

---

## 中文

OKX feeds 处理所有 REST API 请求和 WebSocket 订阅。按资产类型（现货 vs 永续）和数据类型（行情 vs 账户）组织。

### OkxRequestData — REST Feed 基类

`OkxRequestData` 继承自 **11 个 mixin**，提供全面的 REST API 方法：

| Mixin | REST 方法 |
|---|---|
| `MarketDataMixin` | `get_ticker`, `get_orderbook`, `get_bars`, `get_trades`, `get_funding_rate`, `get_mark_price`, `get_open_interest`, `get_instruments` |
| `TradeMixin` | `make_order`, `amend_order`, `cancel_order`, `get_order`, `get_open_orders`, `get_order_history`, `get_deals`, `get_algo_orders`, `batch_make_orders` |
| `AccountMixin` | `get_account`, `get_balance`, `get_positions`, `get_config`, `get_max_size`, `get_fee` |
| `TradingAccountMixin` | `set_leverage`, `set_margin_type`, `set_position_mode` |

### 现货 Feeds

- `OkxRequestDataSpot` — 现货 REST feed
- `OkxMarketWssDataSpot` — 现货行情 WebSocket feed
- `OkxAccountWssDataSpot` — 现货账户 WebSocket feed

### 永续合约 Feeds

- `OkxRequestDataSwap` — U本位永续 REST feed
- `OkxMarketWssDataSwap` — U本位永续行情 WebSocket feed
- `OkxAccountWssDataSwap` — U本位永续账户 WebSocket feed

### 关键方法示例

```python
# 行情
ticker = feed.get_ticker(symbol="BTC-USDT")
bars = feed.get_bars(symbol="BTC-USDT", period="1m", count=100)

# 交易
order = feed.make_order(symbol="BTC-USDT", price=67000, vol=0.001, order_type="buy-limit")
feed.cancel_order(symbol="BTC-USDT", order_id="123456")

# 账户
balances = feed.get_balance()
positions = feed.get_position(symbol="BTC-USDT-SWAP")
```
