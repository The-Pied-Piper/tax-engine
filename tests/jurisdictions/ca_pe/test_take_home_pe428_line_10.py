"""PE428 (2025) line 10, age amount, refused above its printed maximum.

Form text (Form PE428, CRA 5002-c-25e.txt): "Age amount (if you were born in 1960 or earlier) (use
Worksheet PE428) (maximum $6,510)". The line is an entry line: the claimed amount is refused above
the printed maximum ($6,510), not capped, as Newfoundland and Labrador's line 37 is. A blank claim
passes on as blank.

The test builds the engine over the real input and line parts through the shared `take_home_service`
fixture, under a test-local header and form declaration.
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
    PE428_AGE_AMOUNT_CLAIMED_LINE_10,
    PE428_AGE_AMOUNT_LINE_10,
    PE428_AGE_AMOUNT_MAXIMUM,
)
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import HEADER, SALARY_PARTS, compute, form
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_PART_NAME = "pe428_line_10.yaml"
CLAIMED = "ca-pe/pe428_age_amount_claimed_line_10"
MAXIMUM = "ca-pe/pe428_age_amount_maximum"
LINE = "ca-pe/pe428_age_amount_line_10"
TITLE = "Age amount"
PARTS = (*SALARY_PARTS, "pe428_line_10_input.yaml", LINE_PART_NAME)


def _line(take_home_service: TakeHomeService, claimed: str | None = None) -> Any:
    service = take_home_service(HEADER, form(LINE), *PARTS)
    sheet = compute(service, "20000", None if claimed is None else {CLAIMED: claimed})
    return sheet.get(prince_edward_island_kinds().kind(LINE))


def test_an_amount_at_the_maximum_passes_unchanged(take_home_service: TakeHomeService) -> None:
    assert D(_line(take_home_service, "6510").value) == D("6510.00")


def test_an_amount_below_the_maximum_passes_unchanged(take_home_service: TakeHomeService) -> None:
    assert D(_line(take_home_service, "250.50").value) == D("250.50")


def test_an_amount_of_zero_passes(take_home_service: TakeHomeService) -> None:
    assert D(_line(take_home_service, "0").value) == D("0")


def test_one_cent_above_the_maximum_is_refused_not_capped(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(InputAboveBoundError):
        _line(take_home_service, "6510.01")


def test_a_large_amount_is_refused_not_capped(take_home_service: TakeHomeService) -> None:
    with pytest.raises(InputAboveBoundError):
        _line(take_home_service, "50000")


def test_a_negative_amount_is_refused_by_the_non_negative_kind() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(prince_edward_island_kinds().kind(CLAIMED), D("-0.01"))


def test_a_salary_only_run_computes_and_leaves_the_line_blank(
    take_home_service: TakeHomeService,
) -> None:
    assert _line(take_home_service).is_blank


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / LINE_PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_has_a_maximum_step_with_no_title_and_no_reference_then_the_line() -> None:
    maximum, line = _part()["capabilities"]

    assert maximum == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": "ca-pe/age_amount_maximum"},
        "produces": {"output": MAXIMUM},
    }
    assert line == {
        "name": "core/at_most",
        "title": TITLE,
        "reference": "10",
        "unit": "ca/cad",
        "consumes": {"amount": CLAIMED, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": LINE},
    }


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (CLAIMED, PE428_AGE_AMOUNT_CLAIMED_LINE_10),
        (MAXIMUM, PE428_AGE_AMOUNT_MAXIMUM),
        (LINE, PE428_AGE_AMOUNT_LINE_10),
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
