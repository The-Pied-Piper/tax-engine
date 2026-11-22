"""Revenu Quebec TP-1 (2025) line 447, "Premium payable under the Québec prescription drug insurance
plan. Complete Schedule K or enter the number corresponding to your situation in box 449.", as the
Quebec take-home manifest wires it: one `core/record_total` over the line 98 export of
`ca-qc/tp1_schedule_k`. The chain runs the real Schedule K parts (see `tp1_totals_support.py`). The
answer to Schedule K line 50 is the default (not covered by a group drug plan) unless given; the
salary is $20,000, $70,000 and $200,000. The expected figures are hand-computed from the printed
lines, not a Revenu Quebec example."""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    TP1_DRUG_INSURANCE_PREMIUM_LINE_447,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_447_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

PART = "tp1_totals_line_447.yaml"
IDENTIFIER = "ca-qc/tp1_drug_insurance_premium_line_447"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_447_is_the_schedule_k_premium(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_447_PARTS)

    assert str(sheet.get(TP1_DRUG_INSURANCE_PREMIUM_LINE_447).value) == EXPECTED[salary]["447"]


@pytest.mark.parametrize(("salary", "expected"), [("20000", "0.00"), ("70000", "0.00")])
def test_line_447_for_a_person_covered_by_a_group_drug_plan(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    given = Artifact(SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, 1)
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_447_PARTS, given)

    assert str(sheet.get(TP1_DRUG_INSURANCE_PREMIUM_LINE_447).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Premium payable under the Québec prescription drug insurance plan",
        "reference": "447",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_schedule_k.schedule_k_premium_payable_line_98"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_DRUG_INSURANCE_PREMIUM_LINE_447
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
