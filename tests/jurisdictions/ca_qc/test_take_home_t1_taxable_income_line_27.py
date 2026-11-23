"""5005-R (2025) line 27 as the Quebec manifest part wires it.

Form text (CRA 5005-R page 3, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 27: Add lines 22 to 26. Net self-employment income =".
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
    NET_SELF_EMPLOYMENT_INCOME,
    T1_LINE_13500,
    T1_LINE_13700,
    T1_LINE_13900,
    T1_LINE_14100,
    T1_LINE_14300,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS_PART = "t1_taxable_income_line_27_inputs.yaml"
PART = "t1_taxable_income_line_27.yaml"
KINDS = {
    "13500": T1_LINE_13500,
    "13700": T1_LINE_13700,
    "13900": T1_LINE_13900,
    "14100": T1_LINE_14100,
    "14300": T1_LINE_14300,
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
        - ca-qc/net_self_employment_income
    capabilities: []
    """)


def line_27(take_home_service: TakeHomeService, **given: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, INPUTS_PART, PART).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            2025,
            (*(Artifact(KINDS[line], D(value)) for line, value in given.items()),),
        ),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(NET_SELF_EMPLOYMENT_INCOME).value


def test_line_27_adds_the_lines_given(take_home_service: TakeHomeService) -> None:
    assert line_27(take_home_service, **{"13500": "4000", "14100": "1500.50"}) == D("5500.50")


def test_line_27_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert line_27(take_home_service) == D("0.00")


def test_a_loss_on_one_line_reduces_line_27(take_home_service: TakeHomeService) -> None:
    # The form prints no floor on lines 22 to 26 or line 27; a loss is shown in brackets.
    assert line_27(take_home_service, **{"13500": "-2000", "13700": "5000"}) == D("3000.00")


def test_line_27_rounds_the_sum_once(take_home_service: TakeHomeService) -> None:
    assert line_27(take_home_service, **{"13500": "0.004", "13700": "0.004"}) == D("0.01")
