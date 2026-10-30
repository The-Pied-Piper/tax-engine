"""Registered and money kinds of the federal catalog family `income`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    BOND_DISPOSITIONS,
    BOND_GAIN_OR_LOSS,
    BOND_PROCEEDS,
    BUSINESS_CAPITAL_CONTRIBUTIONS,
    BUSINESS_DRAWINGS,
    BUSINESS_EPOP_AGREEMENT_FILED,
    BUSINESS_EPOP_AGREEMENT_FILED_CHECKED,
    BUSINESS_EPOP_ASSOCIATED,
    BUSINESS_EPOP_ASSOCIATED_CHECKED,
    BUSINESS_EPOP_PERCENTAGE,
    BUSINESS_EPOP_PERCENTAGE_MAXIMUM,
    BUSINESS_EPOP_PERCENTAGE_ROOM,
    BUSINESS_EPOP_PERCENTAGE_TOTAL,
    BUSINESS_FISCAL_PERIOD_DAYS,
    BUSINESS_FISCAL_PERIOD_FROM,
    BUSINESS_FISCAL_PERIOD_TO,
    BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED,
    BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_CAP,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    BUSINESS_IMMEDIATE_EXPENSING_SHARE,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_LAND_ADDITIONS,
    BUSINESS_LAND_DISPOSITIONS,
    BUSINESS_LIABILITIES,
    BUSINESS_MINISTER_ALLOCATION,
    BUSINESS_MINISTER_ALLOCATION_GIVEN,
    BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
    BUSINESS_PARTNER_CHECKED,
    BUSINESS_VEHICLE_DAYS_DIVISOR,
    BUSINESS_VEHICLE_LIST_PRICE,
    BUSINESS_VEHICLE_SALES_TAX_RATE,
    BUSINESS_VEHICLES,
    CAPITAL_GAIN,
    CAPITAL_GAINS_AFTER_DEFERRAL,
    CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION,
    CAPITAL_GAINS_BEFORE_RESERVES,
    CAPITAL_GAINS_DEFERRAL,
    CAPITAL_GAINS_DEFERRAL_CHECKED,
    CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    CCA_SOLD_ZEPVS,
    COMMISSION_INCOME,
    CPP_OR_QPP_BENEFITS,
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    CRYPTO_ASSET_DISPOSITIONS,
    CRYPTO_ASSET_GAIN_OR_LOSS,
    CRYPTO_ASSET_PROCEEDS,
    DISPOSITION_ADJUSTED_COST_BASE,
    DISPOSITION_DEPRECIABLE_PROPERTY,
    DISPOSITION_FARM_LOSS_INTEREST,
    DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
    DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
    DISPOSITION_OUTLAYS,
    DISPOSITION_PROCEEDS,
    DIVIDEND_TAX_CREDIT,
    DIVIDENDS_AMOUNT_A,
    DIVIDENDS_AMOUNT_A_LESS_B,
    DIVIDENDS_AMOUNT_B,
    DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP,
    EI_AND_OTHER_BENEFITS,
    EI_MATERNITY_PARENTAL_BENEFITS,
    ELECTED_SPLIT_PENSION_AMOUNT,
    ELIGIBLE_DIVIDENDS_CREDIT,
    ELIGIBLE_DIVIDENDS_GROSSED_UP,
    ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
    EMERGENCY_SERVICES_VOLUNTEER_CONFLICT_CHECKED,
    EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
    EMPLOYMENT_INCOME,
    FARM_ALSO_OUTSIDE_EIGHT,
    FARM_AMOUNT_8_AB,
    FARM_AMOUNT_8_MB,
    FARM_AMOUNT_8_NB,
    FARM_AMOUNT_8_NL,
    FARM_AMOUNT_8_NS,
    FARM_AMOUNT_8_ON,
    FARM_AMOUNT_8_PE,
    FARM_AMOUNT_8_SK,
    FARM_CAPITAL_CONTRIBUTIONS,
    FARM_CHART_A_AMOUNT_8,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_SUBTOTAL,
    FARM_DAYS_IN_2024,
    FARM_DESIGNATED_PROVINCE,
    FARM_DRAWINGS,
    FARM_EPOP_AGREEMENT_FILED,
    FARM_EPOP_AGREEMENT_FILED_CHECKED,
    FARM_EPOP_ASSOCIATED,
    FARM_EPOP_ASSOCIATED_CHECKED,
    FARM_EPOP_PERCENTAGE,
    FARM_EPOP_PERCENTAGE_MAXIMUM,
    FARM_EPOP_PERCENTAGE_ROOM,
    FARM_EPOP_PERCENTAGE_TOTAL,
    FARM_FISCAL_PERIOD_DAYS,
    FARM_FISCAL_PERIOD_DAYS_ENTERED,
    FARM_IMMEDIATE_EXPENSING_ALLOCATED,
    FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FARM_IMMEDIATE_EXPENSING_CAP,
    FARM_IMMEDIATE_EXPENSING_CLAIM,
    FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FARM_IMMEDIATE_EXPENSING_LIMIT,
    FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FARM_IMMEDIATE_EXPENSING_SHARE,
    FARM_IN_PROVINCE_AB,
    FARM_IN_PROVINCE_MB,
    FARM_IN_PROVINCE_NB,
    FARM_IN_PROVINCE_NL,
    FARM_IN_PROVINCE_NS,
    FARM_IN_PROVINCE_ON,
    FARM_IN_PROVINCE_PE,
    FARM_IN_PROVINCE_SK,
    FARM_INCOME_BEFORE_CCA,
    FARM_LAND_ADDITIONS,
    FARM_LAND_DISPOSITIONS,
    FARM_LIABILITIES,
    FARM_MINISTER_ALLOCATION,
    FARM_MINISTER_ALLOCATION_GIVEN,
    FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FARM_MOTOR_VEHICLE_EXPENSES,
    FARM_NON_ARMS_LENGTH_EXPENSES,
    FARM_PARTNER_CHECKED,
    FARM_PRESENT_AMOUNT_AB,
    FARM_PRESENT_AMOUNT_MB,
    FARM_PRESENT_AMOUNT_NB,
    FARM_PRESENT_AMOUNT_NL,
    FARM_PRESENT_AMOUNT_NS,
    FARM_PRESENT_AMOUNT_ON,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT,
    FARM_PRESENT_AMOUNT_PE,
    FARM_PRESENT_AMOUNT_SK,
    FARM_PRESENT_IN_PROVINCE_AB,
    FARM_PRESENT_IN_PROVINCE_MB,
    FARM_PRESENT_IN_PROVINCE_NB,
    FARM_PRESENT_IN_PROVINCE_NL,
    FARM_PRESENT_IN_PROVINCE_NS,
    FARM_PRESENT_IN_PROVINCE_ON,
    FARM_PRESENT_IN_PROVINCE_PE,
    FARM_PRESENT_IN_PROVINCE_SK,
    FARM_PRESENT_OUTSIDE_EIGHT,
    FARM_QUOTA_ADDITIONS,
    FARM_QUOTA_DISPOSITIONS,
    FARM_VEHICLE_SALES_TAX_RATE,
    FARMING_INCOME,
    FHSA_INCOME,
    FISH_CAPITAL_CONTRIBUTIONS,
    FISH_DRAWINGS,
    FISH_EPOP_AGREEMENT_FILED,
    FISH_EPOP_AGREEMENT_FILED_CHECKED,
    FISH_EPOP_ASSOCIATED,
    FISH_EPOP_ASSOCIATED_CHECKED,
    FISH_EPOP_PERCENTAGE,
    FISH_EPOP_PERCENTAGE_MAXIMUM,
    FISH_EPOP_PERCENTAGE_ROOM,
    FISH_EPOP_PERCENTAGE_TOTAL,
    FISH_FISCAL_PERIOD_DAYS,
    FISH_FISCAL_PERIOD_DAYS_ENTERED,
    FISH_IMMEDIATE_EXPENSING_ALLOCATED,
    FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FISH_IMMEDIATE_EXPENSING_CAP,
    FISH_IMMEDIATE_EXPENSING_CLAIM,
    FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FISH_IMMEDIATE_EXPENSING_LIMIT,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FISH_IMMEDIATE_EXPENSING_SHARE,
    FISH_INCOME_BEFORE_CCA,
    FISH_LAND_ADDITIONS,
    FISH_LAND_DISPOSITIONS,
    FISH_LIABILITIES,
    FISH_MINISTER_ALLOCATION,
    FISH_MINISTER_ALLOCATION_GIVEN,
    FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FISH_MOTOR_VEHICLE_EXPENSES,
    FISH_PARTNER_CHECKED,
    FISH_VEHICLE_SALES_TAX_RATE,
    FISHING_INCOME,
    FLIPPED_PROPERTY,
    FLIPPED_PROPERTY_DISPOSED,
    FLIPPED_PROPERTY_DISPOSED_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_1,
    FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_2,
    FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_3,
    FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_4,
    FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_5,
    FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_6,
    FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_7,
    FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_8,
    FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_9,
    FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
    FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES,
    FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED,
    FOREIGN_INVESTMENT_INCOME,
    FUEL_CHARGE_FARM_STATEMENT_COUNT,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
    FUEL_CHARGE_MULTIPLE_PROVINCES_BOX,
    GROSS_RENTAL_INCOME,
    IMMEDIATE_EXPENSING_AGREED_LIMIT,
    IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS,
    IMMEDIATE_EXPENSING_TOTAL_CLAIM,
    INCLUDED_CAPITAL_GAIN,
    INCOME_SUPPORT_BENEFITS,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
    INVESTMENT_INCOME_CREDITED_NOT_RECEIVED,
    INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS,
    INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED,
    INVESTMENT_INCOME_WITHOUT_A_SLIP,
    INVESTMENT_ROYALTIES,
    LISTED_PERSONAL_PROPERTY_DISPOSITIONS,
    LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS,
    LISTED_PERSONAL_PROPERTY_NET_GAIN,
    NET_FEDERAL_SUPPLEMENTS,
    NET_PARTNERSHIP_INCOME,
    NET_RENTAL_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    NO_SLIP_DIVIDEND_TAX_CREDIT,
    NON_COMPLIANT_CCA,
    OLD_AGE_SECURITY,
    OTHER_DIVIDENDS_CREDIT,
    OTHER_DIVIDENDS_GROSSED_UP,
    OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_FHSA_INCOME,
    OTHER_FORECLOSURE_DISPOSITIONS,
    OTHER_FORECLOSURE_GAIN_OR_LOSS,
    OTHER_FORECLOSURE_PROCEEDS,
    OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    OTHER_INCOME,
    OTHER_PENSIONS_AND_SUPERANNUATION,
    PARTNERSHIP_GAINS_AT_FULL_INCLUSION,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    PROFESSIONAL_INCOME,
    QFFP_DISPOSITIONS,
    QFFP_FORECLOSURE_DISPOSITIONS,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_FORECLOSURE_PROCEEDS,
    QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    QFFP_GAIN_OR_LOSS,
    QFFP_PROCEEDS,
    QFFP_RESTRICTED_FARM_LOSS_APPLIED,
    QSBCS_DISPOSITIONS,
    QSBCS_GAIN_OR_LOSS,
    QSBCS_PROCEEDS,
    RDSP_INCOME,
    REAL_ESTATE_DISPOSITIONS,
    REAL_ESTATE_GAIN_OR_LOSS,
    REAL_ESTATE_PROCEEDS,
    REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED,
    RENTAL_ADDITION_PERSONAL_PORTION,
    RENTAL_ADDITION_TOTAL_COST,
    RENTAL_ADVERTISING,
    RENTAL_ADVERTISING_PERSONAL_PORTION,
    RENTAL_ADVERTISING_SHORT_TERM_PORTION,
    RENTAL_BUILDING_ADDITIONS,
    RENTAL_BUILDING_ADDITIONS_TOTAL,
    RENTAL_CCA_ADDITIONS_TOTAL,
    RENTAL_CCA_BUSINESS_USE_OF_HOME,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_LESS_PERSONAL_PART,
    RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES,
    RENTAL_CCA_CLAIM_SHARE,
    RENTAL_CCA_CLAIMS_TOTAL,
    RENTAL_CCA_CLASSES,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_LIMIT_ALL_STATEMENTS,
    RENTAL_CCA_OPENING_UCC_TOTAL,
    RENTAL_CCA_PERSONAL_PART,
    RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CCA_TABLE_RECAPTURE,
    RENTAL_CCA_TABLE_TERMINAL_LOSS,
    RENTAL_CCA_TOTAL_CLAIM,
    RENTAL_CLOSING_UCC,
    RENTAL_COOWNER,
    RENTAL_COOWNER_CCA_CLAIM,
    RENTAL_COOWNER_CCA_CLAIM_CHECKED,
    RENTAL_COOWNER_CHECKED,
    RENTAL_COOWNER_OTHER_EXPENSES,
    RENTAL_COOWNER_RECAPTURED_CCA,
    RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
    RENTAL_COOWNER_SHARE,
    RENTAL_COOWNER_TERMINAL_LOSS,
    RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_EPOP_AGREEMENT_FILED,
    RENTAL_EPOP_AGREEMENT_FILED_CHECKED,
    RENTAL_EPOP_ASSOCIATED,
    RENTAL_EPOP_ASSOCIATED_CHECKED,
    RENTAL_EPOP_PERCENTAGE,
    RENTAL_EPOP_PERCENTAGE_MAXIMUM,
    RENTAL_EPOP_PERCENTAGE_ROOM,
    RENTAL_EPOP_PERCENTAGE_TOTAL,
    RENTAL_EQUIPMENT_ADDITIONS,
    RENTAL_EQUIPMENT_ADDITIONS_TOTAL,
    RENTAL_EXPENSES_LESS_PERSONAL_PORTION,
    RENTAL_FISCAL_PERIOD_DAYS,
    RENTAL_FISCAL_PERIOD_DAYS_ENTERED,
    RENTAL_GROSS_RENTS,
    RENTAL_IMMEDIATE_EXPENSING_ALLOCATED,
    RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_CAP,
    RENTAL_IMMEDIATE_EXPENSING_CLAIM,
    RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    RENTAL_IMMEDIATE_EXPENSING_SHARE,
    RENTAL_INCOME_BEFORE_CCA,
    RENTAL_INCOME_BEFORE_CCA_TOTAL,
    RENTAL_INSURANCE,
    RENTAL_INSURANCE_PERSONAL_PORTION,
    RENTAL_INSURANCE_SHORT_TERM_PORTION,
    RENTAL_INTEREST_AND_BANK_CHARGES,
    RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION,
    RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION,
    RENTAL_LAND_ADDITIONS,
    RENTAL_LAND_DISPOSITIONS,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION,
    RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION,
    RENTAL_MINISTER_ALLOCATION,
    RENTAL_MINISTER_ALLOCATION_GIVEN,
    RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
    RENTAL_MOTOR_VEHICLE_EXPENSES,
    RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION,
    RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_NO_CCA_CLAIM,
    RENTAL_NON_COMPLIANT_CCA,
    RENTAL_NON_COMPLIANT_EXPENSES,
    RENTAL_OFFICE_EXPENSES,
    RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION,
    RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_OTHER_EXPENSES,
    RENTAL_OTHER_EXPENSES_PERSONAL_PORTION,
    RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION,
    RENTAL_OTHER_INCOME,
    RENTAL_PARTNER,
    RENTAL_PARTNER_AMOUNT_7,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED,
    RENTAL_PARTNER_CHECKED,
    RENTAL_PARTNER_GST_HST_REBATE,
    RENTAL_PARTNER_OTHER_EXPENSES,
    RENTAL_PARTNER_PERCENTAGE,
    RENTAL_PARTNER_PERCENTAGE_CHECKED,
    RENTAL_PARTNER_SHARE,
    RENTAL_PARTNER_SHARE_OF_AMOUNT_6,
    RENTAL_PARTNER_SHARE_WITH_REBATE,
    RENTAL_PARTNER_T5013_SLIP,
    RENTAL_PARTNER_T5013_SLIP_CHECKED,
    RENTAL_PARTNERSHIP_NET_INCOME,
    RENTAL_PERSONAL_PORTION,
    RENTAL_PROFESSIONAL_FEES,
    RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION,
    RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION,
    RENTAL_PROPERTIES,
    RENTAL_PROPERTY_GROSS_RENTS,
    RENTAL_PROPERTY_SHORT_TERM_RENTS,
    RENTAL_PROPERTY_TAXES,
    RENTAL_PROPERTY_TAXES_PERSONAL_PORTION,
    RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION,
    RENTAL_PROPERTY_UNITS,
    RENTAL_RECAPTURED_CCA,
    RENTAL_REPAIRS_AND_MAINTENANCE,
    RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION,
    RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION,
    RENTAL_SALARIES_WAGES_AND_BENEFITS,
    RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION,
    RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION,
    RENTAL_SHORT_TERM_PORTION,
    RENTAL_T5013_SLIP_CONFLICT,
    RENTAL_T5013_SLIP_CONFLICT_CHECKED,
    RENTAL_TERMINAL_LOSS,
    RENTAL_TOTAL_EXPENSES,
    RENTAL_TRAVEL,
    RENTAL_TRAVEL_PERSONAL_PORTION,
    RENTAL_TRAVEL_SHORT_TERM_PORTION,
    RENTAL_UTILITIES,
    RENTAL_UTILITIES_PERSONAL_PORTION,
    RENTAL_UTILITIES_SHORT_TERM_PORTION,
    RENTAL_VEHICLE_SALES_TAX_RATE,
    RRSP_INCOME,
    SCHEDULE_3_LINE_19200,
    SHARE_DISPOSITIONS,
    SHARE_GAIN_NOT_BELOW_ZERO,
    SHARE_GAIN_OR_LOSS,
    SHARE_PROCEEDS,
    SHORT_TERM_RENTAL_CCA_UNITS,
    SHORT_TERM_RENTAL_DAYS,
    SHORT_TERM_RENTAL_GROSS_RENTS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
    SHORT_TERM_RENTAL_RELATED_CCA,
    SHORT_TERM_RENTAL_RELATED_EXPENSES,
    SHORT_TERM_RENTAL_UNITS,
    SLIP_CAPITAL_GAINS_OR_LOSSES,
    SLIP_DIVIDEND_TAX_CREDIT,
    SLIP_TAXABLE_DIVIDENDS,
    SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    SOCIAL_ASSISTANCE_PAYMENTS,
    SUPPORT_PAYMENTS_RECEIVED_TOTAL,
    T3_CAPITAL_GAINS_OR_LOSSES,
    T3_DIVIDEND_TAX_CREDIT,
    T3_INVESTMENT_INCOME,
    T3_TAXABLE_DIVIDENDS,
    T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T4_COMMISSIONS,
    T4AP_DISABILITY_BENEFITS,
    T4PS_DIVIDEND_TAX_CREDIT,
    T4PS_TAXABLE_DIVIDENDS,
    T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T5_DIVIDEND_TAX_CREDIT,
    T5_INVESTMENT_INCOME,
    T5_TAXABLE_DIVIDENDS,
    T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T776_STATEMENTS,
    T2042_STATEMENTS,
    T2121_STATEMENTS,
    T2125_STATEMENTS,
    T5013_DIVIDEND_TAX_CREDIT,
    T5013_INVESTMENT_INCOME,
    T5013_TAXABLE_DIVIDENDS,
    T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    TAX_REFUND_INTEREST,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_SCHOLARSHIPS,
    TAXABLE_SUPPORT_PAYMENTS,
    TOTAL_INCOME,
    UCCB_DESIGNATED_TO_DEPENDANT,
    UNAPPLIED_LISTED_PERSONAL_PROPERTY_LOSSES,
    UNIVERSAL_CHILD_CARE_BENEFIT,
    WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS,
    WORKERS_COMPENSATION_BENEFITS,
)
from tests.jurisdictions.ca.catalog_snapshot import (
    COUNTS,
    RECORD_LISTS,
    REGISTERED,
    SIGNED,
)

# The Form T2043 Chart A amounts of each Form T2042 statement: amount 5, amount 6, amount 8 and the
# eight province amounts of amount 8, each an amount computed for each statement.
T2043_CHART_A_AMOUNTS = (
    FARM_CHART_A_SUBTOTAL,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_AMOUNT_8,
    FARM_AMOUNT_8_ON,
    FARM_AMOUNT_8_MB,
    FARM_AMOUNT_8_SK,
    FARM_AMOUNT_8_AB,
    FARM_AMOUNT_8_NS,
    FARM_AMOUNT_8_PE,
    FARM_AMOUNT_8_NL,
    FARM_AMOUNT_8_NB,
)


def test_the_form_t2043_statement_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/farm_designated_province") is FARM_DESIGNATED_PROVINCE
    assert registry.get("ca/farm_non_arms_length_expenses") is FARM_NON_ARMS_LENGTH_EXPENSES
    assert registry.get("ca/farm_days_in_2024") is FARM_DAYS_IN_2024


def test_the_form_t2043_statement_fields_are_an_int_code_an_int_count_and_an_amount() -> None:
    assert FARM_DESIGNATED_PROVINCE.value_type is int
    assert FARM_DAYS_IN_2024.value_type is int
    assert FARM_NON_ARMS_LENGTH_EXPENSES.value_type is Decimal
    assert {FARM_DESIGNATED_PROVINCE.identifier, FARM_DAYS_IN_2024.identifier} <= COUNTS
    assert FARM_NON_ARMS_LENGTH_EXPENSES.non_negative
    assert FARM_DAYS_IN_2024.non_negative


def test_the_checked_designated_province_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    # The statement's province code once `ca/count_refused_by_conditions` has refused a code above
    # 8: the eight province counts of Chart A read this kind, not the raw code.
    kind = _kind(registry, "ca/farm_designated_province_checked")

    assert kind.value_type is int
    assert kind.non_negative is True
    assert kind.identifier in COUNTS
    assert kind.identifier in REGISTERED
    assert kind is not FARM_DESIGNATED_PROVINCE


def test_the_chart_a_amounts_are_registered_money_on_each_statement(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_CHART_A_AMOUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_chart_a_gross_expenses_is_signed_money() -> None:
    # Amount 6 "Amount 1 minus amount 5" prints no floor and amount 5 no maximum, so it may be below
    # zero.
    assert FARM_CHART_A_GROSS_EXPENSES.value_type is Decimal
    assert not FARM_CHART_A_GROSS_EXPENSES.non_negative
    assert "ca/farm_chart_a_gross_expenses" in SIGNED


# Form T2042 Chart A amount 8 "Amount 6 multiplied by amount 7" for each province: the count of
# each province's condition (1 when the designated province is that one, else 0) is an int count,
# and the amount for the province is the amount 8 times that count.
T2043_FARM_IN_PROVINCE_COUNTS = (
    FARM_IN_PROVINCE_ON,
    FARM_IN_PROVINCE_MB,
    FARM_IN_PROVINCE_SK,
    FARM_IN_PROVINCE_AB,
    FARM_IN_PROVINCE_NS,
    FARM_IN_PROVINCE_PE,
    FARM_IN_PROVINCE_NL,
    FARM_IN_PROVINCE_NB,
)


def test_the_farm_in_province_counts_are_registered_non_negative_ints(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_FARM_IN_PROVINCE_COUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is int, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.non_negative, kind.identifier


# Form T2043 box 67062 (multiple farming businesses in multiple provinces): each statement's
# presence in the nine places (the eight designated provinces, then outside eight) is an int count,
# and the presence amount of each place is the statements present in it, Decimal money of the
# statement. The statement count and the box are int counts of the statements.
T2043_PRESENT_IN_PLACE_COUNTS = (
    FARM_PRESENT_IN_PROVINCE_ON,
    FARM_PRESENT_IN_PROVINCE_MB,
    FARM_PRESENT_IN_PROVINCE_SK,
    FARM_PRESENT_IN_PROVINCE_AB,
    FARM_PRESENT_IN_PROVINCE_NS,
    FARM_PRESENT_IN_PROVINCE_PE,
    FARM_PRESENT_IN_PROVINCE_NL,
    FARM_PRESENT_IN_PROVINCE_NB,
    FARM_PRESENT_OUTSIDE_EIGHT,
)
T2043_PRESENT_AMOUNTS = (
    FARM_PRESENT_AMOUNT_ON,
    FARM_PRESENT_AMOUNT_MB,
    FARM_PRESENT_AMOUNT_SK,
    FARM_PRESENT_AMOUNT_AB,
    FARM_PRESENT_AMOUNT_NS,
    FARM_PRESENT_AMOUNT_PE,
    FARM_PRESENT_AMOUNT_NL,
    FARM_PRESENT_AMOUNT_NB,
    FARM_PRESENT_AMOUNT_OUTSIDE_EIGHT,
)
T2043_FUEL_CHARGE_PLACE_TOTALS = (
    FUEL_CHARGE_FARMS_IN_PROVINCE_ON,
    FUEL_CHARGE_FARMS_IN_PROVINCE_MB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_SK,
    FUEL_CHARGE_FARMS_IN_PROVINCE_AB,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NS,
    FUEL_CHARGE_FARMS_IN_PROVINCE_PE,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NL,
    FUEL_CHARGE_FARMS_IN_PROVINCE_NB,
    FUEL_CHARGE_FARMS_OUTSIDE_EIGHT,
)


def test_the_presence_counts_are_registered_non_negative_ints(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_PRESENT_IN_PLACE_COUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_presence_amounts_are_registered_non_negative_money_and_not_counts(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_PRESENT_AMOUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier
        assert kind.identifier not in COUNTS, kind.identifier


def test_the_fuel_charge_place_totals_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_FUEL_CHARGE_PLACE_TOTALS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_statement_count_and_the_box_are_registered_non_negative_ints(
    registry: ArtifactRegistry,
) -> None:
    for kind in (FUEL_CHARGE_FARM_STATEMENT_COUNT, FUEL_CHARGE_MULTIPLE_PROVINCES_BOX):
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_income_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/employment_income") is EMPLOYMENT_INCOME
    assert registry.get("ca/capital_gain") is CAPITAL_GAIN
    assert registry.get("ca/taxable_capital_gains") is TAXABLE_CAPITAL_GAINS
    assert registry.get("ca/total_income") is TOTAL_INCOME
    assert registry.get("ca/other_employment_income") is OTHER_EMPLOYMENT_INCOME
    assert registry.get("ca/old_age_security") is OLD_AGE_SECURITY
    assert registry.get("ca/cpp_or_qpp_benefits") is CPP_OR_QPP_BENEFITS
    assert registry.get("ca/other_pensions_and_superannuation") is OTHER_PENSIONS_AND_SUPERANNUATION
    assert registry.get("ca/elected_split_pension_amount") is ELECTED_SPLIT_PENSION_AMOUNT
    assert registry.get("ca/universal_child_care_benefit") is UNIVERSAL_CHILD_CARE_BENEFIT
    assert registry.get("ca/ei_and_other_benefits") is EI_AND_OTHER_BENEFITS
    assert (
        registry.get("ca/t3_taxable_dividends_other_than_eligible")
        is T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert (
        registry.get("ca/t4ps_taxable_dividends_other_than_eligible")
        is T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert (
        registry.get("ca/t5_taxable_dividends_other_than_eligible")
        is T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert (
        registry.get("ca/t5013_taxable_dividends_other_than_eligible")
        is T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert (
        registry.get("ca/t3_taxable_dividends_other_than_eligible_checked")
        is T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED
    )
    assert (
        registry.get("ca/t4ps_taxable_dividends_other_than_eligible_checked")
        is T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED
    )
    assert (
        registry.get("ca/t5_taxable_dividends_other_than_eligible_checked")
        is T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED
    )
    assert (
        registry.get("ca/t5013_taxable_dividends_other_than_eligible_checked")
        is T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED
    )
    assert registry.get("ca/t3_taxable_dividends") is T3_TAXABLE_DIVIDENDS
    assert registry.get("ca/t4ps_taxable_dividends") is T4PS_TAXABLE_DIVIDENDS
    assert registry.get("ca/t5_taxable_dividends") is T5_TAXABLE_DIVIDENDS
    assert registry.get("ca/t5013_taxable_dividends") is T5013_TAXABLE_DIVIDENDS
    assert (
        registry.get("ca/eligible_dividends_received_without_a_slip")
        is ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP
    )
    assert (
        registry.get("ca/other_dividends_received_without_a_slip")
        is OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP
    )
    assert registry.get("ca/t3_dividend_tax_credit") is T3_DIVIDEND_TAX_CREDIT
    assert registry.get("ca/t4ps_dividend_tax_credit") is T4PS_DIVIDEND_TAX_CREDIT
    assert registry.get("ca/t5_dividend_tax_credit") is T5_DIVIDEND_TAX_CREDIT
    assert registry.get("ca/t5013_dividend_tax_credit") is T5013_DIVIDEND_TAX_CREDIT
    assert (
        registry.get("ca/slip_taxable_dividends_other_than_eligible")
        is SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert registry.get("ca/slip_taxable_dividends") is SLIP_TAXABLE_DIVIDENDS
    assert registry.get("ca/eligible_dividends_grossed_up") is ELIGIBLE_DIVIDENDS_GROSSED_UP
    assert registry.get("ca/other_dividends_grossed_up") is OTHER_DIVIDENDS_GROSSED_UP
    assert (
        registry.get("ca/dividends_without_a_slip_grossed_up")
        is DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP
    )
    assert (
        registry.get("ca/taxable_dividends_other_than_eligible")
        is TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE
    )
    assert registry.get("ca/taxable_dividends") is TAXABLE_DIVIDENDS
    assert registry.get("ca/slip_dividend_tax_credit") is SLIP_DIVIDEND_TAX_CREDIT
    assert registry.get("ca/dividends_amount_a") is DIVIDENDS_AMOUNT_A
    assert registry.get("ca/dividends_amount_b") is DIVIDENDS_AMOUNT_B
    assert registry.get("ca/other_dividends_credit") is OTHER_DIVIDENDS_CREDIT
    assert registry.get("ca/dividends_amount_a_less_b") is DIVIDENDS_AMOUNT_A_LESS_B
    assert registry.get("ca/eligible_dividends_credit") is ELIGIBLE_DIVIDENDS_CREDIT
    assert registry.get("ca/no_slip_dividend_tax_credit") is NO_SLIP_DIVIDEND_TAX_CREDIT
    assert registry.get("ca/dividend_tax_credit") is DIVIDEND_TAX_CREDIT
    assert registry.get("ca/credits_against_basic_federal_tax") is CREDITS_AGAINST_BASIC_FEDERAL_TAX
    assert registry.get("ca/t3_investment_income") is T3_INVESTMENT_INCOME
    assert registry.get("ca/t5_investment_income") is T5_INVESTMENT_INCOME
    assert registry.get("ca/t5013_investment_income") is T5013_INVESTMENT_INCOME
    assert (
        registry.get("ca/investment_income_credited_not_received")
        is INVESTMENT_INCOME_CREDITED_NOT_RECEIVED
    )
    assert registry.get("ca/tax_refund_interest") is TAX_REFUND_INTEREST
    assert registry.get("ca/foreign_investment_income") is FOREIGN_INVESTMENT_INCOME
    assert registry.get("ca/investment_income_without_a_slip") is INVESTMENT_INCOME_WITHOUT_A_SLIP
    assert registry.get("ca/investment_royalties") is INVESTMENT_ROYALTIES
    assert (
        registry.get("ca/investment_income_before_prior_years")
        is INVESTMENT_INCOME_BEFORE_PRIOR_YEARS
    )
    assert (
        registry.get("ca/investment_income_reported_in_previous_years")
        is INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS
    )
    assert (
        registry.get("ca/investment_income_reported_in_previous_years_applied")
        is INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED
    )
    assert (
        registry.get("ca/interest_and_other_investment_income")
        is INTEREST_AND_OTHER_INVESTMENT_INCOME
    )
    assert registry.get("ca/net_partnership_income") is NET_PARTNERSHIP_INCOME
    assert registry.get("ca/rdsp_income") is RDSP_INCOME
    assert registry.get("ca/taxable_support_payments") is TAXABLE_SUPPORT_PAYMENTS
    assert registry.get("ca/rrsp_income") is RRSP_INCOME
    assert registry.get("ca/fhsa_income") is FHSA_INCOME
    assert registry.get("ca/other_fhsa_income") is OTHER_FHSA_INCOME
    assert registry.get("ca/other_income") is OTHER_INCOME
    assert registry.get("ca/taxable_scholarships") is TAXABLE_SCHOLARSHIPS
    assert registry.get("ca/business_income") is BUSINESS_INCOME
    assert registry.get("ca/business_epop_associated") is BUSINESS_EPOP_ASSOCIATED
    assert registry.get("ca/business_epop_agreement_filed") is BUSINESS_EPOP_AGREEMENT_FILED
    assert registry.get("ca/business_epop_percentage") is BUSINESS_EPOP_PERCENTAGE
    assert registry.get("ca/business_epop_percentage_total") is BUSINESS_EPOP_PERCENTAGE_TOTAL
    assert (
        registry.get("ca/business_minister_allocation_given") is BUSINESS_MINISTER_ALLOCATION_GIVEN
    )
    assert registry.get("ca/business_minister_allocation") is BUSINESS_MINISTER_ALLOCATION
    assert registry.get("ca/business_immediate_expensing_cap") is BUSINESS_IMMEDIATE_EXPENSING_CAP
    assert registry.get("ca/business_epop_percentage_maximum") is BUSINESS_EPOP_PERCENTAGE_MAXIMUM
    assert (
        registry.get("ca/business_immediate_expensing_share") is BUSINESS_IMMEDIATE_EXPENSING_SHARE
    )
    assert registry.get("ca/business_epop_percentage_room") is BUSINESS_EPOP_PERCENTAGE_ROOM
    assert (
        registry.get("ca/business_immediate_expensing_allocated")
        is BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED
    )
    assert (
        registry.get("ca/business_immediate_expensing_associated_limit")
        is BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT
    )
    assert (
        registry.get("ca/business_immediate_expensing_limit_before_minister")
        is BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER
    )
    assert (
        registry.get("ca/business_immediate_expensing_limit_before_proration")
        is BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION
    )
    assert (
        registry.get("ca/business_immediate_expensing_limit") is BUSINESS_IMMEDIATE_EXPENSING_LIMIT
    )
    assert (
        registry.get("ca/business_immediate_expensing_limit_unprorated")
        is BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED
    )
    assert (
        registry.get("ca/business_immediate_expensing_claim") is BUSINESS_IMMEDIATE_EXPENSING_CLAIM
    )
    assert registry.get("ca/business_income_before_cca") is BUSINESS_INCOME_BEFORE_CCA
    assert registry.get("ca/business_fiscal_period_from") is BUSINESS_FISCAL_PERIOD_FROM
    assert registry.get("ca/business_fiscal_period_to") is BUSINESS_FISCAL_PERIOD_TO
    assert registry.get("ca/business_fiscal_period_days") is BUSINESS_FISCAL_PERIOD_DAYS
    assert registry.get("ca/business_land_additions") is BUSINESS_LAND_ADDITIONS
    assert registry.get("ca/business_land_dispositions") is BUSINESS_LAND_DISPOSITIONS
    assert registry.get("ca/business_liabilities") is BUSINESS_LIABILITIES
    assert registry.get("ca/business_drawings") is BUSINESS_DRAWINGS
    assert registry.get("ca/business_capital_contributions") is BUSINESS_CAPITAL_CONTRIBUTIONS
    assert registry.get("ca/farm_fiscal_period_days_entered") is FARM_FISCAL_PERIOD_DAYS_ENTERED
    assert registry.get("ca/farm_fiscal_period_days") is FARM_FISCAL_PERIOD_DAYS
    assert registry.get("ca/farm_land_additions") is FARM_LAND_ADDITIONS
    assert registry.get("ca/farm_land_dispositions") is FARM_LAND_DISPOSITIONS
    assert registry.get("ca/farm_quota_additions") is FARM_QUOTA_ADDITIONS
    assert registry.get("ca/farm_quota_dispositions") is FARM_QUOTA_DISPOSITIONS
    assert registry.get("ca/farm_liabilities") is FARM_LIABILITIES
    assert registry.get("ca/farm_drawings") is FARM_DRAWINGS
    assert registry.get("ca/farm_capital_contributions") is FARM_CAPITAL_CONTRIBUTIONS
    assert registry.get("ca/fish_fiscal_period_days_entered") is FISH_FISCAL_PERIOD_DAYS_ENTERED
    assert registry.get("ca/fish_fiscal_period_days") is FISH_FISCAL_PERIOD_DAYS
    assert registry.get("ca/fish_land_additions") is FISH_LAND_ADDITIONS
    assert registry.get("ca/fish_land_dispositions") is FISH_LAND_DISPOSITIONS
    assert registry.get("ca/fish_liabilities") is FISH_LIABILITIES
    assert registry.get("ca/fish_drawings") is FISH_DRAWINGS
    assert registry.get("ca/fish_capital_contributions") is FISH_CAPITAL_CONTRIBUTIONS
    assert registry.get("ca/professional_income") is PROFESSIONAL_INCOME
    assert registry.get("ca/commission_income") is COMMISSION_INCOME
    assert registry.get("ca/farming_income") is FARMING_INCOME
    assert registry.get("ca/farm_epop_associated") is FARM_EPOP_ASSOCIATED
    assert registry.get("ca/farm_epop_agreement_filed") is FARM_EPOP_AGREEMENT_FILED
    assert registry.get("ca/farm_epop_percentage") is FARM_EPOP_PERCENTAGE
    assert registry.get("ca/farm_epop_percentage_total") is FARM_EPOP_PERCENTAGE_TOTAL
    assert registry.get("ca/farm_minister_allocation_given") is FARM_MINISTER_ALLOCATION_GIVEN
    assert registry.get("ca/farm_minister_allocation") is FARM_MINISTER_ALLOCATION
    assert registry.get("ca/farm_immediate_expensing_cap") is FARM_IMMEDIATE_EXPENSING_CAP
    assert registry.get("ca/farm_epop_percentage_maximum") is FARM_EPOP_PERCENTAGE_MAXIMUM
    assert registry.get("ca/farm_immediate_expensing_share") is FARM_IMMEDIATE_EXPENSING_SHARE
    assert registry.get("ca/farm_epop_percentage_room") is FARM_EPOP_PERCENTAGE_ROOM
    assert (
        registry.get("ca/farm_immediate_expensing_allocated") is FARM_IMMEDIATE_EXPENSING_ALLOCATED
    )
    assert (
        registry.get("ca/farm_immediate_expensing_associated_limit")
        is FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT
    )
    assert (
        registry.get("ca/farm_immediate_expensing_limit_before_minister")
        is FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER
    )
    assert (
        registry.get("ca/farm_immediate_expensing_limit_before_proration")
        is FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION
    )
    assert registry.get("ca/farm_immediate_expensing_limit") is FARM_IMMEDIATE_EXPENSING_LIMIT
    assert (
        registry.get("ca/farm_immediate_expensing_limit_unprorated")
        is FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED
    )
    assert registry.get("ca/farm_immediate_expensing_claim") is FARM_IMMEDIATE_EXPENSING_CLAIM
    assert registry.get("ca/farm_income_before_cca") is FARM_INCOME_BEFORE_CCA
    assert registry.get("ca/fish_epop_associated") is FISH_EPOP_ASSOCIATED
    assert registry.get("ca/fish_epop_agreement_filed") is FISH_EPOP_AGREEMENT_FILED
    assert registry.get("ca/fish_epop_percentage") is FISH_EPOP_PERCENTAGE
    assert registry.get("ca/fish_epop_percentage_total") is FISH_EPOP_PERCENTAGE_TOTAL
    assert registry.get("ca/fish_minister_allocation_given") is FISH_MINISTER_ALLOCATION_GIVEN
    assert registry.get("ca/fish_minister_allocation") is FISH_MINISTER_ALLOCATION
    assert registry.get("ca/fish_immediate_expensing_cap") is FISH_IMMEDIATE_EXPENSING_CAP
    assert registry.get("ca/fish_epop_percentage_maximum") is FISH_EPOP_PERCENTAGE_MAXIMUM
    assert registry.get("ca/fish_immediate_expensing_share") is FISH_IMMEDIATE_EXPENSING_SHARE
    assert registry.get("ca/fish_epop_percentage_room") is FISH_EPOP_PERCENTAGE_ROOM
    assert (
        registry.get("ca/fish_immediate_expensing_allocated") is FISH_IMMEDIATE_EXPENSING_ALLOCATED
    )
    assert (
        registry.get("ca/fish_immediate_expensing_associated_limit")
        is FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT
    )
    assert (
        registry.get("ca/fish_immediate_expensing_limit_before_minister")
        is FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER
    )
    assert (
        registry.get("ca/fish_immediate_expensing_limit_before_proration")
        is FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION
    )
    assert registry.get("ca/fish_immediate_expensing_limit") is FISH_IMMEDIATE_EXPENSING_LIMIT
    assert (
        registry.get("ca/fish_immediate_expensing_limit_unprorated")
        is FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED
    )
    assert registry.get("ca/fish_immediate_expensing_claim") is FISH_IMMEDIATE_EXPENSING_CLAIM
    assert registry.get("ca/fish_income_before_cca") is FISH_INCOME_BEFORE_CCA
    assert registry.get("ca/fishing_income") is FISHING_INCOME
    assert registry.get("ca/workers_compensation_benefits") is WORKERS_COMPENSATION_BENEFITS
    assert registry.get("ca/social_assistance_payments") is SOCIAL_ASSISTANCE_PAYMENTS
    assert registry.get("ca/net_federal_supplements") is NET_FEDERAL_SUPPLEMENTS
    assert registry.get("ca/income_support_benefits") is INCOME_SUPPORT_BENEFITS
    assert registry.get("ca/net_self_employment_income") is NET_SELF_EMPLOYMENT_INCOME
    assert (
        registry.get("ca/short_term_rental_related_expenses") is SHORT_TERM_RENTAL_RELATED_EXPENSES
    )
    assert (
        registry.get("ca/short_term_rental_non_compliant_days")
        is SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS
    )
    assert registry.get("ca/short_term_rental_days") is SHORT_TERM_RENTAL_DAYS
    assert registry.get("ca/short_term_rental_units") is SHORT_TERM_RENTAL_UNITS
    assert registry.get("ca/short_term_rental_related_cca") is SHORT_TERM_RENTAL_RELATED_CCA
    assert registry.get("ca/short_term_rental_cca_units") is SHORT_TERM_RENTAL_CCA_UNITS
    assert registry.get("ca/non_compliant_cca") is NON_COMPLIANT_CCA
    assert (
        registry.get("ca/short_term_rental_non_compliant_cca_by_class")
        is SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS
    )
    assert registry.get("ca/rental_property_units") is RENTAL_PROPERTY_UNITS
    assert registry.get("ca/rental_property_short_term_rents") is RENTAL_PROPERTY_SHORT_TERM_RENTS
    assert registry.get("ca/rental_property_gross_rents") is RENTAL_PROPERTY_GROSS_RENTS
    assert registry.get("ca/rental_properties") is RENTAL_PROPERTIES
    assert registry.get("ca/short_term_rental_gross_rents") is SHORT_TERM_RENTAL_GROSS_RENTS
    assert registry.get("ca/rental_gross_rents") is RENTAL_GROSS_RENTS
    assert registry.get("ca/rental_other_income") is RENTAL_OTHER_INCOME
    assert registry.get("ca/gross_rental_income") is GROSS_RENTAL_INCOME
    assert registry.get("ca/rental_advertising") is RENTAL_ADVERTISING
    assert (
        registry.get("ca/rental_advertising_personal_portion")
        is RENTAL_ADVERTISING_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_advertising_short_term_portion")
        is RENTAL_ADVERTISING_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_insurance") is RENTAL_INSURANCE
    assert registry.get("ca/rental_insurance_personal_portion") is RENTAL_INSURANCE_PERSONAL_PORTION
    assert (
        registry.get("ca/rental_insurance_short_term_portion")
        is RENTAL_INSURANCE_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_interest_and_bank_charges") is RENTAL_INTEREST_AND_BANK_CHARGES
    assert (
        registry.get("ca/rental_interest_and_bank_charges_personal_portion")
        is RENTAL_INTEREST_AND_BANK_CHARGES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_interest_and_bank_charges_short_term_portion")
        is RENTAL_INTEREST_AND_BANK_CHARGES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_office_expenses") is RENTAL_OFFICE_EXPENSES
    assert (
        registry.get("ca/rental_office_expenses_personal_portion")
        is RENTAL_OFFICE_EXPENSES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_office_expenses_short_term_portion")
        is RENTAL_OFFICE_EXPENSES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_professional_fees") is RENTAL_PROFESSIONAL_FEES
    assert (
        registry.get("ca/rental_professional_fees_personal_portion")
        is RENTAL_PROFESSIONAL_FEES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_professional_fees_short_term_portion")
        is RENTAL_PROFESSIONAL_FEES_SHORT_TERM_PORTION
    )
    assert (
        registry.get("ca/rental_management_and_administration_fees")
        is RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES
    )
    assert (
        registry.get("ca/rental_management_and_administration_fees_personal_portion")
        is RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_management_and_administration_fees_short_term_portion")
        is RENTAL_MANAGEMENT_AND_ADMINISTRATION_FEES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_repairs_and_maintenance") is RENTAL_REPAIRS_AND_MAINTENANCE
    assert (
        registry.get("ca/rental_repairs_and_maintenance_personal_portion")
        is RENTAL_REPAIRS_AND_MAINTENANCE_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_repairs_and_maintenance_short_term_portion")
        is RENTAL_REPAIRS_AND_MAINTENANCE_SHORT_TERM_PORTION
    )
    assert (
        registry.get("ca/rental_salaries_wages_and_benefits") is RENTAL_SALARIES_WAGES_AND_BENEFITS
    )
    assert (
        registry.get("ca/rental_salaries_wages_and_benefits_personal_portion")
        is RENTAL_SALARIES_WAGES_AND_BENEFITS_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_salaries_wages_and_benefits_short_term_portion")
        is RENTAL_SALARIES_WAGES_AND_BENEFITS_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_property_taxes") is RENTAL_PROPERTY_TAXES
    assert (
        registry.get("ca/rental_property_taxes_personal_portion")
        is RENTAL_PROPERTY_TAXES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_property_taxes_short_term_portion")
        is RENTAL_PROPERTY_TAXES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_travel") is RENTAL_TRAVEL
    assert registry.get("ca/rental_travel_personal_portion") is RENTAL_TRAVEL_PERSONAL_PORTION
    assert registry.get("ca/rental_travel_short_term_portion") is RENTAL_TRAVEL_SHORT_TERM_PORTION
    assert registry.get("ca/rental_utilities") is RENTAL_UTILITIES
    assert registry.get("ca/rental_utilities_personal_portion") is RENTAL_UTILITIES_PERSONAL_PORTION
    assert (
        registry.get("ca/rental_utilities_short_term_portion")
        is RENTAL_UTILITIES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_motor_vehicle_expenses") is RENTAL_MOTOR_VEHICLE_EXPENSES
    assert (
        registry.get("ca/rental_motor_vehicle_expenses_personal_portion")
        is RENTAL_MOTOR_VEHICLE_EXPENSES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_motor_vehicle_expenses_short_term_portion")
        is RENTAL_MOTOR_VEHICLE_EXPENSES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_other_expenses") is RENTAL_OTHER_EXPENSES
    assert (
        registry.get("ca/rental_other_expenses_personal_portion")
        is RENTAL_OTHER_EXPENSES_PERSONAL_PORTION
    )
    assert (
        registry.get("ca/rental_other_expenses_short_term_portion")
        is RENTAL_OTHER_EXPENSES_SHORT_TERM_PORTION
    )
    assert registry.get("ca/rental_total_expenses") is RENTAL_TOTAL_EXPENSES
    assert registry.get("ca/rental_personal_portion") is RENTAL_PERSONAL_PORTION
    assert registry.get("ca/rental_short_term_portion") is RENTAL_SHORT_TERM_PORTION
    assert registry.get("ca/rental_non_compliant_expenses") is RENTAL_NON_COMPLIANT_EXPENSES
    assert registry.get("ca/rental_non_compliant_cca") is RENTAL_NON_COMPLIANT_CCA
    assert (
        registry.get("ca/rental_expenses_less_personal_portion")
        is RENTAL_EXPENSES_LESS_PERSONAL_PORTION
    )
    assert registry.get("ca/rental_deductible_expenses") is RENTAL_DEDUCTIBLE_EXPENSES
    assert (
        registry.get("ca/rental_net_income_before_adjustments")
        is RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS
    )
    assert registry.get("ca/rental_coowner") is RENTAL_COOWNER
    assert registry.get("ca/rental_coowner_share") is RENTAL_COOWNER_SHARE
    assert registry.get("ca/rental_net_income_share") is RENTAL_NET_INCOME_SHARE
    assert registry.get("ca/rental_coowner_other_expenses") is RENTAL_COOWNER_OTHER_EXPENSES
    assert (
        registry.get("ca/rental_net_income_after_coowner_expenses")
        is RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES
    )
    assert registry.get("ca/rental_recaptured_cca") is RENTAL_RECAPTURED_CCA
    assert registry.get("ca/rental_net_income_with_recapture") is RENTAL_NET_INCOME_WITH_RECAPTURE
    assert registry.get("ca/rental_terminal_loss") is RENTAL_TERMINAL_LOSS
    assert (
        registry.get("ca/rental_net_income_after_terminal_loss")
        is RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS
    )
    assert registry.get("ca/rental_cca_claim") is RENTAL_CCA_CLAIM
    assert registry.get("ca/rental_cca_classes") is RENTAL_CCA_CLASSES
    assert registry.get("ca/cca_sold_zepvs") is CCA_SOLD_ZEPVS
    assert registry.get("ca/rental_vehicle_sales_tax_rate") is RENTAL_VEHICLE_SALES_TAX_RATE
    assert registry.get("ca/rental_cca_table_recapture") is RENTAL_CCA_TABLE_RECAPTURE
    assert registry.get("ca/rental_cca_table_terminal_loss") is RENTAL_CCA_TABLE_TERMINAL_LOSS
    assert registry.get("ca/rental_cca_table_claim") is RENTAL_CCA_TABLE_CLAIM
    assert registry.get("ca/rental_cca_opening_ucc_total") is RENTAL_CCA_OPENING_UCC_TOTAL
    assert registry.get("ca/rental_cca_additions_total") is RENTAL_CCA_ADDITIONS_TOTAL
    assert (
        registry.get("ca/rental_cca_personal_part_remaining_total")
        is RENTAL_CCA_PERSONAL_PART_REMAINING_TOTAL
    )
    assert registry.get("ca/rental_coowner_recaptured_cca") is RENTAL_COOWNER_RECAPTURED_CCA
    assert registry.get("ca/rental_coowner_terminal_loss") is RENTAL_COOWNER_TERMINAL_LOSS
    assert registry.get("ca/rental_coowner_cca_claim") is RENTAL_COOWNER_CCA_CLAIM
    assert registry.get("ca/rental_cca_claim_share") is RENTAL_CCA_CLAIM_SHARE
    assert registry.get("ca/rental_cca_personal_part") is RENTAL_CCA_PERSONAL_PART
    assert registry.get("ca/rental_cca_business_use_of_home") is RENTAL_CCA_BUSINESS_USE_OF_HOME
    assert (
        registry.get("ca/rental_cca_claim_less_personal_part")
        is RENTAL_CCA_CLAIM_LESS_PERSONAL_PART
    )
    assert registry.get("ca/rental_cca_limit") is RENTAL_CCA_LIMIT
    assert registry.get("ca/rental_closing_ucc") is RENTAL_CLOSING_UCC
    assert registry.get("ca/rental_net_income_after_cca") is RENTAL_NET_INCOME_AFTER_CCA
    assert registry.get("ca/rental_epop_associated") is RENTAL_EPOP_ASSOCIATED
    assert registry.get("ca/rental_epop_agreement_filed") is RENTAL_EPOP_AGREEMENT_FILED
    assert registry.get("ca/rental_epop_percentage") is RENTAL_EPOP_PERCENTAGE
    assert registry.get("ca/rental_epop_percentage_total") is RENTAL_EPOP_PERCENTAGE_TOTAL
    assert registry.get("ca/rental_minister_allocation_given") is RENTAL_MINISTER_ALLOCATION_GIVEN
    assert registry.get("ca/rental_minister_allocation") is RENTAL_MINISTER_ALLOCATION
    assert registry.get("ca/rental_immediate_expensing_cap") is RENTAL_IMMEDIATE_EXPENSING_CAP
    assert registry.get("ca/rental_epop_percentage_maximum") is RENTAL_EPOP_PERCENTAGE_MAXIMUM
    assert registry.get("ca/rental_immediate_expensing_share") is RENTAL_IMMEDIATE_EXPENSING_SHARE
    assert registry.get("ca/rental_epop_percentage_room") is RENTAL_EPOP_PERCENTAGE_ROOM
    assert (
        registry.get("ca/rental_immediate_expensing_allocated")
        is RENTAL_IMMEDIATE_EXPENSING_ALLOCATED
    )
    assert (
        registry.get("ca/rental_immediate_expensing_associated_limit")
        is RENTAL_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT
    )
    assert (
        registry.get("ca/rental_immediate_expensing_limit_before_minister")
        is RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER
    )
    assert (
        registry.get("ca/rental_immediate_expensing_limit_before_proration")
        is RENTAL_IMMEDIATE_EXPENSING_LIMIT_BEFORE_PRORATION
    )
    assert registry.get("ca/rental_immediate_expensing_limit") is RENTAL_IMMEDIATE_EXPENSING_LIMIT
    assert (
        registry.get("ca/rental_immediate_expensing_limit_unprorated")
        is RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED
    )
    assert registry.get("ca/rental_immediate_expensing_claim") is RENTAL_IMMEDIATE_EXPENSING_CLAIM
    assert registry.get("ca/rental_fiscal_period_days_entered") is RENTAL_FISCAL_PERIOD_DAYS_ENTERED
    assert registry.get("ca/rental_fiscal_period_days") is RENTAL_FISCAL_PERIOD_DAYS
    assert registry.get("ca/rental_addition_total_cost") is RENTAL_ADDITION_TOTAL_COST
    assert registry.get("ca/rental_addition_personal_portion") is RENTAL_ADDITION_PERSONAL_PORTION
    assert registry.get("ca/rental_equipment_additions") is RENTAL_EQUIPMENT_ADDITIONS
    assert registry.get("ca/rental_building_additions") is RENTAL_BUILDING_ADDITIONS
    assert registry.get("ca/rental_equipment_additions_total") is RENTAL_EQUIPMENT_ADDITIONS_TOTAL
    assert registry.get("ca/rental_building_additions_total") is RENTAL_BUILDING_ADDITIONS_TOTAL
    assert registry.get("ca/rental_land_additions") is RENTAL_LAND_ADDITIONS
    assert registry.get("ca/rental_land_dispositions") is RENTAL_LAND_DISPOSITIONS
    assert registry.get("ca/rental_partner") is RENTAL_PARTNER
    assert registry.get("ca/rental_partner_share") is RENTAL_PARTNER_SHARE
    assert registry.get("ca/rental_partner_gst_hst_rebate") is RENTAL_PARTNER_GST_HST_REBATE
    assert registry.get("ca/rental_partner_other_expenses") is RENTAL_PARTNER_OTHER_EXPENSES
    assert registry.get("ca/rental_partner_share_with_rebate") is RENTAL_PARTNER_SHARE_WITH_REBATE
    assert registry.get("ca/rental_partnership_net_income") is RENTAL_PARTNERSHIP_NET_INCOME
    assert registry.get("ca/net_rental_income") is NET_RENTAL_INCOME
    assert registry.get("ca/t776_statements") is T776_STATEMENTS
    assert registry.get("ca/t2125_statements") is T2125_STATEMENTS
    assert registry.get("ca/t2042_statements") is T2042_STATEMENTS
    assert registry.get("ca/t2121_statements") is T2121_STATEMENTS


def test_the_previous_years_applied_kind_is_the_checked_non_negative_money_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet 2025 line 10 "Interest and other investment income, included on line 9,
    # received and reported in previous years": it cannot exceed line 9, so the amount is checked
    # against line 9 (`core/at_most`) and the checked amount is what line 11 subtracts. The checked
    # kind is new, beside the input; the input is what the caller gives.
    kind = registry.kind("ca/investment_income_reported_in_previous_years_applied")
    assert kind is INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED
    assert kind.identifier == "ca/investment_income_reported_in_previous_years_applied"
    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert kind is not INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS
    assert registry.kind("ca/investment_income_reported_in_previous_years").value_type is Decimal


def test_the_income_kinds_are_money() -> None:
    for kind in (
        EMPLOYMENT_INCOME,
        CAPITAL_GAIN,
        TAXABLE_CAPITAL_GAINS,
        TOTAL_INCOME,
        OTHER_EMPLOYMENT_INCOME,
        OLD_AGE_SECURITY,
        CPP_OR_QPP_BENEFITS,
        OTHER_PENSIONS_AND_SUPERANNUATION,
        ELECTED_SPLIT_PENSION_AMOUNT,
        UNIVERSAL_CHILD_CARE_BENEFIT,
        EI_AND_OTHER_BENEFITS,
        T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        T3_TAXABLE_DIVIDENDS,
        T4PS_TAXABLE_DIVIDENDS,
        T5_TAXABLE_DIVIDENDS,
        T5013_TAXABLE_DIVIDENDS,
        ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
        OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
        T3_DIVIDEND_TAX_CREDIT,
        T4PS_DIVIDEND_TAX_CREDIT,
        T5_DIVIDEND_TAX_CREDIT,
        T5013_DIVIDEND_TAX_CREDIT,
        SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        SLIP_TAXABLE_DIVIDENDS,
        ELIGIBLE_DIVIDENDS_GROSSED_UP,
        OTHER_DIVIDENDS_GROSSED_UP,
        DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP,
        TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        TAXABLE_DIVIDENDS,
        SLIP_DIVIDEND_TAX_CREDIT,
        DIVIDENDS_AMOUNT_A,
        DIVIDENDS_AMOUNT_B,
        OTHER_DIVIDENDS_CREDIT,
        DIVIDENDS_AMOUNT_A_LESS_B,
        ELIGIBLE_DIVIDENDS_CREDIT,
        NO_SLIP_DIVIDEND_TAX_CREDIT,
        DIVIDEND_TAX_CREDIT,
        CREDITS_AGAINST_BASIC_FEDERAL_TAX,
        T3_INVESTMENT_INCOME,
        T5_INVESTMENT_INCOME,
        T5013_INVESTMENT_INCOME,
        INVESTMENT_INCOME_CREDITED_NOT_RECEIVED,
        TAX_REFUND_INTEREST,
        FOREIGN_INVESTMENT_INCOME,
        INVESTMENT_INCOME_WITHOUT_A_SLIP,
        INVESTMENT_ROYALTIES,
        INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
        INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS,
        INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED,
        INTEREST_AND_OTHER_INVESTMENT_INCOME,
        NET_PARTNERSHIP_INCOME,
        RDSP_INCOME,
        TAXABLE_SUPPORT_PAYMENTS,
        RRSP_INCOME,
        FHSA_INCOME,
        OTHER_FHSA_INCOME,
        OTHER_INCOME,
        TAXABLE_SCHOLARSHIPS,
        BUSINESS_INCOME,
        PROFESSIONAL_INCOME,
        COMMISSION_INCOME,
        FARMING_INCOME,
        FISHING_INCOME,
        NET_SELF_EMPLOYMENT_INCOME,
        WORKERS_COMPENSATION_BENEFITS,
        SOCIAL_ASSISTANCE_PAYMENTS,
        NET_FEDERAL_SUPPLEMENTS,
        INCOME_SUPPORT_BENEFITS,
        SHORT_TERM_RENTAL_RELATED_CCA,
        NON_COMPLIANT_CCA,
        RENTAL_NON_COMPLIANT_CCA,
    ):
        assert kind.value_type is Decimal, kind.identifier


# --- Schedule 3 (form 5000-S3) Parts 3 and 4 --------------------------------------------------

DISPOSITION_LISTS: list[tuple[str, RecordListKind]] = [
    ("ca/qsbcs_dispositions", QSBCS_DISPOSITIONS),
    ("ca/qffp_dispositions", QFFP_DISPOSITIONS),
    ("ca/qffp_foreclosure_dispositions", QFFP_FORECLOSURE_DISPOSITIONS),
    ("ca/share_dispositions", SHARE_DISPOSITIONS),
    ("ca/real_estate_dispositions", REAL_ESTATE_DISPOSITIONS),
    ("ca/bond_dispositions", BOND_DISPOSITIONS),
    ("ca/crypto_asset_dispositions", CRYPTO_ASSET_DISPOSITIONS),
    ("ca/other_foreclosure_dispositions", OTHER_FORECLOSURE_DISPOSITIONS),
    ("ca/personal_use_property_dispositions", PERSONAL_USE_PROPERTY_DISPOSITIONS),
    ("ca/listed_personal_property_dispositions", LISTED_PERSONAL_PROPERTY_DISPOSITIONS),
]

SIGNED_LINES: list[tuple[str, ArtifactKind[Any]]] = [
    ("ca/qsbcs_gain_or_loss", QSBCS_GAIN_OR_LOSS),
    ("ca/qffp_gain_or_loss", QFFP_GAIN_OR_LOSS),
    ("ca/qffp_foreclosure_gain_or_loss", QFFP_FORECLOSURE_GAIN_OR_LOSS),
    ("ca/share_gain_or_loss", SHARE_GAIN_OR_LOSS),
    ("ca/real_estate_gain_or_loss", REAL_ESTATE_GAIN_OR_LOSS),
    ("ca/bond_gain_or_loss", BOND_GAIN_OR_LOSS),
    ("ca/crypto_asset_gain_or_loss", CRYPTO_ASSET_GAIN_OR_LOSS),
    ("ca/other_foreclosure_gain_or_loss", OTHER_FORECLOSURE_GAIN_OR_LOSS),
    ("ca/listed_personal_property_gain_or_loss", LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS),
    (
        "ca/capital_gains_of_qualified_and_other_properties",
        CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    ),
    ("ca/capital_gains_after_deferral", CAPITAL_GAINS_AFTER_DEFERRAL),
    ("ca/slip_capital_gains_or_losses", SLIP_CAPITAL_GAINS_OR_LOSSES),
    ("ca/t3_capital_gains_or_losses", T3_CAPITAL_GAINS_OR_LOSSES),
    (
        "ca/capital_gains_before_investment_loss_reduction",
        CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION,
    ),
    ("ca/capital_gains_before_reserves", CAPITAL_GAINS_BEFORE_RESERVES),
    ("ca/schedule_3_line_19200", SCHEDULE_3_LINE_19200),
    ("ca/capital_gain", CAPITAL_GAIN),
    ("ca/included_capital_gain", INCLUDED_CAPITAL_GAIN),
]

NON_NEGATIVE_LINES: list[tuple[str, ArtifactKind[Any]]] = [
    ("ca/personal_use_property_gain_rows", PERSONAL_USE_PROPERTY_GAIN_ROWS),
    ("ca/personal_use_property_gain", PERSONAL_USE_PROPERTY_GAIN),
    ("ca/unapplied_listed_personal_property_losses", UNAPPLIED_LISTED_PERSONAL_PROPERTY_LOSSES),
    ("ca/listed_personal_property_net_gain", LISTED_PERSONAL_PROPERTY_NET_GAIN),
    ("ca/capital_gains_deferral", CAPITAL_GAINS_DEFERRAL),
    ("ca/partnership_gains_at_full_inclusion", PARTNERSHIP_GAINS_AT_FULL_INCLUSION),
    ("ca/disposition_proceeds", DISPOSITION_PROCEEDS),
    ("ca/disposition_adjusted_cost_base", DISPOSITION_ADJUSTED_COST_BASE),
    ("ca/disposition_outlays", DISPOSITION_OUTLAYS),
    ("ca/qsbcs_proceeds", QSBCS_PROCEEDS),
    ("ca/qffp_proceeds", QFFP_PROCEEDS),
    ("ca/qffp_foreclosure_proceeds", QFFP_FORECLOSURE_PROCEEDS),
    ("ca/share_proceeds", SHARE_PROCEEDS),
    ("ca/real_estate_proceeds", REAL_ESTATE_PROCEEDS),
    ("ca/real_estate_restricted_farm_loss_applied", REAL_ESTATE_RESTRICTED_FARM_LOSS_APPLIED),
    ("ca/qffp_restricted_farm_loss_applied", QFFP_RESTRICTED_FARM_LOSS_APPLIED),
    (
        "ca/qffp_foreclosure_restricted_farm_loss_applied",
        QFFP_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    ),
    (
        "ca/other_foreclosure_restricted_farm_loss_applied",
        OTHER_FORECLOSURE_RESTRICTED_FARM_LOSS_APPLIED,
    ),
    ("ca/bond_proceeds", BOND_PROCEEDS),
    ("ca/crypto_asset_proceeds", CRYPTO_ASSET_PROCEEDS),
    ("ca/other_foreclosure_proceeds", OTHER_FORECLOSURE_PROCEEDS),
]


def test_the_schedule_3_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for identifier, kind in [*DISPOSITION_LISTS, *SIGNED_LINES, *NON_NEGATIVE_LINES]:
        assert registry.get(identifier) is kind, identifier
        assert kind.identifier == identifier
        assert identifier in REGISTERED


def test_the_ten_property_lists_are_record_lists_of_columns_2_to_4() -> None:
    # Schedule 3 Part 3: "(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost base",
    # "(Column 4): Outlays and expenses"; column 1 (year acquired) feeds no line, column 5 is
    # worked out. One kind of each field, shared by all ten lists, in the form's column order.
    # The real estate list also holds the filer's 0 or 1 "depreciable property" answer, as its
    # fourth field: Guide T4037 p.19 "A loss from the sale of depreciable property is not
    # considered to be a capital loss." (confirmed 2026-10-25 from the PDF; no .txt published).
    for identifier, kind in DISPOSITION_LISTS:
        assert isinstance(kind, RecordListKind), identifier
        columns: tuple[ArtifactKind[Any], ...] = (
            DISPOSITION_PROCEEDS,
            DISPOSITION_ADJUSTED_COST_BASE,
            DISPOSITION_OUTLAYS,
        )
        if kind is REAL_ESTATE_DISPOSITIONS:
            columns = (
                *columns,
                DISPOSITION_DEPRECIABLE_PROPERTY,
                DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
                DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
                DISPOSITION_FARM_LOSS_INTEREST,
            )
        if kind in (
            QFFP_DISPOSITIONS,
            QFFP_FORECLOSURE_DISPOSITIONS,
            OTHER_FORECLOSURE_DISPOSITIONS,
        ):
            columns = (
                *columns,
                DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
                DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
                DISPOSITION_FARM_LOSS_INTEREST,
            )
        assert kind.value_type is RecordList
        assert kind.fields == columns, identifier
        assert identifier in RECORD_LISTS


def test_the_depreciable_property_answer_is_a_non_negative_int_count_of_the_real_estate_list(
    registry: ArtifactRegistry,
) -> None:
    assert DISPOSITION_DEPRECIABLE_PROPERTY.identifier == "ca/disposition_depreciable_property"
    assert DISPOSITION_DEPRECIABLE_PROPERTY.value_type is int
    assert DISPOSITION_DEPRECIABLE_PROPERTY.non_negative is True
    assert registry.kind("ca/disposition_depreciable_property") is DISPOSITION_DEPRECIABLE_PROPERTY
    assert REAL_ESTATE_DISPOSITIONS.fields[3] is DISPOSITION_DEPRECIABLE_PROPERTY
    for identifier, kind in DISPOSITION_LISTS:
        if kind is not REAL_ESTATE_DISPOSITIONS:
            assert DISPOSITION_DEPRECIABLE_PROPERTY not in kind.fields, identifier


def test_the_farm_loss_fields_are_non_negative_decimals_of_the_farm_and_real_estate_lists(
    registry: ArtifactRegistry,
) -> None:
    # The qualified farm or fishing property lists and the other foreclosures list hold them as
    # their fourth to sixth fields (Guide T4037 p.34 farmland), the real estate list as its fifth
    # to seventh.
    for kind, identifier, position in (
        (
            DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
            "ca/disposition_farm_loss_taxes_and_interest",
            4,
        ),
        (DISPOSITION_FARM_LOSS_PROPERTY_TAXES, "ca/disposition_farm_loss_property_taxes", 5),
        (DISPOSITION_FARM_LOSS_INTEREST, "ca/disposition_farm_loss_interest", 6),
    ):
        assert kind.identifier == identifier
        assert kind.value_type is Decimal
        assert kind.non_negative is True
        assert registry.kind(identifier) is kind
        assert REAL_ESTATE_DISPOSITIONS.fields[position] is kind
        assert QFFP_DISPOSITIONS.fields[position - 1] is kind
        assert QFFP_FORECLOSURE_DISPOSITIONS.fields[position - 1] is kind
        assert OTHER_FORECLOSURE_DISPOSITIONS.fields[position - 1] is kind
        for list_identifier, other in DISPOSITION_LISTS:
            if other not in (
                REAL_ESTATE_DISPOSITIONS,
                QFFP_DISPOSITIONS,
                QFFP_FORECLOSURE_DISPOSITIONS,
                OTHER_FORECLOSURE_DISPOSITIONS,
            ):
                assert kind not in other.fields, list_identifier


def test_the_disposition_fields_are_non_negative_decimals() -> None:
    for kind in (DISPOSITION_PROCEEDS, DISPOSITION_ADJUSTED_COST_BASE, DISPOSITION_OUTLAYS):
        assert kind.value_type is Decimal
        assert kind.non_negative is True


def test_the_part_3_and_part_4_lines_that_print_losses_in_brackets_are_signed_decimals() -> None:
    # "Report all negative amounts (losses) using brackets."
    for identifier, kind in SIGNED_LINES:
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is False, identifier
        assert identifier in SIGNED


def test_the_gain_only_lines_the_deferral_and_the_unapplied_losses_are_non_negative() -> None:
    # Line 9 and line 10 are "gain only"; line 13 and the unapplied listed personal property
    # losses are amounts the filer states.
    for identifier, kind in NON_NEGATIVE_LINES:
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is True, identifier
        assert identifier not in SIGNED


def test_the_share_gain_not_below_zero_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 3 line 4 and line 13200 "Total gain or loss (add all the amounts under column 5)"
    # is the share gain or loss, which may be a loss; the deferral "included on line 4" is at most
    # it, floored at 0 (a loss leaves no share gain to defer), so the floored total is what the
    # deferral is checked against. It is a plain non-negative decimal, not a signed line.
    assert registry.get("ca/share_gain_not_below_zero") is SHARE_GAIN_NOT_BELOW_ZERO
    assert SHARE_GAIN_NOT_BELOW_ZERO.value_type is Decimal
    assert SHARE_GAIN_NOT_BELOW_ZERO.non_negative is True
    assert "ca/share_gain_not_below_zero" not in SIGNED


def test_the_checked_capital_gains_deferral_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 3 line 13 and line 16100 "Capital gains deferral from qualifying dispositions of
    # eligible small business corporation shares included on line 4" is checked to be at most
    # line 4 (`core/at_most`); the subtraction of line 14 reads the checked amount.
    assert registry.get("ca/capital_gains_deferral_checked") is CAPITAL_GAINS_DEFERRAL_CHECKED
    assert CAPITAL_GAINS_DEFERRAL_CHECKED.value_type is Decimal
    assert CAPITAL_GAINS_DEFERRAL_CHECKED.non_negative is True
    assert "ca/capital_gains_deferral_checked" not in SIGNED


def test_the_taxable_capital_gains_stay_non_negative() -> None:
    # T1 line 12700 takes line 26 only "If positive".
    assert TAXABLE_CAPITAL_GAINS.non_negative is True
    assert "ca/taxable_capital_gains" not in SIGNED


def test_every_disposition_list_is_a_kind_of_its_own() -> None:
    assert len({id(kind) for _, kind in DISPOSITION_LISTS}) == 10


def test_the_t2125_chart_kinds_are_registered_under_their_names(registry: ArtifactRegistry) -> None:
    # Form T2125 Charts A to C: the vehicles list, the caller's sales tax rate and the printed
    # constants (each a dataset of the same name, which T2042 and T2121 still produce as kinds); the
    # lines the charts compute are in the trace of `ca/business_vehicle_expenses`, not artifacts.
    assert registry.get("ca/business_vehicle_days_divisor") is BUSINESS_VEHICLE_DAYS_DIVISOR
    assert registry.get("ca/business_vehicle_list_price") is BUSINESS_VEHICLE_LIST_PRICE
    assert registry.get("ca/business_vehicle_sales_tax_rate") is BUSINESS_VEHICLE_SALES_TAX_RATE
    assert registry.get("ca/business_vehicles") is BUSINESS_VEHICLES
    assert BUSINESS_VEHICLE_DAYS_DIVISOR.non_negative is True
    for kind in (
        BUSINESS_VEHICLE_DAYS_DIVISOR,
        BUSINESS_VEHICLE_LIST_PRICE,
        BUSINESS_VEHICLE_SALES_TAX_RATE,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_t2125_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines 12, 13, 19, 26, 28 and the rest are worked inside the capability.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/business_vehicle_{name}" not in registry.identifiers(), name


def test_the_t2042_chart_kinds_are_registered_under_their_names(registry: ArtifactRegistry) -> None:
    # Form T2042 Charts A to C: each vehicle is a record of the shared `ca/business_vehicles`, the
    # sales tax rate of the province is the statement's input, and the line 9819 kind is
    # the capability's output over the vehicles.
    assert BUSINESS_VEHICLES in T2042_STATEMENTS.fields
    assert registry.get("ca/business_vehicles") is BUSINESS_VEHICLES
    assert registry.get("ca/farm_vehicle_sales_tax_rate") is FARM_VEHICLE_SALES_TAX_RATE
    assert registry.get("ca/farm_motor_vehicle_expenses") is FARM_MOTOR_VEHICLE_EXPENSES
    assert registry.get("ca/business_vehicle_days_divisor") is BUSINESS_VEHICLE_DAYS_DIVISOR


def test_the_t2042_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines of Charts A to C are worked inside the capability, as on T2125.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/farm_vehicle_{name}" not in registry.identifiers(), name


def test_the_t2121_chart_kinds_are_registered_under_their_names(registry: ArtifactRegistry) -> None:
    # Form T2121 Charts A to C: each vehicle is a record of the shared `ca/business_vehicles`, the
    # sales tax rate of the province is the statement's input, and the line 9281 kind is
    # the capability's output over the vehicles.
    assert BUSINESS_VEHICLES in T2121_STATEMENTS.fields
    assert registry.get("ca/business_vehicles") is BUSINESS_VEHICLES
    assert registry.get("ca/fish_vehicle_sales_tax_rate") is FISH_VEHICLE_SALES_TAX_RATE
    assert registry.get("ca/fish_motor_vehicle_expenses") is FISH_MOTOR_VEHICLE_EXPENSES
    assert registry.get("ca/business_vehicle_days_divisor") is BUSINESS_VEHICLE_DAYS_DIVISOR


def test_the_t2121_chart_lines_are_no_longer_artifacts(registry: ArtifactRegistry) -> None:
    # Each vehicle's lines of Charts A to C are worked inside the capability, as on T2125.
    for name in (
        "list_price_limit_tax",
        "lease_charge_limit_tax",
        "lease_cost_limit_tax",
        "list_price_limit_with_tax",
        "lease_charge_limit_with_tax",
        "lease_cost_limit_with_tax",
        "total_expenses",
        "business_use_part",
        "interest_for_period",
        "available_interest",
        "lease_price_base",
        "lease_price_85_percent",
        "lease_charge_portion",
        "lease_charges_net",
        "lease_cost_portion",
        "leasing_cost",
    ):
        assert f"ca/fish_vehicle_{name}" not in registry.identifiers(), name


# --- the immediate expensing limit checks: a yes or no answer checked to be 0 or 1, and a
# business's own percentage checked against the total of column 3 (the forms are silent on both).

CHECKED_KINDS = (
    (
        "ca/rental_coowner",
        "ca/rental_coowner_checked",
        RENTAL_COOWNER_CHECKED,
        int,
    ),
    (
        "ca/emergency_services_volunteer_conflict",
        "ca/emergency_services_volunteer_conflict_checked",
        EMERGENCY_SERVICES_VOLUNTEER_CONFLICT_CHECKED,
        int,
    ),
    (
        "ca/rental_coowner_recaptured_cca",
        "ca/rental_coowner_recaptured_cca_checked",
        RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
        Decimal,
    ),
    (
        "ca/rental_coowner_terminal_loss",
        "ca/rental_coowner_terminal_loss_checked",
        RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
        Decimal,
    ),
    (
        "ca/rental_coowner_cca_claim",
        "ca/rental_coowner_cca_claim_checked",
        RENTAL_COOWNER_CCA_CLAIM_CHECKED,
        Decimal,
    ),
    (
        "ca/rental_partner",
        "ca/rental_partner_checked",
        RENTAL_PARTNER_CHECKED,
        int,
    ),
    (
        "ca/rental_epop_associated",
        "ca/rental_epop_associated_checked",
        RENTAL_EPOP_ASSOCIATED_CHECKED,
        int,
    ),
    (
        "ca/rental_epop_agreement_filed",
        "ca/rental_epop_agreement_filed_checked",
        RENTAL_EPOP_AGREEMENT_FILED_CHECKED,
        int,
    ),
    (
        "ca/rental_minister_allocation_given",
        "ca/rental_minister_allocation_given_checked",
        RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
        int,
    ),
    (
        "ca/rental_partner_percentage",
        "ca/rental_partner_percentage_checked",
        RENTAL_PARTNER_PERCENTAGE_CHECKED,
        Decimal,
    ),
    (
        "ca/business_epop_associated",
        "ca/business_epop_associated_checked",
        BUSINESS_EPOP_ASSOCIATED_CHECKED,
        int,
    ),
    (
        "ca/business_epop_agreement_filed",
        "ca/business_epop_agreement_filed_checked",
        BUSINESS_EPOP_AGREEMENT_FILED_CHECKED,
        int,
    ),
    (
        "ca/business_minister_allocation_given",
        "ca/business_minister_allocation_given_checked",
        BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
        int,
    ),
    (
        "ca/farm_epop_associated",
        "ca/farm_epop_associated_checked",
        FARM_EPOP_ASSOCIATED_CHECKED,
        int,
    ),
    (
        "ca/farm_epop_agreement_filed",
        "ca/farm_epop_agreement_filed_checked",
        FARM_EPOP_AGREEMENT_FILED_CHECKED,
        int,
    ),
    (
        "ca/farm_minister_allocation_given",
        "ca/farm_minister_allocation_given_checked",
        FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
        int,
    ),
    (
        "ca/farm_partner",
        "ca/farm_partner_checked",
        FARM_PARTNER_CHECKED,
        int,
    ),
    (
        "ca/fish_epop_associated",
        "ca/fish_epop_associated_checked",
        FISH_EPOP_ASSOCIATED_CHECKED,
        int,
    ),
    (
        "ca/fish_epop_agreement_filed",
        "ca/fish_epop_agreement_filed_checked",
        FISH_EPOP_AGREEMENT_FILED_CHECKED,
        int,
    ),
    (
        "ca/fish_minister_allocation_given",
        "ca/fish_minister_allocation_given_checked",
        FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
        int,
    ),
    (
        "ca/fish_partner",
        "ca/fish_partner_checked",
        FISH_PARTNER_CHECKED,
        int,
    ),
    (
        "ca/business_partner",
        "ca/business_partner_checked",
        BUSINESS_PARTNER_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_disposed",
        "ca/flipped_property_disposed_checked",
        FLIPPED_PROPERTY_DISPOSED_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_1",
        "ca/flipped_property_life_event_1_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_2",
        "ca/flipped_property_life_event_2_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_3",
        "ca/flipped_property_life_event_3_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_4",
        "ca/flipped_property_life_event_4_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_5",
        "ca/flipped_property_life_event_5_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_6",
        "ca/flipped_property_life_event_6_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_7",
        "ca/flipped_property_life_event_7_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_8",
        "ca/flipped_property_life_event_8_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED,
        int,
    ),
    (
        "ca/flipped_property_life_event_9",
        "ca/flipped_property_life_event_9_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED,
        int,
    ),
    (
        "ca/capital_gains_deferral",
        "ca/capital_gains_deferral_checked",
        CAPITAL_GAINS_DEFERRAL_CHECKED,
        Decimal,
    ),
    (
        "ca/t3_taxable_dividends_other_than_eligible",
        "ca/t3_taxable_dividends_other_than_eligible_checked",
        T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        Decimal,
    ),
    (
        "ca/t4ps_taxable_dividends_other_than_eligible",
        "ca/t4ps_taxable_dividends_other_than_eligible_checked",
        T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        Decimal,
    ),
    (
        "ca/t5_taxable_dividends_other_than_eligible",
        "ca/t5_taxable_dividends_other_than_eligible_checked",
        T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        Decimal,
    ),
    (
        "ca/t5013_taxable_dividends_other_than_eligible",
        "ca/t5013_taxable_dividends_other_than_eligible_checked",
        T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        Decimal,
    ),
)


@pytest.mark.parametrize(("input_id", "identifier", "constant", "value_type"), CHECKED_KINDS)
def test_each_checked_kind_is_registered_and_is_the_output_of_its_check(
    input_id: str,
    identifier: str,
    constant: ArtifactKind[Any],
    value_type: type,
    registry: ArtifactRegistry,
) -> None:
    # The endnote 5 answers are yes or no questions, taken as a count and checked to be 0 or 1
    # (`ca/yes_or_no_count`); the percentage is checked not to exceed the total of column 3
    # (`core/at_most`, a choice, not a form rule). The checked kind is new, beside the input.
    kind = registry.kind(identifier)
    assert kind is constant
    assert kind.identifier == identifier
    assert kind.value_type is value_type
    assert kind.non_negative is True
    assert registry.kind(input_id) is not kind
    assert registry.kind(input_id).value_type is value_type


# The immediate expensing limit is the person's, across the statements of Forms T776, T2125, T2042
# and T2121. Area A endnote 5 of each form: "The total immediate expensing amount for the tax year
# (total of column 9) is limited to the lesser of: the immediate expensing limit ..."; Guides T4002
# and T4036: "The deduction is limited to $1.5 million per tax year".
def test_the_immediate_expensing_total_kinds_are_the_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    kinds = (
        RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
        BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
        FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
        FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
        IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
        IMMEDIATE_EXPENSING_AGREED_LIMIT,
        IMMEDIATE_EXPENSING_TOTAL_CLAIM,
    )

    assert [kind.identifier for kind in kinds] == [
        "ca/rental_immediate_expensing_claims_total",
        "ca/business_immediate_expensing_claims_total",
        "ca/farm_immediate_expensing_claims_total",
        "ca/fish_immediate_expensing_claims_total",
        "ca/immediate_expensing_claims_total",
        "ca/immediate_expensing_agreed_limit",
        "ca/immediate_expensing_total_claim",
    ]
    assert all(registry.get(kind.identifier) is kind for kind in kinds)
    assert all(kind.value_type is Decimal and kind.non_negative for kind in kinds)


# Guide T4036 "Limits on CCA": "you have to calculate your overall net income or loss for the year
# from all your rental properties before you can claim CCA ... You cannot use CCA to create or
# increase a rental loss"; and "if you received a T5013 slip, fill in only the following fields".
def test_the_rental_cca_limit_over_all_statements_kinds_are_registered(
    registry: ArtifactRegistry,
) -> None:
    money = (
        (RENTAL_NO_CCA_CLAIM, "ca/rental_no_cca_claim", True),
        (RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES, "ca/rental_cca_claim_on_own_properties", False),
        (RENTAL_INCOME_BEFORE_CCA, "ca/rental_income_before_cca", False),
        (RENTAL_INCOME_BEFORE_CCA_TOTAL, "ca/rental_income_before_cca_total", False),
        (RENTAL_CCA_LIMIT_ALL_STATEMENTS, "ca/rental_cca_limit_all_statements", True),
        (RENTAL_CCA_CLAIMS_TOTAL, "ca/rental_cca_claims_total", False),
        (RENTAL_CCA_TOTAL_CLAIM, "ca/rental_cca_total_claim", False),
    )
    counts = (
        (RENTAL_PARTNER_T5013_SLIP, "ca/rental_partner_t5013_slip"),
        (RENTAL_PARTNER_T5013_SLIP_CHECKED, "ca/rental_partner_t5013_slip_checked"),
        (RENTAL_T5013_SLIP_CONFLICT, "ca/rental_t5013_slip_conflict"),
        (RENTAL_T5013_SLIP_CONFLICT_CHECKED, "ca/rental_t5013_slip_conflict_checked"),
    )

    for kind, identifier, non_negative in money:
        assert kind.identifier == identifier
        assert registry.get(identifier) is kind
        assert kind.value_type is Decimal
        assert kind.non_negative is non_negative
    for count_kind, count_identifier in counts:
        assert count_kind.identifier == count_identifier
        assert registry.get(count_identifier) is count_kind
        assert count_kind.value_type is int
        assert count_kind.non_negative is True


# Income Tax Regulations 1104(3.5)(b): "where an eligible person or partnership has a taxation year
# that is less than 51 weeks, its immediate expensing limit for the year is that proportion of its
# immediate expensing limit for the year". The 51 weeks, 357 days, is one shared figure of every
# statement's limit, read where a statement's fiscal period is prorated.
def test_the_short_year_days_kind_is_the_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/immediate_expensing_short_year_days")
        is IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS
    )
    assert IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS.value_type is Decimal
    assert IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS.non_negative is True


# --- Schedule 3 Part 1, flipped property: the answer to line 17905 and the nine tick boxes of line
# 17906 are the inputs (each a 0 or 1 count), and the flag the form exports is a count of 1 or 0
# that `ca/count_by_conditions` gives from the ten answers checked by `ca/yes_or_no_count`. The
# flag is not a printed line of the form; it is the form's answer to whether the unit is a flipped
# property.

FLIPPED_PROPERTY_KINDS = (
    ("ca/flipped_property_disposed", FLIPPED_PROPERTY_DISPOSED),
    ("ca/flipped_property_disposed_checked", FLIPPED_PROPERTY_DISPOSED_CHECKED),
    ("ca/flipped_property_life_event_1", FLIPPED_PROPERTY_LIFE_EVENT_1),
    ("ca/flipped_property_life_event_1_checked", FLIPPED_PROPERTY_LIFE_EVENT_1_CHECKED),
    ("ca/flipped_property_life_event_2", FLIPPED_PROPERTY_LIFE_EVENT_2),
    ("ca/flipped_property_life_event_2_checked", FLIPPED_PROPERTY_LIFE_EVENT_2_CHECKED),
    ("ca/flipped_property_life_event_3", FLIPPED_PROPERTY_LIFE_EVENT_3),
    ("ca/flipped_property_life_event_3_checked", FLIPPED_PROPERTY_LIFE_EVENT_3_CHECKED),
    ("ca/flipped_property_life_event_4", FLIPPED_PROPERTY_LIFE_EVENT_4),
    ("ca/flipped_property_life_event_4_checked", FLIPPED_PROPERTY_LIFE_EVENT_4_CHECKED),
    ("ca/flipped_property_life_event_5", FLIPPED_PROPERTY_LIFE_EVENT_5),
    ("ca/flipped_property_life_event_5_checked", FLIPPED_PROPERTY_LIFE_EVENT_5_CHECKED),
    ("ca/flipped_property_life_event_6", FLIPPED_PROPERTY_LIFE_EVENT_6),
    ("ca/flipped_property_life_event_6_checked", FLIPPED_PROPERTY_LIFE_EVENT_6_CHECKED),
    ("ca/flipped_property_life_event_7", FLIPPED_PROPERTY_LIFE_EVENT_7),
    ("ca/flipped_property_life_event_7_checked", FLIPPED_PROPERTY_LIFE_EVENT_7_CHECKED),
    ("ca/flipped_property_life_event_8", FLIPPED_PROPERTY_LIFE_EVENT_8),
    ("ca/flipped_property_life_event_8_checked", FLIPPED_PROPERTY_LIFE_EVENT_8_CHECKED),
    ("ca/flipped_property_life_event_9", FLIPPED_PROPERTY_LIFE_EVENT_9),
    ("ca/flipped_property_life_event_9_checked", FLIPPED_PROPERTY_LIFE_EVENT_9_CHECKED),
    ("ca/flipped_property", FLIPPED_PROPERTY),
    # The life event count: 1 when line 17905 is "No" and a box of line 17906 is ticked. Its checked
    # count refuses a 1 (an input error), so only a 0 is produced by it.
    ("ca/flipped_property_life_event_without_yes", FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES),
    (
        "ca/flipped_property_life_event_without_yes_checked",
        FLIPPED_PROPERTY_LIFE_EVENT_WITHOUT_YES_CHECKED,
    ),
)


@pytest.mark.parametrize(("identifier", "kind"), FLIPPED_PROPERTY_KINDS)
def test_each_flipped_property_kind_is_a_registered_non_negative_int_count(
    identifier: str, kind: ArtifactKind[Any], registry: ArtifactRegistry
) -> None:
    # Line 17905 "Yes or No" and each box of line 17906 is a count of 0 or 1, as the form takes a
    # tick box: a non-negative int, checked before it is read. The flag is a count too.
    assert kind.identifier == identifier
    assert registry.get(identifier) is kind
    assert kind.value_type is int
    assert kind.non_negative is True


CHART_B_C_ARTIFACTS = (
    "ca/farm_chart_b_row_8_percentage",
    "ca/farm_chart_b_row_3_on",
    "ca/farm_chart_b_row_6_on",
    "ca/farm_chart_b_row_7_on",
    "ca/farm_chart_b_row_8_on",
    "ca/farm_chart_b_row_9_on",
    "ca/farm_chart_b_row_11_on",
    "ca/farm_chart_b_row_3_mb",
    "ca/farm_chart_b_row_6_mb",
    "ca/farm_chart_b_row_7_mb",
    "ca/farm_chart_b_row_8_mb",
    "ca/farm_chart_b_row_9_mb",
    "ca/farm_chart_b_row_11_mb",
    "ca/farm_chart_b_row_3_sk",
    "ca/farm_chart_b_row_6_sk",
    "ca/farm_chart_b_row_7_sk",
    "ca/farm_chart_b_row_8_sk",
    "ca/farm_chart_b_row_9_sk",
    "ca/farm_chart_b_row_11_sk",
    "ca/farm_chart_b_row_3_ab",
    "ca/farm_chart_b_row_6_ab",
    "ca/farm_chart_b_row_7_ab",
    "ca/farm_chart_b_row_8_ab",
    "ca/farm_chart_b_row_9_ab",
    "ca/farm_chart_b_row_11_ab",
    "ca/farm_chart_b_row_3_ns",
    "ca/farm_chart_b_row_6_ns",
    "ca/farm_chart_b_row_7_ns",
    "ca/farm_chart_b_row_8_ns",
    "ca/farm_chart_b_row_9_ns",
    "ca/farm_chart_b_row_11_ns",
    "ca/farm_chart_b_row_3_pe",
    "ca/farm_chart_b_row_6_pe",
    "ca/farm_chart_b_row_7_pe",
    "ca/farm_chart_b_row_8_pe",
    "ca/farm_chart_b_row_9_pe",
    "ca/farm_chart_b_row_11_pe",
    "ca/farm_chart_b_row_3_nl",
    "ca/farm_chart_b_row_6_nl",
    "ca/farm_chart_b_row_7_nl",
    "ca/farm_chart_b_row_8_nl",
    "ca/farm_chart_b_row_9_nl",
    "ca/farm_chart_b_row_11_nl",
    "ca/farm_chart_b_row_3_nb",
    "ca/farm_chart_b_row_6_nb",
    "ca/farm_chart_b_row_7_nb",
    "ca/farm_chart_b_row_8_nb",
    "ca/farm_chart_b_row_9_nb",
    "ca/farm_chart_b_row_11_nb",
    "ca/farm_chart_c_amount_on",
    "ca/farm_chart_c_amount_mb",
    "ca/farm_chart_c_amount_sk",
    "ca/farm_chart_c_amount_ab",
    "ca/farm_chart_c_amount_ns",
    "ca/farm_chart_c_amount_pe",
    "ca/farm_chart_c_amount_nl",
    "ca/farm_chart_c_amount_nb",
    "ca/farm_chart_b_total_gross_income",
    "ca/farm_chart_b_total_salaries",
)

# --- Form T2043 Chart B (#191): the statement's starting amounts and the Chart B totals ----------

# Chart B row 1 and row 4 for each designated province: computed artifacts (the total over the
# statement's province list), not fields of the statement.
CHART_B_STATEMENT_AMOUNTS = (
    "ca/farm_chart_b_gross_income_on",
    "ca/farm_chart_b_gross_income_mb",
    "ca/farm_chart_b_gross_income_sk",
    "ca/farm_chart_b_gross_income_ab",
    "ca/farm_chart_b_gross_income_ns",
    "ca/farm_chart_b_gross_income_pe",
    "ca/farm_chart_b_gross_income_nl",
    "ca/farm_chart_b_gross_income_nb",
    "ca/farm_chart_b_salaries_on",
    "ca/farm_chart_b_salaries_mb",
    "ca/farm_chart_b_salaries_sk",
    "ca/farm_chart_b_salaries_ab",
    "ca/farm_chart_b_salaries_ns",
    "ca/farm_chart_b_salaries_pe",
    "ca/farm_chart_b_salaries_nl",
    "ca/farm_chart_b_salaries_nb",
)


def test_the_sixteen_chart_b_starting_amounts_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for identifier in CHART_B_STATEMENT_AMOUNTS:
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind), identifier
        assert kind.identifier == identifier
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative, identifier
        assert identifier in REGISTERED, identifier


def test_the_chart_b_starting_amounts_are_no_longer_fields_of_each_statement() -> None:
    fields = {field.identifier for field in T2042_STATEMENTS.fields}
    for identifier in CHART_B_STATEMENT_AMOUNTS:
        assert identifier not in fields, identifier


CHART_B_PROVINCE_LIST_FIELDS = (
    "ca/farm_chart_b_province",
    "ca/farm_chart_b_province_gross_income",
    "ca/farm_chart_b_province_salaries",
)


def test_the_chart_b_province_list_is_a_nested_record_list_of_each_statement(
    registry: ArtifactRegistry,
) -> None:
    kind = registry.get("ca/farm_chart_b_provinces")
    assert isinstance(kind, RecordListKind)
    assert kind.identifier == "ca/farm_chart_b_provinces"
    assert kind.value_type is RecordList
    assert kind.identifier in REGISTERED
    assert {field.identifier for field in kind.fields} == set(CHART_B_PROVINCE_LIST_FIELDS)
    assert kind in T2042_STATEMENTS.fields


def test_the_chart_b_province_list_fields_are_an_int_code_and_two_non_negative_amounts(
    registry: ArtifactRegistry,
) -> None:
    kind = registry.get("ca/farm_chart_b_provinces")
    assert isinstance(kind, RecordListKind)
    fields = {field.identifier: field for field in kind.fields}

    province = fields["ca/farm_chart_b_province"]
    assert province.value_type is int
    assert province.non_negative
    assert "ca/farm_chart_b_province" in COUNTS
    for identifier in (
        "ca/farm_chart_b_province_gross_income",
        "ca/farm_chart_b_province_salaries",
    ):
        amount = fields[identifier]
        assert amount.value_type is Decimal, identifier
        assert amount.non_negative, identifier
        assert identifier in REGISTERED, identifier
        assert identifier not in SIGNED, identifier


def test_the_chart_b_province_list_is_a_record_list_and_not_a_count() -> None:
    assert "ca/farm_chart_b_provinces" in RECORD_LISTS
    assert "ca/farm_chart_b_provinces" not in COUNTS


def test_the_chart_b_starting_amounts_are_not_counts_or_designated_provinces() -> None:
    assert not set(CHART_B_STATEMENT_AMOUNTS) & COUNTS


def test_the_chart_b_totals_of_rows_2_and_5_are_registered_decimal_amounts(
    registry: ArtifactRegistry,
) -> None:
    for identifier in ("ca/farm_chart_b_total_gross_income", "ca/farm_chart_b_total_salaries"):
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind)
        assert kind.value_type is Decimal, identifier
        assert identifier in REGISTERED, identifier


def test_the_chart_b_note_9_count_is_an_int_count(registry: ArtifactRegistry) -> None:
    kind = registry.get("ca/farm_chart_b_note_9_applies")
    assert isinstance(kind, ArtifactKind)

    assert kind.value_type is int
    assert "ca/farm_chart_b_note_9_applies" in COUNTS


def test_the_chart_b_rows_and_chart_c_amounts_are_registered_decimal_artifacts(
    registry: ArtifactRegistry,
) -> None:
    for identifier in CHART_B_C_ARTIFACTS:
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind)
        assert kind.value_type is Decimal, identifier
        assert identifier in REGISTERED, identifier


# --- Form T2125 statement lines: the T1 line each statement goes on ----------------------------
# Form T2125 "Report the net income amount from line 9946 on the applicable line of your income tax
# and benefit return as indicated below: business income on line 13500, professional income on line
# 13700, commission income on line 13900". The statement's code for that choice is a count (1
# business, 2 professional, 3 commission; the form names no codes). Each statement's net (line 9946)
# and gross (line 8299) go to the line of its code, as a routed export per line, and the T1 lines
# total the routed exports over the statements.


def _kind(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind


def test_the_statement_line_code_is_a_non_negative_int_count(registry: ArtifactRegistry) -> None:
    kind = _kind(registry, "ca/business_income_line")
    assert kind.value_type is int
    assert kind.non_negative is True


def test_the_checked_statement_line_code_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    # The statement's line code once `ca/count_refused_by_conditions` has refused a code outside
    # 1 to 3: the three line flags read this kind, not the raw code.
    kind = _kind(registry, "ca/business_income_line_checked")
    assert kind.value_type is int
    assert kind.non_negative is True
    assert kind.identifier in COUNTS
    assert kind.identifier in REGISTERED
    assert kind is not _kind(registry, "ca/business_income_line")


def test_the_business_income_stays_the_signed_line_9946_kind(registry: ArtifactRegistry) -> None:
    # Form T2125 line 9946 "Your net income (loss): Amount 5D minus line 9945 (line 9946)": the kind
    # keeps its name and meaning inside the form. It prints no floor, so a loss is negative.
    kind = _kind(registry, "ca/business_income")
    assert kind.value_type is Decimal
    assert kind.non_negative is False


def test_the_routed_net_kinds_are_signed_decimals_one_per_line(registry: ArtifactRegistry) -> None:
    # The line 9946 net of a statement whose code names the line: the net times the 1 or 0 flag of
    # the code, so a loss keeps its sign on the line it goes to.
    for identifier in (
        "ca/net_on_business_line",
        "ca/net_on_professional_line",
        "ca/net_on_commission_line",
    ):
        kind = _kind(registry, identifier)
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is False, identifier


def test_the_routed_gross_kinds_are_signed_decimals_like_the_business_gross(
    registry: ArtifactRegistry,
) -> None:
    # Form T2125 line 8299 "Gross business or professional income: Line 8000 plus amount 3O": the
    # gross of each statement, routed by its code the same way as the net. The business gross of
    # the statement, `ca/business_gross_income`, is a signed Decimal, and so are these.
    for identifier in (
        "ca/gross_on_business_line",
        "ca/gross_on_professional_line",
        "ca/gross_on_commission_line",
    ):
        kind = _kind(registry, identifier)
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is _kind(registry, "ca/business_gross_income").non_negative, (
            identifier
        )


def test_the_split_gross_t1_kinds_are_signed_decimals_like_the_business_gross(
    registry: ArtifactRegistry,
) -> None:
    # T1 lines 13499, 13699 and 13899 "Gross": the totals of the routed grosses over the statements.
    for identifier in (
        "ca/gross_business_income",
        "ca/gross_professional_income",
        "ca/gross_commission_income",
    ):
        kind = _kind(registry, identifier)
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is _kind(registry, "ca/business_gross_income").non_negative, (
            identifier
        )


def test_the_routing_flags_are_non_negative_int_counts_of_0_or_1(
    registry: ArtifactRegistry,
) -> None:
    # The flag of each line is 1 when the statement's code is that line's number, else 0: a count
    # from `ca/count_by_conditions`, so an int that is never negative.
    for identifier in (
        "ca/business_line_is_business",
        "ca/business_line_is_professional",
        "ca/business_line_is_commission",
    ):
        kind = _kind(registry, identifier)
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier


# T1 income lines that are printed memos: each is a caller's input and a declared output, and no
# step reads it. Line 10120, 11410 and 11905 are "already included" in the lines above them (General
# Guide), so none of them is a total and none is added to total income.
def test_the_memo_income_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/emergency_services_volunteer_exempt_income")
        is EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME
    )
    assert registry.get("ca/t4_commissions") is T4_COMMISSIONS
    assert (
        registry.get("ca/wage_loss_replacement_contributions")
        is WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS
    )
    assert registry.get("ca/t4ap_disability_benefits") is T4AP_DISABILITY_BENEFITS
    assert registry.get("ca/uccb_designated_to_dependant") is UCCB_DESIGNATED_TO_DEPENDANT
    assert registry.get("ca/ei_maternity_parental_benefits") is EI_MATERNITY_PARENTAL_BENEFITS
    assert registry.get("ca/support_payments_received_total") is SUPPORT_PAYMENTS_RECEIVED_TOTAL


def test_the_memo_income_kinds_are_non_negative_money() -> None:
    for kind in (
        EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
        T4_COMMISSIONS,
        WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS,
        T4AP_DISABILITY_BENEFITS,
        UCCB_DESIGNATED_TO_DEPENDANT,
        EI_MATERNITY_PARENTAL_BENEFITS,
        SUPPORT_PAYMENTS_RECEIVED_TOTAL,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_also_outside_the_eight_answer_is_a_non_negative_int_count_and_its_checked_kind_too(
    registry: ArtifactRegistry,
) -> None:
    # The statement's yes or no answer for box 67062, and the answer once `ca/yes_or_no_count` has
    # refused a value above 1: the outside-eight presence reads the checked kind.
    checked = _kind(registry, "ca/farm_also_outside_eight_checked")

    assert registry.get("ca/farm_also_outside_eight") is FARM_ALSO_OUTSIDE_EIGHT
    for kind in (FARM_ALSO_OUTSIDE_EIGHT, checked):
        assert kind.value_type is int
        assert kind.non_negative is True
        assert kind.identifier in COUNTS
        assert kind.identifier in REGISTERED
    assert checked is not FARM_ALSO_OUTSIDE_EIGHT


# Form T776 line 7 "Partners: your share of amount 6, or the amount from your T5013 slip" and Part 1
# "Your percentage of the partnership %": the percentage is a starting amount, the share of amount
# 6 and amount 7 are signed, and the conflict count and its checked count are counts.
def test_the_rental_partner_amount_7_kinds_are_registered(registry: ArtifactRegistry) -> None:
    money = (
        (RENTAL_PARTNER_PERCENTAGE, "ca/rental_partner_percentage", True),
        (RENTAL_PARTNER_PERCENTAGE_CHECKED, "ca/rental_partner_percentage_checked", True),
        (RENTAL_PARTNER_SHARE_OF_AMOUNT_6, "ca/rental_partner_share_of_amount_6", False),
        (RENTAL_PARTNER_AMOUNT_7, "ca/rental_partner_amount_7", False),
    )
    counts = (
        (RENTAL_PARTNER_AMOUNT_7_CONFLICT, "ca/rental_partner_amount_7_conflict"),
        (RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED, "ca/rental_partner_amount_7_conflict_checked"),
    )

    for kind, identifier, non_negative in money:
        assert kind.identifier == identifier
        assert registry.get(identifier) is kind
        assert kind.value_type is Decimal
        assert kind.non_negative is non_negative
    for count_kind, count_identifier in counts:
        assert count_kind.identifier == count_identifier
        assert registry.get(count_identifier) is count_kind
        assert count_kind.value_type is int
        assert count_kind.non_negative is True
