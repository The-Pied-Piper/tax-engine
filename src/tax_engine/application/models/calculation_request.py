"""A request to compute the forms of a return."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode


@dataclass(frozen=True, slots=True)
class TaxCalculationRequest:
    """The jurisdiction and tax year to compute, and the artifacts the computation starts from.

    `artifacts` are one of each declared input kind, among them each form's instances.
    """

    jurisdiction: JurisdictionCode
    tax_year: int
    artifacts: tuple[Artifact[Any], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifacts", tuple(self.artifacts))
