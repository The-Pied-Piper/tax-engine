"""PE428 (2025) line 68 column 1, net income, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 68: Net income from line 23600 of the return (or the amount you would have entered if the
instructions on line 23600 said "if negative, show in brackets") Column 1: You

Column 1 is a copy of the T1 net income before its floor (`ca/net_income_signed`), read as a
record list through core/record_total. The result is signed. Hand figures: 20,000 gives 19,835.00;
70,000 gives 69,335.00. Column 2 (spouse) is not modelled.

The test builds the engine over the real federal parts and the real parts of lines 1 to 68 through
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
from tax_engine.domain.trace import RecordTotalLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_NET_INCOME_LINE_68
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_68,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_68.yaml"
OUTPUT = "ca-pe/pe428_net_income_line_68"
PARTS = CHAIN_68
EXPORTS = (
    "ca-pe/pe428_tax_line_67",
    "ca-pe/pe428_net_income_line_68",
)
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_net_income_line_68": "19835.00"}),
    ("30000", {}, {"ca-pe/pe428_net_income_line_68": "29735.00"}),
    ("70000", {}, {"ca-pe/pe428_net_income_line_68": "69335.00"}),
]


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


def test_the_trace_is_one_record_total_of_the_signed_t1_net_income(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output is kinds.kind(OUTPUT)
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
            "name": "core/record_total",
            "title": "Net income from line 23600 of the return",
            "reference": "68 (column 1)",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income_signed"},
            "produces": {"output": "ca-pe/pe428_net_income_line_68"},
        }
    ]


def test_the_kind_is_a_registered_signed_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_NET_INCOME_LINE_68
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
