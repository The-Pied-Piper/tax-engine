"""A request for the take-home pay of a salary."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.jurisdiction_code import JurisdictionCode


@dataclass(frozen=True, slots=True)
class TakeHomeRequest:
    """The jurisdiction, tax year and salary to answer for; rates and trace only when asked."""

    jurisdiction: JurisdictionCode
    tax_year: int
    salary: Decimal
    include_rates: bool = False
    include_trace: bool = False
