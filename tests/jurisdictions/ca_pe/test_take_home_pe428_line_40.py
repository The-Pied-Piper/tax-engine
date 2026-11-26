"""PE428 (2025) line 40, the medical expenses from line 33099 of the return, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 40 and line 58689: Amount from line 33099 of
your return ^". A copy of T1 line 33099, which the T1 owns and exports, so the one step is a
core/record_total over that export. A salary-only filer has none (0.00); a typed T1 medical
expenses figure of 5,000.55 is the line's figure.

The test builds the engine over the real federal parts and the real part of line 40 through the
shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import PE428_MEDICAL_EXPENSES_LINE_40
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    FEDERAL_PARTS,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_40.yaml"
OUTPUT = "ca-pe/pe428_medical_expenses_line_40"
PARTS = (*FEDERAL_PARTS, PART_NAME)
CASES = [
    ("20000", {}, {"ca-pe/pe428_medical_expenses_line_40": "0.00"}),
    (
        "20000",
        {"ca/medical_expenses": "5000.55"},
        {"ca-pe/pe428_medical_expenses_line_40": "5000.55"},
    ),
    ("70000", {"ca/medical_expenses": "0.01"}, {"ca-pe/pe428_medical_expenses_line_40": "0.01"}),
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
            "title": "Amount from line 33099 of your return",
            "reference": "40",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_lines_copied_by_provinces.medical_expenses_line_33099"},
            "produces": {"output": "ca-pe/pe428_medical_expenses_line_40"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_medical_expenses_line_40", PE428_MEDICAL_EXPENSES_LINE_40),
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
