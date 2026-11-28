"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 48, as the Quebec take-home manifest wires
it (`tp752_pc_line_48.yaml`): "Add lines 359 through 367 of your return. x 14% - 48".
The values over the whole form are in `test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_48
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    EXACT_ROUNDING,
    K,
    op,
    steps,
)

PART = "tp752_pc_line_48.yaml"
STEPS = [
    op(
        "core/record_total",
        K + "tp1_line_359",
        {"records": "ca-qc/tp1_credits_lines_350_to_361.tp1_line_359"},
    ),
    op(
        "core/record_total",
        K + "tp1_line_361",
        {
            "records": "ca-qc/tp1_credits_lines_350_to_361"
            ".tp1_age_living_alone_retirement_amount_line_361"
        },
    ),
    op(
        "core/sum",
        K + "lines_359_to_367",
        {"parts": [K + "tp1_line_359", K + "tp1_line_361"]},
        params=EXACT_ROUNDING,
    ),
    op(
        "core/apply_rate",
        K + "line_48",
        {"base": K + "lines_359_to_367"},
        reference="48",
        params={"rate": K + "line_48_rate"},
    ),
]


def test_the_part_is_the_printed_line_steps_with_their_reads_and_rounding() -> None:
    assert steps(PART) == STEPS


def test_the_line_kind_is_a_registered_amount() -> None:
    kind = TP752_PC_LINE_48

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == "ca-qc/tp752_pc_line_48"
    assert isinstance(kind, AmountKind)
