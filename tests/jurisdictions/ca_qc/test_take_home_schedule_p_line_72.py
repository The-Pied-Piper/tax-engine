"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 72,
"Subtract line 70 from line 68. If the result is negative, enter 0", as the Quebec take-home
manifest wires it: one `core/subtract_not_below_zero` of line 70 (2,400) from line 68, rounded
half-up to the cent.

The expected figures of a salary-only filer are hand-computed from the printed lines, not from a
Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_WORK_PREMIUM_INCOME_OVER_EXEMPT_LINE_72,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    SCHEDULE_P_WORK_INCOME_PARTS,
    schedule_p_form,
    schedule_p_worksheet,
)

PARTS = (
    *SCHEDULE_P_WORK_INCOME_PARTS,
    "schedule_p_line_66.yaml",
    "schedule_p_line_68.yaml",
    "schedule_p_line_70.yaml",
    "schedule_p_line_72.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_income_over_exempt_line_72")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = schedule_p_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_INCOME_OVER_EXEMPT_LINE_72).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 68 is 12,620 from a salary of 12,620 up, so line 72 is 12,620 less 2,400.
        ("20000", "10220.00"),
        ("70000", "10220.00"),
        ("200000", "10220.00"),
        # Line 68 is the salary below 12,620.
        ("5000", "2600.00"),
        # The difference is zero at 2,400 and negative below it, so line 72 prints 0.
        ("2400", "0.00"),
        ("2000", "0.00"),
    ],
)
def test_line_72_is_line_68_less_line_70_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected
