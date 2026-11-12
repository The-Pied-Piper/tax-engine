"""Jurisdiction codes: which tax jurisdiction a manifest or computation is for.

A code is ISO 3166-1 alpha-2 (`CA`) or ISO 3166-2 (`CA-ON`). Only the format is checked, and a code
is never coerced: `ca-on` is rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tax_engine.domain.errors import InvalidJurisdictionCodeError
from tax_engine.domain.registry import Namespace

_ISO_3166 = re.compile(r"[A-Z]{2}(-[A-Z0-9]{1,3})?")


@dataclass(frozen=True, slots=True)
class JurisdictionCode:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"jurisdiction code must be a str, got {type(self.value).__name__}")
        if not _ISO_3166.fullmatch(self.value):
            raise InvalidJurisdictionCodeError(
                f"invalid jurisdiction code {self.value!r}: expected ISO 3166 form, "
                "e.g. 'CA' or 'CA-ON'"
            )

    @property
    def namespace(self) -> Namespace:
        """The namespace of its jurisdiction package: the code lower-cased, `EX-ON` -> `ex-on`."""
        return Namespace(self.value.lower())

    @property
    def namespaces(self) -> tuple[str, ...]:
        """The namespaces whose shared pieces this jurisdiction uses, its own first: `CA-ON` gives
        `ca-on` then `ca`, so a province inherits the country's; a country gives only its own.
        """
        own = self.namespace.name
        country = own.partition("-")[0]
        return (own,) if country == own else (own, country)

    def __str__(self) -> str:
        return self.value
