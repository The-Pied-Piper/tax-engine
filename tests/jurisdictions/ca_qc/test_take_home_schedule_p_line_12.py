"""Quebec Schedule P (TP-1.D.P-V, 2025) Part A line 12, "Amount from line 107 of your return", as
the Quebec take-home manifest wires it: the figure is an optional input of another form, which
exports it, so the line reads that export (`core/record_total`, a blank read as 0) and rounds it
half-up to the cent (`core/sum`). Line 18 adds it."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_P_TP1_LINE_107, TP1_LINE_107
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import (
    SCHEDULE_P_WORK_INCOME_PARTS,
    schedule_p_form,
    schedule_p_worksheet,
)

PART = "schedule_p_line_12.yaml"
FORM = schedule_p_form("ca-qc/schedule_p_tp1_line_107", "ca-qc/schedule_p_work_income_line_29")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(Path(QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_12_reads_the_export_declares_no_input_and_rounds_to_the_cent() -> None:
    part = _part()

    assert "inputs" not in part
    read, printed = part["capabilities"]
    assert read["name"] == "core/record_total"
    assert read["consumes"] == {"records": "ca-qc/tp1_income.tp1_line_107"}
    assert printed["name"] == "core/sum"
    assert printed["reference"] == "12"
    assert printed["params"] == {"rounding": "ca-qc/cent_rounding"}


def test_a_request_that_leaves_out_the_figure_gives_line_12_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = schedule_p_worksheet(take_home_service, FORM, SCHEDULE_P_WORK_INCOME_PARTS, "70000")

    assert sheet.get(SCHEDULE_P_TP1_LINE_107).value == Decimal(0)


def test_the_figure_given_to_its_owner_is_line_12_rounded_to_the_cent(
    take_home_service: TakeHomeService,
) -> None:
    sheet = schedule_p_worksheet(
        take_home_service, FORM, SCHEDULE_P_WORK_INCOME_PARTS, "70000", (TP1_LINE_107, "1000.505")
    )

    assert sheet.get(SCHEDULE_P_TP1_LINE_107).value == Decimal("1000.51")
