"""5005-R (2025) line 155 (line 43850) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 8,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 155 and line 43850: Line 153 minus line 154 =".
One core/subtract, rounded half-up to the cent, not floored: the form prints no floor, so a line
154 above line 153 gives a negative line 155. A blank line is read as 0.

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
    INCOME_TAX_DEDUCTED_NET_LINE_155,
    T1_LINE_43700,
    T1_LINE_43800,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_tax_and_credits_line_43850_inputs.yaml",
    "t1_tax_and_credits_line_43850.yaml",
)
KINDS = {
    "43700": T1_LINE_43700,
    "43800": T1_LINE_43800,
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
        - ca-qc/income_tax_deducted_net_line_155
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
    return sheet.get(INCOME_TAX_DEDUCTED_NET_LINE_155).value


def test_line_155_is_line_153_less_line_154(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"43700": "9000", "43800": "1250.25"}) == D("7749.75")


def test_a_line_154_above_line_153_gives_a_negative_line_155(
    take_home_service: TakeHomeService,
) -> None:
    assert line(take_home_service, **{"43700": "100", "43800": "300"}) == D("-200.00")


def test_a_blank_line_154_is_read_as_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"43700": "100"}) == D("100.00")


def test_a_blank_line_153_is_read_as_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"43800": "100"}) == D("-100.00")


def test_line_155_with_both_lines_blank_is_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service) == D("0.00")
