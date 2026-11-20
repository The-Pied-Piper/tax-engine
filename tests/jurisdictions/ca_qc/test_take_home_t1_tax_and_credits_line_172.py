"""5005-R (2025) line 172, real parts.

Form text (CRA 5005-R page 8, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 172: Line 152 minus line 171 If the amount is negative, enter it on line 48400 below. If the
amount is positive, enter it on line 48500 below. Refund or balance owing ="
Line 152 is "Enter the amount from line 151 of the previous page", a pure copy, so line 151 is read
directly. The form prints no floor, so the figure is signed: negative is a refund (line 48400),
positive a balance owing (line 48500). The figures at 20,000, 70,000 and 200,000 are hand-computed
from the printed forms, not a CRA example (at 70,000 and 200,000 line 172 is line 151 less the
abatement of line 156). One core/subtract, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    REFUND_OR_BALANCE_OWING_LINE_172,
    TAX_PAID_BY_INSTALMENTS_LINE_170,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "-2560.02"), ("70000", "6282.16"), ("200000", "32886.26")],
)
def test_a_salary_only_line_172_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(REFUND_OR_BALANCE_OWING_LINE_172).value == D(expected)


def test_credits_over_the_total_payable_give_a_refund(take_home_service: TakeHomeService) -> None:
    # 7,523.55 payable less 1,241.39 and 10,000.00 of credits is a refund of 3,717.84.
    _, sheet = sheets(take_home_service, "70000", (TAX_PAID_BY_INSTALMENTS_LINE_170, "10000"))

    assert sheet.get(REFUND_OR_BALANCE_OWING_LINE_172).value == D("-3717.84")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "20000")

    assert (
        "Line 43500 (CA$142.57) less line 48200 (CA$2702.59) gives -CA$2560.02"
        " (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_172_kind_is_signed() -> None:
    assert non_negative(REFUND_OR_BALANCE_OWING_LINE_172) is False
