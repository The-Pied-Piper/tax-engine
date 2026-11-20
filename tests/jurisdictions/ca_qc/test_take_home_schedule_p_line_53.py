"""Quebec Schedule P (TP-1.D.P-V, 2025) Part C line 53, "Amount from line 275 of your spouse's
return (spouse on December 31, 2025)", as the Quebec take-home manifest wires it: the spouse's
line 275 is an optional input of the TP-1 net income form, which exports it, so the line is one
`core/record_total` over that export, a blank read as 0. Line 54 adds it."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_P_SPOUSE_NET_INCOME_LINE_53,
    TP1_SPOUSE_NET_INCOME_LINE_275,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_p_family_income_support import family_income_worksheet
from tests.jurisdictions.ca_qc.support import schedule_p_form

PARTS = (
    "schedule_p_line_52.yaml",
    "schedule_p_line_53.yaml",
    "schedule_p_line_54.yaml",
)
FORM = schedule_p_form(
    "ca-qc/schedule_p_spouse_net_income_line_53", "ca-qc/schedule_p_family_income_line_54"
)


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load(Path(QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_line_53_reads_the_net_income_form_export_and_declares_no_input_of_its_own() -> None:
    part = _part("schedule_p_line_53.yaml")

    assert "inputs" not in part
    read, printed = part["capabilities"]
    assert read["name"] == "core/record_total"
    assert read["consumes"] == {"records": "ca-qc/tp1_net_income.tp1_spouse_net_income_line_275"}
    assert printed["name"] == "core/sum"
    assert printed["reference"] == "53"
    assert printed["params"] == {"rounding": "ca-qc/cent_rounding"}


def test_a_request_that_leaves_out_the_spouse_amount_gives_line_53_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = family_income_worksheet(take_home_service, FORM, PARTS, "70000")

    assert sheet.get(SCHEDULE_P_SPOUSE_NET_INCOME_LINE_53).value == Decimal(0)


def test_the_spouse_amount_given_to_the_net_income_form_is_line_53(
    take_home_service: TakeHomeService,
) -> None:
    sheet = family_income_worksheet(
        take_home_service, FORM, PARTS, "70000", (TP1_SPOUSE_NET_INCOME_LINE_275, "30000.25")
    )

    assert sheet.get(SCHEDULE_P_SPOUSE_NET_INCOME_LINE_53).value == Decimal("30000.25")


def test_line_53_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    sheet = family_income_worksheet(
        take_home_service, FORM, PARTS, "70000", (TP1_SPOUSE_NET_INCOME_LINE_275, "1000.505")
    )

    assert sheet.get(SCHEDULE_P_SPOUSE_NET_INCOME_LINE_53).value == Decimal("1000.51")
