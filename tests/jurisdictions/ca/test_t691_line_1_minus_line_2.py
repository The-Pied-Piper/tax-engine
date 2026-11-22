"""T691 Part 7, "line 1 minus line 2": the amount AB428 line 67, MB428 line 66 and SK428 line 68
read, as one cent-rounded subtraction with no floor.

Form text (AB428, MB428, SK428): "Form T691: line 1 minus line 2 of Part 7". T691 (2025) Part 7:
line 1 "Minimum amount from line 103 of Part 1", line 2 "Basic federal tax from line 7 of Part 2".
No floor is printed, so the result can be negative and its kind is signed.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tests.federal_forms import FEDERAL_FORMS
from tests.jurisdictions.ca.t691_support import t691_figure
from tests.kinds import bundled_kinds, non_negative

D = Decimal


def _step(name: str) -> dict[str, Any]:
    part = yaml.safe_load((FEDERAL_FORMS / "t691" / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    return dict(step)


OUTPUT = "ca/t691_line_1_minus_line_2_of_part_7"


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # 5,000.00 minus 1,200.00.
        ({"line_1": "5000.00", "line_2": "1200.00"}, "3800.00"),
        # Line 2 above line 1: negative, not floored.
        ({"line_1": "1000.00", "line_2": "5000.00"}, "-4000.00"),
        # Line 2 left out reads 0.
        ({"line_1": "5000.00"}, "5000.00"),
        # Both left out read 0.
        ({}, "0.00"),
    ],
)
def test_the_figure_is_line_1_minus_line_2_with_blanks_read_as_0(
    tmp_path: Path, given: dict[str, str], expected: str
) -> None:
    assert t691_figure(tmp_path, OUTPUT, **given) == D(expected)


def test_the_part_is_one_subtract_step_with_no_floor() -> None:
    assert _step("t691_line_1_minus_line_2.yaml") == {
        "name": "core/subtract",
        "title": "Line 1 minus line 2 of Part 7",
        "reference": "1 minus 2",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"amount": "ca/t691_line_1_amount", "less": "ca/t691_line_2_amount"},
        "produces": {"output": OUTPUT},
    }


def test_the_export_kind_is_a_signed_decimal_amount() -> None:
    kind = bundled_kinds().kind(OUTPUT)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
