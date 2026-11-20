"""Revenu Quebec Schedule K (TP-1.D.K-V, 2025-12), Part A, line 37, "Amount from line 275 of your
spouse's return (spouse on December 31, 2025)", as the Quebec take-home manifest wires it: the
spouse's line 275 is an optional input of the TP-1 net income form, which exports it, so the line is
a `core/record_total` over that export (a blank read as 0) and a `core/sum` that rounds it half-up
to the cent. Line 40 adds it."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_SPOUSE_NET_INCOME_LINE_37,
    TP1_SPOUSE_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_support import schedule_k_sheet

EXPORT = (
    "ca-qc/schedule_k_spouse_net_income_line_37",
    "ca-qc/schedule_k_income_line_40",
)
PARTS = (
    "tp1_schedule_k_line_36.yaml",
    "tp1_schedule_k_line_37.yaml",
    "tp1_schedule_k_line_40.yaml",
)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(Path(QUEBEC_PARTS / PARTS[1]).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_37_reads_the_export_declares_no_input_and_rounds_to_the_cent() -> None:
    part = _part()

    assert "inputs" not in part
    read, printed = part["capabilities"]
    assert read["name"] == "core/record_total"
    assert read["consumes"] == {"records": "ca-qc/tp1_net_income.tp1_spouse_net_income_line_275"}
    assert printed["name"] == "core/sum"
    assert printed["reference"] == "37"
    assert printed["params"] == {"rounding": "ca-qc/cent_rounding"}


def test_a_request_that_leaves_out_the_spouse_amount_gives_line_37_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS)

    assert sheet.get(SCHEDULE_K_SPOUSE_NET_INCOME_LINE_37).value == Decimal(0)


def test_the_spouse_amount_given_to_the_net_income_form_is_line_37_rounded_to_the_cent(
    take_home_service: TakeHomeService,
) -> None:
    given = (TP1_SPOUSE_NET_INCOME_LINE_275, "1000.505")
    sheet = schedule_k_sheet(take_home_service, "70000", EXPORT, PARTS, given)

    assert sheet.get(SCHEDULE_K_SPOUSE_NET_INCOME_LINE_37).value == Decimal("1000.51")
