"""Tests for OkxOrderData container."""

from __future__ import annotations

from bt_api_okx.containers.orders.okx_order import OkxOrderData


class TestOkxOrderData:
    """Tests for OkxOrderData."""

    def test_init(self):
        """Test initialization."""
        order = OkxOrderData({}, symbol_name="BTC-USDT", asset_type="SPOT")

        assert order.exchange_name == "OKX"
        assert order.symbol_name == "BTC-USDT"
        assert order.asset_type == "SPOT"
        assert order.has_been_init_data is False

    def test_init_data(self):
        """Test init_data with order info."""
        # OKX order_data is set directly from order_info when has_been_json_encoded=True
        data = {"ordId": "123456", "instId": "BTC-USDT", "side": "buy", "state": "filled"}
        order = OkxOrderData(
            data, symbol_name="BTC-USDT", asset_type="SPOT", has_been_json_encoded=True
        )
        order.init_data()

        assert order.order_id == "123456"
        assert order.order_symbol_name == "BTC-USDT"

    def test_get_all_data(self):
        """Test get_all_data."""
        order = OkxOrderData(
            {}, symbol_name="BTC-USDT", asset_type="SPOT", has_been_json_encoded=True
        )
        result = order.get_all_data()

        assert result["exchange_name"] == "OKX"
        assert result["symbol_name"] == "BTC-USDT"

    def test_get_all_data_initializes_direct_order_aliases_and_remaining_quantity(self):
        order = OkxOrderData(
            {
                "ordId": "venue-123",
                "clOrdId": "client-456",
                "instId": "BTC-USDT-SWAP",
                "state": "partially_filled",
                "sz": "2",
                "accFillSz": "0.75",
            },
            symbol_name="BTC-USDT-SWAP",
            asset_type="SWAP",
            has_been_json_encoded=True,
        )

        projected = order.get_all_data()

        assert projected["order_id"] == projected["external_order_id"] == "venue-123"
        assert projected["venue_order_id"] == projected["id"] == "venue-123"
        assert projected["order_ref"] == "venue-123"
        assert projected["client_order_id"] == "client-456"
        assert projected["symbol"] == projected["data_name"] == "BTC-USDT-SWAP"
        assert projected["remaining"] == 1.25
        assert order.has_been_init_data is True

    def test_str_representation(self):
        """Test __str__ method."""
        order = OkxOrderData(
            {}, symbol_name="BTC-USDT", asset_type="SPOT", has_been_json_encoded=True
        )
        result = str(order)

        assert "OKX" in result
