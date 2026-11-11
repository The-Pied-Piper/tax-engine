"""A title and a reference given to a manifest input reach the worksheet of every form reading it.

The inputs are test-local: one input with the printed title and reference of the salary line, read
by one form of one step.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_on.conftest import TakeHomeService

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    inputs:
      - name: ca/employment_income
        required: true
        title: Employment income
        reference: "10100"
    """)
FORM = dedent("""\
    form:
      name: ca/t1_tax_and_credits
      required: true
      exports:
        - ca/non_refundable_tax_credits
    capabilities:
      - name: core/sum
        params:
          rounding: ca/cent_rounding
        consumes:
          parts:
            - ca/employment_income
        produces:
          output: ca/non_refundable_tax_credits
    """)


def test_a_manifest_input_title_and_reference_reach_the_worksheet(
    take_home_service: TakeHomeService,
) -> None:
    worksheets = take_home_service(HEADER, FORM).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal("70000"))
    )

    (sheet,) = worksheets["ca/t1_tax_and_credits"]
    assert sheet.title(EMPLOYMENT_INCOME.label) == "Employment income"
    assert sheet.reference(EMPLOYMENT_INCOME.label) == "10100"
    assert sheet.title("no_such_label") is None
