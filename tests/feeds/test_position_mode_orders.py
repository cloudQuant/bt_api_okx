"""Long/short closes preserve position identity and native contract size."""

import pytest
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap


@pytest.mark.parametrize("side,position_side", [("sell", "long"), ("buy", "short")])
def test_hedge_close_parameters(side, position_side):
    feed = OkxRequestDataSwap(None, environment="demo")
    try:
        _, params, _ = feed._make_order(
            "BTC-USDT-SWAP",
            0.2,
            price=60000,
            order_type=side + "-limit",
            offset="close",
            position_side=position_side,
            reduce_only=True,
            size_in_contracts=True,
            time_in_force="IOC",
        )
        assert params["side"] == side and params["posSide"] == position_side
        assert params["sz"] == "0.2" and params["ordType"] == "ioc"
        assert params["reduceOnly"] == "true"
    finally:
        feed._http_client.close()


def test_net_close_retains_reduce_only():
    feed = OkxRequestDataSwap(None, environment="demo")
    try:
        _, params, _ = feed._make_order(
            "BTC-USDT-SWAP",
            0.2,
            price=60000,
            order_type="sell-limit",
            offset="close",
            position_side="net",
            reduce_only=True,
            size_in_contracts=True,
        )
        assert params["reduceOnly"] == "true"
    finally:
        feed._http_client.close()
