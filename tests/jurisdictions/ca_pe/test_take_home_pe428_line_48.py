"""PE428 (2025) line 48, line 39 plus line 47, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 48 and line 58800: Line 39 plus line 47 = ^". A
salary-only filer has line 47 of 0.00, so line 48 equals line 39 (15,794.75 at $20,000, 16,453.75
at $30,000, 19,019.23 at $70,000). With tuition and education amounts of 100.00 and medical
expenses of 5,000.00 on the return at $20,000, line 39 is 15,894.75, line 47 is 4,404.95 and line
48 is 20,299.70 (hand figures, not a CRA example). The form prints no label for line 48, so the
step has no title.

The test builds the engine over the real federal parts and the real parts of lines 9 to 48 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_TOTAL_LINE_48
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_48,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_48.yaml"
OUTPUT = "ca-pe/pe428_credits_total_line_48"
PARTS = CHAIN_48
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_total_line_48": "15794.75"}),
    ("30000", {}, {"ca-pe/pe428_credits_total_line_48": "16453.75"}),
    ("70000", {}, {"ca-pe/pe428_credits_total_line_48": "19019.23"}),
    (
        "20000",
        {"ca/medical_expenses": "5000", "ca-pe/pe428_tuition_and_education_amounts_line_36": "100"},
        {
            "ca-pe/pe428_credits_subtotal_line_39": "15894.75",
            "ca-pe/pe428_medical_expenses_allowable_line_47": "4404.95",
            "ca-pe/pe428_credits_total_line_48": "20299.70",
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
        if isinstance(t, SumLine) and t.output is kinds.kind("ca-pe/pe428_credits_total_line_48")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_credits_subtotal_line_39", D("15794.75")),
        ("ca-pe/pe428_medical_expenses_allowable_line_47", D("0.00")),
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
            "reference": "48",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_credits_subtotal_line_39",
                    "ca-pe/pe428_medical_expenses_allowable_line_47",
                ]
            },
            "produces": {"output": "ca-pe/pe428_credits_total_line_48"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_credits_total_line_48", PE428_CREDITS_TOTAL_LINE_48),
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
