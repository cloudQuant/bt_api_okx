---
title: Home | bt_api_okx
---

<!-- English -->
# bt_api_okx Documentation

[![PyPI Version](https://img.shields.io/pypi/v/bt_api_okx.svg)](https://pypi.org/project/bt_api_okx/)
[![Python Versions](https://img.shields.io/pypi/pyversions/bt_api_okx.svg)](https://pypi.org/project/bt_api_okx/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/cloudQuant/bt_api_okx/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudQuant/bt_api_okx/actions)
[![Docs](https://readthedocs.org/projects/bt-api-okx/badge/?version=latest)](https://bt-api-okx.readthedocs.io/)

## Overview

`bt_api_okx` is the **OKX exchange plugin** for the [bt_api](https://github.com/cloudQuant/bt_api_py) plugin ecosystem. It provides unified REST and WebSocket interfaces for **Spot** and **U本位永续合约 (USDT-M Perpetual Futures)**.

This package is a **runtime plugin dependency** for `bt_api` applications connecting to OKX. It depends on [bt_api_base](https://github.com/cloudQuant/bt_api_base) for core infrastructure (registry, event bus, WebSocket management, caching, rate limiting).

## Key Benefits

- **2 Asset Types**: Spot (`OKX___SPOT`), USDT-M Perpetual (`OKX___SWAP`)
- **11 Mixin Modules**: Market data, trading, account, funding, grid, copy trading, RFQ, spread, statistics, status, sub-accounts
- **18 Container Types**: Comprehensive coverage of all OKX data types
- **Dual API Modes**: Synchronous REST and asynchronous WebSocket streaming
- **Plugin Architecture**: Integrates via `ExchangeRegistry` — auto-registers at import time
- **Gateway Adapter**: `OkxGatewayAdapter` for standalone use without the full bt_api framework
- **Unified Data Model**: All responses normalized to bt_api_base container types
- **HMAC-SHA256 Auth**: Full request signing for authenticated endpoints

## Architecture Overview

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
└── gateway/
    └── adapter.py              # OkxGatewayAdapter(PluginGatewayAdapter)
```

## Supported Exchange Codes

| Exchange Code | Asset Type | REST Base | WSS Base |
|---|---|---|---|
| `OKX___SPOT` | Spot | `https://www.okx.com` | `wss://ws.okx.com:8443/ws/v5/public` |
| `OKX___SWAP` | USDT-M Perpetual | `https://www.okx.com` | `wss://ws.okx.com:8443/ws/v5/public` |

## Quick Start

### Installation

```bash
pip install bt_api_okx
```

Or from source:

```bash
git clone https://github.com/cloudQuant/bt_api_okx
cd bt_api_okx
pip install -e .
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

### bt_api Plugin Integration

```python
from bt_api_py import BtApi

api = BtApi(
    exchange_kwargs={
        "OKX___SWAP": {
            "api_key": "your_key",
            "secret": "your_secret",
            "passphrase": "your_passphrase",
        }
    }
)

ticker = api.get_tick("OKX___SWAP", "BTC-USDT")
balance = api.get_balance("OKX___SWAP")
order = api.make_order(
    exchange_name="OKX___SWAP",
    symbol="BTC-USDT",
    volume=0.001,
    price=67000,
    order_type="limit",
)
```

### WebSocket Subscription

```python
api.subscribe(
    "OKX___SWAP___BTC-USDT",
    [
        {"topic": "ticker", "symbol": "BTC-USDT"},
        {"topic": "depth", "symbol": "BTC-USDT"},
    ],
)

data_queue = api.get_data_queue("OKX___SWAP")
while True:
    msg = data_queue.get(timeout=10)
    print(type(msg).__name__, msg)
```

## API Reference

- [Gateway Adapter](api/gateway.md) — OkxGatewayAdapter standalone entry point
- [Feeds](api/feeds.md) — REST request feeds and WebSocket market/account feeds
- [Exchange Data](api/exchange_data.md) — Exchange configuration classes
- [Containers](api/containers.md) — Normalized data containers

## Online Documentation

| Resource | Link |
|----------|------|
| English Docs | https://bt-api-okx.readthedocs.io/ |
| Chinese Docs | https://bt-api-okx.readthedocs.io/zh/latest/ |
| GitHub Repository | https://github.com/cloudQuant/bt_api_okx |
| Issue Tracker | https://github.com/cloudQuant/bt_api_okx/issues |
| PyPI Package | https://pypi.org/project/bt_api_okx/ |
| bt_api_base Docs | https://bt-api-base.readthedocs.io/ |
| Main Project | https://github.com/cloudQuant/bt_api_py |

---

## 中文

### 概述

`bt_api_okx` 是 [bt_api](https://github.com/cloudQuant/bt_api_py) 插件生态系统的 **OKX 交易所插件**。它为**现货**和**U本位永续合约**提供统一的 REST 和 WebSocket 接口。

本包是 `bt_api` 应用连接 OKX 的**运行时插件依赖**。它依赖 [bt_api_base](https://github.com/cloudQuant/bt_api_base) 提供核心基础设施（注册表、事件总线、WebSocket 管理、缓存、限流）。

### 核心优势

- **2 种资产类型**: 现货 (`OKX___SPOT`)、U本位永续 (`OKX___SWAP`)
- **11 个 Mixin 模块**: 行情数据、交易、账户、资金费率、网格交易、跟单、RFQ、价差交易、统计、状态、子账户
- **18 种容器类型**: 全面覆盖所有 OKX 数据类型
- **双 API 模式**: 同步 REST 和异步 WebSocket 流
- **插件架构**: 通过 `ExchangeRegistry` 集成 — 导入时自动注册
- **网关适配器**: `OkxGatewayAdapter` 无需完整 bt_api 框架即可独立使用
- **统一数据模型**: 所有响应规范化为 bt_api_base 容器类型
- **HMAC-SHA256 认证**: 完整请求签名支持

### 架构

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
└── gateway/
    └── adapter.py              # OkxGatewayAdapter(PluginGatewayAdapter)
```

### 支持的交易所代码

| 交易所代码 | 资产类型 | REST 基础地址 | WSS 基础地址 |
|---|---|---|---|
| `OKX___SPOT` | 现货 | `https://www.okx.com` | `wss://ws.okx.com:8443/ws/v5/public` |
| `OKX___SWAP` | U本位永续 | `https://www.okx.com` | `wss://ws.okx.com:8443/ws/v5/public` |

### 快速开始

```bash
pip install bt_api_okx
```

独立网关适配器使用：

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

bt_api 插件集成：

```python
from bt_api_py import BtApi

api = BtApi(exchange_kwargs={
    "OKX___SWAP": {
        "api_key": "your_key",
        "secret": "your_secret",
        "passphrase": "your_passphrase",
    }
})

ticker = api.get_tick("OKX___SWAP", "BTC-USDT")
```

### API 参考

- [网关适配器](api/gateway.md) — OkxGatewayAdapter 独立入口
- [Feeds](api/feeds.md) — REST 请求 feeds 和 WebSocket 行情/账户 feeds
- [交易所数据](api/exchange_data.md) — 交易所配置类
- [容器](api/containers.md) — 规范化数据容器

### 在线文档

| 资源 | 链接 |
|----------|------|
| 英文文档 | https://bt-api-okx.readthedocs.io/ |
| 中文文档 | https://bt-api-okx.readthedocs.io/zh/latest/ |
| GitHub 仓库 | https://github.com/cloudQuant/bt_api_okx |
| 问题反馈 | https://github.com/cloudQuant/bt_api_okx/issues |
| PyPI 包 | https://pypi.org/project/bt_api_okx/ |
| bt_api_base 文档 | https://bt-api-base.readthedocs.io/ |
| 主项目 | https://github.com/cloudQuant/bt_api_py |
