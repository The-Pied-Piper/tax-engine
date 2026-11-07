"""ON428 (2025) line 74, the basic reduction, as the Ontario take-home manifest part wires it.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 74: Basic reduction 294.00". The amount is the
`ca-on/tax_reduction_basic` dataset, claimed whole through core/credit_amount, so it is the same at
every salary. Line 74 reads nothing. Line 77 reads it later.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import ON428_BASIC_REDUCTION_LINE_74
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "on428_line_74.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - ca-on/on428_basic_reduction_line_74
    """)


def line_74(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428"]
    value = sheet.get(ON428_BASIC_REDUCTION_LINE_74).value
    assert isinstance(value, Decimal)
    return value


def test_line_74_kind_id_is_pinned() -> None:
    assert ON428_BASIC_REDUCTION_LINE_74.identifier == "ca-on/on428_basic_reduction_line_74"


@pytest.mark.parametrize("salary", ["20000", "70000", "150000"])
def test_line_74_is_the_basic_reduction_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_74(take_home_service, salary) == D("294.00")
