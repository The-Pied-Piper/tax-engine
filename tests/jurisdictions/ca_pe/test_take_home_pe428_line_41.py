"""PE428 (2025) line 41, the net income from line 23600 of the return, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 41: Amount from line 23600 of your return ^". It
is the T1 net income, the salary less the enhanced CPP deduction (hand figures, not a CRA
example): 19,835.00 at $20,000, 29,735.00 at $30,000 and 69,335.00 at $70,000. The form prints no
label for line 41, so the step has no title.

The test builds the engine over the real federal parts, including the T1 taxable income form, and
the real part of line 41 through the shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import PE428_NET_INCOME_LINE_41
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    FEDERAL_PARTS,
    HEADER,
    NET_INCOME_PARTS,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_41.yaml"
OUTPUT = "ca-pe/pe428_net_income_line_41"
PARTS = (*FEDERAL_PARTS, *NET_INCOME_PARTS, PART_NAME)
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_net_income_line_41": "19835.00"}),
    ("30000", {}, {"ca-pe/pe428_net_income_line_41": "29735.00"}),
    ("70000", {}, {"ca-pe/pe428_net_income_line_41": "69335.00"}),
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
            "name": "core/record_total",
            "reference": "41",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income"},
            "produces": {"output": "ca-pe/pe428_net_income_line_41"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_net_income_line_41", PE428_NET_INCOME_LINE_41),
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
