"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 46, as the Quebec take-home manifest
wires it. Printed as "Add line 41 and, as applicable, line 42 or line 44".

`core/sum` adds line 41 (the printed 19,890) and line 44 (the dependent child amount, 0 when the
filer had no dependent child; line 42 is for a filer with a spouse and has no step), rounded
half-up to the cent by `ca-qc/cent_rounding`.
The expected figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44,
    SCHEDULE_K_TOTAL_LINE_46,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_total_line_46"
PARTS = (
    "tp1_schedule_k_line_41.yaml",
    "tp1_schedule_k_line_44_input.yaml",
    "tp1_schedule_k_line_44_amounts.yaml",
    "tp1_schedule_k_line_44.yaml",
    "tp1_schedule_k_line_46.yaml",
)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_46_is_line_41_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_TOTAL_LINE_46).value) == "19890.00"


@pytest.mark.parametrize(("children", "expected"), [("1", "32240.00"), ("2", "36460.00")])
def test_the_dependent_child_amount_of_line_44_is_added(
    take_home_service: TakeHomeService, children: str, expected: str
) -> None:
    given = (SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44, children)
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_TOTAL_LINE_46).value) == expected


def test_the_part_is_one_sum_of_lines_41_and_44() -> None:
    part = yaml.safe_load(
        (QUEBEC_PARTS / "tp1_schedule_k_line_46.yaml").read_text(encoding="utf-8")
    )
    (step,) = part["capabilities"]

    assert step["name"] == "core/sum"
    assert step["consumes"]["parts"] == [
        "ca-qc/schedule_k_amount_line_41",
        "ca-qc/schedule_k_amount_line_44",
    ]
    assert "blank" not in step
    assert step["params"] == {"rounding": "ca-qc/cent_rounding"}
