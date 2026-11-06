"""Registered and money kinds of the federal catalog family `income`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    BOND_DISPOSITIONS,
    BOND_GAIN_OR_LOSS,
    BOND_PROCEEDS,
    BUSINESS_EPOP_AGREEMENT_FILED_CHECKED,
    BUSINESS_EPOP_ASSOCIATED_CHECKED,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    BUSINESS_INCOME,
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
    FARM_CHART_A_AMOUNT_8,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_SUBTOTAL,
    FARM_DAYS_IN_2024,
    FARM_DESIGNATED_PROVINCE,
    FARM_EPOP_AGREEMENT_FILED_CHECKED,
    FARM_EPOP_ASSOCIATED_CHECKED,
    FARM_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    FARM_IN_PROVINCE_AB,
    FARM_IN_PROVINCE_MB,
    FARM_IN_PROVINCE_NB,
    FARM_IN_PROVINCE_NL,
    FARM_IN_PROVINCE_NS,
    FARM_IN_PROVINCE_ON,
    FARM_IN_PROVINCE_PE,
    FARM_IN_PROVINCE_SK,
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
    FARM_VEHICLE_SALES_TAX_RATE,
    FARMING_INCOME,
    FHSA_INCOME,
    FISH_EPOP_AGREEMENT_FILED_CHECKED,
    FISH_EPOP_ASSOCIATED_CHECKED,
    FISH_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
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
    RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES,
    RENTAL_CCA_CLAIMS_TOTAL,
    RENTAL_CCA_LIMIT_ALL_STATEMENTS,
    RENTAL_CCA_TOTAL_CLAIM,
    RENTAL_COOWNER_CCA_CLAIM_CHECKED,
    RENTAL_COOWNER_CHECKED,
    RENTAL_COOWNER_RECAPTURED_CCA_CHECKED,
    RENTAL_COOWNER_TERMINAL_LOSS_CHECKED,
    RENTAL_EPOP_AGREEMENT_FILED_CHECKED,
    RENTAL_EPOP_ASSOCIATED_CHECKED,
    RENTAL_IMMEDIATE_EXPENSING_CLAIMS_TOTAL,
    RENTAL_INCOME_BEFORE_CCA,
    RENTAL_INCOME_BEFORE_CCA_TOTAL,
    RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
    RENTAL_NO_CCA_CLAIM,
    RENTAL_NON_COMPLIANT_CCA,
    RENTAL_PARTNER_AMOUNT_7,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT,
    RENTAL_PARTNER_AMOUNT_7_CONFLICT_CHECKED,
    RENTAL_PARTNER_CHECKED,
    RENTAL_PARTNER_PERCENTAGE,
    RENTAL_PARTNER_PERCENTAGE_CHECKED,
    RENTAL_PARTNER_SHARE_OF_AMOUNT_6,
    RENTAL_PARTNER_T5013_SLIP,
    RENTAL_PARTNER_T5013_SLIP_CHECKED,
    RENTAL_T5013_SLIP_CONFLICT,
    RENTAL_T5013_SLIP_CONFLICT_CHECKED,
    RRSP_INCOME,
    SCHEDULE_3_LINE_19200,
    SHARE_DISPOSITIONS,
    SHARE_GAIN_NOT_BELOW_ZERO,
    SHARE_GAIN_OR_LOSS,
    SHARE_PROCEEDS,
    SHORT_TERM_RENTAL_RELATED_CCA,
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
    T2042_STATEMENTS,
    T2121_STATEMENTS,
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
from tests.kinds import non_negative as declared_non_negative

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
    assert declared_non_negative(FARM_NON_ARMS_LENGTH_EXPENSES)
    assert declared_non_negative(FARM_DAYS_IN_2024)


def test_the_checked_designated_province_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    # The statement's province code once `ca/count_refused_by_conditions` has refused a code above
    # 8: the eight province counts of Chart A read this kind, not the raw code.
    kind = _kind(registry, "ca/farm_designated_province_checked")

    assert kind.value_type is int
    assert declared_non_negative(kind) is True
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
    assert not declared_non_negative(FARM_CHART_A_GROSS_EXPENSES)
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
        assert declared_non_negative(kind), kind.identifier


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
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


def test_the_presence_amounts_are_registered_non_negative_money_and_not_counts(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_PRESENT_AMOUNTS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier
        assert kind.identifier not in COUNTS, kind.identifier


def test_the_fuel_charge_place_totals_are_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    for kind in T2043_FUEL_CHARGE_PLACE_TOTALS:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_statement_count_and_the_box_are_registered_non_negative_ints(
    registry: ArtifactRegistry,
) -> None:
    for kind in (FUEL_CHARGE_FARM_STATEMENT_COUNT, FUEL_CHARGE_MULTIPLE_PROVINCES_BOX):
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.value_type is int, kind.identifier
        assert declared_non_negative(kind), kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier


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
    assert declared_non_negative(kind) is True
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
    assert declared_non_negative(DISPOSITION_DEPRECIABLE_PROPERTY) is True
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
        assert declared_non_negative(kind) is True
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
        assert declared_non_negative(kind) is True


def test_the_part_3_and_part_4_lines_that_print_losses_in_brackets_are_signed_decimals() -> None:
    # "Report all negative amounts (losses) using brackets."
    for identifier, kind in SIGNED_LINES:
        assert kind.value_type is Decimal, identifier
        assert declared_non_negative(kind) is False, identifier
        assert identifier in SIGNED


def test_the_gain_only_lines_the_deferral_and_the_unapplied_losses_are_non_negative() -> None:
    # Line 9 and line 10 are "gain only"; line 13 and the unapplied listed personal property
    # losses are amounts the filer states.
    for identifier, kind in NON_NEGATIVE_LINES:
        assert kind.value_type is Decimal, identifier
        assert declared_non_negative(kind) is True, identifier
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
    assert declared_non_negative(SHARE_GAIN_NOT_BELOW_ZERO) is True
    assert "ca/share_gain_not_below_zero" not in SIGNED


def test_the_checked_capital_gains_deferral_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 3 line 13 and line 16100 "Capital gains deferral from qualifying dispositions of
    # eligible small business corporation shares included on line 4" is checked to be at most
    # line 4 (`core/at_most`); the subtraction of line 14 reads the checked amount.
    assert registry.get("ca/capital_gains_deferral_checked") is CAPITAL_GAINS_DEFERRAL_CHECKED
    assert CAPITAL_GAINS_DEFERRAL_CHECKED.value_type is Decimal
    assert declared_non_negative(CAPITAL_GAINS_DEFERRAL_CHECKED) is True
    assert "ca/capital_gains_deferral_checked" not in SIGNED


def test_the_taxable_capital_gains_stay_non_negative() -> None:
    # T1 line 12700 takes line 26 only "If positive".
    assert declared_non_negative(TAXABLE_CAPITAL_GAINS) is True
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
    assert declared_non_negative(BUSINESS_VEHICLE_DAYS_DIVISOR) is True
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
    assert declared_non_negative(kind) is True
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
    assert all(kind.value_type is Decimal and declared_non_negative(kind) for kind in kinds)


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
        assert declared_non_negative(kind) is non_negative
    for count_kind, count_identifier in counts:
        assert count_kind.identifier == count_identifier
        assert registry.get(count_identifier) is count_kind
        assert count_kind.value_type is int
        assert declared_non_negative(count_kind) is True


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
    assert declared_non_negative(IMMEDIATE_EXPENSING_SHORT_YEAR_DAYS) is True


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
    assert declared_non_negative(kind) is True


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
        assert declared_non_negative(kind), identifier
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
    assert declared_non_negative(province)
    assert "ca/farm_chart_b_province" in COUNTS
    for identifier in (
        "ca/farm_chart_b_province_gross_income",
        "ca/farm_chart_b_province_salaries",
    ):
        amount = fields[identifier]
        assert amount.value_type is Decimal, identifier
        assert declared_non_negative(amount), identifier
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
    assert declared_non_negative(kind) is True


def test_the_checked_statement_line_code_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    # The statement's line code once `ca/count_refused_by_conditions` has refused a code outside
    # 1 to 3: the three line flags read this kind, not the raw code.
    kind = _kind(registry, "ca/business_income_line_checked")
    assert kind.value_type is int
    assert declared_non_negative(kind) is True
    assert kind.identifier in COUNTS
    assert kind.identifier in REGISTERED
    assert kind is not _kind(registry, "ca/business_income_line")


def test_the_business_income_stays_the_signed_line_9946_kind(registry: ArtifactRegistry) -> None:
    # Form T2125 line 9946 "Your net income (loss): Amount 5D minus line 9945 (line 9946)": the kind
    # keeps its name and meaning inside the form. It prints no floor, so a loss is negative.
    kind = _kind(registry, "ca/business_income")
    assert kind.value_type is Decimal
    assert declared_non_negative(kind) is False


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
        assert declared_non_negative(kind) is False, identifier


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
        assert declared_non_negative(kind) is declared_non_negative(
            _kind(registry, "ca/business_gross_income")
        ), identifier


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
        assert declared_non_negative(kind) is declared_non_negative(
            _kind(registry, "ca/business_gross_income")
        ), identifier


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
        assert declared_non_negative(kind) is True, identifier


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
        assert declared_non_negative(kind) is True, kind.identifier


def test_the_also_outside_the_eight_answer_is_a_non_negative_int_count_and_its_checked_kind_too(
    registry: ArtifactRegistry,
) -> None:
    # The statement's yes or no answer for box 67062, and the answer once `ca/yes_or_no_count` has
    # refused a value above 1: the outside-eight presence reads the checked kind.
    checked = _kind(registry, "ca/farm_also_outside_eight_checked")

    assert registry.get("ca/farm_also_outside_eight") is FARM_ALSO_OUTSIDE_EIGHT
    for kind in (FARM_ALSO_OUTSIDE_EIGHT, checked):
        assert kind.value_type is int
        assert declared_non_negative(kind) is True
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
        assert declared_non_negative(kind) is non_negative
    for count_kind, count_identifier in counts:
        assert count_kind.identifier == count_identifier
        assert registry.get(count_identifier) is count_kind
        assert count_kind.value_type is int
        assert declared_non_negative(count_kind) is True
