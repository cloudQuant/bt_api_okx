# OKX Documentation

## English

Welcome to the OKX documentation for bt_api.

### Quick Start

```bash
pip install bt_api_okx
```

```python
from bt_api_okx import OKXApi
feed = OKXApi(api_key="your_key", secret="your_secret")
ticker = feed.get_ticker("BTC-USDT")
```

## 中文

欢迎使用 bt_api 的 OKX交易所 文档。

### 快速开始

```bash
pip install bt_api_okx
```

```python
from bt_api_okx import OKXApi
feed = OKXApi(api_key="your_key", secret="your_secret")
ticker = feed.get_ticker("BTC-USDT")
```

## API Reference

See source code in `src/bt_api_okx/` for detailed API documentation.
