"""Quebec Schedule P (TP-1.D.P-V, 2025) Part C "Family income", line 52, "Amount from line 275 of
your return", as the Quebec take-home manifest wires it: one `core/record_total` that reads TP-1
line 275 (net income) from the TP-1 net income form's export.

The expected figures of a salary-only filer are hand-computed from the printed lines (the
Quebec 2025 hand calculation of 19 Nov 2026), not from a Revenu Quebec example."""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_NET_INCOME_LINE_52
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = ("schedule_p_line_52.yaml",)
FORM = schedule_p_form("ca-qc/schedule_p_net_income_line_52")


def value(take_home_service: TakeHomeService, salary: str) -> str:
    """The printed figure of the line for a salary-only filer."""
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, salary)
    return str(sheet.get(SCHEDULE_P_NET_INCOME_LINE_52).value)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "18635.00"), ("70000", "67915.00"), ("200000", "197506.00")],
)
def test_line_52_is_the_net_income_of_line_275(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(take_home_service, salary) == expected
