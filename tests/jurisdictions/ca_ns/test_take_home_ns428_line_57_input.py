"""NS428 (2025) line 57's input, as the Nova Scotia take-home manifest part declares it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF):
  "Line 57 and line 61520: Nova Scotia dividend tax credit (use Worksheet NS428)".
Umar ruled on 26 Nov 2026 that the credit is one optional input; Worksheet NS428 is not built.
A request that leaves the line out is read as blank; the step that reads it reads that blank as 0.
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

IDENTIFIER = "ca-ns/ns428_dividend_tax_credit_line_57"


def test_the_part_declares_only_the_line_57_input() -> None:
    part = s.part("ns428_line_57_input.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["inputs"] == [
        {
            "name": IDENTIFIER,
            "title": "Nova Scotia dividend tax credit",
            "reference": "57",
            "unit": "ca/cad",
            "required": False,
            "default": None,
            "basis": (
                "Line 57 and line 61520: Nova Scotia dividend tax credit (use Worksheet NS428)"
            ),
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_DIVIDEND_TAX_CREDIT_LINE_57


def test_a_request_that_leaves_out_line_57_has_no_figure_of_its_own(tmp_path: Path) -> None:
    sheet = s.sheet(tmp_path, "70000", (s.LINE_64,))

    assert nova_scotia_kinds().kind(IDENTIFIER) is ns_catalog.NS428_DIVIDEND_TAX_CREDIT_LINE_57
    assert s.value(sheet, s.LINE_64) == D("7213.10")
