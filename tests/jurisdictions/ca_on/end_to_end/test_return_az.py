"""CA-ON 2025 end to end: return az."""

from __future__ import annotations

from tax_calculator.jurisdictions.ca.catalog import (
    BASIC_PERSONAL_AMOUNT,
    CREDIT_AMOUNTS_SUBTOTAL,
    DISABILITY_AMOUNT_FOR_SELF,
    DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE,
    DISABILITY_SELF_BASE_AMOUNT,
    DISABILITY_SELF_CARE_OVER_THRESHOLD,
    DISABILITY_SELF_CARE_THRESHOLD,
    DISABILITY_SELF_SUPPLEMENT,
    DISABILITY_SELF_SUPPLEMENT_MAXIMUM,
    DISABILITY_SELF_WORKSHEET_AMOUNT,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, step_3


def test_return_az_under_18_qualifying_claims_line_7_of_the_worksheet_14516() -> None:
    # Return AZ: the expenses 5000.00 less the threshold 3464.00 is 1536.00 (line 5); the
    # supplement 5914.00 less 1536.00 is 4378.00 (line 6); the base 10138.00 plus 4378.00 is
    # 14516.00 (line 7), below the maximum 16052.00, so line 31600 is 14516.00.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(DISABILITY_SELF_BASE_AMOUNT).value == D("10138.00")
    assert worksheet.get(DISABILITY_SELF_SUPPLEMENT_MAXIMUM).value == D("5914.00")
    assert worksheet.get(DISABILITY_SELF_CARE_THRESHOLD).value == D("3464.00")
    assert worksheet.get(DISABILITY_SELF_CARE_OVER_THRESHOLD).value == D("1536.00")
    assert worksheet.get(DISABILITY_SELF_SUPPLEMENT).value == D("4378.00")
    assert worksheet.get(DISABILITY_SELF_WORKSHEET_AMOUNT).value == D("14516.00")
    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE).value == D("14516.00")
    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF).value == D("14516.00")


def test_return_az_is_in_the_credit_amounts_with_the_basic_personal_amount() -> None:
    # T1 line 101 and line 33500: the basic personal amount 16129.00 plus the disability amount
    # 14516.00 is 30645.00, and nothing else is claimed.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(BASIC_PERSONAL_AMOUNT).value == D("16129.00")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("30645.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("30645.00")


def test_return_az_18_or_older_who_qualifies_claims_the_10138_amount() -> None:
    # Line 31600 "enter $10,138 on line 31600 of your return" for a filer 18 or older on December
    # 31, 2025: the worksheet is not used.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE).value == D("10138.00")
    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF).value == D("10138.00")


def test_return_az_who_does_not_qualify_claims_nothing() -> None:
    # "If you qualify for the disability amount": without the approved Form T2201 the line is 0.
    worksheet = step_3(
        eligible_for_disability_amount=0,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF).value == D("0")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("16129.00")


def test_return_az_with_expenses_under_the_threshold_claims_the_maximum_supplement() -> None:
    # Expenses 3000.00 are under the threshold 3464.00, so line 5 is 0 and line 6 is the maximum
    # supplement 5914.00; line 7 is 10138.00 + 5914.00 = 16052.00, the maximum.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="3000.00",
    )

    assert worksheet.get(DISABILITY_SELF_CARE_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(DISABILITY_SELF_SUPPLEMENT).value == D("5914.00")
    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF).value == D("16052.00")


def test_return_az_supplement_is_kept_at_zero_when_expenses_exceed_the_maximum() -> None:
    # Expenses 20000.00: line 5 is 16536.00, over the maximum supplement, so line 6 is 0 and line 7
    # is the base amount 10138.00 alone.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="20000.00",
    )

    assert worksheet.get(DISABILITY_SELF_CARE_OVER_THRESHOLD).value == D("16536.00")
    assert worksheet.get(DISABILITY_SELF_SUPPLEMENT).value == D("0")
    assert worksheet.get(DISABILITY_AMOUNT_FOR_SELF).value == D("10138.00")


def test_return_az_ontario_under_18_qualifying_claims_line_58440_of_14823() -> None:
    # Worksheet ON428 line 58440: the expenses 5000.00 less the threshold 3518.00 is 1482.00
    # (line 5); the maximum amount 6007.00 less 1482.00 is 4525.00 (line 6); the base 10298.00 plus
    # 4525.00 is 14823.00 (line 7), below the maximum 16305.00.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(ontario.DISABILITY_SELF_BASE_AMOUNT).value == D("10298.00")
    assert worksheet.get(ontario.DISABILITY_SELF_SUPPLEMENT_MAXIMUM).value == D("6007.00")
    assert worksheet.get(ontario.DISABILITY_SELF_CARE_THRESHOLD).value == D("3518.00")
    assert worksheet.get(ontario.DISABILITY_SELF_CARE_OVER_THRESHOLD).value == D("1482.00")
    assert worksheet.get(ontario.DISABILITY_SELF_SUPPLEMENT).value == D("4525.00")
    assert worksheet.get(ontario.DISABILITY_SELF_WORKSHEET_AMOUNT).value == D("14823.00")
    assert worksheet.get(ontario.DISABILITY_AMOUNT_FOR_SELF).value == D("14823.00")


def test_return_az_ontario_18_or_older_who_qualifies_claims_the_10298_amount() -> None:
    # ON428 line 29 "claim $10,298" for a filer 18 or older on December 31, 2025.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(ontario.DISABILITY_AMOUNT_FOR_SELF).value == D("10298.00")


def test_return_az_ontario_credit_amounts_include_the_disability_amount() -> None:
    # ON428 line 31 and line 44: the Ontario basic personal amount 12747.00 plus the disability
    # amount 14823.00 is 27570.00, and nothing else is claimed.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(ontario.BASIC_PERSONAL_AMOUNT).value == D("12747.00")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER).value == D("27570.00")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("27570.00")


def test_return_az_ontario_who_does_not_qualify_claims_nothing() -> None:
    worksheet = step_3(
        eligible_for_disability_amount=0,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="5000.00",
    )

    assert worksheet.get(ontario.DISABILITY_AMOUNT_FOR_SELF).value == D("0")


def test_return_az_ontario_expenses_under_the_threshold_claim_the_maximum_16305() -> None:
    # Expenses 3000.00 are under the threshold 3518.00, so line 5 is 0 and line 6 is the maximum
    # amount 6007.00; line 7 is 10298.00 + 6007.00 = 16305.00.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="3000.00",
    )

    assert worksheet.get(ontario.DISABILITY_SELF_CARE_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(ontario.DISABILITY_SELF_SUPPLEMENT).value == D("6007.00")
    assert worksheet.get(ontario.DISABILITY_AMOUNT_FOR_SELF).value == D("16305.00")


def test_return_az_ontario_supplement_is_kept_at_zero_when_expenses_exceed_the_maximum() -> None:
    # Expenses 20000.00: line 5 is 16482.00, line 6 is 6007.00 - 16482.00 floored at 0.
    worksheet = step_3(
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        aged_18_or_older_at_end_of_2025=0,
        disability_self_care_expenses="20000.00",
    )

    assert worksheet.get(ontario.DISABILITY_SELF_SUPPLEMENT).value == D("0")
    assert worksheet.get(ontario.DISABILITY_AMOUNT_FOR_SELF).value == D("10298.00")
