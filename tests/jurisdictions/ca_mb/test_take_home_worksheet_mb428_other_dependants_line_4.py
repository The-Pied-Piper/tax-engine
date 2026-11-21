"""Worksheet MB428 (2025) section "Line 58729", line 4, from the real parts through the engine.

Form text (Worksheet MB428, CRA 5007-D): "Line 4: Add the amounts from line 3 for columns 1, 2, and
3 (and others, if any). Enter this amount on line 58729 of your Form MB428." One core/record_total
step over the column form's line 3; with no dependant it is 0.00. The hand figures are asserted.
"""

from __future__ import annotations

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tests.jurisdictions.ca_mb.mb428_dependants_support import (
    COLUMNS_FORM,
    LINE_3,
    LINE_4,
    TOTAL_FORM,
    D,
    amount,
    load_part,
    sheets,
)


def test_the_part_is_one_record_total_step_over_the_columns() -> None:
    assert load_part("worksheet_mb428_other_dependants_total.yaml")["capabilities"] == [
        {
            "name": "core/record_total",
            "reference": "4",
            "unit": "ca/cad",
            "consumes": {"records": f"{COLUMNS_FORM}.{LINE_3.removeprefix('ca-mb/')}"},
            "produces": {"output": LINE_4},
        }
    ]


def test_line_4_adds_the_columns_and_more_than_three_dependants_work() -> None:
    (sheet,) = sheets(TOTAL_FORM, ("900", "400"), ("300", "450"), ("1200", None), ("50.50", "0"))

    assert amount(sheet, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_4) == D("1750.50")


def test_line_4_is_zero_with_no_dependant() -> None:
    (sheet,) = sheets(TOTAL_FORM)

    assert amount(sheet, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_4) == D("0")
