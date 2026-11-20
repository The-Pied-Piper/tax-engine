"""5005-R (2025) line 117 and line 33500, "Line 110 plus line 116", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 117 and line 33500: Line 110 plus line 116 =". One core/sum, rounded half-up to the cent. Line
116 is 0.00 from the salary alone, so the line equals line 110. The figures of the ticket at 20,000,
70,000 and 200,000 are 18,851.80, 22,397.47 and 22,162.72, which are also line 85 plus line 100
(16,129.00 + 2,722.80, 16,129.00 + 6,268.47 and 15,705.72 + 6,476.99; hand-computed from the printed
forms, not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    CREDIT_AMOUNTS_LINE_85,
    CREDIT_AMOUNTS_LINE_117,
    CREDITS_LINE_100,
    MEDICAL_EXPENSES_LINE_111,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18851.80"), ("70000", "22397.47"), ("200000", "22162.72")],
)
def test_a_salary_only_line_117_is_line_110(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CREDIT_AMOUNTS_LINE_117).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_117_is_line_85_plus_line_100(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert (
        sheet.get(CREDIT_AMOUNTS_LINE_117).value
        == sheet.get(CREDIT_AMOUNTS_LINE_85).value + sheet.get(CREDITS_LINE_100).value
    )


def test_the_medical_expenses_of_line_116_are_added(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (MEDICAL_EXPENSES_LINE_111, "3000"))

    assert sheet.get(CREDIT_AMOUNTS_LINE_117).value == D("23317.42")


def test_the_trace_adds_line_116_to_line_110(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (MEDICAL_EXPENSES_LINE_111, "3000"))

    assert (
        "Line 110 (CA$22397.47) plus line 33200 (CA$919.95) gives CA$23317.42 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_117_kind_is_non_negative() -> None:
    assert non_negative(CREDIT_AMOUNTS_LINE_117) is True
