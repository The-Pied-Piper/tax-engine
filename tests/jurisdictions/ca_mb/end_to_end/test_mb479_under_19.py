"""Form MB479 (2025 and 2026) line 7 and line 81 for a filer under 19 at the end of the year: the
real Manitoba manifest composed end to end, the salary and the year of birth the only inputs.

Form MB479 (CRA 5007-TC) line 7 prints no age condition. The Manitoba guide, CRA 5007-PC (Form
MB479, Personal tax credit): "If you were under 19 years of age at the end of the year, you can
only claim this credit if one of the following applies to you: You had a spouse or common-law
partner / You were a parent / You can claim the Manitoba homeowners affordability tax credit on
your 2025 return". The engine models a filer with none of those, so a filer under 19 has no basic
credit and line 81 (the Manitoba credits) is 0.00. A filer 19 or older (born 1980) is unchanged,
and one born in 1955 still has the basic line: the basic credit of 195.00 less 1% of the family
income over the threshold, 95.65 at a salary of $10,000 and 0.00 at $20,000. The 2026 datasets are
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
MB479 = "ca-mb/mb479"
LINE_7 = "ca-mb/mb479_basic_credit_line_7"
LINE_81 = "ca-mb/mb479_manitoba_credits_line_81"


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _mb479(year: int, salary: str, birth_year: int) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-MB"),
            year,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, birth_year)),
        )
    )
    (mb479,) = worksheets[MB479]
    return mb479


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["5000", "10000", "17500"])
@pytest.mark.parametrize("age", [0, 10, 16, 18])
def test_a_filer_under_19_has_no_basic_credit_and_no_manitoba_credits(
    year: int, salary: str, age: int
) -> None:
    sheet = _mb479(year, salary, year - age)

    assert _figure(sheet, LINE_7) == D("0.00")
    assert _figure(sheet, LINE_81) == D("0.00")


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize(
    ("salary", "credits"), [("5000", "145.15"), ("10000", "95.65"), ("20000", "0.00")]
)
def test_a_filer_born_in_1980_is_unchanged(year: int, salary: str, credits: str) -> None:
    sheet = _mb479(year, salary, 1980)

    assert _figure(sheet, LINE_7) == D("195.00")
    assert _figure(sheet, LINE_81) == D(credits)


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["10000", "17500"])
def test_a_filer_born_in_1955_still_has_the_basic_line(year: int, salary: str) -> None:
    assert _figure(_mb479(year, salary, 1955), LINE_7) == D("195.00")
