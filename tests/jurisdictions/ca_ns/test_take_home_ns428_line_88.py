"""NS428 (2025) line 88, the food bank tax credit for farmers, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 88: Food bank tax
credit for farmers ... multiplied by 25%". One core/apply_rate step (`ns428_line_88.yaml`): the
entered amount times the printed 25%, read as 0 when the line is left blank. The line prints no
maximum.
Figures are hand-computed from the printed form (not a CRA example).
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


def test_a_blank_line_88_is_a_credit_of_0(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_88)) == "0.00"


def test_the_entered_amount_is_multiplied_by_25_percent(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_88, {s.LINE_88_INPUT: "200"})) == "50.00"


def test_the_product_is_rounded_half_up_to_the_cent(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_88, {s.LINE_88_INPUT: "0.02"})) == "0.01"
    assert str(s.line(tmp_path, "70000", s.LINE_88, {s.LINE_88_INPUT: "0.01"})) == "0.00"


def test_the_part_is_one_titled_apply_rate_step() -> None:
    assert s.part("ns428_line_88.yaml")["capabilities"] == [
        {
            "name": "core/apply_rate",
            "title": "Food bank tax credit for farmers",
            "reference": "88",
            "unit": "ca/cad",
            "params": {"rate": "ca-ns/food_bank_credit_rate"},
            "consumes": {"base": s.LINE_88_INPUT},
            "blank": {"base": "0"},
            "produces": {"output": s.LINE_88},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_88)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_FOOD_BANK_CREDIT_LINE_88
