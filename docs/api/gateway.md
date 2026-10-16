---
title: ServiceHost boundary | bt_api_okx
---

# OKX direct provider and ServiceHost boundary

The OKX package exposes direct REST/WebSocket feeds and typed container projections. PluginLoader explicitly registers those feeds through register_plugin(registry); importing this package alone does not register a gateway.

The legacy standalone gateway runtime remains in the source tree pending the complete migration, but is retired and unsupported as a public integration. Package-level ticker, symbol/fee, order, position, and fill projections do not provide ServiceHost lifecycle, a complete account observation, or a managed execution session. After the provider is integrated with the host, managed live writes must go through ServiceExecutionSession and service-v2.

See the README, feed reference, and container reference for the supported direct APIs.
