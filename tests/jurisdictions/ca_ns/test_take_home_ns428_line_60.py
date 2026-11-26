"""NS428 (2025) line 60, line 55 minus line 59, not below zero.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 60: Line 55 minus
line 59 (if negative, enter "0")". The ticket's figures: 610.58, 1,422.86 and 7,213.10.
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
def test_line_60_at_the_salary(
    tmp_path: Path, salary: str, _tax: str, _credits: str, expected: str
) -> None:
    assert s.line(tmp_path, salary, s.LINE_60) == D(expected)


def test_credits_larger_than_the_tax_floor_line_60_to_0(tmp_path: Path) -> None:
    # Line 55 is 8,629.45 and line 59 is 1,416.35 + 10,000.00, so line 55 minus line 59 is negative.
    value = s.line(tmp_path, "70000", s.LINE_60, {s.LINE_57: "10000.00"})

    assert str(value) == "0.00"


def test_a_low_income_filer_has_line_60_of_0_or_more(tmp_path: Path) -> None:
    assert s.line(tmp_path, "5000", s.LINE_60) >= D("0")


def test_the_part_is_one_untitled_subtract_not_below_zero() -> None:
    assert s.part("ns428_line_60.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "60",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_55, "less": s.LINE_59},
            "produces": {"output": s.LINE_60},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_60)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_LINE_60
