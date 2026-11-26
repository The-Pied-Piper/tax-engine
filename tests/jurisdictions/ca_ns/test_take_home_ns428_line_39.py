"""NS428 (2025) line 39, net income, from T1 line 23600.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 39: Amount
from line 23600 of your return". It is the T1 net income, which reaches this form as a record list,
so the one step is core/record_total over it, as Saskatchewan's line 44 is. The form prints no
label for the line, so the step has no title. Hand figures: the salary less the enhanced CPP
deduction (1% of the earnings from $3,500 to $71,300).
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
LINE_PART = s.NS_PARTS / "ns428_line_39.yaml"
NEEDS = ("ns428_line_39.yaml",)
EXPORTS = (s.LINE_39,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "19835.00"), ("30000", "29735.00"), ("70000", "69335.00")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_39_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_39) == D(expected)


KINDS = [
    (s.LINE_39, ns_catalog.NS428_NET_INCOME_LINE_39),
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
            "reference": "39",
            "unit": "ca/cad",
            "consumes": {"records": "ca/t1_taxable_income.net_income"},
            "produces": {"output": "ca-ns/ns428_net_income_line_39"},
        }
    ]
