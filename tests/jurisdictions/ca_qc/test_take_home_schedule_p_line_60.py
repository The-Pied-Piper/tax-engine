"""Quebec Schedule P (TP-1.D.P-V, 2025) Part D line 60, "Multiply line 56 by line 59", as the Quebec
take-home manifest wires it: one `core/times_count` of line 56 (the printed 200.00 for each month)
by line 59 (the lesser of the months of lines 57 and 58), rounded half-up to the cent.

Part D matters only to former recipients of last-resort financial assistance, so every figure of a
salary-only filer is 0.00; the other rows are hand-computed from the printed lines, not from a
Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_RL5_MONTHS_LINE_57,
    SCHEDULE_P_SUPPLEMENT_LINE_60,
    SCHEDULE_P_SUPPLEMENT_MONTHS_LINE_58,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    schedule_p_form,
    schedule_p_worksheet,
)

PARTS = (
    "salary.yaml",
    "schedule_p_line_56.yaml",
    "schedule_p_line_57_inputs.yaml",
    "schedule_p_line_58_inputs.yaml",
    "schedule_p_line_59.yaml",
    "schedule_p_line_60.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_supplement_line_60")


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_60_is_0(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_p_worksheet(take_home_service, FORM, PARTS, salary)

    assert str(sheet.get(SCHEDULE_P_SUPPLEMENT_LINE_60).value) == "0.00"


@pytest.mark.parametrize(
    ("line_57", "line_58", "expected"),
    [
        # Line 57 is the lesser: 4 months of 200.00.
        ("4", "9", "800.00"),
        # Line 58 is the lesser: 7 months of 200.00.
        ("12", "7", "1400.00"),
        # A full year.
        ("12", "12", "2400.00"),
    ],
)
def test_line_60_is_line_56_times_the_lesser_months(
    take_home_service: TakeHomeService, line_57: str, line_58: str, expected: str
) -> None:
    sheet = schedule_p_worksheet(
        take_home_service,
        FORM,
        PARTS,
        "70000",
        (SCHEDULE_P_RL5_MONTHS_LINE_57, line_57),
        (SCHEDULE_P_SUPPLEMENT_MONTHS_LINE_58, line_58),
    )

    assert str(sheet.get(SCHEDULE_P_SUPPLEMENT_LINE_60).value) == expected
