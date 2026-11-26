"""PE428 (2025) line 53, line 51 plus line 52, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 53 and line 58969: Line 51 plus line 52 = ^". A
salary-only filer has no donations, so both lines are 0.00 and line 53 is 0.00. With donations of
1,000.00, line 51 is 19.00 and line 52 is 152.00, so line 53 is 171.00; with 300.00 it is 19.00 +
19.00 = 38.00 (hand figures, not a CRA example). The form prints no label for line 53, so the step
has no title.

The test builds the engine over the real Schedule 9 parts and the real parts of lines 51 to 53
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
from tax_engine.domain.trace import SumLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_DONATIONS_AND_GIFTS_CREDIT_LINE_53
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
PART_NAME = "pe428_line_53.yaml"
OUTPUT = "ca-pe/pe428_donations_and_gifts_credit_line_53"
PARTS = (
    *SALARY_PARTS,
    *DONATION_PARTS,
    "pe428_line_51.yaml",
    "pe428_line_52.yaml",
    PART_NAME,
)
CASES = [
    ("20000", {}, {"ca-pe/pe428_donations_and_gifts_credit_line_53": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_donations_and_gifts_credit_line_53": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_donations_and_gifts_credit_line_53": "0.00"}),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "1000"},
        {
            "ca-pe/pe428_donations_credit_at_rate_line_51": "19.00",
            "ca-pe/pe428_donations_credit_at_rate_line_52": "152.00",
            "ca-pe/pe428_donations_and_gifts_credit_line_53": "171.00",
        },
    ),
    (
        "20000",
        {"ca/donations_and_gifts_line_12": "300"},
        {"ca-pe/pe428_donations_and_gifts_credit_line_53": "38.00"},
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
        and t.output is kinds.kind("ca-pe/pe428_donations_and_gifts_credit_line_53")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_donations_credit_at_rate_line_51", D("0.00")),
        ("ca-pe/pe428_donations_credit_at_rate_line_52", D("0.00")),
    ]
    assert line.total == D("0.00")


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
            "reference": "53",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_donations_credit_at_rate_line_51",
                    "ca-pe/pe428_donations_credit_at_rate_line_52",
                ]
            },
            "produces": {"output": "ca-pe/pe428_donations_and_gifts_credit_line_53"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (
            "ca-pe/pe428_donations_and_gifts_credit_line_53",
            PE428_DONATIONS_AND_GIFTS_CREDIT_LINE_53,
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
