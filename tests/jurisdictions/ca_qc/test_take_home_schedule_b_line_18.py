"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part A line 18, "Subtract line 16 from line 15. If the
result is negative, enter 0", as the Quebec take-home manifest wires it: one
`core/subtract_not_below_zero`, rounded half-up to the cent by `ca-qc/cent_rounding`. The expected
figures are hand-computed from the printed lines (line 14, which is line 10 for a single filer,
is line 275 at a salary of 20,000 / 70,000 / 200,000, less line 16, 42,090.00), not a Revenu Quebec
example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_18
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import schedule_b_sheet
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

D = Decimal
PART = "schedule_b_line_18.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_18"
EXPORTS = (IDENTIFIER,)
PARTS = (
    "schedule_b_line_10.yaml",
    "schedule_b_line_16.yaml",
    PART,
)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 10 is 18,635.00, below line 16: the negative result is entered as 0.
        ("20000", "0.00"),
        ("70000", "25825.00"),
        ("200000", "155416.00"),
    ],
)
def test_line_18_at_each_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS).get(SCHEDULE_B_LINE_18)

    assert str(value.value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_subtract_not_below_zero_of_line_16_from_line_10() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "18",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "amount": "ca-qc/schedule_b_line_10",
            "less": "ca-qc/schedule_b_threshold_line_16",
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is SCHEDULE_B_LINE_18
    assert isinstance(SCHEDULE_B_LINE_18, AmountKind)
    assert non_negative(SCHEDULE_B_LINE_18)
