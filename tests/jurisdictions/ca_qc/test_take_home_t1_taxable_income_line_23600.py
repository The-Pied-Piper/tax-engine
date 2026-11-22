"""5005-R (2025) line 57 (line 23600) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 57 and line 23600: Line 55 minus line 56 (if negative, enter "0") ... Net income =". The step
is core/subtract_not_below_zero of line 56 (`ca/social_benefits_repayment`) from line 55, rounded
through `ca-qc/cent_rounding`. Line 56 is the real optional input part, read as 0 when left out.

The part is the real one. The header, the form's export and the line 55 figure (a plain starting
input here) are made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import SOCIAL_BENEFITS_REPAYMENT
from tax_engine.jurisdictions.ca_qc.catalog import NET_INCOME, T1_LINE_55
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS = "t1_taxable_income_line_23500_inputs.yaml"
PART = "t1_taxable_income_line_23600.yaml"

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
        - ca-qc/net_income
    inputs:
      - name: ca-qc/t1_line_55
        required: true
    capabilities: []
    """)


def net_income(take_home_service: TakeHomeService, line_55: str, line_56: str | None) -> Decimal:
    starting = [Artifact(T1_LINE_55, D(line_55))]
    if line_56 is not None:
        starting.append(Artifact(SOCIAL_BENEFITS_REPAYMENT, D(line_56)))
    worksheets = take_home_service(HEADER, FORM, INPUTS, PART).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, tuple(starting))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(NET_INCOME).value


@pytest.mark.parametrize(
    ("line_55", "expected"),
    [("19835.00", "19835.00"), ("69335.00", "69335.00"), ("198926.00", "198926.00")],
)
def test_line_57_with_line_56_left_blank_is_line_55(
    take_home_service: TakeHomeService, line_55: str, expected: str
) -> None:
    assert net_income(take_home_service, line_55, None) == D(expected)


def test_line_57_is_line_55_less_line_56(take_home_service: TakeHomeService) -> None:
    assert net_income(take_home_service, "69335.00", "1000") == D("68335.00")


@pytest.mark.parametrize(("line_55", "line_56"), [("1000.00", "5000"), ("-765.00", None)])
def test_a_negative_difference_is_entered_as_zero(
    take_home_service: TakeHomeService, line_55: str, line_56: str | None
) -> None:
    assert net_income(take_home_service, line_55, line_56) == D("0.00")
