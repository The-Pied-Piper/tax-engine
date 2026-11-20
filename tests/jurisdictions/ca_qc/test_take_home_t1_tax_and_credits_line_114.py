"""5005-R (2025) line 114, "Line 111 minus line 113 (if negative, enter "0")", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 114: Line 111 minus line 113 (if negative, enter "0") =". Line 111 (line 33099, medical
expenses) is an optional input, left blank by a salary-only filer and read as 0, so the line is 0.00
from the salary alone. One core/subtract_not_below_zero. With medical expenses of 3,000.00 against a
line 113 of 595.05, 2,080.05 and 2,834.00 at 20,000, 70,000 and 200,000, the hand figures are
2,404.95, 919.95 and 166.00 (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    MEDICAL_EXPENSES_LINE_111,
    MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_114_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114).value == D("0.00")


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2404.95"), ("70000", "919.95"), ("200000", "166.00")],
)
def test_medical_expenses_over_the_threshold_are_line_114(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary, (MEDICAL_EXPENSES_LINE_111, "3000"))

    assert sheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114).value == D(expected)


def test_medical_expenses_under_the_threshold_give_zero(
    take_home_service: TakeHomeService,
) -> None:
    _, sheet = sheets(take_home_service, "70000", (MEDICAL_EXPENSES_LINE_111, "2000"))

    assert sheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114).value == D("0.00")


def test_the_trace_takes_line_113_off_line_111(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (MEDICAL_EXPENSES_LINE_111, "3000"))

    assert (
        "Line 33099 (CA$3000.00) less line 113 (CA$2080.05), not below 0, gives "
        "CA$919.95 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_114_kind_is_non_negative() -> None:
    assert non_negative(MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114) is True
