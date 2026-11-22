"""5005-R (2025) line 10400, other employment income, as the Quebec manifest part wires it.

The step is one core/sum over its one input, carried as it is (the form prints no rounding on this
line), and it prints the line once, with its printed title and reference. The header and the
form's export are made up.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import OTHER_EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import OTHER_EMPLOYMENT_INCOME_LINE_10400
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_employment_income_line_10400.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_employment_income
      required: true
      exports:
        - ca-qc/other_employment_income_line_10400
    capabilities: []
    """)


def sheet_of(take_home_service: TakeHomeService, *artifacts: Artifact[Any]) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets["ca-qc/t1_employment_income"]
    return sheet


@pytest.mark.parametrize(("other", "expected"), [(None, "0"), ("1500", "1500.00")])
def test_line_10400_is_the_other_income_and_zero_when_none_is_given(
    take_home_service: TakeHomeService, other: str | None, expected: str
) -> None:
    given = [] if other is None else [Artifact(OTHER_EMPLOYMENT_INCOME, D(other))]
    sheet = sheet_of(take_home_service, *given)
    assert sheet.get(OTHER_EMPLOYMENT_INCOME_LINE_10400).value == D(expected)


def test_line_10400_is_listed_once_with_its_title_and_reference(
    take_home_service: TakeHomeService,
) -> None:
    sheet = sheet_of(take_home_service)
    assert sheet.reference("other_employment_income_line_10400") == "10400"
    assert sheet.reference("other_employment_income") is None


def test_line_10400_prints_cents(take_home_service: TakeHomeService) -> None:
    # A line the person writes on the form rounds to the cent, so 1500 prints as 1500.00.
    sheet = sheet_of(take_home_service, Artifact(OTHER_EMPLOYMENT_INCOME, D("1500")))
    assert sheet.get(OTHER_EMPLOYMENT_INCOME_LINE_10400).value.as_tuple().exponent == -2
