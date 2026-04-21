# bt_api_okx

[![PyPI Version](https://img.shields.io/pypi/v/bt_api_okx.svg)](https://pypi.org/project/bt_api_okx/)
[![Python Versions](https://img.shields.io/pypi/pyversions/bt_api_okx.svg)](https://pypi.org/project/bt_api_okx/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/cloudQuant/bt_api_okx/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudQuant/bt_api_okx/actions)
[![Docs](https://readthedocs.org/projects/bt-api-okx/badge/?version=latest)](https://bt-api-okx.readthedocs.io/)

---

<!-- English -->
# bt_api_okx

> **OKX exchange plugin for bt_api** — Unified REST and WebSocket API for **Spot** and **U本位永续合约 (USDT-M Perpetual Futures)**.

`bt_api_okx` is a runtime plugin for [bt_api](https://github.com/cloudQuant/bt_api_py) that connects to **OKX** exchange. It depends on [bt_api_base](https://github.com/cloudQuant/bt_api_base) for core infrastructure. It also ships `OkxGatewayAdapter` for **standalone use** without the full bt_api framework.

| Resource | Link |
|----------|------|
| English Docs | https://bt-api-okx.readthedocs.io/ |
| Chinese Docs | https://bt-api-okx.readthedocs.io/zh/latest/ |
| GitHub | https://github.com/cloudQuant/bt_api_okx |
| PyPI | https://pypi.org/project/bt_api_okx/ |
| Issues | https://github.com/cloudQuant/bt_api_okx/issues |
| bt_api_base | https://bt-api-base.readthedocs.io/ |
| Main Project | https://github.com/cloudQuant/bt_api_py |

---

## Features

### 2 Asset Types

| Asset Type | Code | REST | WebSocket | Description |
|---|---|---|---|---|
| Spot | `OKX___SPOT` | ✅ | ✅ | Spot trading |
| USDT-M Perpetual | `OKX___SWAP` | ✅ | ✅ | U本位永续合约 |

### 11 Mixin Modules

`OkxRequestData` inherits capabilities from 11 focused mixins:

| Mixin | Capabilities |
|---|---|
| `MarketDataMixin` | Ticker, depth, kline, funding rate, mark price, open interest, instruments, index/insurance/fee |
| `TradeMixin` | Place order, amend, cancel, query open orders, order history, deals, algo orders, batch orders |
| `AccountMixin` | Account info, balance, positions, margin config, fee, max order size |
| `TradingAccountMixin` | Leverage, margin type, position mode |
| `FundingMixin` | Funding rate history |
| `GridTradingMixin` | Grid trading |
| `CopyTradingMixin` | Copy trading |
| `RfqMixin` | Request for Quote |
| `SpreadTradingMixin` | Spread trading |
| `StatisticsMixin` | Trading statistics |
| `StatusMixin` | System status |
| `SubAccountMixin` | Sub-account management |

### Dual API Modes

- **REST API** — Synchronous polling for order management, balance queries, historical data
- **WebSocket API** — Real-time streaming for ticker, order book, k-lines, trades, account updates

### Plugin Architecture

Auto-registers at import time via `ExchangeRegistry`. Works seamlessly with `BtApi`:

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "OKX___SPOT": {
        "api_key": "your_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase",
    }
})

ticker = api.get_tick("OKX___SPOT", "BTC-USDT")
balance = api.get_balance("OKX___SPOT")
order = api.make_order(exchange_name="OKX___SPOT", symbol="BTC-USDT", volume=0.001, price=67000, order_type="limit")
```

### Standalone Gateway Adapter

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(
    api_key="your_api_key",
    secret_key="your_secret",
    passphrase="your_passphrase",
    asset_type="SWAP",  # or "SPOT"
)
adapter.connect()
adapter.subscribe_symbols(["BTC-USDT", "ETH-USDT"])

# get_balance, get_positions, place_order, cancel_order...
```

### Unified Data Containers

All exchange responses normalized to bt_api_base container types:

- `OkxTickerData` / `TickContainer` — 24hr rolling ticker
- `OkxOrderBookData` / `OrderBookContainer` — Order book depth
- `OkxBarData` / `BarContainer` — K-line/candlestick
- `OkxTradeData` / `TradeContainer` — Individual trades
- `OkxOrderData` / `OrderContainer` — Order status and fills
- `OkxPositionData` / `PositionContainer` — Futures positions
- `OkxBalanceData` / `AccountBalanceContainer` — Asset balances
- `OkxFundingRateData` / `FundingRateContainer` — Perpetual funding rate
- `OkxMarkPriceData` / `MarkPriceContainer` — Mark price
- `OkxOpenInterestData` / `OpenInterestContainer` — Open interest
- `OkxSymbolData` / `SymbolContainer` — Symbol metadata
- Plus 8 more specialized containers

---

## Installation

### From PyPI (Recommended)

```bash
pip install bt_api_okx
```

### From Source

```bash
git clone https://github.com/cloudQuant/bt_api_okx
cd bt_api_okx
pip install -e .
```

### Requirements

- Python `3.9` – `3.14`
- `bt_api_base >= 0.15`
- `requests` for HTTP client
- `websocket-client` for WebSocket client
- `aiohttp` for async HTTP client

---

## Quick Start

### 1. Install

```bash
pip install bt_api_okx
```

### 2. Get ticker (public — no API key needed)

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(asset_type="SPOT")
adapter.connect()
adapter.subscribe_symbols(["BTC-USDT"])
# Use adapter.poll_output() or BtApi.get_data_queue() to receive data
```

### 3. Place an order (requires API key)

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(
    api_key="your_api_key",
    secret_key="your_secret",
    passphrase="your_passphrase",
    asset_type="SWAP",
)
adapter.connect()

order = adapter.place_order({
    "symbol": "BTC-USDT",
    "side": "buy",
    "order_type": "limit",
    "price": 67000,
    "volume": 0.001,
})
print(f"Order placed: {order}")
```

### 4. bt_api Plugin Integration

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "OKX___SWAP": {
        "api_key": "your_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase",
    }
})

# REST calls
ticker = api.get_tick("OKX___SWAP", "BTC-USDT")
balance = api.get_balance("OKX___SWAP")

# WebSocket subscription
api.subscribe("OKX___SWAP___BTC-USDT", [
    {"topic": "ticker", "symbol": "BTC-USDT"},
    {"topic": "depth", "symbol": "BTC-USDT"},
])
queue = api.get_data_queue("OKX___SWAP")
msg = queue.get(timeout=10)
```

---

## Architecture

```
bt_api_okx/
├── plugin.py                     # register_plugin() — bt_api plugin entry point
├── registry_registration.py      # register_okx() — feeds / exchange_data / balance_handler registration
├── exchange_data/
│   └── okx_exchange_data.py     # OkxExchangeData (base) + Spot / Swap / Futures subclasses
├── feeds/live_okx/
│   ├── request_base.py          # OkxRequestData — inherits 11 mixins, all REST API methods
│   ├── spot.py                  # OkxRequestDataSpot, OkxMarketWssDataSpot, OkxAccountWssDataSpot
│   ├── swap.py                  # OkxRequestDataSwap, OkxMarketWssDataSwap, OkxAccountWssDataSwap
│   ├── account_wss_base.py      # Account WSS base class
│   ├── market_wss_base.py       # Market WSS base class
│   └── mixins/                  # 11 mixins: market_data, trade, account, funding, etc.
├── containers/                   # 18 normalized data container types
│   ├── orders/                  # OkxOrderData
│   ├── tickers/                 # OkxTickerData
│   ├── trades/                  # OkxTradeData, OkxWssFillsData, OkxWssTradeData
│   ├── bars/                    # OkxBarData
│   ├── balance/                 # OkxBalanceData
│   ├── positions/                # OkxPositionData
│   ├── funding_rates/           # OkxFundingRateData
│   ├── mark_prices/             # OkxMarkPriceData
│   ├── open_interest/           # OkxOpenInterestData
│   ├── orderbooks/              # OkxOrderBookData, OkxL2OrderBookData
│   ├── assets/                  # OkxAssetData, OkxCurrencyData, OkxBalanceData
│   ├── liquidations/            # OkxLiquidationOrderData, OkxLiquidationWarningData
│   ├── greeks/                  # OkxAccountGreeksData
│   ├── symbols/                 # OkxSymbolData
│   └── price_limits/            # OkxPriceLimitData
└── gateway/
    └── adapter.py              # OkxGatewayAdapter(PluginGatewayAdapter)
```

---

## Supported Operations

| Category | Operation | Notes |
|---|---|---|
| **Market Data** | `get_ticker` | 24hr rolling ticker |
| | `get_orderbook` | Order book depth |
| | `get_bars` | K-line/candlestick (1m–1M) |
| | `get_trades` | Recent trade history |
| | `get_funding_rate` | Futures only |
| | `get_mark_price` | Futures only |
| | `get_open_interest` | Futures only |
| **Account** | `get_balance` | All asset balances |
| | `get_account` | Full account info |
| | `get_position` | Futures/Spot positions |
| | `get_open_orders` | All open orders |
| | `get_order` | Single order by ID |
| **Trading** | `make_order` | LIMIT/MARKET/STOP variants |
| | `cancel_order` | Cancel single order |
| | `cancel_orders` | Cancel all open orders |
| | `set_leverage` | Futures only |
| | `set_margin_type` | Cross/isolated |
| | `set_position_mode` | Hedge mode |
| **WebSocket** | `subscribe_symbols` | Market data streams |
| | `poll_output` | Blocking/non-blocking output poll |
| | `get_balance` | Account balance via WSS |
| | `get_positions` | Positions via WSS |

---

## Supported OKX Symbols

All OKX trading pairs are supported, including:

- **Spot**: `BTC-USDT`, `ETH-USDT`, `SOL-USDT`, `XRP-USDT` ...
- **USDT-M Perpetual**: `BTC-USDT-SWAP`, `ETH-USDT-SWAP`, `SOL-USDT-SWAP` ...

---

## Error Handling

All OKX API errors are translated to bt_api_base `ApiError` subclasses via `OKXErrorTranslator`.

---

## Rate Limits

| Endpoint Category | Limit |
|---|---|
| Market data (`/market/*`) | 20 requests / 2s (sliding window) |
| Trading (`/trade/*`) | 60 requests / 2s |
| Account (`/account/*`) | 10 requests / 2s |

---

## Documentation

| Doc | Link |
|-----|------|
| **English** | https://bt-api-okx.readthedocs.io/ |
| **中文** | https://bt-api-okx.readthedocs.io/zh/latest/ |
| API Reference | https://bt-api-okx.readthedocs.io/api/client/ |
| bt_api_base | https://bt-api-base.readthedocs.io/ |
| Main Project | https://cloudquant.github.io/bt_api_py/ |

---

## License

MIT — see [LICENSE](LICENSE).

---

## Support

- [GitHub Issues](https://github.com/cloudQuant/bt_api_okx/issues) — bug reports, feature requests
- Email: yunjinqi@gmail.com

---

---

## 中文

> **bt_api 的 OKX 交易所插件** — 为**现货**和**U本位永续合约**提供统一的 REST 和 WebSocket API。

`bt_api_okx` 是 [bt_api](https://github.com/cloudQuant/bt_api_py) 的运行时插件，连接 **OKX** 交易所。依赖 [bt_api_base](https://github.com/cloudQuant/bt_api_base) 提供核心基础设施。同时提供 `OkxGatewayAdapter`，可**独立使用**无需完整 bt_api 框架。

| 资源 | 链接 |
|------|------|
| 英文文档 | https://bt-api-okx.readthedocs.io/ |
| 中文文档 | https://bt-api-okx.readthedocs.io/zh/latest/ |
| GitHub | https://github.com/cloudQuant/bt_api_okx |
| PyPI | https://pypi.org/project/bt_api_okx/ |
| 问题反馈 | https://github.com/cloudQuant/bt_api_okx/issues |
| bt_api_base | https://bt-api-base.readthedocs.io/ |
| 主项目 | https://github.com/cloudQuant/bt_api_py |

---

## 功能特点

### 2 种资产类型

| 资产类型 | 代码 | REST | WebSocket | 说明 |
|---|---|---|---|---|
| 现货 | `OKX___SPOT` | ✅ | ✅ | 现货交易 |
| U本位永续 | `OKX___SWAP` | ✅ | ✅ | USDT 保证金永续合约 |

### 11 个 Mixin 模块

`OkxRequestData` 继承 11 个专注领域的 mixin：

| Mixin | 提供的功能 |
|---|---|
| `MarketDataMixin` | 行情、深度、K线、资金费率、标记价格、持仓量、交易对信息、指数/保险/费率 |
| `TradeMixin` | 下单、改单、撤单、查询挂单、订单历史、成交记录、算法单、批量下单 |
| `AccountMixin` | 账户信息、余额、持仓、保证金配置、费率、最大下单量 |
| `TradingAccountMixin` | 杠杆、保证金类型、持仓模式 |
| `FundingMixin` | 资金费率历史 |
| `GridTradingMixin` | 网格交易 |
| `CopyTradingMixin` | 跟单交易 |
| `RfqMixin` | 报价请求 |
| `SpreadTradingMixin` | 价差交易 |
| `StatisticsMixin` | 交易统计 |
| `StatusMixin` | 系统状态 |
| `SubAccountMixin` | 子账户管理 |

### 双 API 模式

- **REST API** — 同步轮询：订单管理、余额查询、历史数据
- **WebSocket API** — 实时流：行情、订单簿、K线、交易、账户更新

### 插件架构

通过 `ExchangeRegistry` 在导入时自动注册，与 `BtApi` 无缝协作：

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "OKX___SPOT": {
        "api_key": "your_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase",
    }
})

ticker = api.get_tick("OKX___SPOT", "BTC-USDT")
balance = api.get_balance("OKX___SPOT")
order = api.make_order(exchange_name="OKX___SPOT", symbol="BTC-USDT", volume=0.001, price=67000, order_type="limit")
```

### 独立网关适配器

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(
    api_key="your_api_key",
    secret_key="your_secret",
    passphrase="your_passphrase",
    asset_type="SWAP",  # 或 "SPOT"
)
adapter.connect()
adapter.subscribe_symbols(["BTC-USDT", "ETH-USDT"])

# get_balance, get_positions, place_order, cancel_order...
```

### 统一数据容器

所有交易所响应规范化为 bt_api_base 容器类型：

- `OkxTickerData` / `TickContainer` — 24小时滚动行情
- `OkxOrderBookData` / `OrderBookContainer` — 订单簿深度
- `OkxBarData` / `BarContainer` — K线/蜡烛图
- `OkxTradeData` / `TradeContainer` — 逐笔成交
- `OkxOrderData` / `OrderContainer` — 订单状态和成交
- `OkxPositionData` / `PositionContainer` — 合约持仓
- `OkxBalanceData` / `AccountBalanceContainer` — 资产余额
- `OkxFundingRateData` / `FundingRateContainer` — 永续资金费率
- `OkxMarkPriceData` / `MarkPriceContainer` — 标记价格
- `OkxOpenInterestData` / `OpenInterestContainer` — 持仓量
- `OkxSymbolData` / `SymbolContainer` — 交易对元数据
- 以及其他 8 种专业容器类型

---

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install bt_api_okx
```

### 从源码安装

```bash
git clone https://github.com/cloudQuant/bt_api_okx
cd bt_api_okx
pip install -e .
```

### 系统要求

- Python `3.9` – `3.14`
- `bt_api_base >= 0.15`
- `requests` HTTP 客户端
- `websocket-client` WebSocket 客户端
- `aiohttp` 异步 HTTP 客户端

---

## 快速开始

### 1. 安装

```bash
pip install bt_api_okx
```

### 2. 获取行情（公开接口，无需 API key）

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(asset_type="SPOT")
adapter.connect()
adapter.subscribe_symbols(["BTC-USDT"])
# 使用 adapter.poll_output() 或 BtApi.get_data_queue() 接收数据
```

### 3. 下单交易（需要 API key）

```python
from bt_api_okx import OkxGatewayAdapter

adapter = OkxGatewayAdapter(
    api_key="your_api_key",
    secret_key="your_secret",
    passphrase="your_passphrase",
    asset_type="SWAP",
)
adapter.connect()

order = adapter.place_order({
    "symbol": "BTC-USDT",
    "side": "buy",
    "order_type": "limit",
    "price": 67000,
    "volume": 0.001,
})
print(f"订单已下单: {order}")
```

### 4. bt_api 插件集成

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "OKX___SWAP": {
        "api_key": "your_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase",
    }
})

# REST 调用
ticker = api.get_tick("OKX___SWAP", "BTC-USDT")
balance = api.get_balance("OKX___SWAP")

# WebSocket 订阅
api.subscribe("OKX___SWAP___BTC-USDT", [
    {"topic": "ticker", "symbol": "BTC-USDT"},
    {"topic": "depth", "symbol": "BTC-USDT"},
])
queue = api.get_data_queue("OKX___SWAP")
msg = queue.get(timeout=10)
```

---

## 架构

```
bt_api_okx/
├── plugin.py                     # register_plugin() — bt_api 插件入口
├── registry_registration.py      # register_okx() — feeds / exchange_data / balance_handler 注册
├── exchange_data/
│   └── okx_exchange_data.py     # OkxExchangeData（基类）+ Spot / Swap / Futures 子类
├── feeds/live_okx/
│   ├── request_base.py          # OkxRequestData — 继承 11 个 mixin，全部 REST API 方法
│   ├── spot.py                  # OkxRequestDataSpot, OkxMarketWssDataSpot, OkxAccountWssDataSpot
│   ├── swap.py                  # OkxRequestDataSwap, OkxMarketWssDataSwap, OkxAccountWssDataSwap
│   ├── account_wss_base.py      # 账户 WSS 基类
│   ├── market_wss_base.py       # 行情 WSS 基类
│   └── mixins/                  # 11 个 mixin: market_data, trade, account, funding 等
├── containers/                   # 18 种规范化数据容器类型
│   ├── orders/                  # OkxOrderData
│   ├── tickers/                 # OkxTickerData
│   ├── trades/                  # OkxTradeData, OkxWssFillsData, OkxWssTradeData
│   ├── bars/                    # OkxBarData
│   ├── balance/                 # OkxBalanceData
│   ├── positions/                # OkxPositionData
│   ├── funding_rates/           # OkxFundingRateData
│   ├── mark_prices/             # OkxMarkPriceData
│   ├── open_interest/           # OkxOpenInterestData
│   ├── orderbooks/              # OkxOrderBookData, OkxL2OrderBookData
│   ├── assets/                  # OkxAssetData, OkxCurrencyData, OkxBalanceData
│   ├── liquidations/            # OkxLiquidationOrderData, OkxLiquidationWarningData
│   ├── greeks/                  # OkxAccountGreeksData
│   ├── symbols/                 # OkxSymbolData
│   └── price_limits/            # OkxPriceLimitData
└── gateway/
    └── adapter.py              # OkxGatewayAdapter(PluginGatewayAdapter)
```

---

## 支持的操作

| 类别 | 操作 | 说明 |
|---|---|---|
| **行情数据** | `get_ticker` | 24小时滚动行情 |
| | `get_orderbook` | 订单簿深度 |
| | `get_bars` | K线/蜡烛图（1m–1M） |
| | `get_trades` | 近期成交历史 |
| | `get_funding_rate` | 仅合约 |
| | `get_mark_price` | 仅合约 |
| | `get_open_interest` | 仅合约 |
| **账户** | `get_balance` | 所有资产余额 |
| | `get_account` | 完整账户信息 |
| | `get_position` | 合约/现货持仓 |
| | `get_open_orders` | 所有挂单 |
| | `get_order` | 按ID查询单笔订单 |
| **交易** | `make_order` | 限价/市价/止损 及其变体 |
| | `cancel_order` | 撤销单笔订单 |
| | `cancel_orders` | 撤销所有挂单 |
| | `set_leverage` | 仅合约 |
| | `set_margin_type` | 全仓/逐仓 |
| | `set_position_mode` | 双向持仓模式 |
| **WebSocket** | `subscribe_symbols` | 行情数据流订阅 |
| | `poll_output` | 阻塞/非阻塞输出轮询 |
| | `get_balance` | 通过 WSS 获取账户余额 |
| | `get_positions` | 通过 WSS 获取持仓 |

---

## 支持的 OKX 交易对

全部 OKX 交易对均支持，包括：

- **现货**: `BTC-USDT`, `ETH-USDT`, `SOL-USDT`, `XRP-USDT` ...
- **U本位永续**: `BTC-USDT-SWAP`, `ETH-USDT-SWAP`, `SOL-USDT-SWAP` ...

---

## 错误处理

所有 OKX API 错误均通过 `OKXErrorTranslator` 翻译为 bt_api_base `ApiError` 子类。

---

## 限流配置

| 端点类别 | 限制 |
|---|---|
| 行情数据 (`/market/*`) | 20 请求 / 2秒（滑动窗口） |
| 交易 (`/trade/*`) | 60 请求 / 2秒 |
| 账户 (`/account/*`) | 10 请求 / 2秒 |

---

## 文档

| 文档 | 链接 |
|-----|------|
| **英文文档** | https://bt-api-okx.readthedocs.io/ |
| **中文文档** | https://bt-api-okx.readthedocs.io/zh/latest/ |
| API 参考 | https://bt-api-okx.readthedocs.io/api/client/ |
| bt_api_base | https://bt-api-base.readthedocs.io/ |
| 主项目 | https://cloudquant.github.io/bt_api_py/ |

---

## 许可证

MIT — 详见 [LICENSE](LICENSE)。

---

## 技术支持

- [GitHub Issues](https://github.com/cloudQuant/bt_api_okx/issues) — bug 报告、功能请求
- 邮箱: yunjinqi@gmail.com
