---
title: Containers | bt_api_okx
---

# Containers | 数据容器

All OKX data containers normalize exchange responses into bt_api_base unified types. Containers follow a consistent pattern: construct with raw dict or JSON string, call `init_data()` to parse, use typed getter methods.

---

## Order Data

### OkxOrderData

```python
from bt_api_okx.containers.orders.okx_order import OkxOrderData
```

Represents a placed or historical order.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol name (e.g. `"BTC-USDT"`) |
| `order_id` | `str` | Exchange order ID |
| `client_order_id` | `str` | Client-supplied order ID |
| `price` | `float` | Order price |
| `size` | `float` | Order quantity |
| `order_type` | `str` | `"buy-limit"`, `"sell-limit"`, `"buy-market"`, `"sell-market"` |
| `side` | `str` | `"buy"` or `"sell"` |
| `position_side` | `str` | `"long"`, `"short"`, `"both"` (hedge mode) |
| `status` | `str` | Order status |
| `filled_qty` | `float` | Filled quantity |
| `avg_price` | `float` | Average fill price |
| ` rebate` | `float` | Rebate amount |
| `rebate_ccy` | `str` | Rebate currency |

### Key Methods

```python
order = OkxOrderData(raw_dict)
order.init_data()
order.get_order_id()           # str
order.get_client_order_id()    # str
order.get_symbol_name()        # str
order.get_order_status()       # str
order.get_order_side()         # str
order.get_order_price()        # float
order.get_order_size()        # float
order.get_executed_qty()       # float
order.get_all_data()           # dict
```

---

## Ticker Data

### OkxTickerData

```python
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData
```

24-hour rolling ticker data.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol (e.g. `"BTC-USDT"`) |
| `last` | `float` | Last trade price |
| `bid` | `float` | Best bid price |
| `ask` | `float` | Best ask price |
| `bid_volume` | `float` | Best bid quantity |
| `ask_volume` | `float` | Best ask quantity |
| `open_24h` | `float` | 24h open price |
| `high_24h` | `float` | 24h high |
| `low_24h` | `float` | 24h low |
| `vol_24h` | `float` | 24h volume (base asset) |
| `vol_ccy_24h` | `float` | 24h turnover (quote asset) |
| `server_time` | `float` | Server timestamp (ms) |

### Key Methods

```python
ticker = OkxTickerData(raw_dict)
ticker.init_data()
ticker.get_last_price()       # float
ticker.get_bid_price()       # float
ticker.get_ask_price()        # float
ticker.get_bid_volume()       # float
ticker.get_ask_volume()       # float
ticker.get_vol_24h()          # float
ticker.get_vol_ccy_24h()     # float
ticker.get_high_24h()         # float
ticker.get_low_24h()          # float
ticker.get_open_24h()        # float
ticker.get_server_time()      # float
ticker.get_symbol_name()      # str
```

---

## Trade Data

### OkxWssTradeData

Real-time trade data from WebSocket.

```python
from bt_api_okx.containers.trades.okx_trade import OkxWssTradeData, OkxWssFillsData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `trade_id` | `str` | Trade ID |
| `order_id` | `str` | Related order ID |
| `price` | `float` | Trade price |
| `volume` | `float` | Trade quantity |
| `side` | `str` | `"buy"` or `"sell"` |
| `timestamp` | `float` | Trade timestamp (ms) |

### OkxWssFillsData

User's own trade fills from account WebSocket.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `trade_id` | `str` | Fill ID |
| `order_id` | `str` | Related order ID |
| `price` | `float` | Fill price |
| `volume` | `float` | Fill quantity |
| `side` | `str` | `"buy"` or `"sell"` |
| `fee` | `float` | Fee paid |
| `fee_ccy` | `str` | Fee currency |
| `timestamp` | `float` | Fill timestamp (ms) |

---

## Bar Data

### OkxBarData

```python
from bt_api_okx.containers.bars.okx_bar import OkxBarData
```

K-line / candlestick data.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `timestamp` | `float` | Bar open timestamp (ms) |
| `open` | `float` | Open price |
| `high` | `float` | High price |
| `low` | `float` | Low price |
| `close` | `float` | Close price |
| `volume` | `float` | Base asset volume |
| `quote_volume` | `float` | Quote asset volume |
| `close_time` | `float` | Bar close timestamp (ms) |

---

## Balance Data

### OkxBalanceData

```python
from bt_api_okx.containers.balance.okx_balance import OkxBalanceData
```

Account balance and valuation.

| Field | Type | Description |
|-------|------|-------------|
| `total_eq` | `float` | Total equity (USD) |
| `btc_eq` | `float` | BTC equivalent |
| `avail_bal` | `float` | Available balance |
| `frozen_bal` | `float` | Frozen/locked balance |
| `server_time` | `float` | Timestamp (ms) |

---

## Position Data

### OkxPositionData

```python
from bt_api_okx.containers.positions.okx_position import OkxPositionData
```

Futures / margin position.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Position symbol |
| `side` | `str` | `"long"` or `"short"` |
| `size` | `float` | Position size |
| `available` | `float` | Available to close |
| `avg_price` | `float` | Average entry price |
| `notional_value` | `float` | Position notional value |
| `leverage` | `float` | Leverage multiplier |
| `unrealized_pnl` | `float` | Unrealized PnL |
| `realized_pnl` | `float` | Realized PnL |
| `margin` | `float` | Position margin |
| `margin_mode` | `str` | `"cross"` or `"isolated"` |
| `position_mode` | `str` | `"long_short"` or `"net"` |

---

## Funding Rate Data

### OkxFundingRateData

```python
from bt_api_okx.containers.funding_rates.okx_funding_rate import OkxFundingRateData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `funding_rate` | `float` | Current funding rate |
| `funding_time` | `float` | Next funding time (ms) |
| `mark_price` | `float` | Mark price |
| `index_price` | `float` | Index price |

---

## Mark Price Data

### OkxMarkPriceData

```python
from bt_api_okx.containers.mark_prices.okx_mark_price import OkxMarkPriceData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `mark_price` | `float` | Mark price |
| `timestamp` | `float` | Timestamp (ms) |

---

## Open Interest Data

### OkxOpenInterestData

```python
from bt_api_okx.containers.open_interest.okx_open_interest import OkxOpenInterestData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `open_interest` | `float` | Open interest (contracts or USD) |
| `timestamp` | `float` | Timestamp (ms) |

---

## Order Book Data

### OkxOrderBookData

```python
from bt_api_okx.containers.orderbooks.okx_orderbook import OkxOrderBookData, OkxL2OrderBookData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `timestamp` | `float` | Timestamp (ms) |
| `asks` | `List[Tuple[float, float]]` | Ask levels `[[price, qty], ...]` |
| `bids` | `List[Tuple[float, float]]` | Bid levels `[[price, qty], ...]` |
| `seq` | `int` | Sequence number |

---

## Symbol Data

### OkxSymbolData

```python
from bt_api_okx.containers.symbols.okx_symbol import OkxSymbolData
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Full symbol (e.g. `"BTC-USDT"`) |
| `base_asset` | `str` | Base asset (e.g. `"BTC"`) |
| `quote_asset` | `str` | Quote asset (e.g. `"USDT"`) |
| `price_precision` | `int` | Price decimal places |
| `qty_precision` | `int` | Quantity decimal places |
| `min_size` | `float` | Minimum order quantity |
| `tick_size` | `float` | Price tick size |

---

## Liquidation Data

### OkxLiquidationOrderData

```python
from bt_api_okx.containers.liquidations.okx_liquidation_order import (
    OkxLiquidationOrderData,
    OkxLiquidationWarningData,
)
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol |
| `side` | `str` | `"buy"` or `"sell"` |
| `price` | `float` | Liquidation price |
| `size` | `float` | Liquidation quantity |
| `timestamp` | `float` | Timestamp (ms) |

---

## Greek Data

### OkxAccountGreeksData

```python
from bt_api_okx.containers.greeks.okx_greeks import OkxAccountGreeksData
```

| Field | Type | Description |
|-------|------|-------------|
| `delta` | `float` | Position delta |
| `gamma` | `float` | Position gamma |
| `theta` | `float` | Position theta |
| `vega` | `float` | Position vega |

---

## All Containers

| Class | File |
|-------|------|
| `OkxOrderData` | `containers/orders/okx_order.py` |
| `OkxTickerData` | `containers/tickers/okx_ticker.py` |
| `OkxTradeData` | `containers/trades/okx_trade.py` |
| `OkxWssTradeData` | `containers/trades/okx_trade.py` |
| `OkxWssFillsData` | `containers/trades/okx_trade.py` |
| `OkxBarData` | `containers/bars/okx_bar.py` |
| `OkxBalanceData` | `containers/balance/okx_balance.py` |
| `OkxPositionData` | `containers/positions/okx_position.py` |
| `OkxFundingRateData` | `containers/funding_rates/okx_funding_rate.py` |
| `OkxMarkPriceData` | `containers/mark_prices/okx_mark_price.py` |
| `OkxOpenInterestData` | `containers/open_interest/okx_open_interest.py` |
| `OkxOrderBookData` | `containers/orderbooks/okx_orderbook.py` |
| `OkxL2OrderBookData` | `containers/orderbooks/okx_orderbook.py` |
| `OkxSymbolData` | `containers/symbols/okx_symbol.py` |
| `OkxLiquidationOrderData` | `containers/liquidations/okx_liquidation_order.py` |
| `OkxLiquidationWarningData` | `containers/liquidations/okx_liquidation_order.py` |
| `OkxAccountGreeksData` | `containers/greeks/okx_greeks.py` |

---

## Container Usage Pattern

```python
from bt_api_okx.containers.tickers.okx_ticker import OkxTickerData

# Method 1: dict input
ticker = OkxTickerData({"instId": "BTC-USDT", "last": "67000.0", ...})
ticker.init_data()
print(ticker.get_last_price())  # 67000.0

# Method 2: JSON string input
ticker2 = OkxTickerData('{"instId": "BTC-USDT", "last": "67000.0", ...}', has_been_json_encoded=True)
ticker2.init_data()

# Get all normalized fields
data = ticker.get_all_data()
# {'symbol': 'BTC-USDT', 'last': 67000.0, 'bid': ..., 'ask': ...}
```

---

## 中文

所有 OKX 数据容器将交易所响应规范化为 bt_api_base 统一类型。容器遵循一致的构造模式：用原始 dict 或 JSON 字符串构造，调用 `init_data()` 解析，使用类型化的 getter 方法访问。

### 订单数据 (OkxOrderData)

订单状态和成交数据。

```python
order = OkxOrderData(raw_dict)
order.init_data()
order.get_order_id()
order.get_symbol_name()
order.get_order_status()
order.get_executed_qty()
```

### 行情数据 (OkxTickerData)

24小时滚动行情。

```python
ticker = OkxTickerData(raw_dict)
ticker.init_data()
ticker.get_last_price()
ticker.get_bid_price()
ticker.get_ask_price()
ticker.get_vol_24h()
```

### 成交数据 (OkxWssTradeData / OkxWssFillsData)

实时成交和用户成交明细。

### K线数据 (OkxBarData)

蜡烛图/K线数据。

### 余额数据 (OkxBalanceData)

账户余额和估值。

### 持仓数据 (OkxPositionData)

合约/杠杆持仓。

### 资金费率 (OkxFundingRateData)

永续合约资金费率。

### 标记价格 (OkxMarkPriceData)

合约标记价格。

### 持仓量 (OkxOpenInterestData)

合约持仓量。

### 订单簿 (OkxOrderBookData / OkxL2OrderBookData)

订单簿深度数据。

### 交易对元数据 (OkxSymbolData)

交易对规格（精度、最小数量等）。

### 强平数据 (OkxLiquidationOrderData / OkxLiquidationWarningData)

强平订单和强平预警。

### 希腊值 (OkxAccountGreeksData)

期权希腊值数据。

### 通用使用模式

```python
ticker = OkxTickerData(raw_dict)
ticker.init_data()
print(ticker.get_last_price())
data = ticker.get_all_data()  # 获取所有规范化字段
```
