"""NS428 (2025) line 64, line 62 minus line 63, not below zero: the tax after credits.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 64: Line 62 minus
line 63 (if negative, enter "0")". Line 63, the provincial foreign tax credit, is an optional
input read as 0 when left out. The ticket's figures: 610.58, 1,422.86 and 7,213.10.
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


@pytest.mark.parametrize(("salary", "_tax", "_credits", "expected"), s.CASES)
def test_line_64_at_the_salary(
    tmp_path: Path, salary: str, _tax: str, _credits: str, expected: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_64) == D(expected)


def test_a_given_foreign_tax_credit_is_subtracted(tmp_path: Path) -> None:
    assert s.line(tmp_path, "70000", s.LINE_64, {s.LINE_63: "500.00"}) == D("6713.10")


def test_a_foreign_tax_credit_larger_than_the_tax_floors_line_64_to_0(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_64, {s.LINE_63: "9000.00"})) == "0.00"


def test_credits_larger_than_the_tax_leave_a_tax_of_0_at_line_64(tmp_path: Path) -> None:
    given = {s.LINE_57: "10000.00"}

    assert str(s.line(tmp_path, "70000", s.LINE_64, given)) == "0.00"


def test_the_part_is_one_untitled_subtract_not_below_zero_with_a_blank_rule() -> None:
    assert s.part("ns428_line_64.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "64",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_62, "less": s.LINE_63},
            "blank": {"less": "0"},
            "produces": {"output": s.LINE_64},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_64)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_AFTER_CREDITS_LINE_64
