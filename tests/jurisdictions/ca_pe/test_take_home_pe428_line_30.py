"""PE428 (2025) line 30, add lines 26 to 29, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 30: Add lines 26 to 29. = ^". Line 26 is a copy
of line 25 and has no step of its own; lines 27 to 29 are optional lines a salary-only filer
leaves blank, read as 0, so line 30 equals line 25 (15,794.75 at $20,000, 16,453.75 at $30,000,
19,019.23 at $70,000). With a pension income amount of 1,000.00, a children's wellness tax credit
of 100.10 and a caregiver amount of 200.20 at $20,000 the sum is 15,794.75 + 1,300.30 = 17,095.05.
The form prints no label for line 30, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 9 to 30 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_SUBTOTAL_LINE_30
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_30,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_30.yaml"
OUTPUT = "ca-pe/pe428_credits_subtotal_line_30"
PARTS = CHAIN_30
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_subtotal_line_30": "15794.75"}),
    ("30000", {}, {"ca-pe/pe428_credits_subtotal_line_30": "16453.75"}),
    ("70000", {}, {"ca-pe/pe428_credits_subtotal_line_30": "19019.23"}),
    (
        "20000",
        {
            "ca-pe/pe428_pension_income_amount_claimed_line_27": "1000",
            "ca-pe/pe428_childrens_wellness_tax_credit_line_28": "100.10",
            "ca-pe/pe428_caregiver_amount_line_29": "200.20",
        },
        {"ca-pe/pe428_credits_subtotal_line_30": "17095.05"},
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
        if isinstance(t, SumLine) and t.output is kinds.kind("ca-pe/pe428_credits_subtotal_line_30")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_credits_subtotal_line_25", D("15794.75")),
        ("ca-pe/pe428_pension_income_amount_line_27", D("0")),
        ("ca-pe/pe428_childrens_wellness_tax_credit_line_28", D("0")),
        ("ca-pe/pe428_caregiver_amount_line_29", D("0")),
    ]
    assert line.total == D("15794.75")


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
            "reference": "30",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_credits_subtotal_line_25",
                    "ca-pe/pe428_pension_income_amount_line_27",
                    "ca-pe/pe428_childrens_wellness_tax_credit_line_28",
                    "ca-pe/pe428_caregiver_amount_line_29",
                ]
            },
            "blank": {
                "ca-pe/pe428_pension_income_amount_line_27": "0",
                "ca-pe/pe428_childrens_wellness_tax_credit_line_28": "0",
                "ca-pe/pe428_caregiver_amount_line_29": "0",
            },
            "produces": {"output": "ca-pe/pe428_credits_subtotal_line_30"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_credits_subtotal_line_30", PE428_CREDITS_SUBTOTAL_LINE_30),
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
