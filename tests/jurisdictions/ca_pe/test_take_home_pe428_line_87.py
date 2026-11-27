"""PE428 (2025) line 87, the low-income tax reduction, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 87: Line 81 minus line 86 (if negative, enter "0") Prince Edward Island low-income tax
reduction =

One core/subtract_not_below_zero. The printed form has no eligibility test: the arithmetic alone
gives the reduction, 350.00 up to a net income of 22,650 fading to 0 at 29,650. Line 66 is blank
for a single filer, so the instruction to enter 0 on line 87 does not apply and the line is
calculated: 350.00 at $20,000, 0.00 at $30,000 and $70,000, and 232.50 at a net income of
25,000.00 (350.00 less 117.50).

The test builds the engine over the real federal parts and the real parts of lines 1 to 87 through
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
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_LOW_INCOME_TAX_REDUCTION_LINE_87
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_87,
    HEADER,
    compute,
    exports_of,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_87.yaml"
OUTPUT = "ca-pe/pe428_low_income_tax_reduction_line_87"
PARTS = CHAIN_87
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "350.00"}),
    ("30000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "0.00"}),
    ("25217.17", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "232.50"}),
    ("22650", {}, {"ca-pe/pe428_low_income_tax_reduction_line_87": "350.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(*exports_of(PARTS)), *PARTS)
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


def test_the_trace_is_one_floored_subtraction_of_line_86_from_line_81(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.minuend.identifier == "ca-pe/pe428_low_income_reductions_total_line_81"
    assert line.minuend_amount == D("350.00")
    assert line.subtrahend.identifier == "ca-pe/pe428_reduction_phase_out_line_86"
    assert line.subtrahend_amount == D("0.00")
    assert line.result == D("350.00")


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
            "title": "Prince Edward Island low-income tax reduction",
            "reference": "87",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_low_income_reductions_total_line_81",
                "less": "ca-pe/pe428_reduction_phase_out_line_86",
            },
            "produces": {"output": "ca-pe/pe428_low_income_tax_reduction_line_87"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_LOW_INCOME_TAX_REDUCTION_LINE_87
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
