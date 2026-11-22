"""5005-R (2025) line 48 (line 22215) as the Quebec manifest part wires it.

Form text (CRA 5005-R page 4, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt):
"Line 48 and line 22215: Deduction for CPP or QPP enhanced contributions on employment income
(complete Schedule 8 or Form RC381, whichever applies) (maximum $1,074.00)". The figure is Schedule
8 line 28, which the shared form exports as a record list of one amount; the step is one
core/record_total over it.

The real Schedule 8 is imported with the real Quebec dataset swap, so the figure comes from the
salary alone through the real engine. The header and the form's export are made up here. The
expected figures are hand-computed from the printed Schedule 8 lines (not a CRA example)."""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import T1_LINE_48
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import real_import

D = Decimal
PART = "t1_taxable_income_line_22215.yaml"
# The real Quebec T1 employment income parts: Schedule 8 line 1 reads line 10100 from that form.
T1_EMPLOYMENT_INCOME_PARTS = form_part_names("t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    imports:
    """) + real_import("ca/schedule_8")
FORM = dedent("""\
    form:
      name: ca-qc/t1_taxable_income
      required: true
      exports:
        - ca-qc/t1_line_48
    capabilities: []
    """)


def line_48(take_home_service: TakeHomeService, salary: str) -> Decimal:
    worksheets = take_home_service(HEADER, FORM, *T1_EMPLOYMENT_INCOME_PARTS, PART).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-QC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        ),
    )
    (sheet,) = worksheets["ca-qc/t1_taxable_income"]
    return sheet.get(T1_LINE_48).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # 1% of (20,000 - 3,500) is 165.00.
        ("20000", "165.00"),
        ("70000", "665.00"),
        # The printed maximum: 678.00 (line 12) + 396.00 (line 22) is 1,074.00.
        ("200000", "1074.00"),
        # Under the $3,500 exemption there is nothing to deduct.
        ("3500", "0.00"),
    ],
)
def test_line_48_is_the_schedule_8_deduction(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_48(take_home_service, salary) == D(expected)
