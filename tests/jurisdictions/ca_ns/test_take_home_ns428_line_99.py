"""NS428 (2025) line 99, the Nova Scotia tax, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 99: Line 97 minus
line 98 (if negative, enter "0") Enter this amount on line 42800 of your return. Nova Scotia tax".
Line 99 is line 97 less line 98, the age tax credit (0.00 unless born in 1960 or earlier with
taxable income under $24,000), not below 0: one core/subtract_not_below_zero step, rounded half-up
to the cent by `ca-ns/cent_rounding`. Line 99 is the form's export and is supplied as
`ca/provincial_tax.amount` (see `test_form_ns428.py`). Figures are the ticket's: 552.33 /
1,422.86 / 7,213.10 at salaries of 20,000 / 30,000 / 70,000.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


@pytest.mark.parametrize(("salary", "_income", "_a", "_b", "_c", "line_99"), s.REDUCTION_CASES)
def test_line_99_at_the_salary(
    tmp_path: Path, salary: str, _income: str, _a: str, _b: str, _c: str, line_99: str
) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_99)) == line_99


def test_the_claims_lower_line_99_and_line_99_is_never_negative(tmp_path: Path) -> None:
    claims = {s.LINE_94: "200", s.LINE_96: "300"}

    assert str(s.line(tmp_path, "20000", s.LINE_97, claims)) == "52.33"
    assert str(s.line(tmp_path, "20000", s.LINE_99, claims)) == "52.33"
    assert str(s.line(tmp_path, "20000", s.LINE_97, {s.LINE_96: "600"})) == "0.00"
    assert str(s.line(tmp_path, "20000", s.LINE_99, {s.LINE_96: "600"})) == "0.00"


def test_the_part_is_one_untitled_subtract_not_below_zero_step_line_97_less_line_98() -> None:
    assert s.part("ns428_line_99.yaml")["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "99",
            "unit": "ca/cad",
            "params": {"rounding": "ca-ns/cent_rounding"},
            "consumes": {
                "amount": s.LINE_97,
                "less": "ca-ns/ns428_age_tax_credit_line_98",
            },
            "produces": {"output": s.LINE_99},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_99)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_NOVA_SCOTIA_TAX_LINE_99
