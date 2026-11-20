"""5005-R (2025) line 143 and line 41700, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 143 and line 41700: Line 138 minus line 142 (if negative, enter "0") ="
Line 142 (the sum of lines 139 to 141) is one optional input, a blank for a salary-only filer and
read as 0. The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not
a CRA example. One core/subtract_not_below_zero, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_CREDITS_LINE_142,
    FEDERAL_TAX_LESS_CREDITS_LINE_143,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "142.57"), ("70000", "7523.55"), ("200000", "39384.74")],
)
def test_a_salary_only_line_143_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(FEDERAL_TAX_LESS_CREDITS_LINE_143).value == D(expected)


def test_line_142_is_taken(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (FEDERAL_CREDITS_LINE_142, "100.10"))

    assert sheet.get(FEDERAL_TAX_LESS_CREDITS_LINE_143).value == D("7423.45")


def test_a_negative_difference_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (FEDERAL_CREDITS_LINE_142, "10000"))

    assert sheet.get(FEDERAL_TAX_LESS_CREDITS_LINE_143).value == D("0.00")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 40600 (CA$7523.55) less line 41600 (CA$0.00), not below 0,"
        " gives CA$7523.55 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_143_kind_is_non_negative() -> None:
    assert non_negative(FEDERAL_TAX_LESS_CREDITS_LINE_143) is True
