"""CA-ON 2025 end to end: return FH, the Schedule 9 high-income and capital gift lines.

Return FH is `returns/2025_return_fh.yaml`: a filer with $300,000 of other income, so that the
taxable income is over the Schedule 9 income threshold (the high-income rate), with gifts of
capital property and of depreciable property, and every kind of donation. The donations are
larger than the limit, so line 10 is cut back to the limit, and line 20 is limited by the taxable
income over the threshold (line 19), not by line 16, so that both arms of line 20 are reached. The
lines no other worked return sets are non-zero: Schedule 9 lines 5 to 23, the charts for lines
33700 and 33900, and the donation credits. The figures are chosen (no CRA example exists) and
worked out by hand from the form text, as the description of the return shows. The tests check the
hand figure of each line; the engine's tax figures are checked in the YAML only.
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
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


def return_fh() -> Worksheet:
    """The worksheet of return FH: the inputs of `returns/2025_return_fh.yaml`, no spouse."""
    base = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_income="300000",
        charitable_donations="250000",
        government_donations="10000",
        university_donations_outside_canada="5000",
        foreign_charity_donations="5000",
        ecological_and_cultural_gifts="30000",
        ecological_gifts_before_2016="5000",
        depreciable_gift_recaptured_depreciation="3000",
        depreciable_gift_net_proceeds="8000",
        depreciable_gift_capital_cost="6000",
        capital_gift_taxable_gains="4000",
        capital_gift_gains_deduction="1000",
    )
    return service().compute(CA_ON, 2025, *base)["ca-on/return"][0]


def test_chart_33700_gives_a_depreciable_gift_of_3000_on_line_b() -> None:
    # Chart for line 33700: line 4 is the lesser of the net proceeds (8,000) and the capital cost
    # (6,000), that is 6,000. Line 5 is the lesser of the recaptured depreciation (3,000) and
    # line 4 (6,000), that is 3,000, which is line B.
    worksheet = return_fh()

    assert worksheet.get(DEPRECIABLE_GIFT_PROCEEDS_OR_COST).value == D("6000")
    assert worksheet.get(DEPRECIABLE_GIFTS).value == D("3000")


def test_chart_33900_gives_a_capital_property_gift_of_3000_on_line_c() -> None:
    # Chart for line 33900: line 3 is the taxable capital gains less the capital gains deduction:
    # 4,000 - 1,000 = 3,000, which is line C.
    worksheet = return_fh()

    assert worksheet.get(CAPITAL_PROPERTY_GIFTS).value == D("3000")


def test_the_limit_is_226500_and_line_10_cuts_the_270000_of_donations_back_to_it() -> None:
    # Line 5: 250,000 + 10,000 + 5,000 + 5,000 = 270,000. Line 6: net income 300,000 (amount A) x
    # 75% = 225,000. Line 7: amount B plus amount C (3,000 + 3,000 = 6,000, line D) x 25% = 1,500.
    # Line 8: 225,000 + 1,500 = 226,500. Line 9: the lesser of amount A (300,000) and line 8
    # (226,500) = 226,500. Line 10: the lesser of line 5 (270,000) and line 9 (226,500) = 226,500,
    # so the donations are cut back to the limit.
    worksheet = return_fh()

    assert worksheet.get(TOTAL_CHARITABLE_DONATIONS).value == D("270000")
    assert worksheet.get(CAPITAL_GIFTS_TOTAL).value == D("6000")
    assert worksheet.get(CAPITAL_GIFTS_LIMIT_ADDITION).value == D("1500.00")
    assert worksheet.get(DONATION_LIMIT_ON_NET_INCOME).value == D("225000.00")
    assert worksheet.get(DONATION_LIMIT_WITH_CAPITAL_GIFTS).value == D("226500.00")
    assert worksheet.get(CHARITABLE_DONATIONS_LIMIT).value == D("226500.00")
    assert worksheet.get(CHARITABLE_DONATIONS_CLAIMED).value == D("226500.00")


def test_the_first_tier_and_the_gifts_after_2016_give_256300_and_251300() -> None:
    # Line 12: 226,500 (line 10) + 30,000 (ecological and cultural gifts) = 256,500. Line 13: the
    # lesser of line 12 and $200 = 200. Line 14: 256,500 - 200 = 256,300. Line 16: 256,300 - 5,000
    # (the ecological gifts made after February 10, 2014 and before 2016) = 251,300.
    worksheet = return_fh()

    assert worksheet.get(DONATIONS_AND_GIFTS_TOTAL).value == D("256500.00")
    assert worksheet.get(DONATION_FIRST_TIER_MAXIMUM).value == D("200.00")
    assert worksheet.get(DONATIONS_FIRST_TIER).value == D("200.00")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER).value == D("256300.00")
    assert worksheet.get(DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS).value == D("251300.00")


def test_line_19_is_the_smaller_so_the_high_income_credit_is_15373_38() -> None:
    # Line 17: taxable income 300,000. Line 18: the income threshold 253,414. Line 19: 300,000 -
    # 253,414 = 46,586. Line 20 (line F): the lesser of line 16 (251,300) and line 19 (46,586) =
    # 46,586, times 33% = 15,373.38. Line 21: amount E (line 14, 256,300) minus amount F (46,586) =
    # 209,714 (line G), times 29% = 60,817.06. Line 22: amount H (line 13, 200) times 14.5% = 29.00.
    # Line 23 (line 34900): 15,373.38 + 60,817.06 + 29.00 = 76,219.44.
    worksheet = return_fh()

    assert worksheet.get(TAXABLE_INCOME).value == D("300000.00")
    assert worksheet.get(DONATION_HIGH_INCOME_THRESHOLD).value == D("253414.00")
    assert worksheet.get(TAXABLE_INCOME_OVER_DONATION_THRESHOLD).value == D("46586.00")
    assert worksheet.get(HIGH_INCOME_DONATIONS).value == D("46586.00")
    assert worksheet.get(HIGH_INCOME_DONATION_CREDIT).value == D("15373.38")
    assert worksheet.get(REGULAR_RATE_DONATIONS).value == D("209714.00")
    assert worksheet.get(REGULAR_RATE_DONATION_CREDIT).value == D("60817.06")
    assert worksheet.get(FIRST_TIER_DONATION_CREDIT).value == D("29.00")
    assert worksheet.get(DONATIONS_AND_GIFTS_CREDIT).value == D("76219.44")


def test_total_income_of_300000_is_the_net_and_taxable_income_as_no_deduction_applies() -> None:
    # The only income is other income of 300,000 (line 13000). No deduction applies, so net income
    # and taxable income are 300,000.
    worksheet = return_fh()

    assert worksheet.get(TOTAL_INCOME).value == D("300000.00")
    assert worksheet.get(NET_INCOME).value == D("300000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("300000.00")
