"""T1 line 12500 UCCB/RDSP part: one sum step reading the blank as 0."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_taxable_income"

LINE = "12500"
NAME = "ca/rdsp_income"
OUTPUT = "ca/rdsp_income_line_12500"
BASIC = (
    "Line 12 and line 12500: Registered disability savings plan "
    "(RDSP) income (box 131 of the T4A slip)"
)


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_each_t1_line_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part = _part(T1 / f"t1_taxable_income_line_{LINE}.yaml")

    assert part["form"] == {"name": "ca/t1_taxable_income"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": step["title"],
        "reference": LINE,
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [NAME]},
        "blank": {NAME: "0"},
        "produces": {"output": OUTPUT},
    }
