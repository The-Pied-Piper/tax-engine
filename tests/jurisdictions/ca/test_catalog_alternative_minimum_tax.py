"""Registered and money kinds of the federal catalog family `alternative_minimum_tax`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.catalog.alternative_minimum_tax
from tax_engine.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.jurisdictions.ca.catalog import (
    AMT_ADDITIONAL_TAXES_FOR_CARRYOVER,
    AMT_ADJUSTED_INCOME_WITH_GAINS,
    AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS,
    AMT_ADJUSTED_TAXABLE_INCOME,
    AMT_ADJUSTMENTS_AFTER_RATE_TOTAL,
    AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL,
    AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL,
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_AMOUNT_A_MINUS_AMOUNT_B,
    AMT_APPLICABLE_RATE_AMOUNT,
    AMT_BASIC_EXEMPTION,
    AMT_BASIC_FEDERAL_TAX,
    AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX,
    AMT_CAPITAL_GAIN_NOT_BELOW_ZERO,
    AMT_CAPITAL_GAINS_ADDED,
    AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO,
    AMT_CAPITAL_GAINS_ADJUSTMENTS,
    AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL,
    AMT_CAPITAL_GAINS_DIFFERENCE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_CARRYOVER_BALANCE,
    AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES,
    AMT_CLASS_43_1_INCOME,
    AMT_COMMISSION_EMPLOYMENT_EXPENSES,
    AMT_CREDITS_ADJUSTMENTS_TOTAL,
    AMT_CREDITS_TOTAL,
    AMT_DEDUCTIONS_TOTAL,
    AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION,
    AMT_DIVIDENDS_ADJUSTMENTS_TOTAL,
    AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT,
    AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT,
    AMT_DONATIONS_AND_GIFTS_ADJUSTMENT,
    AMT_EXCESS_EPSP_AMOUNTS,
    AMT_EXPENSES_INCLUDED_ON_LINE_22100,
    AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED,
    AMT_FEDERAL_SURTAX,
    AMT_FEDERAL_SURTAX_AT_48_PERCENT,
    AMT_FEDERAL_SURTAX_IF_NON_RESIDENT,
    AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS,
    AMT_FEDERAL_TAX_PAYABLE,
    AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
    AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX,
    AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE,
    AMT_FILM_PROPERTY_ADJUSTMENT,
    AMT_FILM_PROPERTY_CCA_AND_CARRYING_CHARGES,
    AMT_FILM_PROPERTY_INCOME_BEFORE_CCA,
    AMT_FINANCING_EXPENSES,
    AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL,
    AMT_FOREIGN_BUSINESS_INCOME,
    AMT_FOREIGN_BUSINESS_TAX_PAID,
    AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE,
    AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE_CLAIM,
    AMT_FOREIGN_INCOME_LIMIT,
    AMT_FOREIGN_NON_BUSINESS_INCOME,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_FOREIGN_TAX_CREDIT_LESSER,
    AMT_FOREIGN_TAXES_PAID,
    AMT_FORFEITED_SALARY_DEFERRAL_AMOUNTS,
    AMT_GRADUATED_RATE_ESTATE_CAPITAL_GAINS,
    AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT,
    AMT_GROSS_MINIMUM_AMOUNT,
    AMT_INVESTMENT_COUNSEL_FEES,
    AMT_INVESTMENT_TAX_CREDIT,
    AMT_INVESTMENT_TAX_CREDIT_CLAIM,
    AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D,
    AMT_LEGAL_AND_ACCOUNTING_EXPENSES,
    AMT_LIFE_INSURANCE_PREMIUMS_AS_COLLATERAL,
    AMT_LIFETIME_EXEMPTION_ADJUSTMENT,
    AMT_LIMITED_PARTNER_CARRYING_CHARGES,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED_CHECKED,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION,
    AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT,
    AMT_LINE_3_HAS_AMOUNT,
    AMT_LINES_39_AND_40_BOTH,
    AMT_LINES_39_AND_40_BOTH_CHECKED,
    AMT_LINES_22100_22400_AND_23200,
    AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL,
    AMT_MAXIMUM_CARRYOVER_APPLIED,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_AFTER_REGULAR_TAX,
    AMT_MINIMUM_TAX_CARRYOVER_APPLIED,
    AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
    AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS,
    AMT_NET_ADJUSTED_TAXABLE_INCOME,
    AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS,
    AMT_NET_CAPITAL_LOSSES_DIFFERENCE,
    AMT_NET_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_NON_CAPITAL_LOSSES_ADJUSTMENT,
    AMT_NON_CAPITAL_LOSSES_DIFFERENCE,
    AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
    AMT_NON_DEDUCTIBLE_INTEREST,
    AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES,
    AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED,
    AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES,
    AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT,
    AMT_NON_RESIDENT_OR_DEEMED_RESIDENT,
    AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED,
    AMT_OFFICE_EXPENSES_ADJUSTMENT,
    AMT_OTHER_YEARS_LOSSES_TOTAL,
    AMT_PART_1_SUBTOTAL,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    AMT_PART_6_FEDERAL_SURTAX,
    AMT_PART_6_HAS_AMOUNT_ON_LINE_10,
    AMT_PART_6_SURTAX_AT_48_PERCENT,
    AMT_PART_6_SURTAX_IF_NON_RESIDENT,
    AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS,
    AMT_PART_6_TAX_WITH_SURTAX,
    AMT_PART_7_BASIC_TAX_WITH_RECAPTURE,
    AMT_PART_7_CREDITS_TOTAL,
    AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE,
    AMT_PART_7_FOREIGN_CREDIT_SHARE,
    AMT_PART_7_FOREIGN_TAXES_PAID,
    AMT_PART_7_TAX_LESS_CREDITS,
    AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE,
    AMT_PART_8_ADDITIONAL_TAXES,
    AMT_PPIP_PREMIUMS_DEDUCTION,
    AMT_PPIP_PREMIUMS_IN_ONTARIO,
    AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED,
    AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION,
    AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT,
    AMT_PUBLICLY_LISTED_GIFTS_NET,
    AMT_PUBLICLY_LISTED_GIFTS_T1170_LINE_68231,
    AMT_PUBLICLY_LISTED_GIFTS_TOTAL,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED,
    AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE,
    AMT_REGULAR_NET_TAX_LESS_SURTAX,
    AMT_REGULAR_TAX_CREDITS_TOTAL,
    AMT_RENTAL_PROPERTY_ADJUSTMENT,
    AMT_RENTAL_PROPERTY_CCA_AND_CARRYING_CHARGES,
    AMT_RENTAL_PROPERTY_INCOME_BEFORE_CCA,
    AMT_REPAYMENT_OF_SALARY_AND_WAGES,
    AMT_REPAYMENT_OF_WAGE_LOSS_REPLACEMENT,
    AMT_RESOURCE_EXPENDITURES,
    AMT_RESOURCE_EXPENDITURES_CHECKED,
    AMT_RESOURCE_FOREIGN_PROPERTY_INCOME,
    AMT_RESOURCE_INCOME_TOTAL,
    AMT_RESOURCE_PRODUCTION_INCOME,
    AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES,
    AMT_SECTION_119_FORMER_RESIDENT_CREDIT,
    AMT_SECURITY_OPTION_GIFTS_DEDUCTION,
    AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS,
    AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL,
    AMT_SECURITY_OPTIONS_D1_TOTAL,
    AMT_SECURITY_OPTIONS_D_TOTAL,
    AMT_SECURITY_OPTIONS_NET,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    AMT_SPLIT_INCOME_AND_CREDITS_TOTAL,
    AMT_SUBJECT_TO_MINIMUM_TAX,
    AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS,
    AMT_T2203_COLUMN_5_PERCENTAGE,
    AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED,
    AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM,
    AMT_TAX_PAYABLE_AFTER_CREDITS,
    AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER,
    AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE,
    AMT_TAX_SHELTER_ADJUSTMENTS,
    AMT_TAX_SHELTER_DEDUCTIBLE_AMOUNTS,
    AMT_TAX_SHELTER_LOSSES,
    AMT_TOTAL_FOREIGN_INCOME,
    AMT_TREATY_EXEMPT_CAPITAL_GAINS,
    AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED,
    AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS,
    AMT_UNAPPLIED_2018_CARRYOVER,
    AMT_UNAPPLIED_2018_CARRYOVER_CHECKED,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, SIGNED

PART_1_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_FILM_PROPERTY_CCA_AND_CARRYING_CHARGES,
    AMT_FILM_PROPERTY_INCOME_BEFORE_CCA,
    AMT_FILM_PROPERTY_ADJUSTMENT,
    AMT_RENTAL_PROPERTY_CCA_AND_CARRYING_CHARGES,
    AMT_RENTAL_PROPERTY_INCOME_BEFORE_CCA,
    AMT_RENTAL_PROPERTY_ADJUSTMENT,
    AMT_TAX_SHELTER_LOSSES,
    AMT_TAX_SHELTER_DEDUCTIBLE_AMOUNTS,
    AMT_LIMITED_PARTNER_CARRYING_CHARGES,
    AMT_TAX_SHELTER_ADJUSTMENTS,
    AMT_PART_1_SUBTOTAL,
    AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS,
    AMT_TREATY_EXEMPT_CAPITAL_GAINS,
    AMT_GRADUATED_RATE_ESTATE_CAPITAL_GAINS,
    AMT_CAPITAL_GAINS_ADJUSTMENTS,
    AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS,
    AMT_PUBLICLY_LISTED_GIFTS_TOTAL,
    AMT_PUBLICLY_LISTED_GIFTS_T1170_LINE_68231,
    AMT_PUBLICLY_LISTED_GIFTS_NET,
    AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT,
    AMT_CAPITAL_GAINS_DIFFERENCE,
    AMT_CAPITAL_GAINS_ADDED,
    AMT_ADJUSTED_INCOME_WITH_GAINS,
    AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS,
    AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL,
    AMT_ADJUSTMENTS_AFTER_RATE_TOTAL,
    AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT,
    AMT_AMOUNT_A_MINUS_AMOUNT_B,
    AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT,
    AMT_DIVIDENDS_ADJUSTMENTS_TOTAL,
    AMT_LIFETIME_EXEMPTION_ADJUSTMENT,
    AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE,
    AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL,
    AMT_ADJUSTED_TAXABLE_INCOME,
    AMT_BASIC_EXEMPTION,
    AMT_NET_ADJUSTED_TAXABLE_INCOME,
    AMT_GROSS_MINIMUM_AMOUNT,
    AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT,
    AMT_DONATIONS_AND_GIFTS_ADJUSTMENT,
    AMT_SECTION_119_FORMER_RESIDENT_CREDIT,
    AMT_CREDITS_ADJUSTMENTS_TOTAL,
    AMT_MINIMUM_AMOUNT,
)

PART_9_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_RESOURCE_EXPENDITURES,
    AMT_RESOURCE_PRODUCTION_INCOME,
    AMT_RESOURCE_FOREIGN_PROPERTY_INCOME,
    AMT_CLASS_43_1_INCOME,
    AMT_RESOURCE_INCOME_TOTAL,
    AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES,
)

# Part 1 lines 28 to 32 and 35 to 38: the security options deductions.
SECURITY_OPTIONS_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    T4_SECURITY_OPTIONS_BOXES_39_AND_91,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS,
    AMT_SECURITY_OPTIONS_D_TOTAL,
    AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS,
    AMT_SECURITY_OPTION_GIFTS_DEDUCTION,
    AMT_SECURITY_OPTIONS_NET,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION,
    AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION,
    AMT_SECURITY_OPTIONS_D1_TOTAL,
)

# Part 1 lines 39 to 63: the losses of other years, the deductions of lines 54 to 62 and line 63.
LOSSES_AND_DEDUCTIONS_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION,
    AMT_NON_CAPITAL_LOSSES_DIFFERENCE,
    AMT_NET_CAPITAL_LOSSES_DIFFERENCE,
    AMT_OTHER_YEARS_LOSSES_TOTAL,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED,
    AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT,
    AMT_NON_CAPITAL_LOSSES_ADJUSTMENT,
    AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL,
    AMT_PPIP_PREMIUMS_DEDUCTION,
    AMT_DEDUCTIONS_TOTAL,
)

# Part 1 lines 64 to 80: the non-deductible expenses and the applicable rate.
NON_DEDUCTIBLE_AND_RATE_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_NON_DEDUCTIBLE_INTEREST,
    AMT_LIFE_INSURANCE_PREMIUMS_AS_COLLATERAL,
    AMT_FINANCING_EXPENSES,
    AMT_INVESTMENT_COUNSEL_FEES,
    AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES,
    AMT_COMMISSION_EMPLOYMENT_EXPENSES,
    AMT_LEGAL_AND_ACCOUNTING_EXPENSES,
    AMT_REPAYMENT_OF_SALARY_AND_WAGES,
    AMT_EXCESS_EPSP_AMOUNTS,
    AMT_FORFEITED_SALARY_DEFERRAL_AMOUNTS,
    AMT_REPAYMENT_OF_WAGE_LOSS_REPLACEMENT,
    AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES,
    AMT_OFFICE_EXPENSES_ADJUSTMENT,
    AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL,
    AMT_APPLICABLE_RATE_AMOUNT,
)

# Part 3 lines 1 to 15: the federal surtax, the credits and the regular net federal tax payable,
# with the T2203 percentage and the two counts that choose the surtax line 4 takes.
PART_3_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_FEDERAL_SURTAX_AT_48_PERCENT,
    AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS,
    AMT_FEDERAL_SURTAX_IF_NON_RESIDENT,
    AMT_FEDERAL_SURTAX,
    AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE,
    AMT_T2203_COLUMN_5_PERCENTAGE,
    AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL,
    AMT_FEDERAL_TAX_PAYABLE,
    AMT_INVESTMENT_TAX_CREDIT_CLAIM,
    AMT_INVESTMENT_TAX_CREDIT,
    AMT_REGULAR_TAX_CREDITS_TOTAL,
    AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE,
)
# Part 3 counts, and the caller's choice of minimum tax, a count of 1 for yes and 0 for no, which
# chooses between Form T2203 Part 2 line 10 and Part 3 line 4 for T1 line 127 (Form T2203 Part 2:
# "If you are subject to minimum tax, do not complete lines 4 to 10").
PART_3_COUNTS: tuple[ArtifactKind[int], ...] = (
    AMT_NON_RESIDENT_OR_DEEMED_RESIDENT,
    AMT_LINE_3_HAS_AMOUNT,
    AMT_SUBJECT_TO_MINIMUM_TAX,
)

# Part 4 lines 1 to 11: the special foreign tax credit, with the caller's foreign figures and the
# claim on line 3. The bound of line 3, line 23 of Part 1 with a loss taken as 0, is not a form line
# but is a money kind of the same family.
PART_4_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO,
    AMT_FOREIGN_BUSINESS_INCOME,
    AMT_FOREIGN_NON_BUSINESS_INCOME,
    AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE_CLAIM,
    AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE,
    AMT_TOTAL_FOREIGN_INCOME,
    AMT_FOREIGN_INCOME_LIMIT,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_FOREIGN_BUSINESS_TAX_PAID,
    AMT_FOREIGN_TAXES_PAID,
    AMT_FOREIGN_TAX_CREDIT_LESSER,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
)

# Part 5 lines 1 to 11: the net minimum tax payable, the regular net tax less the surtax, the
# minimum tax after the regular tax, the investment tax credit less amount 15 of Part D of Form
# T2038(IND), and the alternative minimum tax payable; line 9 is the investment tax credit of Part
# D, which the investment tax credit family computes and this family reads.
PART_5_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_REGULAR_NET_TAX_LESS_SURTAX,
    AMT_MINIMUM_TAX_AFTER_REGULAR_TAX,
    AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D,
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
)
# Part 5 line 11: the count of the condition "line 11 is positive", which chooses T1 line 41700.
PART_5_COUNTS: tuple[ArtifactKind[int], ...] = (AMT_PART_5_LINE_11_IS_POSITIVE,)

# Part 6 lines 1 to 14: the federal tax payable under the alternative minimum tax, from line 3, the
# basic federal tax less the split income tax, to line 14, the greater of line 12 and the split
# income tax after the credits of Form T1206 (line 24), with the surtax of lines 9 to 11.
PART_6_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX,
    AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT,
    AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX,
    AMT_PART_6_SURTAX_AT_48_PERCENT,
    AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS,
    AMT_PART_6_SURTAX_IF_NON_RESIDENT,
    AMT_PART_6_FEDERAL_SURTAX,
    AMT_PART_6_TAX_WITH_SURTAX,
    AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
)
# Part 6 line 11: the count of the condition "you have an amount on line 10".
PART_6_COUNTS: tuple[ArtifactKind[int], ...] = (AMT_PART_6_HAS_AMOUNT_ON_LINE_10,)

# Part 7 lines 1 to 14: the additional taxes paid for minimum tax carryover, from the basic federal
# tax with the recapture to the foreign credit share, the tax less the credits plus the share, and
# line 14, the additional taxes that Part 8 line 14 reads.
PART_7_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_PART_7_BASIC_TAX_WITH_RECAPTURE,
    AMT_PART_7_CREDITS_TOTAL,
    AMT_PART_7_TAX_LESS_CREDITS,
    AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE,
    AMT_PART_7_FOREIGN_TAXES_PAID,
    AMT_PART_7_FOREIGN_CREDIT_SHARE,
    AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE,
    AMT_ADDITIONAL_TAXES_FOR_CARRYOVER,
)

# Part 8 lines 13 to 17: the balance of the minimum tax carryover available for later years, with
# the additional 2025 taxes, and the total available for 2026, less the unapplied 2018 carryover.
PART_8_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_PART_8_ADDITIONAL_TAXES,
    AMT_CARRYOVER_BALANCE,
    AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES,
    AMT_UNAPPLIED_2018_CARRYOVER,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
)


# Part 2 lines 1 to 7 and Part 8 lines 1 to 12: the basic federal tax and the minimum tax
# carryover, with the carryover claim (line 12) and the cap on it.
PART_2_AND_8_KINDS: tuple[ArtifactKind[Decimal], ...] = (
    AMT_CREDITS_TOTAL,
    AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER,
    AMT_BASIC_FEDERAL_TAX,
    AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS,
    AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE,
    AMT_SPLIT_INCOME_AND_CREDITS_TOTAL,
    AMT_TAX_PAYABLE_AFTER_CREDITS,
    AMT_MAXIMUM_CARRYOVER_APPLIED,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_TAX_CARRYOVER_APPLIED,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
)


def test_the_alternative_minimum_tax_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_film_property_cca_and_carrying_charges")
        is AMT_FILM_PROPERTY_CCA_AND_CARRYING_CHARGES
    )
    assert (
        registry.get("ca/amt_film_property_income_before_cca")
        is AMT_FILM_PROPERTY_INCOME_BEFORE_CCA
    )
    assert registry.get("ca/amt_film_property_adjustment") is AMT_FILM_PROPERTY_ADJUSTMENT
    assert (
        registry.get("ca/amt_rental_property_cca_and_carrying_charges")
        is AMT_RENTAL_PROPERTY_CCA_AND_CARRYING_CHARGES
    )
    assert (
        registry.get("ca/amt_rental_property_income_before_cca")
        is AMT_RENTAL_PROPERTY_INCOME_BEFORE_CCA
    )
    assert registry.get("ca/amt_rental_property_adjustment") is AMT_RENTAL_PROPERTY_ADJUSTMENT
    assert registry.get("ca/amt_tax_shelter_losses") is AMT_TAX_SHELTER_LOSSES
    assert (
        registry.get("ca/amt_tax_shelter_deductible_amounts") is AMT_TAX_SHELTER_DEDUCTIBLE_AMOUNTS
    )
    assert (
        registry.get("ca/amt_limited_partner_carrying_charges")
        is AMT_LIMITED_PARTNER_CARRYING_CHARGES
    )
    assert registry.get("ca/amt_tax_shelter_adjustments") is AMT_TAX_SHELTER_ADJUSTMENTS
    assert registry.get("ca/amt_part_1_subtotal") is AMT_PART_1_SUBTOTAL


def test_the_part_9_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/amt_resource_expenditures") is AMT_RESOURCE_EXPENDITURES
    assert registry.get("ca/amt_resource_production_income") is AMT_RESOURCE_PRODUCTION_INCOME
    assert (
        registry.get("ca/amt_resource_foreign_property_income")
        is AMT_RESOURCE_FOREIGN_PROPERTY_INCOME
    )
    assert registry.get("ca/amt_class_43_1_income") is AMT_CLASS_43_1_INCOME
    assert registry.get("ca/amt_resource_income_total") is AMT_RESOURCE_INCOME_TOTAL
    assert (
        registry.get("ca/amt_resource_property_and_flow_through_shares")
        is AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES
    )


def test_the_part_1_capital_gains_and_gifts_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_mortgage_foreclosure_capital_gains")
        is AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS
    )
    assert registry.get("ca/amt_treaty_exempt_capital_gains") is AMT_TREATY_EXEMPT_CAPITAL_GAINS
    assert (
        registry.get("ca/amt_graduated_rate_estate_capital_gains")
        is AMT_GRADUATED_RATE_ESTATE_CAPITAL_GAINS
    )
    assert registry.get("ca/amt_capital_gains_adjustments") is AMT_CAPITAL_GAINS_ADJUSTMENTS
    assert (
        registry.get("ca/amt_net_capital_gains_after_adjustments")
        is AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS
    )
    assert registry.get("ca/amt_publicly_listed_gifts_total") is AMT_PUBLICLY_LISTED_GIFTS_TOTAL
    assert (
        registry.get("ca/amt_publicly_listed_gifts_t1170_line_68231")
        is AMT_PUBLICLY_LISTED_GIFTS_T1170_LINE_68231
    )
    assert registry.get("ca/amt_publicly_listed_gifts_net") is AMT_PUBLICLY_LISTED_GIFTS_NET
    assert (
        registry.get("ca/amt_publicly_listed_gifts_adjustment")
        is AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT
    )


def test_the_part_1_lines_22_23_and_27_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/amt_capital_gains_difference") is AMT_CAPITAL_GAINS_DIFFERENCE
    assert registry.get("ca/amt_capital_gains_added") is AMT_CAPITAL_GAINS_ADDED
    assert registry.get("ca/amt_adjusted_income_with_gains") is AMT_ADJUSTED_INCOME_WITH_GAINS


def test_the_part_1_lines_33_44_and_82_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_adjusted_income_with_security_options")
        is AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS
    )
    assert (
        registry.get("ca/amt_security_options_and_losses_total")
        is AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL
    )
    assert registry.get("ca/amt_adjustments_after_rate_total") is AMT_ADJUSTMENTS_AFTER_RATE_TOTAL


def test_the_part_1_lines_84_to_89_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_dividends_other_than_eligible_adjustment")
        is AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT
    )
    assert registry.get("ca/amt_amount_a_minus_amount_b") is AMT_AMOUNT_A_MINUS_AMOUNT_B
    assert (
        registry.get("ca/amt_dividends_difference_adjustment")
        is AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT
    )
    assert registry.get("ca/amt_dividends_adjustments_total") is AMT_DIVIDENDS_ADJUSTMENTS_TOTAL
    assert registry.get("ca/amt_lifetime_exemption_adjustment") is AMT_LIFETIME_EXEMPTION_ADJUSTMENT
    assert (
        registry.get("ca/amt_adjustments_with_lifetime_exemption_total")
        is AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL
    )
    assert (
        registry.get("ca/amt_qbt_capital_gains_deduction_doubled")
        is AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED
    )


def test_the_part_1_lines_91_to_103_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_qbt_capital_gains_deduction_difference")
        is AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE
    )
    assert (
        registry.get("ca/amt_capital_gains_deductions_total") is AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL
    )
    assert registry.get("ca/amt_adjusted_taxable_income") is AMT_ADJUSTED_TAXABLE_INCOME
    assert registry.get("ca/amt_basic_exemption") is AMT_BASIC_EXEMPTION
    assert registry.get("ca/amt_net_adjusted_taxable_income") is AMT_NET_ADJUSTED_TAXABLE_INCOME
    assert registry.get("ca/amt_gross_minimum_amount") is AMT_GROSS_MINIMUM_AMOUNT
    assert (
        registry.get("ca/amt_non_refundable_credits_adjustment")
        is AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT
    )
    assert (
        registry.get("ca/amt_donations_and_gifts_adjustment") is AMT_DONATIONS_AND_GIFTS_ADJUSTMENT
    )
    # The caller's stand-in is gone: Form T691 line 100 reads the computed line 133.
    assert "ca/amt_federal_logging_tax_credit" not in registry.identifiers()
    assert (
        registry.get("ca/amt_section_119_former_resident_credit")
        is AMT_SECTION_119_FORMER_RESIDENT_CREDIT
    )
    assert registry.get("ca/amt_credits_adjustments_total") is AMT_CREDITS_ADJUSTMENTS_TOTAL
    assert registry.get("ca/amt_minimum_amount") is AMT_MINIMUM_AMOUNT


def test_the_security_options_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/t4_security_options_boxes_39_and_91")
        is T4_SECURITY_OPTIONS_BOXES_39_AND_91
    )
    assert (
        registry.get("ca/amt_t1212_line_29_deferred_security_options")
        is AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS
    )
    assert registry.get("ca/amt_security_options_d_total") is AMT_SECURITY_OPTIONS_D_TOTAL
    assert (
        registry.get("ca/amt_security_option_publicly_listed_gifts")
        is AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS
    )
    assert (
        registry.get("ca/amt_security_option_gifts_deduction")
        is AMT_SECURITY_OPTION_GIFTS_DEDUCTION
    )
    assert registry.get("ca/amt_security_options_net") is AMT_SECURITY_OPTIONS_NET
    assert (
        registry.get("ca/t4_security_options_boxes_41_and_92")
        is T4_SECURITY_OPTIONS_BOXES_41_AND_92
    )
    assert (
        registry.get("ca/amt_prospector_or_grubstaker_deduction")
        is AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION
    )
    assert (
        registry.get("ca/amt_deferred_profit_sharing_plan_deduction")
        is AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION
    )
    assert registry.get("ca/amt_security_options_d1_total") is AMT_SECURITY_OPTIONS_D1_TOTAL


def test_the_losses_and_deductions_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/amt_limited_partnership_difference_no_election")
        is AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION
    )
    assert (
        registry.get("ca/amt_limited_partnership_difference_election")
        is AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION
    )
    assert registry.get("ca/amt_non_capital_losses_difference") is AMT_NON_CAPITAL_LOSSES_DIFFERENCE
    assert registry.get("ca/amt_net_capital_losses_difference") is AMT_NET_CAPITAL_LOSSES_DIFFERENCE
    assert registry.get("ca/amt_other_years_losses_total") is AMT_OTHER_YEARS_LOSSES_TOTAL
    assert (
        registry.get("ca/amt_limited_partnership_difference_applied")
        is AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED
    )
    assert (
        registry.get("ca/amt_limited_partnership_losses_adjustment")
        is AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT
    )
    assert registry.get("ca/amt_non_capital_losses_adjustment") is AMT_NON_CAPITAL_LOSSES_ADJUSTMENT
    assert (
        registry.get("ca/amt_losses_and_deductions_subtotal") is AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL
    )
    assert registry.get("ca/amt_ppip_premiums_deduction") is AMT_PPIP_PREMIUMS_DEDUCTION
    assert registry.get("ca/amt_deductions_total") is AMT_DEDUCTIONS_TOTAL


def test_the_non_deductible_expenses_and_applicable_rate_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/amt_non_deductible_interest") is AMT_NON_DEDUCTIBLE_INTEREST
    assert (
        registry.get("ca/amt_life_insurance_premiums_as_collateral")
        is AMT_LIFE_INSURANCE_PREMIUMS_AS_COLLATERAL
    )
    assert registry.get("ca/amt_financing_expenses") is AMT_FINANCING_EXPENSES
    assert registry.get("ca/amt_investment_counsel_fees") is AMT_INVESTMENT_COUNSEL_FEES
    assert (
        registry.get("ca/amt_non_deductible_property_expenses")
        is AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES
    )
    assert (
        registry.get("ca/amt_commission_employment_expenses") is AMT_COMMISSION_EMPLOYMENT_EXPENSES
    )
    assert registry.get("ca/amt_legal_and_accounting_expenses") is AMT_LEGAL_AND_ACCOUNTING_EXPENSES
    assert registry.get("ca/amt_repayment_of_salary_and_wages") is AMT_REPAYMENT_OF_SALARY_AND_WAGES
    assert registry.get("ca/amt_excess_epsp_amounts") is AMT_EXCESS_EPSP_AMOUNTS
    assert (
        registry.get("ca/amt_forfeited_salary_deferral_amounts")
        is AMT_FORFEITED_SALARY_DEFERRAL_AMOUNTS
    )
    assert (
        registry.get("ca/amt_repayment_of_wage_loss_replacement")
        is AMT_REPAYMENT_OF_WAGE_LOSS_REPLACEMENT
    )
    assert (
        registry.get("ca/amt_non_deductible_office_expenses") is AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES
    )
    assert registry.get("ca/amt_office_expenses_adjustment") is AMT_OFFICE_EXPENSES_ADJUSTMENT
    assert registry.get("ca/amt_adjustments_before_rate_total") is AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL
    assert registry.get("ca/amt_applicable_rate_amount") is AMT_APPLICABLE_RATE_AMOUNT


def test_the_line_76_check_is_registered_beside_its_sum(registry: ArtifactRegistry) -> None:
    # Form T691 Part 1 line 76 "Add lines 70 to 75." is at most line 69, the other employment
    # expenses of line 22900 (line 77 "Line 69 minus line 76" has no floor). The checked sum is the
    # amount line 77 reads, and it is not a form line.
    assert (
        registry.get("ca/amt_non_deductible_office_expenses_checked")
        is AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED
    )
    assert AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED is not AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES
    assert AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED.value_type is Decimal
    assert AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED.non_negative is True


def test_the_part_2_and_part_8_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/amt_credits_total") is AMT_CREDITS_TOTAL
    assert (
        registry.get("ca/amt_tax_payable_before_minimum_tax_carryover")
        is AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER
    )
    assert registry.get("ca/amt_basic_federal_tax") is AMT_BASIC_FEDERAL_TAX
    assert (
        registry.get("ca/amt_minimum_tax_carryover_from_previous_years")
        is AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS
    )
    assert (
        registry.get("ca/amt_tax_payable_with_itc_recapture") is AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE
    )
    assert (
        registry.get("ca/amt_split_income_and_credits_total") is AMT_SPLIT_INCOME_AND_CREDITS_TOTAL
    )
    assert registry.get("ca/amt_tax_payable_after_credits") is AMT_TAX_PAYABLE_AFTER_CREDITS
    assert registry.get("ca/amt_maximum_carryover_applied") is AMT_MAXIMUM_CARRYOVER_APPLIED
    assert registry.get("ca/amt_maximum_carryover_claim") is AMT_MAXIMUM_CARRYOVER_CLAIM
    assert registry.get("ca/amt_minimum_tax_carryover_applied") is AMT_MINIMUM_TAX_CARRYOVER_APPLIED
    assert (
        registry.get("ca/amt_minimum_tax_carryover_within_maximum")
        is AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM
    )


def test_the_part_3_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/amt_federal_surtax_at_48_percent") is AMT_FEDERAL_SURTAX_AT_48_PERCENT
    assert registry.get("ca/amt_t2203_column_5_percentage") is AMT_T2203_COLUMN_5_PERCENTAGE
    assert (
        registry.get("ca/amt_federal_surtax_multiple_jurisdictions")
        is AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS
    )
    assert (
        registry.get("ca/amt_federal_surtax_if_non_resident") is AMT_FEDERAL_SURTAX_IF_NON_RESIDENT
    )
    assert registry.get("ca/amt_federal_surtax") is AMT_FEDERAL_SURTAX
    assert (
        registry.get("ca/amt_federal_tax_with_surtax_and_recapture")
        is AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE
    )
    assert (
        registry.get("ca/amt_foreign_and_logging_credits_total")
        is AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL
    )
    assert registry.get("ca/amt_federal_tax_payable") is AMT_FEDERAL_TAX_PAYABLE
    assert registry.get("ca/amt_investment_tax_credit_claim") is AMT_INVESTMENT_TAX_CREDIT_CLAIM
    assert registry.get("ca/amt_investment_tax_credit") is AMT_INVESTMENT_TAX_CREDIT
    assert registry.get("ca/amt_regular_tax_credits_total") is AMT_REGULAR_TAX_CREDITS_TOTAL
    assert (
        registry.get("ca/amt_regular_net_federal_tax_payable")
        is AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE
    )


def test_the_t2203_column_5_percentage_maximum_and_checked_kinds_are_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 3 line 3 "multiply the amount from line 2 by the percentage in Column 5 of line
    # 52220 on Form T2203" is refused above 100 (a choice: the form prints no maximum). The maximum
    # is a credit dataset's 100; the checked percentage is the output of `core/at_most`, which the
    # readers of the percentage read in place of the input.
    assert (
        registry.kind("ca/amt_t2203_column_5_percentage_maximum")
        is AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM
    )
    assert (
        registry.kind("ca/amt_t2203_column_5_percentage_checked")
        is AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED
    )
    for kind in (AMT_T2203_COLUMN_5_PERCENTAGE_MAXIMUM, AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
    assert AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED is not AMT_T2203_COLUMN_5_PERCENTAGE


def test_the_checked_lines_17_39_40_41_and_42_are_registered_beside_their_inputs(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 17 "Part of total capital gains included on line 15 that is exempt from
    # Canadian tax under a tax treaty" is at most line 15 (`capital_gain`). Lines 39 or 40 (the
    # difference of the limited partnership losses), 41 and 42 are "the difference between those
    # losses and the losses that are deductible for AMT purposes", so each is at most the losses of
    # other years claimed on T1 line 25100, 25200 or 25300 (line 46 is the sum of lines 39 and 40).
    # An amount above its bound is an input error, not capped; the checked amount is the output of
    # `core/at_most`, which the lines that read it take in place of the input.
    checked = (
        (
            "ca/amt_treaty_exempt_capital_gains_checked",
            AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED,
            AMT_TREATY_EXEMPT_CAPITAL_GAINS,
        ),
        (
            "ca/amt_limited_partnership_difference_applied_checked",
            AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED_CHECKED,
            AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED,
        ),
        (
            "ca/amt_non_capital_losses_difference_checked",
            AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
            AMT_NON_CAPITAL_LOSSES_DIFFERENCE,
        ),
        (
            "ca/amt_net_capital_losses_difference_checked",
            AMT_NET_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
            AMT_NET_CAPITAL_LOSSES_DIFFERENCE,
        ),
    )
    for identifier, checked_kind, input_kind in checked:
        assert registry.kind(identifier) is checked_kind, identifier
        assert checked_kind.value_type is Decimal, identifier
        assert checked_kind.non_negative is True, identifier
        assert checked_kind is not input_kind, identifier


def test_the_treaty_exempt_gains_within_additional_deductions_kind_is_registered_beside_its_input(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 17 "(included on line 25600 of your return)": the checked amount is at
    # most line 25600 "Additional deductions" (`ca/additional_deductions`), which the return deducts
    # it in, so an amount above it is refused, not capped. Line 19 reads this amount in place of
    # the checked amount, which is its input.
    kind = registry.kind("ca/amt_treaty_exempt_capital_gains_within_additional_deductions")
    assert kind is AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS
    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert kind is not AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED


def test_the_line_15_not_below_zero_kind_is_registered_beside_the_line_17_input(
    registry: ArtifactRegistry,
) -> None:
    # Not a form line: Part 1 line 15 with a loss taken as 0, the bound of line 17, so a loss on
    # line 15 still accepts an amount of 0.
    kind = registry.kind("ca/amt_capital_gain_not_below_zero")
    assert kind is AMT_CAPITAL_GAIN_NOT_BELOW_ZERO
    assert kind.value_type is Decimal
    assert kind.non_negative is True


def test_the_lines_39_and_40_both_counts_are_registered_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 "complete line 39 or 40 depending on your situation": the count of the two
    # lines both above 0, and its checked count, which refuses a 1 (an input error, not capped).
    for identifier, kind in (
        ("ca/amt_lines_39_and_40_both", AMT_LINES_39_AND_40_BOTH),
        ("ca/amt_lines_39_and_40_both_checked", AMT_LINES_39_AND_40_BOTH_CHECKED),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
        assert identifier in COUNTS
    assert AMT_LINES_39_AND_40_BOTH_CHECKED is not AMT_LINES_39_AND_40_BOTH


def test_the_line_22100_and_part_9_checks_are_registered_beside_their_inputs(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 lines 10 and 64 to 67 "(included on line 22100 of your return)", their sum
    # at most the Federal Worksheet's line 22100, and Part 9 line 1 "(included on lines 22100,
    # 22400, and 23200 of your return)", at most the sum of those three lines. The checked amounts
    # are the inputs read after the checks, and the sums are not form lines.
    pairs: tuple[tuple[str, ArtifactKind[Any]], ...] = (
        ("ca/amt_expenses_included_on_line_22100", AMT_EXPENSES_INCLUDED_ON_LINE_22100),
        (
            "ca/amt_expenses_included_on_line_22100_checked",
            AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED,
        ),
        ("ca/amt_lines_22100_22400_and_23200", AMT_LINES_22100_22400_AND_23200),
        ("ca/amt_resource_expenditures_checked", AMT_RESOURCE_EXPENDITURES_CHECKED),
    )
    for identifier, kind in pairs:
        assert registry.get(identifier) is kind, identifier
        assert kind.value_type is Decimal, identifier
        assert kind.non_negative is True, identifier
    assert AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED is not AMT_EXPENSES_INCLUDED_ON_LINE_22100
    assert AMT_RESOURCE_EXPENDITURES_CHECKED is not AMT_RESOURCE_EXPENDITURES


def test_the_ppip_premiums_in_ontario_counts_are_registered_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 59 "(Quebec only)": the count of line 59 above 0 for a resident of
    # Ontario, and its checked count, which refuses a 1 (an input error, not capped).
    for identifier, kind in (
        ("ca/amt_ppip_premiums_in_ontario", AMT_PPIP_PREMIUMS_IN_ONTARIO),
        ("ca/amt_ppip_premiums_in_ontario_checked", AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
        assert identifier in COUNTS
    assert AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED is not AMT_PPIP_PREMIUMS_IN_ONTARIO


def test_the_part_3_counts_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in PART_3_COUNTS:
        assert registry.get(kind.identifier) is kind
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier in COUNTS


def test_the_part_4_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/amt_capital_gains_added_not_below_zero")
        is AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO
    )
    assert registry.get("ca/amt_foreign_business_income") is AMT_FOREIGN_BUSINESS_INCOME
    assert registry.get("ca/amt_foreign_non_business_income") is AMT_FOREIGN_NON_BUSINESS_INCOME
    assert (
        registry.get("ca/amt_foreign_capital_gains_non_taxable_claim")
        is AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE_CLAIM
    )
    assert (
        registry.get("ca/amt_foreign_capital_gains_non_taxable")
        is AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE
    )
    assert registry.get("ca/amt_total_foreign_income") is AMT_TOTAL_FOREIGN_INCOME
    assert registry.get("ca/amt_foreign_income_limit") is AMT_FOREIGN_INCOME_LIMIT
    assert (
        registry.get("ca/amt_foreign_non_business_tax_paid_before_excess")
        is AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS
    )
    assert registry.get("ca/amt_foreign_non_business_tax_paid") is AMT_FOREIGN_NON_BUSINESS_TAX_PAID
    assert (
        registry.get("ca/amt_foreign_non_business_tax_two_thirds")
        is AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS
    )
    assert registry.get("ca/amt_foreign_business_tax_paid") is AMT_FOREIGN_BUSINESS_TAX_PAID
    assert registry.get("ca/amt_foreign_taxes_paid") is AMT_FOREIGN_TAXES_PAID
    assert registry.get("ca/amt_foreign_tax_credit_lesser") is AMT_FOREIGN_TAX_CREDIT_LESSER
    assert registry.get("ca/amt_special_foreign_tax_credit") is AMT_SPECIAL_FOREIGN_TAX_CREDIT


def test_the_part_5_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/amt_net_minimum_tax_payable") is AMT_NET_MINIMUM_TAX_PAYABLE
    assert registry.get("ca/amt_regular_net_tax_less_surtax") is AMT_REGULAR_NET_TAX_LESS_SURTAX
    assert registry.get("ca/amt_minimum_tax_after_regular_tax") is AMT_MINIMUM_TAX_AFTER_REGULAR_TAX
    assert (
        registry.get("ca/amt_investment_tax_credit_less_part_d")
        is AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D
    )
    assert (
        registry.get("ca/amt_alternative_minimum_tax_payable")
        is AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE
    )


def test_the_part_5_counts_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in PART_5_COUNTS:
        assert registry.get(kind.identifier) is kind


def test_the_part_5_line_11_is_positive_count_is_a_non_negative_whole_number() -> None:
    # Form T691 Part 5 line 11 "If line 11 is positive, complete parts 6 and 7.": the condition
    # "line 11 is positive" is a count of 1 or 0, not an amount, and it is never negative.
    assert AMT_PART_5_LINE_11_IS_POSITIVE.identifier == "ca/amt_part_5_line_11_is_positive"
    assert AMT_PART_5_LINE_11_IS_POSITIVE.value_type is int
    assert AMT_PART_5_LINE_11_IS_POSITIVE.non_negative is True
    assert Artifact(AMT_PART_5_LINE_11_IS_POSITIVE, 1).value == 1


def test_the_part_6_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/amt_basic_federal_tax_less_split_income_tax")
        is AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX
    )
    assert (
        registry.get("ca/amt_greater_of_basic_tax_and_minimum_amount")
        is AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT
    )
    assert registry.get("ca/amt_federal_tax_under_minimum_tax") is AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX
    assert registry.get("ca/amt_part_6_surtax_at_48_percent") is AMT_PART_6_SURTAX_AT_48_PERCENT
    assert (
        registry.get("ca/amt_part_6_surtax_multiple_jurisdictions")
        is AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS
    )
    assert registry.get("ca/amt_part_6_surtax_if_non_resident") is AMT_PART_6_SURTAX_IF_NON_RESIDENT
    assert registry.get("ca/amt_part_6_federal_surtax") is AMT_PART_6_FEDERAL_SURTAX
    assert registry.get("ca/amt_part_6_tax_with_surtax") is AMT_PART_6_TAX_WITH_SURTAX
    assert (
        registry.get("ca/amt_federal_tax_payable_under_minimum_tax")
        is AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX
    )


def test_the_part_6_counts_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in PART_6_COUNTS:
        assert registry.get(kind.identifier) is kind


def test_the_part_7_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert (
        registry.get("ca/amt_part_7_basic_tax_with_recapture")
        is AMT_PART_7_BASIC_TAX_WITH_RECAPTURE
    )
    assert registry.get("ca/amt_part_7_credits_total") is AMT_PART_7_CREDITS_TOTAL
    assert registry.get("ca/amt_part_7_tax_less_credits") is AMT_PART_7_TAX_LESS_CREDITS
    assert (
        registry.get("ca/amt_part_7_foreign_credit_difference")
        is AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE
    )
    assert registry.get("ca/amt_part_7_foreign_taxes_paid") is AMT_PART_7_FOREIGN_TAXES_PAID
    assert registry.get("ca/amt_part_7_foreign_credit_share") is AMT_PART_7_FOREIGN_CREDIT_SHARE
    assert (
        registry.get("ca/amt_part_7_tax_less_credits_plus_share")
        is AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE
    )
    assert (
        registry.get("ca/amt_additional_taxes_for_carryover") is AMT_ADDITIONAL_TAXES_FOR_CARRYOVER
    )


def test_the_part_8_kinds_after_line_12_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/amt_part_8_additional_taxes") is AMT_PART_8_ADDITIONAL_TAXES
    assert registry.get("ca/amt_carryover_balance") is AMT_CARRYOVER_BALANCE
    assert (
        registry.get("ca/amt_carryover_balance_with_additional_taxes")
        is AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES
    )
    assert registry.get("ca/amt_unapplied_2018_carryover") is AMT_UNAPPLIED_2018_CARRYOVER
    assert (
        registry.get("ca/amt_unapplied_2018_carryover_checked")
        is AMT_UNAPPLIED_2018_CARRYOVER_CHECKED
    )
    assert AMT_UNAPPLIED_2018_CARRYOVER_CHECKED is not AMT_UNAPPLIED_2018_CARRYOVER
    assert AMT_UNAPPLIED_2018_CARRYOVER_CHECKED.value_type is Decimal
    assert AMT_UNAPPLIED_2018_CARRYOVER_CHECKED.non_negative is True
    assert registry.get("ca/amt_carryover_available_for_2026") is AMT_CARRYOVER_AVAILABLE_FOR_2026


def test_the_alternative_minimum_tax_module_declares_no_amt_box_kind() -> None:
    assert not hasattr(
        tax_engine.jurisdictions.ca.catalog.alternative_minimum_tax,
        "AMT_T4_SECURITY_OPTIONS_BOXES_39_AND_91",
    )
    assert not hasattr(
        tax_engine.jurisdictions.ca.catalog.alternative_minimum_tax,
        "AMT_T4_SECURITY_OPTIONS_BOXES_41_AND_92",
    )


def test_the_alternative_minimum_tax_kinds_are_money() -> None:
    for kind in (
        PART_1_KINDS
        + PART_9_KINDS
        + SECURITY_OPTIONS_KINDS
        + LOSSES_AND_DEDUCTIONS_KINDS
        + NON_DEDUCTIBLE_AND_RATE_KINDS
        + PART_2_AND_8_KINDS
        + PART_3_KINDS
        + PART_4_KINDS
        + PART_5_KINDS
        + PART_6_KINDS
        + PART_7_KINDS
        + PART_8_KINDS
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_bracketed_lines_are_signed_and_the_rest_are_not_below_zero() -> None:
    for kind in (
        PART_1_KINDS
        + PART_9_KINDS
        + SECURITY_OPTIONS_KINDS
        + LOSSES_AND_DEDUCTIONS_KINDS
        + NON_DEDUCTIBLE_AND_RATE_KINDS
        + PART_2_AND_8_KINDS
        + PART_3_KINDS
        + PART_4_KINDS
        + PART_5_KINDS
        + PART_6_KINDS
        + PART_7_KINDS
        + PART_8_KINDS
    ):
        assert kind.non_negative is (kind.identifier not in SIGNED), kind.identifier


def test_the_amt_part_1_subtotal_is_signed_because_its_line_1_is(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 12 "Add lines 1, 4, 7, and 11." takes
    # line 1, the signed taxable income of `ca/taxable_income_signed`, so the subtotal can be
    # negative and is declared signed.
    assert AMT_PART_1_SUBTOTAL.non_negative is False
    assert registry.get("ca/amt_part_1_subtotal") is AMT_PART_1_SUBTOTAL
    assert registry.kind("ca/amt_part_1_subtotal").non_negative is False
    assert "ca/amt_part_1_subtotal" in SIGNED


def test_the_federal_surtax_at_48_percent_holds_a_negative_base() -> None:
    # Part 3 line 2, "Multiply the amount from line 1 by 48%.", with line 1 the basic federal tax,
    # which is negative when the credits exceed the tax: 48% of a negative amount is negative,
    # and the kind holds it, as the form prints no floor.
    assert Artifact(AMT_FEDERAL_SURTAX_AT_48_PERCENT, Decimal("-567.29")).value == Decimal(
        "-567.29"
    )


def test_the_foreign_business_income_holds_a_negative_amount() -> None:
    # Part 4 line 1, "Foreign business income (total business income earned in the foreign country,
    # minus allowable expenses and deductions for the foreign income)": it is net of expenses, so
    # it can be a loss, and the kind holds it; line 4 is then reduced by it.
    assert Artifact(AMT_FOREIGN_BUSINESS_INCOME, Decimal("-300")).value == Decimal("-300")


def test_the_federal_tax_under_minimum_tax_holds_a_negative_amount() -> None:
    # Part 6 line 7, "Line 5 plus line 6 (14)": line 6 is the amount from line 22 of Form T1206, a
    # signed figure, so the sum can be negative; the form prints no floor on it, and the kind holds
    # it.
    assert Artifact(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX, Decimal("-2104.82")).value == Decimal(
        "-2104.82"
    )


def test_the_federal_tax_payable_under_minimum_tax_refuses_a_negative_amount() -> None:
    # Part 6 line 14, "Enter whichever is more: amount from line 12 or line 13.": line 13 is the
    # amount from line 24 of Form T1206, which is not below zero, so the greater of the two is not
    # negative; a negative figure is an input error, refused and not taken as 0.
    with pytest.raises(
        NegativeArtifactError,
        match="ca/amt_federal_tax_payable_under_minimum_tax cannot be negative",
    ):
        Artifact(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX, Decimal("-1"))


def test_the_part_7_basic_tax_with_recapture_holds_a_negative_amount() -> None:
    # Part 7 line 4, "Line 2 plus line 3": line 2 is the basic federal tax of Part 2 line 7, which
    # is negative when the credits exceed the tax, so the sum can be negative; the form prints no
    # floor on it, and the kind holds it.
    assert Artifact(AMT_PART_7_BASIC_TAX_WITH_RECAPTURE, Decimal("-512.40")).value == Decimal(
        "-512.40"
    )


def test_the_part_7_tax_less_credits_holds_a_negative_amount() -> None:
    # Part 7 line 8, "Line 4 minus line 7": the form prints no floor, so a credit above the tax
    # gives a negative difference, and the kind holds it.
    assert Artifact(AMT_PART_7_TAX_LESS_CREDITS, Decimal("-80.00")).value == Decimal("-80.00")


def test_the_carryover_available_for_2026_holds_a_negative_amount() -> None:
    # Part 8 line 17, "Total minimum tax carryover available for 2026: line 15 minus line 16": the
    # form prints no floor, so an unapplied 2018 carryover above line 15 gives a negative total.
    assert Artifact(AMT_CARRYOVER_AVAILABLE_FOR_2026, Decimal("-25.00")).value == Decimal("-25.00")


def test_the_unapplied_2018_carryover_refuses_a_negative_amount() -> None:
    # Part 8 line 16, "unapplied 2018 minimum tax carryover": the caller's figure is never below
    # zero, so a negative figure is an input error, refused and not taken as 0.
    with pytest.raises(
        NegativeArtifactError, match="ca/amt_unapplied_2018_carryover cannot be negative"
    ):
        Artifact(AMT_UNAPPLIED_2018_CARRYOVER, Decimal("-1"))


def test_the_part_7_foreign_credit_share_refuses_a_negative_amount() -> None:
    # Part 7 line 12, "Line 11 × [...] / [...]": line 11 is not below zero and the share is the
    # product over the denominator, so a negative share is an input error, refused and not 0.
    with pytest.raises(
        NegativeArtifactError, match="ca/amt_part_7_foreign_credit_share cannot be negative"
    ):
        Artifact(AMT_PART_7_FOREIGN_CREDIT_SHARE, Decimal("-1"))


def test_the_amt_non_resident_or_deemed_resident_checked_is_a_non_negative_count(
    registry: ArtifactRegistry,
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before Form T691 Part 3 line 4 and Part 6
    # line 11 read it; the raw answer stays beside it.
    assert (
        registry.get("ca/amt_non_resident_or_deemed_resident_checked")
        is AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED
    )
    assert (
        registry.get("ca/amt_non_resident_or_deemed_resident")
        is AMT_NON_RESIDENT_OR_DEEMED_RESIDENT
    )
    assert AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED.value_type is int
    assert AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED.non_negative is True
