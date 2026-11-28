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

import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361,
    TP1_LINE_359,
    TP1_NET_INCOME_LINE_275,
    TP752_PC_LINE_10,
    TP752_PC_LINE_11,
    TP752_PC_LINE_12,
    TP752_PC_LINE_13,
    TP752_PC_LINE_14,
    TP752_PC_LINE_15,
    TP752_PC_LINE_16,
    TP752_PC_LINE_35,
    TP752_PC_LINE_36,
    TP752_PC_LINE_37,
    TP752_PC_LINE_38,
    TP752_PC_LINE_39,
    TP752_PC_LINE_40,
    TP752_PC_LINE_47,
    TP752_PC_LINE_48,
    TP752_PC_LINE_49,
    TP752_PC_LINE_50,
    WORK_CHART_201_TOTAL_LINE_6,
    WORK_CHART_401_INCOME_TAX_LINE_8,
)
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
    # "Subtract $7,655 from line 14 (maximum $12,755)": signed, then the maximum.
    lines[16] = cents(min(lines[14] - lines[15], LINE_16_MAXIMUM[year]))
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


KINDS = {
    10: TP752_PC_LINE_10,
    11: TP752_PC_LINE_11,
    12: TP752_PC_LINE_12,
    13: TP752_PC_LINE_13,
    14: TP752_PC_LINE_14,
    15: TP752_PC_LINE_15,
    16: TP752_PC_LINE_16,
    35: TP752_PC_LINE_35,
    36: TP752_PC_LINE_36,
    37: TP752_PC_LINE_37,
    38: TP752_PC_LINE_38,
    39: TP752_PC_LINE_39,
    40: TP752_PC_LINE_40,
    47: TP752_PC_LINE_47,
    48: TP752_PC_LINE_48,
    49: TP752_PC_LINE_49,
    50: TP752_PC_LINE_50,
}
PRINTED_LINES = (10, 12, 14, 15, 16, 35, 36, 37, 38, 39, 40, 47, 48, 49, 50)
CENT_ROUNDING = {"rounding": "ca-qc/cent_rounding"}
EXACT_ROUNDING = {"rounding": "ca-qc/exact_rounding"}
K = "ca-qc/tp752_pc_"


def lines_of(
    take_home_service: TakeHomeService,
    salary: str,
    year: int,
    born: int | None,
    *given: Artifact[Any],
) -> tuple[dict[int, Decimal], dict[int, Decimal]]:
    """The engine's printed lines of the form, and the lines worked out from the printed text over
    the figures of the other forms the form reads (read from their own worksheets)."""
    sheets = compute(take_home_service, salary, year=year, born=born, given=given)
    reads = Reads(
        work_income=D(salary),
        net_income=sheets["ca-qc/tp1_net_income"].get(TP1_NET_INCOME_LINE_275).value,
        income_tax=sheets["ca-qc/work_chart_401"].get(WORK_CHART_401_INCOME_TAX_LINE_8).value,
        line_359=sheets["ca-qc/tp1_credits_lines_350_to_361"].get(TP1_LINE_359).value,
        line_361=sheets["ca-qc/tp1_credits_lines_350_to_361"]
        .get(TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361)
        .value,
    )
    # Work Chart 201 line 6 is the salary when nothing else is given (the export line 10 reads).
    assert sheets["ca-qc/work_chart_201"].get(WORK_CHART_201_TOTAL_LINE_6).value == D(salary)
    values = given_lines(given)
    expected = printed_form(
        year, reads, born=born, line_11=values.get(11, D(0)), line_13=values.get(13, D(0))
    )
    sheet = sheets[FORM]
    actual = {line: sheet.get(KINDS[line]).value for line in PRINTED_LINES}
    return actual, {line: expected[line] for line in PRINTED_LINES}


def given_lines(given: tuple[Artifact[Any], ...]) -> dict[int, Decimal]:
    return {
        line: artifact.value
        for artifact in given
        for line, kind in KINDS.items()
        if artifact.kind is kind
    }


def step_without_title(step: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in step.items() if key != "title"}


def part(name: str) -> dict[str, Any]:
    loaded = yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def steps(name: str) -> list[dict[str, Any]]:
    declared = part(name)
    assert list(declared) == ["form", "capabilities"]
    assert declared["form"] == {"name": FORM}
    return [step_without_title(step) for step in declared["capabilities"]]


def op(
    name: str,
    output: str,
    consumes: dict[str, Any],
    *,
    reference: str | None = None,
    params: dict[str, str] | None = None,
    blank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    step: dict[str, Any] = {"name": name}
    if reference is not None:
        step["reference"] = reference
    step["unit"] = "ca/cad"
    if params is not None:
        step["params"] = params
    if consumes:
        step["consumes"] = consumes
    if blank is not None:
        step["blank"] = blank
    step["produces"] = {"output": output}
    return step
