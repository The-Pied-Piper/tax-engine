"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, lines 46, 54, 56 and 58, as the
Quebec take-home manifest wires them. Each prints the TP-1 line it copies, in the printed words:
"Deduction for retirement income transferred to your spouse on December 31 (line 245)", "Support
payments made (deductible amount) (line 225)", "Carrying charges and interest expenses (line 231)"
and "Business investment loss (line 234)". Line 41 is not among them: the printed line excludes
certain repayments that TP-1 line 246 includes, so it stays its own input.

Each TP-1 line is an optional, non-negative input of the TP-1 net income form only, which takes it
once and exports it; the Schedule F line reads that export as a record list of one, so each part is
one `core/record_total`, and a blank TP-1 line is read as 0. The values reaching Schedule F line 68
and TP-1 line 254 are pinned with the line 68 tests and the input-ownership tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc

PARTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests" / "2025"
# Schedule F line, TP-1 line, the title (the printed name without its "(line N)" reference).
COPIES = [
    (
        "46",
        "245",
        "Deduction for retirement income transferred to your spouse on December 31",
    ),
    ("54", "225", "Support payments made (deductible amount)"),
    ("56", "231", "Carrying charges and interest expenses"),
    ("58", "234", "Business investment loss"),
]


@pytest.mark.parametrize(("line", "tp1_line", "title"), COPIES)
def test_the_part_is_one_record_total_of_the_tp1_net_income_export(
    line: str, tp1_line: str, title: str
) -> None:
    part: dict[str, Any] = yaml.safe_load(
        (PARTS / f"tp1_schedule_f_line_{line}.yaml").read_text(encoding="utf-8")
    )

    assert part == {
        "form": {"name": "ca-qc/tp1_schedule_f"},
        "capabilities": [
            {
                "name": "core/record_total",
                "title": title,
                "reference": line,
                "unit": "ca/cad",
                "consumes": {"records": f"ca-qc/tp1_net_income.tp1_line_{tp1_line}"},
                "blank": {"records": {f"ca-qc/tp1_line_{tp1_line}": "0"}},
                "produces": {"output": f"ca-qc/tp1_schedule_f_line_{line}"},
            }
        ],
    }
