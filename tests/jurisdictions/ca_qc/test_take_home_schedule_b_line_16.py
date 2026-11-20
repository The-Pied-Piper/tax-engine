"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part A line 16: the printed figure 42,090.00, subtracted
from the family income, as the Quebec take-home manifest wires it: one `core/credit_amount` over the
dataset `ca-qc/schedule_b_threshold_line_16`, claimed whole. The figure does not depend on the
salary.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_THRESHOLD_LINE_16
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_16.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_threshold_line_16"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_16_is_the_printed_42090(take_home_service: TakeHomeService, salary: str) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, (PART,)).get(
        SCHEDULE_B_THRESHOLD_LINE_16
    )

    assert str(value.value) == "42090.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_credit_amount_over_the_dataset() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/credit_amount",
        "reference": "16",
        "unit": "ca/cad",
        "params": {"amount": "ca-qc/schedule_b_threshold_line_16"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_THRESHOLD_LINE_16
    assert isinstance(SCHEDULE_B_THRESHOLD_LINE_16, AmountKind)
    assert non_negative(SCHEDULE_B_THRESHOLD_LINE_16)
