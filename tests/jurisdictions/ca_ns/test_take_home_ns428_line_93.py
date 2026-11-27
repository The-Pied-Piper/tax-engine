"""NS428 (2025) line 93, line 91 minus line 92 (if negative, enter "0"), real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 93: Line 91 minus
line 92 (if negative, enter "0")". One core/subtract_not_below_zero step (`ns428_line_93.yaml`),
rounded half-up to the cent by `ca-ns/cent_rounding`. Line 92 is an optional input, read as 0 when
blank. The form prints no title for the line, so the step is untitled. Figures are hand-computed
from the printed form (not a CRA example): line 85 is 552.33 / 7,213.10 at salaries of 20,000 /
70,000.
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

# (salary, lines typed in, line 93).
CASES = [
    ("70000", {s.LINE_92: "1000"}, "6213.10"),
    ("20000", {s.LINE_92: "200"}, "352.33"),
    ("20000", {s.LINE_92: "600"}, "0.00"),
]


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_line_93_at_the_claims(
    tmp_path: Path, salary: str, given: dict[str, str], expected: str
) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_93, given)) == expected


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "552.33"), ("30000", "1422.86"), ("70000", "7213.10")]
)
def test_a_salary_only_filer_has_line_93_equal_to_line_85(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_93)) == expected


def test_the_part_is_one_untitled_subtract_not_below_zero_step() -> None:
    assert s.part("ns428_line_93.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "93",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {"amount": s.LINE_91, "less": s.LINE_92},
            "blank": {"less": "0"},
            "produces": {"output": s.LINE_93},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_93)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_LINE_93


def test_the_input_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_92)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_EQUITY_TAX_CREDIT_LINE_92
