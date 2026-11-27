"""NS428 (2025) line 69, column 1: line 67 minus line 68, not below zero.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 69: Line 67 minus
line 68 (if negative, enter "0")". Line 70 adds the amounts from line 69 of columns 1 and 2;
column 2 is deferred, so line 70 (and line 79, its copy) is line 69 and has no step. For a salary-
only filer line 68 is 0, so line 69 is the net income: 19,835.00 / 29,735.00 / 69,335.00 (the
ticket's line 70 figures).
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


@pytest.mark.parametrize(("salary", "income", "_a", "_b", "_c", "_d"), s.REDUCTION_CASES)
def test_line_69_is_the_net_income_for_a_salary_only_filer(
    tmp_path: Path, salary: str, income: str, _a: str, _b: str, _c: str, _d: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_69) == D(income)


def test_line_69_takes_the_income_off_line_67(tmp_path: Path) -> None:
    given = {s.INPUTS["uccb_repayment"]: "100.00", s.INPUTS["uccb_income"]: "400.00"}
    net = s.line(tmp_path, "20000", s.LINE_65, given)

    assert s.line(tmp_path, "20000", s.LINE_69, given) == net + D("100.00") - D("400.00")


def test_line_69_is_one_untitled_subtract_not_below_zero() -> None:
    assert s.part("ns428_line_69.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "69 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_67, "less": s.LINE_68},
            "produces": {"output": s.LINE_69},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_69)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_69
