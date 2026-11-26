"""PE428 (2025) line 45, line 40 minus line 44, not below zero, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 45: Line 40 minus line 44 (if negative, enter
"0") = ^". With no medical expenses (line 40 is 0.00) line 45 is 0.00 at every salary. With
medical expenses of 5,000.00 on the return, line 45 is 5,000.00 less line 44: 4,404.95 at $20,000
(595.05), 4,107.95 at $30,000 (892.05) and 3,322.00 at $70,000 (the 1,678.00 ceiling); with 100.00
it is 0.00 (a negative difference is entered as 0). Hand figures, not a CRA example. The form
prints no label for line 45, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 40 to 45
through the shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import PE428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_45
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    FEDERAL_PARTS,
    HEADER,
    NET_INCOME_PARTS,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_45.yaml"
OUTPUT = "ca-pe/pe428_medical_expenses_over_limit_line_45"
PARTS = (
    *FEDERAL_PARTS,
    *NET_INCOME_PARTS,
    "pe428_line_40.yaml",
    "pe428_line_41.yaml",
    "pe428_line_43.yaml",
    "pe428_line_44.yaml",
    PART_NAME,
)
CASES = [
    ("20000", {}, {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.00"}),
    (
        "20000",
        {"ca/medical_expenses": "5000"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "4404.95"},
    ),
    (
        "30000",
        {"ca/medical_expenses": "5000"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "4107.95"},
    ),
    (
        "70000",
        {"ca/medical_expenses": "5000"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "3322.00"},
    ),
    (
        "20000",
        {"ca/medical_expenses": "100"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.00"},
    ),
    (
        "20000",
        {"ca/medical_expenses": "595.05"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.00"},
    ),
    (
        "20000",
        {"ca/medical_expenses": "595.06"},
        {"ca-pe/pe428_medical_expenses_over_limit_line_45": "0.01"},
    ),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(OUTPUT), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_figures(
    take_home_service: TakeHomeService,
    salary: str,
    given: dict[str, str],
    expected: dict[str, str],
) -> None:
    sheet = _sheet(take_home_service, salary, given)

    for identifier, amount in expected.items():
        assert value(sheet, identifier) == D(amount)


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "45",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_medical_expenses_line_40",
                "less": "ca-pe/pe428_medical_expenses_limited_amount_line_44",
            },
            "produces": {"output": "ca-pe/pe428_medical_expenses_over_limit_line_45"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (
            "ca-pe/pe428_medical_expenses_over_limit_line_45",
            PE428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_45,
        ),
    ],
)
def test_each_kind_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, constant: AmountKind
) -> None:
    kind = prince_edward_island_kinds().kind(identifier)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
