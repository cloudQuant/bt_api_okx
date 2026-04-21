---
title: Gateway Adapter | bt_api_okx
---

# Gateway Adapter | 网关适配器

`OkxGatewayAdapter` provides a standalone gateway interface to OKX — wrapping REST API calls and WebSocket streams into a unified adapter that can be used independently of the full `bt_api` framework.

---

## OkxGatewayAdapter

```python
from bt_api_okx.gateway.adapter import OkxGatewayAdapter
```

### Constructor

```python
adapter = OkxGatewayAdapter(
    api_key="your_api_key",       # OKX API key
    secret_key="your_secret",     # OKX API secret
    passphrase="your_passphrase",  # OKX API passphrase
    asset_type="SWAP",            # "SWAP" (default) or "SPOT"
    # Optional:
    testnet=False,               # Use simulated trading (OKX sandbox)
    gateway_startup_timeout_sec=10.0,
    market_stream_connect_timeout_sec=1.0,
    account_stream_connect_timeout_sec=1.0,
)
```

### Connection Management

```python
adapter.connect()      # Start the adapter (spawns background thread)
adapter.disconnect()   # Stop the adapter and join background thread
```

### Market Data

```python
# Subscribe to real-time ticker data for symbols
adapter.subscribe_symbols(["BTC-USDT", "ETH-USDT"])
# Returns: {"symbols": ["BTC-USDT", "ETH-USDT"]}
```

### poll_output

```python
# Blocking poll of the internal queue
channel, data = adapter.poll_output(timeout=1.0)
# channel: "market" | "account" | "event"
# data: depends on channel type
```

### get_balance

```python
balance = adapter.get_balance()
# Returns: dict with balance data
# Example: {"ccy": "USDT", "bal": "1000.0", "frozenBal": "0.0", "availBal": "1000.0"}
```

### get_positions

```python
positions = adapter.get_positions()
# Returns: list[dict] — one dict per open position
# Each dict contains: symbol, side, size, avgPx, upl, margin, etc.
```

### place_order

```python
order = adapter.place_order({
    "symbol": "BTC-USDT",        # Trading symbol (use "-" not "/")
    "side": "buy",               # "buy" or "sell"
    "order_type": "limit",      # "limit", "market"
    "price": 67000,             # Order price (None for market orders)
    "volume": 0.001,             # Order quantity
    # Optional:
    "client_order_id": "my_id_123",  # Custom client order ID
    "offset": "open",            # "open" or "close" (futures only)
})
# Returns: dict with order response
```

### cancel_order

```python
result = adapter.cancel_order({
    "symbol": "BTC-USDT",
    "order_id": "1234567890",       # Exchange order ID
    # OR:
    "client_order_id": "my_id_123", # Custom client order ID
})
# Returns: dict with cancel response
```

---

## Adapter Dispatch

The adapter automatically routes incoming WebSocket messages to typed dispatch:

| Message Type | Channel | Dispatch Method |
|---|---|---|
| `OkxTickerData` | `CHANNEL_MARKET` | `_emit_ticker()` |
| `OkxOrderData` | `CHANNEL_EVENT` | `_emit_order()` |
| `OkxWssTradeData` / `OkxWssFillsData` | `CHANNEL_EVENT` | `_emit_trade()` |
| All other events | `CHANNEL_EVENT` | raw dispatch |

---

## GatewayTick Output

`_emit_ticker` normalizes ticker data into a `GatewayTick`:

```python
@dataclass
class GatewayTick:
    timestamp: float          # Unix timestamp (seconds)
    symbol: str              # e.g. "BTC-USDT"
    exchange: str             # Always "OKX"
    asset_type: str           # "SWAP" or "SPOT"
    local_time: float         # Local receive time
    price: float             # Last trade price
    bid_price: float
    ask_price: float
    bid_volume: float
    ask_volume: float
    volume: float             # 24h volume (base asset)
    turnover: float          # 24h turnover (quote asset)
    high_price: float
    low_price: float
    open_price: float
```

---

## Asset Type Normalization

```python
def _normalize_asset_type(raw) -> str:
    # "SWAP" / "SPOT" → as-is
    # "FUTURE" / "FUT" → "SWAP"
    # Default: "SWAP"
```

---

## Rate Limits

The adapter respects OKX rate limits via the feed's `RateLimiter`:

| Endpoint Category | Limit |
|---|---|
| Market data (`/market/*`) | 20 requests / 2s |
| Trading (`/trade/*`) | 60 requests / 2s |
| Account (`/account/*`) | 10 requests / 2s |

---

## 中文

`OkxGatewayAdapter` 提供独立的 OKX 网关接口 — 将 REST API 调用和 WebSocket 流包装成统一的适配器，无需完整 `bt_api` 框架即可独立使用。

### 构造方法

```python
adapter = OkxGatewayAdapter(
    api_key="your_api_key",       # OKX API 密钥
    secret_key="your_secret",     # OKX API 密码
    passphrase="your_passphrase",  # OKX API 口令
    asset_type="SWAP",            # "SWAP"（默认）或 "SPOT"
)
```

### 连接管理

```python
adapter.connect()      # 启动适配器（启动后台线程）
adapter.disconnect()   # 停止适配器并等待后台线程退出
```

### 行情订阅

```python
adapter.subscribe_symbols(["BTC-USDT", "ETH-USDT"])
```

### 查询余额

```python
balance = adapter.get_balance()
# 返回: {"ccy": "USDT", "bal": "1000.0", "frozenBal": "0.0", "availBal": "1000.0"}
```

### 查询持仓

```python
positions = adapter.get_positions()
# 返回: list[dict] — 每个持仓一个 dict
```

### 下单

```python
order = adapter.place_order({
    "symbol": "BTC-USDT",
    "side": "buy",
    "order_type": "limit",
    "price": 67000,
    "volume": 0.001,
})
```

### 撤单

```python
result = adapter.cancel_order({
    "symbol": "BTC-USDT",
    "order_id": "1234567890",
})
```
