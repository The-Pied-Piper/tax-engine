"""5005-R (2025) line 54 (line 23300) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 54 and line 23300: Add lines 35 to 53." Lines 35 to 47 and 49 to 53 are blank for a salary-
only filer and not built, so the parts are line 40 (line 21300, the UCCB repayment), line 48 (line
22215) and line 53 (line 23200, the RDSP income repayment), in that order; the step is core/sum,
rounded through `ca-qc/cent_rounding`. Lines 40 and 53 are the form's own steps, read as 0 when the
caller gives none.

The part is the real one. The header, the form's export and the line 48 figure (a plain starting
input here) are made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import RDSP_INCOME_REPAYMENT, UCCB_REPAYMENT
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_48, T1_LINE_54
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_23300.yaml"
REPAYMENT_PARTS = (
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
)

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
        - ca-qc/t1_line_54
    inputs:
      - name: ca-qc/t1_line_48
        required: true
    capabilities: []
    """)


@pytest.mark.parametrize(
    ("line_48", "expected"),
    [("165.00", "165.00"), ("665.00", "665.00"), ("1074.00", "1074.00"), ("0", "0.00")],
)
def test_line_54_is_line_48(
    take_home_service: TakeHomeService, line_48: str, expected: str
) -> None:
    worksheets = take_home_service(HEADER, FORM, *REPAYMENT_PARTS, PART).compute(
        TaxCalculationRequest(JurisdictionCode("CA-QC"), 2025, (Artifact(T1_LINE_48, D(line_48)),))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    assert sheet.get(T1_LINE_54).value == D(expected)


def test_line_54_adds_the_uccb_and_rdsp_repayments_to_line_48(
    take_home_service: TakeHomeService,
) -> None:
    # 40.10 (line 40, line 21300) + 665.00 (line 48) + 9.90 (line 53, line 23200).
    worksheets = take_home_service(HEADER, FORM, *REPAYMENT_PARTS, PART).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"),
            2025,
            (
                Artifact(T1_LINE_48, D("665.00")),
                Artifact(UCCB_REPAYMENT, D("40.10")),
                Artifact(RDSP_INCOME_REPAYMENT, D("9.90")),
            ),
        ),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    assert sheet.get(T1_LINE_54).value == D("715.00")
