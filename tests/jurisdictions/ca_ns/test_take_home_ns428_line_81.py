"""NS428 (2025) line 81: line 79 minus line 80, not below zero.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 81: Line 79 minus
line 80 (if negative, enter "0")". Line 79 is a copy of line 70, which is line 69 while column 2 is
deferred . The ticket's figures: 4,835.00 / 14,735.00 / 54,335.00 at salaries of 20,000 /
30,000 / 70,000.
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


@pytest.mark.parametrize(("salary", "_income", "line_81", "_a", "_b", "_c"), s.REDUCTION_CASES)
def test_line_81_at_the_salary(
    tmp_path: Path, salary: str, _income: str, line_81: str, _a: str, _b: str, _c: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_81) == D(line_81)


def test_income_at_the_base_amount_leaves_line_81_at_0(tmp_path: Path) -> None:
    salary, income, line_81, _line_83, _reduction = s.AT_BASE

    assert s.line(tmp_path, salary, s.LINE_69) == D(income)
    assert str(s.line(tmp_path, salary, s.LINE_81)) == line_81


def test_line_81_is_one_untitled_subtract_not_below_zero() -> None:
    assert s.part("ns428_line_81.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "81",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_69, "less": s.LINE_80},
            "produces": {"output": s.LINE_81},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_81)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_LINE_81
