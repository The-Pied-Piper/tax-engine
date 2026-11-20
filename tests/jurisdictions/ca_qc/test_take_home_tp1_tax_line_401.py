"""Revenu Quebec TP-1 (2025) line 401, "Income tax on taxable income. Complete Work Chart 401", as
the Quebec take-home manifest wires it: one `core/record_total` over the line 8 export of
`ca-qc/work_chart_401`. The chain runs the real parts of the chart and of the forms it reads (see
`tp1_tax_support.py`). The salary is $20,000, $70,000 and $200,000. The expected figures are
hand-computed from the printed chart, not a Revenu Quebec example.
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_tax_support import LINE_401_CHAIN, tax_sheet

PART = "tp1_tax_line_401.yaml"
FORM = "ca-qc/tp1_tax"
IDENTIFIER = "ca-qc/tp1_income_tax_on_taxable_income_line_401"
EXPORTS = (IDENTIFIER,)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "2608.90"), ("70000", "10241.10"), ("200000", "40602.47")],
)
def test_line_401_is_work_chart_401_line_8(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    sheet = tax_sheet(take_home_service, salary, EXPORTS, (*LINE_401_CHAIN, PART))

    assert str(sheet.get(TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401).value) == expected


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_chart_export_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "title": "Income tax on taxable income",
        "reference": "401",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/work_chart_401.work_chart_401_income_tax_line_8"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
