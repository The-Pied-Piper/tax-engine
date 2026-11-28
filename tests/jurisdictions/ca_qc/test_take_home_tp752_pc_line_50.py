"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 50, as the Quebec take-home manifest wires
it (`tp752_pc_line_50.yaml`): "Enter the amount from line 40 or line 49, whichever is less. Carry
this amount to line 391
of your return. Tax credit for career extension 50".
The values over the whole form are in `test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_50
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    K,
    op,
    steps,
)
from tests.kinds import non_negative

PART = "tp752_pc_line_50.yaml"
STEPS = [
    op(
        "core/lesser_of",
        K + "line_50",
        {"amounts": [K + "line_40", K + "line_49"]},
        reference="50",
    )
]


def test_the_part_is_the_printed_line_steps_with_their_reads_and_rounding() -> None:
    assert steps(PART) == STEPS


def test_the_line_kind_is_a_registered_amount() -> None:
    kind = TP752_PC_LINE_50

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == "ca-qc/tp752_pc_line_50"
    assert isinstance(kind, AmountKind)


def test_the_floored_or_printed_figure_line_is_non_negative() -> None:
    assert non_negative(TP752_PC_LINE_50)
