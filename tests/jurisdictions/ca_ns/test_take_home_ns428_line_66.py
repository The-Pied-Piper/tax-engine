"""NS428 (2025) line 66, column 1: the UCCB and RDSP income repayments, as a total of two T1 lines.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 66: Total of the
universal child care benefit (UCCB) repayment (line 21300 of the return) and the registered
disability savings plan (RDSP) income repayment (included on line 23200 of the return)". The part
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
def test_a_salary_only_filer_has_no_repayments(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_66)) == "0.00"


def test_a_uccb_repayment_is_read_from_t1_line_21300(tmp_path: Path) -> None:
    given = {s.INPUTS["uccb_repayment"]: "120.00"}

    assert s.line(tmp_path, "20000", s.LINE_66_A, given) == D("120.00")
    assert s.line(tmp_path, "20000", s.LINE_66, given) == D("120.00")


def test_the_total_adds_both_lines(tmp_path: Path) -> None:
    given = {s.INPUTS["uccb_repayment"]: "120.00", s.INPUTS["rdsp_income_repayment"]: "80.50"}

    assert s.line(tmp_path, "20000", s.LINE_66, given) == D("200.50")


def test_the_part_is_two_record_totals_and_a_sum_with_no_input_of_its_own() -> None:
    first, second, total = s.part("ns428_line_66.yaml")["capabilities"]

    assert [each["name"] for each in (first, second, total)] == [
        "core/record_total",
        "core/record_total",
        "core/sum",
    ]
    assert first["consumes"]["records"] == "ca/t1_taxable_income.uccb_repayment_line_21300"
    assert second["consumes"]["records"] == (
        "ca/t1_taxable_income.rdsp_income_repayment_line_23200"
    )
    assert total["reference"] == "66 (column 1)"
    assert total["params"] == {"rounding": "ca-ns/cent_rounding"}
    assert total["consumes"]["parts"] == [s.LINE_66_A, s.LINE_66_B]
    assert "blank" not in total
    assert total["produces"] == {"output": s.LINE_66}


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (s.LINE_66_A, ns_catalog.NS428_UCCB_REPAYMENT_LINE_21300),
        (s.LINE_66_B, ns_catalog.NS428_RDSP_INCOME_REPAYMENT_LINE_23200),
        (s.LINE_66, ns_catalog.NS428_UCCB_RDSP_REPAYMENTS_LINE_66),
    ],
)
def test_the_kinds_are_registered_non_negative_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = nova_scotia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is constant
