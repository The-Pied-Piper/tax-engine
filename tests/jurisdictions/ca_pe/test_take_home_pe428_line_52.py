"""PE428 (2025) line 52, computed from the real part files through the real engine.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 52: Amount from line 14 of your federal Schedule
9 multiplied by 19% = ^". The amount is the federal Schedule 9 line 14 export, totalled by the
first step of `pe428_line_52.yaml` (box A); its second step applies the 19% (box B). A blank
Schedule 9 reads as 0. With no donations both boxes are 0.00. With donations of 1,000.00 box A is
the 800.00 beyond the first 200.00 and box B is 152.00; with 300.00 box B is 19.00; with 5.00,
under the 200.00, both are 0.00 (hand figures, not a CRA example).

The test builds the engine over the real Schedule 9 parts and the real part of line 52 through the
shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import (
    PE428_DONATIONS_AMOUNT_LINE_52,
    PE428_DONATIONS_CREDIT_AT_RATE_LINE_52,
)
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    DONATION_PARTS,
    HEADER,
    SALARY_PARTS,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_52.yaml"
OUTPUT = "ca-pe/pe428_donations_credit_at_rate_line_52"
PARTS = (*SALARY_PARTS, *DONATION_PARTS, PART_NAME)
CASES = [
    (
        "20000",
        {},
        {
            "ca-pe/pe428_donations_amount_line_52": "0.00",
            "ca-pe/pe428_donations_credit_at_rate_line_52": "0.00",
        },
    ),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "1000"},
        {
            "ca-pe/pe428_donations_amount_line_52": "800.00",
            "ca-pe/pe428_donations_credit_at_rate_line_52": "152.00",
        },
    ),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "5.00"},
        {
            "ca-pe/pe428_donations_amount_line_52": "0.00",
            "ca-pe/pe428_donations_credit_at_rate_line_52": "0.00",
        },
    ),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "300"},
        {
            "ca-pe/pe428_donations_amount_line_52": "100.00",
            "ca-pe/pe428_donations_credit_at_rate_line_52": "19.00",
        },
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
            "name": "core/record_total",
            "title": "Amount from line 14 of your federal Schedule 9",
            "reference": "52 box A",
            "unit": "ca/cad",
            "consumes": {"records": "ca/schedule_9.donations_and_gifts_line_14"},
            "produces": {"output": "ca-pe/pe428_donations_amount_line_52"},
        },
        {
            "name": "core/apply_rate",
            "reference": "52 box B",
            "unit": "ca/cad",
            "params": {"rate": "ca-pe/donations_credit_rate_line_52"},
            "consumes": {"base": "ca-pe/pe428_donations_amount_line_52"},
            "blank": {"base": "0"},
            "produces": {"output": "ca-pe/pe428_donations_credit_at_rate_line_52"},
        },
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_donations_amount_line_52", PE428_DONATIONS_AMOUNT_LINE_52),
        ("ca-pe/pe428_donations_credit_at_rate_line_52", PE428_DONATIONS_CREDIT_AT_RATE_LINE_52),
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
