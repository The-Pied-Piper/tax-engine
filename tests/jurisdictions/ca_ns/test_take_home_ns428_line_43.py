"""NS428 (2025) line 43, line 38 minus line 42, not below zero.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 43: Line 38
minus line 42 (if negative, enter "0") =". One core/subtract_not_below_zero step over line 38
and line 42. A request that leaves line 38 blank has no medical expenses, so the blank is read as
0 and line 43 is 0.00. Hand figures: line 38 less line 42, not below 0.
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
LINE_PART = s.NS_PARTS / "ns428_line_43.yaml"
NEEDS = (
    "ns428_line_38.yaml",
    "ns428_line_39.yaml",
    "ns428_line_41.yaml",
    "ns428_line_42.yaml",
    "ns428_line_43.yaml",
)
EXPORTS = (s.LINE_43,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_43_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_43) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "medical" in amounts:
        found.append(medical_expenses(amounts["medical"]))
    return found


SCENARIOS = [
    ("70000", {"medical": "3000"}, "1363.00"),
    ("20000", {"medical": "3000"}, "2404.95"),
    ("70000", {"medical": "1637"}, "0.00"),
    ("70000", {"medical": "1637.01"}, "0.01"),
    ("70000", {"medical": "100"}, "0.00"),
]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_43_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_43) == D(expected)


KINDS = [
    (s.LINE_43, ns_catalog.NS428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_43),
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
            "name": "core/subtract_not_below_zero",
            "reference": "43",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {
                "amount": "ca-ns/ns428_medical_expenses_line_38",
                "less": "ca-ns/ns428_medical_expenses_limited_amount_line_42",
            },
            "blank": {"amount": "0"},
            "produces": {"output": "ca-ns/ns428_medical_expenses_over_limit_line_43"},
        }
    ]
