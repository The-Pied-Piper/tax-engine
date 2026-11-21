"""ON428 (2025) line 36 with a category above its printed maximum, through the real engine from a
salary.

Form text (CRA 5006-PC, section "Line 58689"): "the maximum Ontario claim for attendant care
expenses is $17,627 ($35,253 in the year of death)". A $70,000 salary has line 39 of 2,080.05 (see
`test_return_on428_medical_and_donations.py`). A claim of 30,000 with 20,000 of attendant care is
reduced by 20,000 less 17,627, 2,373, so line 36 is 27,627.00 and line 41 is 27,627.00 less
2,080.05. The hand figures are asserted (not a CRA example).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on import catalog as on
from tests.kinds import bundled_kinds

D = Decimal


def test_attendant_care_above_its_maximum_reduces_line_36_and_line_41() -> None:
    kinds = bundled_kinds()
    given = [
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(on.ON428_MEDICAL_EXPENSES_LINE_36, D("30000")),
        Artifact(kinds.kind("ca-on/on428_attendant_care_expenses_line_36"), D("20000")),
    ]
    (sheet,) = build_tax_computation().compute(JurisdictionCode("CA-ON"), 2025, *given)[
        "ca-on/on428"
    ]

    allowed = sheet.get(kinds.kind("ca-on/on428_medical_expenses_allowed_line_36")).value
    assert allowed == D("27627.00")
    assert sheet.get(on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41).value == D("25546.95")
