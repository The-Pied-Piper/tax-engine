"""Jurisdiction codes: which tax jurisdiction a manifest or computation is for.

Codes follow ISO 3166: a country (ISO 3166-1 alpha-2, e.g. `CA`) or a country
plus subdivision (ISO 3166-2, e.g. `CA-ON`). Only the format is checked, not
membership in the ISO lists. Codes are never coerced: `ca-on` is rejected,
not upper-cased.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tax_calculator.domain.errors import InvalidJurisdictionCodeError
from tax_calculator.domain.registry import Namespace

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

    def __str__(self) -> str:
        return self.value
