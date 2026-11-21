"""5005-R (2025) line 69 (line 25700) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 69 and line 25700: Add lines 59 to 68. =".
Three core/sum steps: two unprinted subtotals (lines 59 to 63 and 64 to 68), then the printed line,
which rounds once.

The parts are the real ones (the line inputs and the step). The header and the form's export are
test-local.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.taxable_income import DEDUCTIONS_FROM_NET_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_24400, T1_LINE_25000, T1_LINE_25600
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS_PART = "t1_taxable_income_line_25700_inputs.yaml"
PART = "t1_taxable_income_line_25700.yaml"
KINDS = {
    "24400": T1_LINE_24400,
    "25000": T1_LINE_25000,
    "25600": T1_LINE_25600,
}

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca-qc/t1_line_24400
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca/deductions_from_net_income
    capabilities: []
    """)


def line(take_home_service: TakeHomeService, **given: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, INPUTS_PART, PART).compute(
        JurisdictionCode("CA-QC"),
        2025,
        *(Artifact(KINDS[name], D(value)) for name, value in given.items()),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(DEDUCTIONS_FROM_NET_INCOME).value


def test_line_69_adds_the_lines_given(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"24400": "1000", "25600": "250.50"}) == D("1250.50")


def test_line_69_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service) == D("0.00")


def test_line_69_rounds_the_sum_once(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"24400": "0.004", "25000": "0.004"}) == D("0.01")
