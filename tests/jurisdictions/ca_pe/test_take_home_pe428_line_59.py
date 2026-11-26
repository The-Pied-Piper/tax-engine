"""PE428 (2025) line 59, line 57 minus line 58, not below 0, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 59: Line 57 minus line 58 (if
negative, enter "0") =". Line 58 is a copy of line 54 and has no step. Hand figures: 1,884.33 less
1,500.50 is 383.83 at $20,000; 2,824.83 less 1,563.11 is 1,261.72 at $30,000; 8,162.75 less
1,806.83 is 6,355.92 at $70,000. With a line 56 of 100.10 at $20,000 the line is 483.93. With
donations of 1,000 line 54 is 1,671.50 and the line is 212.83; with donations of 5,000 the credits
pass the tax and the line is 0.00. The form prints no label for line 59, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 59
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
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_LINE_59
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_59,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_59.yaml"
OUTPUT = "ca-pe/pe428_tax_line_59"
PARTS = CHAIN_59
CASES = [
    ("20000", {}, {"ca-pe/pe428_tax_line_59": "383.83"}),
    ("30000", {}, {"ca-pe/pe428_tax_line_59": "1261.72"}),
    ("70000", {}, {"ca-pe/pe428_tax_line_59": "6355.92"}),
    (
        "20000",
        {"ca-pe/pe428_tax_on_split_income_line_56": "100.10"},
        {"ca-pe/pe428_tax_line_59": "483.93"},
    ),
    ("20000", {"ca/donations_and_gifts_line_12": "1000"}, {"ca-pe/pe428_tax_line_59": "212.83"}),
    ("20000", {"ca/donations_and_gifts_line_12": "5000"}, {"ca-pe/pe428_tax_line_59": "0.00"}),
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


def test_the_trace_is_one_floored_subtraction_of_line_58_from_line_57(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.minuend.identifier == "ca-pe/pe428_tax_line_57"
    assert line.minuend_amount == D("1884.33")
    assert line.subtrahend.identifier == "ca-pe/pe428_non_refundable_credits_line_54"
    assert line.subtrahend_amount == D("1500.50")
    assert line.result == D("383.83")


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
            "reference": "59",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_tax_line_57",
                "less": "ca-pe/pe428_non_refundable_credits_line_54",
            },
            "produces": {"output": "ca-pe/pe428_tax_line_59"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_tax_line_59")

    assert kind is PE428_TAX_LINE_59
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
