"""PE428 (2025) line 88, line 74 minus line 87, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 74: Amount from line 67 of the previous page; Line 88: Line 74 minus line 87 (if negative,
enter "0") =

One core/subtract_not_below_zero. Line 74 is a copy of line 67 and has no step. Figures (hand-
computed, ticket #2007): 383.83 less 350.00 is 33.83 at $20,000; the reduction is 0 at $30,000 so
line 88 is line 67, 1,261.72; at $70,000 it is 6,355.92.

The test builds the engine over the real federal parts and the real parts of lines 1 to 88 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_LINE_88
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_88,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_88.yaml"
OUTPUT = "ca-pe/pe428_tax_line_88"
PARTS = CHAIN_88
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_tax_line_88": "33.83"}),
    ("30000", {}, {"ca-pe/pe428_tax_line_88": "1261.72"}),
    ("70000", {}, {"ca-pe/pe428_tax_line_88": "6355.92"}),
    (
        "20000",
        {},
        {
            "ca-pe/pe428_tax_line_67": "383.83",
            "ca-pe/pe428_low_income_tax_reduction_line_87": "350.00",
        },
    ),
]
EXPORTS = sorted({OUTPUT, *(name for _, _, expected in CASES for name in expected)})


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
            "reference": "88",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_tax_line_67",
                "less": "ca-pe/pe428_low_income_tax_reduction_line_87",
            },
            "produces": {"output": "ca-pe/pe428_tax_line_88"},
        }
    ]


def test_the_kind_is_a_registered_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_TAX_LINE_88
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
