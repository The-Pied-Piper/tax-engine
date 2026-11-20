"""Revenu Quebec TP-1 (2025) line 248, "Deduction for QPP and CPP contributions and QPIP premiums",
as the Quebec take-home manifest part wires it: Schedule U line 23 ("Carry the result to line 248
of your return"). Schedule U is its own form, so line 23 arrives as that form's export and the one
step is `core/record_total` over it. The salary is the starting input; Schedule U and the TP-1
income steps are the real parts. The expected figures are hand-computed from the printed lines, not
an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_QPP_DEDUCTION_LINE_248,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp1_net_income_support import net_income_sheet

LINE = TP1_QPP_DEDUCTION_LINE_248
EXPORTS = ("ca-qc/tp1_qpp_deduction_line_248",)
PARTS = ("tp1_net_income_line_248.yaml",)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "165.00"), ("70000", "665.00"), ("200000", "1074.00")],
)
def test_line_248_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = net_income_sheet(take_home_service, salary, EXPORTS, PARTS).get(LINE).value

    assert str(value) == expected


def test_a_salary_below_the_exemption_carries_a_nil_line_23(
    take_home_service: TakeHomeService,
) -> None:
    """Schedule U line 14 is floored at 0 below the exemption (owner's ruling), so at a $3,000
    salary line 23 is 0.00 and line 248 carries it."""
    value = net_income_sheet(take_home_service, "3000", EXPORTS, PARTS).get(LINE).value

    assert str(value) == "0.00"
