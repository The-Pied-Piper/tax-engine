"""Outbound port: where jurisdictions and their manifests come from."""

from __future__ import annotations

from typing import Protocol

from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.jurisdiction_code import JurisdictionCode


class JurisdictionSource(Protocol):
    def get_jurisdiction(self, code: JurisdictionCode) -> Jurisdiction:
        """The jurisdiction with every manifest stored for it.

        Raise NotFoundError if none are stored, InvalidManifestError if any cannot be read.
        """
        ...
