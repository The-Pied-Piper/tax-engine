"""5005-R (2025) line 70 (line 26000) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 5, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 70 and line 26000: Line 58 minus line 69 (if negative, enter "0") Taxable income =". The step
is core/subtract_not_below_zero of line 69 (`ca/deductions_from_net_income`) from net income
(line 58, a copy of line 57), rounded through `ca-qc/cent_rounding`. Line 69 is the real optional
input part, read as 0 when left out.

The part is the real one. The header, the form's export and the net income figure (a plain starting
input here) are made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.taxable_income import DEDUCTIONS_FROM_NET_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import NET_INCOME, TAXABLE_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS = "t1_taxable_income_line_25700_inputs.yaml"
PART = "t1_taxable_income_line_26000.yaml"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca-qc/net_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/taxable_income
    inputs:
      - name: ca-qc/net_income
        required: true
    capabilities: []
    """)


def taxable_income(take_home_service: TakeHomeService, net: str, deductions: str | None) -> Decimal:
    starting = [Artifact(NET_INCOME, D(net))]
    if deductions is not None:
        starting.append(Artifact(DEDUCTIONS_FROM_NET_INCOME, D(deductions)))
    worksheets = take_home_service(HEADER, FORM, INPUTS, PART).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(TAXABLE_INCOME).value


@pytest.mark.parametrize(
    ("net", "expected"),
    [("19835.00", "19835.00"), ("69335.00", "69335.00"), ("198926.00", "198926.00")],
)
def test_line_70_with_line_69_left_blank_is_line_58(
    take_home_service: TakeHomeService, net: str, expected: str
) -> None:
    assert taxable_income(take_home_service, net, None) == D(expected)


def test_line_70_is_line_58_less_line_69(take_home_service: TakeHomeService) -> None:
    assert taxable_income(take_home_service, "69335.00", "1000") == D("68335.00")


def test_a_deduction_above_net_income_is_entered_as_zero(
    take_home_service: TakeHomeService,
) -> None:
    assert taxable_income(take_home_service, "1000.00", "5000") == D("0.00")
