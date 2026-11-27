"""PE428 (2025) line 84, line 82 minus line 83, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 82: Amount from line 73 of the previous page; Line 83: Base amount 22,650.00; Line 84: Line
82 minus line 83 (if negative, enter "0") =

One core/subtract_not_below_zero. Lines 73 and 82 are copies of line 72 and have no step. Hand
figures: 19,835.00 less 22,650.00 is below 0, so 0.00 at $20,000; 29,735.00 less 22,650.00 gives
7,085.00; 69,335.00 less 22,650.00 gives 46,685.00. A net income of 25,000.00 (salary 25,217.17)
gives 2,350.00, inside the fade band.

The test builds the engine over the real federal parts and the real parts of lines 1 to 84 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_INCOME_OVER_BASE_AMOUNT_LINE_84
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_84,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_84.yaml"
OUTPUT = "ca-pe/pe428_income_over_base_amount_line_84"
PARTS = CHAIN_84
EXPORTS = (
    "ca-pe/pe428_tax_line_67",
    "ca-pe/pe428_net_income_line_68",
    "ca-pe/pe428_uccb_repayment_line_69",
    "ca-pe/pe428_family_income_line_70",
    "ca-pe/pe428_uccb_income_line_71",
    "ca-pe/pe428_adjusted_family_income_line_72",
    "ca-pe/low_income_reduction_basic",
    "ca-pe/pe428_low_income_reductions_total_line_81",
    "ca-pe/low_income_reduction_base_amount",
    "ca-pe/pe428_income_over_base_amount_line_84",
)
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_income_over_base_amount_line_84": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_income_over_base_amount_line_84": "7085.00"}),
    ("70000", {}, {"ca-pe/pe428_income_over_base_amount_line_84": "46685.00"}),
    (
        "25217.17",
        {},
        {
            "ca-pe/pe428_adjusted_family_income_line_72": "25000.00",
            "ca-pe/pe428_income_over_base_amount_line_84": "2350.00",
        },
    ),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(*EXPORTS), *PARTS)
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


def test_the_trace_is_one_floored_subtraction_of_line_83_from_line_72(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "30000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.minuend.identifier == "ca-pe/pe428_adjusted_family_income_line_72"
    assert line.minuend_amount == D("29735.00")
    assert line.subtrahend.identifier == "ca-pe/low_income_reduction_base_amount"
    assert line.subtrahend_amount == D("22650.00")
    assert line.result == D("7085.00")


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
            "reference": "84",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_adjusted_family_income_line_72",
                "less": "ca-pe/low_income_reduction_base_amount",
            },
            "produces": {"output": "ca-pe/pe428_income_over_base_amount_line_84"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_INCOME_OVER_BASE_AMOUNT_LINE_84
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
