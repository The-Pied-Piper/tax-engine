"""NL428 lines 28, 30, 43 and 48, each a record total of a T1 export, with no input of their own.

The form prints "Amount from line 31000 / 31217 / 31900 / 33099 of your return" on these lines.
The T1 lines form owns the inputs and exports the lines; another form reads an export only as a
record list, so each line is one core/record_total step, as line 27 is. A salary-only caller has
none, so each is 0.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl

NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
CASES = [
    (
        "28",
        "self_employment_cpp_qpp_contributions_line_31000",
        "ca-nl/nl428_qpp_contributions_line_28",
    ),
    ("30", "ei_premiums_on_self_employment_line_31217", "ca-nl/nl428_ei_premiums_line_30"),
    ("43", "student_loan_interest_line_31900", "ca-nl/nl428_student_loan_interest_line_43"),
    ("48", "medical_expenses_line_33099", "ca-nl/nl428_medical_expenses_line_48"),
]


@pytest.mark.parametrize(("line", "export", "output"), CASES)
def test_the_part_is_one_record_total_of_the_t1_export_with_no_input_of_its_own(
    line: str, export: str, output: str
) -> None:
    part: dict[str, Any] = yaml.safe_load(
        (NL_PARTS / f"nl428_credits_line_{line}.yaml").read_text(encoding="utf-8")
    )

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-nl/nl428_credits"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": step["title"],
        "reference": line,
        "unit": "ca/cad",
        "consumes": {"records": f"ca/t1_lines_copied_by_provinces.{export}"},
        "produces": {"output": output},
    }
