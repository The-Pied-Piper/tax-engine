"""SK428 (2025) line 49, as the T1 line 33199 export: the part has no input of its own.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 49 and line 58729: Allowable amount of medical
expenses for other dependants from line 33199 of your return". The amount is T1 line 33199, asked
once on the `ca/t1_medical_expenses` form (as `ca/other_dependants_medical_expenses`) and exported
as `other_dependants_medical_expenses_line_33199`. Another form reads an export only as a record
list, so the part is one core/record_total step that gives the same kind the typed input gave
(`ca-sk/sk428_other_dependants_medical_expenses_line_49`), and the lines after it are unchanged. A
salary-only caller has none, so the line is 0. The figures through the engine are in
`test_medical_expenses_taken_once.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca_sk

PART = (
    Path(tax_engine.jurisdictions.ca_sk.__file__).parent
    / "manifests"
    / "2025"
    / "sk428_credits_line_49.yaml"
)


def test_the_part_is_one_record_total_of_the_t1_export_and_has_no_input_of_its_own() -> None:
    part: dict[str, Any] = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-sk/sk428_credits"}
    (step,) = part["capabilities"]
    # The title and the reference are wording; every other key is pinned.
    assert {key: value for key, value in step.items() if key not in ("title", "reference")} == {
        "name": "core/record_total",
        "unit": "ca/cad",
        "consumes": {
            "records": "ca/t1_medical_expenses.other_dependants_medical_expenses_line_33199"
        },
        "produces": {"output": "ca-sk/sk428_other_dependants_medical_expenses_line_49"},
    }
