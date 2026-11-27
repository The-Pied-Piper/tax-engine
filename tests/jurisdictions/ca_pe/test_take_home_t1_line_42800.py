"""T1 line 42800 reads PE428 line 97 (Prince Edward Island tax), 2025.

Form text (Form PE428, CRA 5002-C): "Line 97: Line 93 minus line 96 (if negative, enter "0") Enter
this amount on line 42800 of your return. Prince Edward Island tax =". The form supplies line 97
as `ca/provincial_tax.amount`, the name the T1 form reads, so the T1's line 42800
(`ca/provincial_tax_line_42800`, line 147) is line 97 at every salary: 33.83 / 1,261.72 / 6,355.92
at $20,000 / $30,000 / $70,000. The test composes the real federal parts, the real PE428 parts and
the real form declaration with a test-local header and T1 declaration.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import ALL_PARTS, HEADER
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds

D = Decimal
T1 = "ca/t1_tax_and_credits"
LINE_42800 = "ca/provincial_tax_line_42800"
LINE_43500 = "ca/total_payable"
LINE_97 = "ca-pe/pe428_prince_edward_island_tax_line_97"
T1_PARTS = (
    *form_part_names("schedule_9", "t691"),
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
    "t1_tax_and_credits_line_107.yaml",
    "t1_tax_and_credits_line_108.yaml",
    "t1_tax_and_credits_line_109.yaml",
    "t1_tax_and_credits_line_110.yaml",
    "t1_tax_and_credits_line_111.yaml",
    "t1_tax_and_credits_line_33200.yaml",
    "t1_tax_and_credits_line_33500.yaml",
    "t1_tax_and_credits_line_33800.yaml",
    "t1_tax_and_credits_line_35000.yaml",
    "t1_tax_and_credits_line_125.yaml",
    "t1_tax_and_credits_line_40400.yaml",
    "t1_tax_and_credits_line_42900.yaml",
    "t1_tax_and_credits_line_128.yaml",
    "t1_tax_and_credits_line_40500_inputs.yaml",
    "t1_tax_and_credits_line_130.yaml",
    "t1_tax_and_credits_line_132.yaml",
    "t1_tax_and_credits_line_40600_inputs.yaml",
    "t1_tax_and_credits_line_40600.yaml",
    "t1_tax_and_credits_line_41600.yaml",
    "t1_tax_and_credits_line_41700.yaml",
    "t1_tax_and_credits_line_42000.yaml",
    "t1_tax_and_credits_line_43500.yaml",
)
T1_FORM = dedent(f"""\
    form:
      name: {T1}
      required: true
      exports:
        - {LINE_42800}
        - {LINE_43500}
    """)


@pytest.mark.parametrize(
    ("salary", "line_97"),
    [("20000", "33.83"), ("30000", "1261.72"), ("70000", "6355.92")],
)
def test_t1_line_42800_is_pe428_line_97(
    take_home_service: TakeHomeService, salary: str, line_97: str
) -> None:
    service = take_home_service(HEADER, T1_FORM, "pe428.yaml", *ALL_PARTS, *T1_PARTS)

    worksheets = service.compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-PE"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )

    (t1,) = worksheets[T1]
    (pe,) = worksheets["ca-pe/pe428"]
    assert pe.get(prince_edward_island_kinds().kind(LINE_97)).value == D(line_97)
    assert t1.get(prince_edward_island_kinds().kind(LINE_42800)).value == D(line_97)
