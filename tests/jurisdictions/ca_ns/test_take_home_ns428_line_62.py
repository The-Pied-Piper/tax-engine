"""NS428 (2025) line 62, line 60 plus line 61.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 62: Line 60 plus
line 61". The ticket's figures with no additional tax: 610.58, 1,422.86 and 7,213.10.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative
from tests.t691_support import line_14

D = Decimal


@pytest.mark.parametrize(("salary", "_tax", "_credits", "expected"), s.CASES)
def test_line_62_is_line_60_for_a_salary_only_caller(
    tmp_path: Path, salary: str, _tax: str, _credits: str, expected: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_62) == D(expected)


def test_a_given_t691_amount_adds_its_57_point_5_percent(tmp_path: Path) -> None:
    given = {artifact.kind.identifier: str(artifact.value) for artifact in line_14("1000.00")}

    assert s.line(tmp_path, "70000", s.LINE_62, given) == D("7788.10")


def test_the_part_is_one_untitled_sum_over_lines_60_and_61() -> None:
    assert s.part("ns428_line_62.yaml")["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "62",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"parts": [s.LINE_60, s.LINE_61]},
            "produces": {"output": s.LINE_62},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_62)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_LINE_62
