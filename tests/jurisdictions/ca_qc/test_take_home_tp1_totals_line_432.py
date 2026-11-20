"""Revenu Quebec TP-1 (2025) page 5, "Amount from line 432", as the Quebec take-home manifest wires
it: one `core/record_total` over the line 432 export of `ca-qc/tp1_tax`. The chain runs the real
parts of lines 401 to 432 and of the forms they read (see `tp1_totals_support.py`). The salary is
$20,000, $70,000 and $200,000. The expected figures are hand-computed from the printed lines, not a
Revenu Quebec example."""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import TP1_TOTALS_LINE_432
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_totals_support import (
    EXPECTED,
    FORM,
    LINE_432_PARTS,
    SALARIES,
    totals_form,
    totals_sheet,
)

PART = "tp1_totals_line_432.yaml"
IDENTIFIER = "ca-qc/tp1_totals_line_432"


@pytest.mark.parametrize("salary", SALARIES)
def test_line_432_is_the_line_432_of_the_tax_form(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = totals_sheet(take_home_service, salary, totals_form(IDENTIFIER), LINE_432_PARTS)

    assert str(sheet.get(TP1_TOTALS_LINE_432).value) == EXPECTED[salary]["432"]


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_record_total_over_the_tax_form_export() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/record_total",
        "reference": "432",
        "unit": "ca/cad",
        "consumes": {"records": "ca-qc/tp1_tax.tp1_line_432"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    kind = quebec_kinds().kind(IDENTIFIER)

    assert kind is TP1_TOTALS_LINE_432
    assert isinstance(kind, AmountKind)
    assert kind.non_negative
