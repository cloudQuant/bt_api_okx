"""Tests for OKX position module."""

from __future__ import annotations

import pytest

from bt_api_okx.containers.positions.okx_position import OkxPositionData


class TestOkxPositionData:
    """Tests for OkxPositionData class."""

    def test_init(self):
        """Test initialization."""
        position = OkxPositionData(
            {"instId": "BTC-USDT-SWAP"},
            symbol_name="BTC-USDT-SWAP",
            asset_type="FUTURE",
            has_been_json_encoded=True,
        )

        assert position.exchange_name == "OKX"
        assert position.symbol_name == "BTC-USDT-SWAP"
        assert position.asset_type == "FUTURE"

    def test_init_data(self):
        """Test init_data method."""
        position_info = {
            "uTime": "1705315800000",
            "mgnMode": "cross",
            "lever": "10",
            "instId": "BTC-USDT-SWAP",
            "pos": "100",
            "posSide": "long",
            "avgPx": "40000.0",
            "markPx": "41000.0",
            "idxPx": "40980.0",
            "last": "41010.0",
            "bePx": "39950.0",
            "liqPx": "35000.0",
            "margin": "1250.0",
            "notionalUsd": "4100000.0",
            "imr": "1000.0",
            "mmr": "500.0",
            "ordFrozen": "25.0",
            "fee": "10.0",
            "realizedPnl": "100.0",
            "upl": "1000.0",
            "uplLastPx": "1010.0",
            "uplRatio": "0.025",
            "uplRatioLastPx": "0.02525",
            "pnl": "1100.0",
            "fundingFee": "5.0",
        }
        position = OkxPositionData(
            position_info,
            symbol_name="BTC-USDT-SWAP",
            asset_type="FUTURE",
            has_been_json_encoded=True,
        )
        position.init_data()

        assert position.server_time == 1705315800000.0
        assert position.margin_type == "cross"
        assert position.is_isolated is False
        assert position.leverage == 10.0
        assert position.position_symbol_name == "BTC-USDT-SWAP"
        assert position.position_volume == 100.0
        assert position.position_side == "long"
        assert position.avg_price == 40000.0
        assert position.mark_price == 41000.0
        assert position.index_price == 40980.0
        assert position.last_price == 41010.0
        assert position.break_even_price == 39950.0
        assert position.liquidation_price == 35000.0
        assert position.position_margin == 1250.0
        assert position.position_notional_usd == 4100000.0
        assert position.position_initial_margin == 1000.0
        assert position.open_order_initial_margin_value == 25.0
        assert position.position_pnl == 1100.0
        assert position.unrealized_pnl_last_price == 1010.0
        assert position.unrealized_pnl_ratio == 0.025
        assert position.unrealized_pnl_ratio_last_price == 0.02525

        all_data = position.get_all_data()
        assert all_data["liquidation_price"] == 35000.0
        assert all_data["position_notional_usd"] == 4100000.0
        assert all_data["notionalUsd"] == 4100000.0
        assert all_data["market_value"] == 4100000.0
        assert all_data["position_initial_margin"] == 1000.0
        assert all_data["open_order_initial_margin"] == 25.0
        assert all_data["position_pnl"] == 1100.0

    def test_init_data_accepts_raw_json_payload(self):
        """Raw OKX REST payloads should unwrap data[0] before parsing."""
        position = OkxPositionData(
            '{"code":"0","data":[{"instId":"BTC-USDT-SWAP","pos":"2","markPx":"61000","notionalUsd":"1220"}]}',
            symbol_name="BTC-USDT-SWAP",
            asset_type="SWAP",
            has_been_json_encoded=False,
        )

        position.init_data()

        assert position.position_symbol_name == "BTC-USDT-SWAP"
        assert position.position_volume == 2.0
        assert position.mark_price == 61000.0
        assert position.position_notional_usd == 1220.0

    def test_position_data_inheritance(self):
        """Test that OkxPositionData inherits from PositionData."""
        position = OkxPositionData(
            {}, symbol_name="BTC-USDT-SWAP", asset_type="FUTURE", has_been_json_encoded=True
        )

        assert hasattr(position, "position_info")
        assert hasattr(position, "event")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
