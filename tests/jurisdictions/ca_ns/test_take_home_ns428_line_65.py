"""NS428 (2025) line 65, column 1: the net income from line 23600 of the return.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 65: Net income
from line 23600 of the return". The signed T1 net income (before its floor) of a salary-only filer
is the salary less the enhanced CPP deduction: 19,835.00 / 29,735.00 / 69,335.00 at 20,000 /
30,000 / 70,000 (the ticket's figures).
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
def test_line_65_is_the_t1_net_income(
    tmp_path: Path, salary: str, income: str, _a: str, _b: str, _c: str, _d: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_65) == D(income)


def test_the_part_is_one_titled_record_total_over_the_t1_net_income() -> None:
    assert s.part("ns428_line_65.yaml")["capabilities"] == [
        {
            "name": "core/record_total",
            "title": "Net income from line 23600 of the return",
            "reference": "65 (column 1)",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income_signed"},
            "produces": {"output": s.LINE_65},
        }
    ]


def test_line_65_is_signed_for_a_negative_net_income(tmp_path: Path) -> None:
    # A social benefits repayment of 30,000 against a salary of 20,000 leaves a net income of
    # -10,165.00 (the salary less the CPP deduction of 165.00 less 30,000).
    given = {s.NEGATIVE_NET_INCOME: "30000.00"}

    assert s.line(tmp_path, "20000", s.LINE_65, given) == D("-10165.00")


def test_the_kind_is_a_registered_signed_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_65)

    assert isinstance(kind, AmountKind)
    assert not non_negative(kind)
    assert kind is ns_catalog.NS428_NET_INCOME_LINE_65
