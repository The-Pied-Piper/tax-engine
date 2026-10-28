"""Registered and money kinds of the federal catalog family `taxable_income`."""

from __future__ import annotations

import ast
import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_calculator.jurisdictions.ca.catalog
from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    ABIL_AFTER_QBT_REDUCTION,
    ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
    ADDITIONAL_DEDUCTIONS,
    ADDITIONAL_DEDUCTIONS_TOTAL,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
    ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
    ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
    ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_LOSSES_LEFT_AFTER_2000,
    ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    ANNUAL_GAINS_LIMIT_2025,
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE,
    ANNUAL_GAINS_LINE_5,
    ANNUAL_GAINS_LINE_7,
    ANNUAL_GAINS_LINE_9,
    ANNUAL_GAINS_LINE_10,
    ANNUAL_GAINS_LINE_12,
    ANNUAL_GAINS_SCHEDULE_3_TOTAL,
    CAPITAL_GAINS_DEDUCTION,
    CAPITAL_GAINS_DEDUCTION_CLAIMED,
    CHART_1_COLUMN_G_TOTAL,
    CHART_2_LINE_3,
    CHART_2_LINE_4,
    CHART_2_LINE_5,
    CHART_2_LINE_7,
    CHART_2_LINE_8,
    CHART_2_LINE_9,
    CHART_2_LINE_11,
    CHART_2_LINE_12,
    CHART_2_LINE_13,
    CHART_2_LINE_14_OVER_TWICE_IR,
    CHART_2_LINE_15,
    CHART_2_LINE_16,
    CHART_2_LINE_17,
    CHART_2_LINE_19,
    CHART_2_NUMERATOR_ONE,
    CHART_2_TWICE_IR,
    CHART_2025_PART_1_AMOUNT_A,
    CHART_2025_PART_1_AMOUNT_C,
    CHART_2025_PART_1_AMOUNT_E,
    CHART_2025_PART_1_AMOUNT_K,
    CHART_2025_PART_1_AMOUNT_M,
    CHART_2025_PART_1_AMOUNT_N,
    CHART_2025_PART_1_AMOUNT_P,
    CHART_2025_PART_1_AMOUNT_Q,
    CHART_2025_PART_1_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_AMOUNT_A,
    CHART_2025_PART_2_AMOUNT_C,
    CHART_2025_PART_2_AMOUNT_E,
    CHART_2025_PART_2_AMOUNT_F,
    CHART_2025_PART_2_AMOUNT_G,
    CHART_2025_PART_2_AMOUNT_H,
    CHART_2025_PART_2_AMOUNT_K,
    CHART_2025_PART_2_AMOUNT_M,
    CHART_2025_PART_2_AMOUNT_N,
    CHART_2025_PART_2_AMOUNT_P,
    CHART_2025_PART_2_AMOUNT_Q,
    CHART_2025_PART_2_AMOUNTS_F_TO_J,
    CHART_2025_PART_2_MAXIMUM_CLAIM,
    CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    CUMULATIVE_GAINS_LIMIT_2025,
    CUMULATIVE_LOSSES_AND_DEDUCTIONS,
    DEDUCTIONS_FROM_NET_INCOME,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
    ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
    EXEMPT_INCOME_DEDUCTIONS,
    EXEMPT_INCOME_DEDUCTIONS_CHECKED,
    HAS_INVESTMENT_EXPENSES,
    HAS_INVESTMENT_EXPENSES_CHECKED,
    LIMITED_PARTNERSHIP_AT_RISK_AMOUNT,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
    NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
    NET_CAPITAL_LOSS_TWICE_IR_2000,
    NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
    NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
    NET_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSSES_CLAIMED,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_FARMING_INCOME_NOT_BELOW_ZERO,
    NON_ACTIVE_PARTNERSHIP_LOSSES,
    NON_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NON_CAPITAL_LOSSES_ON_LINE_25200,
    OTHER_INVESTMENT_EXPENSES,
    OTHER_PROPERTY_INCOME,
    PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
    PRE_1986_CAPITAL_LOSS_BALANCE,
    PRE_1986_DEDUCTIONS_1988_AND_1989,
    PRE_1986_DEDUCTIONS_1990_TO_1999,
    PRE_1986_DEDUCTIONS_2000,
    PRE_1986_DEDUCTIONS_2001_TO_2024,
    PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
    PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
    PRE_1986_DEDUCTIONS_ADJUSTED_2000,
    PRE_1986_DEDUCTIONS_BEFORE_1988,
    PRE_1986_DEDUCTIONS_TOTAL,
    QBT_2024_RESERVE,
    QBT_2025_RESERVE,
    QBT_2025_RESERVE_CHECKED,
    QBT_ABIL_AND_NET_INVESTMENT_LOSS,
    QBT_ABIL_REDUCTION,
    QBT_ALLOCATION_LIMIT,
    QBT_ALLOCATION_TOTAL,
    QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER,
    QBT_AMOUNT_ALLOCATED,
    QBT_CAPITAL_GAINS,
    QBT_CAPITAL_GAINS_DEDUCTION,
    QBT_CAPITAL_GAINS_WITH_2024_RESERVE,
    QBT_CHART_A_NET_CAPITAL_LOSSES_USED,
    QBT_CHART_A_NET_INVESTMENT_LOSS,
    QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER,
    QBT_DEDUCTION_AVAILABLE,
    QBT_DEDUCTION_BASE,
    QBT_DEDUCTION_CLAIMED,
    QBT_DEDUCTION_LIMIT,
    QBT_DIVIDENDS_AND_INVESTMENT_INCOME,
    QBT_EARLIER_ABIL_REDUCTION_TOTAL,
    QBT_EARLIER_ALLOCATION_TOTAL,
    QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL,
    QBT_ELECTION_DEDUCTION,
    QBT_ELECTION_ELIGIBLE_AMOUNT,
    QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED,
    QBT_ELECTION_ELIGIBLE_AMOUNT_MAXIMUM,
    QBT_ELECTION_IS_QBT,
    QBT_ELECTION_IS_QBT_IN_ORDER,
    QBT_EXPLORATION_EXPENSES_AT_HALF,
    QBT_EXPLORATION_RECOVERY_INCOME,
    QBT_EXPLORATION_RECOVERY_INCOME_CHECKED,
    QBT_GAINS_ARE_QSBCS_OR_QFFP,
    QBT_HAS_INVESTMENT_EXPENSES,
    QBT_INVESTMENT_EXPENSES,
    QBT_INVESTMENT_INCOME,
    QBT_MAXIMUM_DEDUCTION,
    QBT_NET_CAPITAL_LOSSES_REMAINING,
    QBT_NET_INVESTMENT_LOSS,
    QBT_NET_INVESTMENT_LOSS_REDUCTION,
    QBT_NET_RENTAL_INCOME,
    QBT_NET_RENTAL_LOSS,
    QBT_OTHER_INVESTMENT_EXPENSES,
    QBT_OTHER_PROPERTY_INCOME,
    QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    QBT_PARTNERSHIP_LOSSES,
    QBT_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
    QBT_PERCENTAGE_ALLOCATED,
    QBT_PERCENTAGE_ALLOCATED_CHECKED,
    QBT_PERCENTAGE_ALLOCATED_MAXIMUM,
    QBT_PRIOR_YEARS_CLAIMS,
    QBT_PRIOR_YEARS_CLAIMS_CHECKED,
    QBT_RECOVERY_OF_EXPLORATION_EXPENSES,
    QBT_REDUCTION_AMOUNT,
    QBT_REDUCTIONS_FROM_LOSSES,
    QBT_TAXABLE_AMOUNT_ALLOCATED,
    QBT_TAXABLE_CAPITAL_GAINS,
    QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER,
    QBT_TAXABLE_GAINS_LIMIT,
    QBT_TAXABLE_GAINS_NOT_LIMITED,
    QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    QBT_TOTAL_CAPITAL_GAINS,
    QCC_ELECTION_DEDUCTION,
    QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    RESTRICTED_FARM_LOSS_APPLIED_CHECKED,
    RESTRICTED_FARM_LOSS_APPLIED_TOTAL,
    RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS,
    RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED,
    SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO,
    SCHEDULE_3_LINE_19900,
    T657_ABIL_CLAIMED_1985_TO_2024,
    T657_CAPITAL_LOSSES_CLAIMED_1985,
    T657_CHART_1_COLUMN_A,
    T657_CHART_1_COLUMN_B,
    T657_CHART_1_COLUMN_C,
    T657_CHART_1_COLUMN_D,
    T657_CHART_1_ROWS,
    T657_CHART_2_LINE_1,
    T657_CHART_2_LINE_2,
    T657_CHART_2_LINE_6,
    T657_CHART_2_LINE_10,
    T657_CHART_2_LINE_14,
    T657_CHART_2_LINE_18,
    T657_CUMULATIVE_NET_INVESTMENT_LOSS,
    T657_DEDUCTIONS_CLAIMED_1985_TO_2024,
    T657_GAINS_1985_TO_1991,
    T657_GAINS_1992_AND_1993,
    T657_GAINS_1994,
    T657_GAINS_1995,
    T657_GAINS_1996_TO_1999,
    T657_GAINS_2000,
    T657_GAINS_2001,
    T657_GAINS_2002_TO_2024,
    T657_INCLUSION_RATE_2000,
    T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    T657_PART_1_AMOUNT_F,
    T657_PART_1_AMOUNT_G,
    T657_PART_1_AMOUNT_H,
    T657_PART_1_AMOUNT_I,
    T657_PART_1_AMOUNT_J,
    T657_PART_1_AMOUNT_L,
    T657_PART_2_AMOUNT_I,
    T657_PART_2_AMOUNT_J,
    T657_PART_2_AMOUNT_L,
    T657_PART_2_EXCLUDED_F,
    T657_PART_2_EXCLUDED_G,
    T657_PART_2_EXCLUDED_H,
    T657_T2048_LINE_17217_FOR_2024,
    T2048_DISPOSITIONS,
    TAXABLE_INCOME,
    TAXABLE_INCOME_SIGNED,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
    UNAPPLIED_NET_CAPITAL_LOSSES_1985_TO_1987,
    UNAPPLIED_NET_CAPITAL_LOSSES_1988_AND_1989,
    UNAPPLIED_NET_CAPITAL_LOSSES_1990_TO_1999,
    UNAPPLIED_NET_CAPITAL_LOSSES_2000,
    UNAPPLIED_NET_CAPITAL_LOSSES_2001_TO_2024,
    UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST,
    US_SOCIAL_SECURITY_BENEFITS,
    US_SOCIAL_SECURITY_BENEFITS_CHECKED,
    US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE,
    US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE,
    US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996,
    US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED,
    US_SOCIAL_SECURITY_TREATY_DEDUCTION,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, SIGNED


def test_the_taxable_income_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/taxable_income") is TAXABLE_INCOME
    assert (
        registry.get("ca/limited_partnership_losses_of_other_years")
        is LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS
    )
    assert (
        registry.get("ca/limited_partnership_at_risk_amount") is LIMITED_PARTNERSHIP_AT_RISK_AMOUNT
    )
    assert (
        registry.get("ca/limited_partnership_losses_of_other_years_checked")
        is LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED
    )
    assert registry.get("ca/non_capital_losses_of_other_years") is NON_CAPITAL_LOSSES_OF_OTHER_YEARS
    assert registry.get("ca/non_capital_losses_on_line_25200") is NON_CAPITAL_LOSSES_ON_LINE_25200
    assert (
        registry.get("ca/restricted_farm_losses_of_other_years")
        is RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS
    )
    assert (
        registry.get("ca/restricted_farm_losses_of_other_years_checked")
        is RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED
    )
    assert (
        registry.get("ca/unapplied_restricted_farm_loss_taxes_and_interest")
        is UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST
    )
    assert (
        registry.get("ca/restricted_farm_loss_applied_total") is RESTRICTED_FARM_LOSS_APPLIED_TOTAL
    )
    assert (
        registry.get("ca/restricted_farm_loss_applied_checked")
        is RESTRICTED_FARM_LOSS_APPLIED_CHECKED
    )
    assert registry.get("ca/net_farming_income_not_below_zero") is NET_FARMING_INCOME_NOT_BELOW_ZERO
    assert (
        registry.get("ca/unapplied_net_capital_losses_1985_to_1987")
        is UNAPPLIED_NET_CAPITAL_LOSSES_1985_TO_1987
    )
    assert (
        registry.get("ca/unapplied_net_capital_losses_1988_and_1989")
        is UNAPPLIED_NET_CAPITAL_LOSSES_1988_AND_1989
    )
    assert (
        registry.get("ca/unapplied_net_capital_losses_1990_to_1999")
        is UNAPPLIED_NET_CAPITAL_LOSSES_1990_TO_1999
    )
    assert (
        registry.get("ca/unapplied_net_capital_losses_2001_to_2024")
        is UNAPPLIED_NET_CAPITAL_LOSSES_2001_TO_2024
    )
    assert registry.get("ca/net_capital_losses_claimed") is NET_CAPITAL_LOSSES_CLAIMED
    assert (
        registry.get("ca/adjusted_gross_capital_losses_1985_to_1987")
        is ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987
    )
    assert (
        registry.get("ca/adjusted_gross_capital_losses_1988_and_1989")
        is ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989
    )
    assert (
        registry.get("ca/adjusted_gross_capital_losses_1990_to_1999")
        is ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999
    )
    assert (
        registry.get("ca/adjusted_gross_capital_losses_2001_to_2024")
        is ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024
    )
    assert registry.get("ca/total_adjusted_net_capital_losses") is TOTAL_ADJUSTED_NET_CAPITAL_LOSSES
    assert (
        registry.get("ca/net_capital_losses_available_to_claim")
        is NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM
    )
    assert registry.get("ca/net_capital_losses_of_other_years") is NET_CAPITAL_LOSSES_OF_OTHER_YEARS
    assert (
        registry.get("ca/adjusted_losses_applied_1985_to_1987")
        is ADJUSTED_LOSSES_APPLIED_1985_TO_1987
    )
    assert (
        registry.get("ca/adjusted_losses_left_after_1985_to_1987")
        is ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987
    )
    assert (
        registry.get("ca/remaining_adjusted_losses_1985_to_1987")
        is REMAINING_ADJUSTED_LOSSES_1985_TO_1987
    )
    assert (
        registry.get("ca/net_capital_loss_balance_1985_to_1987")
        is NET_CAPITAL_LOSS_BALANCE_1985_TO_1987
    )
    assert (
        registry.get("ca/adjusted_losses_applied_1988_and_1989")
        is ADJUSTED_LOSSES_APPLIED_1988_AND_1989
    )
    assert (
        registry.get("ca/adjusted_losses_left_after_1988_and_1989")
        is ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989
    )
    assert (
        registry.get("ca/remaining_adjusted_losses_1988_and_1989")
        is REMAINING_ADJUSTED_LOSSES_1988_AND_1989
    )
    assert (
        registry.get("ca/net_capital_loss_balance_1988_and_1989")
        is NET_CAPITAL_LOSS_BALANCE_1988_AND_1989
    )
    assert (
        registry.get("ca/adjusted_losses_applied_1990_to_1999")
        is ADJUSTED_LOSSES_APPLIED_1990_TO_1999
    )
    assert (
        registry.get("ca/adjusted_losses_left_after_1990_to_1999")
        is ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999
    )
    assert (
        registry.get("ca/remaining_adjusted_losses_1990_to_1999")
        is REMAINING_ADJUSTED_LOSSES_1990_TO_1999
    )
    assert (
        registry.get("ca/net_capital_loss_balance_1990_to_1999")
        is NET_CAPITAL_LOSS_BALANCE_1990_TO_1999
    )
    assert (
        registry.get("ca/adjusted_losses_applied_2001_to_2024")
        is ADJUSTED_LOSSES_APPLIED_2001_TO_2024
    )
    assert (
        registry.get("ca/remaining_adjusted_losses_2001_to_2024")
        is REMAINING_ADJUSTED_LOSSES_2001_TO_2024
    )
    assert (
        registry.get("ca/net_capital_loss_balance_2001_to_2024")
        is NET_CAPITAL_LOSS_BALANCE_2001_TO_2024
    )
    assert registry.get("ca/unapplied_net_capital_losses_2000") is UNAPPLIED_NET_CAPITAL_LOSSES_2000
    assert registry.get("ca/net_capital_loss_twice_ir_2000") is NET_CAPITAL_LOSS_TWICE_IR_2000
    assert (
        registry.get("ca/net_capital_loss_numerator_one_2000")
        is NET_CAPITAL_LOSS_NUMERATOR_ONE_2000
    )
    assert (
        registry.get("ca/adjusted_gross_capital_losses_2000") is ADJUSTED_GROSS_CAPITAL_LOSSES_2000
    )
    assert registry.get("ca/adjusted_losses_applied_2000") is ADJUSTED_LOSSES_APPLIED_2000
    assert registry.get("ca/adjusted_losses_left_after_2000") is ADJUSTED_LOSSES_LEFT_AFTER_2000
    assert registry.get("ca/remaining_adjusted_losses_2000") is REMAINING_ADJUSTED_LOSSES_2000
    assert registry.get("ca/net_capital_loss_balance_2000") is NET_CAPITAL_LOSS_BALANCE_2000
    assert (
        registry.get("ca/net_capital_losses_before_may_23_1985")
        is NET_CAPITAL_LOSSES_BEFORE_MAY_23_1985
    )
    assert registry.get("ca/pre_1986_deductions_before_1988") is PRE_1986_DEDUCTIONS_BEFORE_1988
    assert registry.get("ca/pre_1986_deductions_1988_and_1989") is PRE_1986_DEDUCTIONS_1988_AND_1989
    assert registry.get("ca/pre_1986_deductions_1990_to_1999") is PRE_1986_DEDUCTIONS_1990_TO_1999
    assert registry.get("ca/pre_1986_deductions_2000") is PRE_1986_DEDUCTIONS_2000
    assert registry.get("ca/pre_1986_deductions_2001_to_2024") is PRE_1986_DEDUCTIONS_2001_TO_2024
    assert (
        registry.get("ca/pre_1986_deductions_adjusted_1988_and_1989")
        is PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989
    )
    assert (
        registry.get("ca/pre_1986_deductions_adjusted_1990_to_1999")
        is PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999
    )
    assert registry.get("ca/pre_1986_deductions_adjusted_2000") is PRE_1986_DEDUCTIONS_ADJUSTED_2000
    assert registry.get("ca/pre_1986_deductions_total") is PRE_1986_DEDUCTIONS_TOTAL
    assert registry.get("ca/pre_1986_capital_loss_balance") is PRE_1986_CAPITAL_LOSS_BALANCE
    assert (
        registry.get("ca/adjusted_gross_capital_losses_before_may_23_1985")
        is ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985
    )
    assert (
        registry.get("ca/adjusted_losses_applied_before_may_23_1985")
        is ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985
    )
    assert (
        registry.get("ca/adjusted_losses_left_after_before_may_23_1985")
        is ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985
    )
    assert (
        registry.get("ca/remaining_adjusted_losses_before_may_23_1985")
        is REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985
    )
    assert (
        registry.get("ca/net_capital_loss_balance_before_may_23_1985")
        is NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985
    )
    assert (
        registry.get("ca/adjusted_net_capital_losses_applied")
        is ADJUSTED_NET_CAPITAL_LOSSES_APPLIED
    )
    assert (
        registry.get("ca/unapplied_adjusted_net_capital_losses")
        is UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES
    )
    assert (
        registry.get("ca/net_capital_losses_additional_deduction")
        is NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION
    )
    assert (
        registry.get("ca/total_adjusted_net_capital_losses_applied")
        is TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED
    )
    assert registry.get("ca/additional_deductions") is ADDITIONAL_DEDUCTIONS
    assert registry.get("ca/additional_deductions_total") is ADDITIONAL_DEDUCTIONS_TOTAL
    assert registry.get("ca/deductions_from_net_income") is DEDUCTIONS_FROM_NET_INCOME


def test_the_taxable_income_kinds_are_money() -> None:
    for kind in (
        LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS,
        LIMITED_PARTNERSHIP_AT_RISK_AMOUNT,
        LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
        NON_CAPITAL_LOSSES_OF_OTHER_YEARS,
        NON_CAPITAL_LOSSES_ON_LINE_25200,
        RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS,
        RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED,
        UNAPPLIED_RESTRICTED_FARM_LOSS_TAXES_AND_INTEREST,
        RESTRICTED_FARM_LOSS_APPLIED_TOTAL,
        RESTRICTED_FARM_LOSS_APPLIED_CHECKED,
        NET_FARMING_INCOME_NOT_BELOW_ZERO,
        UNAPPLIED_NET_CAPITAL_LOSSES_1985_TO_1987,
        UNAPPLIED_NET_CAPITAL_LOSSES_1988_AND_1989,
        UNAPPLIED_NET_CAPITAL_LOSSES_1990_TO_1999,
        UNAPPLIED_NET_CAPITAL_LOSSES_2001_TO_2024,
        NET_CAPITAL_LOSSES_CLAIMED,
        ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
        ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
        ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
        ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
        TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
        NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
        NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
        ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
        ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
        REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
        NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
        ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
        ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
        REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
        NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
        ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
        ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
        REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
        NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
        ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
        REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
        NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
        UNAPPLIED_NET_CAPITAL_LOSSES_2000,
        NET_CAPITAL_LOSS_TWICE_IR_2000,
        NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
        ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
        ADJUSTED_LOSSES_APPLIED_2000,
        ADJUSTED_LOSSES_LEFT_AFTER_2000,
        REMAINING_ADJUSTED_LOSSES_2000,
        NET_CAPITAL_LOSS_BALANCE_2000,
        NET_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
        PRE_1986_DEDUCTIONS_BEFORE_1988,
        PRE_1986_DEDUCTIONS_1988_AND_1989,
        PRE_1986_DEDUCTIONS_1990_TO_1999,
        PRE_1986_DEDUCTIONS_2000,
        PRE_1986_DEDUCTIONS_2001_TO_2024,
        PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
        PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
        PRE_1986_DEDUCTIONS_ADJUSTED_2000,
        PRE_1986_DEDUCTIONS_TOTAL,
        PRE_1986_CAPITAL_LOSS_BALANCE,
        ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
        ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
        ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
        REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
        NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
        ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
        UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
        NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
        TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
        ADDITIONAL_DEDUCTIONS,
        ADDITIONAL_DEDUCTIONS_TOTAL,
        DEDUCTIONS_FROM_NET_INCOME,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_us_social_security_treaty_deduction_kinds_are_registered(
    registry: ArtifactRegistry,
) -> None:
    # Guide 5000-G "Line 25600 - Additional deductions": the benefits and the deductions at the two
    # printed rates are non-negative money; the 0 or 1 answer and its checked twin are counts.
    for kind in (
        US_SOCIAL_SECURITY_BENEFITS,
        US_SOCIAL_SECURITY_BENEFITS_CHECKED,
        US_SOCIAL_SECURITY_DEDUCTION_AT_STANDARD_RATE,
        US_SOCIAL_SECURITY_DEDUCTION_AT_RESIDENT_RATE,
        US_SOCIAL_SECURITY_TREATY_DEDUCTION,
        ADDITIONAL_DEDUCTIONS_TOTAL,
    ):
        assert registry.get(kind.identifier) is kind
        assert kind.value_type is Decimal
        assert kind.non_negative is True
        assert kind.identifier not in SIGNED
    for count in (
        US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996,
        US_SOCIAL_SECURITY_RESIDENT_SINCE_BEFORE_1996_CHECKED,
    ):
        assert registry.get(count.identifier) is count
        assert count.value_type is int
        assert count.identifier in COUNTS


def test_the_taxable_income_signed_is_the_signed_twin_of_the_taxable_income(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 1 "Taxable income from line 26000 of your return (or the amount you
    # would have entered on line 26000 if the instructions for lines 23600 and 26000 said "if
    # negative, show in brackets") (1)" reads the amount before the floor, a kind of its own that
    # is signed; T1 line 26000 "Line 57 minus line 68 (if negative, enter "0")" stays the
    # non-negative `ca/taxable_income`.
    assert TAXABLE_INCOME_SIGNED is not TAXABLE_INCOME
    assert TAXABLE_INCOME_SIGNED.identifier == "ca/taxable_income_signed"
    assert TAXABLE_INCOME_SIGNED.value_type is Decimal
    assert TAXABLE_INCOME_SIGNED.non_negative is False
    assert registry.get("ca/taxable_income_signed") is TAXABLE_INCOME_SIGNED
    assert registry.kind("ca/taxable_income_signed") is TAXABLE_INCOME_SIGNED
    assert "ca/taxable_income_signed" in SIGNED
    assert TAXABLE_INCOME.non_negative is True
    assert "ca/taxable_income" not in SIGNED


def test_the_pre_1986_capital_loss_balance_is_signed_money(registry: ArtifactRegistry) -> None:
    # Form T1436 (Capital Gains Worksheet, 2025), "Line 25300 - Net capital loss of other years (if
    # you have pre-1986 capital loss balance)" line 3 "Pre-1986 capital loss balance available for
    # 2025: line 1 minus line 2" (confirmed from the PDF; no .txt published) prints no floor, so
    # the kind is not declared non-negative, as the Federal Worksheet's lines 5 and 9.
    assert PRE_1986_CAPITAL_LOSS_BALANCE.value_type is Decimal
    assert PRE_1986_CAPITAL_LOSS_BALANCE.non_negative is False
    assert registry.kind("ca/pre_1986_capital_loss_balance").non_negative is False
    assert "ca/pre_1986_capital_loss_balance" in SIGNED


def test_the_pre_1986_chart_kinds_do_not_clash_with_the_business_investment_loss_kinds(
    registry: ArtifactRegistry,
) -> None:
    # Line 21700's capital gains deductions are `ca/capital_gains_deductions_*`: the T1436
    # chart's own lines carry another name.
    abil = {i for i in registry.identifiers() if i.startswith("ca/capital_gains_deductions_")}
    chart = {i for i in registry.identifiers() if i.startswith("ca/pre_1986_deductions")}

    assert abil
    assert chart
    assert not abil & chart


def test_the_deductions_the_foreign_tax_credit_subtracts_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    # Form T2209 note (3), net income, "minus any:" "capital gains deduction for qualifying
    # business transfer or qualifying cooperative conversion you claimed (line 25395 of your
    # return)", "capital gains deduction you claimed (line 25400 of your return)" and "amounts
    # deductible as net employment income from a prescribed international organization, as
    # foreign income exempt under a tax treaty, or as adult basic education tuition assistance
    # (included on line 25600 of your return)". T1 lines 64 and 65 are not wired into line 68.
    assert registry.get("ca/capital_gains_deduction") is CAPITAL_GAINS_DEDUCTION
    assert registry.get("ca/exempt_income_deductions") is EXEMPT_INCOME_DEDUCTIONS


def test_the_deductions_the_foreign_tax_credit_subtracts_are_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in (
        CAPITAL_GAINS_DEDUCTION,
        EXEMPT_INCOME_DEDUCTIONS,
        EXEMPT_INCOME_DEDUCTIONS_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_checked_exempt_income_deductions_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    # Form T2209 note (3) subtracts the part of line 25600 that is exempt income, and that part is
    # at most the whole, `ca/additional_deductions` (line 25600 "Additional deductions"). The
    # checked amount `core/at_most` produces is what the foreign tax credit's sum reads, in place
    # of the input `ca/exempt_income_deductions`.
    assert registry.get("ca/exempt_income_deductions_checked") is EXEMPT_INCOME_DEDUCTIONS_CHECKED
    assert EXEMPT_INCOME_DEDUCTIONS_CHECKED.value_type is Decimal
    assert EXEMPT_INCOME_DEDUCTIONS_CHECKED.non_negative is True
    assert registry.kind("ca/exempt_income_deductions_checked") is EXEMPT_INCOME_DEDUCTIONS_CHECKED
    assert "ca/exempt_income_deductions_checked" not in SIGNED


def test_the_form_t2048_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    # Form T2048 (Capital Gains Deduction for Qualifying Business Transfers or Qualifying
    # Cooperative Conversions) Parts 2 to 5 and Chart A, and line 25395 (T1 line 64).
    for identifier, kind in (
        ("ca/qbt_election_eligible_amount", QBT_ELECTION_ELIGIBLE_AMOUNT),
        ("ca/qbt_election_eligible_amount_maximum", QBT_ELECTION_ELIGIBLE_AMOUNT_MAXIMUM),
        ("ca/qbt_election_eligible_amount_checked", QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED),
        ("ca/qbt_percentage_allocated", QBT_PERCENTAGE_ALLOCATED),
        ("ca/qbt_percentage_allocated_maximum", QBT_PERCENTAGE_ALLOCATED_MAXIMUM),
        ("ca/qbt_percentage_allocated_checked", QBT_PERCENTAGE_ALLOCATED_CHECKED),
        ("ca/qbt_amount_allocated", QBT_AMOUNT_ALLOCATED),
        ("ca/qbt_taxable_amount_allocated", QBT_TAXABLE_AMOUNT_ALLOCATED),
        ("ca/qbt_prior_years_claims", QBT_PRIOR_YEARS_CLAIMS),
        ("ca/qbt_prior_years_claims_checked", QBT_PRIOR_YEARS_CLAIMS_CHECKED),
        ("ca/qbt_deduction_available", QBT_DEDUCTION_AVAILABLE),
        ("ca/qbt_capital_gains", QBT_CAPITAL_GAINS),
        ("ca/qbt_2024_reserve", QBT_2024_RESERVE),
        ("ca/qbt_capital_gains_with_2024_reserve", QBT_CAPITAL_GAINS_WITH_2024_RESERVE),
        ("ca/qbt_2025_reserve", QBT_2025_RESERVE),
        ("ca/qbt_2025_reserve_checked", QBT_2025_RESERVE_CHECKED),
        ("ca/qbt_total_capital_gains", QBT_TOTAL_CAPITAL_GAINS),
        ("ca/qbt_taxable_capital_gains", QBT_TAXABLE_CAPITAL_GAINS),
        ("ca/qbt_taxable_gains_limit", QBT_TAXABLE_GAINS_LIMIT),
        ("ca/qbt_taxable_gains_not_limited", QBT_TAXABLE_GAINS_NOT_LIMITED),
        ("ca/qbt_net_capital_losses_remaining", QBT_NET_CAPITAL_LOSSES_REMAINING),
        ("ca/qbt_has_investment_expenses", QBT_HAS_INVESTMENT_EXPENSES),
        ("ca/qbt_net_investment_loss", QBT_NET_INVESTMENT_LOSS),
        ("ca/qbt_reductions_from_losses", QBT_REDUCTIONS_FROM_LOSSES),
        ("ca/qbt_deduction_limit", QBT_DEDUCTION_LIMIT),
        ("ca/qbt_maximum_deduction", QBT_MAXIMUM_DEDUCTION),
        ("ca/qbt_deduction_claimed", QBT_DEDUCTION_CLAIMED),
        ("ca/qbt_capital_gains_deduction", QBT_CAPITAL_GAINS_DEDUCTION),
        ("ca/qbt_deduction_base", QBT_DEDUCTION_BASE),
        ("ca/qbt_reduction_amount", QBT_REDUCTION_AMOUNT),
        ("ca/qbt_allocation_total", QBT_ALLOCATION_TOTAL),
        ("ca/qbt_abil_and_net_investment_loss", QBT_ABIL_AND_NET_INVESTMENT_LOSS),
        ("ca/qbt_allocation_limit", QBT_ALLOCATION_LIMIT),
        ("ca/qbt_abil_reduction", QBT_ABIL_REDUCTION),
        ("ca/qbt_net_investment_loss_reduction", QBT_NET_INVESTMENT_LOSS_REDUCTION),
        ("ca/qbt_election_is_qbt", QBT_ELECTION_IS_QBT),
        ("ca/qbt_gains_are_qsbcs_or_qffp", QBT_GAINS_ARE_QSBCS_OR_QFFP),
        ("ca/qcc_election_deduction", QCC_ELECTION_DEDUCTION),
        ("ca/qbt_election_deduction", QBT_ELECTION_DEDUCTION),
        ("ca/qbt_taxable_gains_related_to_deduction", QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION),
        (
            "ca/qsbcs_qffp_taxable_gains_related_to_deduction",
            QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
        ),
        ("ca/qbt_net_rental_income", QBT_NET_RENTAL_INCOME),
        ("ca/qbt_net_rental_loss", QBT_NET_RENTAL_LOSS),
        ("ca/qbt_partnership_losses", QBT_PARTNERSHIP_LOSSES),
        ("ca/qbt_exploration_expenses_at_half", QBT_EXPLORATION_EXPENSES_AT_HALF),
        ("ca/qbt_other_investment_expenses", QBT_OTHER_INVESTMENT_EXPENSES),
        ("ca/qbt_chart_a_net_capital_losses_used", QBT_CHART_A_NET_CAPITAL_LOSSES_USED),
        ("ca/qbt_investment_expenses", QBT_INVESTMENT_EXPENSES),
        ("ca/qbt_dividends_and_investment_income", QBT_DIVIDENDS_AND_INVESTMENT_INCOME),
        ("ca/qbt_other_property_income", QBT_OTHER_PROPERTY_INCOME),
        ("ca/qbt_partnership_taxable_capital_gains", QBT_PARTNERSHIP_TAXABLE_CAPITAL_GAINS),
        ("ca/qbt_partnership_income_other_than_gains", QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS),
        ("ca/qbt_exploration_recovery_income", QBT_EXPLORATION_RECOVERY_INCOME),
        (
            "ca/qbt_exploration_recovery_income_checked",
            QBT_EXPLORATION_RECOVERY_INCOME_CHECKED,
        ),
        ("ca/qbt_recovery_of_exploration_expenses", QBT_RECOVERY_OF_EXPLORATION_EXPENSES),
        ("ca/qbt_investment_income", QBT_INVESTMENT_INCOME),
        ("ca/qbt_chart_a_net_investment_loss", QBT_CHART_A_NET_INVESTMENT_LOSS),
        ("ca/qbt_earlier_allocation_total", QBT_EARLIER_ALLOCATION_TOTAL),
        ("ca/qbt_taxable_capital_gains_after_earlier", QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER),
        ("ca/qbt_earlier_abil_reduction_total", QBT_EARLIER_ABIL_REDUCTION_TOTAL),
        (
            "ca/qbt_allowable_business_investment_loss_after_earlier",
            QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER,
        ),
        (
            "ca/qbt_earlier_net_investment_loss_reduction_total",
            QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL,
        ),
        (
            "ca/qbt_chart_a_net_investment_loss_after_earlier",
            QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER,
        ),
        ("ca/qbt_election_is_qbt_in_order", QBT_ELECTION_IS_QBT_IN_ORDER),
    ):
        assert registry.get(identifier) is kind, identifier


def test_the_percentage_allocated_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Form T2048 line 2 "Percentage allocated to you" is refused above 100 (a choice: the form
    # prints no maximum). The maximum is a credit dataset's 100; the checked percentage is the
    # output of `core/at_most`, which the form's apply step reads in place of the input.
    assert registry.kind("ca/qbt_percentage_allocated_maximum") is QBT_PERCENTAGE_ALLOCATED_MAXIMUM
    assert registry.kind("ca/qbt_percentage_allocated_checked") is QBT_PERCENTAGE_ALLOCATED_CHECKED
    for kind in (QBT_PERCENTAGE_ALLOCATED_MAXIMUM, QBT_PERCENTAGE_ALLOCATED_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert QBT_PERCENTAGE_ALLOCATED_CHECKED is not QBT_PERCENTAGE_ALLOCATED


def test_the_election_eligible_amount_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Form T2048 line 1 "Total eligible amount for the joint election (maximum of $10 million per
    # election)" is refused above the printed maximum. The maximum is a credit dataset's figure;
    # the checked amount is the output of `core/at_most`, which line 3's step reads in place of the
    # input.
    assert (
        registry.kind("ca/qbt_election_eligible_amount_maximum")
        is QBT_ELECTION_ELIGIBLE_AMOUNT_MAXIMUM
    )
    assert (
        registry.kind("ca/qbt_election_eligible_amount_checked")
        is QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED
    )
    for kind in (QBT_ELECTION_ELIGIBLE_AMOUNT_MAXIMUM, QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED is not QBT_ELECTION_ELIGIBLE_AMOUNT


def test_the_form_t2048_kinds_are_money_and_counts() -> None:
    # Line 2 "Percentage allocated to you" is a number entered as printed (50 for 50%), so money.
    for kind in (
        QBT_PERCENTAGE_ALLOCATED,
        QBT_PERCENTAGE_ALLOCATED_MAXIMUM,
        QBT_PERCENTAGE_ALLOCATED_CHECKED,
        QBT_ELECTION_ELIGIBLE_AMOUNT,
        QBT_ELECTION_ELIGIBLE_AMOUNT_MAXIMUM,
        QBT_ELECTION_ELIGIBLE_AMOUNT_CHECKED,
        QBT_AMOUNT_ALLOCATED,
        QBT_TAXABLE_AMOUNT_ALLOCATED,
        QBT_PRIOR_YEARS_CLAIMS,
        QBT_PRIOR_YEARS_CLAIMS_CHECKED,
        QBT_2025_RESERVE_CHECKED,
        QBT_DEDUCTION_AVAILABLE,
        QBT_CAPITAL_GAINS,
        QBT_2024_RESERVE,
        QBT_CAPITAL_GAINS_WITH_2024_RESERVE,
        QBT_2025_RESERVE,
        QBT_TOTAL_CAPITAL_GAINS,
        QBT_TAXABLE_CAPITAL_GAINS,
        QBT_TAXABLE_GAINS_LIMIT,
        QBT_TAXABLE_GAINS_NOT_LIMITED,
        QBT_NET_CAPITAL_LOSSES_REMAINING,
        QBT_NET_INVESTMENT_LOSS,
        QBT_REDUCTIONS_FROM_LOSSES,
        QBT_DEDUCTION_CLAIMED,
        QBT_CAPITAL_GAINS_DEDUCTION,
        QBT_DEDUCTION_BASE,
        QBT_REDUCTION_AMOUNT,
        QBT_ALLOCATION_TOTAL,
        QBT_ABIL_AND_NET_INVESTMENT_LOSS,
        QBT_ALLOCATION_LIMIT,
        QBT_ABIL_REDUCTION,
        QBT_NET_INVESTMENT_LOSS_REDUCTION,
        QCC_ELECTION_DEDUCTION,
        QBT_ELECTION_DEDUCTION,
        QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
        QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
        QBT_NET_RENTAL_INCOME,
        QBT_NET_RENTAL_LOSS,
        QBT_PARTNERSHIP_LOSSES,
        QBT_EXPLORATION_EXPENSES_AT_HALF,
        QBT_OTHER_INVESTMENT_EXPENSES,
        QBT_CHART_A_NET_CAPITAL_LOSSES_USED,
        QBT_INVESTMENT_EXPENSES,
        QBT_DIVIDENDS_AND_INVESTMENT_INCOME,
        QBT_OTHER_PROPERTY_INCOME,
        QBT_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
        QBT_EXPLORATION_RECOVERY_INCOME,
        QBT_EXPLORATION_RECOVERY_INCOME_CHECKED,
        QBT_RECOVERY_OF_EXPLORATION_EXPENSES,
        QBT_CHART_A_NET_INVESTMENT_LOSS,
        QBT_EARLIER_ALLOCATION_TOTAL,
        QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER,
        QBT_EARLIER_ABIL_REDUCTION_TOTAL,
        QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER,
        QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL,
        # Chart A line 20 after note (3): the floor printed on line 20 applies to the result.
        QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    # "election is for a QBT", "gains are QSBCS/QFFP" and "you have investment expenses in 2025"
    # are 0 or 1, the pattern of the other yes/no inputs.
    for count in (
        QBT_HAS_INVESTMENT_EXPENSES,
        QBT_ELECTION_IS_QBT,
        QBT_GAINS_ARE_QSBCS_OR_QFFP,
        QBT_ELECTION_IS_QBT_IN_ORDER,
    ):
        assert count.value_type is int, count.identifier
        assert count.non_negative is True, count.identifier


def test_the_form_t2048_lines_26_and_27_are_signed_as_the_form_prints_them() -> None:
    # Line 26 "Line 17 minus line 25" and line 27 "whichever is less: amount from line 7 or line
    # 26" print no floor: both are negative when the losses on line 25 pass line 17.
    # Chart A lines 13 and 19 print no floor either: gains above line 12200 leave them negative.
    for kind in (
        QBT_DEDUCTION_LIMIT,
        QBT_MAXIMUM_DEDUCTION,
        QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
        QBT_INVESTMENT_INCOME,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier


def test_the_t2048_dispositions_kind_is_a_record_list_of_the_nine_inputs(
    registry: ArtifactRegistry,
) -> None:
    # Form T2048 is run once for each disposition: one record of the 9 starting inputs of Parts 2
    # to 5 and Chart A, in the order of the form's inputs (`01_inputs.yaml`, "Form T2048").
    assert registry.get("ca/t2048_dispositions") is T2048_DISPOSITIONS
    assert isinstance(T2048_DISPOSITIONS, RecordListKind)
    assert T2048_DISPOSITIONS.fields == (
        QBT_ELECTION_ELIGIBLE_AMOUNT,
        QBT_PERCENTAGE_ALLOCATED,
        QBT_PRIOR_YEARS_CLAIMS,
        QBT_CAPITAL_GAINS,
        QBT_2024_RESERVE,
        QBT_2025_RESERVE,
        QBT_DEDUCTION_CLAIMED,
        QBT_ELECTION_IS_QBT,
        QBT_GAINS_ARE_QSBCS_OR_QFFP,
    )


def test_the_shared_investment_facts_are_registered_non_negative_amounts(
    registry: ArtifactRegistry,
) -> None:
    # Form T936 Part 1 lines 3 and 6 and Part 2 lines 10 and 11 ask the same facts as Form T2048
    # Chart A lines 3, 6, 13 and 14: each is entered once, in a form of its own, and not a field of
    # the T2048 disposition record.
    for identifier, kind in (
        ("ca/non_active_partnership_losses", NON_ACTIVE_PARTNERSHIP_LOSSES),
        ("ca/other_investment_expenses", OTHER_INVESTMENT_EXPENSES),
        ("ca/other_property_income", OTHER_PROPERTY_INCOME),
        ("ca/partnership_taxable_capital_gains", PARTNERSHIP_TAXABLE_CAPITAL_GAINS),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is True, identifier
        assert kind not in T2048_DISPOSITIONS.fields, identifier


def test_the_investment_expenses_answer_is_a_registered_count_and_not_a_disposition_field(
    registry: ArtifactRegistry,
) -> None:
    # Form T2048 Part 3 line 24 "If you have investment expenses in 2025" is one answer for the
    # year: entered once, in a form of its own, checked to be 0 or 1, and not a field of the
    # T2048 disposition record.
    for identifier, kind in (
        ("ca/has_investment_expenses", HAS_INVESTMENT_EXPENSES),
        ("ca/has_investment_expenses_checked", HAS_INVESTMENT_EXPENSES_CHECKED),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
    assert QBT_HAS_INVESTMENT_EXPENSES not in T2048_DISPOSITIONS.fields


def test_the_form_t657_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    # Form T657 (Calculation of Capital Gains Deduction) Steps 1 and 2, Charts 1, 2 and 2025, and
    # line 25400 (T1 line 65).
    for identifier, kind in (
        ("ca/annual_gains_line_2", ANNUAL_GAINS_LINE_2),
        (
            "ca/t657_net_non_eligible_taxable_capital_gains",
            T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
        ),
        ("ca/t657_gains_1985_to_1991", T657_GAINS_1985_TO_1991),
        ("ca/t657_gains_1992_and_1993", T657_GAINS_1992_AND_1993),
        ("ca/t657_gains_1994", T657_GAINS_1994),
        ("ca/t657_gains_1995", T657_GAINS_1995),
        ("ca/t657_gains_1996_to_1999", T657_GAINS_1996_TO_1999),
        ("ca/t657_gains_2000", T657_GAINS_2000),
        ("ca/t657_gains_2001", T657_GAINS_2001),
        ("ca/t657_gains_2002_to_2024", T657_GAINS_2002_TO_2024),
        ("ca/t657_capital_losses_claimed_1985", T657_CAPITAL_LOSSES_CLAIMED_1985),
        ("ca/t657_abil_claimed_1985_to_2024", T657_ABIL_CLAIMED_1985_TO_2024),
        ("ca/t657_t2048_line_17217_for_2024", T657_T2048_LINE_17217_FOR_2024),
        ("ca/t657_cumulative_net_investment_loss", T657_CUMULATIVE_NET_INVESTMENT_LOSS),
        ("ca/t657_deductions_claimed_1985_to_2024", T657_DEDUCTIONS_CLAIMED_1985_TO_2024),
        ("ca/t657_chart_2_line_1", T657_CHART_2_LINE_1),
        ("ca/t657_chart_2_line_2", T657_CHART_2_LINE_2),
        ("ca/t657_chart_2_line_6", T657_CHART_2_LINE_6),
        ("ca/t657_chart_2_line_10", T657_CHART_2_LINE_10),
        ("ca/t657_chart_2_line_14", T657_CHART_2_LINE_14),
        ("ca/t657_inclusion_rate_2000", T657_INCLUSION_RATE_2000),
        ("ca/t657_chart_2_line_18", T657_CHART_2_LINE_18),
        ("ca/t657_part_1_amount_f", T657_PART_1_AMOUNT_F),
        ("ca/t657_part_1_amount_g", T657_PART_1_AMOUNT_G),
        ("ca/t657_part_1_amount_h", T657_PART_1_AMOUNT_H),
        ("ca/t657_part_1_amount_i", T657_PART_1_AMOUNT_I),
        ("ca/t657_part_1_amount_j", T657_PART_1_AMOUNT_J),
        ("ca/t657_part_1_amount_l", T657_PART_1_AMOUNT_L),
        ("ca/t657_part_2_excluded_f", T657_PART_2_EXCLUDED_F),
        ("ca/t657_part_2_excluded_g", T657_PART_2_EXCLUDED_G),
        ("ca/t657_part_2_excluded_h", T657_PART_2_EXCLUDED_H),
        ("ca/t657_part_2_amount_i", T657_PART_2_AMOUNT_I),
        ("ca/t657_part_2_amount_j", T657_PART_2_AMOUNT_J),
        ("ca/t657_part_2_amount_l", T657_PART_2_AMOUNT_L),
        ("ca/capital_gains_deduction_claimed", CAPITAL_GAINS_DEDUCTION_CLAIMED),
        ("ca/annual_gains_schedule_3_total", ANNUAL_GAINS_SCHEDULE_3_TOTAL),
        ("ca/annual_gains_line_3", ANNUAL_GAINS_LINE_3),
        ("ca/annual_gains_line_3_at_inclusion_rate", ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE),
        ("ca/annual_gains_line_5", ANNUAL_GAINS_LINE_5),
        ("ca/annual_gains_line_7", ANNUAL_GAINS_LINE_7),
        ("ca/schedule_3_line_19900", SCHEDULE_3_LINE_19900),
        ("ca/schedule_3_line_17600_not_below_zero", SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO),
        ("ca/annual_gains_line_9", ANNUAL_GAINS_LINE_9),
        ("ca/annual_gains_line_10", ANNUAL_GAINS_LINE_10),
        ("ca/annual_gains_line_12", ANNUAL_GAINS_LINE_12),
        ("ca/eligible_taxable_capital_gains_2025", ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025),
        (
            "ca/adjusted_net_capital_losses_of_other_years",
            ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
        ),
        ("ca/abil_after_qbt_reduction", ABIL_AFTER_QBT_REDUCTION),
        ("ca/total_losses_for_annual_gains_limit", TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT),
        ("ca/annual_gains_limit_2025", ANNUAL_GAINS_LIMIT_2025),
        (
            "ca/eligible_taxable_capital_gains_2002_to_2025",
            ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
        ),
        ("ca/cumulative_eligible_taxable_capital_gains", CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS),
        ("ca/abil_claimed_after_1984_and_before_2025", ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025),
        ("ca/chart_1_column_g_total", CHART_1_COLUMN_G_TOTAL),
        ("ca/cumulative_losses_and_deductions", CUMULATIVE_LOSSES_AND_DEDUCTIONS),
        ("ca/cumulative_gains_limit_2025", CUMULATIVE_GAINS_LIMIT_2025),
        ("ca/chart_2_line_3", CHART_2_LINE_3),
        ("ca/chart_2_line_4", CHART_2_LINE_4),
        ("ca/chart_2_line_5", CHART_2_LINE_5),
        ("ca/chart_2_line_7", CHART_2_LINE_7),
        ("ca/chart_2_line_8", CHART_2_LINE_8),
        ("ca/chart_2_line_9", CHART_2_LINE_9),
        ("ca/chart_2_line_11", CHART_2_LINE_11),
        ("ca/chart_2_line_12", CHART_2_LINE_12),
        ("ca/chart_2_line_13", CHART_2_LINE_13),
        ("ca/chart_2_line_15", CHART_2_LINE_15),
        ("ca/chart_2_twice_ir", CHART_2_TWICE_IR),
        ("ca/chart_2_line_14_over_twice_ir", CHART_2_LINE_14_OVER_TWICE_IR),
        ("ca/chart_2_line_16", CHART_2_LINE_16),
        ("ca/chart_2_line_17", CHART_2_LINE_17),
        ("ca/chart_2_line_19", CHART_2_LINE_19),
        ("ca/chart_2_numerator_one", CHART_2_NUMERATOR_ONE),
        ("ca/chart_2025_part_1_amount_a", CHART_2025_PART_1_AMOUNT_A),
        ("ca/chart_2025_part_1_amount_c", CHART_2025_PART_1_AMOUNT_C),
        ("ca/chart_2025_part_1_amount_e", CHART_2025_PART_1_AMOUNT_E),
        ("ca/chart_2025_part_1_amounts_f_to_j", CHART_2025_PART_1_AMOUNTS_F_TO_J),
        ("ca/chart_2025_part_1_amount_k", CHART_2025_PART_1_AMOUNT_K),
        ("ca/chart_2025_part_1_amount_m", CHART_2025_PART_1_AMOUNT_M),
        ("ca/chart_2025_part_1_amount_n", CHART_2025_PART_1_AMOUNT_N),
        ("ca/chart_2025_part_1_amount_p", CHART_2025_PART_1_AMOUNT_P),
        ("ca/chart_2025_part_1_amount_q", CHART_2025_PART_1_AMOUNT_Q),
        ("ca/chart_2025_part_2_amount_a", CHART_2025_PART_2_AMOUNT_A),
        ("ca/chart_2025_part_2_amount_c", CHART_2025_PART_2_AMOUNT_C),
        ("ca/chart_2025_part_2_amount_e", CHART_2025_PART_2_AMOUNT_E),
        ("ca/chart_2025_part_2_amount_f", CHART_2025_PART_2_AMOUNT_F),
        ("ca/chart_2025_part_2_amount_g", CHART_2025_PART_2_AMOUNT_G),
        ("ca/chart_2025_part_2_amount_h", CHART_2025_PART_2_AMOUNT_H),
        ("ca/chart_2025_part_2_amounts_f_to_j", CHART_2025_PART_2_AMOUNTS_F_TO_J),
        ("ca/chart_2025_part_2_amount_k", CHART_2025_PART_2_AMOUNT_K),
        ("ca/chart_2025_part_2_amount_m", CHART_2025_PART_2_AMOUNT_M),
        ("ca/chart_2025_part_2_amount_n", CHART_2025_PART_2_AMOUNT_N),
        ("ca/chart_2025_part_2_amount_p", CHART_2025_PART_2_AMOUNT_P),
        ("ca/chart_2025_part_2_amount_q", CHART_2025_PART_2_AMOUNT_Q),
        ("ca/chart_2025_part_2_maximum_claim", CHART_2025_PART_2_MAXIMUM_CLAIM),
        ("ca/capital_gains_deduction", CAPITAL_GAINS_DEDUCTION),
        ("ca/t657_chart_1_column_a", T657_CHART_1_COLUMN_A),
        ("ca/t657_chart_1_column_b", T657_CHART_1_COLUMN_B),
        ("ca/t657_chart_1_column_c", T657_CHART_1_COLUMN_C),
        ("ca/t657_chart_1_column_d", T657_CHART_1_COLUMN_D),
        ("ca/t657_chart_1_rows", T657_CHART_1_ROWS),
    ):
        assert registry.get(identifier) is kind, identifier


def test_the_form_t657_amounts_are_money_non_negative_except_the_signed_lines() -> None:
    # The lines that print "if negative, show in brackets", or no floor on a gain or loss, are
    # signed; every other amount, starting or computed, is non-negative.
    signed = (
        ANNUAL_GAINS_LINE_2,
        T657_PART_1_AMOUNT_I,
        T657_PART_1_AMOUNT_J,
        T657_PART_2_AMOUNT_I,
        T657_PART_2_AMOUNT_J,
        ANNUAL_GAINS_SCHEDULE_3_TOTAL,
        ANNUAL_GAINS_LINE_3,
        ANNUAL_GAINS_LINE_3_AT_INCLUSION_RATE,
        ANNUAL_GAINS_LINE_7,
        SCHEDULE_3_LINE_19900,
        ANNUAL_GAINS_LINE_10,
        ANNUAL_GAINS_LINE_12,
        ELIGIBLE_TAXABLE_CAPITAL_GAINS_2025,
        ELIGIBLE_TAXABLE_CAPITAL_GAINS_2002_TO_2025,
        CUMULATIVE_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
        CHART_2025_PART_2_AMOUNT_F,
        CHART_2025_PART_2_AMOUNT_G,
        CHART_2025_PART_2_AMOUNT_H,
        CUMULATIVE_LOSSES_AND_DEDUCTIONS,
        TOTAL_LOSSES_FOR_ANNUAL_GAINS_LIMIT,
        ABIL_CLAIMED_AFTER_1984_AND_BEFORE_2025,
        ABIL_AFTER_QBT_REDUCTION,
        CHART_2025_PART_1_AMOUNT_C,
        CHART_2025_PART_1_AMOUNT_M,
        CHART_2025_PART_1_AMOUNT_N,
        CHART_2025_PART_1_AMOUNT_P,
        CHART_2025_PART_1_AMOUNT_Q,
        CHART_2025_PART_2_AMOUNT_C,
        CHART_2025_PART_2_AMOUNT_M,
        CHART_2025_PART_2_AMOUNT_N,
        CHART_2025_PART_2_AMOUNT_P,
        CHART_2025_PART_2_AMOUNT_Q,
    )
    for kind in signed:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier
    for kind in (
        T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
        T657_GAINS_1985_TO_1991,
        T657_GAINS_1992_AND_1993,
        T657_GAINS_1994,
        T657_GAINS_1995,
        T657_GAINS_1996_TO_1999,
        T657_GAINS_2000,
        T657_GAINS_2001,
        T657_GAINS_2002_TO_2024,
        T657_CAPITAL_LOSSES_CLAIMED_1985,
        T657_ABIL_CLAIMED_1985_TO_2024,
        T657_T2048_LINE_17217_FOR_2024,
        T657_CUMULATIVE_NET_INVESTMENT_LOSS,
        T657_DEDUCTIONS_CLAIMED_1985_TO_2024,
        T657_CHART_2_LINE_1,
        T657_CHART_2_LINE_2,
        T657_CHART_2_LINE_6,
        T657_CHART_2_LINE_10,
        T657_CHART_2_LINE_14,
        T657_INCLUSION_RATE_2000,
        T657_CHART_2_LINE_18,
        T657_PART_1_AMOUNT_F,
        T657_PART_1_AMOUNT_G,
        T657_PART_1_AMOUNT_H,
        T657_PART_1_AMOUNT_L,
        T657_PART_2_EXCLUDED_F,
        T657_PART_2_EXCLUDED_G,
        T657_PART_2_EXCLUDED_H,
        T657_PART_2_AMOUNT_L,
        CAPITAL_GAINS_DEDUCTION_CLAIMED,
        ANNUAL_GAINS_LINE_5,
        SCHEDULE_3_LINE_17600_NOT_BELOW_ZERO,
        ANNUAL_GAINS_LINE_9,
        ADJUSTED_NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
        ANNUAL_GAINS_LIMIT_2025,
        CHART_1_COLUMN_G_TOTAL,
        CUMULATIVE_GAINS_LIMIT_2025,
        CHART_2_LINE_3,
        CHART_2_LINE_4,
        CHART_2_LINE_5,
        CHART_2_LINE_7,
        CHART_2_LINE_8,
        CHART_2_LINE_9,
        CHART_2_LINE_11,
        CHART_2_LINE_12,
        CHART_2_LINE_13,
        CHART_2_LINE_15,
        CHART_2_TWICE_IR,
        CHART_2_LINE_14_OVER_TWICE_IR,
        CHART_2_LINE_16,
        CHART_2_LINE_17,
        CHART_2_LINE_19,
        CHART_2_NUMERATOR_ONE,
        CHART_2025_PART_1_AMOUNT_A,
        CHART_2025_PART_1_AMOUNT_E,
        CHART_2025_PART_1_AMOUNTS_F_TO_J,
        CHART_2025_PART_1_AMOUNT_K,
        CHART_2025_PART_2_AMOUNT_A,
        CHART_2025_PART_2_AMOUNT_E,
        CHART_2025_PART_2_AMOUNTS_F_TO_J,
        CHART_2025_PART_2_AMOUNT_K,
        CHART_2025_PART_2_MAXIMUM_CLAIM,
        CAPITAL_GAINS_DEDUCTION,
        T657_CHART_1_COLUMN_A,
        T657_CHART_1_COLUMN_B,
        T657_CHART_1_COLUMN_C,
        T657_CHART_1_COLUMN_D,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_chart_1_is_a_record_list_of_one_record_for_each_year_row(
    registry: ArtifactRegistry,
) -> None:
    # Chart 1 "Calculate your net capital losses of other years (line 14 of Step 2)": columns A to
    # D of each printed year row; a cell the form prints N/A is left 0 by the filer.
    assert registry.get("ca/t657_chart_1_rows") is T657_CHART_1_ROWS
    assert isinstance(T657_CHART_1_ROWS, RecordListKind)
    assert T657_CHART_1_ROWS.fields == (
        T657_CHART_1_COLUMN_A,
        T657_CHART_1_COLUMN_B,
        T657_CHART_1_COLUMN_C,
        T657_CHART_1_COLUMN_D,
    )


# --- more than one disposition: notes (1) to (3) and the order of the claims ---------------------
#
# The kinds are the sums of the earlier runs and the lines as corrected, each with a docstring that
# quotes the form's own words (`docs/cra-forms-2025/t2048-25e.pdf`).

EARLIER_RUNS_QUOTES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "qbt_earlier_allocation_total",
        ("T2048", "subtract the sum of all previous amounts from line 32 of the next page"),
    ),
    (
        "qbt_taxable_capital_gains_after_earlier",
        (
            "T2048",
            "Taxable capital gains from line 12700 of your return",
            "subtract the sum of all previous amounts from line 32 of the next page",
        ),
    ),
    (
        "qbt_earlier_abil_reduction_total",
        ("T2048", "subtract the sum of all previous amounts from line 41 above"),
    ),
    (
        "qbt_allowable_business_investment_loss_after_earlier",
        (
            "T2048",
            "Allowable business investment loss (ABIL) for the year (line 21700 of your return)",
            "subtract the sum of all previous amounts from line 41 above",
        ),
    ),
    (
        "qbt_earlier_net_investment_loss_reduction_total",
        ("T2048", "subtract the sum of all previous amounts from line 42 of Part 4"),
    ),
    (
        "qbt_chart_a_net_investment_loss_after_earlier",
        (
            "T2048",
            'Line 10 minus line 19 (if negative enter "0")',
            "subtract the sum of all previous amounts from line 42 of Part 4",
        ),
    ),
    (
        "qbt_election_is_qbt_in_order",
        (
            "T2048",
            "You must claim any deduction under a QBT before any deduction under a QCC",
        ),
    ),
)


def squashed(text: str) -> str:
    """`text` with every run of white space made one blank."""
    return re.sub(r"\s+", " ", text).strip()


def docstring_of(name: str) -> str:
    """The string right after `NAME = CATALOG.declare("<name>", ...)` in a catalog module."""
    folder = Path(tax_calculator.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            arguments = statement.value.args
            if not (
                arguments
                and isinstance(arguments[0], ast.Constant)
                and arguments[0].value == name
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {name!r} followed by a docstring")


@pytest.mark.parametrize(
    ("name", "quotes"), EARLIER_RUNS_QUOTES, ids=[name for name, _ in EARLIER_RUNS_QUOTES]
)
def test_each_earlier_runs_kind_docstring_quotes_the_form(
    name: str, quotes: tuple[str, ...]
) -> None:
    docstring = squashed(docstring_of(name))

    for quote in quotes:
        assert squashed(quote) in docstring, quote
