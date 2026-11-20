"""Revenu Quebec TP-1 (2025) line 350, "Basic personal amount ... 350 18,571 00", as the Quebec
take-home manifest wires it: one `core/credit_amount` over the dataset
`ca-qc/tp1_basic_personal_amount_line_350`, claimed whole. The figure does not depend on the salary.
"""

from __future__ import annotations

from typing import Any

import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_BASIC_PERSONAL_AMOUNT_LINE_350
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import credits_sheet
from tests.kinds import non_negative

FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_350.yaml"
IDENTIFIER = "ca-qc/tp1_basic_personal_amount_line_350"
EXPORTS = (IDENTIFIER,)


def test_line_350_is_the_printed_18571(take_home_service: TakeHomeService) -> None:
    sheet = credits_sheet(take_home_service, EXPORTS, (PART,))

    assert str(sheet.get(TP1_BASIC_PERSONAL_AMOUNT_LINE_350).value) == "18571.00"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_credit_amount_over_the_dataset_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/credit_amount",
        "title": "Basic personal amount",
        "reference": "350",
        "unit": "ca/cad",
        "params": {"amount": IDENTIFIER},
        "produces": {"output": IDENTIFIER},
    }


def test_it_is_not_the_federal_basic_personal_amount_kind() -> None:
    assert IDENTIFIER != "ca-qc/basic_personal_amount"


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is TP1_BASIC_PERSONAL_AMOUNT_LINE_350
    assert isinstance(TP1_BASIC_PERSONAL_AMOUNT_LINE_350, AmountKind)
    assert non_negative(TP1_BASIC_PERSONAL_AMOUNT_LINE_350)
