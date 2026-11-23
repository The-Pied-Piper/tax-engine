"""Revenu Quebec Schedule F (TP-1.D.F-V, 2025-12), Part A, lines 22, 23, 26, 28 and 29, as the
Quebec take-home manifest wires them. Each prints the TP-1 line it copies, in the printed words:
"Old Age Security pension (line 114)", "Dividends from taxable Canadian corporations: Taxable
amount (line 128)", "Support payments received (taxable amount), other than a repayment (line
142)", "Social assistance payments and similar financial assistance (line 147)" and "Income
replacement indemnities and net federal supplements (line 148)".

Each TP-1 line is an optional input of the TP-1 income form only, which takes it once and exports
it; the Schedule F line reads that export as a record list of one, so each part is one
`core/record_total`, and a blank TP-1 line is read as 0. The values reaching Schedule F line 34 and
TP-1 line 199 are pinned with the input-ownership tests.
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
    ("22", "114", "Old Age Security pension"),
    ("23", "128", "Dividends from taxable Canadian corporations, taxable amount"),
    (
        "26",
        "142",
        "Support payments received (taxable amount), other than a repayment",
    ),
    ("28", "147", "Social assistance payments and similar financial assistance"),
    ("29", "148", "Income replacement indemnities and net federal supplements"),
]


@pytest.mark.parametrize(("line", "tp1_line", "title"), COPIES)
def test_the_part_is_one_record_total_of_the_tp1_income_export(
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
                "consumes": {"records": f"ca-qc/tp1_income.tp1_line_{tp1_line}"},
                "blank": {"records": {f"ca-qc/tp1_line_{tp1_line}": "0"}},
                "produces": {"output": f"ca-qc/tp1_schedule_f_line_{line}"},
            }
        ],
    }
