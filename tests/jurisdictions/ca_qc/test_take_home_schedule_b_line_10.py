"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part A line 10, "Amount from line 275 of your return", as
the Quebec take-home manifest wires it: one `core/record_total` over the line 275 export of the TP-1
net income form. The expected figures are hand-computed from the printed lines (line 275 at a salary
of 20,000 / 70,000 / 200,000), not a Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_10
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_275, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_10.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_10"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_10_is_line_275(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, (PART,)).get(SCHEDULE_B_LINE_10)

    assert str(value.value) == LINE_275[salary]


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_line_275_export() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "reference": "10",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_net_income.tp1_net_income_line_275"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_10
    assert isinstance(SCHEDULE_B_LINE_10, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_10)
