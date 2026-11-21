"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 82,
"Subtract line 80 from line 78. If the result is negative, enter 0", as the Quebec take-home
manifest wires it: one `core/subtract_not_below_zero` of line 80 (12,620) from line 78, which is a
copy of line 54 and has no step of its own, rounded half-up to the cent.

The expected figures of a salary-only filer are hand-computed from the printed lines (the Quebec
2025 hand calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_FAMILY_INCOME_OVER_THRESHOLD_LINE_82
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_52.yaml",
    "schedule_p_line_53.yaml",
    "schedule_p_line_54.yaml",
    "schedule_p_line_80.yaml",
    "schedule_p_line_82.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_family_income_over_threshold_line_82")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_FAMILY_INCOME_OVER_THRESHOLD_LINE_82).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 78 is 18,635.00, 67,915.00 and 197,506.00; each less 12,620.00.
        ("20000", "6015.00"),
        ("70000", "55295.00"),
        ("200000", "184886.00"),
    ],
)
def test_line_82_is_line_78_less_line_80(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected


def test_line_82_prints_0_when_line_78_is_below_line_80(
    take_home_service: TakeHomeService,
) -> None:
    # A salary of 3,000 gives a family income below 12,620, so the negative difference prints 0.
    assert value(take_home_service, "3000") == "0.00"
