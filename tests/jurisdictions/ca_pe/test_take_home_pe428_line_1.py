"""PE428 (2025) line 1, taxable income, from the salary alone, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the PDF 5002-c-25e): "Enter your
taxable income from line 26000 of your return." Line 1 is a calculation, not an input: its one
step is a core/record_total over the T1 export that gives taxable income
(`ca/t1_taxable_income.taxable_income`), as Saskatchewan's line 1 is. The form prints no label for
the line, so the step has no title. Line 2 in each column is a copy of line 1 and has no step.

The expected figures are computed in `pe428_support` (the salary less the enhanced CPP deduction,
1% of the earnings from $3,500 to $71,300 plus 4% from $71,300 to $81,200, each rounded half-up to
the cent) and the hand figures are asserted too (not a CRA example): 20,000 gives 19,835.00; 70,000
gives 69,335.00. The salaries 50,469.70, 121,074.00 and 201,074.00 give taxable incomes of exactly
50,000.00, 120,000.00 and 200,000.00, the starting points of the ticket's hand figures.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe.catalog as pe_catalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1,)
EXPORTS = (s.LINE_1,)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(1).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


@pytest.mark.parametrize(("salary", "expected"), s.CASES)
def test_line_1_is_the_t1_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.taxable_income(D(salary)) == D(expected)
    value = _sheet(tmp_path, salary).get(s.kind(s.LINE_1)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)


def test_the_part_is_one_untitled_record_total_step_over_the_t1_taxable_income() -> None:
    (step,) = _part()

    assert step == {
        "name": "core/record_total",
        "reference": "1",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.taxable_income"},
        "produces": {"output": s.LINE_1},
    }


def test_line_1_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = prince_edward_island_kinds()

    assert s.LINE_1 in kinds.identifiers()
    kind = kinds.kind(s.LINE_1)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is pe_catalog.PE428_TAXABLE_INCOME_LINE_1
