"""CA-ON 2025 end to end: return s, Form T2222 (Northern Residents Deductions).

Return S has employment income of 50000, days lived in Zone A and Zone B and trips from both
zones, as in `returns/2025_return_s.yaml`; the tests after it are hand-derived from the form
(docs/cra-forms-2025/t2222-25e.txt) and, for the most part, take no income but one amount of
other income (line 13000), so that net income (line 23600) is exactly that amount.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError, InvalidRecordError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    REFUND_OR_BALANCE_OWING,
    RESIDENCY_AMOUNT,
    RESIDENCY_DEDUCTION,
    RESIDENCY_NET_INCOME_LIMIT,
    STANDARD_AMOUNT_ALLOCATED,
    TAXABLE_INCOME,
    TOTAL_PAYABLE,
    TRAVEL_DEDUCTION,
    TRAVEL_TOTAL_ZONE_A,
    TRAVEL_TOTAL_ZONE_B,
    TRAVEL_ZONE_B_DEDUCTION,
    ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_A_BASIC_RESIDENCY_AMOUNT,
    ZONE_A_RESIDENCY_AFTER_WORK_SITE,
    ZONE_A_RESIDENCY_AMOUNT,
    ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT,
    ZONE_B_BASIC_RESIDENCY_AMOUNT,
    ZONE_B_RESIDENCY_AFTER_WORK_SITE,
    ZONE_B_RESIDENCY_AMOUNT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, individual, trip

ZONE_A = 1
ZONE_B = 2


def return_s() -> Worksheet:
    """Return S's inputs, as in `returns/2025_return_s.yaml`."""
    return compute(
        "50000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        zone_a_days_lived=200,
        zone_a_additional_residency_days=200,
        zone_b_days_lived=165,
        zone_b_special_work_site_benefits="100.00",
        travel_trips=(
            trip(1, ZONE_A, "1500", "1300", "750"),
            trip(1, ZONE_A, "1500", "800", "900"),
            trip(2, ZONE_B, "400", "400", "600"),
            trip(2, ZONE_B, "800", "850", "900"),
        ),
        travel_individuals=(individual(1), individual(2, "1200")),
        income_tax_deducted="5000",
    )


def northern(net_income: str = "50000", **inputs: Any) -> Worksheet:
    """A return of other income only, so that net income is `net_income`, with T2222 inputs."""
    return compute("0", (), "0", "0", "0", "0", "0", other_income=net_income, **inputs)


def test_zone_a_for_365_days_as_the_sole_claimant_deducts_8030_with_no_travel() -> None:
    # Zone A, 365 days, and the additional residency amount for the same 365 days as the only
    # person in the household claiming the basic residency amount; no work site, no trip; net
    # income 50,000. Line 1 365 x $11.00 = 4,015.00; line 2 365 x $11.00 = 4,015.00; line 3 and
    # line 11 4,015.00 + 4,015.00 = 8,030.00; line 4 0, line 5 8,030.00; Zone B 0; line 12 50,000
    # x 20% = 10,000.00; line 13 the lesser, 8,030.00; no travel; line 19 (line 25500) 8,030.00.
    worksheet = northern(zone_a_days_lived=365, zone_a_additional_residency_days=365)

    assert worksheet.get(NET_INCOME).value == D("50000")
    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("4015.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("4015.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("8030.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("8030.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("0")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("0")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("8030.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("10000.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("8030.00")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("0")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("0")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("0")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("0")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("8030.00")
    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("0")
    # Line 25700 adds line 66 (25500) to the other deductions, all 0: 8,030.00, so taxable income
    # (line 26000) is 50,000 - 8,030.00 = 41,970.00.
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("8030.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("41970.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "zone_a_basic_residency_amount: 11 for each of 365 zone_a_days_lived = 4015 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "zone_a_additional_residency_amount: 11 for each of 365 "
        "zone_a_additional_residency_days_checked = 4015 (half-up to 0.01)"
    ) in rendered
    assert (
        "zone_a_residency_amount: zone_a_basic_residency_amount 4015 "
        "+ zone_a_additional_residency_amount 4015 = 8030"
    ) in rendered
    assert (
        "zone_a_residency_after_work_site: zone_a_residency_amount 8030 "
        "less zone_a_special_work_site_benefits 0, not below 0 = 8030"
    ) in rendered
    assert (
        "zone_b_basic_residency_amount: 5.5 for each of 0 zone_b_days_lived = 0 (half-up to 0.01)"
    ) in rendered
    assert (
        "residency_amount: zone_a_residency_after_work_site 8030 "
        "+ zone_b_residency_after_work_site 0 = 8030"
    ) in rendered
    assert "residency_net_income_limit: 20% of net_income 50000 (half-up to 0.01)" in rendered
    assert (
        "residency_deduction: lesser of residency_amount 8030 "
        "and residency_net_income_limit 10000 = 8030"
    ) in rendered
    assert (
        "northern_residents_deductions: residency_deduction 8030 + travel_deduction 0 = 8030"
    ) in rendered


def test_example_1_zone_a_for_292_days_claims_the_basic_and_the_additional_amount() -> None:
    # Example 1: "You can claim $11 for each day that you lived in Yellowknife (292 days) and an
    # additional residency amount of $11 per day". Lines 1 and 2 are each 292 x 11.00 = 3,212.00,
    # line 3 6,424.00; net income 100,000 so line 12 is 20,000.00 and line 13 6,424.00.
    worksheet = northern("100000", zone_a_days_lived=292, zone_a_additional_residency_days=292)

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("6424.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("20000.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("6424.00")


def test_example_2_zone_b_for_292_days_claims_5_50_a_day_for_each_amount() -> None:
    # Example 2: "You can claim $5.50 for each day that you lived in Vanrena (292 days) and an
    # additional residency amount of $5.50 per day". Lines 6 and 7 are each 292 x 5.50 = 1,606.00,
    # line 8 and line 10 3,212.00 (line 9 is 0), line 5 is 0, line 11 3,212.00; net income 100,000
    # so line 12 is 20,000.00 and line 13 3,212.00.
    worksheet = northern("100000", zone_b_days_lived=292, zone_b_additional_residency_days=292)

    assert worksheet.get(ZONE_B_BASIC_RESIDENCY_AMOUNT).value == D("1606.00")
    assert worksheet.get(ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT).value == D("1606.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("3212.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("0")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("3212.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("3212.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("3212.00")


def test_zone_b_for_365_days_without_the_additional_amount() -> None:
    # Line 6 365 x 5.50 = 2,007.50; line 7 0 x 5.50 = 0.00; line 8 2,007.50; line 9 0, line 10
    # 2,007.50; line 5 is 0, so line 11 is 2,007.50, under line 12's 10,000.00 (50,000 x 20%).
    worksheet = northern(zone_b_days_lived=365)

    assert worksheet.get(ZONE_B_BASIC_RESIDENCY_AMOUNT).value == D("2007.50")
    assert worksheet.get(ZONE_B_ADDITIONAL_RESIDENCY_AMOUNT).value == D("0.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("2007.50")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("2007.50")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("2007.50")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("10000.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("2007.50")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "zone_b_basic_residency_amount: 5.5 for each of 365 zone_b_days_lived = 2007.5 "
        "(half-up to 0.01)"
    ) in rendered


def test_a_filer_who_lived_in_both_zones_adds_the_two_residency_amounts() -> None:
    # Zone A 200 days basic and additional: lines 1 and 2 are each 200 x 11.00 = 2,200.00, line 3
    # and line 5 4,400.00. Zone B 165 days: line 6 165 x 5.50 = 907.50, line 8 and line 10
    # 907.50. Line 11 is 4,400.00 + 907.50 = 5,307.50, under line 12's 10,000.00.
    worksheet = northern(
        zone_a_days_lived=200, zone_a_additional_residency_days=200, zone_b_days_lived=165
    )

    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("4400.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("907.50")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("5307.50")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("5307.50")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("5307.50")


def test_the_special_work_site_benefits_come_off_each_zone_before_the_two_are_added() -> None:
    # Zone A 200 days basic and additional: line 3 4,400.00, line 4 (box 31) 1,000.00, line 5
    # 3,400.00. Zone B 165 days: line 8 907.50, line 9 100.00, line 10 807.50. Line 11 is
    # 3,400.00 + 807.50 = 4,207.50, under line 12's 10,000.00.
    worksheet = northern(
        zone_a_days_lived=200,
        zone_a_additional_residency_days=200,
        zone_a_special_work_site_benefits="1000.00",
        zone_b_days_lived=165,
        zone_b_special_work_site_benefits="100.00",
    )

    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("4400.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("3400.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("907.50")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("807.50")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("4207.50")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("4207.50")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "zone_a_residency_after_work_site: zone_a_residency_amount 4400 "
        "less zone_a_special_work_site_benefits 1000, not below 0 = 3400"
    ) in rendered


def test_work_site_benefits_above_a_zones_amount_leave_zero_not_a_negative_for_that_zone() -> None:
    # Line 5 "Line 3 minus line 4 (if negative, enter "0")": Zone A 100 days basic, line 3 1,100.00,
    # line 4 1,500.00, line 5 0 (not -400). Line 10: Zone B 100 days, line 8 550.00, line 9
    # 550.00, line 10 0. The zero does not take the other zone's amount down: Zone B 365 days
    # next to the Zone A 0 is 2,007.50 (see above); here both are 0, so line 11 is 0.
    worksheet = northern(
        zone_a_days_lived=100,
        zone_a_special_work_site_benefits="1500",
        zone_b_days_lived=100,
        zone_b_special_work_site_benefits="550.00",
    )

    assert worksheet.get(ZONE_A_RESIDENCY_AMOUNT).value == D("1100.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("0")
    assert worksheet.get(ZONE_B_RESIDENCY_AMOUNT).value == D("550.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("0")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("0")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("0")


def test_a_zone_with_work_site_benefits_above_its_amount_does_not_lower_the_other_zone() -> None:
    # Zone A 100 days (1,100.00) with box 31 of 1,500.00: line 5 is 0 whatever line 4 is above
    # line 3. Zone B 365 days: line 10 2,007.50. Line 11 is 0 + 2,007.50 = 2,007.50, not
    # 2,007.50 - 400.00.
    worksheet = northern(
        zone_a_days_lived=100,
        zone_a_special_work_site_benefits="1500",
        zone_b_days_lived=365,
    )

    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("0")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("2007.50")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("2007.50")


def test_line_12_limits_the_residency_deduction_to_20_percent_of_net_income() -> None:
    # Net income 10,000: line 12 is 10,000 x 20% = 2,000.00; Zone A 365 days basic and
    # additional is 8,030.00 on line 11, so line 13, the lesser, is 2,000.00.
    worksheet = northern("10000", zone_a_days_lived=365, zone_a_additional_residency_days=365)

    assert worksheet.get(RESIDENCY_AMOUNT).value == D("8030.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("2000.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("2000.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("2000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("8000.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "residency_deduction: lesser of residency_amount 8030 "
        "and residency_net_income_limit 2000 = 2000"
    ) in rendered


def test_line_12_is_the_amount_when_line_11_is_exactly_20_percent_of_net_income() -> None:
    # Net income 40,150: line 12 is 8,030.00, equal to line 11 (Zone A 365 and 365).
    worksheet = northern("40150", zone_a_days_lived=365, zone_a_additional_residency_days=365)

    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("8030.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("8030.00")


def test_no_net_income_leaves_no_residency_deduction() -> None:
    # Line 12 is 0 x 20% = 0.00, so line 13 is 0 whatever line 11 is.
    worksheet = northern("0", zone_a_days_lived=365, zone_a_additional_residency_days=365)

    assert worksheet.get(RESIDENCY_AMOUNT).value == D("8030.00")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("0")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("0")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("0")


def test_the_limit_on_net_income_is_rounded_half_up_to_the_cent() -> None:
    # 99.99 x 20% = 19.998, rounded half-up to 20.00 (line 12 is a dollars-and-cents box).
    worksheet = northern("99.99", zone_a_days_lived=365, zone_a_additional_residency_days=365)

    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("20.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("20.00")


def test_no_days_empty_trip_and_individual_lists_leave_the_deduction_at_zero() -> None:
    # Every input zero and both lists empty: lines 1 to 19 are 0, line 12 is 20% of the net
    # income of 50,000, which is not a deduction by itself, and taxable income is net income.
    worksheet = northern()

    assert worksheet.get(RESIDENCY_AMOUNT).value == D("0")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("10000.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("0")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("0")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("0")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("0")
    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("0")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("50000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "travel_total_zone_a: no items = 0" in rendered
    assert "travel_total_zone_b: no items = 0" in rendered
    assert "standard_amount_allocated: no items = 0" in rendered


def test_example_3_one_trip_from_zone_a_is_the_lowest_of_5000_1500_and_400() -> None:
    # Example 3: column 3 $5,000 (the allowance), column 4 $1,500 (the trip), column 5 $400 (the
    # lowest return airfare): "you enter $400 under the "Zone A" column". Amount A is 400, box B
    # 0, line 14 400, line 15 0 x 50% = 0.00, line 16 400.00; no residency claimed, so line 17
    # is 0, line 18 400.00 and line 19 (line 25500) 400.00.
    worksheet = northern(travel_trips=(trip(1, ZONE_A, "5000", "1500", "400"),))

    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("400")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("0")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("0")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("400")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("0")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("400")
    assert worksheet.get(TAXABLE_INCOME).value == D("49600")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "travel_total_zone_a: item 1: lesser of trip_benefit_or_standard_amount 5000 "
        "and trip_travel_expenses 1500 and trip_lowest_return_airfare 400 = 400"
    ) in rendered
    assert "travel_total_zone_a: item 1 400 = 400" in rendered
    assert "travel_total_zone_b: no items = 0" in rendered
    assert "travel_zone_b_deduction: 50% of travel_total_zone_b 0 (half-up to 0.01)" in rendered
    assert (
        "travel_deduction: travel_total_zone_a 400 + travel_zone_b_deduction 0 = 400"
    ) in rendered


def test_example_4_trips_of_three_individuals_with_chart_a_row_c_of_0_1200_and_1200() -> None:
    # Example 4 (the example does not say which zone Whitehorse is in: Zone A here): her trip 1
    # (1,500, 1,300, 750) 750, trip 2 (1,500, 800, 900) 800, the spouse's trip 1 (400, 400, 600)
    # 400 and trip 2 (800, 850, 900) 800 and the child's (1,200, 1,500, 900) 900: amount A is
    # 750 + 800 + 400 + 800 + 900 = 3,650. Chart A: Individual 1 $0, Individual 2 $1,200 and
    # Individual 3 $1,200 in row C, 2,400 in all. Line 14 3,650, line 15 0.00, line 16 3,650.00.
    worksheet = northern(
        travel_trips=(
            trip(1, ZONE_A, "1500", "1300", "750"),
            trip(1, ZONE_A, "1500", "800", "900"),
            trip(2, ZONE_A, "400", "400", "600"),
            trip(2, ZONE_A, "800", "850", "900"),
            trip(3, ZONE_A, "1200", "1500", "900"),
        ),
        travel_individuals=(
            individual(1, "0"),
            individual(2, "1200"),
            individual(3, "1200"),
        ),
    )

    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("3650")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("0")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("3650.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("3650.00")
    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("2400")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "travel_total_zone_a: item 1: lesser of trip_benefit_or_standard_amount 1500 "
        "and trip_travel_expenses 1300 and trip_lowest_return_airfare 750 = 750"
    ) in rendered
    assert (
        "travel_total_zone_a: item 1 750 + item 2 800 + item 3 400 + item 4 800 + item 5 900 = 3650"
    ) in rendered
    assert (
        "standard_amount_allocated: item 2: standard_amount_allocated_1 1200 "
        "+ standard_amount_allocated_2 0 + standard_amount_allocated_3 0 = 1200"
    ) in rendered
    assert "standard_amount_allocated: item 1 0 + item 2 1200 + item 3 1200 = 2400" in rendered


def test_chart_a_feeds_no_line_so_the_deduction_is_the_same_without_it() -> None:
    trips = (trip(1, ZONE_A, "1500", "1300", "750"), trip(2, ZONE_A, "400", "400", "600"))

    without = northern(travel_trips=trips)
    with_chart_a = northern(
        travel_trips=trips, travel_individuals=(individual(2, "400", "400", "400"),)
    )

    assert without.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("1150")
    assert with_chart_a.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("1150")
    assert without.get(STANDARD_AMOUNT_ALLOCATED).value == D("0")
    assert with_chart_a.get(STANDARD_AMOUNT_ALLOCATED).value == D("1200")


def test_trips_from_both_zones_take_zone_a_whole_and_half_of_zone_b() -> None:
    # Zone A: her trips (750 and 800) = 1,550, line 14. Zone B: the spouse's trips (400 and 800) =
    # 1,200, box B; line 15 1,200 x 50% = 600.00; line 16 1,550 + 600.00 = 2,150.00. Residency
    # Zone A 365 days basic and additional, net income 50,000: line 13 8,030.00. Line 19 is
    # 8,030.00 + 2,150.00 = 10,180.00: the travel deduction is not limited to net income.
    worksheet = northern(
        zone_a_days_lived=365,
        zone_a_additional_residency_days=365,
        travel_trips=(
            trip(1, ZONE_A, "1500", "1300", "750"),
            trip(1, ZONE_A, "1500", "800", "900"),
            trip(2, ZONE_B, "400", "400", "600"),
            trip(2, ZONE_B, "800", "850", "900"),
        ),
        travel_individuals=(individual(1), individual(2, "1200")),
    )

    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("1550")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("1200")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("600.00")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("2150.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("8030.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("10180.00")
    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("1200")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("10180.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("39820.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "travel_total_zone_a: item 1 750 + item 2 800 = 1550" in rendered
    assert "travel_total_zone_b: item 3 400 + item 4 800 = 1200" in rendered
    assert "travel_zone_b_deduction: 50% of travel_total_zone_b 1200 (half-up to 0.01)" in rendered
    assert (
        "travel_deduction: travel_total_zone_a 1550 + travel_zone_b_deduction 600 = 2150"
    ) in rendered


def test_the_travel_deduction_is_not_limited_by_the_20_percent_of_net_income() -> None:
    # Net income 1,000: line 12 is 200.00 and line 13 is 200.00 (the lesser of 8,030.00 and
    # 200.00); the travel deduction of 2,150.00 (as above) is added whole by line 19: 2,350.00.
    worksheet = northern(
        "1000",
        zone_a_days_lived=365,
        zone_a_additional_residency_days=365,
        travel_trips=(
            trip(1, ZONE_A, "1500", "1300", "750"),
            trip(1, ZONE_A, "1500", "800", "900"),
            trip(2, ZONE_B, "400", "400", "600"),
            trip(2, ZONE_B, "800", "850", "900"),
        ),
    )

    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("200.00")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("2150.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("2350.00")


def test_any_number_of_medical_trips_are_claimed_in_both_zones() -> None:
    # "You can also claim any number of medical trips": four trips by one individual from Zone A,
    # each at its lowest amount, 300 (500, 2,000, 300), 1,000 (5,000, 1,000, 1,200), 1,200
    # (1,200, 1,200, 1,500) and 1,200 (1,200, 1,600, 2,000): 3,700. Three from Zone B: 900
    # (2,000, 900, 1,000), 1,200 (1,200, 1,200, 1,200) and 50 (50, 60, 70): 2,150, at 50% 1,075.00.
    # Line 16 is 3,700 + 1,075.00 = 4,775.00.
    worksheet = northern(
        travel_trips=(
            trip(1, ZONE_A, "500", "2000", "300"),
            trip(1, ZONE_A, "5000", "1000", "1200"),
            trip(1, ZONE_A, "1200", "1200", "1500"),
            trip(1, ZONE_A, "1200", "1600", "2000"),
            trip(2, ZONE_B, "2000", "900", "1000"),
            trip(2, ZONE_B, "1200", "1200", "1200"),
            trip(2, ZONE_B, "50", "60", "70"),
        )
    )

    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("3700")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("2150")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("1075.00")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("4775.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("4775.00")


def test_half_of_an_odd_zone_b_total_is_rounded_half_up_to_the_cent() -> None:
    # Box B 0.03 (one trip of 0.03, 5, 9): line 15 is 0.03 x 50% = 0.015, a tie, up to 0.02.
    worksheet = northern(travel_trips=(trip(1, ZONE_B, "0.03", "5", "9"),))

    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("0.03")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("0.02")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("0.02")


def test_two_individuals_with_a_row_c_over_1200_are_refused_naming_the_second() -> None:
    # Individual 1: 400 + 400 + 400 = 1,200, allowed ("not more than $1,200"). Individual 2:
    # 700 + 600 + 0 = 1,300, more than 1,200: an input error, not a cap.
    individuals = (individual(1, "400", "400", "400"), individual(2, "700", "600", "0"))

    with pytest.raises(
        InputAboveBoundError, match=r"item 2.*This total cannot be more than \$1,200\."
    ):
        northern(travel_individuals=individuals)


def test_a_row_c_of_exactly_1200_for_each_of_two_individuals_is_allowed() -> None:
    worksheet = northern(
        travel_individuals=(individual(1, "400", "400", "400"), individual(2, "1200"))
    )

    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("2400")


def test_a_trip_in_neither_zone_is_refused_naming_the_item() -> None:
    trips = (trip(1, ZONE_A, "100", "200", "300"), trip(1, 3, "100", "200", "300"))

    with pytest.raises(InvalidRecordError, match=r"item 2.*trip_zone"):
        northern(travel_trips=trips)


def test_the_northern_residents_deductions_come_off_net_income_with_the_other_deductions() -> None:
    # Line 25700 "Add lines 58 to 67.": security options deduction (line 24900) 1,000.00, the
    # northern residents deductions (line 25500) 8,030.00 and additional deductions (line 25600)
    # 500.00: 9,530.00; taxable income (line 26000) is 50,000 - 9,530.00 = 40,470.00.
    worksheet = northern(
        zone_a_days_lived=365,
        zone_a_additional_residency_days=365,
        t4_security_options_boxes_39_and_91="1000",
        additional_deductions="500",
    )

    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("8030.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("9530.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("40470.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "deductions_from_net_income: canadian_armed_forces_and_police_deduction 0 "
        "+ security_options_deductions 1000 + other_payments_deduction 0 "
        "+ limited_partnership_losses_of_other_years_checked 0 "
        "+ non_capital_losses_on_line_25200 0 "
        "+ net_capital_losses_of_other_years 0 + qbt_capital_gains_deduction 0 "
        "+ capital_gains_deduction 0 + northern_residents_deductions 8030 "
        "+ additional_deductions_total 500 = 9530"
    ) in rendered


def test_return_ss_northern_residents_deductions_come_off_net_income_to_taxable_income() -> None:
    # Net income 50,000.00 - 465.00 = 49,535.00. Zone A: lines 1 and 2 each 200 x 11.00 =
    # 2,200.00, line 3 4,400.00, line 5 4,400.00. Zone B: line 6 165 x 5.50 = 907.50, line 7
    # 0.00, line 8 907.50, line 9 100.00, line 10 807.50. Line 11 5,207.50; line 12 49,535.00 x
    # 20% = 9,907.00; line 13 5,207.50. Chart B: Zone A 750 + 800 = 1,550, Zone B 400 + 800 =
    # 1,200, line 15 600.00, line 16 2,150.00. Line 19 5,207.50 + 2,150.00 = 7,357.50, so
    # taxable income is 49,535.00 - 7,357.50 = 42,177.50. Chart A: row C 0 and 1,200: 1,200.
    worksheet = return_s()

    assert worksheet.get(NET_INCOME).value == D("49535.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("4400.00")
    assert worksheet.get(ZONE_B_RESIDENCY_AFTER_WORK_SITE).value == D("807.50")
    assert worksheet.get(RESIDENCY_AMOUNT).value == D("5207.50")
    assert worksheet.get(RESIDENCY_NET_INCOME_LIMIT).value == D("9907.00")
    assert worksheet.get(RESIDENCY_DEDUCTION).value == D("5207.50")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_A).value == D("1550")
    assert worksheet.get(TRAVEL_TOTAL_ZONE_B).value == D("1200")
    assert worksheet.get(TRAVEL_ZONE_B_DEDUCTION).value == D("600.00")
    assert worksheet.get(TRAVEL_DEDUCTION).value == D("2150.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("7357.50")
    assert worksheet.get(STANDARD_AMOUNT_ALLOCATED).value == D("1200")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("7357.50")
    assert worksheet.get(TAXABLE_INCOME).value == D("42177.50")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("6115.74")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4866.43")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-133.57")


# --- day counts (`ca/count_at_most`) ------------------------------------------------------
#
# T2222 Step 2 lines 1 and 6 ask for the days lived in a zone in 2025, and lines 2 and 7 for the
# days that qualify for the additional residency amount. The form prints no maximum for the days
# lived, so they are used as typed (even above 365). The additional residency amount is claimed
# "for the days you used to calculate your basic residency amount", so the additional days are
# refused above the days lived.


def test_zone_a_366_days_lived_is_accepted_and_is_366_times_11() -> None:
    # Line 1 366 x $11.00 = 4,026.00; no additional days, so line 5 4,026.00, under the 20% of
    # net income 50,000 (10,000.00).
    worksheet = northern(zone_a_days_lived=366)

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("4026.00")
    assert worksheet.get(ZONE_A_RESIDENCY_AFTER_WORK_SITE).value == D("4026.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("4026.00")


def test_zone_b_366_days_lived_is_accepted_and_is_366_times_5_50() -> None:
    worksheet = northern(zone_b_days_lived=366)

    assert worksheet.get(ZONE_B_BASIC_RESIDENCY_AMOUNT).value == D("2013.00")
    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("2013.00")


def test_zone_a_additional_days_may_exceed_365_up_to_the_days_lived() -> None:
    worksheet = northern(zone_a_days_lived=400, zone_a_additional_residency_days=400)

    assert worksheet.get(ZONE_A_BASIC_RESIDENCY_AMOUNT).value == D("4400.00")
    assert worksheet.get(ZONE_A_ADDITIONAL_RESIDENCY_AMOUNT).value == D("4400.00")


@pytest.mark.parametrize(
    ("inputs", "message"),
    [
        (
            {"zone_a_days_lived": 10, "zone_a_additional_residency_days": 300},
            "ca/zone_a_additional_residency_days 300 is above ca/zone_a_days_lived 10",
        ),
        (
            {"zone_b_days_lived": 10, "zone_b_additional_residency_days": 300},
            "ca/zone_b_additional_residency_days 300 is above ca/zone_b_days_lived 10",
        ),
        (
            {"zone_a_days_lived": 365, "zone_a_additional_residency_days": 366},
            "ca/zone_a_additional_residency_days 366 is above ca/zone_a_days_lived 365",
        ),
    ],
    ids=[
        "zone_a_additional_300_over_10_lived",
        "zone_b_additional_300_over_10_lived",
        "zone_a_additional_366_over_365_lived",
    ],
)
def test_an_impossible_t2222_day_count_is_refused_naming_the_input(
    inputs: dict[str, Any], message: str
) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        northern(**inputs)

    assert message in str(raised.value)


def test_zone_a_with_10_days_lived_and_10_additional_days_deducts_220() -> None:
    # 10 days at $11.00 for the basic amount (110.00) and 10 days for the additional amount
    # (110.00): the additional amount is for the days used to calculate the basic amount.
    worksheet = northern(zone_a_days_lived=10, zone_a_additional_residency_days=10)

    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("220.00")


def test_zone_b_for_365_days_with_the_additional_amount_deducts_4015() -> None:
    # 365 days at $5.50 for each amount: 2,007.50 + 2,007.50 = 4,015.00.
    worksheet = northern(zone_b_days_lived=365, zone_b_additional_residency_days=365)

    assert worksheet.get(NORTHERN_RESIDENTS_DEDUCTIONS).value == D("4015.00")
