"""5005-R (2025) line 159 and line 45100, real parts.

Form text (CRA 5005-R page 8, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 158: Amount from line 31210"; "Line 159 and line 45100: Net EI overpayment Line 157 minus line
158 (if negative, enter "0") ="
Line 158 is a copy of line 92, so line 92 is read directly. A salary-only filer has no EI
overpayment and a blank on line 92, so the line is 0.00 at 20,000, 70,000 and 200,000. One
core/subtract_not_below_zero, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    NET_EI_OVERPAYMENT_LINE_159,
    PPIP_PREMIUMS_PAYABLE_LINE_92,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_159_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(NET_EI_OVERPAYMENT_LINE_159).value == D("0.00")


def test_a_negative_difference_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    # Line 157 is 0.00, so any amount on line 158 (line 92) makes the difference negative.
    _, sheet = sheets(take_home_service, "70000", (PPIP_PREMIUMS_PAYABLE_LINE_92, "100.10"))

    assert sheet.get(NET_EI_OVERPAYMENT_LINE_159).value == D("0.00")


def test_line_158_is_taken_off_the_overpayment(take_home_service: TakeHomeService) -> None:
    # At 2,000 line 157 is 26.20; 10.00 on line 158 (line 92) leaves 16.20.
    _, sheet = sheets(take_home_service, "2000", (PPIP_PREMIUMS_PAYABLE_LINE_92, "10"))

    assert sheet.get(NET_EI_OVERPAYMENT_LINE_159).value == D("16.20")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 45000 (CA$0.00) less line 31210 (CA$0.00), not below 0,"
        " gives CA$0.00 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_159_kind_is_non_negative() -> None:
    assert non_negative(NET_EI_OVERPAYMENT_LINE_159) is True
