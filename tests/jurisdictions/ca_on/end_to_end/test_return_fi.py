"""CA-ON 2025 end to end: return FI, the Schedule 9 capital gift and net income limit lines.

Return FI is `returns/2025_return_fi.yaml`: a filer with $300,000 of other income and gifts of
capital property larger than the net income, so that the net income (amount A) is the total
charitable donations limit (line 9), and a gift of depreciable property limited by its proceeds.
The taxable income is over the Schedule 9 income threshold, so line 19 is positive, but line 16 is
zero (the first tier takes all of the 150.00 of gifts, so line 14 is 0 and line 15 takes it
below zero), so line 20 is zero: the second arm of
line 20 is reached. The figures are chosen (no CRA example exists) and worked out by hand from the
form text, as the description of the return shows. The tests check the hand figure of each line; the
engine's tax figures are checked in the YAML only.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GIFTS_LIMIT_ADDITION,
    CAPITAL_GIFTS_TOTAL,
    CAPITAL_PROPERTY_GIFTS,
    CHARITABLE_DONATIONS_CLAIMED,
    CHARITABLE_DONATIONS_LIMIT,
    DEPRECIABLE_GIFT_PROCEEDS_OR_COST,
    DEPRECIABLE_GIFTS,
    DONATION_FIRST_TIER_MAXIMUM,
    DONATION_HIGH_INCOME_THRESHOLD,
    DONATION_LIMIT_ON_NET_INCOME,
    DONATION_LIMIT_WITH_CAPITAL_GIFTS,
    DONATIONS_AND_GIFTS_CREDIT,
    DONATIONS_AND_GIFTS_TOTAL,
    DONATIONS_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER,
    DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS,
    FIRST_TIER_DONATION_CREDIT,
    HIGH_INCOME_DONATION_CREDIT,
    HIGH_INCOME_DONATIONS,
    NET_INCOME,
    REGULAR_RATE_DONATION_CREDIT,
    REGULAR_RATE_DONATIONS,
    TAXABLE_INCOME,
    TAXABLE_INCOME_OVER_DONATION_THRESHOLD,
    TOTAL_CHARITABLE_DONATIONS,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_fi() -> Worksheet:
    """The worksheet of return FI: the inputs of `returns/2025_return_fi.yaml`, no spouse."""
    base = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="300000",
        charitable_donations="50",
        ecological_and_cultural_gifts="100",
        ecological_gifts_before_2016="100",
        depreciable_gift_recaptured_depreciation="7000",
        depreciable_gift_net_proceeds="6500",
        depreciable_gift_capital_cost="9000",
        capital_gift_taxable_gains="400000",
        capital_gift_gains_deduction="1000",
    )
    return service().compute(CA_ON, 2025, *base)["ca-on/return"][0]


def test_chart_33700_gives_a_depreciable_gift_of_6500_limited_by_the_proceeds() -> None:
    # Chart for line 33700: line 4 is the lesser of the net proceeds (6,500) and the capital cost
    # (9,000), that is 6,500. Line 5 is the lesser of the recaptured depreciation (7,000) and line 4
    # (6,500), that is 6,500, which is line B.
    worksheet = return_fi()

    assert worksheet.get(DEPRECIABLE_GIFT_PROCEEDS_OR_COST).value == D("6500")
    assert worksheet.get(DEPRECIABLE_GIFTS).value == D("6500")


def test_chart_33900_gives_a_capital_property_gift_of_399000_on_line_c() -> None:
    # Chart for line 33900: line 3 is the taxable capital gains less the capital gains deduction:
    # 400,000 - 1,000 = 399,000, which is line C.
    worksheet = return_fi()

    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("399000")


def test_net_income_of_300000_is_the_donation_limit_as_the_gifts_exceed_it() -> None:
    # Line 6: net income of 300,000 (amount A) x 75% = 225,000. Line 7: amount B plus amount C
    # (6,500 + 399,000 = 405,500, line D) x 25% = 101,375. Line 8: 225,000 + 101,375 = 326,375. Line
    # 9: the lesser of amount A (300,000) and line 8 (326,375) = 300,000, so the net income is the
    # limit. Line 10: the lesser of line 5 (50) and line 9 (300,000) = 50, the donations claimed.
    worksheet = return_fi()

    assert worksheet.get(TOTAL_CHARITABLE_DONATIONS).value == D("50")
    assert worksheet.get(CAPITAL_GIFTS_TOTAL).value == D("405500")
    assert worksheet.get(CAPITAL_GIFTS_LIMIT_ADDITION).value == D("101375.00")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("225000.00")
    assert worksheet.get(DONATION_LIMIT_WITH_CAPITAL_GIFTS).value == D("326375.00")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("300000.00")
    assert worksheet.get(CHARITABLE_DONATIONS_CLAIMED).value == D("50.00")


def test_the_first_tier_takes_all_of_the_150_and_nothing_is_over_it() -> None:
    # Line 11: 100 of ecological gifts made after February 10, 2014 and before 2016 (line 15 is
    # 100). Line 12: 50 + 100 = 150. Line 13: the lesser of line 12 and $200 = 150. Line 14: 150 -
    # 150 = 0. Line 16: 0 - 100 is negative, so it is 0.
    worksheet = return_fi()

    assert worksheet.get(DONATIONS_AND_GIFTS_TOTAL).value == D("150.00")
    assert worksheet.get(DONATION_FIRST_TIER_MAXIMUM).value == D("200.00")
    assert worksheet.get(DONATIONS_FIRST_TIER).value == D("150.00")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("0.00")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS).value == D("0.00")


def test_line_16_of_zero_makes_line_20_zero_though_income_is_over_the_threshold() -> None:
    # Line 17: taxable income 300,000. Line 18: the income threshold 253,414. Line 19: 300,000 -
    # 253,414 = 46,586. Line 20 (line F): the lesser of line 16 (0) and line 19 (46,586) = 0, times
    # 33% = 0.00. Line 21: amount E (line 14, 0) minus amount F (0) = 0 (line G), times 29% = 0.00.
    # Line 22: amount H (line 13, 150) times 14.5% = 21.75. Line 23: 0 + 0 + 21.75 = 21.75.
    worksheet = return_fi()

    assert worksheet.get(TAXABLE_INCOME).value == D("300000.00")
    assert worksheet.get(DONATION_HIGH_INCOME_THRESHOLD).value == D("253414.00")
    assert worksheet.get(TAXABLE_INCOME_OVER_DONATION_THRESHOLD).value == D("46586.00")
    assert worksheet.get(HIGH_INCOME_DONATIONS).value == D("0.00")
    assert worksheet.get(HIGH_INCOME_DONATION_CREDIT).value == D("0.00")
    assert worksheet.get(REGULAR_RATE_DONATIONS).value == D("0.00")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("0.00")
    assert worksheet.get(FIRST_TIER_DONATION_CREDIT).value == D("21.75")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("21.75")


def test_total_income_of_300000_is_the_net_and_taxable_income_as_no_deduction_applies() -> None:
    # The only income is other income of 300,000 (line 13000). No deduction applies, so net income
    # and taxable income are 300,000.
    worksheet = return_fi()

    assert worksheet.get(TOTAL_INCOME).value == D("300000.00")
    assert worksheet.get(NET_INCOME).value == D("300000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("300000.00")
