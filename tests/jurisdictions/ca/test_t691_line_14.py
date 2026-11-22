"""T691 Part 7 line 14, "Additional taxes paid for minimum tax carryover": the amount BC428 line 69
and NL428 line 71 read, as one cent-rounded subtraction with the printed floor.

Form text (T691 E (25), Part 7): "Line 1 minus line 13 (if negative, enter "0")". Line 13 is typed.
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


OUTPUT = "ca/t691_additional_taxes_for_minimum_tax_carryover_line_14"


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # 5,000.00 minus 1,200.00.
        ({"line_1": "5000.00", "line_13": "1200.00"}, "3800.00"),
        # Line 13 above line 1: the printed floor gives 0.
        ({"line_1": "1000.00", "line_13": "5000.00"}, "0.00"),
        # Line 13 left out reads 0.
        ({"line_1": "5000.00"}, "5000.00"),
        # Both left out read 0.
        ({}, "0.00"),
    ],
)
def test_the_figure_is_line_1_minus_line_13_not_below_zero(
    tmp_path: Path, given: dict[str, str], expected: str
) -> None:
    assert t691_figure(tmp_path, OUTPUT, **given) == D(expected)


def test_the_part_is_one_subtract_not_below_zero_step() -> None:
    assert _step("t691_line_14.yaml") == {
        "name": "core/subtract_not_below_zero",
        "title": "Additional taxes paid for minimum tax carryover",
        "reference": "14",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"amount": "ca/t691_line_1_amount", "less": "ca/t691_line_13_amount"},
        "produces": {"output": OUTPUT},
    }


def test_the_export_kind_is_a_non_negative_decimal_amount() -> None:
    kind = bundled_kinds().kind(OUTPUT)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
