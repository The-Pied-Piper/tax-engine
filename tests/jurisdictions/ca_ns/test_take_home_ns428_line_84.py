"""NS428 (2025) line 84, the Nova Scotia low-income tax reduction.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 84: Line 78 minus
line 83 (if negative, enter "0") Nova Scotia low-income tax reduction". Line 78 is a copy of line
76, which is line 74 while lines 72, 73 and 75 are deferred . The ticket's figures: 58.25 /
0.00 / 0.00 at salaries of 20,000 / 30,000 / 70,000.
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


@pytest.mark.parametrize(("salary", "_income", "_a", "_b", "line_84", "_c"), s.REDUCTION_CASES)
def test_line_84_at_the_salary(
    tmp_path: Path, salary: str, _income: str, _a: str, _b: str, line_84: str, _c: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_84) == D(line_84)


def test_the_reduction_is_300_at_an_income_of_15000(tmp_path: Path) -> None:
    salary, income, _line_81, _line_83, reduction = s.AT_BASE

    assert s.line(tmp_path, salary, s.LINE_69) == D(income)
    assert str(s.line(tmp_path, salary, s.LINE_84)) == reduction


def test_the_reduction_is_gone_at_an_income_of_21000(tmp_path: Path) -> None:
    salary, income, line_81, line_83, reduction = s.AT_GONE

    assert s.line(tmp_path, salary, s.LINE_69) == D(income)
    assert str(s.line(tmp_path, salary, s.LINE_81)) == line_81
    assert str(s.line(tmp_path, salary, s.LINE_83)) == line_83
    assert str(s.line(tmp_path, salary, s.LINE_84)) == reduction


def test_the_reduction_is_part_way_at_an_income_of_20825(tmp_path: Path) -> None:
    # Income 20,825.00: line 81 is 5,825.00, line 83 is 291.25, so the reduction is 8.75.
    assert s.line(tmp_path, "21000", s.LINE_69) == D("20825.00")
    assert s.line(tmp_path, "21000", s.LINE_84) == D("8.75")


def test_line_84_is_one_titled_subtract_not_below_zero() -> None:
    assert s.part("ns428_line_84.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "title": "Nova Scotia low-income tax reduction",
            "reference": "84",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_74, "less": s.LINE_83},
            "produces": {"output": s.LINE_84},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_84)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_LOW_INCOME_REDUCTION_LINE_84
