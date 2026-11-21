"""Quebec Schedule P (TP-1.D.P-V, 2025) Part D line 59, "Number from line 57 or line 58, whichever
is less", as the Quebec take-home manifest wires it: one `ca-qc/lesser_of_counts` of line 57 and
line 58, each blank read as 0.

Part D matters only to former recipients of last-resort financial assistance, so every figure of a
salary-only filer is 0; the other rows are hand-computed from the printed lines."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_LESSER_MONTHS_LINE_59,
    SCHEDULE_P_RL5_MONTHS_LINE_57,
    SCHEDULE_P_SUPPLEMENT_MONTHS_LINE_58,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    T1_SALARY_PARTS,
    schedule_p_form,
    schedule_p_worksheet,
)

PARTS = (
    *T1_SALARY_PARTS,
    "schedule_p_line_57_inputs.yaml",
    "schedule_p_line_58_inputs.yaml",
    "schedule_p_line_59.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_lesser_months_line_59")


def value(
    take_home_service: TakeHomeService, salary: str, line_57: str | None, line_58: str | None
) -> int:
    """The figure of the line for a filer who gives the months of lines 57 and 58, or none."""
    given = (
        (SCHEDULE_P_RL5_MONTHS_LINE_57, line_57),
        (SCHEDULE_P_SUPPLEMENT_MONTHS_LINE_58, line_58),
    )
    sheet = schedule_p_worksheet(
        take_home_service,
        FORM,
        PARTS,
        salary,
        *((kind, months) for kind, months in given if months is not None),
    )
    return sheet.get(SCHEDULE_P_LESSER_MONTHS_LINE_59).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_59_is_0(take_home_service: TakeHomeService, salary: str) -> None:
    assert value(take_home_service, salary, None, None) == 0


@pytest.mark.parametrize(
    ("line_57", "line_58", "expected"),
    [
        # Line 57 is less.
        ("4", "9", 4),
        # Line 58 is less.
        ("12", "7", 7),
        # A tie.
        ("6", "6", 6),
        # A blank line is read as 0, so the lesser is 0.
        ("5", None, 0),
        (None, "5", 0),
    ],
)
def test_line_59_is_the_lesser_of_line_57_and_line_58(
    take_home_service: TakeHomeService, line_57: str | None, line_58: str | None, expected: int
) -> None:
    assert value(take_home_service, "70000", line_57, line_58) == expected
