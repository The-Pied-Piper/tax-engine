"""The T1 taxable income form declaration exports the four UCCB and RDSP lines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_taxable_income"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_form_exports_the_four_lines() -> None:
    part = _part(T1 / "t1_taxable_income.yaml")

    assert part["form"]["name"] == "ca/t1_taxable_income"
    assert set(part["form"]["exports"]) >= {
        "ca/uccb_income_line_11700",
        "ca/rdsp_income_line_12500",
        "ca/uccb_repayment_line_21300",
        "ca/rdsp_income_repayment_line_23200",
    }
