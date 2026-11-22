"""NL428 (2025) line 48, as the T1 medical expenses export: the part has no input of its own.

Form text (Form NL428, CRA 5001-c; that file is not in the confirmed cra-docs set, so the quote is
the one the part already carried): "Line 48 and line 58689: Amount from line 33099 of your
return". The amount is T1 line 33099, asked once on the `ca/t1_medical_expenses` form (as
`ca/medical_expenses`) and exported as `medical_expenses_line_33099`. Another form reads an export
only as a record list, so the part is one core/record_total step that gives the same kind the
typed input gave (`ca-nl/nl428_medical_expenses_line_48`), and the lines after it are unchanged. A
salary-only caller has no medical expenses, so the line is 0. The figures through the engine are
in `test_medical_expenses_taken_once.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_nl

PART = (
    Path(tax_engine.jurisdictions.ca_nl.__file__).parent
    / "manifests"
    / "2025"
    / "nl428_credits_line_48.yaml"
)


def test_the_part_is_one_record_total_of_the_t1_export_and_has_no_input_of_its_own() -> None:
    part: dict[str, Any] = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-nl/nl428_credits"}
    (step,) = part["capabilities"]
    # The title and the reference are wording; every other key is pinned.
    assert {key: value for key, value in step.items() if key not in ("title", "reference")} == {
        "name": "core/record_total",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_medical_expenses.medical_expenses_line_33099"},
        "produces": {"output": "ca-nl/nl428_medical_expenses_line_48"},
    }
