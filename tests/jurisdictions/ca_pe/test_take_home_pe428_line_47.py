"""PE428 (2025) line 47, line 45 plus line 46, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 47 and line 58769: Line 45 plus line 46 = ^". A
salary-only filer has no medical expenses (line 45 is 0.00) and leaves line 46 blank (read as 0),
so line 47 is 0.00. With medical expenses of 5,000.00 on the return and an allowable amount for
other dependants of 250.25 at $20,000, line 45 is 4,404.95 and line 47 is 4,655.20 (hand figures,
not a CRA example). The form prints no label for line 47, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 40 to 47
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
from tax_engine.domain.trace import SumLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_MEDICAL_EXPENSES_ALLOWABLE_LINE_47
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
PART_NAME = "pe428_line_47.yaml"
OUTPUT = "ca-pe/pe428_medical_expenses_allowable_line_47"
PARTS = (
    *FEDERAL_PARTS,
    *NET_INCOME_PARTS,
    "pe428_line_40.yaml",
    "pe428_line_41.yaml",
    "pe428_line_43.yaml",
    "pe428_line_44.yaml",
    "pe428_line_45.yaml",
    "pe428_line_46_input.yaml",
    PART_NAME,
)
CASES = [
    ("20000", {}, {"ca-pe/pe428_medical_expenses_allowable_line_47": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_medical_expenses_allowable_line_47": "0.00"}),
    ("70000", {}, {"ca-pe/pe428_medical_expenses_allowable_line_47": "0.00"}),
    (
        "20000",
        {
            "ca/medical_expenses": "5000",
            "ca-pe/pe428_allowable_medical_expenses_for_other_dependants_line_46": "250.25",
        },
        {
            "ca-pe/pe428_medical_expenses_over_limit_line_45": "4404.95",
            "ca-pe/pe428_medical_expenses_allowable_line_47": "4655.20",
        },
    ),
    (
        "20000",
        {"ca-pe/pe428_allowable_medical_expenses_for_other_dependants_line_46": "250.25"},
        {"ca-pe/pe428_medical_expenses_allowable_line_47": "250.25"},
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


def test_the_trace_is_one_sum_with_the_blank_parts_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SumLine)
        and t.output is kinds.kind("ca-pe/pe428_medical_expenses_allowable_line_47")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_medical_expenses_over_limit_line_45", D("0.00")),
        ("ca-pe/pe428_allowable_medical_expenses_for_other_dependants_line_46", D("0")),
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
            "name": "core/sum",
            "reference": "47",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_medical_expenses_over_limit_line_45",
                    "ca-pe/pe428_allowable_medical_expenses_for_other_dependants_line_46",
                ]
            },
            "blank": {"ca-pe/pe428_allowable_medical_expenses_for_other_dependants_line_46": "0"},
            "produces": {"output": "ca-pe/pe428_medical_expenses_allowable_line_47"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (
            "ca-pe/pe428_medical_expenses_allowable_line_47",
            PE428_MEDICAL_EXPENSES_ALLOWABLE_LINE_47,
        ),
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
