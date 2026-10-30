"""CA-ON 2025 end to end: return at."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    CANADA_TRAINING_CREDIT,
    CANADA_TRAINING_CREDIT_BASIS,
    CANADA_TRAINING_CREDIT_MAXIMUM,
    CANADIAN_TUITION_AVAILABLE,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_SUBTOTAL,
    CURRENT_YEAR_TUITION_AVAILABLE,
    CURRENT_YEAR_TUITION_CLAIMED,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TUITION_AMOUNT,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    SPOUSE_ADJUSTED_TAXABLE_INCOME,
    SPOUSE_CREDITS_USED,
    SPOUSE_DESIGNATED_TUITION_CHECKED,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_RETURN_AGE_AMOUNT_CHECKED,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED,
    SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    SPOUSE_UNUSED_AMOUNTS,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    TOTAL_TUITION_AVAILABLE,
    TUITION_AVAILABLE_TO_TRANSFER,
    TUITION_CARRIED_FORWARD,
    TUITION_INCOME_BASE,
    TUITION_INCOME_LESS_CREDITS,
    TUITION_INCOME_REMAINING,
    TUITION_TRANSFER_LIMIT,
    TUITION_TRANSFERRED,
    UNUSED_FEDERAL_TUITION,
    UNUSED_TUITION_CLAIMED,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_at(**overrides: Any) -> Worksheet:
    """Return AT's inputs, as in `returns/2025_return_at.yaml`.

    The filer is a student with employment income of 40000 and income tax deducted of 5000. Their
    Canadian tuition fees are 6000, their foreign fees 1250, the unused tuition of the 2024 notice
    2000 and the Canada training credit limit and claim 1250; a tuition amount transferred from a
    child is 1500 and nothing is transferred to a designated individual. The spouse's age amount
    is 9028 and pension amount 2000, their taxable income 20000, their line 30000 16129 and their
    line 96 1500; the filer was not separated for 90 days or more including December 31, 2025.
    On their Form ON428 the spouse's line 58080 is 6223, line 58360 1762, line 8 1010.00, line
    58040 12747, line 24 1500 and line 58560 0 (Schedule ON(S2)).
    """
    inputs: dict[str, Any] = {
        "employment_income": "40000",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "income_tax_deducted": "5000",
        "canadian_tuition_fees": "6000",
        "canadian_tuition_institutions": 1,
        "canada_training_credit_limit": "1250",
        "canada_training_credit_claimed": "1250",
        "foreign_tuition_fees": "1250",
        "unused_tuition_from_2024": "2000",
        "tuition_transfer_elected": "0",
        "tuition_transferred_from_child": "1500",
        "tuition_transfer_students": 1,
        "spouse_return_age_amount": "9028",
        "spouse_return_pension_income_amount": "2000",
        "spouse_return_taxable_income": "20000",
        "spouse_return_basic_personal_amount": "16129",
        "spouse_return_line_96": "1500",
        "spouse_not_separated_90_days": 1,
        "spouse_return_ontario_age_amount": "6223",
        "spouse_return_ontario_pension_income_amount": "1762",
        "spouse_return_ontario_basic_tax": "1010.00",
        "spouse_return_ontario_basic_personal_amount": "12747",
        "spouse_return_ontario_line_24": "1500",
    }
    return compute(**{**inputs, **overrides})


def test_the_students_federal_tuition_amount_is_8000_and_the_training_credit_1250() -> None:
    # Schedule 11. Line 1 is 6000 and line 2 is 6000 x 50% = 3000.00; with a limit (line 3) of
    # 1250, line 4 is 1250.00 and the credit claimed, an election of 1250 at most line 4, is
    # 1250.00 (line 5, line 45350). Line 6 is 6000 - 1250.00 = 4750.00, line 8 is 4750.00 + 1250
    # of foreign fees = 6000.00 and line 10 is 6000.00 + 2000 unused from 2024 = 8000.00. Taxable
    # income 39635.00 is under 57375, so line 11 is 39635.00; line 12 is T1 line 101, 20062.75
    # (16129.00 + 1806.75 + 656.00 + 1471.00); line 13 is 19572.25. Line 14 is the lesser of
    # 2000 and 19572.25: 2000.00; line 15 is 17572.25; line 16 is the lesser of 6000.00 and
    # 17572.25: 6000.00; line 17 and line 32300 is 2000.00 + 6000.00 = 8000.00.
    worksheet = return_at()

    assert worksheet.get(CANADA_TRAINING_CREDIT_BASIS).value == D("3000.00")
    assert worksheet.get(CANADA_TRAINING_CREDIT_MAXIMUM).value == D("1250.00")
    assert worksheet.get(CANADA_TRAINING_CREDIT).value == D("1250.00")
    assert worksheet.get(CANADIAN_TUITION_AVAILABLE).value == D("4750.00")
    assert worksheet.get(CURRENT_YEAR_TUITION_AVAILABLE).value == D("6000.00")
    assert worksheet.get(TOTAL_TUITION_AVAILABLE).value == D("8000.00")
    assert worksheet.get(TUITION_INCOME_BASE).value == D("39635.00")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("20062.75")
    assert worksheet.get(TUITION_INCOME_LESS_CREDITS).value == D("19572.25")
    assert worksheet.get(UNUSED_TUITION_CLAIMED).value == D("2000.00")
    assert worksheet.get(TUITION_INCOME_REMAINING).value == D("17572.25")
    assert worksheet.get(CURRENT_YEAR_TUITION_CLAIMED).value == D("6000.00")
    assert worksheet.get(FEDERAL_TUITION_AMOUNT).value == D("8000.00")


def test_nothing_is_left_to_transfer_or_carry_forward_when_the_whole_amount_is_claimed() -> None:
    # Line 20 is 8000.00 - 8000.00 = 0.00; line 21 is line 8 (6000.00) at most 5000: 5000.00;
    # line 23 is 5000.00 - 6000.00, not below zero: 0.00; the election on line 24 is 0 and line
    # 25 is 0.00 - 0 = 0.00.
    worksheet = return_at()

    assert worksheet.get(UNUSED_FEDERAL_TUITION).value == D("0.00")
    assert worksheet.get(TUITION_TRANSFER_LIMIT).value == D("5000.00")
    assert worksheet.get(TUITION_AVAILABLE_TO_TRANSFER).value == D("0.00")
    assert worksheet.get(TUITION_TRANSFERRED).value == D("0")
    assert worksheet.get(TUITION_CARRIED_FORWARD).value == D("0.00")


def test_the_spouses_unused_amounts_are_8657_on_line_32600() -> None:
    # Schedule 2. Line 6 is 9028 + 0 + 2000 + 0 + 0 = 11028.00; their taxable income of 20000 is
    # under 57375, so line 7 is 20000.00; line 11 is 16129 + 1500 + 0 = 17629.00; line 12 is
    # 20000.00 - 17629.00 = 2371.00 and line 13 is 11028.00 - 2371.00 = 8657.00; not separated,
    # line 32600 is 8657.00.
    worksheet = return_at()

    assert worksheet.get(SPOUSE_TRANSFERABLE_AMOUNTS).value == D("11028.00")
    assert worksheet.get(SPOUSE_INCOME_FOR_TRANSFER).value == D("20000.00")
    assert worksheet.get(SPOUSE_CREDITS_USED).value == D("17629.00")
    assert worksheet.get(SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("2371.00")
    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D("8657.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8657.00")


def test_lines_32300_32400_and_32600_are_added_into_line_33500() -> None:
    # Line 33500 is 20062.75 (T1 line 101) + 8000.00 (32300) + 1500 (32400) + 8657.00 (32600) =
    # 38219.75, and line 33800 is 38219.75 x 14.5% = 5541.86375, half-up to the cent: 5541.86.
    worksheet = return_at()

    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("38219.75")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("5541.86")


def test_line_45350_is_added_into_the_total_credits_on_line_48200() -> None:
    # The federal tax after credits is 5747.08 - 5541.86 = 205.22; with the Ontario tax of
    # 1052.51 (see the Schedule ON(S2) test) the total payable is 1257.73. Line 48200 is the 5000
    # of income tax deducted plus 1250.00 on line 45350: 6250.00, so line 167 is 1257.73 -
    # 6250.00 = -4992.27, a refund.
    worksheet = return_at()

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("205.22")
    assert worksheet.get(TOTAL_PAYABLE).value == D("1257.73")
    assert worksheet.get(TOTAL_CREDITS).value == D("6250.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-4992.27")
    assert worksheet.get(REFUND).value == D("4992.27")


@pytest.mark.parametrize(("not_separated", "line_32600"), [(1, "8657.00"), (0, "0")])
def test_the_count_is_1_when_not_separated_and_0_when_separated(
    not_separated: int, line_32600: str
) -> None:
    # Schedule 2: a filer separated for 90 days or more including December 31, 2025 can have
    # nothing transferred: line 13 (8657.00) is counted once for a count of 1 and not at all for 0.
    worksheet = return_at(spouse_not_separated_90_days=not_separated)

    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D("8657.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D(line_32600)


def test_a_spouse_separated_for_90_days_transfers_nothing_on_line_32600() -> None:
    # The count is 0 for a filer separated for 90 days or more including December 31, 2025:
    # Schedule 2 line 13 is still 8657.00 but line 32600 is 8657.00 x 0 = 0, so line 33500 is
    # 20062.75 + 8000.00 + 1500 = 29562.75, line 33800 is 29562.75 x 14.5% = 4286.59875, half-up:
    # 4286.60, the federal tax after credits 5747.08 - 4286.60 = 1460.48, the Ontario line 58640
    # is 0 as well (the same count), so the Ontario tax is 1165.23, the total payable is
    # 1460.48 + 1165.23 = 2625.71 and line 167 is 2625.71 - 6250.00 = -3624.29.
    worksheet = return_at(spouse_not_separated_90_days=0)

    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D("8657.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("29562.75")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("4286.60")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("1460.48")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-3624.29")


@pytest.mark.parametrize(
    ("taxable_income", "line_12", "line_13"),
    [
        # Line 12 is line 7 less 17629.00; line 13 is 11028.00 less line 12, not below zero.
        ("20000", "2371.00", "8657.00"),
        ("22000", "4371.00", "6657.00"),
        ("28657", "11028.00", "0.00"),
        # Line 12 would be 12371.00, more than line 6: line 13 is 0, not negative.
        ("30000", "12371.00", "0.00"),
        # Their taxable income is under their credits: line 12 is 0, not negative.
        ("10000", "0.00", "11028.00"),
    ],
)
def test_the_spouses_taxable_income_reduces_what_they_can_transfer(
    taxable_income: str, line_12: str, line_13: str
) -> None:
    worksheet = return_at(spouse_return_taxable_income=taxable_income)

    assert worksheet.get(SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D(line_12)
    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D(line_13)
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D(line_13)


def test_a_spouse_with_taxable_income_over_57375_uses_their_tax_divided_by_14_5_percent() -> None:
    # Schedule 2 line 7: their line 76 of 11000 divided by 14.5% = 75862.0689..., half-up to the
    # cent: 75862.07; line 12 is 75862.07 - 17629.00 = 58233.07, more than line 6, so line 13
    # and line 32600 are 0.
    worksheet = return_at(
        spouse_return_taxable_income="70000", spouse_return_federal_basic_tax="11000"
    )

    assert worksheet.get(SPOUSE_INCOME_FOR_TRANSFER).value == D("75862.07")
    assert worksheet.get(SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("58233.07")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")


def test_a_student_with_taxable_income_over_57375_uses_the_tax_divided_by_14_5_percent() -> None:
    # Employment income of 80000: net income and taxable income 78974.00, over 57375, so line 11
    # is the federal tax (line 76), 12747.18, divided by 14.5% = 87911.5862..., half-up to the
    # cent: 87911.59. Line 12 is T1 line 101, 22033.58 (16129.00 + 3356.10 + 1077.48 + 1471.00),
    # and line 13 is 87911.59 - 22033.58 = 65878.01. Lines 14 and 16 are the 2000 and 6000, so
    # line 32300 is 8000.00 as before.
    worksheet = return_at(employment_income="80000")

    assert worksheet.get(TUITION_INCOME_BASE).value == D("87911.59")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("22033.58")
    assert worksheet.get(TUITION_INCOME_LESS_CREDITS).value == D("65878.01")
    assert worksheet.get(FEDERAL_TUITION_AMOUNT).value == D("8000.00")


def test_a_low_income_leaves_tuition_to_transfer_and_to_carry_forward() -> None:
    # Employment income of 20000, no Canada training credit and no foreign fees: taxable income
    # 19835.00 (line 11), T1 line 101 18744.75 (16129.00 + 816.75 + 328.00 + 1471.00), so line 13
    # is 1090.25. Line 8 is 6000.00 and line 10 is 8000.00. Line 14 is the lesser of 2000 and
    # 1090.25: 1090.25; line 15 is 0.00; line 16 is 0.00; line 17 and line 32300 is 1090.25.
    # Line 20 is 8000.00 - 1090.25 = 6909.75; line 21 is 5000.00; line 23 is 5000.00 - 0.00 =
    # 5000.00; of that 3000 is transferred (line 24, line 32700), and line 25 is 6909.75 - 3000 =
    # 3909.75 to carry forward.
    worksheet = return_at(
        employment_income="20000",
        canada_training_credit_claimed="0",
        foreign_tuition_fees="0",
        tuition_transfer_elected="3000",
    )

    assert worksheet.get(CANADA_TRAINING_CREDIT).value == D("0")
    assert worksheet.get(CANADIAN_TUITION_AVAILABLE).value == D("6000.00")
    assert worksheet.get(TOTAL_TUITION_AVAILABLE).value == D("8000.00")
    assert worksheet.get(TUITION_INCOME_BASE).value == D("19835.00")
    assert worksheet.get(CREDIT_AMOUNTS_SUBTOTAL).value == D("18744.75")
    assert worksheet.get(TUITION_INCOME_LESS_CREDITS).value == D("1090.25")
    assert worksheet.get(UNUSED_TUITION_CLAIMED).value == D("1090.25")
    assert worksheet.get(TUITION_INCOME_REMAINING).value == D("0.00")
    assert worksheet.get(CURRENT_YEAR_TUITION_CLAIMED).value == D("0.00")
    assert worksheet.get(FEDERAL_TUITION_AMOUNT).value == D("1090.25")
    assert worksheet.get(UNUSED_FEDERAL_TUITION).value == D("6909.75")
    assert worksheet.get(TUITION_TRANSFER_LIMIT).value == D("5000.00")
    assert worksheet.get(TUITION_AVAILABLE_TO_TRANSFER).value == D("5000.00")
    assert worksheet.get(TUITION_TRANSFERRED).value == D("3000")
    assert worksheet.get(TUITION_CARRIED_FORWARD).value == D("3909.75")


def test_a_transfer_over_line_23_is_refused() -> None:
    # Line 24 "cannot be more than the amount on line 23": line 23 is 5000.00 here, and 5000.01 is
    # an input above its bound.
    changes = {
        "employment_income": "20000",
        "canada_training_credit_claimed": "0",
        "foreign_tuition_fees": "0",
    }

    assert return_at(**changes, tuition_transfer_elected="5000").get(
        TUITION_TRANSFERRED
    ).value == D("5000")
    with pytest.raises(InputAboveBoundError, match="ca/tuition_transfer_elected"):
        return_at(**changes, tuition_transfer_elected="5000.01")


def test_a_training_credit_over_line_4_is_refused() -> None:
    # Line 5 "cannot be more than the amount on line 4": line 4 is 1250.00 here, and 1250.01 is an
    # input above its bound.
    with pytest.raises(InputAboveBoundError, match="ca/canada_training_credit_claimed"):
        return_at(canada_training_credit_claimed="1250.01")


def test_a_spouse_age_amount_of_9028_is_accepted_as_it_is() -> None:
    # Schedule 2 line 1 "Enter the amount from line 30100 of their return.", their line 30100 at
    # its printed maximum of $9,028 (T1 line 78 "(maximum $9,028)"): the checked amount is 9028,
    # and line 6 and line 13 are as before, so line 32600 is still 8657.00.
    worksheet = return_at(spouse_return_age_amount="9028")

    assert worksheet.get(SPOUSE_RETURN_AGE_AMOUNT_CHECKED).value == D("9028")
    assert worksheet.get(SPOUSE_TRANSFERABLE_AMOUNTS).value == D("11028.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8657.00")


def test_a_spouse_pension_amount_of_2000_is_accepted_as_it_is() -> None:
    # Schedule 2 line 3 "Enter the amount from line 31400 of their return. (maximum $2,000)", their
    # line 31400 at its printed maximum of $2,000 (T1 line 97): the checked amount is 2000, and
    # line 32600 is 8657.00 as before.
    worksheet = return_at(spouse_return_pension_income_amount="2000")

    assert worksheet.get(SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED).value == D("2000")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8657.00")


@pytest.mark.parametrize(
    ("field", "amount", "maximum"),
    [
        # One cent above the printed maximum, and the $30,000 and $9,000 of the example: refused,
        # not capped, so the amount is not carried into line 6.
        ("spouse_return_age_amount", "9028.01", "9028.00"),
        ("spouse_return_age_amount", "30000", "9028.00"),
        ("spouse_return_pension_income_amount", "2000.01", "2000.00"),
        ("spouse_return_pension_income_amount", "9000", "2000.00"),
        ("spouse_return_basic_personal_amount", "16129.01", "16129.00"),
        ("spouse_return_basic_personal_amount", "40000", "16129.00"),
        ("spouse_designated_tuition", "5000.01", "5000.00"),
        ("spouse_designated_tuition", "8000", "5000.00"),
        # Schedule 2 line 4 and their line 31600 "(maximum $16,052)": refused, not capped.
        ("spouse_return_disability_amount", "16053", "16052.00"),
        ("spouse_return_disability_amount", "20000", "16052.00"),
    ],
)
def test_a_spouse_amount_above_its_printed_maximum_is_refused(
    field: str, amount: str, maximum: str
) -> None:
    # Schedule 2 line 1, line 3 and line 8 copy the T1 lines that print "maximum $9,028", "maximum
    # $2,000" and "(maximum $16,129)". Schedule 2 line 5 is bounded by Note 2, "The maximum tuition
    # amount your spouse or common-law partner can transfer to you is $5,000 minus the current year
    # amounts they use". Schedule 2 line 4 is bounded by their line 31600, "(maximum $16,052)" on
    # Federal Worksheet 5000-D1 line 7. Above the maximum is an input error, as a line 23 tuition
    # transfer is.
    message = f"ca/{field} {amount} is above ca/{field}_maximum {maximum}"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_at(**{field: amount})


def test_a_spouse_basic_personal_amount_of_16129_is_accepted_as_it_is() -> None:
    # Schedule 2 line 8 "Amount from line 30000 of their return.", their line 30000 at its printed
    # maximum of $16,129 (T1 line 30000 "(maximum $16,129)"): the checked amount is 16129, and
    # line 32600 is 8657.00 as before.
    worksheet = return_at(spouse_return_basic_personal_amount="16129")

    assert worksheet.get(SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED).value == D("16129")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8657.00")


def test_a_spouse_designated_tuition_of_5000_is_accepted_as_it_is() -> None:
    # Schedule 2 line 5 "Enter the federal amount designated to you from their forms T2202, TL11A,
    # or TL11C. (Note 2)", $5,000 at the maximum of Note 2 "$5,000 minus the current year amounts
    # they use": the checked amount is 5000. A tuition amount of 0 is accepted by the defaults.
    worksheet = return_at(spouse_designated_tuition="5000")

    assert worksheet.get(SPOUSE_DESIGNATED_TUITION_CHECKED).value == D("5000")


def test_a_spouse_disability_amount_of_16052_is_accepted_as_it_is() -> None:
    # Schedule 2 line 4 "Enter the amount from line 31600 of their return. (Note 1)", their line
    # 31600 at its printed maximum of $16,052 (Federal Worksheet 5000-D1 line 7): the checked
    # amount is 16052.
    worksheet = return_at(spouse_return_disability_amount="16052")

    assert worksheet.get(SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED).value == D("16052")


def test_a_training_credit_below_line_4_leaves_more_tuition() -> None:
    # Claiming only 250 of the 1250: line 6 is 6000 - 250.00 = 5750.00 and line 8 is 5750.00 +
    # 1250 = 7000.00. Line 21 is 7000.00 at most 5000: 5000.00; line 16 is 7000.00 (line 15 is
    # 17572.25), so line 23 is 5000.00 - 7000.00, not below zero: 0.00.
    worksheet = return_at(canada_training_credit_claimed="250")

    assert worksheet.get(CANADA_TRAINING_CREDIT).value == D("250")
    assert worksheet.get(CANADIAN_TUITION_AVAILABLE).value == D("5750.00")
    assert worksheet.get(CURRENT_YEAR_TUITION_AVAILABLE).value == D("7000.00")
    assert worksheet.get(TUITION_TRANSFER_LIMIT).value == D("5000.00")
    assert worksheet.get(TUITION_AVAILABLE_TO_TRANSFER).value == D("0.00")


def test_the_ontario_spouse_amounts_are_2232_on_line_58640() -> None:
    # Schedule ON(S2). Line 4 is 6223 + 1762 + 0 = 7985.00; their taxable income of 20000 is
    # under 52886, so line 5 is 20000.00 (their line 8, 1010.00, is not used); line 9 is 12747 +
    # 1500 + 0 = 14247.00; line 10 is 20000.00 - 14247.00 = 5753.00 and line 11 is 7985.00 -
    # 5753.00 = 2232.00; not separated, ON428 line 34 and line 58640 is 2232.00.
    worksheet = return_at()

    assert worksheet.get(ontario.SPOUSE_TRANSFERABLE_AMOUNTS).value == D("7985.00")
    assert worksheet.get(ontario.SPOUSE_INCOME_FOR_TRANSFER).value == D("20000.00")
    assert worksheet.get(ontario.SPOUSE_CREDITS_USED).value == D("14247.00")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("5753.00")
    assert worksheet.get(ontario.SPOUSE_UNUSED_AMOUNTS).value == D("2232.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("2232.00")


def test_line_58640_is_added_into_the_ontario_credit_amounts_on_line_44() -> None:
    # ON428 line 44 (line 58800) is 12747 + 1806.75 + 656.00 + 2232.00 = 17441.75, and line 46
    # (line 58840) is 17441.75 x 5.05% = 880.808375, half-up to the cent: 880.81; the Ontario tax
    # after credits is 2001.57 - 880.81 = 1120.76. The LIFT credit 518.25 and the health premium
    # 450 give an Ontario tax of 1120.76 - 518.25 + 450 = 1052.51, so line 167 above is 205.22 +
    # 1052.51 = 1257.73 less 6250.00.
    worksheet = return_at()

    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("17441.75")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("880.81")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("1120.76")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("1120.76")


def test_the_federal_count_also_zeroes_line_58640_for_a_separated_spouse() -> None:
    # The one count (ca/spouse_not_separated_90_days) is 0 for a filer separated for 90 days or
    # more including December 31, 2025: Schedule ON(S2) line 11 is still 2232.00 but line 58640 is
    # 2232.00 x 0 = 0, so ON428 line 44 is 12747 + 1806.75 + 656.00 = 15209.75, line 46 is
    # 15209.75 x 5.05% = 768.088..., half-up: 768.09, and the Ontario tax after credits is
    # 2001.57 - 768.09 = 1233.48.
    worksheet = return_at(spouse_not_separated_90_days=0)

    assert worksheet.get(ontario.SPOUSE_UNUSED_AMOUNTS).value == D("2232.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15209.75")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("768.09")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("1233.48")


@pytest.mark.parametrize(
    ("taxable_income", "line_10", "line_11"),
    [
        # Line 10 is line 5 less 14247.00; line 11 is 7985.00 less line 10, not below zero.
        ("20000", "5753.00", "2232.00"),
        ("22000", "7753.00", "232.00"),
        ("22232", "7985.00", "0.00"),
        # Line 10 would be 15753.00, more than line 4: line 11 is 0, not negative.
        ("30000", "15753.00", "0.00"),
        # Their taxable income is under their credits: line 10 is 0, not negative.
        ("10000", "0.00", "7985.00"),
    ],
)
def test_the_spouses_taxable_income_reduces_what_they_can_transfer_in_ontario(
    taxable_income: str, line_10: str, line_11: str
) -> None:
    # The same spouse taxable income (their line 26000) feeds line 5 and, on the federal
    # Schedule 2, line 7.
    worksheet = return_at(spouse_return_taxable_income=taxable_income)

    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D(line_10)
    assert worksheet.get(ontario.SPOUSE_UNUSED_AMOUNTS).value == D(line_11)
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D(line_11)


def test_a_spouse_with_taxable_income_over_52886_uses_their_ontario_tax_over_5_05_percent() -> None:
    # Schedule ON(S2) line 5: their line 8 of 3500.00 divided by 5.05% = 69306.9306..., half-up to
    # the cent: 69306.93 (their line 26000, 60000, is not used); line 10 is 69306.93 - 14247.00 =
    # 55059.93, more than line 4 (7985.00), so line 11 and line 58640 are 0.
    worksheet = return_at(
        spouse_return_taxable_income="60000", spouse_return_ontario_basic_tax="3500.00"
    )

    assert worksheet.get(ontario.SPOUSE_INCOME_FOR_TRANSFER).value == D("69306.93")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("55059.93")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")


def test_the_spouses_taxable_income_at_52886_is_used_as_it_is() -> None:
    # "$52,886 or less": at the threshold their line 26000 passes through, so line 5 is 52886.00
    # whatever their line 8 is, and line 10 is 52886.00 - 14247.00 = 38639.00.
    worksheet = return_at(
        spouse_return_taxable_income="52886", spouse_return_ontario_basic_tax="9999.00"
    )

    assert worksheet.get(ontario.SPOUSE_INCOME_FOR_TRANSFER).value == D("52886.00")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("38639.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("0")


def test_the_spouses_disability_and_unused_tuition_change_lines_4_and_9() -> None:
    # Their line 58440 of 4000 makes line 4 6223 + 1762 + 4000 = 11985.00; their line 58560 of
    # 2000 makes line 9 12747 + 1500 + 2000 = 16247.00, so line 10 is 20000.00 - 16247.00 =
    # 3753.00 and line 11 is 11985.00 - 3753.00 = 8232.00.
    worksheet = return_at(
        spouse_return_ontario_disability_amount="4000",
        spouse_return_ontario_unused_tuition_amount="2000",
    )

    assert worksheet.get(ontario.SPOUSE_TRANSFERABLE_AMOUNTS).value == D("11985.00")
    assert worksheet.get(ontario.SPOUSE_CREDITS_USED).value == D("16247.00")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("3753.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("8232.00")
