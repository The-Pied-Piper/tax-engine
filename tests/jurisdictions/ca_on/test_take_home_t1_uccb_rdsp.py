"""The T1 UCCB and RDSP form declaration: its four exports and no steps of its own."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import tax_engine.jurisdictions.ca

T1 = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms" / "t1_uccb_rdsp"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_t1_form_exports_the_four_lines_and_builds_nothing_itself() -> None:
    part = _part(T1 / "t1_uccb_rdsp.yaml")

    assert part["form"]["name"] == "ca/t1_uccb_rdsp"
    assert part["form"]["required"] is True
    assert part["form"]["exports"] == [
        "ca/uccb_income_line_11700",
        "ca/rdsp_income_line_12500",
        "ca/uccb_repayment_line_21300",
        "ca/rdsp_income_repayment_line_23200",
    ]
    assert part["capabilities"] == []
