"""NS428 (2025) line 85, line 77 minus line 84, not below zero: the tax after the reduction.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 85: Line 77 minus
line 84 (if negative, enter "0")". Line 77 is a copy of line 64. The ticket's figures: 552.33 /
1,422.86 / 7,213.10 at salaries of 20,000 / 30,000 / 70,000.
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


@pytest.mark.parametrize(("salary", "_income", "_a", "_b", "_c", "line_85"), s.REDUCTION_CASES)
def test_line_85_at_the_salary(
    tmp_path: Path, salary: str, _income: str, _a: str, _b: str, _c: str, line_85: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_85) == D(line_85)


def test_a_reduction_larger_than_the_tax_leaves_line_85_at_0(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "15000", s.LINE_64)) == "204.43"
    assert s.line(tmp_path, "15000", s.LINE_84) == D("300.00")
    assert str(s.line(tmp_path, "15000", s.LINE_85)) == "0.00"


def test_a_foreign_tax_credit_lowers_line_64_and_so_line_85(tmp_path: Path) -> None:
    assert s.line(tmp_path, "70000", s.LINE_85, {s.LINE_63: "500.00"}) == D("6713.10")


def test_line_85_is_one_untitled_subtract_not_below_zero() -> None:
    assert s.part("ns428_line_85.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "85",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_64, "less": s.LINE_84},
            "produces": {"output": s.LINE_85},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_85)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_LINE_85
