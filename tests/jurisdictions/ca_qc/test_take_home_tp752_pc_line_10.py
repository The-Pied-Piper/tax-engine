"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10) line 10, as the Quebec take-home manifest wires
it (`tp752_pc_line_10.yaml`): "Eligible work income (see the information on page 2) 10": Work
Chart 201 line 6 times the
"65 or over on December 31" flag (`ca-qc/t1_birth_year.age_65_or_older`), as Schedule B line 22.
The values over the whole form are in `test_take_home_tp752_pc.py`.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_10
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    CENT_ROUNDING,
    K,
    op,
    steps,
)

PART = "tp752_pc_line_10.yaml"
STEPS = [
    {
        "name": "core/first_record_count",
        "consumes": {"records": "ca-qc/t1_birth_year.age_65_or_older"},
        "blank": {"records": {"ca/age_65_or_older": "pass_on"}},
        "produces": {"output": K + "age_65_or_older"},
    },
    op(
        "core/record_total",
        K + "work_chart_201_line_6",
        {"records": "ca-qc/work_chart_201.work_chart_201_total_line_6"},
    ),
    op(
        "core/times_count",
        K + "line_10",
        {"amount": K + "work_chart_201_line_6", "count": K + "age_65_or_older"},
        reference="10",
        params=CENT_ROUNDING,
        blank={"count": "0"},
    ),
]


def test_the_part_is_the_printed_line_steps_with_their_reads_and_rounding() -> None:
    assert steps(PART) == STEPS


def test_the_line_kind_is_a_registered_amount() -> None:
    kind = TP752_PC_LINE_10

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == "ca-qc/tp752_pc_line_10"
    assert isinstance(kind, AmountKind)
