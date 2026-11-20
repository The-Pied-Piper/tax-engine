"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 41, as the Quebec take-home manifest
wires it: "If you had a spouse on December 31, 2025, enter $32,240; otherwise, enter $19,890". The
take-home is a single filer, so the printed 19,890 is a dataset figure
(`ca-qc/schedule_k_line_41_amount`) claimed whole by one `core/credit_amount`, whatever the salary.
"""

from __future__ import annotations

import pytest

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_K_AMOUNT_LINE_41
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = "ca-qc/schedule_k_amount_line_41"
PARTS = ("tp1_schedule_k_line_41.yaml",)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_41_is_the_printed_19890_at_each_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = schedule_k_sheet(take_home_service, salary, EXPORT, PARTS)

    assert str(sheet.get(SCHEDULE_K_AMOUNT_LINE_41).value) == "19890.00"
