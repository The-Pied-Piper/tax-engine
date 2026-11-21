"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 44, as the Quebec take-home manifest
wires it. Printed as "If you did not have a spouse on December 31, 2025, but you had a dependent
child (see line 447 in the guide for the definition), enter $12,350. If you had more than one
dependent child, enter $16,570."

The number of dependent children is an optional input, read as 0 when left out. Two
`ca/count_by_conditions` read the two questions the line asks (a dependent child: more than 0; more
than one: more than 1), `core/choose_by_count` picks the printed $16,570 or $12,350, and
`core/times_count` makes the figure 0 when the filer had no dependent child. Line 42, for a filer
with a spouse, has no step. The expected figures are the printed amounts.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_AMOUNT_LINE_44,
    SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_amount_line_44"
PART = "tp1_schedule_k_line_44.yaml"
PARTS = ("tp1_schedule_k_line_44_input.yaml", "tp1_schedule_k_line_44_amounts.yaml", PART)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_a_salary_only_line_44_is_zero(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_AMOUNT_LINE_44).value) == "0.00"


@pytest.mark.parametrize(
    ("children", "expected"),
    [("0", "0.00"), ("1", "12350.00"), ("2", "16570.00"), ("3", "16570.00"), ("10", "16570.00")],
)
def test_line_44_is_the_printed_amount_for_the_number_of_dependent_children(
    take_home_service: TakeHomeService, children: str, expected: str
) -> None:
    given = (SCHEDULE_K_DEPENDENT_CHILDREN_LINE_44, children)
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_AMOUNT_LINE_44).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_two_conditions_one_choice_and_one_count_with_line_44_on_the_last() -> None:
    steps = _part()["capabilities"]

    assert [step["name"] for step in steps] == [
        "ca/count_by_conditions",
        "ca/count_by_conditions",
        "core/choose_by_count",
        "core/times_count",
    ]
    assert [step.get("reference") for step in steps] == [None, None, None, "44"]
    assert [step["params"]["conditions"] for step in steps[:2]] == [
        "ca-qc/schedule_k_had_dependent_child_conditions",
        "ca-qc/schedule_k_more_than_one_dependent_child_conditions",
    ]
    assert steps[2]["consumes"] == {
        "count": "ca-qc/schedule_k_more_than_one_dependent_child_line_44",
        "when_none": "ca-qc/schedule_k_line_44_one_child_amount",
        "when_any": "ca-qc/schedule_k_line_44_more_than_one_child_amount",
    }
    assert steps[3]["produces"] == {"output": EXPORT}
