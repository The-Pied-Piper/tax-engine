"""NS428 (2025) lines 81 and 83: the income over the base amount and 5% of it.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 81: Line 79 minus
line 80 (if negative, enter "0")", "Line 82: Applicable rate 5%" and "Line 83: Line 81 multiplied by
the percentage from line 82". Line 79 is a copy of line 70, which is line 69 while column 2 is
deferred (#1999). Line 82 is the `ca-ns/low_income_reduction_rate` dataset and has no step. The
ticket's figures: line 81 is 4,835.00 / 14,735.00 / 54,335.00 and line 83 is 241.75 / 736.75 /
2,716.75 at salaries of 20,000 / 30,000 / 70,000.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_reduction_support as r
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize(("salary", "_income", "line_81", "line_83", "_c", "_d"), r.CASES)
def test_lines_81_and_83_at_the_salary(
    tmp_path: Path, salary: str, _income: str, line_81: str, line_83: str, _c: str, _d: str
) -> None:
    assert r.line(tmp_path, salary, r.LINE_81) == D(line_81)
    assert r.line(tmp_path, salary, r.LINE_83) == D(line_83)


def test_income_at_or_below_the_base_amount_leaves_lines_81_and_83_at_0(tmp_path: Path) -> None:
    salary, income, line_81, line_83, _reduction = r.AT_BASE

    assert r.line(tmp_path, salary, r.LINE_69) == D(income)
    assert str(r.line(tmp_path, salary, r.LINE_81)) == line_81
    assert str(r.line(tmp_path, salary, r.LINE_83)) == line_83


def test_line_83_rounds_half_up_to_the_cent(tmp_path: Path) -> None:
    # Income 15,000.83: line 81 is 0.83 and 5% of it is 0.0415, so 0.04.
    assert r.line(tmp_path, "15117", r.LINE_81) == D("0.83")
    assert r.line(tmp_path, "15117", r.LINE_83) == D("0.04")


def test_line_81_is_one_untitled_subtract_not_below_zero() -> None:
    assert r.part("ns428_line_81.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "81",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": r.LINE_69, "less": r.LINE_80},
            "produces": {"output": r.LINE_81},
        }
    ]


def test_line_83_is_one_untitled_apply_rate() -> None:
    assert r.part("ns428_line_83.yaml")["capabilities"] == [
        {
            "name": "core/apply_rate",
            "reference": "83",
            "unit": "ca/cad",
            "params": {"rate": "ca-ns/low_income_reduction_rate"},
            "consumes": {"base": r.LINE_81},
            "produces": {"output": r.LINE_83},
        }
    ]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [(r.LINE_81, ns_catalog.NS428_LINE_81), (r.LINE_83, ns_catalog.NS428_LINE_83)],
)
def test_the_kinds_are_registered_non_negative_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = r.kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is constant
