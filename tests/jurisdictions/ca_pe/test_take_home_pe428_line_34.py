"""PE428 (2025) line 34, add lines 30 to 33, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 34: Add lines 30 to 33. = ^". Lines 31 to 33 are
optional lines a salary-only filer leaves blank, read as 0, so line 34 equals line 30 (15,794.75
at $20,000, 16,453.75 at $30,000, 19,019.23 at $70,000). With a pension income amount of 1,000.00,
a disability amount for self of 1,000.01, a disability amount transferred from a dependant of
2,000.02 and a teacher school supply amount of 500.00 at $20,000, line 30 is 16,794.75 and line 34
is 20,294.78. The form prints no label for line 34, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 9 to 34 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_SUBTOTAL_LINE_34
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_34,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_34.yaml"
OUTPUT = "ca-pe/pe428_credits_subtotal_line_34"
PARTS = CHAIN_34
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_subtotal_line_34": "15794.75"}),
    ("30000", {}, {"ca-pe/pe428_credits_subtotal_line_34": "16453.75"}),
    ("70000", {}, {"ca-pe/pe428_credits_subtotal_line_34": "19019.23"}),
    (
        "20000",
        {
            "ca-pe/pe428_pension_income_amount_claimed_line_27": "1000",
            "ca-pe/pe428_disability_amount_self_line_31": "1000.01",
            "ca-pe/pe428_disability_amount_transferred_from_a_dependant_line_32": "2000.02",
            "ca-pe/pe428_teacher_school_supply_amount_claimed_line_33": "500",
        },
        {
            "ca-pe/pe428_credits_subtotal_line_30": "16794.75",
            "ca-pe/pe428_credits_subtotal_line_34": "20294.78",
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
        if isinstance(t, SumLine) and t.output is kinds.kind("ca-pe/pe428_credits_subtotal_line_34")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_credits_subtotal_line_30", D("15794.75")),
        ("ca-pe/pe428_disability_amount_self_line_31", D("0")),
        ("ca-pe/pe428_disability_amount_transferred_from_a_dependant_line_32", D("0")),
        ("ca-pe/pe428_teacher_school_supply_amount_line_33", D("0")),
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
            "reference": "34",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_credits_subtotal_line_30",
                    "ca-pe/pe428_disability_amount_self_line_31",
                    "ca-pe/pe428_disability_amount_transferred_from_a_dependant_line_32",
                    "ca-pe/pe428_teacher_school_supply_amount_line_33",
                ]
            },
            "blank": {
                "ca-pe/pe428_disability_amount_self_line_31": "0",
                "ca-pe/pe428_disability_amount_transferred_from_a_dependant_line_32": "0",
                "ca-pe/pe428_teacher_school_supply_amount_line_33": "0",
            },
            "produces": {"output": "ca-pe/pe428_credits_subtotal_line_34"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_credits_subtotal_line_34", PE428_CREDITS_SUBTOTAL_LINE_34),
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
