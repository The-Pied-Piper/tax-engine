"""PE428 (2025) line 39, add lines 34 to 38, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 39: Add lines 34 to 38. = ^". Line 35 is the
student loan interest read from the return (0.00 for a salary-only filer) and lines 36 to 38 are
optional lines left blank, read as 0, so line 39 equals line 34 (15,794.75 at $20,000, 16,453.75
at $30,000, 19,019.23 at $70,000). With a student loan interest of 100.10 on the return and lines
36 to 38 given as 200.20, 300.30 and 400.40 at $20,000 the sum is 15,794.75 + 1,001.00 =
16,795.75. The form prints no label for line 39, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 9 to 39 through
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_SUBTOTAL_LINE_39
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_39,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_39.yaml"
OUTPUT = "ca-pe/pe428_credits_subtotal_line_39"
PARTS = CHAIN_39
CASES = [
    ("20000", {}, {"ca-pe/pe428_credits_subtotal_line_39": "15794.75"}),
    ("30000", {}, {"ca-pe/pe428_credits_subtotal_line_39": "16453.75"}),
    ("70000", {}, {"ca-pe/pe428_credits_subtotal_line_39": "19019.23"}),
    (
        "20000",
        {
            "ca/student_loan_interest": "100.10",
            "ca-pe/pe428_tuition_and_education_amounts_line_36": "200.20",
            "ca-pe/pe428_tuition_transferred_from_child_or_grandchild_line_37": "300.30",
            "ca-pe/pe428_amounts_transferred_from_spouse_or_partner_line_38": "400.40",
        },
        {
            "ca-pe/pe428_student_loan_interest_line_35": "100.10",
            "ca-pe/pe428_credits_subtotal_line_39": "16795.75",
        },
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
        if isinstance(t, SumLine) and t.output is kinds.kind("ca-pe/pe428_credits_subtotal_line_39")
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/pe428_credits_subtotal_line_34", D("15794.75")),
        ("ca-pe/pe428_student_loan_interest_line_35", D("0.00")),
        ("ca-pe/pe428_tuition_and_education_amounts_line_36", D("0")),
        ("ca-pe/pe428_tuition_transferred_from_child_or_grandchild_line_37", D("0")),
        ("ca-pe/pe428_amounts_transferred_from_spouse_or_partner_line_38", D("0")),
    ]
    assert line.total == D("15794.75")


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
            "reference": "39",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/pe428_credits_subtotal_line_34",
                    "ca-pe/pe428_student_loan_interest_line_35",
                    "ca-pe/pe428_tuition_and_education_amounts_line_36",
                    "ca-pe/pe428_tuition_transferred_from_child_or_grandchild_line_37",
                    "ca-pe/pe428_amounts_transferred_from_spouse_or_partner_line_38",
                ]
            },
            "blank": {
                "ca-pe/pe428_tuition_and_education_amounts_line_36": "0",
                "ca-pe/pe428_tuition_transferred_from_child_or_grandchild_line_37": "0",
                "ca-pe/pe428_amounts_transferred_from_spouse_or_partner_line_38": "0",
            },
            "produces": {"output": "ca-pe/pe428_credits_subtotal_line_39"},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        ("ca-pe/pe428_credits_subtotal_line_39", PE428_CREDITS_SUBTOTAL_LINE_39),
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
