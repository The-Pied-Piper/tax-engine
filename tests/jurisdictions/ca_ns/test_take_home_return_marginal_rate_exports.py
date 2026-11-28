"""The Nova Scotia form exports the lines the return summary's marginal rate reads.

Through the registered engine over the real manifest folder: the NS428 form holds the line 5 rate
and the line 81, line 84 and line 99 figures it exports, and the return summary holds each of its
three outputs. The export list itself is pinned in `test_form_ns428.py`.
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
from tax_engine.registrations import artifact_kinds

D = Decimal


def _sheet(salary: str, form: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NS"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def test_the_return_summary_holds_each_of_its_three_outputs() -> None:
    sheet = _sheet("70000", "ca-ns/return")

    for name in (
        "ca/refund_or_balance_owing",
        "ca-ns/average_tax_rate",
        "ca-ns/marginal_tax_rate",
    ):
        assert isinstance(_value(sheet, name), Decimal)


@pytest.mark.parametrize(
    ("salary", "line_5"),
    [("20000", "0.0879"), ("70000", "0.1667"), ("250000", "0.21")],
)
def test_the_ns428_form_exports_the_line_5_rate(salary: str, line_5: str) -> None:
    sheet = _sheet(salary, "ca-ns/ns428")

    assert _value(sheet, "ca-ns/ns428_bracket_rate_line_5") == D(line_5)


@pytest.mark.parametrize(
    ("salary", "line_81", "line_84", "line_99"),
    [
        ("12000", "0.00", "300.00", "0.00"),
        ("16000", "875.00", "256.25", "29.41"),
        ("20000", "4835.00", "58.25", "552.33"),
        ("22000", "6815.00", "0.00", "773.03"),
    ],
)
def test_the_ns428_form_exports_lines_81_84_and_99(
    salary: str, line_81: str, line_84: str, line_99: str
) -> None:
    sheet = _sheet(salary, "ca-ns/ns428")

    assert _value(sheet, "ca-ns/ns428_line_81") == D(line_81)
    assert _value(sheet, "ca-ns/ns428_low_income_reduction_line_84") == D(line_84)
    assert _value(sheet, "ca-ns/ns428_nova_scotia_tax_line_99") == D(line_99)


@pytest.mark.parametrize(("salary", "line_4"), [("20000", "0.00"), ("40000", "8807.00")])
def test_the_ns428_form_exports_the_age_amount_figures_of_a_filer_with_no_birth_year(
    salary: str, line_4: str
) -> None:
    # No birth year: the age amount claimed is 0.00 whatever the income. Line 4 is the net income
    # over the threshold (39,635.00 - 30,828.00 = 8,807.00 at a salary of 40,000).
    sheet = _sheet(salary, "ca-ns/ns428")

    assert _value(sheet, "ca-ns/ns428_age_amount_claimed_line_10") == D("0.00")
    assert _value(sheet, "ca-ns/worksheet_ns428_age_amount_line_4") == D(line_4)
