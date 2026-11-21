"""The T1 UCCB and RDSP form (`ca/t1_uccb_rdsp`): the four T1 lines the totals on other forms are
built from.

For each of lines 11700, 12500, 21300 and the RDSP income repayment on line 23200 the form has an
optional input left blank by a salary-only caller, and a core/sum step that reads that blank as 0,
prints the line and exports it (5006-R page 3).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_uccb_rdsp"

# line, input, output, printed basis
T1_LINES = [
    (
        "11700",
        "ca/uccb_income",
        "ca/uccb_income_line_11700",
        "Line 7 and line 11700: Universal child care benefit (UCCB) (see the RC62 slip)",
    ),
    (
        "12500",
        "ca/rdsp_income",
        "ca/rdsp_income_line_12500",
        "Line 12 and line 12500: Registered disability savings plan (RDSP) income (box 131 of the "
        "T4A slip)",
    ),
    (
        "21300",
        "ca/uccb_repayment",
        "ca/uccb_repayment_line_21300",
        "Line 40 and line 21300: Universal child care benefit (UCCB) repayment (box 12 of all RC62 "
        "slips)",
    ),
    (
        "23200",
        "ca/rdsp_income_repayment",
        "ca/rdsp_income_repayment_line_23200",
        "Line 52 and line 23200: Other deductions (specify)",
    ),
]


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_form_exports_the_four_lines_and_builds_nothing_itself() -> None:
    part = _part(T1 / "t1_uccb_rdsp.yaml")

    assert part["form"]["name"] == "ca/t1_uccb_rdsp"
    assert part["form"]["required"] is True
    assert part["form"]["exports"] == [output for _, _, output, _ in T1_LINES]
    assert part["capabilities"] == []


@pytest.mark.parametrize(("line", "name", "output", "basis"), T1_LINES)
def test_each_t1_line_has_an_optional_input_left_blank_by_a_salary_only_caller(
    line: str, name: str, output: str, basis: str
) -> None:
    part = _part(T1 / f"t1_uccb_rdsp_line_{line}_inputs.yaml")

    assert part["form"] == {"name": "ca/t1_uccb_rdsp"}
    (declaration,) = part["inputs"]
    assert declaration == {
        "name": name,
        "title": declaration["title"],
        "reference": line,
        "unit": "ca/cad",
        "required": False,
        "default": None,
        "basis": basis,
    }


@pytest.mark.parametrize(("line", "name", "output", "basis"), T1_LINES)
def test_each_t1_line_is_one_sum_step_that_reads_its_blank_as_zero(
    line: str, name: str, output: str, basis: str
) -> None:
    part = _part(T1 / f"t1_uccb_rdsp_line_{line}.yaml")

    assert part["form"] == {"name": "ca/t1_uccb_rdsp"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": step["title"],
        "reference": line,
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [name]},
        "blank": {name: "0"},
        "produces": {"output": output},
    }
