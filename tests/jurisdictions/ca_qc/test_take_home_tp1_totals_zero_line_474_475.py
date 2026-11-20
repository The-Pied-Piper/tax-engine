"""Revenu Quebec TP-1 (2025) lines 474 and 475, the "0" of the other side of the sign of line 470,
as the Quebec take-home manifest wires it.

`core/credit_amount` takes the zero from the `ca-qc/tp1_zero_line_474_475` dataset, claimed whole;
it is not a line of the form, so it has no reference and no title. Lines 474 and 475 read it. Every
salary gives the same figure, since the zero does not read the return.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.jurisdictions.ca_qc.catalog import TP1_ZERO_LINE_474_475
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    FORM,
    LINE_474_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)
from tests.kinds import non_negative

LINE = "ca-qc/tp1_zero_line_474_475"
FILE = "tp1_totals_zero_line_474_475.yaml"


@pytest.mark.parametrize("salary", SALARIES)
def test_the_zero_is_0_at_each_salary(take_home_service: TakeHomeService, salary: str) -> None:
    sheet = totals_sheet(
        take_home_service, salary, totals_form("ca-qc/tp1_line_474"), LINE_474_PARTS
    )

    assert str(sheet.get(TP1_ZERO_LINE_474_475).value) == "0.00"


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((QUEBEC_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "No amount entered",
            "unit": "ca/cad",
            "params": {"amount": LINE},
            "produces": {"output": LINE},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = quebec_kinds().kind(LINE)

    assert kind is TP1_ZERO_LINE_474_475
    assert non_negative(kind)
