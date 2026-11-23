"""The Manitoba take-home return (2025): T1 line 167, "Refund or balance owing", from the salary
alone, with the real Manitoba manifest composed end to end.

The registered engine (`build_tax_computation`) runs over the real Manitoba 2025 manifest, with the
gross salary (`ca/employment_income`) the only input and every optional input left blank. The
return sheet (`ca-mb/return`) holds T1 line 167 at salaries of $10,000, $20,000, $70,000, $200,000
and $250,000: -1,728.65 / -1,190.83 / 13,333.23 / 66,331.29 / 90,100.91 (positive is a balance
owing, negative a refund).

Form text (T1 General 5006-R, CRA 5006-r-25e.txt): "Line 147 and line 42800: Provincial or
territorial tax", "Line 148 and line 43500: Add lines 143 to 147. Total payable", "Line 166 and
line 48200: Add lines 150 to 165. Total credits" and "Line 167: Line 149 minus line 166 ... Refund
or balance owing", line 149 being "Enter the amount from line 148 of the previous page.". So line
167 is the total payable (line 148) less the total credits (line 166); the tests tie it to the T1
form's own sheet, to MB428 line 82 (T1 line 42800), to MB479 line 81 (T1 line 47900) and, at
$70,000, to a take-home worked from the printed CPP and EI figures. The line 143 figure (net
federal tax, line 42000) is read from the T1 sheet: it is pinned by the federal tests.
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
MANITOBA = JurisdictionCode("CA-MB")
RETURN = "ca-mb/return"
T1 = "ca/t1_tax_and_credits"
MB428 = "ca-mb/mb428"
MB479 = "ca-mb/mb479"
LINE_167 = "ca/refund_or_balance_owing"
LINE_82 = "ca-mb/mb428_manitoba_tax_line_82"
LINE_81 = "ca-mb/mb479_manitoba_credits_line_81"
LINE_143 = "ca/net_federal_tax"
LINE_147 = "ca/provincial_tax_line_42800"
LINE_148 = "ca/total_payable"
LINE_166 = "ca/total_credits"
LINE_45000 = "ca/ei_overpayment_line_45000"
LINE_45300 = "ca/cwb_line_45300"
LINE_47900 = "ca/provincial_credits_line_47900"
SALARIES = ["10000", "20000", "70000", "200000", "250000"]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(MANITOBA, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


@pytest.mark.parametrize(
    ("salary", "refund_or_balance_owing"),
    [
        # Line 166: 1,633.00 (Canada workers benefit) plus 95.65 (MB479 line 81), against no tax.
        ("10000", "-1728.65"),
        ("20000", "-1190.83"),
        ("70000", "13333.23"),
        ("200000", "66331.29"),
        ("250000", "90100.91"),
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
    line_166 = _figure(t1, LINE_45000) + _figure(t1, LINE_45300) + _figure(t1, LINE_47900)

    assert line_148 == line_143 + line_147
    assert _figure(t1, LINE_166) == line_166
    assert _figure(summary, LINE_167) == line_148 - line_166


@pytest.mark.parametrize("salary", SALARIES)
def test_the_manitoba_forms_feed_t1_lines_42800_and_47900(salary: str) -> None:
    worksheets = _worksheets(salary)
    (t1,) = worksheets[T1]
    (mb428,) = worksheets[MB428]
    (mb479,) = worksheets[MB479]

    assert _figure(t1, LINE_147) == _figure(mb428, LINE_82)
    assert _figure(t1, LINE_47900) == _figure(mb479, LINE_81)


def test_the_70000_take_home_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("70000")
    (t1,) = worksheets[T1]
    (summary,) = worksheets[RETURN]
    cpp = (D("70000") - D("3500")) * D("0.0595")
    ei = D("1077.48")
    total_payable = _figure(t1, LINE_143) + D("5747.59")
    take_home = D("70000") - cpp - ei - total_payable

    assert cpp == D("3956.75")
    assert _figure(summary, LINE_167) == total_payable
    assert take_home == D("51632.54")
    assert D("70000") - cpp - ei - _figure(summary, LINE_167) == take_home
