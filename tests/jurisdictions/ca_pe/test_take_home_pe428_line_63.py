"""PE428 (2025) line 63, line 59 minus line 62, not below 0, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 63: Line 59 minus line 62 (if
negative, enter "0") =". Line 62 is 0 for a salary-only filer, so line 63 equals line 59: 383.83
at $20,000, 1,261.72 at $30,000 and 6,355.92 at $70,000. With a line 60 of 50.25 at $20,000 the
line is 383.83 less 50.25, 333.58; with a line 60 of 500.00 the credit passes the tax and the line
is 0.00. The form prints no label for line 63, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 63
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
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_LINE_63
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_63,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_63.yaml"
OUTPUT = "ca-pe/pe428_tax_line_63"
PARTS = CHAIN_63
CASES = [
    ("20000", {}, {"ca-pe/pe428_tax_line_63": "383.83"}),
    ("30000", {}, {"ca-pe/pe428_tax_line_63": "1261.72"}),
    ("70000", {}, {"ca-pe/pe428_tax_line_63": "6355.92"}),
    (
        "20000",
        {"ca-pe/pe428_dividend_tax_credit_line_60": "50.25"},
        {"ca-pe/pe428_tax_line_63": "333.58"},
    ),
    (
        "20000",
        {"ca-pe/pe428_dividend_tax_credit_line_60": "500"},
        {"ca-pe/pe428_tax_line_63": "0.00"},
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


def test_the_trace_is_one_floored_subtraction_of_line_62_from_line_59(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.minuend.identifier == "ca-pe/pe428_tax_line_59"
    assert line.minuend_amount == D("383.83")
    assert line.subtrahend.identifier == "ca-pe/pe428_credits_total_line_62"
    assert line.subtrahend_amount == D("0")
    assert line.result == D("383.83")


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
            "reference": "63",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_tax_line_59",
                "less": "ca-pe/pe428_credits_total_line_62",
            },
            "produces": {"output": "ca-pe/pe428_tax_line_63"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_tax_line_63")

    assert kind is PE428_TAX_LINE_63
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
