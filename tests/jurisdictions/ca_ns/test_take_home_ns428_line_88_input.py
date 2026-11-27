"""NS428 (2025) line 88's input, as the Nova Scotia take-home manifest part declares it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF):
  "Food bank tax credit for farmers multiplied by 25%".
The line is one optional input; a request that leaves it out is read as blank, and the step that
reads it reads that blank as 0.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal

IDENTIFIER = "ca-ns/ns428_food_bank_donations_line_88"


def test_the_part_declares_only_the_line_88_input() -> None:
    part = s.part("ns428_line_88_input.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Food bank tax credit for farmers",
            "reference": "88",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": "Food bank tax credit for farmers multiplied by 25%",
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_FOOD_BANK_DONATIONS_LINE_88


def test_a_request_that_leaves_out_line_88_leaves_the_tax_unchanged(tmp_path: Path) -> None:
    assert s.line(tmp_path, "70000", s.LINE_99) == D("7213.10")
