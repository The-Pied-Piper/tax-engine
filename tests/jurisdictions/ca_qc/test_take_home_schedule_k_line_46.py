"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 46, as the Quebec take-home manifest
wires it. Printed as "Add line 41 and, as applicable, line 42 or line 44".

`core/sum` adds line 41 (the printed 19,890) and the dependent child amount of line 42 or 44 (an
optional input, read as 0 when left blank), rounded half-up to the cent by `ca-qc/cent_rounding`.
The expected figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44,
    SCHEDULE_K_TOTAL_LINE_46,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_total_line_46"
PARTS = (
    "tp1_schedule_k_line_41.yaml",
    "tp1_schedule_k_line_42_or_44_input.yaml",
    "tp1_schedule_k_line_46.yaml",
)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_46_is_line_41_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_TOTAL_LINE_46).value) == "19890.00"


def test_the_dependent_child_amount_is_added(take_home_service: TakeHomeService) -> None:
    given = (SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44, "6000.25")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_TOTAL_LINE_46).value) == "25890.25"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    given = (SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44, "0.005")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_TOTAL_LINE_46).value) == "19890.01"
