"""Revenu Quebec TP-1 (2025) line 446, "Contribution to the health services fund. Complete Schedule
F.", as the Quebec take-home manifest wires it: one `core/record_total` over the line 82 export of
`ca-qc/tp1_schedule_f`. The chain runs the real Schedule F parts over the real TP-1 income parts
(see `tp1_totals_support.py`). The salary is $20,000, $70,000 and $200,000; a salary-only filer owes
no contribution, so line 446 is 0.00. The expected figures are hand-computed from the printed lines,
not a Revenu Quebec example."""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_HEALTH_SERVICES_FUND_LINE_446
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_446_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

PART = "tp1_totals_line_446.yaml"
IDENTIFIER = "ca-qc/tp1_health_services_fund_line_446"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_446_is_the_schedule_f_contribution(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_446_PARTS)

    assert str(sheet.get(TP1_HEALTH_SERVICES_FUND_LINE_446).value) == EXPECTED[salary]["446"]


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
        "title": "Contribution to the health services fund",
        "reference": "446",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_schedule_f.tp1_schedule_f_contribution_line_82"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_HEALTH_SERVICES_FUND_LINE_446
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
