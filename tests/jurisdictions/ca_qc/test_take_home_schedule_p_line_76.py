"""Quebec Schedule P (TP-1.D.P-V, 2025) Part E, section 2, column 1 "Work premium", line 76,
"Multiply line 72 by line 74 or line 75 (as applicable)", as the Quebec take-home manifest wires
it: one `core/apply_rate` of line 72 by the printed 11.6% of line 74 (`ca-qc/work_premium_rate`, no
step of its own; the take-home designates no child, so the 30% does not apply), rounded half-up to
the cent. Line 84 reads the figure.

The expected figures of a salary-only filer are hand-computed from the printed lines, not from a
Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_WORK_PREMIUM_BEFORE_REDUCTION_LINE_76
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
    "schedule_p_line_76.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_work_premium_before_reduction_line_76")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = schedule_p_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_WORK_PREMIUM_BEFORE_REDUCTION_LINE_76).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 72 is 10,220.00 and 11.6% of it is 1,185.52.
        ("20000", "1185.52"),
        ("70000", "1185.52"),
        ("200000", "1185.52"),
        # Line 72 is 2,600.00 and 11.6% of it is 301.60.
        ("5000", "301.60"),
        # Line 72 prints 0, so line 76 is 0.
        ("2000", "0.00"),
    ],
)
def test_line_76_is_line_72_times_11_6_percent(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected


def test_line_76_rounds_half_up_to_the_cent_from_the_rate_dataset(
    take_home_service: TakeHomeService,
) -> None:
    # Line 72 is 1.25 (a salary of 2,401.25 less 2,400.00). 11.6% of it is 0.145, which rounds
    # half-up to 0.15.
    assert value(take_home_service, "2401.25") == "0.15"
