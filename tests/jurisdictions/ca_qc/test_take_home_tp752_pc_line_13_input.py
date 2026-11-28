"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 13, an optional input read as 0 when left
out
(`tp752_pc_line_13_input.yaml`), non-negative. The values over the whole form are in
`test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_13
from tests.jurisdictions.ca_qc.tp752_pc_support import FORM, part
from tests.kinds import non_negative


def test_line_13_is_an_optional_input_read_as_0() -> None:
    declared = part("tp752_pc_line_13_input.yaml")

    assert declared["form"] == {"name": FORM}
    (declaration,) = declared["inputs"]
    assert {k: v for k, v in declaration.items() if k not in ("title", "basis")} == {
        "name": "ca-qc/tp752_pc_line_13",
        "reference": "13",
        "unit": "ca/cad",
        "required": False,
        "default": None,
    }
    assert non_negative(TP752_PC_LINE_13) is True
