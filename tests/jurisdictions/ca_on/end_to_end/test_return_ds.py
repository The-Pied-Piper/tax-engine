"""CA-ON 2025 end to end: return ds, an infirm eligible dependant 18 or older (Schedule 5).

Return DS (`returns/2025_return_ds.yaml`) is the one filer at dependant net income 20,000; these
tests take the same filer at the other net incomes of the acceptance criteria (10,000 and 25,000)
and with no infirmity, the lines of Schedule 5 line 30400 and line 30425 and the credit totals.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BASIC_PERSONAL_AMOUNT,
    CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
    DEPENDANT_CAREGIVER_AMOUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT,
    DEPENDANT_CAREGIVER_BEFORE_MAXIMUM,
    DEPENDANT_CAREGIVER_LIMIT,
    DEPENDANT_INFIRMITY_SUPPLEMENT,
    ELIGIBLE_DEPENDANT_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT_BASIS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND_OR_BALANCE_OWING,
    SPOUSE_CAREGIVER_AMOUNT,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_ds(dependant_net_income: str, infirm: int = 1, aged_18: int = 1) -> Worksheet:
    """Return DS's worksheet: the filer with one eligible dependant of this net income, who has an
    infirmity (1) or not (0) and is 18 or older (1) or under 18 (0), with employment income of
    60,000 and tax of 8,000 deducted."""
    artifacts = starting(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_dependants=1,
        dependant_net_income=dependant_net_income,
        income_tax_deducted="8000",
        dependant_caregiver_eligible=infirm,
        dependant_caregiver_aged_18_or_older=aged_18,
    )
    return service().compute(CA_ON, 2025, *artifacts)["ca-on/return"][0]


def test_an_infirm_dependant_with_net_income_10000_gives_line_30400_of_8816() -> None:
    # Line 3: 16,129 + 2,687 = 18,816; line 5: 18,816 - 10,000 = 8,816.
    worksheet = return_ds("10000")

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BASIS).value == D("18816.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("8816.00")


def test_at_net_income_10000_line_30425_is_0_as_line_30400_claims_all_of_the_limit() -> None:
    # Line 3: 28,798 - 10,000 = 18,798, at most 8,601; line 5: 8,601 - 8,816, negative, so 0.
    worksheet = return_ds("10000")

    assert worksheet.get(DEPENDANT_CAREGIVER_LIMIT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("0")


def test_at_net_income_20000_line_30400_is_0_and_line_30425_is_8601() -> None:
    # Line 3: 16,129 + 2,687 - 20,000 is negative, so line 30400 is 0; line 30425 line 3:
    # 28,798 - 20,000 = 8,798, the maximum 8,601; line 4 is the 0 claimed on line 30400.
    worksheet = return_ds("20000")

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(DEPENDANT_CAREGIVER_BEFORE_MAXIMUM).value == D("8798.00")
    assert worksheet.get(DEPENDANT_CAREGIVER_LIMIT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT).value == D("8601")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("8601")
    assert worksheet.get(CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT).value == D("8601")


def test_at_net_income_25000_line_30425_is_3798() -> None:
    # Line 3: 28,798 - 25,000 = 3,798, under the maximum of 8,601; line 4 is 0.
    worksheet = return_ds("25000")

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(DEPENDANT_CAREGIVER_LIMIT).value == D("3798")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("3798")


def test_without_an_infirmity_line_30400_is_as_today_and_line_30425_is_0() -> None:
    # Basic personal amount 16,129 less the net income of 10,000: 6,129, as before this change.
    worksheet = return_ds("10000", infirm=0)

    assert worksheet.get(DEPENDANT_INFIRMITY_SUPPLEMENT).value == D("0")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("6129")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("0")


def test_under_18_infirm_keeps_the_supplement_in_30400_and_gets_no_30425() -> None:
    # Line 3: 16,129 + 2,687 = 18,816; line 5: 18,816 - 10,000 = 8,816, the supplement included.
    # Line 30425 is for a dependant 18 or older, so the 8,816 claimed on line 30400 is not a
    # line 30425 amount: the caregiver amount for this dependant is 0.
    worksheet = return_ds("10000", aged_18=0)

    assert worksheet.get(DEPENDANT_INFIRMITY_SUPPLEMENT).value == D("2687")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("8816.00")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("0")


def test_a_dependant_18_or_older_without_an_infirmity_has_no_supplement_and_no_line_30425() -> None:
    worksheet = return_ds("10000", infirm=0, aged_18=1)

    assert worksheet.get(DEPENDANT_INFIRMITY_SUPPLEMENT).value == D("0")
    assert worksheet.get(DEPENDANT_CAREGIVER_AMOUNT).value == D("0")


def test_the_t1_total_credits_rise_by_the_2687_supplement_at_net_income_10000() -> None:
    infirm = return_ds("10000").get(NON_REFUNDABLE_CREDIT_AMOUNTS).value
    not_infirm = return_ds("10000", infirm=0).get(NON_REFUNDABLE_CREDIT_AMOUNTS).value

    assert infirm - not_infirm == D("2687")


def test_the_spouse_amount_for_the_caregiver_is_0_with_only_a_dependant() -> None:
    assert return_ds("20000").get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")


def test_return_ds_gives_a_refund_of_570_35_at_net_income_20000() -> None:
    # Total payable 4,394.33 federal and 3,035.32 Ontario, 7,429.65, against 8,000 deducted.
    worksheet = return_ds("20000")

    assert worksheet.get(TOTAL_PAYABLE).value == D("7429.65")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-570.35")


def test_the_supplement_is_the_basic_personal_amount_plus_2687_for_line_30400() -> None:
    worksheet = return_ds("10000")

    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BASIS).value - worksheet.get(
        BASIC_PERSONAL_AMOUNT
    ).value == D("2687")
