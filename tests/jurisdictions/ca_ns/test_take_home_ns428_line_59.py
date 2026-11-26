"""NS428 (2025) line 59, lines 56 to 58 added.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 59: Add lines 56 to
58." Line 56 is a copy of line 52 on the same form, so the one core/sum reads line 52, the line 57
input (blank read as 0) and line 58. The ticket's figures: 1,132.92, 1,190.85 and 1,416.35.
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


@pytest.mark.parametrize(("salary", "_tax", "expected", "_after"), s.CASES)
def test_line_59_is_line_52_for_a_salary_only_caller(
    tmp_path: Path, salary: str, _tax: str, expected: str, _after: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_59) == D(expected)


def test_a_given_dividend_credit_is_added(tmp_path: Path) -> None:
    assert s.line(tmp_path, "70000", s.LINE_59, {s.LINE_57: "100.00"}) == D("1516.35")


def test_the_minimum_tax_carryover_is_added(tmp_path: Path) -> None:
    given = {s.CARRYOVER: "1000.00"}

    assert s.line(tmp_path, "70000", s.LINE_59, given) == D("1991.35")


def test_the_part_is_one_untitled_sum_over_lines_52_57_and_58() -> None:
    part = s.part("ns428_line_59.yaml")

    assert list(part) == ["form", "capabilities"]
    assert part["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "59",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": [s.LINE_52, s.LINE_57, s.LINE_58]},
            "blank": {s.LINE_57: "0"},
            "produces": {"output": s.LINE_59},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_59)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_CREDITS_SUBTOTAL_LINE_59
