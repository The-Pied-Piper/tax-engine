"""Revenu Quebec TP-1 (2025) line 399, "Add lines 377.1, 389 through 392, 395 through 397, 398 and
398.1. Non-refundable tax credits", as the Quebec take-home manifest wires it: one `core/sum`,
rounded half-up to the cent by `ca-qc/cent_rounding`. Lines 377.1, 389 and 397 are steps; lines 390,
392, 395, 396, 398 and 398.1 are optional inputs, read as 0 when the caller leaves them out; line
391 is TP-752.PC-V line 50 (zero for a filer with no birth year). The chain runs the real parts of
Schedule B and of the forms it reads (see `tp1_credits_support.py`). The expected figures are
hand-computed from the printed lines, not a Revenu Quebec example: line 377.1 is 2,599.94, or
2,897.86 at $20,000 for a person living alone.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358,
    TP1_LINE_381,
    TP1_LINE_390,
    TP1_LINE_398_1,
    TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399,
    TP1_UNION_DUES_LINE_397_1,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_399_PARTS, chain_sheet

D = Decimal
PART = "tp1_credits_line_399.yaml"
FORM = "ca-qc/tp1_credits"
IDENTIFIER = "ca-qc/tp1_non_refundable_tax_credits_line_399"
EXPORTS = (IDENTIFIER,)
LINE_399 = TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_399_with_every_optional_line_blank_is_line_377_1(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_399_PARTS)

    assert str(sheet.get(LINE_399).value) == "2599.94"


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "2897.86"), ("70000", "2599.94"), ("200000", "2599.94")]
)
def test_line_399_for_a_person_living_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = chain_sheet(take_home_service, salary, EXPORTS, LINE_399_PARTS, given)

    assert str(sheet.get(LINE_399).value) == expected


def test_line_399_adds_lines_389_397_390_and_398_1(take_home_service: TakeHomeService) -> None:
    given = (
        Artifact(TP1_LINE_381, D("1000")),
        Artifact(TP1_UNION_DUES_LINE_397_1, D("500")),
        Artifact(TP1_LINE_390, D("10.25")),
        Artifact(TP1_LINE_398_1, D("4.50")),
    )
    sheet = chain_sheet(take_home_service, "70000", EXPORTS, LINE_399_PARTS, *given)

    # 2,599.94 + 200.00 (line 389) + 50.00 (line 397) + 10.25 + 4.50
    assert str(sheet.get(LINE_399).value) == "2864.69"


def test_line_399_rounds_once_so_sub_cent_parts_in_different_subtotals_add_before_rounding(
    take_home_service: TakeHomeService,
) -> None:
    given = (
        Artifact(TP1_LINE_390, D("0.005")),
        Artifact(TP1_LINE_398_1, D("0.005")),
    )
    sheet = chain_sheet(take_home_service, "70000", EXPORTS, LINE_399_PARTS, *given)

    # 2,599.94 + 0.005 + 0.005 = 2,599.95: the unprinted subtotals do not round, the line does.
    assert str(sheet.get(LINE_399).value) == "2599.95"


def test_line_358_lowers_line_399(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358, D("1000"))
    sheet = chain_sheet(take_home_service, "70000", EXPORTS, LINE_399_PARTS, given)

    # (18,571.00 - 1,000.00) x 0.14 = 2,459.94
    assert str(sheet.get(LINE_399).value) == "2459.94"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _subtotal(title: str, parts: list[str], optional: list[str], output: str) -> dict[str, object]:
    return {
        "name": "core/sum",
        "title": title,
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/exact_rounding"},
        "consumes": {"parts": parts},
        "blank": {name: "0" for name in parts if name in optional},
        "produces": {"output": f"ca-qc/{output}"},
    }


def test_the_part_is_two_subtotals_and_a_sum_with_the_optional_lines_read_as_zero() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    first, last, step = part["capabilities"]
    optional = [f"ca-qc/tp1_line_{line}" for line in ("390", "392", "395", "396", "398")]
    optional.append("ca-qc/tp1_line_398_1")
    first_parts = [
        "ca-qc/tp1_line_377_1",
        "ca-qc/tp1_line_389",
        "ca-qc/tp1_line_390",
        "ca-qc/tp1_line_391",
        "ca-qc/tp1_line_392",
    ]
    last_parts = [
        "ca-qc/tp1_line_395",
        "ca-qc/tp1_line_396",
        "ca-qc/tp1_union_dues_credit_line_397",
        "ca-qc/tp1_line_398",
        "ca-qc/tp1_line_398_1",
    ]
    # Two unprinted subtotals keep the sentence of the numbered line short; the line adds them.
    assert first == _subtotal(
        "Lines 377.1 and 389 to 392 added up",
        first_parts,
        optional,
        "tp1_credits_lines_377_1_to_392_subtotal",
    )
    assert last == _subtotal(
        "Lines 395 to 398.1 added up",
        last_parts,
        optional,
        "tp1_credits_lines_395_to_398_1_subtotal",
    )
    assert step == {
        "name": "core/sum",
        "title": "Non-refundable tax credits",
        "reference": "399",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/tp1_credits_lines_377_1_to_392_subtotal",
                "ca-qc/tp1_credits_lines_395_to_398_1_subtotal",
            ]
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is LINE_399
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
