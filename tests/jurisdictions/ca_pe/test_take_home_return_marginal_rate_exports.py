"""The Prince Edward Island forms export the lines the return summary's marginal rate reads.

Through the registered engine: the PE428 form holds the line 5 rate, the line 84, line 87 and
line 97 figures it exports, and the return summary holds the marginal rate. The export lists
themselves are pinned in `test_form_pe428.py`.
"""

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
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds

D = Decimal


def _sheet(salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-PE"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = prince_edward_island_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def test_the_return_summary_holds_each_of_its_three_outputs() -> None:
    sheet = _sheet("70000", "ca-pe/return")

    for name in (
        "ca/refund_or_balance_owing",
        "ca-pe/average_tax_rate",
        "ca-pe/marginal_tax_rate",
    ):
        assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("salary", "line_5"),
    [("20000", "0.095"), ("40000", "0.1347"), ("70000", "0.166"), ("200000", "0.19")],
)
def test_the_pe428_form_exports_the_line_5_rate_of_the_column_taxable_income_falls_in(
    salary: str, line_5: str
) -> None:
    sheet = _sheet(salary, "ca-pe/pe428")

    assert _value(sheet, "ca-pe/pe428_bracket_rate_line_5") == D(line_5)


@pytest.mark.parametrize(
    ("salary", "line_84", "line_87", "line_97"),
    [
        ("20000", "0.00", "350.00", "33.83"),
        ("28000", "5105.00", "94.75", "991.39"),
    ],
)
def test_the_pe428_form_exports_lines_84_87_and_97(
    salary: str, line_84: str, line_87: str, line_97: str
) -> None:
    sheet = _sheet(salary, "ca-pe/pe428")

    assert _value(sheet, "ca-pe/pe428_income_over_base_amount_line_84") == D(line_84)
    assert _value(sheet, "ca-pe/pe428_low_income_tax_reduction_line_87") == D(line_87)
    assert _value(sheet, "ca-pe/pe428_prince_edward_island_tax_line_97") == D(line_97)


@pytest.mark.parametrize(
    ("salary", "line_4", "claimed"),
    [("20000", "0.00", "0"), ("40000", "3035.00", "0"), ("100000", "62326.00", "0")],
)
def test_the_pe428_form_exports_the_age_amount_lines_as_nothing_claimed_without_a_birth_year(
    salary: str, line_4: str, claimed: str
) -> None:
    sheet = _sheet(salary, "ca-pe/pe428")

    assert _value(sheet, "ca-pe/worksheet_pe428_age_amount_line_4") == D(line_4)
    assert _value(sheet, "ca-pe/pe428_age_amount_claimed_line_10") == D(claimed)
