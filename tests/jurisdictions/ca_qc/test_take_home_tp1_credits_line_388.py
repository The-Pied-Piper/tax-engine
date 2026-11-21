"""Revenu Quebec TP-1 (2025) line 388, "Add lines 378 through 385", as the Quebec take-home manifest
wires it: one `core/sum` over the printed lines 378, 381 and 385, rounded half-up to the cent by
`ca-qc/cent_rounding`. The three lines are optional inputs, read as 0 when the caller leaves them
out. The expected figures are hand-computed from the printed lines."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_378,
    TP1_LINE_381,
    TP1_LINE_385,
    TP1_LINE_388,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_388_PARTS, credits_sheet
from tests.kinds import non_negative

D = Decimal
PART = "tp1_credits_line_388.yaml"
FORM = "ca-qc/tp1_credits"
IDENTIFIER = "ca-qc/tp1_line_388"
EXPORTS = (IDENTIFIER,)


def test_line_388_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_388_PARTS)

    assert str(sheet.get(TP1_LINE_388).value) == "0.00"


def test_line_388_adds_lines_378_381_and_385(take_home_service: TakeHomeService) -> None:
    given = (
        Artifact(TP1_LINE_378, D("1000.00")),
        Artifact(TP1_LINE_381, D("200.56")),
        Artifact(TP1_LINE_385, D("34.00")),
    )
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_388_PARTS, *given)

    assert str(sheet.get(TP1_LINE_388).value) == "1234.56"


def test_line_388_reads_a_blank_line_as_zero_beside_a_given_one(
    take_home_service: TakeHomeService,
) -> None:
    given = (Artifact(TP1_LINE_381, D("200.56")), Artifact(TP1_LINE_385, D("34.00")))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_388_PARTS, *given)

    assert str(sheet.get(TP1_LINE_388).value) == "234.56"


@pytest.mark.parametrize(("second", "expected"), [("0.001", "0.01"), ("0.0009", "0.00")])
def test_line_388_rounds_the_sum_half_up_to_the_cent(
    take_home_service: TakeHomeService, second: str, expected: str
) -> None:
    # 0.004 + 0.001 = 0.005 rounds up; 0.004 + 0.0009 = 0.0049 rounds down.
    given = (Artifact(TP1_LINE_378, D("0.004")), Artifact(TP1_LINE_385, D(second)))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_388_PARTS, *given)

    assert str(sheet.get(TP1_LINE_388).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_the_three_printed_lines_with_blanks_read_as_zero() -> None:
    part = _part()
    lines = ["ca-qc/tp1_line_378", "ca-qc/tp1_line_381", "ca-qc/tp1_line_385"]

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "388",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {"parts": lines},
        "blank": {name: "0" for name in lines},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_388
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
