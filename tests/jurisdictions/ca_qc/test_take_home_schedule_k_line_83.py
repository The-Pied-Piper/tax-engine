"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part C, line 83, as the Quebec take-home manifest
wires it. Printed as "Add lines 81 and 82 (maximum $766)".

`core/sum` adds lines 81 and 82, rounded half-up to the cent by `ca-qc/cent_rounding`, and
`core/capped_amount` takes the lesser of that sum and the printed maximum `ca-
qc/schedule_k_line_83_maximum` (766.00), so above a line 48 of $14,669 the line is $766. Line 48 is
given straight to Part C, as line 77 receives it, on both sides of each printed column edge; the
last tests run the real Part A chain from a salary. The expected figures are hand-computed from the
printed lines, not an official example.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_COLUMN_PREMIUM_BEFORE_MAXIMUM,
    SCHEDULE_K_COLUMN_PREMIUM_LINE_83,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_part_c_support import (
    COLUMNS,
    INDEX,
    PART_C,
    SALARY_COLUMNS,
    part_c,
    salary_sheet,
)
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

LINE = "ca-qc/schedule_k_column_premium_line_83"
EXPORT = "ca-qc/schedule_k_column_premium_line_83"
PARTS = PART_C
FILE = "tp1_schedule_k_line_83.yaml"


@pytest.mark.parametrize("line_48", list(COLUMNS))
def test_line_83_for_a_line_48_on_each_side_of_the_column_edges(
    take_home_service: TakeHomeService, line_48: str
) -> None:
    sheet = part_c(take_home_service, line_48, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_COLUMN_PREMIUM_LINE_83).value) == COLUMNS[line_48][INDEX["83"]]


@pytest.mark.parametrize("salary", list(SALARY_COLUMNS))
def test_line_83_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = salary_sheet(take_home_service, salary, EXPORT, PARTS)

    assert (
        str(sheet.get(SCHEDULE_K_COLUMN_PREMIUM_LINE_83).value)
        == SALARY_COLUMNS[salary][INDEX["83"]]
    )


def test_the_part_is_the_sum_then_the_cap_and_only_the_cap_prints_the_line() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    total, cap = part["capabilities"]
    assert total == {
        "name": "core/sum",
        "title": "Lines 81 and 82 added up",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/schedule_k_premium_on_excess_line_81",
                "ca-qc/schedule_k_column_constant_line_82",
            ]
        },
        "produces": {"output": "ca-qc/schedule_k_column_premium_before_maximum"},
    }
    assert cap == {
        "name": "core/capped_amount",
        "reference": "83",
        "unit": "ca/cad",
        "params": {"cap": "ca-qc/schedule_k_line_83_maximum"},
        "consumes": {"base": "ca-qc/schedule_k_column_premium_before_maximum"},
        "produces": {"output": LINE},
    }


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "ca-qc/schedule_k_column_premium_before_maximum",
            SCHEDULE_K_COLUMN_PREMIUM_BEFORE_MAXIMUM,
        ),
        (LINE, SCHEDULE_K_COLUMN_PREMIUM_LINE_83),
    ],
)
def test_the_kinds_are_registered_non_negative_decimal_amounts(name: str, expected: object) -> None:
    kind = quebec_kinds().kind(name)

    assert kind is expected
    assert non_negative(kind)


def test_the_form_declaration_exports_line_83() -> None:
    declaration = yaml.safe_load((QUEBEC_PARTS / "tp1_schedule_k.yaml").read_text("utf-8"))

    assert LINE in declaration["form"]["exports"]
