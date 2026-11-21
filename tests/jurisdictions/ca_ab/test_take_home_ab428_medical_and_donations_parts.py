"""AB428 (2025) lines 45, 47, 48, 49, 51, 55, 56 and 57, the calculated lines of the medical
expenses and donations blocks, as the Alberta take-home manifest parts declare them.

Form text (Form AB428, CRA 5009-c-25e.txt): line 45 "Amount from line 23600 of your return", line
46 "Applicable rate 3%", line 47 "Line 45 multiplied by the percentage from line 46 =", line 48
"Enter whichever is less: $2,884 or the amount from line 47.", line 49 "Line 44 minus line 48 (if
negative, enter "0") =", line 51 "Line 49 plus line 50 =", line 55 "Amount from line 13 of your
federal Schedule 9 multiplied by 60% =", line 56 "Amount from line 14 of your federal Schedule 9
multiplied by 21% =" and line 57 "Line 55 plus line 56 =". One engine step per printed line, the
printed rates and the $2,884 ceiling being datasets; the figures are exercised through the real
engine in `end_to_end/test_return_ab428_medical_and_donations.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.support import alberta_kinds
from tests.kinds import non_negative

PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FORM = {"name": "ca-ab/ab428_credits"}
CASES = [
    (
        "ab428_credits_line_45.yaml",
        {
            "name": "core/record_total",
            "reference": "45",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income"},
            "produces": {"output": "ca-ab/ab428_net_income_line_45"},
        },
    ),
    (
        "ab428_credits_line_47.yaml",
        {
            "name": "core/apply_rate",
            "reference": "47",
            "unit": "ca/cad",
            "params": {"rate": "ca-ab/medical_expense_rate"},
            "consumes": {"base": "ca-ab/ab428_net_income_line_45"},
            "produces": {"output": "ca-ab/ab428_medical_expenses_rate_amount_line_47"},
        },
    ),
    (
        "ab428_credits_line_48.yaml",
        {
            "name": "core/capped_amount",
            "reference": "48",
            "unit": "ca/cad",
            "params": {"cap": "ca-ab/medical_expense_dollar_limit"},
            "consumes": {"base": "ca-ab/ab428_medical_expenses_rate_amount_line_47"},
            "produces": {"output": "ca-ab/ab428_medical_expenses_limited_amount_line_48"},
        },
    ),
    (
        "ab428_credits_line_49.yaml",
        {
            "name": "core/subtract_not_below_zero",
            "reference": "49",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ab/cent_rounding"},
            "consumes": {
                "amount": "ca-ab/ab428_medical_expenses_line_44",
                "less": "ca-ab/ab428_medical_expenses_limited_amount_line_48",
            },
            "blank": {"amount": "0"},
            "produces": {"output": "ca-ab/ab428_medical_expenses_over_limit_line_49"},
        },
    ),
    (
        "ab428_credits_line_51.yaml",
        {
            "name": "core/sum",
            "title": "Medical expenses",
            "reference": "51",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ab/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-ab/ab428_medical_expenses_over_limit_line_49",
                    "ca-ab/ab428_allowable_medical_expenses_for_other_dependants_line_50",
                ]
            },
            "blank": {"ca-ab/ab428_allowable_medical_expenses_for_other_dependants_line_50": "0"},
            "produces": {"output": "ca-ab/ab428_medical_expenses_line_51"},
        },
    ),
    (
        "ab428_credits_line_55.yaml",
        {
            "name": "core/apply_rate",
            "reference": "55 box B",
            "unit": "ca/cad",
            "params": {"rate": "ca-ab/donations_credit_rate_line_55"},
            "consumes": {"base": "ca-ab/ab428_donations_amount_line_55"},
            "blank": {"base": "0"},
            "produces": {"output": "ca-ab/ab428_donations_credit_at_first_rate_line_55"},
        },
    ),
    (
        "ab428_credits_line_56.yaml",
        {
            "name": "core/apply_rate",
            "reference": "56 box B",
            "unit": "ca/cad",
            "params": {"rate": "ca-ab/donations_credit_rate_line_56"},
            "consumes": {"base": "ca-ab/ab428_donations_amount_line_56"},
            "blank": {"base": "0"},
            "produces": {"output": "ca-ab/ab428_donations_credit_at_second_rate_line_56"},
        },
    ),
    (
        "ab428_credits_line_57.yaml",
        {
            "name": "core/sum",
            "title": "Donations and gifts",
            "reference": "57",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ab/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-ab/ab428_donations_credit_at_first_rate_line_55",
                    "ca-ab/ab428_donations_credit_at_second_rate_line_56",
                ]
            },
            "produces": {"output": "ca-ab/ab428_donations_credit_line_57"},
        },
    ),
]


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize(("name", "step"), CASES)
def test_the_part_names_the_form_and_is_one_step_as_the_form_prints_the_line(
    name: str, step: dict[str, Any]
) -> None:
    part = _part(name)

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == FORM
    assert part["capabilities"] == [step]


@pytest.mark.parametrize(("name", "step"), CASES)
def test_the_line_is_a_registered_non_negative_amount_kind(name: str, step: dict[str, Any]) -> None:
    identifier = step["produces"]["output"]
    kinds = alberta_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
