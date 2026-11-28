"""Form BC479 (2025 and 2026) line 9 and line 45 for a filer under 19 at the end of the year: the
real British Columbia manifest composed end to end, the salary and the year of birth the only
inputs.

Form BC479 (CRA 5010-TC) line 9 prints no age condition. The BC guide, CRA 5010-PC (Form BC479,
Sales tax credit): "You can claim this credit if, on December 31, 2025, you were a resident of
British Columbia and you met any of the following conditions: You were 19 years of age or older /
You had a spouse or common-law partner / You were a parent of a child". The engine models a filer
with no spouse or child, so a filer under 19 has no sales tax credit and line 45 (the British
Columbia credits) is 0.00. A filer 19 or older (born 1980) is unchanged, and one born in 1955
still has the basic line: the basic credit of 75.00 less 2% of the net income over 15,000.00, which
is 75.00 at a salary of $10,000, 27.80 at $17,500 (the net income is the salary less the enhanced
CPP contributions the filer pays) and 0.00 at $20,000. The 2026 datasets are
provisional (the 2026 guide is not yet published)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.registrations import artifact_kinds

D = Decimal
BC479 = "ca-bc/bc479"
LINE_9 = "ca-bc/bc479_basic_sales_tax_credit_line_9"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _bc479(year: int, salary: str, birth_year: int) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-BC"),
            year,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, birth_year)),
        )
    )
    (bc479,) = worksheets[BC479]
    return bc479


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["5000", "10000", "17500"])
@pytest.mark.parametrize("age", [0, 10, 16, 18])
def test_a_filer_under_19_has_no_sales_tax_credit_and_no_british_columbia_credits(
    year: int, salary: str, age: int
) -> None:
    sheet = _bc479(year, salary, year - age)

    assert _figure(sheet, LINE_9) == D("0.00")
    assert _figure(sheet, LINE_45) == D("0.00")


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    ("salary", "credits"), [("10000", "75.00"), ("17500", "27.80"), ("20000", "0.00")]
)
def test_a_filer_born_in_1980_is_unchanged(year: int, salary: str, credits: str) -> None:
    sheet = _bc479(year, salary, 1980)

    assert _figure(sheet, LINE_9) == D("75.00")
    assert _figure(sheet, LINE_45) == D(credits)


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["10000", "17500"])
def test_a_filer_born_in_1955_still_has_the_basic_line(year: int, salary: str) -> None:
    assert _figure(_bc479(year, salary, 1955), LINE_9) == D("75.00")


@pytest.mark.parametrize(
    ("year", "birth_year", "expected"),
    [(2025, 2006, "75.00"), (2025, 2007, "0.00"), (2026, 2007, "75.00"), (2026, 2008, "0.00")],
)
def test_the_cutoff_year_moves_with_the_tax_year(year: int, birth_year: int, expected: str) -> None:
    assert _figure(_bc479(year, "10000", birth_year), LINE_9) == D(expected)
