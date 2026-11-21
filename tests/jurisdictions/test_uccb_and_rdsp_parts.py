"""The parts that take the UCCB and RDSP amounts once: the four T1 lines and the totals that import
them.

The T1 UCCB and RDSP form (`ca/t1_uccb_rdsp`) has, for each of lines 11700, 12500, 21300 and the
RDSP income repayment on line 23200, an optional input left blank by a salary-only caller, and a
core/sum step that reads that blank as 0 and prints the line. Each total on another form is two
core/record_total steps over the T1 exports and one core/sum of the two, in line order, never an
input of its own.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_nl

FEDERAL = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
T1 = FEDERAL / "t1_uccb_rdsp"
BC = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
MB = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
NL = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"

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
INCOME = (
    "ca/t1_uccb_rdsp.uccb_income_line_11700",
    "ca/t1_uccb_rdsp.rdsp_income_line_12500",
)
REPAYMENT = (
    "ca/t1_uccb_rdsp.uccb_repayment_line_21300",
    "ca/t1_uccb_rdsp.rdsp_income_repayment_line_23200",
)
# part, form, the printed reference, the two T1 exports it totals, the kind of the total, rounding
TOTALS = [
    (FEDERAL / "schedule_6" / "schedule_6_line_11.yaml", "ca/schedule_6", "11", INCOME,
     "ca/uccb_and_rdsp_income", "ca/cent_rounding"),
    (BC / "bc479_line_2.yaml", "ca-bc/bc479", "2", REPAYMENT,
     "ca-bc/bc479_uccb_rdsp_repayments_line_2", "ca-bc/cent_rounding"),
    (BC / "bc479_line_4.yaml", "ca-bc/bc479", "4", INCOME,
     "ca-bc/bc479_uccb_rdsp_income_line_4", "ca-bc/cent_rounding"),
    (MB / "mb479_line_2.yaml", "ca-mb/mb479", "2", REPAYMENT,
     "ca-mb/mb479_uccb_rdsp_repayments_line_2", "ca-mb/cent_rounding"),
    (MB / "mb479_line_4.yaml", "ca-mb/mb479", "4", INCOME,
     "ca-mb/mb479_uccb_rdsp_income_line_4", "ca-mb/cent_rounding"),
    (NL / "nl428_line_89.yaml", "ca-nl/nl428", "89", REPAYMENT,
     "ca-nl/nl428_uccb_rdsp_repayments_line_89", "ca-nl/cent_rounding"),
    (NL / "nl428_line_91.yaml", "ca-nl/nl428", "91", INCOME,
     "ca-nl/nl428_uccb_rdsp_income_line_91", "ca-nl/cent_rounding"),
]  # fmt: skip


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


@pytest.mark.parametrize(("path", "form", "line", "exports", "kind", "rounding"), TOTALS)
def test_each_total_is_two_record_totals_and_a_sum_with_no_input_of_its_own(
    path: Path, form: str, line: str, exports: tuple[str, str], kind: str, rounding: str
) -> None:
    part = _part(path)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": form}
    first, second, total = part["capabilities"]
    assert [first["name"], second["name"], total["name"]] == [
        "core/record_total",
        "core/record_total",
        "core/sum",
    ]
    assert (first["consumes"]["records"], second["consumes"]["records"]) == exports
    assert total["reference"] == line
    assert total["params"] == {"rounding": rounding}
    assert total["consumes"]["parts"] == [
        first["produces"]["output"],
        second["produces"]["output"],
    ]
    assert "blank" not in total
    assert total["produces"] == {"output": kind}
