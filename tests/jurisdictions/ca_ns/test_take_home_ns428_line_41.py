"""NS428 (2025) line 41, line 39 times the applicable medical rate.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 40:
Applicable rate 3%" and "Line 41: Line 39 multiplied by the percentage from line 40 =". Line 40 is
the printed 3%, the `ca-ns/medical_expense_rate` dataset, with no step of its own; line 41 is one
core/apply_rate step, half-up to the cent. Hand figures: 3% of line 39.
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
LINE_PART = s.NS_PARTS / "ns428_line_41.yaml"
NEEDS = (
    "ns428_line_39.yaml",
    "ns428_line_41.yaml",
)
EXPORTS = (s.LINE_41,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "595.05"), ("30000", "892.05"), ("70000", "2080.05")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_41_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_41) == D(expected)


KINDS = [
    (s.LINE_41, ns_catalog.NS428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_41),
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
            "name": "core/apply_rate",
            "reference": "41",
            "unit": "ca/cad",
            "params": {"rate": "ca-ns/medical_expense_rate"},
            "consumes": {"base": "ca-ns/ns428_net_income_line_39"},
            "produces": {"output": "ca-ns/ns428_medical_expenses_rate_amount_line_41"},
        }
    ]
