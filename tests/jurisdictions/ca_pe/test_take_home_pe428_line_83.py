"""PE428 (2025) line 83, the base amount, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 83: Base amount 22,650.00

The printed 22,650.00 is the `ca-pe/low_income_reduction_base_amount` dataset, taken as printed
through core/credit_amount, the same at every salary.

The test builds the engine over the real federal parts and the real parts of lines 1 to 83 through
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
from tax_engine.jurisdictions.ca_pe.catalog import LOW_INCOME_REDUCTION_BASE_AMOUNT
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_83,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_83.yaml"
OUTPUT = "ca-pe/low_income_reduction_base_amount"
PARTS = CHAIN_83
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/low_income_reduction_base_amount": "22650.00"}),
    ("30000", {}, {"ca-pe/low_income_reduction_base_amount": "22650.00"}),
    ("70000", {}, {"ca-pe/low_income_reduction_base_amount": "22650.00"}),
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
            "name": "core/credit_amount",
            "title": "Base amount",
            "reference": "83",
            "unit": "ca/cad",
            "params": {"amount": "ca-pe/low_income_reduction_base_amount"},
            "produces": {"output": "ca-pe/low_income_reduction_base_amount"},
        }
    ]


def test_the_kind_is_a_registered_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is LOW_INCOME_REDUCTION_BASE_AMOUNT
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
