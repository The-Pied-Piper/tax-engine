"""NS428 (2025) line 49, the Schedule 9 line 13 amount times 8.79%.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 49:
Amount from line 13 of your federal Schedule 9 multiplied by 8.79% =". The 8.79% is the
`ca-ns/donations_credit_rate_line_49` dataset; the line has two boxes, the amount (box A, a
record total of Schedule 9's export) and the multiplied result (box B, one core/apply_rate step,
half-up to the cent). "Box A" and "box B" are the owner's naming, as on Saskatchewan's lines 54
and 55. A salary-only caller has no donations, so both boxes are 0.00.
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
LINE_PART = s.NS_PARTS / "ns428_line_49.yaml"
NEEDS = ("ns428_line_49.yaml",)
EXPORTS = (s.LINE_49_B,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0.00"), ("30000", "0.00"), ("70000", "0.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_49_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_49_B) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "donations" in amounts:
        kind = artifact_kinds().kind("ca/donations_and_gifts_line_12")
        assert isinstance(kind, AmountKind)
        found.append(Artifact(kind, D(amounts["donations"])))
    return found


SCENARIOS = [("70000", {"donations": "1000"}, "17.58"), ("70000", {"donations": "150.55"}, "13.23")]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_49_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_49_B) == D(expected)


KINDS = [
    (s.LINE_49_A, ns_catalog.NS428_DONATIONS_AMOUNT_LINE_49),
    (s.LINE_49_B, ns_catalog.NS428_DONATIONS_CREDIT_AT_RATE_LINE_49),
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
            "title": "Amount from line 13 of your federal Schedule 9",
            "reference": "49 box A",
            "unit": "ca/cad",
            "consumes": {"records": "ca/schedule_9.donations_and_gifts_line_13"},
            "produces": {"output": "ca-ns/ns428_donations_amount_line_49"},
        },
        {
            "name": "core/apply_rate",
            "reference": "49 box B",
            "unit": "ca/cad",
            "params": {"rate": "ca-ns/donations_credit_rate_line_49"},
            "consumes": {"base": "ca-ns/ns428_donations_amount_line_49"},
            "blank": {"base": "0"},
            "produces": {"output": "ca-ns/ns428_donations_credit_at_rate_line_49"},
        },
    ]
