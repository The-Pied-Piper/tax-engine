"""PE428 (2025) line 70 column 1, line 68 plus line 69, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 70: Line 68 plus line 69, Column 1: You =

One core/sum. A UCCB repayment is deducted in the net income (line 21300) and added back here, so
a repayment of 200.00 leaves line 70 at 19,835.00 at $20,000, the same as with none.

The test builds the engine over the real federal parts and the real parts of lines 1 to 70 through
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
from tax_engine.domain.trace import SumLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_FAMILY_INCOME_LINE_70
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_70,
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
PART_NAME = "pe428_line_70.yaml"
OUTPUT = "ca-pe/pe428_family_income_line_70"
PARTS = CHAIN_70
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_family_income_line_70": "19835.00"}),
    ("30000", {}, {"ca-pe/pe428_family_income_line_70": "29735.00"}),
    ("70000", {}, {"ca-pe/pe428_family_income_line_70": "69335.00"}),
    (
        "20000",
        {"ca/uccb_repayment": "200"},
        {
            "ca-pe/pe428_net_income_line_68": "19635.00",
            "ca-pe/pe428_family_income_line_70": "19835.00",
        },
    ),
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


def test_the_trace_is_one_sum_of_line_68_and_line_69_in_order(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(OUTPUT)]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_net_income_line_68", D("19835.00")),
        ("ca-pe/pe428_uccb_repayment_line_69", D("0.00")),
    ]
    assert line.total == D("19835.00")


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
            "reference": "70 (column 1)",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": ["ca-pe/pe428_net_income_line_68", "ca-pe/pe428_uccb_repayment_line_69"]
            },
            "produces": {"output": "ca-pe/pe428_family_income_line_70"},
        }
    ]


def test_the_kind_is_a_registered_signed_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_FAMILY_INCOME_LINE_70
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
