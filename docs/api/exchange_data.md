---
title: Exchange Data | bt_api_okx
---

# Exchange Data | 交易所数据

`OkxExchangeData` classes provide exchange-specific configuration — REST/WSS URLs, API paths, kline periods, and symbol normalization.

---

## OkxExchangeData (Base Class)

```python
from bt_api_okx.exchange_data import OkxExchangeData, OkxExchangeDataSwap, OkxExchangeDataSpot
```

Base class for all OKX exchange types.

### Configuration Loading

Configuration is loaded lazily from `okx.yaml` via `bt_api_base.config_loader`:

```python
def _get_okx_config() -> Any | None:
    # Loads on first call, cached globally
    config_path = get_exchange_config_path("okx.yaml")
    if config_path.exists():
        _okx_config = load_exchange_config(str(config_path))
    return _okx_config
```

### Default URLs

```python
self.rest_url = "https://www.okx.com"
self.wss_url = "wss://ws.okx.com:8443/ws/v5/public"
self.account_wss_url = "wss://ws.okx.com:8443/ws/v5/private"
self.kline_wss_url = "wss://ws.okx.com:8443/ws/v5/business"
```

### Symbol Normalization

```python
# OKX uses "-" separator, bt_api uses "/"
# Swap: "BTC-USDT" ↔ "BTC/USDT-SWAP"
def get_symbol(self, symbol: str) -> str:
    result = symbol.replace("/", "-").upper()
    if not result.endswith("-SWAP"):
        result += "-SWAP"
    return result

def get_symbol_re(self, symbol) -> str:
    # Reverse: "BTC-USDT-SWAP" → "btc/usdt"
    return symbol.replace("-", "/").lower().rsplit("/", 1)[0]
```

### Kline Periods

Maps bt_api period names to OKX API period codes:

```python
self.kline_periods = {
    "1m": "1m", "3m": "3m", "5m": "5m",
    "15m": "15m", "30m": "30m",
    "1h": "1H", "2h": "2H", "4h": "4H",
    "6h": "6H", "8h": "8H",
    "12h": "12H",
    "1d": "1D", "2d": "2D", "3d": "3D",
    "1w": "1W",
    "1M": "1M", "3M": "3M",
    "6M": "6M", "1y": "1Y",
}
```

### REST Path Access

```python
def get_rest_path(self, key: str, **kwargs) -> str:
    if key not in self.rest_paths or self.rest_paths[key] == "":
        self.raise_path_error(self.exchange_name, key)
    return self.rest_paths[key]
```

### WSS Path Access

Generates OKX WebSocket subscription JSON:

```python
def get_wss_path(self, **kwargs) -> str:
    key = kwargs["topic"]
    kwargs["symbol"] = self.get_symbol(kwargs["symbol"])
    if "period" in kwargs:
        kwargs["period"] = self.get_period(kwargs["period"])

    req = copy.deepcopy(self.wss_paths[key])
    # Substitutes <symbol>, <currency>, <period> in path template
    req = json.dumps(req)
    return req
```

---

## OkxExchangeDataSwap

U本位永续合约 (USDT-M Perpetual Futures).

```python
class OkxExchangeDataSwap(OkxExchangeData):
    """OKX USDT-M Perpetual Swap."""
    # Loads config from 'swap' section of okx.yaml
    # Symbol format: "BTC-USDT-SWAP"
```

---

## OkxExchangeDataSpot

现货 (Spot).

```python
class OkxExchangeDataSpot(OkxExchangeData):
    """OKX Spot Trading."""
    # Loads config from 'spot' section of okx.yaml
    # Symbol format: "BTC-USDT"
```

---

## OkxExchangeDataFutures

到期合约 (Expiry futures).

```python
class OkxExchangeDataFutures(OkxExchangeData):
    """OKX Futures (expiry-based contracts)."""
    # Loads config from 'futures' section of okx.yaml
    # Symbol format: "BTC-USD-futures" (no -SWAP suffix)
```

---

## Configuration Structure (okx.yaml)

```yaml
base_urls:
  rest:
    default: "https://www.okx.com"
  wss:
    public: "wss://ws.okx.com:8443/ws/v5/public"
    private: "wss://ws.okx.com:8443/ws/v5/private"
    business: "wss://ws.okx.com:8443/ws/v5/business"

asset_types:
  swap:
    exchange_name: "OKX"
    rest_paths:
      ticker: "/api/v5/market/ticker"
      orderbook: "/api/v5/market/books"
      bars: "/api/v5/market/candles"
      trades: "/api/v5/market/trades"
      funding_rate: "/api/v5/market/funding-rate"
      mark_price: "/api/v5/market/mark-price"
      open_interest: "/api/v5/market/open-interest"
      instruments: "/api/v5/public/instruments"
    wss_paths:
      tick: '{"args": [{"instId": "<symbol>"}], "op": "subscribe"}'
      depth: '{"args": [{"instId": "<symbol>"}], "op": "subscribe"}'
    kline_periods:
      1m: "1m"
      1h: "1H"
      1d: "1D"

  spot:
    # Similar structure for spot
```

---

## Rate Limit Defaults

| Rule | Limit | Interval | Scope |
|---|---|---|---|
| `okx_general` | 20 req | 2s | `/api/v5/market/*` |
| `okx_trade` | 60 req | 2s | `/api/v5/trade/order` |
| `okx_account` | 10 req | 2s | `/api/v5/account/*` |

---

## 中文

`OkxExchangeData` 类提供交易所特定配置 — REST/WSS URL、API 路径、K线周期和交易对规范化。

### OkxExchangeData（基类）

所有 OKX 交易所类型的基类。

```python
# 符号规范化
# OKX 使用 "-" 分隔符，bt_api 使用 "/"
# 永续: "BTC-USDT" ↔ "BTC/USDT-SWAP"
def get_symbol(self, symbol: str) -> str:
    result = symbol.replace("/", "-").upper()
    if not result.endswith("-SWAP"):
        result += "-SWAP"
    return result
```

### 子类

- `OkxExchangeDataSwap` — U本位永续合约（从 `swap` 配置节加载）
- `OkxExchangeDataSpot` — 现货（从 `spot` 配置节加载）
- `OkxExchangeDataFutures` — 到期合约（从 `futures` 配置节加载）

### K线周期映射

bt_api 周期名称 → OKX API 周期代码：

```python
{"1m": "1m", "1h": "1H", "1d": "1D", ...}
```

### WSS 路径生成

生成 OKX WebSocket 订阅 JSON：

```python
def get_wss_path(self, **kwargs) -> str:
    key = kwargs["topic"]
    kwargs["symbol"] = self.get_symbol(kwargs["symbol"])
    req = copy.deepcopy(self.wss_paths[key])
    # 替换 <symbol>, <currency>, <period>
    return json.dumps(req)
```
