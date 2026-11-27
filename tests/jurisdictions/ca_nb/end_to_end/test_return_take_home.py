"""The New Brunswick take-home return (2025): T1 line 167, "Refund or balance owing",
from the salary alone, with the real New Brunswick manifest composed end to end.

The registered engine (`build_tax_computation`) runs over the real New Brunswick 2025
manifest, with the gross salary (`ca/employment_income`) the only input and every optional input
left blank. The return sheet (`ca-nb/return`) holds T1 line 167 at salaries of $20,000, $30,000,
$70,000 and $200,000: -1,474.91 / 1,095.80 / 13,262.53 / 65,517.87 (positive is a balance owing,
negative a refund).

Form text (T1 General 5006-R): "Line 147 and line 42800: Provincial or territorial tax", "Line 148
and line 43500: Add lines 143 to 147. Total payable", "Line 166 and line 48200: Add lines 150 to
165. Total credits" and "Line 167: Line 149 minus line 166 ... Refund or balance owing", line 149
being "Enter the amount from line 148 of the previous page.". So line 167 is the total payable
(line 148) less the total credits (line 166); the tests tie it to the T1 form's own sheet, to NB428
line 97 (T1 line 42800) and, at $70,000, to a take-home worked from the printed CPP and EI figures.
New Brunswick has no provincial credits form here, so T1 line 47900 is blank. The line
143 figure (net federal tax, line 42000) is read from the T1 sheet: it is pinned by the federal
tests, and it is the same figure the Saskatchewan return reads at the same salaries.
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
NEW_BRUNSWICK = JurisdictionCode("CA-NB")
RETURN = "ca-nb/return"
T1 = "ca/t1_tax_and_credits"
NB428 = "ca-nb/nb428"
LINE_167 = "ca/refund_or_balance_owing"
LINE_97 = "ca-nb/nb428_new_brunswick_tax_line_97"
LINE_143 = "ca/net_federal_tax"
LINE_147 = "ca/provincial_tax_line_42800"
LINE_148 = "ca/total_payable"
LINE_166 = "ca/total_credits"
LINE_45000 = "ca/ei_overpayment_line_45000"
LINE_45300 = "ca/cwb_line_45300"
SALARIES = ["20000", "30000", "70000", "200000"]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(NEW_BRUNSWICK, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [
        ("20000", "-1474.91"),
        ("30000", "1095.80"),
        ("70000", "13262.53"),
        ("200000", "65517.87"),
    ],
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
def test_the_new_brunswick_form_feeds_t1_line_42800(salary: str) -> None:
    worksheets = _worksheets(salary)
    (t1,) = worksheets[T1]
    (nb428,) = worksheets[NB428]

    assert _figure(t1, LINE_147) == _figure(nb428, LINE_97)


def test_the_70000_take_home_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("70000")
    (t1,) = worksheets[T1]
    (summary,) = worksheets[RETURN]
    cpp = (D("70000") - D("3500")) * D("0.0595")
    ei = D("1077.48")
    total_payable = _figure(t1, LINE_143) + D("5676.89")
    take_home = D("70000") - cpp - ei - total_payable

    assert cpp == D("3956.75")
    assert _figure(summary, LINE_167) == total_payable
    assert total_payable == D("13262.53")
    assert take_home == D("51703.24")
    assert D("70000") - cpp - ei - _figure(summary, LINE_167) == take_home
