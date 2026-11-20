"""5005-R (2025) line 57 (line 23600) before its floor, the signed net income.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 57 and line 23600: Line 55 minus line 56 (if negative, enter "0")". The shared Schedule 6
line 7 prints "Net income from line 23600 of the return (or the amount you would have entered if the
instructions on line 23600 said "if negative, show in brackets")", so one core/subtract produces the
unfloored figure `ca-qc/net_income_signed`; the floored net income is its own part and is unchanged.

The part is the real one, with the real line 56 input part. The header, the form's export and the
line 55 figure (a plain starting input here) are made up.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import SOCIAL_BENEFITS_REPAYMENT
from tax_engine.jurisdictions.ca_qc.catalog import NET_INCOME_SIGNED, T1_LINE_55
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
INPUTS = "t1_taxable_income_line_23500_inputs.yaml"
PART = "t1_taxable_income_line_23600_signed.yaml"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-qc/t1_line_55
        required: true
    outputs:
      - ca-qc/t1_line_55
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/net_income_signed
    capabilities: []
    """)


def signed(take_home_service: TakeHomeService, line_55: str, line_56: str | None) -> Decimal:
    starting = [Artifact(T1_LINE_55, D(line_55))]
    if line_56 is not None:
        starting.append(Artifact(SOCIAL_BENEFITS_REPAYMENT, D(line_56)))
    worksheets = take_home_service(HEADER, FORM, INPUTS, PART).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(NET_INCOME_SIGNED).value


@pytest.mark.parametrize(
    ("line_55", "expected"), [("19835.00", "19835.00"), ("69335.00", "69335.00")]
)
def test_signed_net_income_with_line_56_blank_is_line_55(
    take_home_service: TakeHomeService, line_55: str, expected: str
) -> None:
    assert signed(take_home_service, line_55, None) == D(expected)


def test_a_repayment_above_line_55_stays_negative(take_home_service: TakeHomeService) -> None:
    # No floor: Schedule 6 line 7 asks for the amount "if negative, show in brackets".
    assert signed(take_home_service, "1000.00", "5000") == D("-4000.00")
