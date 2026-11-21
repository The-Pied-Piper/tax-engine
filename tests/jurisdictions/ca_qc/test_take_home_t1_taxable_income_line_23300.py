"""5005-R (2025) line 54 (line 23300) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 54 and line 23300: Add lines 35 to 53." Lines 35 to 47 and 49 to 53 are blank for a salary-
only filer and not built, so the one part is line 48 (line 22215); the step is core/sum, rounded
through `ca-qc/cent_rounding`.

The part is the real one. The header, the form's export and the line 48 figure (a plain starting
input here) are made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_48, T1_LINE_54
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_23300.yaml"

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
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-QC"), 2025, Artifact(T1_LINE_48, D(line_48))
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    assert sheet.get(T1_LINE_54).value == D(expected)
