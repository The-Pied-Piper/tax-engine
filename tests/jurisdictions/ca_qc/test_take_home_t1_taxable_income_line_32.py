"""5005-R (2025) line 32 as the Quebec manifest part wires it.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 32 and line 14700: Add lines 29 to 31 (see line 25000 in Step 4). =".
One core/sum of the printed lines in form order, rounded half-up to the cent through
`ca-qc/cent_rounding`; a line left blank is read as 0.

The parts are the real ones (the line inputs and the sum). The header and the form's export are
test-local.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import (
    T1_LINE_32,
    T1_LINE_14400,
    T1_LINE_14500,
    T1_LINE_14600,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS_PART = "t1_taxable_income_line_32_inputs.yaml"
PART = "t1_taxable_income_line_32.yaml"
KINDS = {
    "14400": T1_LINE_14400,
    "14500": T1_LINE_14500,
    "14600": T1_LINE_14600,
}

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/t1_line_32
    capabilities: []
    """)


def line_32(take_home_service: TakeHomeService, **given: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, INPUTS_PART, PART).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            2025,
            (*(Artifact(KINDS[line], D(value)) for line, value in given.items()),),
        ),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(T1_LINE_32).value


def test_line_32_adds_the_lines_given(take_home_service: TakeHomeService) -> None:
    assert line_32(take_home_service, **{"14400": "1200", "14600": "300.25"}) == D("1500.25")


def test_line_32_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert line_32(take_home_service) == D("0.00")


def test_line_32_adds_all_three_lines(take_home_service: TakeHomeService) -> None:
    given = {"14400": "100", "14500": "200", "14600": "300"}
    assert line_32(take_home_service, **given) == D("600.00")
