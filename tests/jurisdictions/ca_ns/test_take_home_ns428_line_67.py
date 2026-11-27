"""NS428 (2025) line 67, column 1: line 65 plus line 66.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 67: Line 65 plus
line 66". For a salary-only filer line 66 is 0, so line 67 is the net income: 19,835.00 /
29,735.00 / 69,335.00 at salaries of 20,000 / 30,000 / 70,000.
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
def test_line_67_is_the_net_income_for_a_salary_only_filer(
    tmp_path: Path, salary: str, income: str, _a: str, _b: str, _c: str, _d: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_67) == D(income)


def test_line_67_adds_the_repayments_to_the_net_income(tmp_path: Path) -> None:
    given = {s.INPUTS["uccb_repayment"]: "100.00"}
    net = s.line(tmp_path, "20000", s.LINE_65, given)

    assert s.line(tmp_path, "20000", s.LINE_67, given) == net + D("100.00")


def test_line_67_is_one_untitled_sum_of_lines_65_and_66() -> None:
    assert s.part("ns428_line_67.yaml")["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "67 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": [s.LINE_65, s.LINE_66]},
            "produces": {"output": s.LINE_67},
        }
    ]


def test_line_67_is_signed_for_a_negative_net_income(tmp_path: Path) -> None:
    # A social benefits repayment of 30,000 against a salary of 20,000 leaves a net income of
    # -10,165.00 (the salary less the CPP deduction of 165.00 less 30,000).
    given = {s.NEGATIVE_NET_INCOME: "30000.00"}

    assert s.line(tmp_path, "20000", s.LINE_67, given) == D("-10165.00")


def test_the_kind_is_a_registered_signed_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_67)

    assert isinstance(kind, AmountKind)
    assert not non_negative(kind)
    assert kind is ns_catalog.NS428_FAMILY_INCOME_LINE_67
