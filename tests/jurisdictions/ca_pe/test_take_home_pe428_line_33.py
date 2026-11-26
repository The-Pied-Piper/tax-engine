"""PE428 (2025) line 33, teacher school supply amount, refused above its printed maximum.

Form text (Form PE428, CRA 5002-c-25e.txt): "Teacher school supply amount (maximum $500)". The
line is an entry line: the claimed amount is refused above the printed maximum ($500), not capped,
as line 10 is. A blank claim passes on as blank.

The test builds the engine over the real input and line parts through the shared
`take_home_service` fixture, under a test-local header and form declaration.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import (
    PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_CLAIMED_LINE_33,
    PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_LINE_33,
    PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_MAXIMUM,
)
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    HEADER,
    SALARY_PARTS,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_33.yaml"
OUTPUT = "ca-pe/pe428_teacher_school_supply_amount_line_33"
PARTS = (*SALARY_PARTS, "pe428_line_33_input.yaml", PART_NAME)
CASES = [
    (
        "20000",
        {"ca-pe/pe428_teacher_school_supply_amount_claimed_line_33": "250.50"},
        {"ca-pe/pe428_teacher_school_supply_amount_line_33": "250.50"},
    ),
    (
        "20000",
        {"ca-pe/pe428_teacher_school_supply_amount_claimed_line_33": "0"},
        {"ca-pe/pe428_teacher_school_supply_amount_line_33": "0.00"},
    ),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(OUTPUT), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_figures(
    take_home_service: TakeHomeService,
    salary: str,
    given: dict[str, str],
    expected: dict[str, str],
) -> None:
    sheet = _sheet(take_home_service, salary, given)

    for identifier, amount in expected.items():
        assert value(sheet, identifier) == D(amount)


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": "ca-pe/teacher_school_supply_amount_maximum"},
            "produces": {"output": "ca-pe/pe428_teacher_school_supply_amount_maximum"},
        },
        {
            "name": "core/at_most",
            "title": "Teacher school supply amount (maximum $500)",
            "reference": "33",
            "unit": "ca/cad",
            "consumes": {
                "amount": "ca-pe/pe428_teacher_school_supply_amount_claimed_line_33",
                "bound": "ca-pe/pe428_teacher_school_supply_amount_maximum",
            },
            "blank": {"amount": "pass_on"},
            "produces": {"output": "ca-pe/pe428_teacher_school_supply_amount_line_33"},
        },
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (
            "ca-pe/pe428_teacher_school_supply_amount_claimed_line_33",
            PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_CLAIMED_LINE_33,
        ),
        (
            "ca-pe/pe428_teacher_school_supply_amount_maximum",
            PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_MAXIMUM,
        ),
        (
            "ca-pe/pe428_teacher_school_supply_amount_line_33",
            PE428_TEACHER_SCHOOL_SUPPLY_AMOUNT_LINE_33,
        ),
    ],
)
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, constant: AmountKind
) -> None:
    kind = prince_edward_island_kinds().kind(identifier)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


CLAIMED = "ca-pe/pe428_teacher_school_supply_amount_claimed_line_33"
LINE = "ca-pe/pe428_teacher_school_supply_amount_line_33"


def test_an_amount_at_the_maximum_passes_unchanged(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "20000", {CLAIMED: "500"})

    assert value(sheet, LINE) == D("500.00")


def test_one_cent_above_the_maximum_is_refused_not_capped(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(take_home_service, "20000", {CLAIMED: "500.01"})


def test_a_large_amount_is_refused_not_capped(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(take_home_service, "20000", {CLAIMED: "50000"})


def test_a_negative_amount_is_refused_by_the_non_negative_kind() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(prince_edward_island_kinds().kind(CLAIMED), D("-0.01"))


def test_a_salary_only_run_computes_and_leaves_the_line_blank(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")

    assert sheet.get(prince_edward_island_kinds().kind(LINE)).is_blank
