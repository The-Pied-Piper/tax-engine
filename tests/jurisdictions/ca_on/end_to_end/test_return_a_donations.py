"""CA-ON 2025 end to end: return a donations."""

from __future__ import annotations

import re

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GIFT_GAINS_DEDUCTION,
    CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED,
    CAPITAL_GIFTS_LIMIT_ADDITION,
    CAPITAL_GIFTS_TOTAL,
    CAPITAL_PROPERTY_GIFTS,
    CHARITABLE_DONATIONS,
    CHARITABLE_DONATIONS_CLAIMED,
    CHARITABLE_DONATIONS_LIMIT,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    DEPRECIABLE_GIFT_PROCEEDS_OR_COST,
    DEPRECIABLE_GIFTS,
    DONATION_LIMIT_ON_NET_INCOME,
    DONATION_LIMIT_WITH_CAPITAL_GIFTS,
    DONATIONS_AND_GIFTS_CREDIT,
    DONATIONS_AND_GIFTS_TOTAL,
    DONATIONS_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS,
    FEDERAL_TAX_AFTER_CREDITS,
    FIRST_TIER_DONATION_CREDIT,
    HIGH_INCOME_DONATION_CREDIT,
    HIGH_INCOME_DONATIONS,
    INFIRM_CHILDREN_AMOUNT,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND_OR_BALANCE_OWING,
    REGULAR_RATE_DONATION_CREDIT,
    REGULAR_RATE_DONATIONS,
    TAXABLE_INCOME,
    TAXABLE_INCOME_OVER_DONATION_THRESHOLD,
    TOP_UP_CREDITS_BASE,
    TOP_UP_EXCESS,
    TOP_UP_TAX_CREDIT,
    TOP_UP_THRESHOLD,
    TOTAL_CHARITABLE_DONATIONS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    COMMUNITY_FOOD_PROGRAM_CREDIT,
    COMMUNITY_FOOD_PROGRAM_DONATIONS,
    COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED,
    LIFT_CREDIT,
    ONTARIO_BASIC_TAX,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_AFTER_FOOD_CREDIT,
    ONTARIO_TAX_AFTER_LIFT_CREDIT,
    ONTARIO_TAX_AFTER_REDUCTION,
    ONTARIO_TAX_WITH_SURTAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def test_return_is_community_food_program_credit_comes_off_the_tax_after_the_lift_credit() -> None:
    # Return I with charitable donations of 1000, which the food donations of 1000 must be
    # within: employment income of 48000, with no capital gain, no RRSP contributions and no
    # union dues: base CPP contributions 4.95% x (48000 - 3500) = 2202.75, first additional 1% x
    # 44500 = 445.00, EI premiums 1.64% x 48000 = 787.20; net and taxable income 48000 - 445.00
    # = 47555.00. Ontario basic tax 5.05% x 47555.00 = 2401.5275, rounded half-up to the cent:
    # 2401.53, less the Ontario credits 5.05% x (12747 + 2202.75 + 787.20 = 15736.95) =
    # 794.715975, rounded half-up to the cent: 794.72. ON428 reads Schedule 9 lines 13 and 14,
    # the donations of 1000 being 200 and 800 over it: line 47 = 5.05% x 200 = 10.10, line 48 =
    # 11.16% x 800 = 89.28, line 49 = 99.38 and line 50 = 794.72 + 99.38 = 894.10, so the tax
    # after credits is 2401.53 - 894.10 = 1507.43, below the first surtax threshold and above
    # 588.00, so line 81 is 1507.43.
    # Schedule ON428-A: line 5 is 5.05% x 48000 = 2424.00, at most 875 (line 14); line 17 is
    # 47555.00 - 32500 = 15055.00 and line 19 15055.00 x 5% = 752.75; line 20 is 875 - 752.75 =
    # 122.25 (ON428 line 85). Line 86 is 1507.43 - 122.25 = 1385.18. Qualifying donations of 1000
    # (a caller input, within the donations claimed of Schedule 9 line 12, 1000): line 87 is
    # 25% x 1000 = 250.00 and line 88 is 1385.18 - 250.00 = 1135.18. The health premium on
    # 47555.00, "more than $38,500 but not more than $48,000", is 450, so line 90 is
    # 1135.18 + 450 = 1585.18.
    # The federal tax before credits is 14.5% x 47555.00 = 6895.475, rounded half-up to the cent:
    # 6895.48, less 14.5% x (16129 + 2202.75 + 787.20 + 1471 = 20589.95) = 2985.54275, rounded
    # half-up to the cent: 2985.54, and the donations credit of 14.5% x 200 + 29% x 800 =
    # 29.00 + 232.00 = 261.00, is 3648.94. The total payable is 3648.94 + 1585.18 =
    # 5234.12, and with the chosen tax deducted of 4800 and no Canada workers benefit (the
    # reduction 15% x (47555.00 - 26855) = 3105.00 exceeds the 1633), line 167 is 5234.12 - 4800
    # = 434.12, a balance owing.
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        income_tax_deducted="4800",
        community_food_program_donations="1000",
        charitable_donations="1000",
    )

    assert worksheet.get(NET_INCOME).value == D("47555.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("1507.43")
    assert worksheet.get(LIFT_CREDIT).value == D("122.25")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("1385.18")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_DONATIONS).value == D("1000")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("250.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("1135.18")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("1585.18")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3648.94")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5234.12")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("434.12")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "community_food_program_credit: 25% of community_food_program_donations_applied 1000 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "ontario_tax_after_food_credit: ontario_tax_after_lift_credit 1385.18 "
        "less community_food_program_credit 250, not below 0 = 1135.18"
    ) in rendered
    assert (
        "ontario_tax: split_income_line_52 1135.18 + ontario_health_premium 450 = 1585.18"
    ) in rendered
    assert (
        "community_food_program_donations_applied: community_food_program_donations 1000, "
        "at most donations_and_gifts_total 1000"
    ) in rendered


def test_donations_without_a_larger_line_86_leave_line_88_at_zero_not_negative() -> None:
    # Employment income of 40000 as in the LIFT test above, with charitable donations of 4000
    # (200 at the first tier, 3800 over it: Ontario credits 10.10 + 11.16% x 3800 = 434.18 on
    # ON428 lines 47 to 49), so line 86 is 715.23 - 434.18 = 281.05. Qualifying donations of
    # 4000, within the donations claimed, give line 87 = 25% x 4000 = 1000.00, more than line 86,
    # so line 88 is 0, not negative, and line 90 is the health premium of 450 alone.
    worksheet = compute(
        "40000",
        (),
        "0",
        "0",
        "7200",
        "0",
        "0",
        community_food_program_donations="4000",
        charitable_donations="4000",
    )

    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("281.05")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("1000.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("450")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "ontario_tax_after_food_credit: ontario_tax_after_lift_credit 281.05 "
        "less community_food_program_credit 1000, not below 0 = 0"
    ) in rendered


def test_no_donations_leave_line_88_at_line_86() -> None:
    # The default of 0 donations, as for Returns A to H: line 87 is 0 and line 88 is line 86.
    worksheet = compute("40000", (), "0", "0", "7200", "0", "0")

    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_DONATIONS).value == D("0")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("715.23")
    assert worksheet.get(ONTARIO_TAX).value == D("1165.23")


def test_return_ns_donations_and_gifts_credit_and_top_up_come_off_the_federal_tax() -> None:
    # Return N is Return I with charitable donations of 1500.00 (Schedule 9 line 1): net and
    # taxable income 47555.00 as in Return I. Line 5 = 1500.00; line 6 = 75% x 47555.00 =
    # 35666.25; no gifts of capital property, so line 7 = 25% x 0 = 0.00 and line 8 = 35666.25;
    # line 9 is the lesser of the net income (amount A) and line 8: 35666.25; line 10 = 1500.00;
    # line 12 = 1500.00; line 13 = 200 (the lesser of 1500.00 and $200); line 14 = 1300.00; line 16
    # = 1300.00; line 19 = 47555.00 - 253414.00, negative, so 0; line F = 0 and line 20 = 33% x 0
    # = 0.00; line G = 1300.00 and line 21 = 29% x 1300.00 = 377.00; line 22 = 14.5% x 200 = 29.00;
    # line 23 = 406.00 (T1 line 34900). Federal Worksheet: line 33800 = 14.5% x 20589.95 =
    # 2985.54275, rounded half-up to the cent: 2985.54; line 3 = 2985.54 + 29.00 = 3014.54, less
    # 8319.38 is negative, so line 5 = 0 and line 34990 = 0.00. Line 35000 = 2985.54 + 406.00 +
    # 0.00 = 3391.54, off the federal basic tax of 6895.48: 3503.94. ON428 reads Schedule 9
    # lines 13 and 14: line 46 = 5.05% x 15736.95 = 794.715975, rounded half-up to the cent:
    # 794.72; line 47 = 5.05% x 200 = 10.10; line 48 = 11.16% x 1300.00 = 145.08; line 49 (line
    # 58969) = 10.10 + 145.08 = 155.18; line 50 (line 61500) = 794.72 + 155.18 = 949.90, off the
    # Ontario basic tax of 2401.53: 1451.63, with no surtax and no tax reduction (twice the
    # 294.00 is 588.00, less than the 1451.63, so line 80 is 0); the LIFT credit of 122.25
    # gives 1329.38 and the food credit of 250.00 gives 1079.38; with the health premium of
    # 450, line 90 is 1529.38. The total payable is 3503.94 + 1529.38 = 5033.32 and, with the
    # chosen tax deducted of 4800 and no Canada workers benefit, line 167 is 5033.32 - 4800 =
    # 233.32, a balance owing.
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        income_tax_deducted="4800",
        community_food_program_donations="1000",
        charitable_donations="1500",
    )

    assert worksheet.get(NET_INCOME).value == D("47555.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("47555.00")
    assert worksheet.get(CHARITABLE_DONATIONS).value == D("1500")
    assert worksheet.get(TOTAL_CHARITABLE_DONATIONS).value == D("1500")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("35666.25")
    assert worksheet.get(DEPRECIABLE_GIFTS).value == D("0")
    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("0")
    assert worksheet.get(CAPITAL_GIFTS_TOTAL).value == D("0")
    assert worksheet.get(CAPITAL_GIFTS_LIMIT_ADDITION).value == D("0.00")
    assert worksheet.get(DONATION_LIMIT_WITH_CAPITAL_GIFTS).value == D("35666.25")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("35666.25")
    assert worksheet.get(CHARITABLE_DONATIONS_CLAIMED).value == D("1500")
    assert worksheet.get(DONATIONS_AND_GIFTS_TOTAL).value == D("1500")
    assert worksheet.get(DONATIONS_FIRST_TIER).value == D("200")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("1300")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS).value == D("1300")
    assert worksheet.get(TAXABLE_INCOME_OVER_DONATION_THRESHOLD).value == D("0")
    assert worksheet.get(HIGH_INCOME_DONATIONS).value == D("0")
    assert worksheet.get(HIGH_INCOME_DONATION_CREDIT).value == D("0.00")
    assert worksheet.get(REGULAR_RATE_DONATIONS).value == D("1300")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("377.00")
    assert worksheet.get(FIRST_TIER_DONATION_CREDIT).value == D("29.00")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("406.00")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("2985.54")
    assert worksheet.get(TOP_UP_CREDITS_BASE).value == D("3014.54")
    assert worksheet.get(TOP_UP_EXCESS).value == D("0")
    assert worksheet.get(TOP_UP_TAX_CREDIT).value == D("0.00")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("3391.54")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3503.94")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("794.72")
    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D("10.10")
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D("145.08")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("155.18")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("949.90")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1451.63")
    assert worksheet.get(ONTARIO_TAX_WITH_SURTAX).value == D("1451.63")
    assert worksheet.get(ONTARIO_TAX_AFTER_REDUCTION).value == D("1451.63")
    assert worksheet.get(ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("1329.38")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("1079.38")
    assert worksheet.get(ONTARIO_TAX).value == D("1529.38")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5033.32")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("233.32")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert ("donation_limit_on_net_income: 75% of net_income 47555 (half-up to 0.01)") in rendered
    assert (
        "charitable_donations_limit: lesser of net_income 47555 "
        "and donation_limit_with_capital_gifts 35666.25 = 35666.25"
    ) in rendered
    assert (
        "donations_first_tier: lesser of donations_and_gifts_total 1500 "
        "and donation_first_tier_maximum 200 = 200"
    ) in rendered
    assert (
        "regular_rate_donation_credit: 29% of regular_rate_donations 1300 (half-up to 0.01)"
    ) in rendered
    assert (
        "first_tier_donation_credit: 14.5% of donations_first_tier 200 (half-up to 0.01)"
    ) in rendered
    assert (
        "donations_and_gifts_credit: high_income_donation_credit 0 "
        "+ regular_rate_donation_credit 377 + first_tier_donation_credit 29 = 406"
    ) in rendered
    assert (
        "top_up_credits_base: credit_amounts_at_credit_rate 2985.54 "
        "+ first_tier_donation_credit 29 = 3014.54"
    ) in rendered
    assert (
        "top_up_excess: top_up_credits_base 3014.54 less top_up_threshold 8319.38, not below 0 = 0"
    ) in rendered
    assert (
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 2985.54 "
        "+ donations_and_gifts_credit 406 + top_up_tax_credit 0 = 3391.54"
    ) in rendered
    assert (
        "credits_against_basic_federal_tax: non_refundable_tax_credits 3391.54 "
        "+ dividend_tax_credit 0 + amt_minimum_tax_carryover_applied 0 = 3391.54"
    ) in rendered
    assert (
        "federal_tax_after_credits: federal_tax_with_split_income 6895.48 "
        "less credits_against_basic_federal_tax 3391.54, not below 0 = 3503.94"
    ) in rendered
    assert (
        "donations_first_tier_credit: 5.05% of donations_first_tier 200 (half-up to 0.01)"
    ) in rendered
    assert (
        "donations_over_first_tier_credit: 11.16% of donations_over_first_tier 1300 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "donations_and_gifts_credit: donations_first_tier_credit 10.1 "
        "+ donations_over_first_tier_credit 145.08 = 155.18"
    ) in rendered
    assert (
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 794.72 "
        "+ donations_and_gifts_credit 155.18 = 949.9"
    ) in rendered
    assert (
        "ontario_tax_after_credits: ontario_basic_tax 2401.53 "
        "less non_refundable_tax_credits 949.9, not below 0 = 1451.63"
    ) in rendered
    assert (
        "ontario_tax: split_income_line_52 1079.38 + ontario_health_premium 450 = 1529.38"
    ) in rendered


def test_taxable_income_over_the_threshold_is_charged_33_percent_up_to_line_16() -> None:
    # Employment income of 300000, with donations of 50200 (Schedule 9 line 1): enhanced CPP
    # contributions of 1074.00 give net and taxable income 300000 - 1074.00 = 298926.00. Line 6 =
    # 75% x 298926.00 = 224194.50, line 9 = 224194.50, line 10 = 50200, line 12 = 50200, line 13 =
    # 200, line 14 = 50000 and line 16 = 50000. Line 19 = 298926.00 - 253414.00 = 45512.00, below
    # line 16, so line F = 45512.00 and line 20 = 33% x 45512.00 = 15018.96; line G = 50000 -
    # 45512.00 = 4488.00 and line 21 = 29% x 4488.00 = 1301.52; line 22 = 29.00; line 23 =
    # 15018.96 + 1301.52 + 29.00 = 16349.48. The credit amounts are 14538 (the basic personal
    # amount at or above 253,414) + 3356.10 + 1077.48 + 1471 = 20442.58, and line 33800 = 14.5% x
    # it = 2964.1741, rounded half-up to the cent: 2964.17; the top-up base 2964.17 + 29.00 is
    # below 8319.38, so line 34990 is 0; line 35000 = 2964.17 + 16349.48 + 0.00 = 19313.65.
    worksheet = compute("300000", (), "0", "0", "0", "0", "0", charitable_donations="50200")

    assert worksheet.get(NET_INCOME).value == D("298926.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("298926.00")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("224194.50")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("224194.50")
    assert worksheet.get(CHARITABLE_DONATIONS_CLAIMED).value == D("50200")
    assert worksheet.get(DONATIONS_FIRST_TIER).value == D("200")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("50000")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS).value == D("50000")
    assert worksheet.get(TAXABLE_INCOME_OVER_DONATION_THRESHOLD).value == D("45512.00")
    assert worksheet.get(HIGH_INCOME_DONATIONS).value == D("45512.00")
    assert worksheet.get(HIGH_INCOME_DONATION_CREDIT).value == D("15018.96")
    assert worksheet.get(REGULAR_RATE_DONATIONS).value == D("4488.00")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("1301.52")
    assert worksheet.get(FIRST_TIER_DONATION_CREDIT).value == D("29.00")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("16349.48")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("20442.58")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("2964.17")
    assert worksheet.get(TOP_UP_CREDITS_BASE).value == D("2993.17")
    assert worksheet.get(TOP_UP_TAX_CREDIT).value == D("0.00")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("19313.65")
    # ON428 reads lines 13 and 14, not the 33% and 29% parts: line 47 = 5.05% x 200 = 10.10 and
    # line 48 = 11.16% x 50000 = 5580.00, so line 49 = 5590.10; line 46 = 5.05% x 17180.58 =
    # 867.61929, rounded half-up to the cent: 867.62; line 50 = 867.62 + 5590.10 = 6457.72.
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("17180.58")
    assert worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("867.62")
    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D("10.10")
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D("5580.00")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("5590.10")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("6457.72")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == (
        worksheet.get(ONTARIO_BASIC_TAX).value - D("6457.72")
    )
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "high_income_donations: lesser of donations_over_first_tier_after_2016_gifts 50000 "
        "and taxable_income_over_donation_threshold 45512 = 45512"
    ) in rendered
    assert (
        "high_income_donation_credit: 33% of high_income_donations 45512 (half-up to 0.01)"
    ) in rendered


def test_the_top_up_tax_credit_is_3_45_percent_of_the_credits_over_8319_38() -> None:
    # Employment income of 48000, 15 infirm children (line 30500: 15 x 2687 = 40305.00) and
    # donations of 1500.00: the credit amounts are 16129 + 0 + 40305.00 + 2202.75 + 787.20 + 1471
    # = 60894.95 and line 33800 = 14.5% x 60894.95 = 8829.77275, rounded half-up to the cent:
    # 8829.77. Federal Worksheet line 3 = 8829.77 + 29.00 (Schedule 9 line 22) = 8858.77; line 5 =
    # 8858.77 - 8319.38 = 539.39; line 7 = 3.45% x 539.39 = 18.608955, rounded half-up to the
    # cent: 18.61 (line 34990). Line 35000 = 8829.77 + 406.00 + 18.61 = 9254.38, more than the
    # federal basic tax of 6895.48, so the federal tax after credits is 0.
    worksheet = compute(
        "48000", (), "0", "0", "8640", "0", "0", infirm_children=15, charitable_donations="1500"
    )

    assert worksheet.get(INFIRM_CHILDREN_AMOUNT).value == D("40305.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("60894.95")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("8829.77")
    assert worksheet.get(FIRST_TIER_DONATION_CREDIT).value == D("29.00")
    assert worksheet.get(TOP_UP_CREDITS_BASE).value == D("8858.77")
    assert worksheet.get(TOP_UP_THRESHOLD).value == D("8319.38")
    assert worksheet.get(TOP_UP_EXCESS).value == D("539.39")
    assert worksheet.get(TOP_UP_TAX_CREDIT).value == D("18.61")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("9254.38")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("0")
    # The infirm children are federal only: ON428 line 46 is 794.72 as for Return N, and lines
    # 47 to 49 give 10.10 + 145.08 = 155.18, so line 61500 is 949.90 whatever the federal credits.
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("155.18")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("949.90")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "top_up_excess: top_up_credits_base 8858.77 less top_up_threshold 8319.38, not below 0 "
        "= 539.39"
    ) in rendered
    assert "top_up_tax_credit: 3.45% of top_up_excess 539.39 (half-up to 0.01)" in rendered


def test_gifts_of_capital_property_raise_the_donation_limit_above_75_percent_of_net_income() -> (
    None
):
    # Employment income of 48000: net income 47555.00, so line 6 = 35666.25. Depreciable property
    # (chart for line 33700): recaptured depreciation 3000, net proceeds 5000, capital cost 4000:
    # line 4 = 4000, line 5 (line B) = 3000. Other capital property (chart for line 33900): taxable
    # gains 4000 less the capital gains deduction 1000: 3000 (line C). Line D = 6000 and line 7 =
    # 25% x 6000 = 1500.00; line 8 = 35666.25 + 1500.00 = 37166.25; line 9 is the lesser of the net
    # income 47555.00 and line 8: 37166.25. Donations of 40000 (line 5) are limited to it (line 10),
    # so line 12 = 37166.25, line 14 = 37166.25 - 200 = 36966.25 and, below the threshold, line 21
    # = 29% x 36966.25 = 10720.2125, rounded half-up to the cent: 10720.21; line 22 = 29.00; line
    # 23 = 10749.21.
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        charitable_donations="40000",
        depreciable_gift_recaptured_depreciation="3000",
        depreciable_gift_net_proceeds="5000",
        depreciable_gift_capital_cost="4000",
        capital_gift_taxable_gains="4000",
        capital_gift_gains_deduction="1000",
    )

    assert worksheet.get(DEPRECIABLE_GIFT_PROCEEDS_OR_COST).value == D("4000")
    assert worksheet.get(DEPRECIABLE_GIFTS).value == D("3000")
    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("3000")
    assert worksheet.get(CAPITAL_GIFTS_TOTAL).value == D("6000")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("35666.25")
    assert worksheet.get(CAPITAL_GIFTS_LIMIT_ADDITION).value == D("1500.00")
    assert worksheet.get(DONATION_LIMIT_WITH_CAPITAL_GIFTS).value == D("37166.25")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("37166.25")
    assert worksheet.get(CHARITABLE_DONATIONS_CLAIMED).value == D("37166.25")
    assert worksheet.get(DONATIONS_AND_GIFTS_TOTAL).value == D("37166.25")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("36966.25")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("10720.21")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("10749.21")
    # ON428 line 47 = 5.05% x 200 = 10.10 and line 48 = 11.16% x 36966.25 = 4125.4335, rounded
    # half-up to the cent: 4125.43; line 49 = 4135.53; line 50 = 794.72 + 4135.53 = 4930.25,
    # more than the Ontario basic tax of 2401.53, so line 53 is 0, not negative.
    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D("10.10")
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D("4125.43")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("4135.53")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("4930.25")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("2401.53")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("0")


def test_ecological_and_cultural_gifts_join_line_12_and_those_before_2016_come_off_line_16() -> (
    None
):
    # Employment income of 300000: taxable income 298926.00, line 19 = 45512.00. Donations of
    # 50000 (line 1) and ecological gifts of 10000 (line 11), 4000 of them made before 2016 (line
    # 15): line 12 = 60000, line 13 = 200, line 14 = 59800, line 16 = 59800 - 4000 = 55800, line F
    # = the lesser of 55800 and 45512.00: 45512.00, line 20 = 33% x 45512.00 = 15018.96; line G =
    # 59800 - 45512.00 = 14288.00 and line 21 = 29% x 14288.00 = 4143.52; line 22 = 29.00; line
    # 23 = 19191.48. The 4000 made before 2016 is in line G, at 29%, not at 33%.
    worksheet = compute(
        "300000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        charitable_donations="50000",
        ecological_and_cultural_gifts="10000",
        ecological_gifts_before_2016="4000",
    )

    assert worksheet.get(DONATIONS_AND_GIFTS_TOTAL).value == D("60000")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("59800")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS).value == D("55800")
    assert worksheet.get(HIGH_INCOME_DONATIONS).value == D("45512.00")
    assert worksheet.get(HIGH_INCOME_DONATION_CREDIT).value == D("15018.96")
    assert worksheet.get(REGULAR_RATE_DONATIONS).value == D("14288.00")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("4143.52")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("19191.48")
    # ON428 line 48 takes Schedule 9 line 14 whole, 59800, with the 4000 made before 2016 and
    # the part federal charges at 33% in it: 11.16% x 59800 = 6673.68; line 47 = 10.10; line 49 =
    # 6683.78; line 50 = 867.62 + 6683.78 = 7551.40.
    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D("10.10")
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D("6673.68")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("6683.78")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("7551.40")


def test_no_donations_leave_the_federal_credits_at_the_credit_rate() -> None:
    # The defaults of 0, as for Returns A to I: lines 34900 and 34990 are 0.00, so line 35000 is
    # line 33800 alone.
    worksheet = compute("40000", (), "0", "0", "7200", "0", "0")

    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("0.00")
    assert worksheet.get(TOP_UP_TAX_CREDIT).value == D("0.00")
    assert (
        worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value
        == worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value
    )


def test_no_donations_leave_the_ontario_credits_at_the_credit_rate() -> None:
    # The defaults of 0, as for Returns A to M: lines 47 to 49 are 0.00, so line 50 is line 46
    # alone.
    worksheet = compute("40000", (), "0", "0", "7200", "0", "0")

    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D("0.00")
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D("0.00")
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D("0.00")
    assert (
        worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value
        == worksheet.get(ontario.CREDIT_AMOUNTS_AT_CREDIT_RATE).value
    )


@pytest.mark.parametrize(
    ("charitable_donations", "line_47", "line_48", "line_49"),
    [
        # Schedule 9 line 13 is the lesser of line 12 and $200, line 14 the rest.
        ("0", "0.00", "0.00", "0.00"),
        ("100", "5.05", "0.00", "5.05"),
        ("200", "10.10", "0.00", "10.10"),
        ("200.01", "10.10", "0.00", "10.10"),
        ("201", "10.10", "0.11", "10.21"),
        # 11.16% x 1300 = 145.08; x 1234.57 = 137.778012, rounded half-up to 137.78 (line 14 is
        # 1234.57 for a line 12 of 1434.57).
        ("1500", "10.10", "145.08", "155.18"),
        ("1434.57", "10.10", "137.78", "147.88"),
    ],
)
def test_the_ontario_donations_credit_follows_schedule_9_lines_13_and_14(
    charitable_donations: str, line_47: str, line_48: str, line_49: str
) -> None:
    worksheet = compute(
        "48000", (), "0", "0", "8640", "0", "0", charitable_donations=charitable_donations
    )

    assert worksheet.get(ontario.DONATIONS_FIRST_TIER_CREDIT).value == D(line_47)
    assert worksheet.get(ontario.DONATIONS_OVER_FIRST_TIER_CREDIT).value == D(line_48)
    assert worksheet.get(ontario.DONATIONS_AND_GIFTS_CREDIT).value == D(line_49)
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("794.72") + D(line_49)


def capital_gift_return(taxable_gains: str, gains_deduction: str) -> Worksheet:
    """Employment income of 60000 and no other income or claims, with the Schedule 9 chart for line
    33900 given: line 1 the taxable capital gains and line 2 the capital gains deduction."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        capital_gift_taxable_gains=taxable_gains,
        capital_gift_gains_deduction=gains_deduction,
    )


def test_a_capital_gift_deduction_of_zero_leaves_the_whole_gain() -> None:
    # Schedule 9 chart for line 33900, line 2 "Amount of current-year capital gains deduction from
    # capital property donated in 2025" of 0 is at most line 1 of 1000, and line 3 "Line 1 minus
    # Line 2" is 1000.
    worksheet = capital_gift_return("1000", "0")

    assert worksheet.get(CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED).value == D("0")
    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("1000")


def test_a_capital_gift_deduction_equal_to_the_gain_leaves_nothing() -> None:
    # Line 2 of 1000 is at most line 1 of 1000 (not above it), so line 3 is 1000 - 1000 = 0.
    worksheet = capital_gift_return("1000", "1000")

    assert worksheet.get(CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED).value == D("1000")
    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("0")


def test_a_capital_gift_deduction_a_cent_below_the_gain_leaves_a_cent() -> None:
    # Line 2 of 999.99 is at most line 1 of 1000, so line 3 is 1000 - 999.99 = 0.01.
    worksheet = capital_gift_return("1000", "999.99")

    assert worksheet.get(CAPITAL_GIFT_GAINS_DEDUCTION).value == D("999.99")
    assert worksheet.get(CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED).value == D("999.99")
    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("0.01")


def test_a_capital_gift_deduction_above_the_gain_is_refused_as_an_input_error() -> None:
    # Line 2 of 2000 is above line 1 of 1000. The refusal names both inputs (an input error, HTTP
    # 422), not the derived line 3, which would otherwise be -1000.
    message = "ca/capital_gift_gains_deduction 2000 is above ca/capital_gift_taxable_gains 1000"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        capital_gift_return("1000", "2000")


@pytest.mark.parametrize(
    ("deduction", "gain"),
    [
        # Over by a cent: refused, not capped, so line 3 is never negative.
        ("1000.01", "1000"),
        ("999.99", "999.98"),
    ],
)
def test_a_capital_gift_deduction_over_the_gain_by_a_cent_is_refused(
    deduction: str, gain: str
) -> None:
    message = (
        f"ca/capital_gift_gains_deduction {deduction} is above ca/capital_gift_taxable_gains {gain}"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        capital_gift_return(gain, deduction)


def test_food_donations_with_no_gifts_claimed_are_refused() -> None:
    # Employment income of 60000 with no Schedule 9 donations (line 12 is 0) and community food
    # program donations of 1000: ON428 line 87 "Enter the amount of qualifying donations that have
    # also been claimed as a charitable donation" has no gift to match, so the donations are an
    # input error, not a credit of 250.00.
    with pytest.raises(InputAboveBoundError) as raised:
        compute("60000", (), "0", "0", "0", "0", "0", community_food_program_donations="1000")

    assert str(raised.value) == (
        "ca-on/return, instance 1: ca-on/community_food_program_donations 1000 is above "
        "ca/donations_and_gifts_total 0"
    )


def test_food_donations_equal_to_the_gifts_claimed_get_the_25_percent_credit() -> None:
    # Charitable donations of exactly 1000 (Schedule 9 line 12 is 1000) match the food donations
    # of 1000: the donations are not above the bound, and the credit is 25% of 1000 = 250.00.
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        community_food_program_donations="1000",
        charitable_donations="1000",
    )

    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED).value == D("1000")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("250.00")


def test_food_donations_over_the_gifts_claimed_by_one_cent_are_refused() -> None:
    # Charitable donations of 999.99 and food donations of 1000.00: over the bound by a cent.
    with pytest.raises(InputAboveBoundError) as raised:
        compute(
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            community_food_program_donations="1000.00",
            charitable_donations="999.99",
        )

    assert str(raised.value) == (
        "ca-on/return, instance 1: ca-on/community_food_program_donations 1000.00 "
        "is above ca/donations_and_gifts_total 999.99"
    )


def test_no_food_donations_and_no_gifts_pass_with_a_credit_of_zero() -> None:
    worksheet = compute("60000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_DONATIONS_APPLIED).value == D("0")
    assert worksheet.get(COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("0")


def test_food_donations_above_the_donation_limit_are_refused_though_entered_as_gifts() -> None:
    # Net income of 1000 limits the donations claimed to 75% of it, 750.00 (Schedule 9 line 10),
    # so line 12 is 750.00 and the food donations of 1000 entered as gifts are above it.
    with pytest.raises(InputAboveBoundError) as raised:
        compute(
            "1000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            community_food_program_donations="1000",
            charitable_donations="1000",
        )

    assert str(raised.value) == (
        "ca-on/return, instance 1: ca-on/community_food_program_donations 1000 is above "
        "ca/donations_and_gifts_total 750.00"
    )
