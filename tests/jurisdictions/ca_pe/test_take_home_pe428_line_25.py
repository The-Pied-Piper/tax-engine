"""PE428 (2025) line 25, line 19 plus line 24, and line 26, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 25: Line 19 plus line 24 = ^" and "Line 26: Amount
from line 25 of the previous page ^". Line 25 is one core/sum over line 19 (the personal amounts)
and line 24 (the CPP and EI amounts). Line 26 is a copy of line 25 and has no step of its own: the
line that reads it reads line 25 directly, as Newfoundland and Labrador's line 36 does.

The test builds the engine over the real federal parts and the real parts of lines 9 to 25 through
the shared `take_home_service` fixture, and types in only the salary (and, in one test, an optional
line). Figures hand-computed from the printed forms (not a CRA example): line 19 is 14,650.00, line
24 is 1,144.75 / 1,803.75 / 4,369.23, so line 25 (and line 26) is 15,794.75 at $20,000, 16,453.75 at
$30,000 and 19,019.23 at $70,000.
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CREDITS_SUBTOTAL_LINE_25
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import FEDERAL_PARTS, HEADER, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-pe/pe428_credits_subtotal_line_25"
PART_NAME = "pe428_line_25.yaml"

LINES = ["ca-pe/pe428_credits_subtotal_line_19", "ca-pe/pe428_cpp_ei_and_other_line_24"]
PARTS = (
    *FEDERAL_PARTS,
    "pe428_line_9.yaml",
    "pe428_line_10_worksheet_lines_2_to_3.yaml",
    "pe428_line_10_worksheet_lines_4_to_7.yaml",
    "pe428_line_10.yaml",
    "pe428_line_13_input.yaml",
    "pe428_line_13.yaml",
    "pe428_line_16_input.yaml",
    "pe428_line_16.yaml",
    "pe428_line_17_input.yaml",
    "pe428_line_18_input.yaml",
    "pe428_line_19.yaml",
    "pe428_line_20.yaml",
    "pe428_line_21.yaml",
    "pe428_line_22.yaml",
    "pe428_line_23.yaml",
    "pe428_line_24.yaml",
    PART_NAME,
)


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(IDENTIFIER), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "15794.75"), ("30000", "16453.75"), ("70000", "19019.23"), ("200000", "19083.58")],
)
def test_line_25_is_line_19_plus_line_24(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(_sheet(take_home_service, salary), IDENTIFIER) == D(expected)


def test_line_25_adds_an_optional_personal_amount_and_a_self_employment_amount(
    take_home_service: TakeHomeService,
) -> None:
    given = {
        "ca-pe/pe428_spouse_or_common_law_partner_amount_claimed_line_13": "1000.00",
        "ca/self_employment_cpp_qpp_contributions": "100.25",
    }
    sheet = _sheet(take_home_service, "20000", given)

    assert value(sheet, LINES[0]) == D("15650.00")
    assert value(sheet, LINES[1]) == D("1245.00")
    assert value(sheet, IDENTIFIER) == D("16895.00")


def test_the_trace_is_one_sum_of_lines_19_and_24(take_home_service: TakeHomeService) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        (LINES[0], D("14650.00")),
        (LINES[1], D("1144.75")),
    ]
    assert line.total == D("15794.75")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_one_untitled_sum_step_over_lines_19_and_24_with_nothing_blank() -> None:
    (step,) = _part()["capabilities"]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "25",
        "unit": "ca/cad",
        "params": {"rounding": "ca-pe/cent_rounding"},
        "consumes": {"parts": LINES},
        "produces": {"output": IDENTIFIER},
    }


def test_line_26_has_no_step_of_its_own() -> None:
    (step,) = _part()["capabilities"]

    assert step["reference"] == "25"
    assert not (PE_PARTS / "pe428_line_26.yaml").exists()


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_CREDITS_SUBTOTAL_LINE_25
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
