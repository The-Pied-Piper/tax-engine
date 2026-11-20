"""5005-R (2025) line 116 and line 33200, "Line 114 plus line 115", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 116 and line 33200: Line 114 plus line 115 =". Line 114 is the medical expenses over the
threshold and line 115 (line 33199, allowable medical expenses for other dependants) is an optional
input, left blank by a salary-only filer and read as 0, so the line is 0.00 from the salary alone.
One core/sum, rounded half-up to the cent. With medical expenses of 3,000.00 at 70,000 line 114 is
919.95 (hand-computed from the printed forms, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    MEDICAL_EXPENSES_LINE_111,
    MEDICAL_EXPENSES_LINE_116,
    MEDICAL_EXPENSES_OTHER_DEPENDANTS_LINE_115,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_116_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(MEDICAL_EXPENSES_LINE_116).value == D("0.00")


def test_line_115_is_added(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(
        take_home_service, "70000", (MEDICAL_EXPENSES_OTHER_DEPENDANTS_LINE_115, "100.10")
    )

    assert sheet.get(MEDICAL_EXPENSES_LINE_116).value == D("100.10")


def test_lines_114_and_115_are_added_in_one_sum(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(
        take_home_service,
        "70000",
        (MEDICAL_EXPENSES_LINE_111, "3000"),
        (MEDICAL_EXPENSES_OTHER_DEPENDANTS_LINE_115, "100.10"),
    )

    assert sheet.get(MEDICAL_EXPENSES_LINE_116).value == D("1020.05")


def test_the_trace_adds_line_115_to_line_114(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(
        take_home_service,
        "70000",
        (MEDICAL_EXPENSES_LINE_111, "3000"),
        (MEDICAL_EXPENSES_OTHER_DEPENDANTS_LINE_115, "100.10"),
    )

    assert (
        "Line 114 (CA$919.95) plus line 33199 (CA$100.10) gives CA$1020.05 (rounded "
        "to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_116_kind_is_non_negative() -> None:
    assert non_negative(MEDICAL_EXPENSES_LINE_116) is True
