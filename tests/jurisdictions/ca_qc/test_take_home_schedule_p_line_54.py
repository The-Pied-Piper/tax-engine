"""Quebec Schedule P (TP-1.D.P-V, 2025) Part C line 54, "Add lines 52 and 53. Family income", as the
Quebec take-home manifest wires it: one `core/sum` of line 52 (the net income of TP-1 line 275) and
the optional line 53 (the spouse's), a blank read as 0, rounded half-up to the cent.

The expected figures of a salary-only filer are hand-computed from the printed lines (the Quebec
2025 hand calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_FAMILY_INCOME_LINE_54,
    TP1_SPOUSE_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_52.yaml",
    "schedule_p_line_53.yaml",
    "schedule_p_line_54.yaml",
)
FORM = schedule_p_form("ca-qc/schedule_p_family_income_line_54")


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_a_salary_only_family_income_is_line_52(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)

    assert str(sheet.get(SCHEDULE_P_FAMILY_INCOME_LINE_54).value) == expected


def test_line_53_is_added_to_line_52(take_home_service: TakeHomeService) -> None:
    sheet = family_income_worksheet(
        take_home_service,
        FORM,
        PARTS,
        "70000",
        (TP1_SPOUSE_NET_INCOME_LINE_275, "30000.255"),
    )

    # 67,915.00 + 30,000.255 = 97,915.255, half-up to the cent.
    assert sheet.get(SCHEDULE_P_FAMILY_INCOME_LINE_54).value == Decimal("97915.26")
