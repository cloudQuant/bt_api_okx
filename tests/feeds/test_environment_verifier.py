"""Current-endpoint verification for OKX execution environments."""

from __future__ import annotations

import pytest
from bt_api_okx.environment import configure_environment, verify_environment
from bt_api_okx.exchange_data import OkxExchangeDataSwap
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap

_ENDPOINT_CASES = [
    (
        "global",
        "production",
        False,
        "https://openapi.okx.com",
        "ws.okx.com",
    ),
    (
        "global",
        "demo",
        True,
        "https://openapi.okx.com",
        "wspap.okx.com",
    ),
    (
        "eea",
        "production",
        False,
        "https://eea.okx.com",
        "wseea.okx.com",
    ),
    (
        "eea",
        "demo",
        True,
        "https://eea.okx.com",
        "wseeapap.okx.com",
    ),
    (
        "us",
        "production",
        False,
        "https://us.okx.com",
        "wsus.okx.com",
    ),
    (
        "us",
        "demo",
        True,
        "https://us.okx.com",
        "wsuspap.okx.com",
    ),
    (
        "tr",
        "production",
        False,
        "https://tr.okx.com",
        "ws.okx.com",
    ),
]


@pytest.mark.parametrize(
    "api_region,environment,simulated,rest_url,wss_host",
    _ENDPOINT_CASES,
)
def test_current_official_endpoints_are_selected_and_verified(
    api_region: str,
    environment: str,
    simulated: bool,
    rest_url: str,
    wss_host: str,
) -> None:
    params = configure_environment(
        OkxExchangeDataSwap(),
        {"api_region": api_region, "environment": environment},
    )

    assert params.api_region == api_region
    assert params.rest_url == rest_url
    assert params.wss_url == f"wss://{wss_host}:8443/ws/v5/public"
    assert params.account_wss_url == f"wss://{wss_host}:8443/ws/v5/private"
    assert params.kline_wss_url == f"wss://{wss_host}:8443/ws/v5/business"
    assert verify_environment(params) == {
        "environment": environment,
        "api_region": api_region,
        "simulated": simulated,
        "verified": True,
    }


@pytest.mark.parametrize(
    "environment,wss_host",
    [("production", "ws.okx.com"), ("demo", "wspap.okx.com")],
)
def test_explicit_global_overrides_remain_verified(
    environment: str,
    wss_host: str,
) -> None:
    params = configure_environment(
        OkxExchangeDataSwap(),
        {
            "environment": environment,
            "rest_url": "https://www.okx.com/",
            "wss_url": f"wss://{wss_host}/ws/v5/public",
            "account_wss_url": f"wss://{wss_host}:443/ws/v5/private",
            "kline_wss_url": f"wss://{wss_host}:8443/ws/v5/business",
        },
    )

    assert params.api_region == "global"
    assert params.rest_url == "https://www.okx.com"
    assert verify_environment(params)["verified"] is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("rest_url", "https://openapi.okx.com.evil.invalid"),
        ("rest_url", "https://openapi.okx.com:8443"),
        ("rest_url", "http://openapi.okx.com"),
        ("wss_url", "wss://ws.okx.com:8443/ws/v5/public"),
        ("wss_url", "wss://wspap.okx.com:8443/ws/v5/private"),
        ("wss_url", "wss://wspap.okx.com:8443/ws/v5/public?channel=private"),
        ("account_wss_url", "wss://wspap.okx.com.evil.invalid:8443/ws/v5/private"),
        ("account_wss_url", "wss://wspap.okx.com:8443/ws/v5/public"),
        ("account_wss_url", "wss://wspap.okx.com:8443/ws/v5/private#ignored"),
        ("kline_wss_url", "wss://ws.okx.com:8443/ws/v5/business"),
        ("kline_wss_url", "wss://wspap.okx.com:8443/ws/v5/private"),
    ],
)
def test_mutated_demo_endpoint_invalidates_environment_proof(
    field: str, value: str
) -> None:
    feed = OkxRequestDataSwap(None, environment="demo")
    try:
        setattr(feed._params, field, value)
        assert feed.get_environment_info() == {
            "environment": "demo",
            "api_region": "global",
            "simulated": True,
            "verified": False,
        }
    finally:
        feed._http_client.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("wss_url", "wss://wspap.okx.com:8443/ws/v5/private"),
        ("account_wss_url", "wss://wspap.okx.com:8443/ws/v5/public"),
        ("kline_wss_url", "wss://wspap.okx.com:8443/ws/v5/private"),
        ("wss_url", "wss://wspap.okx.com:8443/ws/v5/public?redirect=1"),
        ("account_wss_url", "wss://wspap.okx.com:8443/ws/v5/private#fragment"),
    ],
)
def test_config_rejects_wrong_channel_role_query_and_fragment(
    field: str, value: str
) -> None:
    with pytest.raises(ValueError):
        OkxRequestDataSwap(None, environment="demo", **{field: value})


@pytest.mark.parametrize(
    "options",
    [
        {"api_region": "apac"},
        {"api_region": ""},
        {"api_region": None},
        {"api_region": True},
        {"api_region": 1},
        {"region": "eea"},
        {"environment": "demo", "demo": False},
        {"environment": "production", "simulated_trading": True},
    ],
)
def test_invalid_regions_and_conflicting_environment_aliases_fail_closed(
    options,
) -> None:
    with pytest.raises(ValueError):
        configure_environment(OkxExchangeDataSwap(), options)


def test_tr_demo_fails_closed_without_a_verified_official_endpoint_set() -> None:
    with pytest.raises(ValueError, match="does not support demo"):
        configure_environment(
            OkxExchangeDataSwap(),
            {"api_region": "tr", "environment": "demo"},
        )


@pytest.mark.parametrize(
    "api_region,environment,field,value",
    [
        ("global", "production", "rest_url", "https://eea.okx.com"),
        ("eea", "production", "rest_url", "https://openapi.okx.com"),
        ("us", "demo", "rest_url", "https://eea.okx.com"),
        ("eea", "demo", "wss_url", "wss://wspap.okx.com:8443/ws/v5/public"),
        (
            "us",
            "production",
            "account_wss_url",
            "wss://ws.okx.com:8443/ws/v5/private",
        ),
        (
            "global",
            "demo",
            "kline_wss_url",
            "wss://wsuspap.okx.com:8443/ws/v5/business",
        ),
    ],
)
def test_config_rejects_mixed_regional_endpoint_sets(
    api_region: str,
    environment: str,
    field: str,
    value: str,
) -> None:
    with pytest.raises(ValueError, match=rf"{field} conflicts"):
        configure_environment(
            OkxExchangeDataSwap(),
            {"api_region": api_region, "environment": environment, field: value},
        )


def test_region_drift_invalidates_the_complete_environment_proof() -> None:
    params = configure_environment(
        OkxExchangeDataSwap(),
        {"api_region": "global", "environment": "demo"},
    )

    params.api_region = "eea"

    assert verify_environment(params) == {
        "environment": "demo",
        "api_region": "eea",
        "simulated": True,
        "verified": False,
    }
