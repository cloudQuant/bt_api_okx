"""Private immutable credential bundle shared by OKX REST and WSS signers."""

from __future__ import annotations

from dataclasses import dataclass, field

from bt_api_base.execution_request_receipt_protocol import (
    ExecutionCredentialRequestOpaqueRef,
)


@dataclass(frozen=True, eq=False)
class OkxCredentialBinding:
    """One credential generation. Values are excluded from repr and equality."""

    api_key: str | None = field(repr=False)
    api_secret: str | None = field(repr=False)
    passphrase: str | None = field(repr=False)
    lineage_ref: ExecutionCredentialRequestOpaqueRef = field(
        default_factory=ExecutionCredentialRequestOpaqueRef,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        for value in (self.api_key, self.api_secret, self.passphrase):
            if value is not None and not isinstance(value, str):
                raise TypeError("OKX credentials must be strings or None")
        if type(self.lineage_ref) is not ExecutionCredentialRequestOpaqueRef:
            raise TypeError("OKX credential lineage marker is invalid")

    def __repr__(self) -> str:
        return "OkxCredentialBinding(<redacted>)"


__all__ = ["OkxCredentialBinding"]
