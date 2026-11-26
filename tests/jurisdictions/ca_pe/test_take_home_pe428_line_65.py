"""PE428 (2025) line 65, line 63 plus line 64, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 65: Line 63 plus line 64 =". Line
64 is an optional input left blank, read as 0, so line 65 equals line 63: 383.83 at $20,000,
1,261.72 at $30,000 and 6,355.92 at $70,000. With a line 64 of 12.34 at $20,000 the sum is 396.17.
The form prints no label for line 65, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 65
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_WITH_MINIMUM_TAX_LINE_65
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_65,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_65.yaml"
OUTPUT = "ca-pe/pe428_tax_with_minimum_tax_line_65"
PARTS = CHAIN_65
EXTRA_EXPORTS = ()
CASES = [
    ("20000", {}, {"ca-pe/pe428_tax_with_minimum_tax_line_65": "383.83"}),
    ("30000", {}, {"ca-pe/pe428_tax_with_minimum_tax_line_65": "1261.72"}),
    ("70000", {}, {"ca-pe/pe428_tax_with_minimum_tax_line_65": "6355.92"}),
    (
        "20000",
        {"ca-pe/pe428_additional_tax_minimum_tax_line_64": "12.34"},
        {"ca-pe/pe428_tax_with_minimum_tax_line_65": "396.17"},
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
        ("ca-pe/pe428_tax_line_63", D("383.83")),
        ("ca-pe/pe428_additional_tax_minimum_tax_line_64", D("0")),
    ]
    assert line.total == D("383.83")


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
            "reference": "65",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_tax_line_63",
                    "ca-pe/pe428_additional_tax_minimum_tax_line_64",
                ]
            },
            "blank": {"ca-pe/pe428_additional_tax_minimum_tax_line_64": "0"},
            "produces": {"output": "ca-pe/pe428_tax_with_minimum_tax_line_65"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_tax_with_minimum_tax_line_65")

    assert kind is PE428_TAX_WITH_MINIMUM_TAX_LINE_65
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
