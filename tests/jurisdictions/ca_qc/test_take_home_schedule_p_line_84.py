"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 84,
"Subtract line 83 from line 76. If the result is negative, enter 0", as the Quebec take-home
manifest wires it: one `core/subtract_not_below_zero` of line 83 from line 76, rounded half-up to
the cent. Line 87 ("Amount from line 84 in column 1 or column 2, whichever is greater") has no
step: column 2 is left out, so line 87 is line 84, and line 90 reads it.

The line 52 to 54 and line 76 chains run for real, over the real TP-1 income parts. The expected
figures of a salary-only filer are hand-computed from the printed lines (the Quebec 2025 hand
calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_WORK_PREMIUM_LINE_87,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_10.yaml",
    "schedule_p_line_14_inputs.yaml",
    "schedule_p_line_12.yaml",
    "schedule_p_line_13.yaml",
    "schedule_p_line_15.yaml",
    "schedule_p_line_18.yaml",
    "schedule_p_line_22_inputs.yaml",
    "schedule_p_line_29.yaml",
    "schedule_p_line_52.yaml",
    "schedule_p_line_66.yaml",
    "schedule_p_line_68.yaml",
    "schedule_p_line_70.yaml",
    "schedule_p_line_72.yaml",
    "schedule_p_line_76.yaml",
    "schedule_p_line_80.yaml",
    "schedule_p_line_82.yaml",
    "schedule_p_line_83.yaml",
    "schedule_p_line_84.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_line_87")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_LINE_87).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 76 is 1,185.52 and line 83 is 601.50, so line 84 is 584.02.
        ("20000", "584.02"),
        # Line 83 is 5,529.50 and 18,488.60, above line 76, so the difference prints 0.
        ("70000", "0.00"),
        ("200000", "0.00"),
        # Line 76 is 69.60 (11.6% of 600.00) and line 82 prints 0 (3,000 is below 12,620), so
        # line 84 is line 76.
        ("3000", "69.60"),
    ],
)
def test_line_84_is_line_76_less_line_83_not_below_zero(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected
