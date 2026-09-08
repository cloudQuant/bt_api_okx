"""Offline OKX position-mode mutation request tests."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap


@pytest.mark.parametrize("mode", ["net_mode", "long_short_mode"])
def test_set_position_mode_uses_account_wide_endpoint(monkeypatch, mode):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock(return_value={"code": "0", "data": [{"posMode": mode}]})
    monkeypatch.setattr(feed, "request", request)
    try:
        result = feed.set_position_mode(
            mode,
            extra_data={"trace": "offline"},
            request_id="mode-1",
        )
        assert result == {"code": "0", "data": [{"posMode": mode}]}
        assert request.call_args.args == ("POST /api/v5/account/set-position-mode",)
        assert request.call_args.kwargs["body"] == {"posMode": mode}
        extra_data = request.call_args.kwargs["extra_data"]
        assert extra_data["request_type"] == "set_mode"
        assert extra_data["trace"] == "offline"
        assert extra_data["request_id"] == "mode-1"
    finally:
        feed._http_client.close()


def test_legacy_set_mode_keeps_dual_side_default(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock(return_value={"code": "0", "data": []})
    monkeypatch.setattr(feed, "request", request)
    try:
        feed.set_mode()
        assert request.call_args.kwargs["body"] == {"posMode": "long_short_mode"}
    finally:
        feed._http_client.close()


@pytest.mark.parametrize("mode", [None, "", "net", "dual_side", "hedge"])
def test_set_position_mode_rejects_non_native_values_before_request(monkeypatch, mode):
    feed = OkxRequestDataSwap(None, environment="demo")
    request = Mock()
    monkeypatch.setattr(feed, "request", request)
    try:
        with pytest.raises(ValueError, match="net_mode or long_short_mode"):
            feed.set_position_mode(mode)
        request.assert_not_called()
    finally:
        feed._http_client.close()


def test_async_set_position_mode_schedules_the_same_request(monkeypatch):
    feed = OkxRequestDataSwap(None, environment="demo")
    pending = object()
    async_request = Mock(return_value=pending)
    submit = Mock()
    monkeypatch.setattr(feed, "async_request", async_request)
    monkeypatch.setattr(feed, "submit", submit)
    try:
        feed.async_set_position_mode("net_mode", extra_data={"trace": "offline"})
        async_request.assert_called_once()
        assert async_request.call_args.args == (
            "POST /api/v5/account/set-position-mode",
        )
        assert async_request.call_args.kwargs["body"] == {"posMode": "net_mode"}
        submit.assert_called_once_with(pending, callback=feed.async_callback)
    finally:
        feed._http_client.close()
