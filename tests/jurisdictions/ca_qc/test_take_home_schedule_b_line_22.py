"""Quebec Schedule B (TP-1.D.B-V, 2025-12) Part B line 22, the age amount, as the Quebec take-home
manifest wires it, in three steps.

Line 22: "If you were born before January 1, 1961, enter $3,906." The year of birth is the 5005-R's
optional input (`ca/birth_year`), read through the T1's export; a caller who gives none is not
claiming the amount. The expected figures are the printed $3,906 and 0, not a Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_AGE_AMOUNT_LINE_22,
    SCHEDULE_B_BIRTH_YEAR_LINE_22,
    SCHEDULE_B_BORN_BEFORE_1961_LINE_22,
    SCHEDULE_B_LINE_22,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_b_support import (
    LINE_22_PARTS,
    schedule_b_sheet,
)
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = "schedule_b_line_22.yaml"
FORM = "ca-qc/schedule_b"
IDENTIFIER = "ca-qc/schedule_b_line_22"
EXPORTS = (IDENTIFIER,)
PARTS = LINE_22_PARTS


def line_22(take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]) -> str:
    sheet = schedule_b_sheet(take_home_service, salary, EXPORTS, PARTS, *given)
    return str(sheet.get(SCHEDULE_B_LINE_22).value)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_22_is_0_when_the_caller_gives_no_birth_year(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_22(take_home_service, salary) == "0.00"


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
@pytest.mark.parametrize("year", [1925, 1959, 1960])
def test_line_22_is_3906_when_born_in_1960_or_earlier(
    take_home_service: TakeHomeService, salary: str, year: int
) -> None:
    assert line_22(take_home_service, salary, Artifact(BIRTH_YEAR, year)) == "3906.00"


@pytest.mark.parametrize("year", [1961, 1990, 2007])
def test_line_22_is_0_when_born_in_1961_or_later(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert line_22(take_home_service, "70000", Artifact(BIRTH_YEAR, year)) == "0.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_four_steps_and_only_the_last_carries_the_reference() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    steps = part["capabilities"]
    assert [step["name"] for step in steps] == [
        "core/first_record_count",
        "ca/count_by_conditions",
        "core/credit_amount",
        "core/times_count",
    ]
    assert [step.get("reference") for step in steps] == [None, None, None, "22"]
    assert [step["produces"]["output"] for step in steps] == [
        "ca-qc/schedule_b_birth_year_line_22",
        "ca-qc/schedule_b_born_before_1961_line_22",
        "ca-qc/schedule_b_age_amount_line_22",
        IDENTIFIER,
    ]
    assert steps[0]["consumes"] == {"records": "ca-qc/t1_tax_and_credits.birth_year"}
    assert steps[0]["blank"] == {"records": {"ca/birth_year": "pass_on"}}
    assert steps[1]["params"] == {"conditions": "ca-qc/schedule_b_line_22_conditions"}
    assert steps[2]["params"] == {"amount": "ca-qc/schedule_b_age_amount_line_22"}
    assert steps[3]["consumes"] == {
        "amount": "ca-qc/schedule_b_age_amount_line_22",
        "count": "ca-qc/schedule_b_born_before_1961_line_22",
    }
    assert steps[3]["blank"] == {"count": "0"}


@pytest.mark.parametrize(
    "kind", [SCHEDULE_B_BIRTH_YEAR_LINE_22, SCHEDULE_B_BORN_BEFORE_1961_LINE_22]
)
def test_the_count_kinds_are_registered_non_negative_counts(kind: CountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, CountKind)
    assert non_negative(kind)


@pytest.mark.parametrize("kind", [SCHEDULE_B_AGE_AMOUNT_LINE_22, SCHEDULE_B_LINE_22])
def test_the_amount_kinds_are_registered_non_negative_amounts(kind: AmountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
