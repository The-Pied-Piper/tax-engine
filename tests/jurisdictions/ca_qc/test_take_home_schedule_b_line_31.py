"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 31, "Amount from line 18 x 18.75%", as the
Quebec take-home manifest wires it: one `core/apply_rate` over line 18 with the printed rate from
the dataset `ca-qc/schedule_b_line_31_rate`, rounded half-up to the cent by the dataset's rule.
The expected figures are hand-computed from the printed lines (line 18 is 0.00 / 25,825.00 /
155,416.00 at a salary of 20,000 / 70,000 / 200,000), not a Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_31
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import LINE_18_PARTS, schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_31.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_31"
EXPORTS = (IDENTIFIER,)
PARTS = (*LINE_18_PARTS, PART)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("20000", "0.00"),
        # 25,825.00 x 0.1875 = 4,842.1875, rounded half-up to the cent.
        ("70000", "4842.19"),
        ("200000", "29140.50"),
    ],
)
def test_line_31_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS).get(SCHEDULE_B_LINE_31)

    assert str(value.value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_apply_rate_over_line_18() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "reference": "31",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/schedule_b_line_31_rate"},
        "consumes": {"base": "ca-qc/schedule_b_line_18"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_31
    assert isinstance(SCHEDULE_B_LINE_31, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_31)
