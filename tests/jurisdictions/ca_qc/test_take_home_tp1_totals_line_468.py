"""Revenu Quebec TP-1 (2025) line 468, "Add lines 465 and 466", as the Quebec take-home manifest
wires it: one `core/sum`, rounded half-up to the cent by `ca-qc/cent_rounding`. Line 466 is an
optional input, read as 0 when left blank. The chain runs the real Schedule P parts (see
`tp1_totals_support.py`). The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_FINANCIAL_COMPENSATION_LINE_466,
    TP1_LINE_468,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_468_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_468.yaml"
IDENTIFIER = "ca-qc/tp1_line_468"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_468_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_468_PARTS)

    assert str(sheet.get(TP1_LINE_468).value) == EXPECTED[salary]["468"]


@pytest.mark.parametrize(("salary", "expected"), [("20000", "684.27"), ("70000", "100.25")])
def test_line_466_is_added(take_home_service: TakeHomeService, salary: str, expected: str) -> None:
    given = Artifact(TP1_FINANCIAL_COMPENSATION_LINE_466, D("100.25"))
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_468_PARTS, given)

    assert str(sheet.get(TP1_LINE_468).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_lines_465_and_466() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "468",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/tp1_income_tax_paid_and_other_credits_line_465",
                "ca-qc/tp1_financial_compensation_line_466",
            ]
        },
        "blank": {"ca-qc/tp1_financial_compensation_line_466": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_LINE_468
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
