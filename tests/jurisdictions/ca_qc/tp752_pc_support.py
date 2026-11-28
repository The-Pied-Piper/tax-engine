"""Shared helpers of the TP-752.PC-V tests (Tax Credit for Career Extension, 2025-10 and 2026-10).

The figures printed on the form, by year (the confirmed text of the 2025-10 and 2026-10 editions):
line 15 "7,500 00" / "7,655 00"; line 16 "(maximum $12,500)" / "(maximum $12,755)"; line 35 "x 14%";
line 37 "56,500 00" / "57,660 00"; line 39 "x 7%"; line 48 "x 14%". Eligibility is "65 or over on
December 31": born in 1960 or earlier for 2025 and in 1961 or earlier for 2026 (the cutoff of the
`ca-qc/age_65_or_older_conditions` dataset).

`printed_form` works the printed lines out with Decimal from the lines the form reads (10 from Work
Chart 201 line 6, 36 from TP-1 line 275, 47 from line 401, 48 from lines 359 and 361), rounding each
dollars-and-cents line half-up to the cent, the project's choice as the form states no rounding
rule. The tests compare the engine's worksheet with it: the expected figures are computed here from
the printed lines, not taken from a Revenu Quebec example.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.tp1_credits_support import (
    CHAIN_PARTS,
    LINE_359_PARTS,
    PART_A_DECLARATION,
    TP752_PC_LINE_PARTS,
    WORK_CHART_401_PARTS,
)
from tests.jurisdictions.ca_qc.tp1_net_income_support import HEADER

D = Decimal
CENT = D("0.01")
ZERO = D(0)
FORM = "ca-qc/tp752_pc"
FORM_PART = "tp752_pc.yaml"
# Everything the form reads, then its own line parts; the real declaration is the form text.
CHAIN = (
    *CHAIN_PARTS,
    *WORK_CHART_401_PARTS,
    PART_A_DECLARATION,
    *LINE_359_PARTS,
    "tp1_credits_line_361.yaml",
    *TP752_PC_LINE_PARTS,
)

LINE_15 = {2025: D("7500"), 2026: D("7655")}
LINE_16_MAXIMUM = {2025: D("12500"), 2026: D("12755")}
LINE_37 = {2025: D("56500"), 2026: D("57660")}
LINE_35_RATE = D("0.14")
LINE_39_RATE = D("0.07")
LINE_48_RATE = D("0.14")
# The last year of birth of a filer 65 or over on December 31 of the tax year.
LAST_BIRTH_YEAR = {2025: 1960, 2026: 1961}
# "If the amount on line 36 is $81,500 / $83,170 or more, you are not entitled to the tax credit."
NO_CREDIT_FROM_LINE_36 = {2025: D("81500"), 2026: D("83170")}


def form_text() -> str:
    """The real declaration of the form, the form of the test manifest."""
    return (QUEBEC_PARTS / FORM_PART).read_text(encoding="utf-8")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Reads:
    """The figures of other forms the form reads."""

    work_income: Decimal  # Work Chart 201 line 6
    net_income: Decimal  # TP-1 line 275
    income_tax: Decimal  # TP-1 line 401 (Work Chart 401 line 8)
    line_359: Decimal
    line_361: Decimal


def printed_form(
    year: int,
    reads: Reads,
    *,
    born: int | None,
    line_11: Decimal = ZERO,
    line_13: Decimal = ZERO,
) -> dict[int, Decimal]:
    """The printed lines 10 to 50 of the form, by line number, worked out from the printed text."""
    aged = born is not None and born <= LAST_BIRTH_YEAR[year]
    lines: dict[int, Decimal] = {}
    lines[10] = cents(reads.work_income) if aged else D("0.00")
    lines[11] = line_11
    lines[12] = cents(lines[10] - line_11)
    lines[13] = line_13
    lines[14] = cents(lines[12] - line_13)
    lines[15] = cents(LINE_15[year])
    # "Subtract $7,655 from line 14 (maximum $12,755)": at or below 0 is not entitled (line 12
    # note), so 0, then the maximum.
    lines[16] = cents(min(max(lines[14] - lines[15], D("0")), LINE_16_MAXIMUM[year]))
    lines[35] = cents(lines[16] * LINE_35_RATE)
    lines[36] = reads.net_income
    lines[37] = cents(LINE_37[year])
    lines[38] = max(cents(lines[36] - lines[37]), D("0.00"))
    lines[39] = cents(lines[38] * LINE_39_RATE)
    lines[40] = max(cents(lines[35] - lines[39]), D("0.00"))
    lines[47] = reads.income_tax
    lines[48] = cents((reads.line_359 + reads.line_361) * LINE_48_RATE)
    lines[49] = max(cents(lines[47] - lines[48]), D("0.00"))
    lines[50] = min(lines[40], lines[49])
    return lines


def compute(
    take_home_service: TakeHomeService,
    salary: str,
    *,
    year: int = 2026,
    born: int | None = None,
    given: tuple[Artifact[Any], ...] = (),
) -> dict[str, Worksheet]:
    """Every worksheet of the chain: Work Chart 201, TP-1 net income, Work Chart 401, the split part
    of the TP-1 credits (lines 359 and 361) and the form, for a salary (every optional input left
    out unless in `given`) and a year of birth (left out when None)."""
    starting: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary)), *given]
    if born is not None:
        starting.append(Artifact(BIRTH_YEAR, born))
    service = take_home_service(HEADER, form_text(), *CHAIN)
    worksheets = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), year, tuple(starting))
    )
    return {form: sheets[0] for form, sheets in worksheets.items()}
