# bt_api_okx

OKX exchange package for `bt_api`.

- The plugin entrypoint is `bt_api_okx.plugin:register_plugin`.
- Core exchange registration and gateway adapter are delegated to existing `bt_api_py` implementations during transition.
- Exchange runtime adapter is `bt_api_py.gateway.adapters.okx_adapter.OkxGatewayAdapter`.

Install and run:

```bash
pip install -e packages/bt_api_okx
```

`bt_api_py` will auto-discover this plugin on startup through the
`bt_api_py.plugins` entry-point group.
