"""Revenu Quebec TP-1 (2025) line 456, "Tax credits respecting the work premium. Complete Schedule
P.", as the Quebec take-home manifest wires it: one `core/record_total` over the line 90 export of
`ca-qc/schedule_p`. The chain runs the real Schedule P parts over the real net income parts (see
`tp1_totals_support.py`). The salary is $20,000, $70,000 and $200,000; the work premium is 584.02 at
$20,000 and nothing at the others. The expected figures are hand-computed from the printed lines,
not a Revenu Quebec example."""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_456_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

PART = "tp1_totals_line_456.yaml"
IDENTIFIER = "ca-qc/tp1_work_premium_tax_credits_line_456"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_456_is_the_schedule_p_tax_credits(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_456_PARTS)

    assert str(sheet.get(TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456).value) == EXPECTED[salary]["456"]


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Tax credits respecting the work premium",
        "reference": "456",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/schedule_p.schedule_p_tax_credits_line_90"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_WORK_PREMIUM_TAX_CREDITS_LINE_456
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
