"""MB428 (2025) line 49, from the real parts through the engine.

Form text (Form MB428, CRA 5007-c): "Line 49 and line 58729: Allowable amount of medical expenses
for other dependants (use Worksheet MB428)". Worksheet MB428 line 4 says to enter its amount on
line 58729, so line 49 is one core/record_total step over that line, as MB428 line 9 reads the
worksheet's line 9. A salary-only caller lists no dependant, so it is 0.00.
"""

from __future__ import annotations

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tests.jurisdictions.ca_mb.mb428_dependants_support import (
    CREDITS_FORM,
    LINE_4,
    TOTAL_FORM,
    D,
    amount,
    load_part,
    sheets,
)

IDENTIFIER = "ca-mb/mb428_other_dependants_medical_expenses_line_49"


def test_the_part_is_one_titled_record_total_step_over_line_4() -> None:
    assert load_part("mb428_credits_line_49.yaml") == {
        "form": {"name": CREDITS_FORM},
        "capabilities": [
            {
                "name": "core/record_total",
                "title": (
                    "Allowable amount of medical expenses for other dependants"
                    " (use Worksheet MB428)"
                ),
                "reference": "49",
                "unit": "ca/cad",
                "consumes": {"records": f"{TOTAL_FORM}.{LINE_4.removeprefix('ca-mb/')}"},
                "produces": {"output": IDENTIFIER},
            }
        ],
    }


def test_line_49_is_a_registered_non_negative_amount() -> None:
    assert mb.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49.identifier == IDENTIFIER


def test_line_49_is_the_worksheet_total() -> None:
    (sheet,) = sheets(CREDITS_FORM, ("900", "400"), ("300", "450"), ("1200", None))

    assert amount(sheet, mb.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49) == D("1700.00")


def test_a_salary_only_caller_has_line_49_of_zero() -> None:
    (sheet,) = sheets(CREDITS_FORM)

    assert amount(sheet, mb.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49) == D("0.00")
