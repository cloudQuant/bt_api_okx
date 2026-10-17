---
title: ServiceHost boundary | bt_api_okx
---

# OKX provider and ServiceHost boundary

The legacy `OkxGatewayAdapter` runtime wrapper and export have been removed. The direct OKX request feeds and typed exchange containers remain available through the plugin registry. OKX's managed market providers support the configured SWAP ticker and bar-history contracts; they do not provide an account-session or ServiceHost order-entry adapter. Raw feed methods remain direct APIs and are not a managed ServiceHost session.
