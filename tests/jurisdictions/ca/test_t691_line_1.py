"""T691 Part 7 line 1: the typed line read as 0 when blank and rounded to the cent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.federal_forms import FEDERAL_FORMS
from tests.jurisdictions.ca.t691_support import D, t691_figure

PART = FEDERAL_FORMS / "t691" / "t691_line_1.yaml"
INPUT = "ca/t691_minimum_amount"
OUTPUT = "ca/t691_line_1_amount"


def test_line_1_is_one_sum_step_that_reads_the_blank_as_zero_and_rounds_to_the_cent() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "1",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [INPUT]},
        "blank": {INPUT: "0"},
        "produces": {"output": OUTPUT},
    }


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # Left blank: read as 0.
        ({}, "0.00"),
        # A whole-cent figure is kept.
        ({"line_1": "1234.56"}, "1234.56"),
        # A half cent rounds half up to the cent.
        ({"line_1": "1000.005"}, "1000.01"),
        ({"line_1": "0.004"}, "0.00"),
    ],
)
def test_the_amount_reads_blank_as_0_and_rounds_to_the_cent(
    tmp_path: Path, given: dict[str, str], expected: str
) -> None:
    value = t691_figure(tmp_path, OUTPUT, **given)

    assert value == D(expected)
    assert str(value) == expected
