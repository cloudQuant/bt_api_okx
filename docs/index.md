---
title: Home | bt_api_okx
---

# bt_api_okx Documentation

## English

bt_api_okx provides direct REST and WebSocket provider feeds for OKX Spot and USDT-margined perpetual futures. PluginLoader explicitly calls register_plugin(registry) to register feed classes; importing the package alone does not mutate a registry.

Direct package projections include ticker mappings from OkxTickerData, instrument/fee metadata from OkxRequestDataSpot or OkxRequestDataSwap, and normalized order, position, and trade container fields. These projections do not establish ServiceHost lifecycle, a complete account observation, or managed execution.

After the provider is integrated with the host, managed live writes must use ServiceExecutionSession through service-v2. The legacy standalone gateway runtime remains in the source tree pending the complete migration, but is retired and unsupported as a public integration. See the README for installation and BtApi usage, and the feeds and containers references for direct package APIs.

## 中文

bt_api_okx 提供面向 OKX 现货和 U 本位永续合约的 REST/WebSocket 直连 provider feed。PluginLoader 会显式调用 register_plugin(registry) 注册 feed 类；单独导入包不会修改注册表。

包级直连投影包括 OkxTickerData 的行情映射、OkxRequestDataSpot 或 OkxRequestDataSwap 的合约/费率元数据，以及订单、持仓和成交容器的规范化字段。这些投影不代表 ServiceHost 生命周期、完整账户观察或托管执行已接入。

provider 完成宿主集成后，托管实盘写操作应通过 service-v2 的 ServiceExecutionSession。完整迁移尚未完成，旧的独立 gateway runtime 仍保留在源码树中，但已退役，不再作为受支持的公共集成接口。安装和 BtApi 使用方式见 README；直连 API 见 feeds 与 containers 参考。
