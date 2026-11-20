"""5005-R (2025) line 161 and line 45300, real parts.

Form text (CRA 5005-R page 8,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 161 and line 45300: Canada workers benefit (CWB) (complete Schedule 6)"; Schedule 6 (5005-S6)
line 28: "Line 22 minus line 27 (if negative, enter "0") If you are not completing Step 3, enter
this amount on line 45300 of your return."
The amount is Schedule 6 line 28 with the Quebec dataset swaps, read by one core/record_total. The
figures at 20,000, 70,000 and 200,000 are hand-computed from the printed forms, not a CRA example.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import CWB_LINE_161
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2679.07"), ("70000", "0.00"), ("200000", "0.00")],
)
def test_a_salary_only_line_161_is_the_printed_figure(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(CWB_LINE_161).value == D(expected)


def test_a_low_salary_gets_the_working_income_part(take_home_service: TakeHomeService) -> None:
    # (12,000 - 2,400) x 37.3% = 3,580.80, under the 3,812.06 maximum and the 33,230.35 chart limit.
    _, sheet = sheets(take_home_service, "12000")

    assert sheet.get(CWB_LINE_161).value == D("3580.80")


def test_the_line_161_kind_is_non_negative() -> None:
    assert non_negative(CWB_LINE_161) is True
