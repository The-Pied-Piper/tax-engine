"""ON428 (2025) line 36, the medical expenses after the printed maximums, from the real part files
through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 36 and line 58689: See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses".
CRA 5006-PC "Ontario tax information for 2025", section "Line 58689": "the maximum Ontario claim for
attendant care expenses is $17,627 ($35,253 in the year of death)", "The maximum Ontario claim for
the cost of a van adapted for transporting a patient who requires the use of a wheelchair is $8,813"
and "The maximum Ontario claim for moving expenses for a patient's move to a more accessible
dwelling is $3,525".

The claim is the filer's medical claim; three optional inputs say how much of it is attendant care,
the van and the move, and a 0/1 count says the year of death. Each category above its maximum is
reduced to it (a cap, not a refusal); line 36 is the claim less what the categories lose. Only the
final step carries the reference "36" and step 10 (the sum) a title alone; the others are
unprinted and have no title. A result below 0 (a category larger than the claim) is refused,
never floored. The hand figures are asserted (not a CRA example).

The real input part and the new `on428_line_36.yaml` are loaded under a test-local header and form.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import CapabilityContractError, InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
INPUTS_PART = "on428_line_36_inputs.yaml"
PART = "on428_line_36.yaml"
CLAIM = "ca-on/on428_medical_expenses_line_36"
ATTENDANT = "ca-on/on428_attendant_care_expenses_line_36"
VAN = "ca-on/on428_adapted_van_expenses_line_36"
MOVE = "ca-on/on428_patient_move_expenses_line_36"
DEATH = "ca-on/on428_year_of_death_line_36"
OUTPUT = "ca-on/on428_medical_expenses_allowed_line_36"

HEADER = f"jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs: [{CLAIM}]\n"
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {OUTPUT}
capabilities: []
"""


def _line_36(take_home_service: TakeHomeService, **given: str) -> Decimal:
    names = {"claim": CLAIM, "att": ATTENDANT, "van": VAN, "move": MOVE, "death": DEATH}
    kinds = bundled_kinds()
    artifacts = [
        Artifact(kinds.kind(names[key]), int(value) if key == "death" else D(value))
        for key, value in given.items()
    ]
    service = take_home_service(HEADER, FORM, INPUTS_PART, PART)
    (sheet,) = service.compute(CODE, 2025, *artifacts)["ca-on/on428"]
    value = sheet.get(kinds.kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ({"claim": "5000"}, "5000.00"),
        ({}, "0.00"),
        ({"claim": "30000", "att": "20000"}, "27627.00"),
        ({"claim": "30000", "att": "10000"}, "30000.00"),
        ({"claim": "50000", "att": "40000", "death": "1"}, "45253.00"),
        ({"claim": "40000", "att": "30000", "death": "1"}, "40000.00"),
        ({"claim": "20000", "van": "10000"}, "18813.00"),
        ({"claim": "20000", "van": "8000"}, "20000.00"),
        ({"claim": "9000", "move": "4000"}, "8525.00"),
        ({"claim": "9000", "move": "3000"}, "9000.00"),
        ({"claim": "60000", "att": "20000", "van": "10000", "move": "4000"}, "55965.00"),
    ],
)
def test_line_36(take_home_service: TakeHomeService, given: dict[str, str], expected: str) -> None:
    assert _line_36(take_home_service, **given) == D(expected)


def test_a_year_of_death_flag_above_1_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_36(take_home_service, claim="50000", att="40000", death="2")


def test_categories_larger_than_the_claim_are_refused_not_floored(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(CapabilityContractError):
        _line_36(take_home_service, claim="1000", att="20000")


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / PART).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def test_the_part_has_the_steps_in_order_and_only_the_last_is_line_36() -> None:
    steps = _steps()

    assert [step["name"] for step in steps] == [
        "core/capped_amount",
        "core/capped_amount",
        "ca/yes_or_no_count",
        "core/choose_by_count",
        "core/capped_amount",
        "core/capped_amount",
        "core/subtract",
        "core/subtract",
        "core/subtract",
        "core/sum",
        "core/subtract",
    ]
    assert [step.get("reference") for step in steps] == [None] * 10 + ["36"]
    assert all("title" not in step for step in steps[:-2])
    assert "title" in steps[-2]
    final = {key: value for key, value in steps[-1].items() if key != "title"}
    assert final == {
        "name": "core/subtract",
        "reference": "36",
        "unit": "ca/cad",
        "params": {"rounding": "ca-on/cent_rounding"},
        "consumes": {
            "amount": CLAIM,
            "less": "ca-on/on428_medical_expenses_excess_line_36",
        },
        "blank": {"amount": "0"},
        "produces": {"output": OUTPUT},
    }
