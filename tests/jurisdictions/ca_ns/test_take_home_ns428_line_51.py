"""NS428 (2025) line 51, line 49 plus line 50.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 51 and line
58969: Line 49 plus line 50 =". One core/sum over the two boxes B, as Saskatchewan's line 56 is.
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
from tax_engine.registrations import artifact_kinds
from tests.jurisdictions.ca_ns import ns428_credits_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINE_PART = s.NS_PARTS / "ns428_line_51.yaml"
NEEDS = (
    "ns428_line_49.yaml",
    "ns428_line_50.yaml",
    "ns428_line_51.yaml",
)
EXPORTS = (s.LINE_51,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_51_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_51) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "donations" in amounts:
        kind = artifact_kinds().kind("ca/donations_and_gifts_line_12")
        assert isinstance(kind, AmountKind)
        found.append(Artifact(kind, D(amounts["donations"])))
    return found


SCENARIOS = [
    ("70000", {"donations": "1000"}, "185.58"),
    ("70000", {"donations": "150.55"}, "13.23"),
]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_51_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_51) == D(expected)


KINDS = [
    (s.LINE_51, ns_catalog.NS428_DONATIONS_CREDIT_LINE_51),
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
            "reference": "51",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-ns/ns428_donations_credit_at_rate_line_49",
                    "ca-ns/ns428_donations_credit_at_rate_line_50",
                ]
            },
            "produces": {"output": "ca-ns/ns428_donations_credit_line_51"},
        }
    ]
