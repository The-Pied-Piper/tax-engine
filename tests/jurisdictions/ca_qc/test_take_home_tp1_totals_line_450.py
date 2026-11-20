"""Revenu Quebec TP-1 (2025) line 450, "Add lines 432 through 447. Income tax and contributions", as
the Quebec take-home manifest wires it: one `core/sum`, rounded half-up to the cent by
`ca-qc/cent_rounding`. Lines 432, 446 and 447 are steps and lines 438, 439, 441, 443 and 445 are
optional inputs, read as 0 when left blank. The chain runs the real parts of the forms the three
steps read (see `tp1_totals_support.py`). The expected figures are hand-computed from the printed
lines, not a Revenu Quebec example: at $70,000 line 432 is 7,641.16 and line 447 is 755.00, so line
450 is 8,396.16."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_DRUG_INSURANCE_PREMIUM_LINE_447,
    TP1_HEALTH_SERVICES_FUND_LINE_446,
    TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450,
    TP1_LINE_438,
    TP1_LINE_439,
    TP1_LINE_441,
    TP1_LINE_443,
    TP1_LINE_445,
    TP1_TOTALS_LINE_432,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_450_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

D = Decimal
PART = "tp1_totals_line_450.yaml"
IDENTIFIER = "ca-qc/tp1_income_tax_and_contributions_line_450"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_450_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_450_PARTS)

    assert (
        str(sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value) == EXPECTED[salary]["450"]
    )


@pytest.mark.parametrize("salary", SALARIES)
def test_line_450_adds_lines_432_446_and_447(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_450_PARTS)

    assert sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value == (
        sheet.get(TP1_TOTALS_LINE_432).value
        + sheet.get(TP1_HEALTH_SERVICES_FUND_LINE_446).value
        + sheet.get(TP1_DRUG_INSURANCE_PREMIUM_LINE_447).value
    )


def test_the_optional_lines_are_added(take_home_service: TakeHomeService) -> None:
    given = [
        Artifact(TP1_LINE_438, D("100.50")),
        Artifact(TP1_LINE_439, D("20.25")),
        Artifact(TP1_LINE_441, D("3.10")),
        Artifact(TP1_LINE_443, D("4.00")),
        Artifact(TP1_LINE_445, D("5.05")),
    ]
    sheet = totals_sheet(
        take_home_service, "70000", totals_form(IDENTIFIER), LINE_450_PARTS, *given
    )

    # 8,396.16 and the five lines, 132.90 in all.
    assert str(sheet.get(TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450).value) == "8529.06"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_sum_of_lines_432_to_447() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": "Income tax and contributions",
        "reference": "450",
        "unit": "ca/cad",
        "params": {"rounding": "ca-qc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-qc/tp1_totals_line_432",
                "ca-qc/tp1_line_438",
                "ca-qc/tp1_line_439",
                "ca-qc/tp1_line_441",
                "ca-qc/tp1_line_443",
                "ca-qc/tp1_line_445",
                "ca-qc/tp1_health_services_fund_line_446",
                "ca-qc/tp1_drug_insurance_premium_line_447",
            ]
        },
        "blank": {
            "ca-qc/tp1_line_438": "0",
            "ca-qc/tp1_line_439": "0",
            "ca-qc/tp1_line_441": "0",
            "ca-qc/tp1_line_443": "0",
            "ca-qc/tp1_line_445": "0",
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_INCOME_TAX_AND_CONTRIBUTIONS_LINE_450
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
