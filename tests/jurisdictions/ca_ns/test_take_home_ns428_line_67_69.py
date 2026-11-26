"""NS428 (2025) lines 67 and 69, column 1: the family income and the adjusted family income.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 67: Line 65 plus
line 66" and "Line 69: Line 67 minus line 68 (if negative, enter "0")". Line 70 adds the amounts
from line 69 of columns 1 and 2; column 2 is #1999, so line 70 (and line 79, its copy) is line 69
and has no step. For a salary-only filer lines 66 and 68 are 0, so lines 67 and 69 are the net
income: 19,835.00 / 29,735.00 / 69,335.00 (the ticket's line 70 figures).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_reduction_support as r
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(("salary", "income", "_a", "_b", "_c", "_d"), r.CASES)
def test_lines_67_and_69_are_the_net_income_for_a_salary_only_filer(
    tmp_path: Path, salary: str, income: str, _a: str, _b: str, _c: str, _d: str
) -> None:
    assert r.line(tmp_path, salary, r.LINE_67) == D(income)
    assert r.line(tmp_path, salary, r.LINE_69) == D(income)


def test_line_67_adds_the_repayments_and_line_69_takes_off_the_income(tmp_path: Path) -> None:
    given = {r.INPUTS["uccb_repayment"]: "100.00", r.INPUTS["uccb_income"]: "400.00"}
    net = r.line(tmp_path, "20000", r.LINE_65, given)

    assert r.line(tmp_path, "20000", r.LINE_66, given) == D("100.00")
    assert r.line(tmp_path, "20000", r.LINE_67, given) == net + D("100.00")
    assert r.line(tmp_path, "20000", r.LINE_69, given) == net + D("100.00") - D("400.00")


def test_line_67_is_one_untitled_sum_of_lines_65_and_66() -> None:
    assert r.part("ns428_line_67.yaml")["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "67 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": [r.LINE_65, r.LINE_66]},
            "produces": {"output": r.LINE_67},
        }
    ]


def test_line_69_is_one_untitled_subtract_not_below_zero() -> None:
    assert r.part("ns428_line_69.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "69 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": r.LINE_67, "less": r.LINE_68},
            "produces": {"output": r.LINE_69},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (r.LINE_67, ns_catalog.NS428_FAMILY_INCOME_LINE_67),
        (r.LINE_69, ns_catalog.NS428_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_69),
    ],
)
def test_the_kinds_are_registered_non_negative_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = r.kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is constant
