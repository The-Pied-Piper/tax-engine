"""PE428 (2025) line 20, cpp or qpp contributions, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 20 and line 58240: Amount from line 30800 of your
return". The line is a copy, so its one step is a core/record_total over the export that gives it
(ca/schedule_8.schedule_8_cpp_base_contributions_on_return), as Newfoundland and Labrador's line it
mirrors is.

The test builds the engine over the real federal parts and the real `pe428_credits_line_20.yaml`
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
from tax_engine.jurisdictions.ca_pe.catalog import PE428_CPP_CONTRIBUTIONS_LINE_20
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import FEDERAL_PARTS, HEADER, compute, form, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-pe/pe428_cpp_contributions_line_20"
PART_NAME = "pe428_credits_line_20.yaml"

PARTS = (*FEDERAL_PARTS, PART_NAME)


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(IDENTIFIER), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "816.75"), ("30000", "1311.75"), ("70000", "3291.75"), ("200000", "3356.10")],
)
def test_line_20_at_a_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert value(_sheet(take_home_service, salary), IDENTIFIER) == D(expected)


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
        "title": "CPP or QPP contributions",
        "reference": "20",
        "unit": "ca/cad",
        "consumes": {"records": "ca/schedule_8.schedule_8_cpp_base_contributions_on_return"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(IDENTIFIER)

    assert kind is PE428_CPP_CONTRIBUTIONS_LINE_20
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
