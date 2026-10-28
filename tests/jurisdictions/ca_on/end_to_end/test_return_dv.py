"""CA-ON 2025 end to end: return dv, an infirm eligible dependant under 18 who is not the filer's
child (Schedule 5 line 30400 and line 30425).

Return DV (`returns/2025_return_dv.yaml`) is the filer of Return DS with one infirm eligible
dependant under 18 at net income 20,000, who is not the filer's child. The supplement is in the
line 30400 calculation, and the Canada caregiver amount on line 30425 is for a dependant 18 or
older, so it is 0 here.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BASIC_PERSONAL_AMOUNT,
    CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
    DEPENDANT_CAREGIVER_AMOUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT,
    DEPENDANT_CAREGIVER_LIMIT,
    DEPENDANT_INFIRMITY_SUPPLEMENT,
    ELIGIBLE_DEPENDANT_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT_BASIS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_dv() -> Worksheet:
    """Return DV's worksheet: the filer with one infirm eligible dependant under 18 who is not the
    filer's child, at net income 20,000, with employment income of 60,000 and tax of 8,000
    deducted."""
    artifacts = starting(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_dependants=1,
        dependant_net_income="20000",
        income_tax_deducted="8000",
        dependant_caregiver_eligible=1,
        dependant_caregiver_aged_18_or_older=0,
    )
    return service().compute(CA_ON, 2025, *artifacts)["ca-on/return"][0]


def test_the_supplement_is_in_the_line_30400_basis_and_line_30400_is_0() -> None:
    # Line 3: 16,129 + 2,687 = 18,816; line 5: 18,816 - 20,000, negative, so 0.
    worksheet = return_dv()

    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(DEPENDANT_INFIRMITY_SUPPLEMENT).value == D("2687.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BASIS).value == D("18816.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")


def test_line_30425_is_0_for_a_dependant_under_18() -> None:
    # The amount before the age count is 8,601 (the infirm count is 1, the limit at most 8,601 with
    # 28,798 - 20,000 = 8,798 before it); the age count is 0, so the line 30425 amount is 0.
    worksheet = return_dv()

    assert worksheet.get(DEPENDANT_CAREGIVER_LIMIT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("0")
    assert worksheet.get(CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT).value == D("0")


def test_the_credit_amounts_have_the_2687_supplement_but_no_line_30425_amount() -> None:
    # Basic personal amount 16,129, Canada employment amount 1,471, CPP base 2,796.75 and EI 984.00,
    # with line 30400 and line 30425 at 0: 21,380.75.
    worksheet = return_dv()

    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("21380.75")


def test_return_dv_owes_676_79_at_total_payable_8676_79() -> None:
    # Federal tax 8,741.68 less 3,100.21 at 14.5% of 21,380.75 is 5,641.47; Ontario 3,035.32, the
    # same as Return DS; total payable 8,676.79 against 8,000.00 deducted: a balance owing.
    worksheet = return_dv()

    assert worksheet.get(TOTAL_PAYABLE).value == D("8676.79")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("676.79")
