"""ON428 (2025) line 36 with a limited attendant care claim, through the real engine from a salary.

Form text (CRA 5006-PC, section "Line 58689"): "If the amount you claimed for medical expenses on
your return includes an amount for attendant care expenses that was limited to $10,000 ($20,000 in
the year of death), the maximum Ontario claim for attendant care expenses is $17,627 ($35,253 in the
year of death)". A $70,000 salary has line 39 of 2,080.05 (see
`test_return_on428_medical_and_donations.py`). A claim of 30,000 with 20,000 of attendant care paid
and the federal claim limited rises by 17,627 less 10,000, 7,627, so line 36 is 37,627.00 and line
41 is 37,627.00 less 2,080.05, 35,546.95. The hand figures are asserted (not a CRA example).
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


def test_a_limited_attendant_care_claim_raises_line_36_and_line_41() -> None:
    kinds = bundled_kinds()
    given = [
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(on.ON428_MEDICAL_EXPENSES_LINE_36, D("30000")),
        Artifact(kinds.kind("ca-on/on428_attendant_care_expenses_line_36"), D("20000")),
        Artifact(kinds.kind("ca-on/on428_attendant_care_federal_limit_applied_line_36"), 1),
    ]
    (sheet,) = build_tax_computation().compute(JurisdictionCode("CA-ON"), 2025, *given)[
        "ca-on/on428"
    ]

    allowed = sheet.get(kinds.kind("ca-on/on428_medical_expenses_allowed_line_36")).value
    assert allowed == D("37627.00")
    assert sheet.get(on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41).value == D("35546.95")


def test_an_adapted_van_claim_is_raised_to_the_ontario_maximum() -> None:
    """RC4065 limits the federal van claim to $5,000 and Ontario to $8,813: a van paid at 10,000
    raises a claim of 20,000 by 8,813 less 5,000, 3,813, to 23,813.00,
    and line 41 to 23,813.00 less 2,080.05, 21,732.95."""
    kinds = bundled_kinds()
    given = [
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(on.ON428_MEDICAL_EXPENSES_LINE_36, D("20000")),
        Artifact(kinds.kind("ca-on/on428_adapted_van_expenses_line_36"), D("10000")),
    ]
    (sheet,) = build_tax_computation().compute(JurisdictionCode("CA-ON"), 2025, *given)[
        "ca-on/on428"
    ]

    allowed = sheet.get(kinds.kind("ca-on/on428_medical_expenses_allowed_line_36")).value
    assert allowed == D("23813.00")
    assert sheet.get(on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41).value == D("21732.95")
