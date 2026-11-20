"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 40, as the Quebec take-home manifest
wires it. Printed as "Add lines 36 and 37".

`core/sum` adds line 36 (TP-1 line 275) and line 37 (the spouse's line 275, an optional input read
as 0 when left blank), rounded half-up to the cent by `ca-qc/cent_rounding`. The expected figures
are hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_INCOME_LINE_40,
    TP1_SPOUSE_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_income_line_40"
PARTS = (
    "tp1_schedule_k_line_36.yaml",
    "tp1_schedule_k_line_37.yaml",
    "tp1_schedule_k_line_40.yaml",
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_a_single_filer_line_40_is_line_36(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_INCOME_LINE_40).value) == expected


def test_the_spouse_amount_of_line_37_is_added(take_home_service: TakeHomeService) -> None:
    given = (TP1_SPOUSE_NET_INCOME_LINE_275, "30000.50")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_INCOME_LINE_40).value) == "97915.50"


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    given = (TP1_SPOUSE_NET_INCOME_LINE_275, "0.005")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert str(sheet.get(SCHEDULE_K_INCOME_LINE_40).value) == "67915.01"
