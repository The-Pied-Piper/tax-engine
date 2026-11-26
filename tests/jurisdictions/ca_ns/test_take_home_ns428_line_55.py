"""NS428 (2025) line 55, line 53 plus line 54.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 55: Line 53 plus
line 54". Line 53 is a copy of line 8 on the same form, so the one core/sum reads line 8 and the
line 54 input (blank read as 0). The ticket's figures: 1,743.50, 2,613.71 and 8,629.45.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(("salary", "expected", "_credits", "_tax"), s.CASES)
def test_line_55_is_line_8_at_the_salary(
    tmp_path: Path, salary: str, expected: str, _credits: str, _tax: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_55) == D(expected)


def test_a_given_line_54_is_added_to_line_53(tmp_path: Path) -> None:
    assert s.line(tmp_path, "70000", s.LINE_55, {s.LINE_54: "200.00"}) == D("8829.45")


def test_the_part_is_one_untitled_sum_over_line_8_and_line_54() -> None:
    part = s.part("ns428_line_55.yaml")

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "55",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": [s.LINE_8, s.LINE_54]},
            "blank": {s.LINE_54: "0"},
            "produces": {"output": s.LINE_55},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_55)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_LINE_55
