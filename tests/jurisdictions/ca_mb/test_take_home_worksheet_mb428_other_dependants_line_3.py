"""Worksheet MB428 (2025) section "Line 58729", line 3, from the real parts through the engine.

Form text (Worksheet MB428, CRA 5007-D): "Line 3: Line 1 minus line 2 (if negative, enter "0")".
One core/subtract_not_below_zero step for each dependant's column, rounded half-up to the cent; a
blank line 2 is read as 0. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

import pytest

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tests.jurisdictions.ca_mb.mb428_dependants_support import (
    COLUMNS_FORM,
    LINE_1,
    LINE_2,
    LINE_3,
    D,
    amount,
    load_part,
    sheets,
)


def test_the_part_is_one_subtract_not_below_zero_step_with_no_title() -> None:
    assert load_part("worksheet_mb428_other_dependants_line_3.yaml") == {
        "form": {"name": COLUMNS_FORM},
        "capabilities": [
            {
                "name": "core/subtract_not_below_zero",
                "reference": "3",
                "unit": "ca/cad",
                "params": {"rounding": "ca-mb/cent_rounding"},
                "consumes": {"amount": LINE_1, "less": LINE_2},
                "blank": {"less": "0"},
                "produces": {"output": LINE_3},
            }
        ],
    }


@pytest.mark.parametrize(
    ("line_1", "line_2", "expected"),
    [
        ("900", "400", "500.00"),
        ("300", "450", "0.00"),
        ("1200", None, "1200.00"),
        ("10.005", "0", "10.01"),
    ],
)
def test_line_3(line_1: str, line_2: str | None, expected: str) -> None:
    (sheet,) = sheets(COLUMNS_FORM, (line_1, line_2))

    assert amount(sheet, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_3) == D(expected)


def test_each_dependant_has_a_worksheet_of_its_own() -> None:
    columns = sheets(COLUMNS_FORM, ("900", "400"), ("300", "450"))

    assert [amount(s, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_3) for s in columns] == [
        D("500.00"),
        D("0.00"),
    ]
