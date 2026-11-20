"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part C, line 78, as the Quebec take-home manifest
wires it. Printed as "0,000 00 | 5,000 00" under columns A and B.

`core/bracket_column_lower_bound` over line 48 (line 77 is a copy and has no step) with `ca-
qc/schedule_k_brackets`: the printed lower bound of the column line 48 falls in, 0.00 up to $5,000
and 5,000.00 above. Line 48 is given straight to Part C, as line 77 receives it, on both sides of
each printed column edge; the last tests run the real Part A chain from a salary. The expected
figures are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_COLUMN_LOWER_BOUND_LINE_78
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

LINE = "ca-qc/schedule_k_column_lower_bound_line_78"
EXPORT = "ca-qc/schedule_k_column_premium_line_83"
PARTS = PART_C
FILE = "tp1_schedule_k_line_78.yaml"


@pytest.mark.parametrize("line_48", list(COLUMNS))
def test_line_78_for_a_line_48_on_each_side_of_the_column_edges(
    take_home_service: TakeHomeService, line_48: str
) -> None:
    sheet = part_c(take_home_service, line_48, EXPORT, PARTS)

    assert (
        str(sheet.get(SCHEDULE_K_COLUMN_LOWER_BOUND_LINE_78).value) == COLUMNS[line_48][INDEX["78"]]
    )


@pytest.mark.parametrize("salary", list(SALARY_COLUMNS))
def test_line_78_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = salary_sheet(take_home_service, salary, EXPORT, PARTS)

    assert (
        str(sheet.get(SCHEDULE_K_COLUMN_LOWER_BOUND_LINE_78).value)
        == SALARY_COLUMNS[salary][INDEX["78"]]
    )


def test_the_part_is_one_step_as_printed() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/bracket_column_lower_bound",
        "reference": "78",
        "unit": "ca/cad",
        "params": {"schedule": "ca-qc/schedule_k_brackets"},
        "consumes": {"base": "ca-qc/schedule_k_premium_income_line_48"},
        "produces": {"output": LINE},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE)

    assert kind is SCHEDULE_K_COLUMN_LOWER_BOUND_LINE_78
    assert non_negative(kind)
