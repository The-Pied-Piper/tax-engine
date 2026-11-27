"""PE428 (2025) line 72 column 1, line 70 minus line 71, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 72: Line 70 minus line 71 (if negative, enter "0"), Column 1: You = and Line 73: Add the
amounts from line 72 of columns 1 and 2. Enter this amount on line 82 of the next page. Adjusted
family income

One core/subtract_not_below_zero. Line 73 adds the two columns and column 2 is not modelled, so
line 73 and line 82 are this figure: 19,835.00 at $20,000, 29,735.00 at $30,000, 69,335.00 at
$70,000. UCCB income of 300.00 is in the net income and taken out again, so line 72 stays
19,835.00.

The test builds the engine over the real federal parts and the real parts of lines 1 to 72 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_ADJUSTED_FAMILY_INCOME_LINE_72
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_72,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_72.yaml"
OUTPUT = "ca-pe/pe428_adjusted_family_income_line_72"
PARTS = CHAIN_72
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_adjusted_family_income_line_72": "19835.00"}),
    ("30000", {}, {"ca-pe/pe428_adjusted_family_income_line_72": "29735.00"}),
    ("70000", {}, {"ca-pe/pe428_adjusted_family_income_line_72": "69335.00"}),
    (
        "20000",
        {"ca/uccb_income": "300"},
        {"ca-pe/pe428_adjusted_family_income_line_72": "19835.00"},
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
            "reference": "72 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_family_income_line_70",
                "less": "ca-pe/pe428_uccb_income_line_71",
            },
            "produces": {"output": "ca-pe/pe428_adjusted_family_income_line_72"},
        }
    ]


def test_the_kind_is_a_registered_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_ADJUSTED_FAMILY_INCOME_LINE_72
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
