"""ON428 (2025) line 36, the medical expenses after the printed attendant care, van and moving
rules, from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 36 and line 58689: See line 58689 at canada.ca/on-
tax-info for maximum allowable amounts for attendant care, an adapted van, and moving expenses".
CRA 5006-PC "Ontario tax information for 2025", section "Line 58689": "If the amount you claimed for
medical expenses on your return includes an amount for attendant care expenses that was limited to
$10,000 ($20,000 in the year of death), the maximum Ontario claim for attendant care expenses is
$17,627 ($35,253 in the year of death)", "The maximum Ontario claim for the cost of a van adapted
for transporting a patient who requires the use of a wheelchair is $8,813" and "The maximum Ontario
claim for moving expenses for a patient's move to a more accessible dwelling is $3,525".

The claim is the filer's medical claim. Attendant care takes the amount paid, a 0/1 answer that the
federal claim was limited and a 0/1 year of death. The increase is the paid amount at the Ontario
maximum less the paid amount at the federal limit, times the limited answer, so an answer of 0
changes nothing and a limited claim rises to the Ontario maximum. The van and the move take no
answer and have no year of death figure, because the guide prints their federal limits without a
condition, so the increase is the amount at the Ontario figure less the amount at the federal one:
Ontario $8,813 and $3,525 replace the federal $5,000 and $2,000
(CRA Guide RC4065 "Medical Expenses", PDF pages 19 and 22: "for residents of Ontario, the
provincial limit is $8,813" and "$3,525"). Only line 36 rounds, to the cent; the unprinted working
steps are exact (`ca-on/exact_rounding`). A blank input is read as 0 by a single-part `core/sum`
step of its own before its cap. Line 36 is the claim plus the three increases.
Only the final step carries the reference "36". A result below 0 is refused, never floored. The hand
figures are asserted (not a CRA example).

The real input part and the new `on428_line_36.yaml` are loaded under a test-local header and form.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
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
LIMITED = "ca-on/on428_attendant_care_federal_limit_applied_line_36"
OUTPUT = "ca-on/on428_medical_expenses_allowed_line_36"

HEADER = "jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\n"
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {OUTPUT}
capabilities: []
"""


def _line_36(take_home_service: TakeHomeService, **given: str) -> Decimal:
    names = {
        "claim": CLAIM,
        "att": ATTENDANT,
        "van": VAN,
        "move": MOVE,
        "death": DEATH,
        "limited": LIMITED,
    }
    kinds = bundled_kinds()
    artifacts = [
        Artifact(kinds.kind(names[key]), int(value) if key in ("death", "limited") else D(value))
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
        ({"claim": "30000", "att": "20000"}, "30000.00"),
        ({"claim": "30000", "att": "20000", "limited": "0"}, "30000.00"),
        ({"claim": "30000", "att": "20000", "limited": "1"}, "37627.00"),
        ({"claim": "30000", "att": "8000", "limited": "1"}, "30000.00"),
        ({"claim": "30000", "att": "40000", "death": "1", "limited": "1"}, "45253.00"),
        ({"claim": "20000", "van": "10000"}, "23813.00"),
        ({"claim": "20000", "van": "10000", "limited": "0"}, "23813.00"),
        ({"claim": "20000", "van": "8000"}, "23000.00"),
        ({"claim": "20000", "van": "5000"}, "20000.00"),
        ({"claim": "20000", "van": "4000"}, "20000.00"),
        ({"claim": "9000", "move": "4000"}, "10525.00"),
        ({"claim": "9000", "move": "3000"}, "10000.00"),
        ({"claim": "9000", "move": "1500"}, "9000.00"),
        # Exact until line 36: the unrounded claim 23813.004 rounds once, to 23813.00.
        ({"claim": "20000.004", "van": "10000.006"}, "23813.00"),
        (
            {"claim": "60000", "att": "20000", "limited": "1", "van": "10000", "move": "4000"},
            "72965.00",
        ),
    ],
)
def test_line_36(take_home_service: TakeHomeService, given: dict[str, str], expected: str) -> None:
    assert _line_36(take_home_service, **given) == D(expected)


@pytest.mark.parametrize(
    "given",
    [
        {"claim": "50000", "att": "40000", "death": "2"},
        {"claim": "50000", "att": "40000", "limited": "2"},
    ],
)
def test_a_yes_or_no_answer_above_1_is_refused(
    take_home_service: TakeHomeService, given: dict[str, str]
) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_36(take_home_service, **given)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / PART).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def test_the_part_has_the_steps_in_order_and_only_the_last_is_line_36() -> None:
    steps = _steps()
    category = [
        "core/sum",  # paid, a blank read as 0
        "core/capped_amount",  # Ontario cap
        "core/capped_amount",  # federal cap
        "core/subtract",  # Ontario less federal: the increase
    ]

    assert [step["name"] for step in steps] == [
        "core/sum",  # attendant care paid, a blank read as 0
        "core/capped_amount",  # Ontario attendant care cap, ordinary
        "core/capped_amount",  # Ontario cap, year of death
        "ca/yes_or_no_count",  # year of death check, shared
        "core/choose_by_count",  # Ontario allowed
        "core/capped_amount",  # federal cap, ordinary
        "core/capped_amount",  # federal cap, year of death
        "core/choose_by_count",  # federal included
        "core/subtract",  # Ontario allowed less federal included
        "ca/yes_or_no_count",  # limited answer check
        "core/times_count",  # increase times the limited answer
        *category,  # adapted van
        *category,  # patient move
        "core/sum",  # line 36: claim plus the three increases
    ]
    assert [step.get("reference") for step in steps] == [None] * 19 + ["36"]
    assert [i for i, step in enumerate(steps) if "title" in step] == [10, 14, 18, 19]
    for index in (0, 11, 15):
        assert steps[index]["blank"] == {"parts": "0"}
        assert len(steps[index]["consumes"]["parts"]) == 1
    rounded = [s for s in steps if s["name"] in ("core/sum", "core/subtract", "core/times_count")]
    assert [s["params"] for s in rounded[:-1]] == [{"rounding": "ca-on/exact_rounding"}] * 7
    assert steps[-1]["params"] == {"rounding": "ca-on/cent_rounding"}
    final = {key: value for key, value in steps[-1].items() if key not in ("title", "blank")}
    assert final == {
        "name": "core/sum",
        "reference": "36",
        "unit": "ca/cad",
        "params": {"rounding": "ca-on/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-on/on428_medical_expenses_line_36",
                "ca-on/on428_attendant_care_increase_line_36",
                "ca-on/on428_adapted_van_increase_line_36",
                "ca-on/on428_patient_move_increase_line_36",
            ],
        },
        "produces": {"output": OUTPUT},
    }
    assert steps[-1]["blank"] == {"ca-on/on428_medical_expenses_line_36": "0"}
    for first, cap, fed in (
        (11, "adapted_van", "federal_adapted_van"),
        (15, "patient_move", "federal_patient_move"),
    ):
        assert steps[first + 1]["params"] == {"cap": f"ca-on/medical_expense_{cap}_maximum"}
        assert steps[first + 2]["params"] == {"cap": f"ca-on/medical_expense_{fed}_maximum"}
