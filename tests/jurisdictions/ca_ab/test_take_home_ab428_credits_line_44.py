"""AB428 (2025) line 44, from the salary and the optional inputs, through the real engine.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 44 and line 58689: Amount from line 33099 of
your return". The part is one core/sum step that reads a blank as 0 and rounds to the cent; the
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
    / "ab428_credits_line_44.yaml"
)
KIND = "ca-ab/ab428_medical_expenses_rounded_line_44"
STEP: dict[str, Any] = {
    "name": "core/sum",
    "reference": "44",
    "unit": "ca/cad",
    "params": {"rounding": "ca-ab/cent_rounding"},
    "consumes": {"parts": ["ca-ab/ab428_medical_expenses_line_44"]},
    "blank": {"ca-ab/ab428_medical_expenses_line_44": "0"},
    "produces": {"output": "ca-ab/ab428_medical_expenses_rounded_line_44"},
}

# salary, given inputs, expected line
CASES: list[tuple[str, dict[str, str], str]] = [
    ("70000", {}, "0.00"),
    ("70000", {"line_44": "100.005"}, "100.01"),
    ("70000", {"line_44": "5000"}, "5000.00"),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_is_ab428_medical_expenses_rounded_line_44_at_each_case(
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
