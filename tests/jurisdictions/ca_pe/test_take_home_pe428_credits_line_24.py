"""PE428 (2025) line 24, add lines 20 to 23, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 24: Add lines 20 to 23. = ^". Lines 20 and 22 are
the amounts from lines 30800 and 31200 of the return (CPP base and EI premiums); lines 21 and 23 are
the amounts from lines 31000 and 31217, which are 0 for a salary-only filer. The one step adds the
four with core/sum, as Newfoundland and Labrador's line 35 does. The form prints no label for line
24, so the step has no title.

The test builds the engine over the real federal parts and the real parts of lines 20 to 24 through
the shared `take_home_service` fixture, and types in only the salary (and, in one test, the two T1
amounts). Figures hand-computed from the printed forms (not a CRA example): CPP base 4.95% of the
salary above the $3,500 basic exemption, EI 1.64% to the $1,077.48 maximum, so line 24 is 1,144.75
at $20,000, 1,803.75 at $30,000 and 4,369.23 at $70,000.
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CPP_EI_AND_OTHER_LINE_24
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import FEDERAL_PARTS, HEADER, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-pe/pe428_cpp_ei_and_other_line_24"
PART_NAME = "pe428_credits_line_24.yaml"

LINES = [
    "ca-pe/pe428_cpp_contributions_line_20",
    "ca-pe/pe428_qpp_contributions_line_21",
    "ca-pe/pe428_ei_premiums_line_22",
    "ca-pe/pe428_ei_premiums_line_23",
]
PARTS = (
    *FEDERAL_PARTS,
    "pe428_credits_line_20.yaml",
    "pe428_credits_line_21.yaml",
    "pe428_credits_line_22.yaml",
    "pe428_credits_line_23.yaml",
    PART_NAME,
)


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(IDENTIFIER), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1144.75"), ("30000", "1803.75"), ("70000", "4369.23"), ("200000", "4433.58")],
)
def test_line_24_adds_the_cpp_and_ei_amounts(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(_sheet(take_home_service, salary), IDENTIFIER) == D(expected)


def test_line_24_adds_the_self_employment_amounts_when_the_filer_has_them(
    take_home_service: TakeHomeService,
) -> None:
    given = {
        "ca/self_employment_cpp_qpp_contributions": "100.25",
        "ca/ei_premiums_on_self_employment": "10.01",
    }
    sheet = _sheet(take_home_service, "20000", given)

    # 816.75 + 100.25 + 328.00 + 10.01.
    assert value(sheet, IDENTIFIER) == D("1255.01")


def test_the_trace_is_one_sum_of_lines_20_to_23_in_order(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        (LINES[0], D("816.75")),
        (LINES[1], D("0")),
        (LINES[2], D("328.00")),
        (LINES[3], D("0")),
    ]


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428_credits"}
    return part


def test_the_part_is_one_untitled_sum_step_over_lines_20_to_23_with_nothing_blank() -> None:
    (step,) = _part()["capabilities"]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "24",
        "unit": "ca/cad",
        "params": {"rounding": "ca-pe/cent_rounding"},
        "consumes": {"parts": LINES},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_CPP_EI_AND_OTHER_LINE_24
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
