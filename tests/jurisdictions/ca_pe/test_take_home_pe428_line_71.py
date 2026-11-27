"""PE428 (2025) line 71 column 1, UCCB income, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 71: Amount from line 11700 of the return, Column 1: You

A T1 line, so the part has no input: one core/record_total over the T1 export. A salary-only
caller has no UCCB income, so it is 0.00. With UCCB income of 300.00 typed on the T1 the line is
300.00.

The test builds the engine over the real federal parts and the real parts of lines 1 to 71 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_UCCB_INCOME_LINE_71
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_71,
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
PART_NAME = "pe428_line_71.yaml"
OUTPUT = "ca-pe/pe428_uccb_income_line_71"
PARTS = CHAIN_71
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_uccb_income_line_71": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_uccb_income_line_71": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_uccb_income_line_71": "0.00"}),
    ("20000", {"ca/uccb_income": "300"}, {"ca-pe/pe428_uccb_income_line_71": "300.00"}),
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


def test_the_trace_is_one_record_total_of_the_t1_uccb_income(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.total == D("0.00")


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
            "title": "Amount from line 11700 of the return",
            "reference": "71 (column 1)",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.uccb_income_line_11700"},
            "produces": {"output": "ca-pe/pe428_uccb_income_line_71"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_UCCB_INCOME_LINE_71
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
