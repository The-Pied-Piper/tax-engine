"""Revenu Quebec TP-1 (2025) line 425, "Add lines 414 through 424", as the Quebec take-home manifest
wires it: one `core/sum` over the printed lines 414, 415, 422 and 424, rounded half-up to the cent
by `ca-qc/cent_rounding`. Line 414 is computed from Work Chart 414 (always present, 0.00 when no
contributions are given); lines 415, 422 and 424 are optional inputs, read as 0 when the caller
leaves them out. The expected figures are hand-computed from the printed lines."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_415,
    TP1_LINE_422,
    TP1_LINE_424,
    TP1_LINE_425,
    WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_413_CHAIN, LINE_414_PARTS, tax_sheet
from tests.kinds import non_negative

D = Decimal
PART = "tp1_tax_line_425.yaml"
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_line_425"
EXPORTS = (IDENTIFIER,)
PARTS = (*LINE_413_CHAIN, *LINE_414_PARTS, "tp1_tax_line_425_inputs.yaml", PART)


def test_line_425_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS)

    assert str(sheet.get(TP1_LINE_425).value) == "0.00"


def test_line_425_adds_lines_414_415_422_and_424(take_home_service: TakeHomeService) -> None:
    # $100 of contributions is a line 414 of 80.00.
    given = (
        Artifact(WORK_CHART_414_CONTRIBUTIONS_INPUT_LINE_1, D("100")),
        Artifact(TP1_LINE_415, D("200.20")),
        Artifact(TP1_LINE_422, D("300.30")),
        Artifact(TP1_LINE_424, D("400.40")),
    )
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS, *given)

    assert str(sheet.get(TP1_LINE_425).value) == "980.90"


def test_line_425_reads_blank_lines_and_an_empty_chart_as_zero_beside_given_ones(
    take_home_service: TakeHomeService,
) -> None:
    given = (Artifact(TP1_LINE_415, D("200.20")), Artifact(TP1_LINE_424, D("400.40")))
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS, *given)

    assert str(sheet.get(TP1_LINE_425).value) == "600.60"


@pytest.mark.parametrize(("second", "expected"), [("0.001", "0.01"), ("0.0009", "0.00")])
def test_line_425_rounds_the_sum_half_up_to_the_cent(
    take_home_service: TakeHomeService, second: str, expected: str
) -> None:
    # 0.004 + 0.001 = 0.005 rounds up; 0.004 + 0.0009 = 0.0049 rounds down.
    given = (Artifact(TP1_LINE_415, D("0.004")), Artifact(TP1_LINE_422, D(second)))
    sheet = tax_sheet(take_home_service, "70000", EXPORTS, PARTS, *given)

    assert str(sheet.get(TP1_LINE_425).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_the_four_printed_lines_with_inputs_blank_read_as_zero() -> None:
    part = _part()
    lines = [f"ca-qc/tp1_line_{line}" for line in ("414", "415", "422", "424")]

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    # Line 414 is the chart's output, always computed, so it has no blank rule.
    assert step == {
        "name": "core/sum",
        "reference": "425",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {"parts": lines},
        "blank": {name: "0" for name in lines if name != "ca-qc/tp1_line_414"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_425
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
