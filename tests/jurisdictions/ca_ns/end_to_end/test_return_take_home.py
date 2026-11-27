"""The Nova Scotia take-home return (2025): T1 line 167, "Refund or balance owing",
from the salary alone, with the real Nova Scotia manifest composed end to end.

The registered engine (`build_tax_computation`) runs over the real Nova Scotia 2025
manifest, with the gross salary (`ca/employment_income`) the only input and every optional input
left blank. The return sheet (`ca-ns/return`) holds T1 line 167 at salaries of $20,000, $30,000 and
$70,000: -922.58 / 1,719.90 / 14,798.74 (positive is a balance owing, negative a refund).

Form text (T1 General 5006-R): "Line 147 and line 42800: Provincial or territorial tax", "Line 148
and line 43500: Add lines 143 to 147. Total payable", "Line 166 and line 48200: Add lines 150 to
165. Total credits" and "Line 167: Line 149 minus line 166 ... Refund or balance owing", line 149
being "Enter the amount from line 148 of the previous page.". So line 167 is the total payable
(line 148) less the total credits (line 166); the tests tie it to the T1 form's own sheet, to NS428
line 99 (T1 line 42800) and, at each salary, to a take-home worked from the printed CPP and EI
figures.
Nova Scotia has no provincial credits form here, so T1 line 47900 is blank. The line
143 figure (net federal tax, line 42000) is read from the T1 sheet: it is pinned by the federal
tests, and it is the same figure the Saskatchewan return reads at the same salaries.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

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
NOVA_SCOTIA = JurisdictionCode("CA-NS")
RETURN = "ca-ns/return"
T1 = "ca/t1_tax_and_credits"
NS428 = "ca-ns/ns428"
LINE_167 = "ca/refund_or_balance_owing"
LINE_99 = "ca-ns/ns428_nova_scotia_tax_line_99"
LINE_143 = "ca/net_federal_tax"
LINE_147 = "ca/provincial_tax_line_42800"
LINE_148 = "ca/total_payable"
LINE_166 = "ca/total_credits"
LINE_45000 = "ca/ei_overpayment_line_45000"
LINE_45300 = "ca/cwb_line_45300"
SALARIES = ["20000", "30000", "70000"]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [("20000", "-922.58"), ("30000", "1719.90"), ("70000", "14798.74")],
)
def test_t1_line_167_is_the_refund_or_balance_owing(
    salary: str, refund_or_balance_owing: str
) -> None:
    (summary,) = _worksheets(salary)[RETURN]

    assert _figure(summary, LINE_167) == D(refund_or_balance_owing)


@pytest.mark.parametrize("salary", SALARIES)
def test_line_167_is_line_149_minus_line_166(salary: str) -> None:
    worksheets = _worksheets(salary)
    (summary,) = worksheets[RETURN]
    (t1,) = worksheets[T1]
    line_143 = _figure(t1, LINE_143)
    line_147 = _figure(t1, LINE_147)
    line_148 = _figure(t1, LINE_148)
    line_166 = _figure(t1, LINE_45000) + _figure(t1, LINE_45300)

    assert line_148 == line_143 + line_147
    assert _figure(t1, LINE_166) == line_166
    assert _figure(summary, LINE_167) == line_148 - line_166


@pytest.mark.parametrize("salary", SALARIES)
def test_the_nova_scotia_form_feeds_t1_line_42800(salary: str) -> None:
    worksheets = _worksheets(salary)
    (t1,) = worksheets[T1]
    (ns428,) = worksheets[NS428]

    assert _figure(t1, LINE_147) == _figure(ns428, LINE_99)


@pytest.mark.parametrize(
    ("salary", "cpp", "ei", "nova_scotia_tax", "total_payable", "take_home"),
    [
        ("20000", "981.75", "328.00", "552.33", "710.42", "17979.83"),
        ("30000", "1576.75", "492.00", "1422.86", "2920.90", "25010.35"),
        ("70000", "3956.75", "1077.48", "7213.10", "14798.74", "50167.03"),
    ],
)
def test_the_take_home_follows_from_the_printed_figures(
    salary: str, cpp: str, ei: str, nova_scotia_tax: str, total_payable: str, take_home: str
) -> None:
    # Take-home is the salary less the income tax (T1 line 43500), EI, CPP and CPP2 (none below
    # $71,300). CPP is 4.95% of the salary over $3,500 and 1% more; EI is 1.64% of the salary up to
    # the maximum of $65,700 (T2204 line 16).
    worksheets = _worksheets(salary)
    (t1,) = worksheets[T1]
    (ns428,) = worksheets[NS428]
    cpp_total = (D(salary) - D("3500")) * D("0.0595")
    ei_total = (min(D(salary), D("65700")) * D("0.0164")).quantize(D("0.01"), ROUND_HALF_UP)

    assert (cpp_total, ei_total) == (D(cpp), D(ei))
    assert _figure(ns428, LINE_99) == D(nova_scotia_tax)
    assert _figure(t1, LINE_148) == D(total_payable)
    assert D(salary) - cpp_total - ei_total - _figure(t1, LINE_148) == D(take_home)
