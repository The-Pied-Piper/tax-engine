"""5005-R (2025) line 102, "Add lines 86, 100, and 101", from the salary alone, real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 102: Add lines 86, 100, and 101. =". Line 86 is a copy of line 85, line 100 is the credits of
lines 87 to 99 and line 101 (line 31400) is an optional input read as 0 for a salary-only filer. One
core/sum, rounded half-up to the cent. The hand figures at 20,000, 70,000 and 200,000 are line 85
plus line 100 (the line 117 figures of the ticket, lines 101 and 103 to 109 being blank): 16,129.00
+ 2,722.80, 16,129.00 + 6,268.47 and 15,705.72 + 6,476.99 (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import CREDITS_LINE_102, PENSION_INCOME_AMOUNT_LINE_101
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18851.80"), ("70000", "22397.47"), ("200000", "22162.72")],
)
def test_a_salary_only_line_102_adds_lines_86_and_100(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CREDITS_LINE_102).value == D(expected)


def test_the_pension_income_amount_is_added(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (PENSION_INCOME_AMOUNT_LINE_101, "100.10"))

    assert sheet.get(CREDITS_LINE_102).value == D("22497.57")


def test_the_trace_adds_the_lines_in_form_order(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 85 (CA$16129.00) plus line 100 (CA$6268.47) plus line 31400 (CA$0.00) gives "
        "CA$22397.47 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_102_kind_is_non_negative() -> None:
    assert non_negative(CREDITS_LINE_102) is True
