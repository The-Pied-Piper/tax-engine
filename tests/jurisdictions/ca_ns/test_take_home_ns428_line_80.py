"""NS428 (2025) line 80, the base amount.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 80: Base amount
15,000.00". The printed figure is the `ca-ns/low_income_reduction_base_amount` dataset through
core/credit_amount, the same at every salary.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


def test_line_80_is_15000(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "20000", s.LINE_80)) == "15000.00"


def test_the_part_is_one_credit_amount_step() -> None:
    assert s.part("ns428_line_80.yaml")["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "Base amount",
            "reference": "80",
            "unit": "ca/cad",
            "params": {"amount": "ca-ns/low_income_reduction_base_amount"},
            "produces": {"output": s.LINE_80},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_80)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.LOW_INCOME_REDUCTION_BASE_AMOUNT
