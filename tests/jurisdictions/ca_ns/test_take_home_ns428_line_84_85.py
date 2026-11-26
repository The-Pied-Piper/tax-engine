"""NS428 (2025) lines 84 and 85: the low-income tax reduction and the tax after it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 84: Line 78 minus
line 83 (if negative, enter "0") Nova Scotia low-income tax reduction" and "Line 85: Line 77 minus
line 84 (if negative, enter "0")". Line 77 is a copy of line 64 and line 78 of line 76, which is
line 74 while lines 72, 73 and 75 are deferred (#1999). The ticket's figures: reduction 58.25 /
0.00 / 0.00 and line 85 552.33 / 1,422.86 / 7,213.10 at salaries of 20,000 / 30,000 / 70,000.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_reduction_support as r
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(("salary", "_income", "_a", "_b", "line_84", "line_85"), r.CASES)
def test_lines_84_and_85_at_the_salary(
    tmp_path: Path, salary: str, _income: str, _a: str, _b: str, line_84: str, line_85: str
) -> None:
    assert r.line(tmp_path, salary, r.LINE_84) == D(line_84)
    assert r.line(tmp_path, salary, r.LINE_85) == D(line_85)


def test_the_reduction_is_300_at_an_income_of_15000(tmp_path: Path) -> None:
    salary, income, _line_81, _line_83, reduction = r.AT_BASE

    assert r.line(tmp_path, salary, r.LINE_69) == D(income)
    assert str(r.line(tmp_path, salary, r.LINE_84)) == reduction


def test_the_reduction_is_gone_at_an_income_of_21000(tmp_path: Path) -> None:
    salary, income, line_81, line_83, reduction = r.AT_GONE

    assert r.line(tmp_path, salary, r.LINE_69) == D(income)
    assert str(r.line(tmp_path, salary, r.LINE_81)) == line_81
    assert str(r.line(tmp_path, salary, r.LINE_83)) == line_83
    assert str(r.line(tmp_path, salary, r.LINE_84)) == reduction


def test_the_reduction_is_part_way_at_an_income_of_20825(tmp_path: Path) -> None:
    # Income 20,825.00: line 81 is 5,825.00, line 83 is 291.25, so the reduction is 8.75.
    assert r.line(tmp_path, "21000", r.LINE_69) == D("20825.00")
    assert r.line(tmp_path, "21000", r.LINE_84) == D("8.75")


def test_a_reduction_larger_than_the_tax_leaves_line_85_at_0(tmp_path: Path) -> None:
    assert str(r.line(tmp_path, "15000", r.LINE_64)) == "204.43"
    assert r.line(tmp_path, "15000", r.LINE_84) == D("300.00")
    assert str(r.line(tmp_path, "15000", r.LINE_85)) == "0.00"


def test_a_foreign_tax_credit_lowers_line_64_and_so_line_85(tmp_path: Path) -> None:
    given = {s.LINE_63: "500.00"}

    assert r.line(tmp_path, "70000", r.LINE_85, given) == D("6713.10")


def test_line_84_is_one_titled_subtract_not_below_zero() -> None:
    assert r.part("ns428_line_84.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "title": "Nova Scotia low-income tax reduction",
            "reference": "84",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": r.LINE_74, "less": r.LINE_83},
            "produces": {"output": r.LINE_84},
        }
    ]


def test_line_85_is_one_untitled_subtract_not_below_zero() -> None:
    assert r.part("ns428_line_85.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "85",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": r.LINE_64, "less": r.LINE_84},
            "produces": {"output": r.LINE_85},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (r.LINE_84, ns_catalog.NS428_LOW_INCOME_REDUCTION_LINE_84),
        (r.LINE_85, ns_catalog.NS428_TAX_LINE_85),
    ],
)
def test_the_kinds_are_registered_non_negative_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = r.kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is constant
