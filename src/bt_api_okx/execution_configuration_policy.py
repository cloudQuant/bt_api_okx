"""OKX-specific credential field and environment declarations."""

from bt_api_base.execution_configuration_policy import ExecutionConfigurationPolicy


def execution_configuration_policy(exchange_name: str) -> ExecutionConfigurationPolicy:
    return ExecutionConfigurationPolicy(
        credential_aliases=(
            ("public", ("public_key", "api_key")),
            ("secret", ("private_key", "secret_key", "api_secret")),
            ("passphrase", ("passphrase",)),
        ),
        require_environment=True,
        api_regions=("global", "eea", "us", "tr"),
        production_only_api_regions=("tr",),
    )
