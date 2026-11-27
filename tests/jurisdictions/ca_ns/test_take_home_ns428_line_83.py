"""NS428 (2025) line 83: line 81 multiplied by the percentage from line 82.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 82: Applicable
rate 5%" and "Line 83: Line 81 multiplied by the percentage from line 82". Line 82 is the
`ca-ns/low_income_reduction_rate` dataset and has no step. The ticket's figures: 241.75 / 736.75 /
2,716.75 at salaries of 20,000 / 30,000 / 70,000.
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

D = Decimal


@pytest.mark.parametrize(("salary", "_income", "_a", "line_83", "_b", "_c"), s.REDUCTION_CASES)
def test_line_83_at_the_salary(
    tmp_path: Path, salary: str, _income: str, _a: str, line_83: str, _b: str, _c: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_83) == D(line_83)


def test_line_83_is_0_at_the_base_amount(tmp_path: Path) -> None:
    salary, _income, _line_81, line_83, _reduction = s.AT_BASE

    assert str(s.line(tmp_path, salary, s.LINE_83)) == line_83


def test_line_83_rounds_half_up_to_the_cent(tmp_path: Path) -> None:
    # Income 15,000.83: line 81 is 0.83 and 5% of it is 0.0415, so 0.04.
    assert s.line(tmp_path, "15117", s.LINE_81) == D("0.83")
    assert s.line(tmp_path, "15117", s.LINE_83) == D("0.04")


def test_line_83_is_one_untitled_apply_rate() -> None:
    assert s.part("ns428_line_83.yaml")["capabilities"] == [
        {
            "name": "core/apply_rate",
            "reference": "83",
            "unit": "ca/cad",
            "params": {"rate": "ca-ns/low_income_reduction_rate"},
            "consumes": {"base": s.LINE_81},
            "produces": {"output": s.LINE_83},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_83)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_LINE_83
