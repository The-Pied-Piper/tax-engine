"""T1 line 21300 UCCB/RDSP part: one sum step reading the blank as 0."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_uccb_rdsp"

LINE = "21300"
NAME = "ca/uccb_repayment"
OUTPUT = "ca/uccb_repayment_line_21300"
BASIC = (
    "Line 40 and line 21300: Universal child care benefit (UCCB) "
    "repayment (box 12 of all RC62 slips)"
)


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_each_t1_line_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part = _part(T1 / f"t1_uccb_rdsp_line_{LINE}.yaml")

    assert part["form"] == {"name": "ca/t1_uccb_rdsp"}
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
