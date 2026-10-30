"""Registered and money kinds of the federal catalog family `non_refundable_credits`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    ADOPTION_CHILD_EXPENSES,
    ADOPTION_CREDIT,
    ADOPTION_EXPENSE_CHILDREN,
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
    CANADA_EMPLOYMENT_AMOUNT,
    CANADA_EMPLOYMENT_AMOUNT_INCOME,
    CANADA_TRAINING_CREDIT_BASIS,
    CANADA_TRAINING_CREDIT_CLAIMED,
    CANADA_TRAINING_CREDIT_LIMIT,
    CANADA_TRAINING_CREDIT_MAXIMUM,
    CANADIAN_TUITION_AVAILABLE,
    CANADIAN_TUITION_FEES,
    CANADIAN_TUITION_FEES_CHECKED,
    CANADIAN_TUITION_INSTITUTIONS,
    CAPITAL_GIFT_GAINS_DEDUCTION,
    CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED,
    CAPITAL_GIFT_TAXABLE_GAINS,
    CAPITAL_GIFTS_LIMIT_ADDITION,
    CAPITAL_GIFTS_TOTAL,
    CAPITAL_PROPERTY_GIFTS,
    CHARITABLE_DONATIONS,
    CHARITABLE_DONATIONS_CLAIMED,
    CHARITABLE_DONATIONS_LIMIT,
    CPP_BASE_CONTRIBUTIONS,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDIT_AMOUNTS_SUBTOTAL,
    CURRENT_YEAR_TUITION_AVAILABLE,
    CURRENT_YEAR_TUITION_CLAIMED,
    DEPRECIABLE_GIFT_CAPITAL_COST,
    DEPRECIABLE_GIFT_NET_PROCEEDS,
    DEPRECIABLE_GIFT_PROCEEDS_OR_COST,
    DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION,
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
    ECOLOGICAL_AND_CULTURAL_GIFTS,
    ECOLOGICAL_GIFTS_BEFORE_2016,
    EI_PREMIUMS,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_SURTAX_OUTSIDE_CANADA,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FEDERAL_TAX_WITH_SPLIT_INCOME,
    FEDERAL_TAX_WITH_SURTAX,
    FEDERAL_TUITION_AMOUNT,
    FIRST_NATIONS_ABATEMENT,
    FIRST_TIER_DONATION_CREDIT,
    FOREIGN_CHARITY_DONATIONS,
    FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
    FOREIGN_TAX_CREDIT_NET_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
    FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
    FOREIGN_TUITION_FEES,
    GOVERNMENT_DONATIONS,
    HIGH_INCOME_DONATION_CREDIT,
    HIGH_INCOME_DONATIONS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED,
    HOME_ACCESSIBILITY_CREDIT,
    HOME_ACCESSIBILITY_EXPENSES,
    HOME_ACCESSIBILITY_LINE_2,
    HOME_BUYERS_CLAIM,
    HOME_BUYERS_CREDIT,
    HOME_BUYERS_MAXIMUM,
    ITC_RECAPTURE,
    ITC_RECAPTURE_AT_15_PERCENT,
    ITC_RECAPTURE_AT_20_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    PENSION_ANNUITY_CONDITIONS_MET,
    PENSION_ANNUITY_CONDITIONS_MET_CHECKED,
    PENSION_ANNUITY_PAYMENTS,
    PENSION_CHART_LINE_1,
    PENSION_CHART_LINE_5,
    PENSION_CHART_LINE_5_CHECKED,
    PENSION_CHART_LINE_6,
    PENSION_CHART_LINE_7,
    PENSION_CHART_LINE_8,
    PENSION_FOREIGN_INCOME,
    PENSION_FOREIGN_INCOME_CHECKED,
    PENSION_INCOME_CREDIT,
    PENSION_RRIF_TRANSFERRED,
    PENSION_US_IRA_INCOME,
    PENSION_WORKSHEET_AMOUNT,
    REGULAR_RATE_DONATION_CREDIT,
    REGULAR_RATE_DONATIONS,
    SEARCH_AND_RESCUE_CONDITIONS_MET,
    SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
    SEARCH_AND_RESCUE_CREDIT,
    SPOUSE_ADJUSTED_TAXABLE_INCOME,
    SPOUSE_CREDITS_USED,
    SPOUSE_DESIGNATED_TUITION,
    SPOUSE_DESIGNATED_TUITION_CHECKED,
    SPOUSE_DESIGNATED_TUITION_MAXIMUM,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_NOT_SEPARATED_90_DAYS,
    SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED,
    SPOUSE_RETURN_AGE_AMOUNT,
    SPOUSE_RETURN_AGE_AMOUNT_CHECKED,
    SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED,
    SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_DISABILITY_AMOUNT,
    SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED,
    SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_FEDERAL_BASIC_TAX,
    SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT,
    SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT,
    SPOUSE_RETURN_LINE_96,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED,
    SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM,
    SPOUSE_RETURN_TAXABLE_INCOME,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    SPOUSE_UNUSED_AMOUNTS,
    STUDENT_LOAN_INTEREST,
    T2203_FEDERAL_SURTAX_OUTSIDE_CANADA,
    T2203_HAS_TAX_ON_SPLIT_INCOME,
    T2203_LINE_5,
    T2203_LINE_6,
    T2203_LINE_8,
    TAXABLE_INCOME_OVER_DONATION_THRESHOLD,
    TOP_UP_CREDITS_BASE,
    TOP_UP_EXCESS,
    TOP_UP_TAX_CREDIT,
    TOP_UP_THRESHOLD,
    TOSI_ADJUSTED_TAXABLE_INCOME,
    TOTAL_CHARITABLE_DONATIONS,
    TOTAL_TUITION_AVAILABLE,
    TUITION_AVAILABLE_TO_TRANSFER,
    TUITION_CANNOT_BE_FULL_TIME_STUDENT,
    TUITION_CARRIED_FORWARD,
    TUITION_FULL_TIME_MONTHS,
    TUITION_INCOME_BASE,
    TUITION_INCOME_LESS_CREDITS,
    TUITION_INCOME_REMAINING,
    TUITION_INCOME_WITH_TOSI,
    TUITION_PART_TIME_MONTHS,
    TUITION_TRANSFER_ELECTED,
    TUITION_TRANSFER_LIMIT,
    TUITION_TRANSFER_STUDENTS,
    TUITION_TRANSFERRED,
    TUITION_TRANSFERRED_FROM_CHILD,
    TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
    TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM,
    UNIVERSITY_DONATIONS_OUTSIDE_CANADA,
    UNUSED_FEDERAL_TUITION,
    UNUSED_TUITION_CLAIMED,
    UNUSED_TUITION_FROM_2024,
    VOLUNTEER_AMOUNT_MAXIMUM,
    VOLUNTEER_CREDITS_CHECKED,
    VOLUNTEER_CREDITS_CLAIMED,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
    VOLUNTEER_FIREFIGHTERS_CREDIT,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, SIGNED


def test_the_non_refundable_credits_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/non_refundable_credit_amounts") is NON_REFUNDABLE_CREDIT_AMOUNTS
    assert registry.get("ca/cpp_base_contributions") is CPP_BASE_CONTRIBUTIONS
    assert (
        registry.get("ca/cpp_base_contributions_on_self_employment")
        is CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT
    )
    assert registry.get("ca/ei_premiums") is EI_PREMIUMS
    assert registry.get("ca/ei_premiums_on_self_employment") is EI_PREMIUMS_ON_SELF_EMPLOYMENT
    assert registry.get("ca/canada_employment_amount") is CANADA_EMPLOYMENT_AMOUNT
    assert registry.get("ca/canada_employment_amount_income") is CANADA_EMPLOYMENT_AMOUNT_INCOME
    assert registry.get("ca/non_refundable_tax_credits") is NON_REFUNDABLE_TAX_CREDITS
    assert (
        registry.get("ca/itc_recapture_expenditure_at_15_percent")
        is ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT
    )
    assert (
        registry.get("ca/itc_recapture_expenditure_at_20_percent")
        is ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT
    )
    assert registry.get("ca/itc_recapture_at_15_percent") is ITC_RECAPTURE_AT_15_PERCENT
    assert registry.get("ca/itc_recapture_at_20_percent") is ITC_RECAPTURE_AT_20_PERCENT
    assert registry.get("ca/itc_recapture") is ITC_RECAPTURE
    assert registry.get("ca/federal_tax_with_itc_recapture") is FEDERAL_TAX_WITH_ITC_RECAPTURE
    assert registry.get("ca/charitable_donations") is CHARITABLE_DONATIONS
    assert registry.get("ca/government_donations") is GOVERNMENT_DONATIONS
    assert (
        registry.get("ca/university_donations_outside_canada")
        is UNIVERSITY_DONATIONS_OUTSIDE_CANADA
    )
    assert registry.get("ca/foreign_charity_donations") is FOREIGN_CHARITY_DONATIONS
    assert registry.get("ca/ecological_and_cultural_gifts") is ECOLOGICAL_AND_CULTURAL_GIFTS
    assert registry.get("ca/ecological_gifts_before_2016") is ECOLOGICAL_GIFTS_BEFORE_2016
    assert (
        registry.get("ca/depreciable_gift_recaptured_depreciation")
        is DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION
    )
    assert registry.get("ca/depreciable_gift_net_proceeds") is DEPRECIABLE_GIFT_NET_PROCEEDS
    assert registry.get("ca/depreciable_gift_capital_cost") is DEPRECIABLE_GIFT_CAPITAL_COST
    assert registry.get("ca/capital_gift_taxable_gains") is CAPITAL_GIFT_TAXABLE_GAINS
    assert registry.get("ca/capital_gift_gains_deduction") is CAPITAL_GIFT_GAINS_DEDUCTION
    assert registry.get("ca/depreciable_gift_proceeds_or_cost") is DEPRECIABLE_GIFT_PROCEEDS_OR_COST
    assert registry.get("ca/depreciable_gifts") is DEPRECIABLE_GIFTS
    assert registry.get("ca/capital_property_gifts") is CAPITAL_PROPERTY_GIFTS
    assert registry.get("ca/total_charitable_donations") is TOTAL_CHARITABLE_DONATIONS
    assert registry.get("ca/donation_limit_on_net_income") is DONATION_LIMIT_ON_NET_INCOME
    assert registry.get("ca/capital_gifts_total") is CAPITAL_GIFTS_TOTAL
    assert registry.get("ca/capital_gifts_limit_addition") is CAPITAL_GIFTS_LIMIT_ADDITION
    assert registry.get("ca/donation_limit_with_capital_gifts") is DONATION_LIMIT_WITH_CAPITAL_GIFTS
    assert registry.get("ca/charitable_donations_limit") is CHARITABLE_DONATIONS_LIMIT
    assert registry.get("ca/charitable_donations_claimed") is CHARITABLE_DONATIONS_CLAIMED
    assert registry.get("ca/donations_and_gifts_total") is DONATIONS_AND_GIFTS_TOTAL
    assert registry.get("ca/donation_first_tier_maximum") is DONATION_FIRST_TIER_MAXIMUM
    assert registry.get("ca/donations_first_tier") is DONATIONS_FIRST_TIER
    assert registry.get("ca/donations_over_first_tier") is DONATIONS_OVER_FIRST_TIER
    assert (
        registry.get("ca/donations_over_first_tier_after_2016_gifts")
        is DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS
    )
    assert registry.get("ca/donation_high_income_threshold") is DONATION_HIGH_INCOME_THRESHOLD
    assert (
        registry.get("ca/taxable_income_over_donation_threshold")
        is TAXABLE_INCOME_OVER_DONATION_THRESHOLD
    )
    assert registry.get("ca/high_income_donations") is HIGH_INCOME_DONATIONS
    assert registry.get("ca/high_income_donation_credit") is HIGH_INCOME_DONATION_CREDIT
    assert registry.get("ca/regular_rate_donations") is REGULAR_RATE_DONATIONS
    assert registry.get("ca/regular_rate_donation_credit") is REGULAR_RATE_DONATION_CREDIT
    assert registry.get("ca/first_tier_donation_credit") is FIRST_TIER_DONATION_CREDIT
    assert registry.get("ca/donations_and_gifts_credit") is DONATIONS_AND_GIFTS_CREDIT
    assert registry.get("ca/credit_amounts_at_credit_rate") is CREDIT_AMOUNTS_AT_CREDIT_RATE
    assert registry.get("ca/top_up_credits_base") is TOP_UP_CREDITS_BASE
    assert registry.get("ca/top_up_threshold") is TOP_UP_THRESHOLD
    assert registry.get("ca/top_up_excess") is TOP_UP_EXCESS
    assert registry.get("ca/top_up_tax_credit") is TOP_UP_TAX_CREDIT
    assert registry.get("ca/federal_tax_on_split_income") is FEDERAL_TAX_ON_SPLIT_INCOME
    assert registry.get("ca/federal_tax_with_split_income") is FEDERAL_TAX_WITH_SPLIT_INCOME
    assert registry.get("ca/tosi_adjusted_taxable_income") is TOSI_ADJUSTED_TAXABLE_INCOME
    assert registry.get("ca/canadian_tuition_fees") is CANADIAN_TUITION_FEES
    assert registry.get("ca/canadian_tuition_institutions") is CANADIAN_TUITION_INSTITUTIONS
    assert registry.get("ca/canadian_tuition_fees_checked") is CANADIAN_TUITION_FEES_CHECKED
    assert registry.get("ca/canada_training_credit_limit") is CANADA_TRAINING_CREDIT_LIMIT
    assert registry.get("ca/canada_training_credit_claimed") is CANADA_TRAINING_CREDIT_CLAIMED
    assert registry.get("ca/foreign_tuition_fees") is FOREIGN_TUITION_FEES
    assert registry.get("ca/unused_tuition_from_2024") is UNUSED_TUITION_FROM_2024
    assert registry.get("ca/tuition_transfer_elected") is TUITION_TRANSFER_ELECTED
    assert registry.get("ca/tuition_transferred_from_child") is TUITION_TRANSFERRED_FROM_CHILD
    assert registry.get("ca/tuition_transfer_students") is TUITION_TRANSFER_STUDENTS
    assert registry.get("ca/canada_training_credit_basis") is CANADA_TRAINING_CREDIT_BASIS
    assert registry.get("ca/canada_training_credit_maximum") is CANADA_TRAINING_CREDIT_MAXIMUM
    assert registry.get("ca/canadian_tuition_available") is CANADIAN_TUITION_AVAILABLE
    assert registry.get("ca/current_year_tuition_available") is CURRENT_YEAR_TUITION_AVAILABLE
    assert registry.get("ca/total_tuition_available") is TOTAL_TUITION_AVAILABLE
    assert registry.get("ca/tuition_income_base") is TUITION_INCOME_BASE
    assert registry.get("ca/tuition_income_with_tosi") is TUITION_INCOME_WITH_TOSI
    assert registry.get("ca/credit_amounts_subtotal") is CREDIT_AMOUNTS_SUBTOTAL
    assert registry.get("ca/tuition_income_less_credits") is TUITION_INCOME_LESS_CREDITS
    assert registry.get("ca/unused_tuition_claimed") is UNUSED_TUITION_CLAIMED
    assert registry.get("ca/tuition_income_remaining") is TUITION_INCOME_REMAINING
    assert registry.get("ca/current_year_tuition_claimed") is CURRENT_YEAR_TUITION_CLAIMED
    assert registry.get("ca/federal_tuition_amount") is FEDERAL_TUITION_AMOUNT
    assert registry.get("ca/unused_federal_tuition") is UNUSED_FEDERAL_TUITION
    assert registry.get("ca/tuition_transfer_limit") is TUITION_TRANSFER_LIMIT
    assert registry.get("ca/tuition_available_to_transfer") is TUITION_AVAILABLE_TO_TRANSFER
    assert registry.get("ca/tuition_transferred") is TUITION_TRANSFERRED
    assert (
        registry.get("ca/tuition_transferred_from_child_maximum")
        is TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM
    )
    assert (
        registry.get("ca/tuition_transferred_from_child_checked")
        is TUITION_TRANSFERRED_FROM_CHILD_CHECKED
    )
    assert registry.get("ca/tuition_carried_forward") is TUITION_CARRIED_FORWARD
    assert registry.get("ca/spouse_return_age_amount") is SPOUSE_RETURN_AGE_AMOUNT
    assert (
        registry.get("ca/spouse_return_infirm_children_amount")
        is SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT
    )
    assert (
        registry.get("ca/spouse_return_pension_income_amount")
        is SPOUSE_RETURN_PENSION_INCOME_AMOUNT
    )
    assert registry.get("ca/spouse_return_disability_amount") is SPOUSE_RETURN_DISABILITY_AMOUNT
    assert registry.get("ca/spouse_designated_tuition") is SPOUSE_DESIGNATED_TUITION
    assert registry.get("ca/spouse_return_taxable_income") is SPOUSE_RETURN_TAXABLE_INCOME
    assert registry.get("ca/spouse_return_federal_basic_tax") is SPOUSE_RETURN_FEDERAL_BASIC_TAX
    assert (
        registry.get("ca/spouse_return_basic_personal_amount")
        is SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT
    )
    assert registry.get("ca/spouse_return_line_96") is SPOUSE_RETURN_LINE_96
    assert (
        registry.get("ca/spouse_return_federal_tuition_amount")
        is SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT
    )
    assert registry.get("ca/spouse_transferable_amounts") is SPOUSE_TRANSFERABLE_AMOUNTS
    assert registry.get("ca/spouse_income_for_transfer") is SPOUSE_INCOME_FOR_TRANSFER
    assert registry.get("ca/spouse_credits_used") is SPOUSE_CREDITS_USED
    assert registry.get("ca/spouse_adjusted_taxable_income") is SPOUSE_ADJUSTED_TAXABLE_INCOME
    assert registry.get("ca/spouse_unused_amounts") is SPOUSE_UNUSED_AMOUNTS
    assert registry.get("ca/amounts_transferred_from_spouse") is AMOUNTS_TRANSFERRED_FROM_SPOUSE
    assert registry.get("ca/spouse_not_separated_90_days") is SPOUSE_NOT_SEPARATED_90_DAYS


def test_the_spouse_age_and_pension_maximum_and_checked_kinds_are_registered_beside_the_inputs(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 2 line 1 and line 3 print maxima on the T1 lines they copy ("maximum $9,028" and
    # "maximum $2,000"), and an amount above one is an input error. The maxima are datasets; the
    # checked amounts are the output of `core/at_most`, which the Schedule 2 sum reads in place of
    # the inputs.
    assert registry.kind("ca/spouse_return_age_amount_maximum") is SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM
    assert registry.kind("ca/spouse_return_age_amount_checked") is SPOUSE_RETURN_AGE_AMOUNT_CHECKED
    assert (
        registry.kind("ca/spouse_return_pension_income_amount_maximum")
        is SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM
    )
    assert (
        registry.kind("ca/spouse_return_pension_income_amount_checked")
        is SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED
    )
    for kind in (
        SPOUSE_RETURN_AGE_AMOUNT_MAXIMUM,
        SPOUSE_RETURN_AGE_AMOUNT_CHECKED,
        SPOUSE_RETURN_PENSION_INCOME_AMOUNT_MAXIMUM,
        SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert SPOUSE_RETURN_AGE_AMOUNT_CHECKED is not SPOUSE_RETURN_AGE_AMOUNT
    assert SPOUSE_RETURN_PENSION_INCOME_AMOUNT_CHECKED is not SPOUSE_RETURN_PENSION_INCOME_AMOUNT


def test_the_spouse_designated_tuition_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 2 line 5 and Note 2: "The maximum tuition amount your spouse or common-law partner
    # can transfer to you is $5,000", and an amount above it is an input error, not capped. The
    # maximum is a dataset; the checked amount is the output of `core/at_most`, which the Schedule
    # 2 line 6 sum reads in place of the input.
    assert (
        registry.kind("ca/spouse_designated_tuition_maximum") is SPOUSE_DESIGNATED_TUITION_MAXIMUM
    )
    assert (
        registry.kind("ca/spouse_designated_tuition_checked") is SPOUSE_DESIGNATED_TUITION_CHECKED
    )
    for kind in (SPOUSE_DESIGNATED_TUITION_MAXIMUM, SPOUSE_DESIGNATED_TUITION_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert SPOUSE_DESIGNATED_TUITION_CHECKED is not SPOUSE_DESIGNATED_TUITION


def test_the_spouse_disability_amount_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 2 line 4 "Enter the amount from line 31600 of their return. (Note 1)", and their
    # line 31600 "Enter this amount on line 31600 of your return. (maximum $16,052)" (Federal
    # Worksheet 5000-D1 line 7): an amount above the maximum is an input error, not capped. The
    # maximum is a dataset; the checked amount is the output of `core/at_most`, which the Schedule
    # 2 line 6 sum reads in place of the input.
    assert (
        registry.kind("ca/spouse_return_disability_amount_maximum")
        is SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM
    )
    assert (
        registry.kind("ca/spouse_return_disability_amount_checked")
        is SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED
    )
    for kind in (SPOUSE_RETURN_DISABILITY_AMOUNT_MAXIMUM, SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert SPOUSE_RETURN_DISABILITY_AMOUNT_CHECKED is not SPOUSE_RETURN_DISABILITY_AMOUNT


def test_the_pension_foreign_income_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet for line 31400, line 2 "Foreign pension income included in the amount on
    # line 11500 of your return and deducted on line 25600 of your return": the amount is at most
    # line 25600 "Additional deductions" (`ca/additional_deductions`), so an amount above it is
    # refused as an input error, not capped. The checked amount is the output of `core/at_most`,
    # which the line 5 sum reads in place of the input.
    assert registry.kind("ca/pension_foreign_income_checked") is PENSION_FOREIGN_INCOME_CHECKED
    assert PENSION_FOREIGN_INCOME_CHECKED.value_type is Decimal
    assert PENSION_FOREIGN_INCOME_CHECKED.non_negative is True
    assert PENSION_FOREIGN_INCOME_CHECKED is not PENSION_FOREIGN_INCOME


def test_the_pension_chart_line_5_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet for line 31400, line 5 "Add lines 2 to 4." and line 6 "Line 1 minus line 5":
    # line 5 is refused above line 1 (the amount from line 11500 of the return) as an input error,
    # not capped. The checked amount is the output of `core/at_most`, which line 6 reads as `less`
    # in place of the sum.
    assert registry.kind("ca/pension_chart_line_5_checked") is PENSION_CHART_LINE_5_CHECKED
    assert PENSION_CHART_LINE_5_CHECKED.value_type is Decimal
    assert PENSION_CHART_LINE_5_CHECKED.non_negative is True
    assert PENSION_CHART_LINE_5_CHECKED is not PENSION_CHART_LINE_5


def test_the_spouse_basic_personal_amount_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 2 line 8 prints no maximum, but T1 line 30000 does: "(maximum $16,129)", and an
    # amount above it is an input error. The maximum is a dataset; the checked amount is the output
    # of `core/at_most`, which the Schedule 2 line 11 sum reads in place of the input.
    assert (
        registry.kind("ca/spouse_return_basic_personal_amount_maximum")
        is SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM
    )
    assert (
        registry.kind("ca/spouse_return_basic_personal_amount_checked")
        is SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED
    )
    for kind in (
        SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_MAXIMUM,
        SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT_CHECKED is not SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT


def test_the_capital_gift_gains_deduction_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 9 chart for line 33900, line 2 "Amount of current-year capital gains deduction from
    # capital property donated in 2025", is checked against line 1 "Amount of current-year taxable
    # capital gains from capital property donated in 2025". The checked amount is the output of
    # `core/at_most`, which line 3 "Line 1 minus Line 2" reads in place of the input.
    assert (
        registry.kind("ca/capital_gift_gains_deduction_checked")
        is CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED
    )
    assert CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED is not CAPITAL_GIFT_GAINS_DEDUCTION
    assert CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED.value_type is Decimal
    assert CAPITAL_GIFT_GAINS_DEDUCTION_CHECKED.non_negative is True


def test_the_home_accessibility_claimed_by_others_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet for line 31285, line 3 "Enter the amount claimed by other qualifying
    # individuals ..." is checked against line 2, because line 4 "Line 2 minus line 3" prints no
    # "if negative, enter 0". The checked amount is the output of `core/at_most`, which line 4
    # reads in place of the input.
    assert (
        registry.kind("ca/home_accessibility_claimed_by_others_checked")
        is HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED
    )
    assert HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED is not HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS
    assert HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED.value_type is Decimal
    assert HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED.non_negative is True


def test_the_tuition_transfer_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Line 32400 "Tuition amount transferred from a child or grandchild"
    # (5000-G: "The maximum amount each student can transfer to you is $5,000 minus the amount that
    # they used to reduce their own tax payable."). The bound is the number of students the
    # transfer comes from, a caller count, times $5,000 (the owner's decision), and the transfer is
    # refused above it, not capped. The bound is `ca/tuition_transferred_from_child_maximum`, the
    # output of `core/per_unit_amount` over the per-student dataset; the checked amount is the
    # output of `core/at_most`, which the line 33500 sum reads in place of the input.
    assert (
        registry.kind("ca/tuition_transferred_from_child_maximum")
        is TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM
    )
    assert (
        registry.kind("ca/tuition_transferred_from_child_checked")
        is TUITION_TRANSFERRED_FROM_CHILD_CHECKED
    )
    for kind in (TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM, TUITION_TRANSFERRED_FROM_CHILD_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert TUITION_TRANSFERRED_FROM_CHILD_CHECKED is not TUITION_TRANSFERRED_FROM_CHILD


def test_the_tuition_transfer_student_count_is_a_non_negative_int(
    registry: ArtifactRegistry,
) -> None:
    # 5000-G line 32400: "Only one person can claim this transfer from a student", so the count is
    # the number of students the transfer comes from, a whole number that is 0 or more.
    assert registry.kind("ca/tuition_transfer_students") is TUITION_TRANSFER_STUDENTS
    assert TUITION_TRANSFER_STUDENTS.value_type is int
    assert TUITION_TRANSFER_STUDENTS.non_negative is True
    assert TUITION_TRANSFER_STUDENTS.identifier in COUNTS


def test_the_canadian_tuition_count_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 11 line 1 and line 32000 "Eligible tuition fees paid to Canadian educational
    # institutions for 2025 (fees for each institution must be more than $100)": the form takes
    # one total, so the caller's number of institutions is the count (a whole number of 0 or
    # more) that `ca/more_than_per_unit` multiplies by $100, and the total it checks is the
    # checked amount that lines 2 to 8 read in place of the input (the owner's decision).
    assert registry.kind("ca/canadian_tuition_institutions") is CANADIAN_TUITION_INSTITUTIONS
    assert CANADIAN_TUITION_INSTITUTIONS.value_type is int
    assert CANADIAN_TUITION_INSTITUTIONS.non_negative is True
    assert CANADIAN_TUITION_INSTITUTIONS.identifier in COUNTS
    assert registry.kind("ca/canadian_tuition_fees_checked") is CANADIAN_TUITION_FEES_CHECKED
    assert CANADIAN_TUITION_FEES_CHECKED.value_type is Decimal
    assert CANADIAN_TUITION_FEES_CHECKED.non_negative is True
    assert CANADIAN_TUITION_FEES_CHECKED is not CANADIAN_TUITION_FEES


def test_the_non_refundable_credits_kinds_are_money() -> None:
    for kind in (
        NON_REFUNDABLE_CREDIT_AMOUNTS,
        CPP_BASE_CONTRIBUTIONS,
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT,
        EI_PREMIUMS,
        EI_PREMIUMS_ON_SELF_EMPLOYMENT,
        CANADA_EMPLOYMENT_AMOUNT,
        CANADA_EMPLOYMENT_AMOUNT_INCOME,
        NON_REFUNDABLE_TAX_CREDITS,
        ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
        ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
        ITC_RECAPTURE_AT_15_PERCENT,
        ITC_RECAPTURE_AT_20_PERCENT,
        ITC_RECAPTURE,
        CHARITABLE_DONATIONS,
        GOVERNMENT_DONATIONS,
        UNIVERSITY_DONATIONS_OUTSIDE_CANADA,
        FOREIGN_CHARITY_DONATIONS,
        ECOLOGICAL_AND_CULTURAL_GIFTS,
        ECOLOGICAL_GIFTS_BEFORE_2016,
        DEPRECIABLE_GIFT_RECAPTURED_DEPRECIATION,
        DEPRECIABLE_GIFT_NET_PROCEEDS,
        DEPRECIABLE_GIFT_CAPITAL_COST,
        CAPITAL_GIFT_TAXABLE_GAINS,
        CAPITAL_GIFT_GAINS_DEDUCTION,
        DEPRECIABLE_GIFT_PROCEEDS_OR_COST,
        DEPRECIABLE_GIFTS,
        CAPITAL_PROPERTY_GIFTS,
        TOTAL_CHARITABLE_DONATIONS,
        DONATION_LIMIT_ON_NET_INCOME,
        CAPITAL_GIFTS_TOTAL,
        CAPITAL_GIFTS_LIMIT_ADDITION,
        DONATION_LIMIT_WITH_CAPITAL_GIFTS,
        CHARITABLE_DONATIONS_LIMIT,
        CHARITABLE_DONATIONS_CLAIMED,
        DONATIONS_AND_GIFTS_TOTAL,
        DONATION_FIRST_TIER_MAXIMUM,
        DONATIONS_FIRST_TIER,
        DONATIONS_OVER_FIRST_TIER,
        DONATIONS_OVER_FIRST_TIER_AFTER_2016_GIFTS,
        DONATION_HIGH_INCOME_THRESHOLD,
        TAXABLE_INCOME_OVER_DONATION_THRESHOLD,
        HIGH_INCOME_DONATIONS,
        HIGH_INCOME_DONATION_CREDIT,
        REGULAR_RATE_DONATIONS,
        REGULAR_RATE_DONATION_CREDIT,
        FIRST_TIER_DONATION_CREDIT,
        DONATIONS_AND_GIFTS_CREDIT,
        CREDIT_AMOUNTS_AT_CREDIT_RATE,
        TOP_UP_CREDITS_BASE,
        TOP_UP_THRESHOLD,
        TOP_UP_EXCESS,
        TOP_UP_TAX_CREDIT,
        FEDERAL_TAX_ON_SPLIT_INCOME,
        FEDERAL_TAX_WITH_SPLIT_INCOME,
        CANADIAN_TUITION_FEES,
        CANADIAN_TUITION_FEES_CHECKED,
        CANADA_TRAINING_CREDIT_LIMIT,
        CANADA_TRAINING_CREDIT_CLAIMED,
        FOREIGN_TUITION_FEES,
        UNUSED_TUITION_FROM_2024,
        TUITION_TRANSFER_ELECTED,
        TUITION_TRANSFERRED_FROM_CHILD,
        TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
        TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM,
        CANADA_TRAINING_CREDIT_BASIS,
        CANADA_TRAINING_CREDIT_MAXIMUM,
        CANADIAN_TUITION_AVAILABLE,
        CURRENT_YEAR_TUITION_AVAILABLE,
        TOTAL_TUITION_AVAILABLE,
        TUITION_INCOME_BASE,
        TOSI_ADJUSTED_TAXABLE_INCOME,
        TUITION_INCOME_WITH_TOSI,
        CREDIT_AMOUNTS_SUBTOTAL,
        TUITION_INCOME_LESS_CREDITS,
        UNUSED_TUITION_CLAIMED,
        TUITION_INCOME_REMAINING,
        CURRENT_YEAR_TUITION_CLAIMED,
        FEDERAL_TUITION_AMOUNT,
        UNUSED_FEDERAL_TUITION,
        TUITION_TRANSFER_LIMIT,
        TUITION_AVAILABLE_TO_TRANSFER,
        TUITION_TRANSFERRED,
        TUITION_CARRIED_FORWARD,
        SPOUSE_RETURN_AGE_AMOUNT,
        SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT,
        SPOUSE_RETURN_PENSION_INCOME_AMOUNT,
        SPOUSE_RETURN_DISABILITY_AMOUNT,
        SPOUSE_DESIGNATED_TUITION,
        SPOUSE_RETURN_TAXABLE_INCOME,
        SPOUSE_RETURN_FEDERAL_BASIC_TAX,
        SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT,
        SPOUSE_RETURN_LINE_96,
        SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT,
        SPOUSE_TRANSFERABLE_AMOUNTS,
        SPOUSE_INCOME_FOR_TRANSFER,
        SPOUSE_CREDITS_USED,
        SPOUSE_ADJUSTED_TAXABLE_INCOME,
        SPOUSE_UNUSED_AMOUNTS,
        AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_split_income_and_t2203_lines_are_non_negative(registry: ArtifactRegistry) -> None:
    # T1 line 120 is 33% of a non-negative amount and line 121 "Line 119 plus line 120 =" adds two
    # non-negative taxes. Form T2203 Part 2 line 6 "Enter whichever is more" is never below line 4
    # (line 42900), line 8 is line 6 times a percentage, line 10 is line 8 times the rate of line
    # 9, and the count of line 5 is 0 or 1.
    for kind in (
        FEDERAL_TAX_ON_SPLIT_INCOME,
        FEDERAL_TAX_WITH_SPLIT_INCOME,
        T2203_HAS_TAX_ON_SPLIT_INCOME,
        T2203_LINE_6,
        T2203_LINE_8,
        T2203_FEDERAL_SURTAX_OUTSIDE_CANADA,
    ):
        assert kind.non_negative is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_tuition_and_transfer_kinds_are_non_negative(registry: ArtifactRegistry) -> None:
    # Schedule 11 and Schedule 2 take amounts the forms never show below zero: the lines that
    # subtract say "(if negative, enter "0")" or are bounded by the line they come off.
    for kind in (
        CANADIAN_TUITION_FEES,
        CANADIAN_TUITION_FEES_CHECKED,
        CANADA_TRAINING_CREDIT_LIMIT,
        CANADA_TRAINING_CREDIT_CLAIMED,
        FOREIGN_TUITION_FEES,
        UNUSED_TUITION_FROM_2024,
        TUITION_TRANSFER_ELECTED,
        TUITION_TRANSFERRED_FROM_CHILD,
        TUITION_TRANSFERRED_FROM_CHILD_CHECKED,
        TUITION_TRANSFERRED_FROM_CHILD_MAXIMUM,
        CANADA_TRAINING_CREDIT_BASIS,
        CANADA_TRAINING_CREDIT_MAXIMUM,
        CANADIAN_TUITION_AVAILABLE,
        CURRENT_YEAR_TUITION_AVAILABLE,
        TOTAL_TUITION_AVAILABLE,
        TUITION_INCOME_BASE,
        TOSI_ADJUSTED_TAXABLE_INCOME,
        TUITION_INCOME_WITH_TOSI,
        CREDIT_AMOUNTS_SUBTOTAL,
        TUITION_INCOME_LESS_CREDITS,
        UNUSED_TUITION_CLAIMED,
        TUITION_INCOME_REMAINING,
        CURRENT_YEAR_TUITION_CLAIMED,
        FEDERAL_TUITION_AMOUNT,
        UNUSED_FEDERAL_TUITION,
        TUITION_TRANSFER_LIMIT,
        TUITION_AVAILABLE_TO_TRANSFER,
        TUITION_TRANSFERRED,
        TUITION_CARRIED_FORWARD,
        SPOUSE_RETURN_AGE_AMOUNT,
        SPOUSE_RETURN_INFIRM_CHILDREN_AMOUNT,
        SPOUSE_RETURN_PENSION_INCOME_AMOUNT,
        SPOUSE_RETURN_DISABILITY_AMOUNT,
        SPOUSE_DESIGNATED_TUITION,
        SPOUSE_RETURN_TAXABLE_INCOME,
        SPOUSE_RETURN_FEDERAL_BASIC_TAX,
        SPOUSE_RETURN_BASIC_PERSONAL_AMOUNT,
        SPOUSE_RETURN_LINE_96,
        SPOUSE_RETURN_FEDERAL_TUITION_AMOUNT,
        SPOUSE_TRANSFERABLE_AMOUNTS,
        SPOUSE_INCOME_FOR_TRANSFER,
        SPOUSE_CREDITS_USED,
        SPOUSE_ADJUSTED_TAXABLE_INCOME,
        SPOUSE_UNUSED_AMOUNTS,
        AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    ):
        assert kind.non_negative is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_separation_count_is_a_non_negative_int(registry: ArtifactRegistry) -> None:
    # Schedule 2: "If you were separated because of a breakdown in your relationship for a period
    # of 90 days or more including December 31, 2025, your spouse or common-law partner cannot
    # transfer any unused amounts to you.": a caller's count, 1 when not separated and 0 when
    # separated (to be confirmed on the ticket).
    assert SPOUSE_NOT_SEPARATED_90_DAYS.value_type is int
    assert SPOUSE_NOT_SEPARATED_90_DAYS.non_negative is True
    assert registry.kind("ca/spouse_not_separated_90_days") is SPOUSE_NOT_SEPARATED_90_DAYS


# --- Form T2209 and T1 lines 128 to 130: the federal foreign tax credit ---------------------------


def test_the_federal_foreign_tax_credit_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/first_nations_abatement") is FIRST_NATIONS_ABATEMENT
    assert (
        registry.get("ca/foreign_tax_credit_net_income_deductions")
        is FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS
    )
    assert (
        registry.get("ca/foreign_tax_credit_net_income_before_split_income")
        is FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME
    )
    assert (
        registry.get("ca/foreign_tax_credit_net_income_with_split_income")
        is FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME
    )
    assert registry.get("ca/foreign_tax_credit_net_income") is FOREIGN_TAX_CREDIT_NET_INCOME
    assert (
        registry.get("ca/basic_federal_tax_with_dividend_credit")
        is BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT
    )
    assert (
        registry.get("ca/foreign_tax_credit_basic_federal_tax")
        is FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX
    )
    assert (
        registry.get("ca/federal_non_business_foreign_tax_credit")
        is FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT
    )
    assert registry.get("ca/federal_foreign_tax_credit") is FEDERAL_FOREIGN_TAX_CREDIT
    assert (
        registry.get("ca/federal_tax_less_foreign_tax_credit")
        is FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT
    )
    assert registry.get("ca/t2203_has_tax_on_split_income") is T2203_HAS_TAX_ON_SPLIT_INCOME
    assert registry.get("ca/t2203_line_5") is T2203_LINE_5
    assert registry.get("ca/t2203_line_6") is T2203_LINE_6
    assert registry.get("ca/t2203_line_8") is T2203_LINE_8
    assert (
        registry.get("ca/t2203_federal_surtax_outside_canada")
        is T2203_FEDERAL_SURTAX_OUTSIDE_CANADA
    )
    assert registry.get("ca/federal_surtax_outside_canada") is FEDERAL_SURTAX_OUTSIDE_CANADA
    assert registry.get("ca/federal_tax_with_surtax") is FEDERAL_TAX_WITH_SURTAX
    assert (
        registry.get("ca/basic_federal_tax_with_dividend_credit_and_surtax")
        is BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX
    )


def test_the_federal_foreign_tax_credit_kinds_are_money() -> None:
    for kind in (
        FIRST_NATIONS_ABATEMENT,
        FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
        FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME,
        FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
        FOREIGN_TAX_CREDIT_NET_INCOME,
        BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
        FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
        FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
        FEDERAL_FOREIGN_TAX_CREDIT,
        FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
        BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
        T2203_LINE_5,
        T2203_LINE_6,
        T2203_LINE_8,
        T2203_FEDERAL_SURTAX_OUTSIDE_CANADA,
        FEDERAL_SURTAX_OUTSIDE_CANADA,
        FEDERAL_TAX_WITH_SURTAX,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_signed_foreign_tax_credit_and_surtax_kinds_are_signed(
    registry: ArtifactRegistry,
) -> None:
    # Form T2209 note (3), net income: "Amount from line 23600 of your return (or the amount you
    # would have entered if the instructions said "if negative, show in brackets") plus the amount
    # on line 68360 of Form T1206, Total split income, minus any:" the listed deductions. The
    # note prints no "(if negative, enter "0")", and line 23600 in brackets is signed, so the
    # amount before the split income, the amount with it and the result may each be negative.
    # Form T2203 line 5 takes "Line 15 minus line 21" of Form T1206, which prints no floor; Form
    # T691 Part 3 line 4 prints no floor, so T1 line 127 may be negative, and T1 line 128 and
    # note (4)'s sum with it may be too. T1 line 130 "Line 128 minus line 129 =" and line 132 "Line
    # 130 plus line 131 =" print no "(if negative, enter "0")" either; line 134 is the first that
    # does.
    for kind in (
        FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME,
        FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
        FOREIGN_TAX_CREDIT_NET_INCOME,
        T2203_LINE_5,
        FEDERAL_SURTAX_OUTSIDE_CANADA,
        FEDERAL_TAX_WITH_SURTAX,
        BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
        FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
        FEDERAL_TAX_WITH_ITC_RECAPTURE,
    ):
        assert kind.non_negative is False, kind.identifier
        assert registry.kind(kind.identifier) is kind
        assert kind.identifier in SIGNED


def test_the_other_federal_foreign_tax_credit_kinds_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Note (4), basic federal tax: line 42900 plus the federal dividend tax credit, minus the
    # First Nations abatement, not below zero; line 3 is the lesser of two non-negative amounts,
    # line 13 "should not be more than" line 42900, and T1 line 130 comes off line 128 within the
    # limit.
    for kind in (
        FIRST_NATIONS_ABATEMENT,
        FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
        BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
        FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
        FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
        FEDERAL_FOREIGN_TAX_CREDIT,
    ):
        assert kind.non_negative is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


# --- Other federal non-refundable amounts: T1 lines 31220, 31240, 31270, 31285, 31300, 31400 and
# 31900 -------------------------------------------------------------------


def test_the_other_federal_non_refundable_amount_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    for identifier, kind in OTHER_FEDERAL_NON_REFUNDABLE_KINDS:
        assert registry.get(identifier) is kind, identifier


def test_the_other_federal_non_refundable_amount_kinds_are_money() -> None:
    # Dollars-and-cents boxes and credits: the caller's claims, the form's lines and the line
    # amounts, each a Decimal (the lines are rounded half-up to the cent through their datasets).
    for kind in (
        HOME_BUYERS_CLAIM,
        HOME_ACCESSIBILITY_EXPENSES,
        HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
        ADOPTION_CHILD_EXPENSES,
        PENSION_FOREIGN_INCOME,
        PENSION_FOREIGN_INCOME_CHECKED,
        PENSION_US_IRA_INCOME,
        PENSION_RRIF_TRANSFERRED,
        PENSION_ANNUITY_PAYMENTS,
        STUDENT_LOAN_INTEREST,
        VOLUNTEER_FIREFIGHTERS_CREDIT,
        SEARCH_AND_RESCUE_CREDIT,
        VOLUNTEER_CREDITS_CLAIMED,
        VOLUNTEER_AMOUNT_MAXIMUM,
        VOLUNTEER_CREDITS_CHECKED,
        HOME_BUYERS_MAXIMUM,
        HOME_BUYERS_CREDIT,
        HOME_ACCESSIBILITY_LINE_2,
        HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED,
        HOME_ACCESSIBILITY_CREDIT,
        ADOPTION_CREDIT,
        PENSION_CHART_LINE_5,
        PENSION_CHART_LINE_6,
        PENSION_CHART_LINE_7,
        PENSION_CHART_LINE_8,
        PENSION_INCOME_CREDIT,
        PENSION_WORKSHEET_AMOUNT,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_conditions_and_the_annuity_gate_are_non_negative_counts() -> None:
    # T1 line 31220 "You can claim $6,000 for the volunteer firefighters' amount (VFA) or search
    # and rescue volunteers' amount (SRVA), but not both": the conditions met are 0 or 1 (a
    # caller's count). Worksheet for line 31400, line 7: "only if you were 65 years of age or
    # older on December 31, 2025, or you received the payments because of the death of your
    # spouse or common-law partner" is a 0 or 1 gate on the annuity payments.
    for kind in (
        VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
        SEARCH_AND_RESCUE_CONDITIONS_MET,
        PENSION_ANNUITY_CONDITIONS_MET,
    ):
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_adoption_expense_children_are_a_record_list_of_one_money_field(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 31300 "Adoption expenses", Enter "the amount of eligible adoption expenses that you
    # can claim for all eligible children": one record per child, holding the filer's eligible
    # expenses for that child.
    assert isinstance(ADOPTION_EXPENSE_CHILDREN, RecordListKind)
    assert ADOPTION_EXPENSE_CHILDREN.fields == (ADOPTION_CHILD_EXPENSES,)
    assert registry.get("ca/adoption_expense_children") is ADOPTION_EXPENSE_CHILDREN
    assert registry.get("ca/adoption_child_expenses") is ADOPTION_CHILD_EXPENSES
    assert ADOPTION_CHILD_EXPENSES.value_type is Decimal
    assert ADOPTION_CHILD_EXPENSES.non_negative is True


OTHER_FEDERAL_NON_REFUNDABLE_KINDS: list[tuple[str, ArtifactKind[Any]]] = [
    ("ca/volunteer_firefighters_conditions_met", VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET),
    ("ca/search_and_rescue_conditions_met", SEARCH_AND_RESCUE_CONDITIONS_MET),
    ("ca/home_buyers_claim", HOME_BUYERS_CLAIM),
    ("ca/home_accessibility_expenses", HOME_ACCESSIBILITY_EXPENSES),
    ("ca/home_accessibility_claimed_by_others", HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS),
    ("ca/pension_foreign_income", PENSION_FOREIGN_INCOME),
    ("ca/pension_foreign_income_checked", PENSION_FOREIGN_INCOME_CHECKED),
    ("ca/pension_us_ira_income", PENSION_US_IRA_INCOME),
    ("ca/pension_rrif_transferred", PENSION_RRIF_TRANSFERRED),
    ("ca/pension_annuity_payments", PENSION_ANNUITY_PAYMENTS),
    ("ca/pension_annuity_conditions_met", PENSION_ANNUITY_CONDITIONS_MET),
    ("ca/student_loan_interest", STUDENT_LOAN_INTEREST),
    ("ca/volunteer_firefighters_credit", VOLUNTEER_FIREFIGHTERS_CREDIT),
    ("ca/search_and_rescue_credit", SEARCH_AND_RESCUE_CREDIT),
    ("ca/volunteer_credits_claimed", VOLUNTEER_CREDITS_CLAIMED),
    ("ca/volunteer_amount_maximum", VOLUNTEER_AMOUNT_MAXIMUM),
    ("ca/volunteer_credits_checked", VOLUNTEER_CREDITS_CHECKED),
    ("ca/home_buyers_maximum", HOME_BUYERS_MAXIMUM),
    ("ca/home_buyers_credit", HOME_BUYERS_CREDIT),
    ("ca/home_accessibility_line_2", HOME_ACCESSIBILITY_LINE_2),
    (
        "ca/home_accessibility_claimed_by_others_checked",
        HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED,
    ),
    ("ca/home_accessibility_credit", HOME_ACCESSIBILITY_CREDIT),
    ("ca/adoption_credit", ADOPTION_CREDIT),
    ("ca/pension_chart_line_1", PENSION_CHART_LINE_1),
    ("ca/pension_chart_line_5", PENSION_CHART_LINE_5),
    ("ca/pension_chart_line_6", PENSION_CHART_LINE_6),
    ("ca/pension_chart_line_7", PENSION_CHART_LINE_7),
    ("ca/pension_chart_line_8", PENSION_CHART_LINE_8),
    ("ca/pension_worksheet_amount", PENSION_WORKSHEET_AMOUNT),
    ("ca/pension_income_credit", PENSION_INCOME_CREDIT),
]


# Schedule 11 lines 32005 (a tick), 32010 and 32020 (months, the form's maximum is 12): caller's
# inputs and declared outputs that no step reads.
def test_the_schedule_11_tuition_memo_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/tuition_cannot_be_full_time_student")
        is TUITION_CANNOT_BE_FULL_TIME_STUDENT
    )
    assert registry.get("ca/tuition_part_time_months") is TUITION_PART_TIME_MONTHS
    assert registry.get("ca/tuition_full_time_months") is TUITION_FULL_TIME_MONTHS


def test_the_schedule_11_tuition_memo_kinds_are_non_negative_int_counts() -> None:
    for kind in (
        TUITION_CANNOT_BE_FULL_TIME_STUDENT,
        TUITION_PART_TIME_MONTHS,
        TUITION_FULL_TIME_MONTHS,
    ):
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


YES_OR_NO_CHECKED = (
    (SPOUSE_NOT_SEPARATED_90_DAYS, SPOUSE_NOT_SEPARATED_90_DAYS_CHECKED),
    (VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET, VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED),
    (SEARCH_AND_RESCUE_CONDITIONS_MET, SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED),
    (PENSION_ANNUITY_CONDITIONS_MET, PENSION_ANNUITY_CONDITIONS_MET_CHECKED),
)


@pytest.mark.parametrize(("raw", "checked"), YES_OR_NO_CHECKED, ids=lambda kind: kind.identifier)
def test_each_yes_or_no_checked_kind_is_a_non_negative_count_named_after_its_input(
    raw: ArtifactKind[int], checked: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the steps that read it; a count of 2 or
    # more is refused, not capped.
    assert checked.identifier == f"{raw.identifier}_checked"
    assert registry.get(checked.identifier) is checked
    assert checked.value_type is int
    assert checked.non_negative is True
