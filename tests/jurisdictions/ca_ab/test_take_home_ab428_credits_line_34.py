"""AB428 line 34, the pension income amount checked against its printed maximum, real parts.

Form text (Form AB428, CRA 5009-c-25e.txt line 142, confirmed): "Line 34 and line 58360: Pension
income amount (maximum $1,719) ^". Line 34 is an entry line with no worksheet: an amount typed above
the printed maximum is rejected with `InputAboveBoundError`, not capped. The maximum is a dataset
figure (`ca-ab/pension_income_amount_maximum`), never an input.

Two parts make the line. `ab428_pension_income_amount_maximum.yaml` is `core/credit_amount` over
that dataset and produces `ca-ab/pension_income_amount_maximum`; the maximum is an intermediate
step and carries no line number in its title, reference or kind name. `ab428_credits_line_34.yaml`
is `core/at_most`, consuming the `ca-ab/ab428_pension_income_amount` input against that maximum and
producing `ca-ab/ab428_pension_income_amount_line_34`, the figure of line 34 that line 36 adds.

The part layout is checked here on the real files; the behaviour (passing, rejection, trace) is
checked end to end in `end_to_end/test_ab428_pension_income_amount_maximum.py`.
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
from tests.kinds import non_negative

D = Decimal
PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
MAXIMUM_PART = PARTS / "ab428_pension_income_amount_maximum.yaml"
LINE_PART = PARTS / "ab428_credits_line_34.yaml"
INPUT = "ca-ab/ab428_pension_income_amount"
MAXIMUM = "ca-ab/pension_income_amount_maximum"
LINE_34 = "ca-ab/ab428_pension_income_amount_line_34"


def _part(path: Path) -> dict[str, Any]:
    part = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_maximum_part_is_one_credit_amount_step_with_no_line_number() -> None:
    part = _part(MAXIMUM_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"
    assert step["title"] == "Pension income amount maximum"
    assert "reference" not in step
    assert step["params"] == {"amount": MAXIMUM}
    assert step["produces"] == {"output": MAXIMUM}
    assert "consumes" not in step


def test_the_line_34_part_is_one_at_most_step_over_the_input_and_the_maximum() -> None:
    part = _part(LINE_PART)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert step["name"] == "core/at_most"
    assert step["title"] == "Pension income amount"
    assert step["reference"] == "34"
    assert step["consumes"] == {"amount": INPUT, "bound": MAXIMUM}
    assert step["produces"] == {"output": LINE_34}
    assert "params" not in step


def test_the_input_keeps_its_name_and_default_of_0() -> None:
    part = _part(PARTS / "ab428_line_34_inputs.yaml")

    (declared,) = part["inputs"]
    assert declared["name"] == INPUT
    assert declared["required"] is False
    assert declared["default"] == "0"


@pytest.mark.parametrize("identifier", [MAXIMUM, LINE_34])
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(identifier: str) -> None:
    kind = alberta_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
