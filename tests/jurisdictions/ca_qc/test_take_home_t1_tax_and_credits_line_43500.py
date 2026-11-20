"""5005-R (2025) line 151 and line 43500, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 151 and line 43500: Add lines 147 to 150. Total payable ="
Line 147 is "Amount from line 42000", a pure copy of line 146, so it is not a step. Lines 148 and
150 are optional inputs, a blank for a salary-only filer and read as 0; line 149 is the social
benefits repayment. The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed
forms, not a CRA example. One core/sum, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.deductions import SOCIAL_BENEFITS_REPAYMENT
from tax_engine.jurisdictions.ca_qc.catalog import (
    EI_PREMIUMS_SELF_EMPLOYED_LINE_148,
    PROVINCIAL_TAX_LINE_150,
    TOTAL_PAYABLE_LINE_151,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "142.57"), ("70000", "7523.55"), ("200000", "39384.74")],
)
def test_a_salary_only_line_151_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(TOTAL_PAYABLE_LINE_151).value == D(expected)


@pytest.mark.parametrize("kind", [EI_PREMIUMS_SELF_EMPLOYED_LINE_148, PROVINCIAL_TAX_LINE_150])
def test_each_optional_line_is_taken(take_home_service: TakeHomeService, kind: AmountKind) -> None:
    _, sheet = sheets(take_home_service, "70000", (kind, "100.10"))

    assert sheet.get(TOTAL_PAYABLE_LINE_151).value == D("7623.65")


def test_the_social_benefits_repayment_is_added(take_home_service: TakeHomeService) -> None:
    # 100 of repayment lowers net income by 100, so line 146 falls by 20.50 and line 149 adds 100.
    _, sheet = sheets(take_home_service, "70000", (SOCIAL_BENEFITS_REPAYMENT, "100"))

    assert sheet.get(TOTAL_PAYABLE_LINE_151).value == D("7603.05")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 42000 (CA$7523.55) plus line 42120 (CA$0.00) plus line 42200 (CA$0.00)"
        " plus line 42800 (CA$0.00) gives CA$7523.55 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_151_kind_is_non_negative() -> None:
    assert non_negative(TOTAL_PAYABLE_LINE_151) is True
