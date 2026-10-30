"""CA-ON 2025 end to end: return j."""

from __future__ import annotations

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AGE_AMOUNT,
    AGE_AMOUNT_BEFORE_COUNT,
    AGE_INCOME_OVER_THRESHOLD,
    AGE_INCOME_THRESHOLD,
    AGE_MAXIMUM,
    AGE_REDUCTION,
    BORN_IN_1960_OR_EARLIER,
    FEDERAL_TAX_AFTER_CREDITS,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND_OR_BALANCE_OWING,
    SPOUSE_AMOUNT,
    SPOUSE_AMOUNT_BASIS,
    SPOUSE_AMOUNT_BEFORE_COUNT,
    SPOUSE_CAREGIVER_AMOUNT,
    SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT,
    SPOUSE_CAREGIVER_BASE,
    SPOUSE_CAREGIVER_BEFORE_MAXIMUM,
    SPOUSE_CAREGIVER_ELIGIBLE,
    SPOUSE_CAREGIVER_LIMIT,
    SPOUSE_INFIRMITY_SUPPLEMENT,
    SPOUSE_NET_INCOME,
    SPOUSES_CLAIMED,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_j(
    born_in_1960_or_earlier: int = 1,
    spouse_net_income: str = "12000",
    spouses_claimed: int = 1,
    spouse_caregiver_eligible: int = 1,
) -> Worksheet:
    """Return J's inputs, as in `returns/2025_return_j.yaml`, with the age and spouse ones given."""
    return compute(
        "50000",
        (("930", "0", "0"),),
        "0",
        "0",
        "9000",
        "0",
        "0",
        born_in_1960_or_earlier=born_in_1960_or_earlier,
        spouse_net_income=spouse_net_income,
        spouses_claimed=spouses_claimed,
        spouse_caregiver_eligible=spouse_caregiver_eligible,
        income_tax_deducted="6000",
    )


def test_return_js_age_spouse_and_caregiver_amounts_come_off_net_income_and_the_spouses() -> None:
    # Return J: employment income of 50000 and a capital gain of 930, so total income is 50000 +
    # 465.00 = 50465.00 and, less the enhanced CPP contributions of 465.00, net income is
    # 50000.00. The filer was born in 1960 or earlier and the spouse, whose net income is 12000,
    # is infirm and eligible for the Canada caregiver amount (line 51090). Age amount (5000-D1):
    # 9028.00 - 15% x (50000.00 - 45522) = 9028.00 - 671.70 = 8356.30. Spouse amount (5000-S5):
    # (16129.00 + 2687) - 12000 = 6816.00. Canada caregiver amount for the spouse: 28798.00 -
    # 12000 = 16798.00, at most 8601, less the spouse amount 6816.00: 1785.00. Line 33500 is
    # 16129.00 + 8356.30 + 6816.00 + 0 + 1785.00 + 0 + 2301.75 + 820.00 + 1471 = 37679.05, and
    # line 35000 37679.05 x 14.5% = 5463.46225, rounded half-up to the cent: 5463.46.
    worksheet = return_j()

    assert worksheet.get(NET_INCOME).value == D("50000.00")
    assert worksheet.get(BORN_IN_1960_OR_EARLIER).value == 1
    assert worksheet.get(SPOUSE_NET_INCOME).value == D("12000")
    assert worksheet.get(SPOUSES_CLAIMED).value == 1
    assert worksheet.get(SPOUSE_CAREGIVER_ELIGIBLE).value == 1
    assert worksheet.get(AGE_MAXIMUM).value == D("9028.00")
    assert worksheet.get(AGE_INCOME_THRESHOLD).value == D("45522.00")
    assert worksheet.get(AGE_INCOME_OVER_THRESHOLD).value == D("4478.00")
    assert worksheet.get(AGE_REDUCTION).value == D("671.70")
    assert worksheet.get(AGE_AMOUNT_BEFORE_COUNT).value == D("8356.30")
    assert worksheet.get(AGE_AMOUNT).value == D("8356.30")
    assert worksheet.get(SPOUSE_INFIRMITY_SUPPLEMENT).value == D("2687")
    assert worksheet.get(SPOUSE_AMOUNT_BASIS).value == D("18816.00")
    assert worksheet.get(SPOUSE_AMOUNT_BEFORE_COUNT).value == D("6816.00")
    assert worksheet.get(SPOUSE_AMOUNT).value == D("6816.00")
    assert worksheet.get(SPOUSE_CAREGIVER_BASE).value == D("28798.00")
    assert worksheet.get(SPOUSE_CAREGIVER_BEFORE_MAXIMUM).value == D("16798.00")
    assert worksheet.get(SPOUSE_CAREGIVER_LIMIT).value == D("8601")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT).value == D("1785.00")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D("1785.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("37679.05")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("5463.46")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("1786.54")
    # Worksheet ON428 (form 5006-D), "Line 58080 - Age amount": line 1 6223.00, line 3 46330.00;
    # line 4 is 50000.00 - 46330.00 = 3670.00, line 6 15% of it, 550.50, and line 7 is 6223.00 -
    # 550.50 = 5672.50, claimed once. ON428 line 11 is 11905.00 and line 12 the spouse's net income,
    # 12000, so line 13 is 11905.00 - 12000, negative, so 0, at most 10823: 0.
    assert worksheet.get(ontario.AGE_MAXIMUM).value == D("6223.00")
    assert worksheet.get(ontario.AGE_INCOME_THRESHOLD).value == D("46330.00")
    assert worksheet.get(ontario.AGE_INCOME_OVER_THRESHOLD).value == D("3670.00")
    assert worksheet.get(ontario.AGE_REDUCTION).value == D("550.50")
    assert worksheet.get(ontario.AGE_AMOUNT_BEFORE_COUNT).value == D("5672.50")
    assert worksheet.get(ontario.AGE_AMOUNT).value == D("5672.50")
    assert worksheet.get(ontario.SPOUSE_BASE).value == D("11905.00")
    assert worksheet.get(ontario.SPOUSE_AMOUNT_BEFORE_MAXIMUM).value == D("0")
    assert worksheet.get(ontario.SPOUSE_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(ontario.SPOUSE_AMOUNT).value == D("0")
    # ON428 line 58800 is 12747 + 5672.50 + 0 + 0 + 2301.75 + 820.00 = 21541.25, and line 61500
    # 21541.25 x 5.05% = 1087.833125, rounded half-up to the cent: 1087.83.
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("21541.25")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("1087.83")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1437.17")
    assert worksheet.get(ONTARIO_TAX).value == D("2037.17")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3823.71")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2176.29")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    for line in (
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 50000 "
        "less age_income_threshold 45522, not below 0 = 4478",
        "age_reduction: 15% of age_income_over_threshold 4478 (half-up to 0.01)",
        "age_amount_before_count: age_maximum 9028 less age_reduction 671.7, not below 0 = 8356.3",
        "age_amount: age_amount_before_count 8356.3 for each of 1 born_in_1960_or_earlier_checked "
        "= 8356.3",
        "spouse_infirmity_supplement: 2687 for each of 1 spouse_caregiver_eligible_checked = 2687 "
        "(half-up to 0.01)",
        "spouse_amount_basis: basic_personal_amount 16129 + spouse_infirmity_supplement 2687 "
        "= 18816",
        "spouse_amount_before_count: spouse_amount_basis 18816 "
        "less spouse_net_income 12000, not below 0 = 6816",
        "spouse_amount: spouse_amount_before_count 6816 for each of 1 spouses_claimed_checked = "
        "6816",
        "spouse_caregiver_before_maximum: spouse_caregiver_base 28798 "
        "less spouse_net_income 12000, not below 0 = 16798",
        "spouse_caregiver_limit: lesser of spouse_caregiver_before_maximum 16798 and 8601 "
        "(half-up to 0.01)",
        "spouse_caregiver_amount_before_count: spouse_caregiver_limit 8601 "
        "less spouse_amount 6816, not below 0 = 1785",
        "spouse_caregiver_amount: spouse_caregiver_amount_before_count 1785 "
        "for each of 1 spouse_caregiver_eligible_checked = 1785",
        "non_refundable_credit_amounts: basic_personal_amount 16129 + age_amount 8356.3 "
        "+ spouse_amount 6816 + eligible_dependant_amount 0 "
        "+ caregiver_amount_for_spouse_or_dependant 1785 "
        "+ caregiver_amount 0 + infirm_children_amount 0 "
        "+ cpp_base_contributions_on_return 2301.75 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 0 + ei_premiums 820 "
        "+ ei_premiums_on_self_employment 0 + volunteer_firefighters_credit 0 + "
        "search_and_rescue_credit 0 + canada_employment_amount 1471 "
        "+ home_buyers_credit 0 + home_accessibility_credit 0 + adoption_credit 0 + "
        "pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + amounts_transferred_from_spouse 0 + "
        "medical_claim 0 = "
        "37679.05",
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 50000 "
        "less age_income_threshold 46330, not below 0 = 3670",
        "age_reduction: 15% of age_income_over_threshold 3670 (half-up to 0.01)",
        "age_amount_before_count: age_maximum 6223 less age_reduction 550.5, not below 0 = 5672.5",
        "age_amount: age_amount_before_count 5672.5 for each of 1 born_in_1960_or_earlier_checked "
        "= 5672.5",
        "spouse_amount_before_maximum: spouse_base 11905 "
        "less spouse_net_income 12000, not below 0 = 0",
        "spouse_amount_before_count: lesser of spouse_amount_before_maximum 0 and 10823 "
        "(half-up to 0.01)",
        "spouse_amount: spouse_amount_before_count 0 for each of 1 spouses_claimed_checked = 0",
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 5672.5 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 0 "
        "+ cpp_base_contributions_on_return 2301.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 820 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 + medical_claim 0 = 21541.25",
    ):
        assert line in rendered


def test_a_filer_born_in_1961_or_later_claims_no_age_amount_whatever_the_net_income() -> None:
    # Federal Worksheet line 7 is 8356.30 at net income 50000.00, but the count of filers born in
    # 1960 or earlier is 0: line 30100 is 0, and the other amounts are as in Return J.
    worksheet = return_j(born_in_1960_or_earlier=0)

    assert worksheet.get(AGE_AMOUNT_BEFORE_COUNT).value == D("8356.30")
    assert worksheet.get(AGE_AMOUNT).value == D("0")
    assert worksheet.get(SPOUSE_AMOUNT).value == D("6816.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("29322.75")


def test_the_ontario_age_amount_is_zero_at_net_income_87817() -> None:
    # Net income is employment income less the enhanced CPP contributions at their maximum
    # (1074.00): 88891 - 1074.00 = 87817.00. Worksheet ON428 line 6 is 15% x (87817.00 - 46330) =
    # 6223.05, more than the 6223.00 maximum, so line 7 "(if negative, enter "0")" is 0.
    worksheet = compute("88891", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(NET_INCOME).value == D("87817.00")
    assert worksheet.get(ontario.AGE_REDUCTION).value == D("6223.05")
    assert worksheet.get(ontario.AGE_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(ontario.AGE_AMOUNT).value == D("0")


def test_the_ontario_age_amount_is_still_a_dollar_short_of_zero_at_net_income_87816() -> None:
    # 88890 - 1074.00 = 87816.00: line 6 is 15% x (87816.00 - 46330) = 6222.90, so line 7 is
    # 6223.00 - 6222.90 = 0.10.
    worksheet = compute("88890", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(NET_INCOME).value == D("87816.00")
    assert worksheet.get(ontario.AGE_REDUCTION).value == D("6222.90")
    assert worksheet.get(ontario.AGE_AMOUNT).value == D("0.10")


def test_the_ontario_age_amount_is_the_whole_maximum_at_a_net_income_below_the_threshold() -> None:
    # Net income is 44585.00 (as for the federal case), below 46330: line 4 is negative, so 0,
    # line 6 is 0 and line 7 is 6223.00: "$46,330 or less, enter $6,223".
    worksheet = compute("45000", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(ontario.AGE_INCOME_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(ontario.AGE_AMOUNT).value == D("6223.00")


def test_a_filer_born_in_1961_or_later_claims_no_ontario_age_amount() -> None:
    worksheet = return_j(born_in_1960_or_earlier=0)

    assert worksheet.get(ontario.AGE_AMOUNT_BEFORE_COUNT).value == D("5672.50")
    assert worksheet.get(ontario.AGE_AMOUNT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15868.75")


def test_a_spouse_with_net_income_4000_who_is_not_infirm_gives_ontario_line_58120_of_7905() -> None:
    # ON428 line 11 11905.00 less line 12, 4000: line 13 is 7905.00, below the 10823 maximum,
    # claimed once. (The federal line 30300 is 16129.00 - 4000 = 12129.00.)
    worksheet = return_j(spouse_net_income="4000", spouse_caregiver_eligible=0)

    assert worksheet.get(ontario.SPOUSE_AMOUNT_BEFORE_MAXIMUM).value == D("7905.00")
    assert worksheet.get(ontario.SPOUSE_AMOUNT_BEFORE_COUNT).value == D("7905.00")
    assert worksheet.get(ontario.SPOUSE_AMOUNT).value == D("7905.00")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("29446.25")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "spouse_amount_before_maximum: spouse_base 11905 "
        "less spouse_net_income 4000, not below 0 = 7905"
    ) in rendered


def test_a_spouse_amount_not_claimed_gives_no_ontario_spouse_amount() -> None:
    worksheet = return_j(spouse_net_income="4000", spouse_caregiver_eligible=0, spouses_claimed=0)

    assert worksheet.get(ontario.SPOUSE_AMOUNT_BEFORE_COUNT).value == D("7905.00")
    assert worksheet.get(ontario.SPOUSE_AMOUNT).value == D("0")


@pytest.mark.parametrize(
    ("spouse_net_income", "amount"),
    [
        # Line 13 is 11905.00 less the spouse's net income, at most 10823: the cap holds up to a
        # net income of 1082.
        ("0", "10823.00"),
        ("1082", "10823.00"),
        ("1083", "10822.00"),
        ("4000", "7905.00"),
        ("11904.99", "0.01"),
        ("11905", "0"),
        ("20000", "0"),
    ],
)
def test_the_ontario_spouse_amount_is_11905_less_their_net_income_at_most_10823(
    spouse_net_income: str, amount: str
) -> None:
    worksheet = return_j(spouse_net_income=spouse_net_income)

    assert worksheet.get(ontario.SPOUSE_AMOUNT).value == D(amount)


def test_the_age_amount_is_reduced_to_ten_cents_at_net_income_105708() -> None:
    # Net income is employment income less the enhanced CPP contributions at their maximum
    # (1074.00): 106782 - 1074.00 = 105708.00. The Federal Worksheet's line 6 is 15% x (105708.00
    # - 45522) = 9027.90, so line 7 is 9028.00 - 9027.90 = 0.10.
    worksheet = compute("106782", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(NET_INCOME).value == D("105708.00")
    assert worksheet.get(AGE_REDUCTION).value == D("9027.90")
    assert worksheet.get(AGE_AMOUNT).value == D("0.10")


def test_the_age_amount_is_zero_at_net_income_105709() -> None:
    # 106783 - 1074.00 = 105709.00: line 6 is 15% x (105709.00 - 45522) = 9028.05, more than the
    # maximum 9028.00, so line 7 "(if negative, enter "0")" is 0.
    worksheet = compute("106783", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(NET_INCOME).value == D("105709.00")
    assert worksheet.get(AGE_REDUCTION).value == D("9028.05")
    assert worksheet.get(AGE_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(AGE_AMOUNT).value == D("0")


def test_the_caregiver_amount_is_zero_at_a_spouse_net_income_of_8623() -> None:
    # Schedule 5: with the spouse eligible for the Canada caregiver amount, line 3 of the
    # line 30300 part is 16129.00 + 2687 = 18816.00 and line 5 is 18816.00 - 8623 = 10193.00,
    # claimed. The caregiver part's line 3 is 28798.00 - 8623 = 20175.00, at most 8601, and line 5
    # is 8601 - 10193.00, negative, so 0.
    worksheet = return_j(spouse_net_income="8623")

    assert worksheet.get(SPOUSE_AMOUNT).value == D("10193.00")
    assert worksheet.get(SPOUSE_CAREGIVER_BEFORE_MAXIMUM).value == D("20175.00")
    assert worksheet.get(SPOUSE_CAREGIVER_LIMIT).value == D("8601")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")


def test_the_caregiver_amount_starts_at_a_dollar_past_a_spouse_net_income_of_10215() -> None:
    # 18816.00 - 10216 = 8600.00 is the spouse amount, so the caregiver amount is 8601 - 8600.00
    # = 1.00; at 10215 the spouse amount is 8601.00 and the caregiver amount is 0.
    at = return_j(spouse_net_income="10215")
    past = return_j(spouse_net_income="10216")

    assert at.get(SPOUSE_AMOUNT).value == D("8601.00")
    assert at.get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")
    assert past.get(SPOUSE_AMOUNT).value == D("8600.00")
    assert past.get(SPOUSE_CAREGIVER_AMOUNT).value == D("1.00")


def test_a_spouse_not_eligible_for_the_caregiver_amount_adds_no_supplement() -> None:
    # The count for line 51090 is 0: line 2 is 0, so line 3 is 16129.00 and line 5 is 16129.00 -
    # 4000 = 12129.00, claimed; the caregiver amount is 0 although its line 5 is 8601 - 12129.00,
    # negative, so 0 as well.
    worksheet = return_j(spouse_net_income="4000", spouse_caregiver_eligible=0)

    assert worksheet.get(SPOUSE_INFIRMITY_SUPPLEMENT).value == D("0")
    assert worksheet.get(SPOUSE_AMOUNT_BASIS).value == D("16129.00")
    assert worksheet.get(SPOUSE_AMOUNT).value == D("12129.00")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")


def test_a_spouse_amount_not_claimed_leaves_the_whole_caregiver_limit_unclaimed() -> None:
    # The count of spouse amounts claimed is 0: line 30300 is 0 (line 5 of the line 30300 part is
    # 4129.00). The model takes line 4 of the line 30425 part, "Amount claimed on line 30300 or
    # line 30400 of your return, if applicable", to be the line 30300 artifact, so line 4 is 0
    # and line 5 is 8601 - 0 = 8601 before the count. Line 30425 applies only with a claim on line
    # 30300, so with none the spouse is not entered as eligible for it and the amount is 0.
    worksheet = return_j(spouses_claimed=0, spouse_caregiver_eligible=0)

    assert worksheet.get(SPOUSE_AMOUNT_BEFORE_COUNT).value == D("4129.00")
    assert worksheet.get(SPOUSE_AMOUNT).value == D("0")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT).value == D("8601")
    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")


def test_the_age_amount_is_the_whole_maximum_at_a_net_income_below_the_threshold() -> None:
    # Net income is 45000 - 415.00 (1% x (45000 - 3500), the enhanced CPP contributions) =
    # 44585.00. Federal Worksheet line 4 is 44585.00 - 45522.00, negative, so 0, line 6 is 0 and
    # line 7 is 9028.00 - 0.00: "$45,522 or less, enter $9,028".
    worksheet = compute("45000", (), "0", "0", "0", "0", "0", born_in_1960_or_earlier=1)

    assert worksheet.get(NET_INCOME).value == D("44585.00")
    assert worksheet.get(AGE_INCOME_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(AGE_REDUCTION).value == D("0")
    assert worksheet.get(AGE_AMOUNT).value == D("9028.00")


@pytest.mark.parametrize(
    ("spouse_net_income", "eligible", "amount"),
    [
        # Line 3 is 16129.00 (no supplement) or 18816.00 (16129.00 + 2687), less the net income.
        ("0", 0, "16129.00"),
        ("4000", 0, "12129.00"),
        ("12000", 0, "4129.00"),
        # Net income at the basic personal amount leaves nothing; a cent under it, a cent.
        ("16128.99", 0, "0.01"),
        ("16129", 0, "0"),
        ("20000", 0, "0"),
        ("0", 1, "18816.00"),
        ("12000", 1, "6816.00"),
        ("18815.50", 1, "0.50"),
        ("18816", 1, "0"),
        ("20000", 1, "0"),
    ],
)
def test_the_spouse_amount_is_the_basic_personal_amount_and_2687_less_their_net_income(
    spouse_net_income: str, eligible: int, amount: str
) -> None:
    worksheet = return_j(spouse_net_income=spouse_net_income, spouse_caregiver_eligible=eligible)

    assert worksheet.get(SPOUSE_AMOUNT).value == D(amount)


@pytest.mark.parametrize(
    ("spouse_net_income", "amount"),
    [
        # Up to a net income of 10215 line 4 is 8601 or more; 10216 leaves 8601 - 8600.
        ("10215", "0"),
        ("10216", "1.00"),
        # Line 4 (the line 30300 amount) falls as the net income rises: 18816 - 16129 = 2687.
        ("16129", "5914.00"),
        # From 18816 up line 30300 is 0, so line 5 is line 3, at most 8601.
        ("18816", "8601.00"),
        ("20000", "8601.00"),
        # Line 3 falls below the maximum above 20197 (28798 - 8601): 28798 - 25000 = 3798.
        ("25000", "3798.00"),
        ("28797.99", "0.01"),
        # "net income is between $8,624 and $28,798": at and above the base, line 3 is 0.
        ("28798", "0"),
        ("30000", "0"),
    ],
)
def test_the_caregiver_amount_for_an_infirm_spouse_is_28798_less_their_net_income(
    spouse_net_income: str, amount: str
) -> None:
    worksheet = return_j(spouse_net_income=spouse_net_income)

    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D(amount)


@pytest.mark.parametrize("spouse_net_income", ["0", "8623", "12000", "20000"])
def test_there_is_no_caregiver_amount_for_a_spouse_not_eligible_for_it(
    spouse_net_income: str,
) -> None:
    # Line 51090 not entered (the count of eligible spouses is 0): line 30425 is not triggered.
    worksheet = return_j(spouse_net_income=spouse_net_income, spouse_caregiver_eligible=0)

    assert worksheet.get(SPOUSE_CAREGIVER_AMOUNT).value == D("0")
