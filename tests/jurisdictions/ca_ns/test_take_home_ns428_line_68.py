"""NS428 (2025) line 68, column 1: the UCCB and RDSP income, as a total of two T1 lines.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 68: Total of the
UCCB income (line 11700 of the return) and the RDSP income (line 12500 of the return)". The part
has no input of its own: the T1 form exports both lines, each is totalled by core/record_total and
the printed total is one core/sum in line order. A salary-only filer has neither, so it is 0.00.
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


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_salary_only_filer_has_no_such_income(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_68)) == "0.00"


def test_the_total_adds_both_lines(tmp_path: Path) -> None:
    given = {s.INPUTS["uccb_income"]: "1000.00", s.INPUTS["rdsp_income"]: "250.25"}

    assert s.line(tmp_path, "20000", s.LINE_68_A, given) == D("1000.00")
    assert s.line(tmp_path, "20000", s.LINE_68_B, given) == D("250.25")
    assert s.line(tmp_path, "20000", s.LINE_68, given) == D("1250.25")


def test_the_part_is_two_record_totals_and_a_sum_with_no_input_of_its_own() -> None:
    first, second, total = s.part("ns428_line_68.yaml")["capabilities"]

    assert [each["name"] for each in (first, second, total)] == [
        "core/record_total",
        "core/record_total",
        "core/sum",
    ]
    assert first["consumes"]["records"] == "ca/t1_taxable_income.uccb_income_line_11700"
    assert second["consumes"]["records"] == "ca/t1_taxable_income.rdsp_income_line_12500"
    assert total["reference"] == "68 (column 1)"
    assert total["params"] == {"rounding": "ca-ns/cent_rounding"}
    assert total["consumes"]["parts"] == [s.LINE_68_A, s.LINE_68_B]
    assert "blank" not in total
    assert total["produces"] == {"output": s.LINE_68}


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (s.LINE_68_A, ns_catalog.NS428_UCCB_INCOME_LINE_11700),
        (s.LINE_68_B, ns_catalog.NS428_RDSP_INCOME_LINE_12500),
        (s.LINE_68, ns_catalog.NS428_UCCB_RDSP_INCOME_LINE_68),
    ],
)
def test_the_kinds_are_registered_non_negative_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = nova_scotia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is constant
