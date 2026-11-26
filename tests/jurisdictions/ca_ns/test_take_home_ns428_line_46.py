"""NS428 (2025) line 46, line 37 plus line 45.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 46 and line
58800: Line 37 plus line 45 =". One core/sum over line 37 and line 45, as Saskatchewan's line 51
is. The ticket's figures at the three salaries: 12,888.75, 13,547.75 and 16,113.23 (line 26, with
no other claim).
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
from tests.medical_support import medical_expenses

D = Decimal
LINE_PART = s.NS_PARTS / "ns428_line_46.yaml"
NEEDS = (
    *s.CHAIN,
    "ns428_line_27_input.yaml",
    "ns428_line_27.yaml",
    "ns428_line_29.yaml",
    "ns428_line_32.yaml",
    "ns428_line_33.yaml",
    "ns428_line_37.yaml",
    "ns428_line_38.yaml",
    "ns428_line_39.yaml",
    "ns428_line_41.yaml",
    "ns428_line_42.yaml",
    "ns428_line_43.yaml",
    "ns428_line_45.yaml",
    "ns428_line_46.yaml",
)
EXPORTS = (s.LINE_46,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "12888.75"), ("30000", "13547.75"), ("70000", "16113.23")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_46_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_46) == D(expected)


def _given(**amounts: str) -> list[Artifact[Any]]:
    found: list[Artifact[Any]] = []
    if "loan" in amounts:
        kind = artifact_kinds().kind("ca/student_loan_interest")
        assert isinstance(kind, AmountKind)
        found.append(Artifact(kind, D(amounts["loan"])))
    if "medical" in amounts:
        found.append(medical_expenses(amounts["medical"]))
    if "pension" in amounts:
        found.append(Artifact(s.kind(s.PENSION), D(amounts["pension"])))
    return found


SCENARIOS = [("70000", {"pension": "500", "loan": "1000", "medical": "3000"}, "18976.23")]


@pytest.mark.parametrize(("salary", "amounts", "expected"), SCENARIOS)
def test_line_46_with_claims_typed_in(
    tmp_path: Path, salary: str, amounts: dict[str, str], expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, *_given(**amounts))
    assert s.value(sheet, s.LINE_46) == D(expected)


KINDS = [
    (s.LINE_46, ns_catalog.NS428_CREDITS_TOTAL_LINE_46),
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
            "reference": "46",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-ns/ns428_credits_subtotal_line_37",
                    "ca-ns/ns428_medical_expenses_line_45",
                ]
            },
            "produces": {"output": "ca-ns/ns428_credits_total_line_46"},
        }
    ]
