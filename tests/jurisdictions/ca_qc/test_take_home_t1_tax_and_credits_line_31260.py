"""5005-R (2025) line 96 and line 31260, "Canada employment amount", real parts.

Form text (CRA 5005-R page 6, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 96 and line 31260: Enter whichever is less: $1,471 or line 1 plus line 2." Line 1 is
line 10100 and line 2 is line 10400, both read from the T1's exports. Two
steps, as the federal line 31260 is built: a core/sum of the two lines, then a core/capped_amount
at the printed $1,471 (the shared dataset `ca/canada_employment_amount`). The figures are
hand-computed from the printed form (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.jurisdictions.ca.catalog.income import OTHER_EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT_INCOME,
)
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_above_1471_gives_the_printed_1471(
    take_home_service: TakeHomeService, salary: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1471.00")


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("1000", "1000.00"), ("1470.99", "1470.99"), ("1471", "1471.00"), ("1471.01", "1471.00")],
)
def test_a_salary_at_or_below_1471_is_the_amount_itself(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D(expected)


def test_line_2_is_added_to_line_1_before_the_limit(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "1000", (OTHER_EMPLOYMENT_INCOME, "300.50"))

    assert sheet.get(CANADA_EMPLOYMENT_AMOUNT_INCOME).value == D("1300.50")
    assert sheet.get(CANADA_EMPLOYMENT_AMOUNT).value == D("1300.50")


def test_a_sub_cent_sum_is_carried_unrounded(take_home_service: TakeHomeService) -> None:
    # 5005-R prints no rounding rule for "line 1 plus line 2", so 1000.004 plus 300.003 stays
    # 1300.007 rather than rounding to 1300.01.
    _, sheet = sheets(take_home_service, "1000.004", (OTHER_EMPLOYMENT_INCOME, "300.003"))

    assert sheet.get(CANADA_EMPLOYMENT_AMOUNT_INCOME).value == D("1300.007")


def test_the_trace_names_the_sum_and_the_limit(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "70000")
    trace = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert (
        '"Employment income from line 10100" (CA$70000.00) plus '
        '"Other employment income from line 10400" (CA$0.00) gives CA$70000.00 '
        "(not rounded)."
    ) in trace
    assert (
        'Lesser of "Employment income plus other employment income, before the limit" '
        "(CA$70000.00) and the Canada employment amount (CA$1471.00) gives CA$1471.00 "
        "(not rounded)."
    ) in trace


def test_the_kinds_are_non_negative() -> None:
    assert non_negative(CANADA_EMPLOYMENT_AMOUNT_INCOME) is True
    assert non_negative(CANADA_EMPLOYMENT_AMOUNT) is True
