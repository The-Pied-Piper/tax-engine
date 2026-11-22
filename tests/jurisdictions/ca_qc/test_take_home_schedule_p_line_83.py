"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 83,
"Multiply line 82 by 10%", as the Quebec take-home manifest wires it: one `core/apply_rate` of line
82 by the printed 10% (`ca-qc/work_premium_reduction_rate`, no step of its own), rounded half-up to
the cent.

The expected figures of a salary-only filer are hand-computed from the printed lines (the Quebec
2025 hand calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_WORK_PREMIUM_REDUCTION_LINE_83
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_52.yaml",
    "schedule_p_line_80.yaml",
    "schedule_p_line_82.yaml",
    "schedule_p_line_83.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_reduction_line_83")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_REDUCTION_LINE_83).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 82 is 6,015.00, 55,295.00 and 184,886.00; 10% of each.
        ("20000", "601.50"),
        ("70000", "5529.50"),
        ("200000", "18488.60"),
        # Line 82 prints 0, so line 83 is 0.
        ("3000", "0.00"),
    ],
)
def test_line_83_is_line_82_times_10_percent(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected
