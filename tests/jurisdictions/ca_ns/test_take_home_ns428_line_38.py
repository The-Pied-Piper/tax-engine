"""NS428 (2025) line 38, medical expenses, from T1 line 33099.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 38 and line
58689: Amount from line 33099 of your return". The amount is T1 line 33099, which the T1 owns
and exports; the one step is core/record_total over that export, as Saskatchewan's line 43 is. A
salary-only caller has none, so it is 0.
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
LINE_PART = s.NS_PARTS / "ns428_line_38.yaml"
NEEDS = ("ns428_line_38.yaml",)
EXPORTS = (s.LINE_38,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_38_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_38) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "medical" in amounts:
        found.append(medical_expenses(amounts["medical"]))
    return found


SCENARIOS = [("70000", {"medical": "3000"}, "3000.00")]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_38_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_38) == D(expected)


KINDS = [
    (s.LINE_38, ns_catalog.NS428_MEDICAL_EXPENSES_LINE_38),
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
            "name": "core/record_total",
            "title": "Amount from line 33099 of your return",
            "reference": "38",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_lines_copied_by_provinces.medical_expenses_line_33099"},
            "produces": {"output": "ca-ns/ns428_medical_expenses_line_38"},
        }
    ]
