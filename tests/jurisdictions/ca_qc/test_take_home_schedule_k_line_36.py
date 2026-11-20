"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 36, as the Quebec take-home manifest
wires it. Printed as "Amount from line 275 of your return".

Line 36 is a copy of TP-1 line 275. It arrives from the TP-1 net income form as a record list of
one, so the one step is `core/record_total`. The expected figures are hand-computed from the printed
lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_NET_INCOME_LINE_36,
    TP1_INVESTMENT_EXPENSES_ADJUSTMENT_LINE_260,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_net_income_line_36"
PARTS = ("tp1_schedule_k_line_36.yaml",)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_36_is_line_275_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)
    assert str(value.get(SCHEDULE_K_NET_INCOME_LINE_36).value) == expected


def test_line_36_follows_line_275_when_line_260_is_given(
    take_home_service: TakeHomeService,
) -> None:
    given = (TP1_INVESTMENT_EXPENSES_ADJUSTMENT_LINE_260, "100.25")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_NET_INCOME_LINE_36).value) == "68015.25"
