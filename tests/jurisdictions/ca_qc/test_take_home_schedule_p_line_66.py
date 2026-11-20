"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2 "Individual without a spouse on December
31, 2025", column 1 "Work premium", line 66, as the Quebec take-home manifest wires it: the printed
12,620, a dataset figure (`ca-qc/work_premium_income_ceiling`) claimed whole by one
`core/credit_amount`, whatever the salary."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_WORK_PREMIUM_INCOME_CEILING_LINE_66
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    schedule_p_form,
    schedule_p_worksheet,
)

PARTS = (
    "salary.yaml",
    "schedule_p_line_66.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_income_ceiling_line_66")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = schedule_p_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_INCOME_CEILING_LINE_66).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_66_is_the_printed_12620_at_each_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert value(take_home_service, salary) == "12620.00"
