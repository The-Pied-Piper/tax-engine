"""PE428 (2025) line 67, line 65 minus line 66, not below 0, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 67: Line 65 minus line 66 (if
negative, enter "0") Enter this amount on line 74. =". Line 66 is an optional input left blank,
read as 0, so line 67 equals line 65: 383.83 at $20,000, 1,261.72 at $30,000 and 6,355.92 at
$70,000 (line 59 at $70,000 is 8,162.75 less 1,806.83). With a line 66 of 100.10 at $20,000 the
line is 283.73; with a line 66 of 1,000.00 it is 0.00. The form prints no label for line 67, so
the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 1 to 67
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_TAX_LINE_67
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_67,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_67.yaml"
OUTPUT = "ca-pe/pe428_tax_line_67"
PARTS = CHAIN_67
CASES = [
    ("20000", {}, {"ca-pe/pe428_tax_line_67": "383.83"}),
    ("30000", {}, {"ca-pe/pe428_tax_line_67": "1261.72"}),
    ("70000", {}, {"ca-pe/pe428_tax_line_67": "6355.92"}),
    (
        "20000",
        {"ca-pe/pe428_amount_from_spouse_or_partner_form_line_66": "100.10"},
        {"ca-pe/pe428_tax_line_67": "283.73"},
    ),
    (
        "20000",
        {"ca-pe/pe428_amount_from_spouse_or_partner_form_line_66": "1000"},
        {"ca-pe/pe428_tax_line_67": "0.00"},
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


def test_the_trace_is_one_floored_subtraction_with_the_blank_line_66_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.minuend.identifier == "ca-pe/pe428_tax_with_minimum_tax_line_65"
    assert line.minuend_amount == D("383.83")
    assert line.subtrahend.identifier == "ca-pe/pe428_amount_from_spouse_or_partner_form_line_66"
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
            "reference": "67",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "amount": "ca-pe/pe428_tax_with_minimum_tax_line_65",
                "less": "ca-pe/pe428_amount_from_spouse_or_partner_form_line_66",
            },
            "blank": {"less": "0"},
            "produces": {"output": "ca-pe/pe428_tax_line_67"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind("ca-pe/pe428_tax_line_67")

    assert kind is PE428_TAX_LINE_67
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
