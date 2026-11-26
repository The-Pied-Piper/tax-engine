"""PE428 (2025) line 50, line 48 at the 9.5% of line 49, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 49: Prince Edward Island non-refundable tax
credit rate 9.5%" and "Line 50 and line 58840: Line 48 multiplied by the percentage from line 49 =
^". Line 49 is the printed rate (a dataset figure, no step); line 50 is line 48 times 9.5%, half-
up to the cent. Hand figures, not a CRA example: 15,794.75 x 9.5% = 1,500.50125 gives 1,500.50 at
$20,000; 16,453.75 x 9.5% = 1,563.10625 gives 1,563.11 at $30,000; 19,019.23 x 9.5% = 1,806.82685
gives 1,806.83 at $70,000.

The test builds the engine over the real federal parts and the real parts of lines 9 to 50 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_AT_RATE_LINE_50
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_50,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_50.yaml"
OUTPUT = "ca-pe/pe428_credits_at_rate_line_50"
PARTS = CHAIN_50
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_at_rate_line_50": "1500.50"}),
    ("30000", {}, {"ca-pe/pe428_credits_at_rate_line_50": "1563.11"}),
    ("70000", {}, {"ca-pe/pe428_credits_at_rate_line_50": "1806.83"}),
    (
        "20000",
        {"ca-pe/pe428_tuition_and_education_amounts_line_36": "100"},
        {"ca-pe/pe428_credits_at_rate_line_50": "1510.00"},
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


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/apply_rate",
            "reference": "50",
            "unit": "ca/cad",
            "params": {"rate": "ca-pe/credit_rate"},
            "consumes": {"base": "ca-pe/pe428_credits_total_line_48"},
            "produces": {"output": "ca-pe/pe428_credits_at_rate_line_50"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_credits_at_rate_line_50", PE428_CREDITS_AT_RATE_LINE_50),
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
