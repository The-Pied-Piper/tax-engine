"""NS428 (2025) line 29, add lines 26 to 28.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 29: Add lines
26 to 28." Line 28 (the caregiver amount, Worksheet NS428) is a blank claim outside the
salary-only scope and is not built, so the one core/sum adds line 26 and the checked line 27, as
Saskatchewan's line 35 does. Figures hand-computed: line 26 (the line 26 ticket's figures) plus
the pension income amount, which is 0 for a salary-only caller.
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
LINE_PART = s.NS_PARTS / "ns428_line_29.yaml"
NEEDS = (
    *s.CHAIN,
    "ns428_line_27_input.yaml",
    "ns428_line_27.yaml",
    "ns428_line_29.yaml",
)
EXPORTS = (s.LINE_29,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "12888.75"), ("30000", "13547.75"), ("70000", "16113.23")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_29_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_29) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "pension" in amounts:
        found.append(Artifact(s.kind(s.PENSION), D(amounts["pension"])))
    return found


SCENARIOS = [("70000", {"pension": "500"}, "16613.23")]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_29_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_29) == D(expected)


KINDS = [
    (s.LINE_29, ns_catalog.NS428_CREDITS_SUBTOTAL_LINE_29),
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
            "reference": "29",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-ns/ns428_credits_subtotal_line_26",
                    "ca-ns/ns428_pension_income_amount_checked_line_27",
                ]
            },
            "produces": {"output": "ca-ns/ns428_credits_subtotal_line_29"},
        }
    ]
