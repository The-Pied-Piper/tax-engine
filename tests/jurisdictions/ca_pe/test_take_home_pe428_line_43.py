"""PE428 (2025) line 43, line 41 at the printed 3%, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 42: Applicable rate 3%" and "Line 43: Line 41
multiplied by the percentage from line 42 = ^". Line 42 is the printed rate (a dataset figure, no
step); line 43 is line 41 times 3%, half-up to the cent: 595.05 at $20,000 (19,835.00), 892.05 at
$30,000 (29,735.00) and 2,080.05 at $70,000 (69,335.00), hand figures, not a CRA example.

The test builds the engine over the real federal parts and the real parts of lines 41 and 43
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_43
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
PART_NAME = "pe428_line_43.yaml"
OUTPUT = "ca-pe/pe428_medical_expenses_rate_amount_line_43"
PARTS = (*FEDERAL_PARTS, *NET_INCOME_PARTS, "pe428_line_41.yaml", PART_NAME)
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_medical_expenses_rate_amount_line_43": "595.05"}),
    ("30000", {}, {"ca-pe/pe428_medical_expenses_rate_amount_line_43": "892.05"}),
    ("70000", {}, {"ca-pe/pe428_medical_expenses_rate_amount_line_43": "2080.05"}),
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
            "name": "core/apply_rate",
            "reference": "43",
            "unit": "ca/cad",
            "params": {"rate": "ca-pe/medical_expense_rate"},
            "consumes": {"base": "ca-pe/pe428_net_income_line_41"},
            "produces": {"output": "ca-pe/pe428_medical_expenses_rate_amount_line_43"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (
            "ca-pe/pe428_medical_expenses_rate_amount_line_43",
            PE428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_43,
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
