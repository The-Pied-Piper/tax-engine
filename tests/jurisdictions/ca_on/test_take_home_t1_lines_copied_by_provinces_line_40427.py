"""T1 line 40427 part of the lines the provinces copy: one sum step reading the blank as 0."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tests.federal_forms import FEDERAL_FORMS

T1 = FEDERAL_FORMS / "t1_lines_copied_by_provinces"

LINE = "40427"
NAME = "ca/minimum_tax_carryover"
OUTPUT = "ca/minimum_tax_carryover_line_40427"
BASIC = "Line 124 and line 40427: Minimum tax carryover (complete Form T691)"
TITLE = "Minimum tax carryover"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_line_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part = _part(T1 / f"t1_lines_copied_by_provinces_line_{LINE}.yaml")

    assert part["form"] == {"name": "ca/t1_lines_copied_by_provinces"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": TITLE,
        "reference": LINE,
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [NAME]},
        "blank": {NAME: "0"},
        "produces": {"output": OUTPUT},
    }
