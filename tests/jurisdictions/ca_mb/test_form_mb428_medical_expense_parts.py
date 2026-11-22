"""The MB428 (2025) medical expense part files, lines 43 to 50: each part's shape.

Form text (Form MB428, CRA 5007-c-25e.txt), lines 43 to 50: see
`end_to_end/test_mb428_medical_expenses.py` for the full text and the figures through the engine.
Each calculated line is one step, one line = one capability; line 43 reads the T1 medical expenses
export (`test_take_home_mb428_credits_line_43.py`) and line 49 is the total of Worksheet MB428
line 4 (see `test_take_home_mb428_credits_line_49.py`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative

MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FORM = {"name": "ca-mb/mb428_credits"}
STEPS = {
    "mb428_credits_line_44.yaml": {
        "name": "core/record_total",
        "reference": "44",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": "ca-mb/mb428_net_income_line_44"},
    },
    "mb428_credits_line_46.yaml": {
        "name": "core/apply_rate",
        "reference": "46",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/medical_expense_rate"},
        "consumes": {"base": "ca-mb/mb428_net_income_line_44"},
        "produces": {"output": "ca-mb/mb428_medical_expenses_rate_amount_line_46"},
    },
    "mb428_credits_line_47.yaml": {
        "name": "core/capped_amount",
        "reference": "47",
        "unit": "ca/cad",
        "params": {"cap": "ca-mb/medical_expense_dollar_limit"},
        "consumes": {"base": "ca-mb/mb428_medical_expenses_rate_amount_line_46"},
        "produces": {"output": "ca-mb/mb428_medical_expenses_limited_amount_line_47"},
    },
    "mb428_credits_line_48.yaml": {
        "name": "core/subtract_not_below_zero",
        "reference": "48",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {
            "amount": "ca-mb/mb428_medical_expenses_line_43",
            "less": "ca-mb/mb428_medical_expenses_limited_amount_line_47",
        },
        "blank": {"amount": "0"},
        "produces": {"output": "ca-mb/mb428_medical_expenses_over_limit_line_48"},
    },
    "mb428_credits_line_50.yaml": {
        "name": "core/sum",
        "title": "Medical expenses",
        "reference": "50",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-mb/mb428_medical_expenses_over_limit_line_48",
                "ca-mb/mb428_other_dependants_medical_expenses_line_49",
            ]
        },
        "produces": {"output": "ca-mb/mb428_medical_expenses_line_50"},
    },
}


def _load(name: str) -> dict[str, Any]:
    part = yaml.safe_load((MB_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


@pytest.mark.parametrize(("name", "step"), STEPS.items())
def test_each_calculated_line_is_one_step_on_the_credits_form(
    name: str, step: dict[str, Any]
) -> None:
    part = _load(name)

    assert part == {"form": FORM, "capabilities": [step]}


def test_the_old_line_50_input_part_is_gone() -> None:
    assert not (MB_PARTS / "mb428_credits_line_50_input.yaml").exists()


@pytest.mark.parametrize(
    ("identifier", "declared"),
    [
        ("ca-mb/mb428_medical_expenses_line_43", mb_catalog.MB428_MEDICAL_EXPENSES_LINE_43),
        ("ca-mb/mb428_net_income_line_44", mb_catalog.MB428_NET_INCOME_LINE_44),
        (
            "ca-mb/mb428_medical_expenses_rate_amount_line_46",
            mb_catalog.MB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_46,
        ),
        (
            "ca-mb/mb428_medical_expenses_limited_amount_line_47",
            mb_catalog.MB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_47,
        ),
        (
            "ca-mb/mb428_medical_expenses_over_limit_line_48",
            mb_catalog.MB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_48,
        ),
        (
            "ca-mb/mb428_other_dependants_medical_expenses_line_49",
            mb_catalog.MB428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_49,
        ),
        ("ca-mb/mb428_medical_expenses_line_50", mb_catalog.MB428_MEDICAL_EXPENSES_LINE_50),
    ],
)
def test_each_line_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, declared: AmountKind
) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert kind is declared
    assert isinstance(kind, AmountKind)
    assert kind.value_type.__name__ == "Decimal"
    assert non_negative(kind)
