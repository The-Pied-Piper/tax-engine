"""PE428 (2025) line 62, line 60 plus line 61, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 62: Line 60 plus line 61 =". Both
lines are optional inputs a salary-only filer leaves blank, read as 0, so line 62 is 0 at every
salary ($20,000, $30,000, $70,000). With a line 60 of 50.25 and a line 61 of 30.10 the sum is
80.35. The form prints no label for line 62, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 62
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_TOTAL_LINE_62
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_62,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_62.yaml"
OUTPUT = "ca-pe/pe428_credits_total_line_62"
PARTS = CHAIN_62
EXTRA_EXPORTS = ("ca-pe/pe428_tax_line_59",)
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_total_line_62": "0"}),
    ("70000", {}, {"ca-pe/pe428_credits_total_line_62": "0"}),
    (
        "20000",
        {"ca-pe/pe428_dividend_tax_credit_line_60": "50.25"},
        {"ca-pe/pe428_credits_total_line_62": "50.25"},
    ),
    (
        "20000",
        {"ca-pe/pe428_minimum_tax_carryover_line_61": "30.10"},
        {"ca-pe/pe428_credits_total_line_62": "30.10"},
    ),
    (
        "20000",
        {
            "ca-pe/pe428_dividend_tax_credit_line_60": "50.25",
            "ca-pe/pe428_minimum_tax_carryover_line_61": "30.10",
        },
        {"ca-pe/pe428_credits_total_line_62": "80.35"},
    ),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(OUTPUT, *EXTRA_EXPORTS), *PARTS)
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


def test_the_trace_is_one_sum_with_both_blank_parts_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(OUTPUT)]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_dividend_tax_credit_line_60", D("0")),
        ("ca-pe/pe428_minimum_tax_carryover_line_61", D("0")),
    ]
    assert line.total == D("0")


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
            "reference": "62",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_dividend_tax_credit_line_60",
                    "ca-pe/pe428_minimum_tax_carryover_line_61",
                ]
            },
            "blank": {
                "ca-pe/pe428_dividend_tax_credit_line_60": "0",
                "ca-pe/pe428_minimum_tax_carryover_line_61": "0",
            },
            "produces": {"output": "ca-pe/pe428_credits_total_line_62"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_credits_total_line_62")

    assert kind is PE428_CREDITS_TOTAL_LINE_62
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
