"""5005-R (2025) line 142 (line 41600) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 7,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 142 and line 41600: Add lines 139 to 141. =".
One core/sum of the printed lines in form order, rounded half-up to the cent; a blank line is
read as 0.

The parts are the real ones (the line inputs and the steps). The header and the form's export are
test-local.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import (
    FEDERAL_CREDITS_LINE_142,
    T1_LINE_41000,
    T1_LINE_41200,
    T1_LINE_41400,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_tax_and_credits_line_41600_inputs.yaml",
    "t1_tax_and_credits_line_41600.yaml",
)
KINDS = {
    "41000": T1_LINE_41000,
    "41200": T1_LINE_41200,
    "41400": T1_LINE_41400,
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
      name: ca-qc/t1_tax_and_credits
      required: true
      exports:
        - ca-qc/federal_credits_line_142
    capabilities: []
    """)


def line(take_home_service: TakeHomeService, **given: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            2025,
            (*(Artifact(KINDS[name], D(value)) for name, value in given.items()),),
        ),
    )
    (sheet,) = worksheets["ca-qc/t1_tax_and_credits"]
    return sheet.get(FEDERAL_CREDITS_LINE_142).value


def test_line_142_adds_the_lines_given(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"41000": "100.10", "41400": "50.25"}) == D("150.35")


def test_line_142_adds_all_three_lines(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"41000": "1", "41200": "2", "41400": "3"}) == D("6.00")


def test_line_142_with_every_line_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service) == D("0.00")


def test_line_142_rounds_the_sum_once(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"41000": "0.004", "41200": "0.004"}) == D("0.01")
