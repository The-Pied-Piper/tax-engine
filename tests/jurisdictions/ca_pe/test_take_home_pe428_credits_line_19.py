"""PE428 (2025) line 19, add lines 9, 10, 13 and 16 to 18, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 19: Add lines 9, 10, 13, and 16 to 18. = ^". Line
9 is the basic personal amount (14,650.00). Lines 10, 13, 16, 17 and 18 are optional inputs a
salary-only filer leaves blank, so the sum reads each blank as 0 and line 19 is 14,650.00 at every
salary. The form prints no label for line 19, so the step has no title.

The test builds the engine over the real parts of line 9, of the five inputs and of line 19 (and the
T1 employment income form that owns the salary), through the shared `take_home_service` fixture,
under a test-local header and form declaration. Figures hand-computed: 14,650.00 alone; with the
five optional lines given as 1,000.10, 2,000.20, 3,000.30, 4,000.40 and 5,000.50 the sum is
14,650.00 + 15,001.50 = 29,651.50.
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_SUBTOTAL_LINE_19
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import HEADER, SALARY_PARTS, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-pe/pe428_credits_subtotal_line_19"
PART_NAME = "pe428_credits_line_19.yaml"

LINES = [
    "ca-pe/basic_personal_amount",
    "ca-pe/pe428_age_amount_line_10",
    "ca-pe/pe428_spouse_or_common_law_partner_amount_line_13",
    "ca-pe/pe428_eligible_dependant_amount_line_16",
    "ca-pe/pe428_infirm_dependants_amount_line_17",
    "ca-pe/pe428_young_children_amount_line_18",
]
OPTIONAL_LINES = LINES[1:]
PARTS = (
    *SALARY_PARTS,
    "pe428_credits_line_9.yaml",
    "pe428_credits_line_10_input.yaml",
    "pe428_credits_line_13_input.yaml",
    "pe428_credits_line_16_input.yaml",
    "pe428_credits_line_17_input.yaml",
    "pe428_credits_line_18_input.yaml",
    PART_NAME,
)


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(IDENTIFIER), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize("salary", ["20000", "30000", "70000", "200000"])
def test_line_19_is_line_9_alone_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert value(_sheet(take_home_service, salary), IDENTIFIER) == D("14650.00")


@pytest.mark.parametrize("line", OPTIONAL_LINES)
def test_line_19_adds_each_optional_line_when_it_is_given(
    take_home_service: TakeHomeService, line: str
) -> None:
    sheet = _sheet(take_home_service, "20000", {line: "1234.56"})

    assert value(sheet, IDENTIFIER) == D("15884.56")


def test_line_19_adds_every_line_together(take_home_service: TakeHomeService) -> None:
    given = dict(
        zip(OPTIONAL_LINES, ["1000.10", "2000.20", "3000.30", "4000.40", "5000.50"], strict=True)
    )

    assert value(_sheet(take_home_service, "20000", given), IDENTIFIER) == D("29651.50")


def test_the_trace_is_one_sum_of_the_six_lines_in_form_order_blanks_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000", {OPTIONAL_LINES[1]: "100.00"})
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        (LINES[0], D("14650.00")),
        (LINES[1], D("0")),
        (LINES[2], D("100.00")),
        (LINES[3], D("0")),
        (LINES[4], D("0")),
        (LINES[5], D("0")),
    ]
    assert line.total == D("14750.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428_credits"}
    return part


def test_the_part_is_one_untitled_sum_step_over_lines_9_10_13_and_16_to_18() -> None:
    (step,) = _part()["capabilities"]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "19",
        "unit": "ca/cad",
        "params": {"rounding": "ca-pe/cent_rounding"},
        "consumes": {"parts": LINES},
        "blank": dict.fromkeys(OPTIONAL_LINES, "0"),
        "produces": {"output": IDENTIFIER},
    }


def test_line_9_has_no_blank_mapping() -> None:
    (step,) = _part()["capabilities"]

    assert LINES[0] not in step["blank"]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_CREDITS_SUBTOTAL_LINE_19
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
