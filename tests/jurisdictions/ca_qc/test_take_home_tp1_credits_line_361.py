"""Revenu Quebec TP-1 (2025) line 361, "Age amount, amount for a person living alone and amount for
retirement income. Complete Schedule B", as the Quebec take-home manifest wires it: one
`core/record_total` over the line 34 export of `ca-qc/schedule_b`. The chain runs the real parts of
Schedule B and of the forms it reads (see `tp1_credits_support.py`). The salary is $20,000, $70,000
and $200,000. The expected figures are hand-computed from the printed lines, not a Revenu Quebec
example: Schedule B line 34 is 0.00 unless the filer lives alone, and 2,128.00 at $20,000 if
they do.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_B_LIVED_ALONE_LINE_20,
    TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import chain_sheet

FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_361.yaml"
IDENTIFIER = "ca-qc/tp1_age_living_alone_retirement_amount_line_361"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_361_is_zero_when_the_filer_does_not_live_alone(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = chain_sheet(take_home_service, salary, EXPORTS, (PART,))

    assert str(sheet.get(TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361).value) == "0.00"


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "2128.00"), ("70000", "0.00"), ("200000", "0.00")]
)
def test_line_361_is_schedule_b_line_34_for_a_person_living_alone(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_B_LIVED_ALONE_LINE_20, 1)
    sheet = chain_sheet(take_home_service, salary, EXPORTS, (PART,), given)

    assert str(sheet.get(TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_schedule_b_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Age amount, amount for a person living alone and amount for retirement income",
        "reference": "361",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/schedule_b.schedule_b_line_34"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_signed_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
