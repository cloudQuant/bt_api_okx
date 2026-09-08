"""Offline trust-boundary tests for OKX demo REST routing."""

from __future__ import annotations

import pytest
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap


@pytest.mark.parametrize(
    "api_region,environment,rest_url",
    [
        ("global", "demo", "https://openapi.okx.com"),
        ("global", "demo", "https://www.okx.com"),
        ("eea", "demo", "https://eea.okx.com"),
        ("us", "demo", "https://us.okx.com"),
        ("tr", "production", "https://tr.okx.com"),
    ],
)
def test_rest_override_accepts_selected_official_region(
    api_region: str,
    environment: str,
    rest_url: str,
) -> None:
    feed = OkxRequestDataSwap(
        None,
        environment=environment,
        api_region=api_region,
        rest_url=rest_url,
    )
    try:
        assert feed._params.rest_url == rest_url
    finally:
        feed._http_client.close()


@pytest.mark.parametrize(
    "rest_url",
    [
        "https://example.com",
        "https://openapi.okx.com.evil.invalid",
        "https://openapi.okx.com:8443",
        "https://eea.okx.com",
        "https://us.okx.com",
        "https://tr.okx.com",
    ],
)
def test_global_demo_rest_override_rejects_other_regions_and_untrusted_hosts(
    rest_url: str,
) -> None:
    with pytest.raises(ValueError, match="rest_url conflicts"):
        OkxRequestDataSwap(None, environment="demo", rest_url=rest_url)
