"""5005-R (2025) line 55 (line 23400) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 34: Enter the amount from line 33 of the previous page." and "Line 55 and line 23400: Line 34
minus line 54 (if negative, show in brackets) Net income before adjustments =". Line 34 is a copy
of line 33 and has no step; the step is core/subtract of line 54 from line 33 with no floor,
rounded through `ca-qc/cent_rounding`.

The part is the real one. The header, the form's export and the line 33 and line 54 figures (plain
starting inputs here) are made up."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_54, T1_LINE_55, TOTAL_INCOME
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_23400.yaml"

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca-qc/total_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/t1_line_55
    inputs:
      - name: ca-qc/total_income
        required: true
      - name: ca-qc/t1_line_54
        required: true
    capabilities: []
    """)


def line_55(take_home_service: TakeHomeService, line_33: str, line_54: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(TOTAL_INCOME, D(line_33)),
        Artifact(T1_LINE_54, D(line_54)),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(T1_LINE_55).value


@pytest.mark.parametrize(
    ("line_33", "line_54", "expected"),
    [
        ("20000", "165.00", "19835.00"),
        ("70000", "665.00", "69335.00"),
        ("200000", "1074.00", "198926.00"),
    ],
)
def test_line_55_is_line_33_less_line_54(
    take_home_service: TakeHomeService, line_33: str, line_54: str, expected: str
) -> None:
    assert line_55(take_home_service, line_33, line_54) == D(expected)


def test_line_55_is_not_floored(take_home_service: TakeHomeService) -> None:
    # The form prints "if negative, show in brackets": a loss stays negative.
    assert line_55(take_home_service, "-100", "665.00") == D("-765.00")
