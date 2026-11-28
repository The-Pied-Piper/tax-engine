"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 14, as the Quebec take-home manifest wires
it (`tp752_pc_line_14.yaml`): "Subtract line 13 from line 12. = 14" (signed: no floor is printed).
The values over the whole form are in `test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_14
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    CENT_ROUNDING,
    K,
    op,
    steps,
)
from tests.kinds import non_negative

PART = "tp752_pc_line_14.yaml"
STEPS = [
    op(
        "core/subtract",
        K + "line_14",
        {"amount": K + "line_12", "less": K + "line_13"},
        reference="14",
        params=CENT_ROUNDING,
        blank={"less": "0"},
    )
]


def test_the_part_is_the_printed_line_steps_with_their_reads_and_rounding() -> None:
    assert steps(PART) == STEPS


def test_the_line_kind_is_a_registered_amount() -> None:
    kind = TP752_PC_LINE_14

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == "ca-qc/tp752_pc_line_14"
    assert isinstance(kind, AmountKind)


def test_the_line_the_form_prints_no_floor_on_is_signed() -> None:
    assert not non_negative(TP752_PC_LINE_14)
