"""PE428 (2025) line 21, amount from line 31000 of your return, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 21 and line 58280: Amount from line 31000 of your
return". The line is a copy, so its one step is a core/record_total over the export that gives it
(ca/t1_lines_copied_by_provinces.self_employment_cpp_qpp_contributions_line_31000), as Newfoundland
and Labrador's line it mirrors is.

The test builds the engine over the real federal parts and the real `pe428_credits_line_21.yaml`
through the shared `take_home_service` fixture, and types in only the salary (and, for the line
copied from an optional T1 input, the amount). The header and the form declaration are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_pe.catalog import PE428_QPP_CONTRIBUTIONS_LINE_21
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import FEDERAL_PARTS, HEADER, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-pe/pe428_qpp_contributions_line_21"
PART_NAME = "pe428_credits_line_21.yaml"

PARTS = (*FEDERAL_PARTS, PART_NAME)


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(IDENTIFIER), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00"), ("200000", "0.00")],
)
def test_line_21_at_a_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(_sheet(take_home_service, salary), IDENTIFIER) == D(expected)


def test_line_21_is_the_t1_line_31000_amount_when_the_filer_has_one(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(
        take_home_service, "20000", {"ca/self_employment_cpp_qpp_contributions": "100.25"}
    )

    assert value(sheet, IDENTIFIER) == D("100.25")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428_credits"}
    return part


def test_the_part_is_one_record_total_step_over_the_export() -> None:
    (step,) = _part()["capabilities"]

    assert step == {
        "name": "core/record_total",
        "title": "Amount from line 31000 of your return",
        "reference": "21",
        "unit": "ca/cad",
        "consumes": {
            "records": (
                "ca/t1_lines_copied_by_provinces.self_employment_cpp_qpp_contributions_line_31000"
            )
        },
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_QPP_CONTRIBUTIONS_LINE_21
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
