"""NS428 (2025) line 42, the lesser of the printed $1,637 and line 41.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 42: Enter
whichever is less: $1,637 or the amount on line 41." The $1,637 is the
`ca-ns/medical_expense_dollar_limit` dataset, with no step of its own; line 42 is one
core/capped_amount step. Hand figures: 595.05 at
20,000 (3% of 19,835) and 892.05 at 30,000 (3% of 29,735), and the cap, 1,637.00, at 70,000 (3% of
69,335 is 2,080.05).
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

D = Decimal
LINE_PART = s.NS_PARTS / "ns428_line_42.yaml"
NEEDS = (
    "ns428_line_39.yaml",
    "ns428_line_41.yaml",
    "ns428_line_42.yaml",
)
EXPORTS = (s.LINE_42,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "595.05"), ("30000", "892.05"), ("70000", "1637.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_42_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_42) == D(expected)


KINDS = [
    (s.LINE_42, ns_catalog.NS428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_42),
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
            "name": "core/capped_amount",
            "reference": "42",
            "unit": "ca/cad",
            "params": {"cap": "ca-ns/medical_expense_dollar_limit"},
            "consumes": {"base": "ca-ns/ns428_medical_expenses_rate_amount_line_41"},
            "produces": {"output": "ca-ns/ns428_medical_expenses_limited_amount_line_42"},
        }
    ]
