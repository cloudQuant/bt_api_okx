"""Explicit exchange environment selection; never fall back from simulation to live."""

from __future__ import annotations

from copy import copy
from urllib.parse import urlsplit

_REST_ENDPOINTS = {
    "global": "https://openapi.okx.com",
    "eea": "https://eea.okx.com",
    "us": "https://us.okx.com",
    "tr": "https://tr.okx.com",
}

# www.okx.com was an accepted global REST override before api_region existed.
_REST_HOSTS = {
    "global": {"openapi.okx.com", "www.okx.com"},
    "eea": {"eea.okx.com"},
    "us": {"us.okx.com"},
    "tr": {"tr.okx.com"},
}

_WSS_HOSTS = {
    ("global", "production"): "ws.okx.com",
    ("global", "demo"): "wspap.okx.com",
    ("eea", "production"): "wseea.okx.com",
    ("eea", "demo"): "wseeapap.okx.com",
    ("us", "production"): "wsus.okx.com",
    ("us", "demo"): "wsuspap.okx.com",
    ("tr", "production"): "ws.okx.com",
}


def resolve_environment(options):
    """Resolve explicit environment and legacy boolean aliases, rejecting ambiguity."""
    aliases = []
    for key in ("testnet", "demo", "simulated_trading"):
        if key not in options:
            continue
        value = options[key]
        if not isinstance(value, bool):
            raise ValueError(
                f"{key} must be a boolean; use environment for named environments"
            )
        if value:
            aliases.append("testnet" if key == "testnet" else "demo")
        else:
            aliases.append("production")
    environment = options.get("environment")
    if environment is not None:
        if not isinstance(environment, str):
            raise ValueError("environment must be production, demo or testnet")
        environment = environment.strip().lower()
    if len(set(aliases)) > 1:
        raise ValueError("Conflicting demo/testnet flags")
    if environment is None:
        environment = aliases[0] if aliases else "production"
    if environment not in {"production", "demo", "testnet"}:
        raise ValueError("environment must be production, demo or testnet")
    if aliases and environment != aliases[0]:
        raise ValueError("environment conflicts with demo/testnet flag")
    return environment


def _resolve_api_region(options):
    """Resolve the canonical OKX API region without guessing from endpoint overrides."""
    if "region" in options:
        raise ValueError("region is not supported; use api_region")
    if "api_region" not in options:
        return "global"
    api_region = options["api_region"]
    if not isinstance(api_region, str):
        raise ValueError("api_region must be global, eea, us or tr")
    api_region = api_region.strip().lower()
    if api_region not in _REST_ENDPOINTS:
        raise ValueError("api_region must be global, eea, us or tr")
    return api_region


def _override(
    options,
    field,
    default,
    *,
    allowed_hosts,
    allowed_ports,
    expected_paths,
):
    url = options.get(field) if options.get(field) is not None else default
    if not isinstance(url, str) or not url or url != url.strip():
        raise ValueError(f"Invalid {field}; an absolute URL is required")
    expected_scheme = "https" if field == "rest_url" else "wss"
    try:
        parsed = urlsplit(url)
        structurally_valid = (
            parsed.scheme == expected_scheme
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
        )
        port = parsed.port
    except (TypeError, ValueError):
        structurally_valid = False
        port = None
    if not structurally_valid:
        raise ValueError(f"Invalid {field}; an authenticated URL is not allowed")
    if (
        parsed.hostname not in allowed_hosts
        or port not in allowed_ports
        or parsed.path not in expected_paths
    ):
        raise ValueError(f"{field} conflicts with the selected environment")
    return url.rstrip("/") if field == "rest_url" else url


def _matches_endpoint(value, scheme, hosts, ports, paths):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == scheme
            and parsed.hostname in hosts
            and parsed.port in ports
            and parsed.path in paths
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
        )
    except (TypeError, ValueError):
        return False


def verify_environment(params):
    """Return a safe proof of the current OKX header and endpoint selection."""
    result = {
        "environment": "unknown",
        "api_region": None,
        "simulated": None,
        "verified": False,
    }
    try:
        environment = params.environment
        api_region = params.api_region
        if (
            environment not in {"production", "demo"}
            or api_region not in _REST_ENDPOINTS
        ):
            return result
        simulated = params.simulated_trading
        if not isinstance(simulated, bool) or simulated != (environment == "demo"):
            return result
        wss_host = _WSS_HOSTS[(api_region, environment)]
        verified = (
            _matches_endpoint(
                params.rest_url,
                "https",
                _REST_HOSTS[api_region],
                {None, 443},
                {"", "/"},
            )
            and _matches_endpoint(
                params.wss_url,
                "wss",
                {wss_host},
                {None, 443, 8443},
                {"/ws/v5/public"},
            )
            and _matches_endpoint(
                params.account_wss_url,
                "wss",
                {wss_host},
                {None, 443, 8443},
                {"/ws/v5/private"},
            )
            and _matches_endpoint(
                params.kline_wss_url,
                "wss",
                {wss_host},
                {None, 443, 8443},
                {"/ws/v5/business"},
            )
        )
        return {
            "environment": environment,
            "api_region": api_region,
            "simulated": simulated,
            "verified": bool(verified),
        }
    except Exception:
        return result


def configure_environment(params, options):
    """Configure OKX demo headers and every WS channel on a private config copy.

    Official reference: https://www.okx.com/docs-v5/en/#overview-demo-trading-services
    """
    params = copy(params)
    environment = resolve_environment(options)
    api_region = _resolve_api_region(options)
    params.environment = "demo" if environment == "testnet" else environment
    params.api_region = api_region
    params.simulated_trading = params.environment == "demo"
    endpoint_key = (api_region, params.environment)
    if endpoint_key not in _WSS_HOSTS:
        raise ValueError(
            f"api_region {api_region} does not support {params.environment}"
        )
    params.rest_url = _override(
        options,
        "rest_url",
        _REST_ENDPOINTS[api_region],
        allowed_hosts=_REST_HOSTS[api_region],
        allowed_ports={None, 443},
        expected_paths={"", "/"},
    )
    host = _WSS_HOSTS[endpoint_key]
    for field, channel in (
        ("wss_url", "public"),
        ("account_wss_url", "private"),
        ("kline_wss_url", "business"),
    ):
        default = f"wss://{host}:8443/ws/v5/{channel}"
        setattr(
            params,
            field,
            _override(
                options,
                field,
                default,
                allowed_hosts={host},
                allowed_ports={None, 443, 8443},
                expected_paths={f"/ws/v5/{channel}"},
            ),
        )
    return params
