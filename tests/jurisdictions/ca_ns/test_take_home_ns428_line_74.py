"""NS428 (2025) line 74, the reductions added and capped at the printed maximum.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 74: Add lines 71
to 73. (maximum $600)". Lines 72 and 73 (spouse, eligible dependant) are deferred, so the base is
line 71 alone, $300, and the $600 maximum is carried but never reached. Lines 76 (line 74 plus
line 75, deferred) and 78 (the amount from line 76) are copies and have no step.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_74_is_the_basic_reduction(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_74)) == "300.00"


def test_the_part_is_one_untitled_capped_amount_step() -> None:
    assert s.part("ns428_line_74.yaml")["capabilities"] == [
        {
            "name": "core/capped_amount",
            "reference": "74",
            "unit": "ca/cad",
            "params": {"cap": "ca-ns/low_income_reduction_maximum"},
            "consumes": {"base": s.LINE_71},
            "produces": {"output": s.LINE_74},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_74)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_LOW_INCOME_REDUCTION_LINE_74
