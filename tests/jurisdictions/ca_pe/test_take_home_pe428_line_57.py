"""PE428 (2025) line 57, line 55 plus line 56, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 57: Line 55 plus line 56 =". Line
55 is a copy of line 8 and has no step; line 56 is an optional input left blank, read as 0, so
line 57 equals line 8 (1,884.33 at $20,000, 2,824.83 at $30,000, 8,162.75 at $70,000). With a line
56 of 100.10 at $20,000 the sum is 1,984.43. The form prints no label for line 57, so the step has
no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 57
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_LINE_57
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_57,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_57.yaml"
OUTPUT = "ca-pe/pe428_tax_line_57"
PARTS = CHAIN_57
EXTRA_EXPORTS = ("ca-pe/pe428_non_refundable_credits_line_54",)
CASES = [
    ("20000", {}, {"ca-pe/pe428_tax_line_57": "1884.33"}),
    ("30000", {}, {"ca-pe/pe428_tax_line_57": "2824.83"}),
    ("70000", {}, {"ca-pe/pe428_tax_line_57": "8162.75"}),
    (
        "20000",
        {"ca-pe/pe428_tax_on_split_income_line_56": "100.10"},
        {"ca-pe/pe428_tax_line_57": "1984.43"},
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


def test_the_trace_is_one_sum_with_the_blank_part_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(OUTPUT)]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_tax_on_taxable_income_line_8", D("1884.33")),
        ("ca-pe/pe428_tax_on_split_income_line_56", D("0")),
    ]
    assert line.total == D("1884.33")


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
            "reference": "57",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_tax_on_taxable_income_line_8",
                    "ca-pe/pe428_tax_on_split_income_line_56",
                ]
            },
            "blank": {"ca-pe/pe428_tax_on_split_income_line_56": "0"},
            "produces": {"output": "ca-pe/pe428_tax_line_57"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_tax_line_57")

    assert kind is PE428_TAX_LINE_57
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
