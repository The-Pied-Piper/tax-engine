"""NS428 (2025) line 45, line 43 plus line 44.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 45 and line
58769: Line 43 plus line 44 =". Line 44 (the allowable amount of medical expenses for other
dependants, Worksheet NS428) is a blank claim outside the salary-only scope and is not built, so
the one core/sum is over line 43 alone.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_credits_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative
from tests.medical_support import medical_expenses

D = Decimal
LINE_PART = s.NS_PARTS / "ns428_line_45.yaml"
NEEDS = (
    "ns428_line_38.yaml",
    "ns428_line_39.yaml",
    "ns428_line_41.yaml",
    "ns428_line_42.yaml",
    "ns428_line_43.yaml",
    "ns428_line_45.yaml",
)
EXPORTS = (s.LINE_45,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_45_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_45) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "medical" in amounts:
        found.append(medical_expenses(amounts["medical"]))
    return found


SCENARIOS = [("70000", {"medical": "3000"}, "1363.00")]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_45_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_45) == D(expected)


KINDS = [
    (s.LINE_45, ns_catalog.NS428_MEDICAL_EXPENSES_LINE_45),
]


@pytest.mark.parametrize(("identifier", "declared"), KINDS)
def test_each_kind_is_a_registered_non_negative_amount_kind(
    identifier: str, declared: AmountKind
) -> None:
    kind = nova_scotia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is declared
    assert identifier in nova_scotia_kinds().identifiers()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_exactly_the_printed_steps() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "45",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": ["ca-ns/ns428_medical_expenses_over_limit_line_43"]},
            "produces": {"output": "ca-ns/ns428_medical_expenses_line_45"},
        }
    ]
