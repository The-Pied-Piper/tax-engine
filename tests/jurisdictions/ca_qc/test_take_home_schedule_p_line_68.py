"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 68, "Amount
from line 64 or line 66, whichever is less", as the Quebec take-home manifest wires it: one
`core/lesser_of` of line 64 (a copy of line 29, the work income) and line 66 (12,620). A tie keeps
line 64.

The expected figures of a salary-only filer are hand-computed from the printed lines, not from a
Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_WORK_PREMIUM_INCOME_LINE_68
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
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_income_line_68")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = schedule_p_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_INCOME_LINE_68).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 64 (the salary) is below line 66.
        ("5000", "5000.00"),
        # Line 64 is above line 66, so line 66 is kept.
        ("20000", "12620.00"),
        ("70000", "12620.00"),
        ("200000", "12620.00"),
        # A tie: line 64 equals line 66.
        ("12620", "12620.00"),
    ],
)
def test_line_68_is_the_lesser_of_line_64_and_line_66(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected
