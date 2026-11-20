"""5005-R (2025) line 130 and line 42900, real parts.

Form text (CRA 5005-R page 7, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 130 and line 42900: Line 125 minus line 129 (if negative, enter "0") Basic federal tax ="

The figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not a CRA
example. One core/subtract_not_below_zero, rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca_qc.catalog import (
    BASIC_FEDERAL_TAX_LINE_130,
    FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77,
    MINIMUM_TAX_CARRYOVER_LINE_128,
    NON_REFUNDABLE_TAX_CREDITS_LINE_122,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "142.57"), ("70000", "7523.55"), ("200000", "39384.74")],
)
def test_a_salary_only_line_130_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(BASIC_FEDERAL_TAX_LINE_130).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_130_is_line_77_less_line_122(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert (
        sheet.get(BASIC_FEDERAL_TAX_LINE_130).value
        == sheet.get(FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77).value
        - sheet.get(NON_REFUNDABLE_TAX_CREDITS_LINE_122).value
    )


def test_a_negative_difference_is_entered_as_zero(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000", (MINIMUM_TAX_CARRYOVER_LINE_128, "100000"))

    assert sheet.get(BASIC_FEDERAL_TAX_LINE_130).value == D("0.00")


def test_the_trace_prints_the_line(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")

    assert (
        "Line 40400 (CA$10771.18) less line 129 (CA$3247.63), not below 0,"
        " gives CA$7523.55 (rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_line_130_kind_is_non_negative() -> None:
    assert non_negative(BASIC_FEDERAL_TAX_LINE_130) is True
