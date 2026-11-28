"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 47, as the Quebec take-home manifest wires
it (`tp752_pc_line_47.yaml`): "Income tax on taxable income (line 401 of your return) 47".
The values over the whole form are in `test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_47
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    K,
    op,
    steps,
)

PART = "tp752_pc_line_47.yaml"
STEPS = [
    op(
        "core/record_total",
        K + "line_47",
        {"records": "ca-qc/work_chart_401.work_chart_401_income_tax_line_8"},
        reference="47",
    )
]


def test_the_part_is_the_printed_line_steps_with_their_reads_and_rounding() -> None:
    assert steps(PART) == STEPS


def test_the_line_kind_is_a_registered_amount() -> None:
    kind = TP752_PC_LINE_47

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == "ca-qc/tp752_pc_line_47"
    assert isinstance(kind, AmountKind)
