"""Tests for exchange_registers/register_okx.py."""

from __future__ import annotations

from bt_api_okx.registry_registration import register_okx


class TestRegisterOkx:
    """Tests for OKX registration module."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert register_okx is not None
