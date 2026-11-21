"""AB428 (2025) line 56 box B, from the salary and the optional inputs, through the real engine.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 56: Amount from line 14 of your federal
Schedule 9 multiplied by 21% =". The part is one core/apply_rate step at the printed rate; the
figures are hand-computed from the printed form (not a CRA example): a $70,000 salary has net
income 69,335.00 (the salary less the enhanced CPP deduction).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.support import alberta_kinds
from tests.jurisdictions.ca_ab.support_medical import credits_sheet, figure
from tests.kinds import non_negative

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "ab428_credits_line_56.yaml"
)
KIND = "ca-ab/ab428_donations_credit_at_second_rate_line_56"
STEP: dict[str, Any] = {
    "name": "core/apply_rate",
    "reference": "56 box B",
    "unit": "ca/cad",
    "params": {"rate": "ca-ab/donations_credit_rate_line_56"},
    "consumes": {"base": "ca-ab/ab428_donations_amount_rounded_line_56"},
    "produces": {"output": "ca-ab/ab428_donations_credit_at_second_rate_line_56"},
}

# salary, given inputs, expected line
CASES: list[tuple[str, dict[str, str], str]] = [
    ("70000", {}, "0.00"),
    ("70000", {"line_56": "1000"}, "210.00"),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_is_ab428_donations_credit_at_second_rate_line_56_at_each_case(
    salary: str, given: dict[str, str], expected: str
) -> None:
    assert figure(credits_sheet(salary, **given), KIND) == D(expected)


def test_the_part_names_the_form_and_is_one_step_as_the_form_prints_the_line() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part == {"form": {"name": "ca-ab/ab428_credits"}, "capabilities": [STEP]}
    assert list(part) == ["form", "capabilities"]


def test_the_line_is_a_registered_non_negative_amount_kind() -> None:
    kind = alberta_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
