"""5005-R (2025) line 157 and line 45000, real parts.

Form text (CRA 5005-R page 8,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 157 and line 45000: Employment insurance (EI) overpayment". The amount is T2204 line 15 ("If
this amount is more than $1, enter it on line 45000 of your return"), read from the shared T2204
(Quebec EI dataset swap) by one core/record_total. A salary of 2,000 gives an overpayment of
26.20; at 20,000, 70,000 and 200,000 the line is 0.00.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import EI_OVERPAYMENT_LINE_157
from tests.jurisdictions.ca_qc.basic_personal_amount_support import sheets
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_157_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    _, sheet = sheets(take_home_service, salary)

    assert sheet.get(EI_OVERPAYMENT_LINE_157).value == D("0.00")


def test_a_low_salary_has_the_t2204_overpayment(take_home_service: TakeHomeService) -> None:
    _, sheet = sheets(take_home_service, "2000")

    assert sheet.get(EI_OVERPAYMENT_LINE_157).value == D("26.20")


def test_the_line_157_kind_is_non_negative() -> None:
    assert non_negative(EI_OVERPAYMENT_LINE_157) is True
