"""PE428 (2025) line 54, line 50 plus line 53, the total non-refundable credits, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 54 and line 61500: Line 50 plus line 53 Enter
this amount on line 58. Prince Edward Island non-refundable tax credits = ^". A salary-only filer
has no donations (line 53 is 0.00), so line 54 equals line 50: 1,500.50 at $20,000, 1,563.11 at
$30,000 and 1,806.83 at $70,000. With donations of 1,000.00 at $20,000, line 53 is 171.00 and line
54 is 1,671.50 (hand figures, not a CRA example).

The test builds the engine over the real federal parts and the real parts of lines 9 to 54 through
the shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import SumLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_NON_REFUNDABLE_CREDITS_LINE_54
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_54,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_54.yaml"
OUTPUT = "ca-pe/pe428_non_refundable_credits_line_54"
PARTS = CHAIN_54
CASES = [
    ("20000", {}, {"ca-pe/pe428_non_refundable_credits_line_54": "1500.50"}),
    ("30000", {}, {"ca-pe/pe428_non_refundable_credits_line_54": "1563.11"}),
    ("70000", {}, {"ca-pe/pe428_non_refundable_credits_line_54": "1806.83"}),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "1000"},
        {
            "ca-pe/pe428_credits_at_rate_line_50": "1500.50",
            "ca-pe/pe428_donations_and_gifts_credit_line_53": "171.00",
            "ca-pe/pe428_non_refundable_credits_line_54": "1671.50",
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


def test_the_trace_is_one_sum_with_the_blank_parts_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SumLine)
        and t.output is kinds.kind("ca-pe/pe428_non_refundable_credits_line_54")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_credits_at_rate_line_50", D("1500.50")),
        ("ca-pe/pe428_donations_and_gifts_credit_line_53", D("0.00")),
    ]
    assert line.total == D("1500.50")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/sum",
            "title": "Prince Edward Island non-refundable tax credits",
            "reference": "54",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_credits_at_rate_line_50",
                    "ca-pe/pe428_donations_and_gifts_credit_line_53",
                ]
            },
            "produces": {"output": "ca-pe/pe428_non_refundable_credits_line_54"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_non_refundable_credits_line_54", PE428_NON_REFUNDABLE_CREDITS_LINE_54),
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
