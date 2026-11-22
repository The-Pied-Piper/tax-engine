"""5005-R (2025) line 167 (line 46900) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 8,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 167 and line 46900: Eligible educator school supply tax credit Supplies expenses
(maximum $1,000) Line 46800 multiplied by 25% =".
Two steps: line 46800 held at the printed $1,000 (core/capped_amount), then 25%
(core/apply_rate), rounded half-up to the cent. A line 46800 left out is 0.

The parts are the real ones (the line inputs and the steps). The header and the form's export are
test-local.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import ELIGIBLE_EDUCATOR_CREDIT_LINE_167, T1_LINE_46800
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PARTS = (
    "t1_tax_and_credits_line_46900_inputs.yaml",
    "t1_tax_and_credits_line_46900.yaml",
)
KINDS = {
    "46800": T1_LINE_46800,
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
        - ca-qc/eligible_educator_credit_line_167
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
    return sheet.get(ELIGIBLE_EDUCATOR_CREDIT_LINE_167).value


def test_line_167_is_a_quarter_of_the_supplies(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"46800": "400.40"}) == D("100.10")


def test_supplies_above_the_maximum_are_held_at_1000(take_home_service: TakeHomeService) -> None:
    # The $1,000 maximum sits before the 25%, so it caps the supplies: 1,000 x 25% is 250.
    assert line(take_home_service, **{"46800": "2500"}) == D("250.00")


def test_supplies_at_the_maximum_give_250(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"46800": "1000"}) == D("250.00")


def test_line_167_rounds_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service, **{"46800": "0.02"}) == D("0.01")


def test_line_167_with_line_46800_left_out_is_zero(take_home_service: TakeHomeService) -> None:
    assert line(take_home_service) == D("0.00")
