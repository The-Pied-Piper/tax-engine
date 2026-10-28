"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.greater_of import GreaterOf
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.capabilities.times_count import TimesCount
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_calculator.jurisdictions.ca.capabilities.foreign_business_tax_paid_total import (
    ForeignBusinessTaxPaidTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.foreign_net_non_business_income_total import (
    ForeignNetNonBusinessIncomeTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.foreign_non_business_tax_paid_total import (
    ForeignNonBusinessTaxPaidTotal,
)
from tax_calculator.jurisdictions.ca.capabilities.sign_chosen_difference import SignChosenDifference
from tax_calculator.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_calculator.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS_TOTAL,
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
    AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS,
    AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED,
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
    CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
    CAPITAL_GAIN,
    CAPITAL_GAINS_DEDUCTION,
    CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
    CHILD_CARE_EXPENSES,
    CLERGY_RESIDENCE_DEDUCTION,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    CREDITS_AGAINST_FEDERAL_TAX,
    DISABILITY_SUPPORTS_DEDUCTION,
    DIVIDEND_TAX_CREDIT,
    DONATIONS_AND_GIFTS_CREDIT,
    EXPLORATION_AND_DEVELOPMENT_EXPENSES,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_LOGGING_TAX_CREDIT,
    FEDERAL_TAX_ON_SPLIT_INCOME,
    FEDERAL_TAX_WITH_SPLIT_INCOME,
    FOREIGN_PROPERTY_TAX_OVER_LIMIT,
    FOREIGN_TAX_COUNTRIES,
    INVESTMENT_TAX_CREDIT,
    ITC_AMOUNT_I,
    ITC_RECAPTURE,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
    MOVING_EXPENSES_DEDUCTION,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NON_CAPITAL_LOSSES_ON_LINE_25200,
    NON_REFUNDABLE_TAX_CREDITS,
    NORTHERN_RESIDENTS_DEDUCTIONS,
    OTHER_DEDUCTIONS,
    OTHER_EMPLOYMENT_EXPENSES,
    OTHER_FORECLOSURE_GAIN_OR_LOSS,
    POLITICAL_CREDIT,
    QBT_CAPITAL_GAINS_DEDUCTION,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_24,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_INCOME_SIGNED,
    TOTAL_SPLIT_INCOME,
    UNION_DUES,
)
from tax_calculator.jurisdictions.ca_on.catalog import NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED

INPUTS = frozenset(
    {
        "ca/amt_film_property_cca_and_carrying_charges",
        "ca/amt_film_property_income_before_cca",
        "ca/amt_rental_property_cca_and_carrying_charges",
        "ca/amt_rental_property_income_before_cca",
        "ca/amt_tax_shelter_losses",
        "ca/amt_tax_shelter_deductible_amounts",
        "ca/amt_limited_partner_carrying_charges",
        "ca/amt_resource_expenditures",
        "ca/amt_resource_production_income",
        "ca/amt_resource_foreign_property_income",
        "ca/amt_class_43_1_income",
        "ca/amt_treaty_exempt_capital_gains",
        "ca/amt_graduated_rate_estate_capital_gains",
        "ca/amt_publicly_listed_gifts_total",
        "ca/amt_publicly_listed_gifts_t1170_line_68231",
        "ca/amt_security_option_publicly_listed_gifts",
        "ca/amt_prospector_or_grubstaker_deduction",
        "ca/amt_deferred_profit_sharing_plan_deduction",
        "ca/amt_limited_partnership_difference_no_election",
        "ca/amt_limited_partnership_difference_election",
        "ca/amt_non_capital_losses_difference",
        "ca/amt_net_capital_losses_difference",
        "ca/amt_ppip_premiums_deduction",
        "ca/amt_non_deductible_interest",
        "ca/amt_life_insurance_premiums_as_collateral",
        "ca/amt_financing_expenses",
        "ca/amt_investment_counsel_fees",
        "ca/amt_commission_employment_expenses",
        "ca/amt_legal_and_accounting_expenses",
        "ca/amt_repayment_of_salary_and_wages",
        "ca/amt_excess_epsp_amounts",
        "ca/amt_forfeited_salary_deferral_amounts",
        "ca/amt_repayment_of_wage_loss_replacement",
        "ca/amt_section_119_former_resident_credit",
        "ca/amt_minimum_tax_carryover_from_previous_years",
        "ca/amt_minimum_tax_carryover_applied",
        "ca/amt_non_resident_or_deemed_resident",
        # Form T2203 Part 2 "If you are subject to minimum tax, do not complete lines 4 to 10." and
        # T1 line 127: the caller's choice, 1 when you are subject to minimum tax (Form T691 Part 3
        # line 4 is then the surtax), else 0.
        "ca/amt_subject_to_minimum_tax",
        "ca/amt_investment_tax_credit_claim",
        "ca/amt_foreign_business_income",
        "ca/amt_foreign_capital_gains_non_taxable_claim",
        "ca/amt_unapplied_2018_carryover",
    }
)

OUTPUTS = frozenset(
    {
        "ca/amt_carryover_available_for_2026",
        "ca/amt_lines_39_and_40_both_checked",
        "ca/amt_ppip_premiums_in_ontario_checked",
        "ca/amt_expenses_included_on_line_22100_checked",
    }
)

STEPS = {
    # Part 1 line 4 "Line 2 minus line 3 (if negative, enter "0")" and "67820 =", the film
    # property's adjustment, line 2 being the caller's CCA and carrying charges and line 3 the
    # caller's net income from film property before CCA.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_film_property_cca_and_carrying_charges",
            "less": "ca/amt_film_property_income_before_cca",
        },
        produces={"output": "ca/amt_film_property_adjustment"},
    ),
    # Part 1 line 7 "Line 5 minus line 6 (if negative, enter "0")" and "67830 =", the rental and
    # leasing property's adjustment, line 5 the caller's CCA and carrying charges and line 6 the
    # caller's net income from rental and leasing property before CCA.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_rental_property_cca_and_carrying_charges",
            "less": "ca/amt_rental_property_income_before_cca",
        },
        produces={"output": "ca/amt_rental_property_adjustment"},
    ),
    # Part 1 line 11 "Add lines 8 to 10." and "67840 =", the tax shelters, limited partnerships and
    # non-active partners: the caller's lines 8, 9 and 10 in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_tax_shelter_losses",
                "ca/amt_tax_shelter_deductible_amounts",
                "ca/amt_limited_partner_carrying_charges",
            )
        },
        produces={"output": "ca/amt_tax_shelter_adjustments"},
    ),
    # Part 1 line 12 "Add lines 1, 4, 7, and 11." (line 1 the taxable income from line 26000 of the
    # return, read from the signed taxable income artifact, `ca/taxable_income_signed`, which is not
    # floored at 0, and lines 4, 7 and 11 in line order).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/taxable_income_signed",
                "ca/amt_film_property_adjustment",
                "ca/amt_rental_property_adjustment",
                "ca/amt_tax_shelter_adjustments",
            )
        },
        produces={"output": "ca/amt_part_1_subtotal"},
    ),
    # Part 9 line 5 "Add lines 2 to 4.", the three income lines of Part 9 in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_resource_production_income",
                "ca/amt_resource_foreign_property_income",
                "ca/amt_class_43_1_income",
            )
        },
        produces={"output": "ca/amt_resource_income_total"},
    ),
    # Part 9 line 6 "Line 1 minus line 5 (if negative, enter "0")" and "Resource property and
    # flow-through share 67860 =", the amount that goes to line 14 of Part 1.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_resource_expenditures_checked",
            "less": "ca/amt_resource_income_total",
        },
        produces={"output": "ca/amt_resource_property_and_flow_through_shares"},
    ),
    # Part 1 line 16 "Capital gains or losses arising from mortgage foreclosures and conditional
    # sales repossessions from lines 12400 and 15500 of Schedule 3", the two foreclosure totals
    # of Schedule 3, a loss in brackets.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/qffp_foreclosure_gain_or_loss",
                "ca/other_foreclosure_gain_or_loss",
            )
        },
        produces={"output": "ca/amt_mortgage_foreclosure_capital_gains"},
    ),
    # Part 1 line 17 "Part of total capital gains included on line 15 that is exempt from Canadian
    # tax under a tax treaty", at most line 15 (`capital_gain`) with a loss taken as 0, so that a
    # loss on line 15 refuses no amount of 0 (not a form line, as for Part 4 line 3). An amount
    # above it is an input error, not capped. The checked amount is the one line 19 reads.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/capital_gain",)},
        produces={"output": "ca/amt_capital_gain_not_below_zero"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_treaty_exempt_capital_gains",
            "bound": "ca/amt_capital_gain_not_below_zero",
        },
        produces={"output": "ca/amt_treaty_exempt_capital_gains_checked"},
    ),
    # Form T691 Part 1 line 17 "Part of total capital gains included on line 15 that is exempt from
    # Canadian tax under a tax treaty (included on line 25600 of your return)": the checked amount
    # is at most line 25600 "Additional deductions" (`ca/additional_deductions_total`), which the
    # return
    # deducts it in. An amount above it is refused, not capped. Line 19 reads the amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_treaty_exempt_capital_gains_checked",
            "bound": "ca/additional_deductions_total",
        },
        produces={"output": "ca/amt_treaty_exempt_capital_gains_within_additional_deductions"},
    ),
    # Part 1 line 19 "Add lines 16 to 18.", lines 16, 17 and 18 in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_mortgage_foreclosure_capital_gains",
                "ca/amt_treaty_exempt_capital_gains_within_additional_deductions",
                "ca/amt_graduated_rate_estate_capital_gains",
            )
        },
        produces={"output": "ca/amt_capital_gains_adjustments"},
    ),
    # Part 1 line 20 "Line 15 minus line 19 (if negative, show in brackets)", the capital gains
    # of line 15 (`capital_gain`, from line 19700 of Schedule 3) less line 19.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gain",
            "less": "ca/amt_capital_gains_adjustments",
        },
        produces={"output": "ca/amt_net_capital_gains_after_adjustments"},
    ),
    # Part 1 line 22 "Line 20 minus line 21 (if negative, do not show in brackets.)", line 21 the
    # amount from line 12700 of the return (the taxable capital gains), left signed here.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_net_capital_gains_after_adjustments",
            "less": "ca/taxable_capital_gains",
        },
        produces={"output": "ca/amt_capital_gains_difference"},
    ),
    # Part 1 line 23 "If line 20 is positive, enter the amount from line 22. If line 20 is negative,
    # enter whichever is less: the amount from line 21 or line 22 (show in brackets).", picked by
    # the sign of line 20.
    CapabilitySelection(
        name="ca/sign_chosen_difference",
        params={},
        consumes={
            "sign_amount": "ca/amt_net_capital_gains_after_adjustments",
            "reference": "ca/taxable_capital_gains",
            "difference": "ca/amt_capital_gains_difference",
        },
        produces={"output": "ca/amt_capital_gains_added"},
    ),
    # Part 1 line 26 "Line 24 minus line 25", the net of the gifts before the 30% of line 26.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_publicly_listed_gifts_total",
            "less": "ca/amt_publicly_listed_gifts_t1170_line_68231",
        },
        produces={"output": "ca/amt_publicly_listed_gifts_net"},
    ),
    # Part 1 line 26 "× 30%" of "Line 24 minus line 25", the rate from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/publicly_listed_gifts_rate"},
        consumes={"base": "ca/amt_publicly_listed_gifts_net"},
        produces={"output": "ca/amt_publicly_listed_gifts_adjustment"},
    ),
    # Part 1 line 27 "Add lines 13, 14, 23, and 26.", line 13 the amount from line 12 and line 14
    # the amount from line 6 of Part 9, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_part_1_subtotal",
                "ca/amt_resource_property_and_flow_through_shares",
                "ca/amt_capital_gains_added",
                "ca/amt_publicly_listed_gifts_adjustment",
            )
        },
        produces={"output": "ca/amt_adjusted_income_with_gains"},
    ),
    # Part 1 line 30 "Line 28 plus line 29" and "67910 =", the security options deduction under
    # paragraph 110(1)(d): the total of the T4 slips' boxes 39 and 91 (line 28, the total of the
    # fact `ca/security_options_boxes_39_and_91`) and the T1212 amount (line 29).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t4_security_options_boxes_39_and_91_total",
                "ca/amt_t1212_line_29_deferred_security_options",
            )
        },
        produces={"output": "ca/amt_security_options_d_total"},
    ),
    # Part 1 line 31 "× 40%" of "Gifts of publicly listed securities acquired under a security
    # option plan included on line 24900 of your return" "67914", the rate from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/security_option_gifts_rate"},
        consumes={"base": "ca/amt_security_option_publicly_listed_gifts"},
        produces={"output": "ca/amt_security_option_gifts_deduction"},
    ),
    # Part 1 line 32 "Line 30 minus line 31 (if negative, enter "0")", not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_security_options_d_total",
            "less": "ca/amt_security_option_gifts_deduction",
        },
        produces={"output": "ca/amt_security_options_net"},
    ),
    # Part 1 line 38 "Add lines 35 to 37." and "67918 =", lines 35, 36 and 37 in line order; line 35
    # is the total of the T4 slips' boxes 41 and 92 (the fact
    # `ca/security_options_boxes_41_and_92`).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t4_security_options_boxes_41_and_92_total",
                "ca/amt_prospector_or_grubstaker_deduction",
                "ca/amt_deferred_profit_sharing_plan_deduction",
            )
        },
        produces={"output": "ca/amt_security_options_d1_total"},
    ),
    # Part 1 line 41 "the difference between those losses and the losses that are deductible for AMT
    # purposes" is at most the non-capital losses of other years claimed on line 25200 of the return
    # (`ca/non_capital_losses_on_line_25200`): an amount above it is an input error, not capped.
    # Line 42 is the same for the net capital losses of line 25300, which has no line 45
    # counterpart. The checked amounts are read by line 43 (lines 41 and 42), and line 41's by
    # line 50.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_non_capital_losses_difference",
            "bound": "ca/non_capital_losses_on_line_25200",
        },
        produces={"output": "ca/amt_non_capital_losses_difference_checked"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_net_capital_losses_difference",
            "bound": "ca/net_capital_losses_of_other_years",
        },
        produces={"output": "ca/amt_net_capital_losses_difference_checked"},
    ),
    # Part 1 line 43 "Line 39 or 40, as applicable, plus line 41 and 42", the one of lines 39 and 40
    # that applies (the other is blank) with lines 41 and 42, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_limited_partnership_difference_no_election",
                "ca/amt_limited_partnership_difference_election",
                "ca/amt_non_capital_losses_difference_checked",
                "ca/amt_net_capital_losses_difference_checked",
            )
        },
        produces={"output": "ca/amt_other_years_losses_total"},
    ),
    # Part 1 line 46 "Amount from line 39 or 40, as applicable", the one of lines 39 and 40 that
    # applies. Lines 39 and 40 are the difference of the limited partnership losses, so the amount
    # is at most line 25100 (`limited_partnership_losses_of_other_years`), not capped.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_limited_partnership_difference_no_election",
                "ca/amt_limited_partnership_difference_election",
            )
        },
        produces={"output": "ca/amt_limited_partnership_difference_applied"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_limited_partnership_difference_applied",
            "bound": "ca/limited_partnership_losses_of_other_years_checked",
        },
        produces={"output": "ca/amt_limited_partnership_difference_applied_checked"},
    ),
    # Part 1 line 47 "Line 45 minus line 46", the limited partnership losses of other years (line
    # 25100 of the return, read from its artifact) less line 46, a loss in brackets.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/limited_partnership_losses_of_other_years_checked",
            "less": "ca/amt_limited_partnership_difference_applied_checked",
        },
        produces={"output": "ca/amt_limited_partnership_losses_adjustment"},
    ),
    # Part 1 line 50 "Line 48 minus line 49", the non-capital losses of other years (line 25200 of
    # the return, read from its artifact) less line 49, the amount from line 41.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/non_capital_losses_on_line_25200",
            "less": "ca/amt_non_capital_losses_difference_checked",
        },
        produces={"output": "ca/amt_non_capital_losses_adjustment"},
    ),
    # Part 1 line 53 "Add lines 47, 50, 51, and 52.", line 51 the union dues of line 21200 of the
    # return and line 52 the child care expenses of line 21400, read from their artifacts.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_limited_partnership_losses_adjustment",
                "ca/amt_non_capital_losses_adjustment",
                "ca/union_dues",
                "ca/child_care_expenses",
            )
        },
        produces={"output": "ca/amt_losses_and_deductions_subtotal"},
    ),
    # Part 1 line 63 "Add lines 54 to 62.", line 53 carried and lines 55 to 62 in line order: the
    # deductions of the return on lines 21500 (the amount computed on Form T929 line 12),
    # 21900 (the moving expenses deduction of Form T1-M), 22200, 22215, 22300 (a caller's amount),
    # 23100, 24400 and 25500.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_losses_and_deductions_subtotal",
                "ca/disability_supports_deduction",
                "ca/moving_expenses_deduction",
                "ca/cpp_deduction_on_self_employment_and_other_earnings",
                "ca/cpp_enhanced_contributions_on_return",
                "ca/amt_ppip_premiums_deduction",
                "ca/clergy_residence_deduction",
                "ca/canadian_armed_forces_and_police_deduction",
                "ca/northern_residents_deductions",
            )
        },
        produces={"output": "ca/amt_deductions_total"},
    ),
    # Part 1 line 68 "Add lines 64 to 67 (11)", the non-deductible property expenses, lines 64 to 67
    # in line order (caller's amounts).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_non_deductible_interest",
                "ca/amt_life_insurance_premiums_as_collateral",
                "ca/amt_financing_expenses",
                "ca/amt_investment_counsel_fees",
            )
        },
        produces={"output": "ca/amt_non_deductible_property_expenses"},
    ),
    # Part 1 line 76 "Add lines 70 to 75." and "67926 =", lines 70 to 75 in line order (caller's
    # amounts).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_commission_employment_expenses",
                "ca/amt_legal_and_accounting_expenses",
                "ca/amt_repayment_of_salary_and_wages",
                "ca/amt_excess_epsp_amounts",
                "ca/amt_forfeited_salary_deferral_amounts",
                "ca/amt_repayment_of_wage_loss_replacement",
            )
        },
        produces={"output": "ca/amt_non_deductible_office_expenses"},
    ),
    # Part 1 line 76 is at most line 69 (`ca/other_employment_expenses`, line 22900 of the return):
    # "Line 69 minus line 76" has no floor, so lines 70 to 75 are parts of line 69, and an amount
    # above it is an input error, not capped. Line 77 reads the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_non_deductible_office_expenses",
            "bound": "ca/other_employment_expenses",
        },
        produces={"output": "ca/amt_non_deductible_office_expenses_checked"},
    ),
    # Part 1 line 77 "Line 69 minus line 76", line 69 the other employment expenses of line 22900
    # of the return, read from its artifact, less line 76 (its checked amount), a loss in brackets.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/other_employment_expenses",
            "less": "ca/amt_non_deductible_office_expenses_checked",
        },
        produces={"output": "ca/amt_office_expenses_adjustment"},
    ),
    # Part 1 line 78 "Add lines 63, 68, and 77.", lines 63, 68 and 77 in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_deductions_total",
                "ca/amt_non_deductible_property_expenses",
                "ca/amt_office_expenses_adjustment",
            )
        },
        produces={"output": "ca/amt_adjustments_before_rate_total"},
    ),
    # Part 1 line 80 "Line 78 multiply by the percentage from line 79", the applicable rate of
    # line 79 "Applicable Rate" "50%" from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_applicable_rate"},
        consumes={"base": "ca/amt_adjustments_before_rate_total"},
        produces={"output": "ca/amt_applicable_rate_amount"},
    ),
    # Part 1 line 33 "Line 27 plus line 32".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_adjusted_income_with_gains",
                "ca/amt_security_options_net",
            )
        },
        produces={"output": "ca/amt_adjusted_income_with_security_options"},
    ),
    # Part 1 line 44 "Add lines 34, 38, and 43.", line 34 the amount from line 33, then lines 38
    # and 43, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_adjusted_income_with_security_options",
                "ca/amt_security_options_d1_total",
                "ca/amt_other_years_losses_total",
            )
        },
        produces={"output": "ca/amt_security_options_and_losses_total"},
    ),
    # Part 1 line 82 "Line 80 plus line 81", line 81 the amount from line 44 ("Enter the amount
    # from line 44.").
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_applicable_rate_amount",
                "ca/amt_security_options_and_losses_total",
            )
        },
        produces={"output": "ca/amt_adjustments_after_rate_total"},
    ),
    # Part 1 line 84 "B × 13.0435%", B the taxable dividends other than eligible of line 12010
    # of the return, the printed rate from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_dividends_other_than_eligible_rate"},
        consumes={"base": "ca/taxable_dividends_other_than_eligible"},
        produces={"output": "ca/amt_dividends_other_than_eligible_adjustment"},
    ),
    # Part 1 "Amount A minus Amount B", A the taxable dividends of line 12000 of the return and B
    # the amount of line 12010 of the return.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/taxable_dividends",
            "less": "ca/taxable_dividends_other_than_eligible",
        },
        produces={"output": "ca/amt_amount_a_minus_amount_b"},
    ),
    # Part 1 line 85 "C × 27.5362%", C the amount A minus amount B, the printed rate from its
    # dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_dividends_difference_rate"},
        consumes={"base": "ca/amt_amount_a_minus_amount_b"},
        produces={"output": "ca/amt_dividends_difference_adjustment"},
    ),
    # Part 1 line 86 "Line 84 plus line 85".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_dividends_other_than_eligible_adjustment",
                "ca/amt_dividends_difference_adjustment",
            )
        },
        produces={"output": "ca/amt_dividends_adjustments_total"},
    ),
    # Part 1 line 87 "Enter the amount from line 25400 of your return" "× 40% =", the lifetime
    # capital gains exemption, the printed rate from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_lifetime_exemption_rate"},
        consumes={"base": "ca/capital_gains_deduction"},
        produces={"output": "ca/amt_lifetime_exemption_adjustment"},
    ),
    # Part 1 line 88 "Line 86 plus line 87".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_dividends_adjustments_total",
                "ca/amt_lifetime_exemption_adjustment",
            )
        },
        produces={"output": "ca/amt_adjustments_with_lifetime_exemption_total"},
    ),
    # Part 1 line 89 "Amount from line 25395 of your return" "× 2 =", the amount from line 25395
    # of the return doubled, the printed 2 a fraction, 2/1, as it is above one.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/amt_qbt_capital_gains_deduction_multiplier"},
        consumes={"base": "ca/qbt_capital_gains_deduction"},
        produces={"output": "ca/amt_qbt_capital_gains_deduction_doubled"},
    ),
    # Part 1 line 91 "line 89 minus line 90", line 90 the amount from line 25395 of your return.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_qbt_capital_gains_deduction_doubled",
            "less": "ca/qbt_capital_gains_deduction",
        },
        produces={"output": "ca/amt_qbt_capital_gains_deduction_difference"},
    ),
    # Part 1 line 92 "Line 88 plus line 91".
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_adjustments_with_lifetime_exemption_total",
                "ca/amt_qbt_capital_gains_deduction_difference",
            )
        },
        produces={"output": "ca/amt_capital_gains_deductions_total"},
    ),
    # Part 1 line 93 "Line 83 minus line 92 (if negative, enter "0")", "Adjusted taxable income",
    # line 83 the amount from line 82 of the previous page.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_adjustments_after_rate_total",
            "less": "ca/amt_capital_gains_deductions_total",
        },
        produces={"output": "ca/amt_adjusted_taxable_income"},
    ),
    # Part 1 line 94 "Basic exemption" 177,882.00, a printed amount from its dataset.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/amt_basic_exemption"},
        consumes={},
        produces={"output": "ca/amt_basic_exemption"},
    ),
    # Part 1 line 95 "Line 93 minus line 94 (if negative, enter "0")", "Net adjusted taxable
    # income".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_adjusted_taxable_income",
            "less": "ca/amt_basic_exemption",
        },
        produces={"output": "ca/amt_net_adjusted_taxable_income"},
    ),
    # Part 1 line 97 "Gross minimum amount: line 95 multiplied by the percentage on line 96.", the
    # federal tax rate of line 96, 20.5%, from its dataset.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_federal_tax_rate"},
        consumes={"base": "ca/amt_net_adjusted_taxable_income"},
        produces={"output": "ca/amt_gross_minimum_amount"},
    ),
    # Part 1 line 98 "Net non-refundable tax credits (line 33800 of your return)" "× 50% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_non_refundable_credits_rate"},
        consumes={"base": "ca/credit_amounts_at_credit_rate"},
        produces={"output": "ca/amt_non_refundable_credits_adjustment"},
    ),
    # Part 1 line 99 "Donations and gifts (line 34900 of your return)" "× 80% =".
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_donations_and_gifts_rate"},
        consumes={"base": "ca/donations_and_gifts_credit"},
        produces={"output": "ca/amt_donations_and_gifts_adjustment"},
    ),
    # Part 1 line 102 "Add lines 98 to 101.", line 100 the federal logging tax credit of line 133
    # and line 101 the caller's amount.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_non_refundable_credits_adjustment",
                "ca/amt_donations_and_gifts_adjustment",
                "ca/federal_logging_tax_credit",
                "ca/amt_section_119_former_resident_credit",
            )
        },
        produces={"output": "ca/amt_credits_adjustments_total"},
    ),
    # Part 1 line 103 "Line 97 minus line 102 (if negative, enter "0")", "Minimum amount".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_gross_minimum_amount",
            "less": "ca/amt_credits_adjustments_total",
        },
        produces={"output": "ca/amt_minimum_amount"},
    ),
    # Part 2 line 4 "Line 2 plus line 3": line 2 "Total non-refundable tax credits (line 35000 of
    # your return)" and line 3 "Dividend tax credit (line 40425 of your return)", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/non_refundable_tax_credits", "ca/dividend_tax_credit")},
        produces={"output": "ca/amt_credits_total"},
    ),
    # Part 2 line 5 "Line 1 minus line 4" "Tax payable before minimum tax carryover": line 1 is
    # "Enter the amount from line 40400 of your return", the federal tax with split income, less
    # line 4. The form shows no floor, so the difference may be negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/federal_tax_with_split_income",
            "less": "ca/amt_credits_total",
        },
        produces={"output": "ca/amt_tax_payable_before_minimum_tax_carryover"},
    ),
    # Part 2 line 7 "Line 5 minus line 6" "Basic federal tax": line 6 "Minimum tax carryover applied
    # in 2025 from line 12 of Part 8", the claim of Part 8 line 12, less line 5.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_tax_payable_before_minimum_tax_carryover",
            "less": "ca/amt_minimum_tax_carryover_applied",
        },
        produces={"output": "ca/amt_basic_federal_tax"},
    ),
    # Part 8 line 4 "Line 2 plus line 3": line 2 "Tax payable before minimum tax carryover from line
    # 5 of Part 2" and line 3 "Recapture of investment tax credit from line 3 of Part C of Form
    # T2038(IND)", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_tax_payable_before_minimum_tax_carryover",
                "ca/itc_recapture",
            )
        },
        produces={"output": "ca/amt_tax_payable_with_itc_recapture"},
    ),
    # Part 8 line 8 "Add lines 5 to 7": line 5 "Federal tax on split income from line 8 of Form
    # T1206", line 6 "Federal logging tax credit" (line 133 of your return, as on Part 1 line 100)
    # and line 7 "Amount from line 41600 of your return", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_tax_on_split_income",
                "ca/federal_logging_tax_credit",
                "ca/credits_against_federal_tax",
            )
        },
        produces={"output": "ca/amt_split_income_and_credits_total"},
    ),
    # Part 8 line 9 "Line 4 minus line 8": the form shows no floor, so the difference may be
    # negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_tax_payable_with_itc_recapture",
            "less": "ca/amt_split_income_and_credits_total",
        },
        produces={"output": "ca/amt_tax_payable_after_credits"},
    ),
    # Part 8 line 11 "Maximum carryover that can be applied in 2025: line 9 minus line 10 (if
    # negative, enter "0")", line 10 "Minimum amount from line 103 of Part 1".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_tax_payable_after_credits",
            "less": "ca/amt_minimum_amount",
        },
        produces={"output": "ca/amt_maximum_carryover_applied"},
    ),
    # Part 8 line 12 "Claim an amount that is not more than line 1 or 11, whichever is less.": the
    # cap on the claim, the lesser of line 1 "Minimum tax carryover from previous years (2018 to
    # 2024)" and line 11. Not printed on the form, it is the bound of the claim below.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/amt_minimum_tax_carryover_from_previous_years",
                "ca/amt_maximum_carryover_applied",
            )
        },
        produces={"output": "ca/amt_maximum_carryover_claim"},
    ),
    # Part 8 line 12 "Claim an amount that is not more than line 1 or 11, whichever is less.": the
    # claim the filer enters (`ca/amt_minimum_tax_carryover_applied`, an input) is checked against
    # the cap, and refused above it. Part 8 line 13 reads the checked amount; the lines before it
    # read the claim itself, because line 11 reads line 41600.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_minimum_tax_carryover_applied",
            "bound": "ca/amt_maximum_carryover_claim",
        },
        produces={"output": "ca/amt_minimum_tax_carryover_within_maximum"},
    ),
    # Part 3 line 2 "Federal surtax on business income earned outside Canada" "Multiply the amount
    # from line 1 by 48%.": line 1 is the basic federal tax of Part 2 line 7, the rate from its
    # dataset. The form prints no floor, so a negative basic federal tax gives a negative surtax.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_federal_surtax_rate"},
        consumes={"base": "ca/amt_basic_federal_tax"},
        produces={"output": "ca/amt_federal_surtax_at_48_percent"},
    ),
    # Part 3 line 3 "If you have to pay tax to multiple jurisdictions, multiply the amount from
    # line 2 by the percentage in Column 5 of line 52220 on Form T2203.": the percentage as printed
    # (50 for 50%), the caller's figure, rounded once by its dataset.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/amt_multiple_jurisdictions_rounding"},
        consumes={
            "amount": "ca/amt_federal_surtax_at_48_percent",
            "percentage": "ca/amt_t2203_column_5_percentage_checked",
        },
        produces={"output": "ca/amt_federal_surtax_multiple_jurisdictions"},
    ),
    # Part 3 line 4 "If you have an amount on line 3, enter that amount. If not, and you are a
    # non-resident or deemed resident, enter the amount from line 2. Otherwise, enter "0".": the
    # condition "you have an amount on line 3" counts 1 when line 3 is not 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/amt_line_3_has_amount_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/amt_federal_surtax_multiple_jurisdictions",),
        },
        produces={"output": "ca/amt_line_3_has_amount"},
    ),
    # The caller's answer to "you are a non-resident or deemed resident" (Part 3 line 4), a count
    # of 1 or 0, checked before the second branch reads it. A count of 2 or more is refused, not
    # capped.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/amt_non_resident_or_deemed_resident"},
        produces={"output": "ca/amt_non_resident_or_deemed_resident_checked"},
    ),
    # Part 3 line 4, the second branch: line 2 when "you are a non-resident or deemed resident"
    # (the caller's count, 1 for yes), and "0" otherwise.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/amt_federal_surtax_at_48_percent",
            "count": "ca/amt_non_resident_or_deemed_resident_checked",
        },
        produces={"output": "ca/amt_federal_surtax_if_non_resident"},
    ),
    # Part 3 line 4, chosen by the condition above: line 3 when there is an amount on it, else the
    # second branch.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/amt_line_3_has_amount",
            "when_none": "ca/amt_federal_surtax_if_non_resident",
            "when_any": "ca/amt_federal_surtax_multiple_jurisdictions",
        },
        produces={"output": "ca/amt_federal_surtax"},
    ),
    # Part 3 line 6 "Add lines 1, 4, and 5.": line 1 (the basic federal tax), line 4 (the surtax)
    # and line 5 "Recapture of investment tax credit (from line 3 of Part C of Form T2038(IND))", in
    # line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_basic_federal_tax",
                "ca/amt_federal_surtax",
                "ca/itc_recapture",
            )
        },
        produces={"output": "ca/amt_federal_tax_with_surtax_and_recapture"},
    ),
    # Part 3 line 9 "Line 7 plus line 8": line 7 "Federal foreign tax credit from Form T2209" and
    # line 8 "Federal logging tax credit", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_foreign_tax_credit",
                "ca/federal_logging_tax_credit",
            )
        },
        produces={"output": "ca/amt_foreign_and_logging_credits_total"},
    ),
    # Part 3 line 10 "Line 6 minus line 9 (if negative, enter "0")" "Federal tax payable".
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_federal_tax_with_surtax_and_recapture",
            "less": "ca/amt_foreign_and_logging_credits_total",
        },
        produces={"output": "ca/amt_federal_tax_payable"},
    ),
    # Part 3 line 12 "Investment tax credit amount up to, but not more than the amount I of Form
    # T2038(IND)": the claim, the filer's figure, may not be more than amount I, and above it is
    # refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_investment_tax_credit_claim",
            "bound": "ca/itc_amount_i",
        },
        produces={"output": "ca/amt_investment_tax_credit"},
    ),
    # Part 3 line 14 "Add lines 11 to 13.": line 11 "Federal political contribution tax credit from
    # line 41000 of your return", line 12 and line 13 "Labour-sponsored funds tax credit from line
    # 41400 of your return", in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/political_credit",
                "ca/amt_investment_tax_credit",
                "ca/labour_sponsored_funds_credit",
            )
        },
        produces={"output": "ca/amt_regular_tax_credits_total"},
    ),
    # Part 3 line 15 "Line 10 minus line 14 (if negative, enter "0")" "Regular net federal tax
    # payable", which nothing reads until Part 5 lands.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_federal_tax_payable",
            "less": "ca/amt_regular_tax_credits_total",
        },
        produces={"output": "ca/amt_regular_net_federal_tax_payable"},
    ),
    # Part 4 line 3 "Non-taxable part of foreign capital gains included in adjusted taxable income
    # (cannot be more than line 23 of Part 1)": the bound is line 23 with a loss taken as 0, so that
    # a loss on line 23 refuses no claim of 0. It is not a form line.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/amt_capital_gains_added",)},
        produces={"output": "ca/amt_capital_gains_added_not_below_zero"},
    ),
    # Part 4 line 3: the claim, the caller's figure, may not be more than the bound, and a claim
    # above it is refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_foreign_capital_gains_non_taxable_claim",
            "bound": "ca/amt_capital_gains_added_not_below_zero",
        },
        produces={"output": "ca/amt_foreign_capital_gains_non_taxable"},
    ),
    # Form T691 Part 4 line 2 "Foreign non-business income (on which non-business income tax was
    # paid to a foreign country (12))": the total of the net foreign non-business income of the
    # foreign tax countries, one record for each country (Form T2209 line 2, 43300).
    CapabilitySelection(
        name="ca/foreign_net_non_business_income_total",
        params={},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/amt_foreign_non_business_income"},
    ),
    # Form T691 Part 4 line 7 "Total non-business income tax paid to a foreign country (12)": the
    # total of the non-business tax paid of the foreign tax countries (Form T2209 line 1, 43100).
    CapabilitySelection(
        name="ca/foreign_non_business_tax_paid_total",
        params={},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/amt_foreign_non_business_tax_paid_before_excess"},
    ),
    # Form T691 Part 4 line 7 "(ii) Total non-business income tax paid to a foreign country (12)",
    # note (12): the tax paid "minus any part of this tax that is deductible under subsection 20(11)
    # or deducted under subsection 20(12) of the ITA", the same as Form T2209 note (1). The tax on
    # income from property over 15% of it is deducted on line 23200
    # (ca/foreign_property_tax_over_limit), so it is taken off the total.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_foreign_non_business_tax_paid_before_excess",
            "less": "ca/foreign_property_tax_over_limit",
        },
        produces={"output": "ca/amt_foreign_non_business_tax_paid"},
    ),
    # Form T691 Part 4 line 8 "Total business income tax paid to a foreign country (13)": the total
    # of the business tax paid for the year of the foreign tax countries (Form T2209 line 4, the
    # first part, 43400); the unused credits of that line are not part of it.
    CapabilitySelection(
        name="ca/foreign_business_tax_paid_total",
        params={},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/amt_foreign_business_tax_paid"},
    ),
    # Part 4 line 4 "Total foreign income: add lines 1 to 3 (if negative, enter "0")": lines 1 (the
    # caller's foreign business income, which may be negative), 2 and 3 in line order, floored at
    # zero.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/amt_foreign_business_income",
                "ca/amt_foreign_non_business_income",
                "ca/amt_foreign_capital_gains_non_taxable",
            )
        },
        produces={"output": "ca/amt_total_foreign_income"},
    ),
    # Part 4 line 5 "Applicable rate" "× 20.5%" and line 6 "Foreign income limit for special foreign
    # tax credit: line 4 multiplied by the percentage on line 5 (if negative, enter "0")": the rate
    # of Part 1 line 96. Line 4 is never negative (it is floored above), so the printed floor on
    # line 6 cannot apply.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_federal_tax_rate"},
        consumes={"base": "ca/amt_total_foreign_income"},
        produces={"output": "ca/amt_foreign_income_limit"},
    ),
    # Part 4 line 7 "Total non-business income tax paid to a foreign country (12)" "× 66.6666%": the
    # caller's tax paid (footnote 12 is the caller's definition), times the percentage as printed.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_special_foreign_tax_credit_rate"},
        consumes={"base": "ca/amt_foreign_non_business_tax_paid"},
        produces={"output": "ca/amt_foreign_non_business_tax_two_thirds"},
    ),
    # Part 4 line 9 "Foreign taxes paid for special foreign tax credit: line 7 plus line 8 (if
    # negative, enter "0")": line 7 and line 8 (the caller's business tax paid), floored at zero.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={
            "parts": (
                "ca/amt_foreign_non_business_tax_two_thirds",
                "ca/amt_foreign_business_tax_paid",
            )
        },
        produces={"output": "ca/amt_foreign_taxes_paid"},
    ),
    # Part 4 line 10 "Enter whichever is less: amount from line 6 or line 9.": the lesser of the
    # two.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/amt_foreign_income_limit",
                "ca/amt_foreign_taxes_paid",
            ),
        },
        produces={"output": "ca/amt_foreign_tax_credit_lesser"},
    ),
    # Part 4 line 11 "Enter whichever is more: amount from line 7 of Part 3 or line 10." "Special
    # foreign tax credit": the greater of the federal foreign tax credit of Part 3 line 7 (Form
    # T2209) and line 10. Nothing reads it until Part 5.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca/federal_foreign_tax_credit",
                "ca/amt_foreign_tax_credit_lesser",
            ),
        },
        produces={"output": "ca/amt_special_foreign_tax_credit"},
    ),
    # Part 5 line 3 "Line 1 minus line 2 (if negative, enter "0")" "Net minimum tax payable": line
    # 1, the minimum amount of line 103 of Part 1, less line 2, the special foreign tax credit of
    # Part 4 line 11, and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_minimum_amount",
            "less": "ca/amt_special_foreign_tax_credit",
        },
        produces={"output": "ca/amt_net_minimum_tax_payable"},
    ),
    # Part 5 line 6 "Line 4 minus line 5 (if negative, enter "0")": line 4, the regular net federal
    # tax payable of Part 3 line 15, less line 5, the federal surtax of Part 3 line 4. Line 5 may be
    # negative when the basic federal tax is negative, and then it is added back.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_regular_net_federal_tax_payable",
            "less": "ca/amt_federal_surtax",
        },
        produces={"output": "ca/amt_regular_net_tax_less_surtax"},
    ),
    # Part 5 line 7 "Line 3 minus line 6 (if negative, enter "0")": line 3 less line 6, never below
    # zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_net_minimum_tax_payable",
            "less": "ca/amt_regular_net_tax_less_surtax",
        },
        produces={"output": "ca/amt_minimum_tax_after_regular_tax"},
    ),
    # Part 5 line 10 "Line 8 minus line 9 (if negative, enter "0")": line 8, the investment tax
    # credit of Part 3 line 12, less line 9, amount 15 of Part D of Form T2038(IND) (line 41200,
    # read from the investment tax credit family), and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_investment_tax_credit",
            "less": "ca/investment_tax_credit",
        },
        produces={"output": "ca/amt_investment_tax_credit_less_part_d"},
    ),
    # Part 5 line 11 "Line 7 minus line 10 (if negative, enter "0")": line 7 less line 10, never
    # below zero. The count of the condition "line 11 is positive" reads it for T1 line 41700.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_minimum_tax_after_regular_tax",
            "less": "ca/amt_investment_tax_credit_less_part_d",
        },
        produces={"output": "ca/amt_alternative_minimum_tax_payable"},
    ),
    # Part 6 line 3 "Line 1 minus line 2 (if negative, enter "0")": line 1, the basic federal tax of
    # Part 2 line 7, less line 2, the amount from line 22 of Form T1206, and never below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_basic_federal_tax",
            "less": "ca/split_income_line_22",
        },
        produces={"output": "ca/amt_basic_federal_tax_less_split_income_tax"},
    ),
    # Part 6 line 5 "Enter whichever is more: amount from line 3 or line 4.": the greater of line 3
    # and line 4, the minimum amount from line 103 of Part 1.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca/amt_basic_federal_tax_less_split_income_tax",
                "ca/amt_minimum_amount",
            ),
        },
        produces={"output": "ca/amt_greater_of_basic_tax_and_minimum_amount"},
    ),
    # Part 6 line 7 "Line 5 plus line 6 (14)": line 5 and line 6, the amount from line 22 of Form
    # T1206, in line order. The form prints no floor, so the sum may be negative.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_greater_of_basic_tax_and_minimum_amount",
                "ca/split_income_line_22",
            )
        },
        produces={"output": "ca/amt_federal_tax_under_minimum_tax"},
    ),
    # Part 6 line 9 "Federal surtax on business income earned outside Canada" "Multiply the amount
    # from line 7 by 48%.": line 7 times the 48% of its dataset, rounded to the cent.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/amt_federal_surtax_rate"},
        consumes={"base": "ca/amt_federal_tax_under_minimum_tax"},
        produces={"output": "ca/amt_part_6_surtax_at_48_percent"},
    ),
    # Part 6 line 10 "If you have to pay tax to multiple jurisdictions, multiply the amount from
    # line 9 by the percentage in Column 5 of line 52220 on Form T2203.": line 9 times the
    # percentage as the form prints it (50 for 50%), rounded once to the cent.
    CapabilitySelection(
        name="ca/apply_percentage",
        params={"rounding": "ca/amt_multiple_jurisdictions_rounding"},
        consumes={
            "amount": "ca/amt_part_6_surtax_at_48_percent",
            "percentage": "ca/amt_t2203_column_5_percentage_checked",
        },
        produces={"output": "ca/amt_part_6_surtax_multiple_jurisdictions"},
    ),
    # Part 6 line 11 "If you have an amount on line 10, enter that amount. If not, and you are a
    # non-resident or deemed resident, enter the amount from line 9. Otherwise, enter "0".": the
    # condition "you have an amount on line 10" counts 1 when line 10 is not 0.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/amt_line_10_has_amount_conditions"},
        consumes={
            "counts": (),
            "amounts": ("ca/amt_part_6_surtax_multiple_jurisdictions",),
        },
        produces={"output": "ca/amt_part_6_has_amount_on_line_10"},
    ),
    # Part 6 line 11, the second branch: line 9 when "you are a non-resident or deemed resident"
    # (the caller's count, 1 for yes, checked in Part 3), and "0" otherwise.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/amt_part_6_surtax_at_48_percent",
            "count": "ca/amt_non_resident_or_deemed_resident_checked",
        },
        produces={"output": "ca/amt_part_6_surtax_if_non_resident"},
    ),
    # Part 6 line 11, chosen by the condition above: line 10 when there is an amount on it, else
    # the second branch.
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/amt_part_6_has_amount_on_line_10",
            "when_none": "ca/amt_part_6_surtax_if_non_resident",
            "when_any": "ca/amt_part_6_surtax_multiple_jurisdictions",
        },
        produces={"output": "ca/amt_part_6_federal_surtax"},
    ),
    # Part 6 line 12 "Line 8 plus line 11": line 8, the net minimum tax payable of Part 5 line 3,
    # and line 11, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_net_minimum_tax_payable",
                "ca/amt_part_6_federal_surtax",
            )
        },
        produces={"output": "ca/amt_part_6_tax_with_surtax"},
    ),
    # Part 6 line 14 "Enter whichever is more: amount from line 12 or line 13. Enter this amount on
    # line 41700 of your return." "Federal tax payable (under alternative minimum tax)": the greater
    # of line 12 and line 13, "Amount from line 24 of Form T1206". The entry on line 41700 of the
    # return is made by the choice of the line 41700 entry, which takes this amount only when Part 5
    # line 11 is positive.
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={
            "amounts": (
                "ca/amt_part_6_tax_with_surtax",
                "ca/split_income_line_24",
            ),
        },
        produces={"output": "ca/amt_federal_tax_payable_under_minimum_tax"},
    ),
    # Part 7 line 4 "Line 2 plus line 3": line 2, the basic federal tax of Part 2 line 7, and line
    # 3, the recapture of investment tax credit, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/amt_basic_federal_tax", "ca/itc_recapture")},
        produces={"output": "ca/amt_part_7_basic_tax_with_recapture"},
    ),
    # Part 7 line 7 "Line 5 plus line 6": line 5, the federal logging tax credit (line 133 of your
    # return, as on Part 1 line 100), and line 6, "Amount from line 41600 of your return", in line
    # order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/federal_logging_tax_credit",
                "ca/credits_against_federal_tax",
            )
        },
        produces={"output": "ca/amt_part_7_credits_total"},
    ),
    # Part 7 line 8 "Line 4 minus line 7": line 4 less line 7. The form prints no floor, so the
    # difference may be negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_part_7_basic_tax_with_recapture",
            "less": "ca/amt_part_7_credits_total",
        },
        produces={"output": "ca/amt_part_7_tax_less_credits"},
    ),
    # Part 7 line 11 "Line 9 minus line 10 (if negative, enter "0")": the special foreign tax credit
    # of Part 4 line 11 less the federal foreign tax credit of Part 3 line 7, not below zero.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_special_foreign_tax_credit",
            "less": "ca/federal_foreign_tax_credit",
        },
        produces={"output": "ca/amt_part_7_foreign_credit_difference"},
    ),
    # Part 7 line 12, the denominator of the fraction: "Foreign taxes paid (non-business income tax
    # paid to a foreign country (15) plus business income tax paid to a foreign country (16))", the
    # two caller's figures added. It is not a numbered line of the form.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_foreign_non_business_tax_paid",
                "ca/amt_foreign_business_tax_paid",
            )
        },
        produces={"output": "ca/amt_part_7_foreign_taxes_paid"},
    ),
    # Part 7 line 12 "Line 11 x [Foreign taxes paid for special foreign tax credit (line 9 of Part
    # 4)] / [Foreign taxes paid ...]": line 11 times line 9 of Part 4 over the denominator, rounded
    # once to the cent; 0 when there are no foreign taxes paid.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/amt_foreign_taxes_ratio_rounding"},
        consumes={
            "amount": "ca/amt_part_7_foreign_credit_difference",
            "numerator": "ca/amt_foreign_taxes_paid",
            "denominator": "ca/amt_part_7_foreign_taxes_paid",
        },
        produces={"output": "ca/amt_part_7_foreign_credit_share"},
    ),
    # Part 7 line 13 "Line 8 plus line 12": line 8 and line 12, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_part_7_tax_less_credits",
                "ca/amt_part_7_foreign_credit_share",
            )
        },
        produces={"output": "ca/amt_part_7_tax_less_credits_plus_share"},
    ),
    # Part 7 line 14 "Line 1 minus line 13 (if negative, enter "0")" "Additional taxes paid for
    # minimum tax carryover": line 1, the minimum amount of Part 1 line 103, less line 13, not below
    # zero. Part 8 line 14 reads it.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/amt_minimum_amount",
            "less": "ca/amt_part_7_tax_less_credits_plus_share",
        },
        produces={"output": "ca/amt_additional_taxes_for_carryover"},
    ),
    # Part 8 line 13 "Balance of minimum tax carryover available for later years, if any: line 1
    # minus line 12": line 1 less line 12. Line 12 is at most line 1 (the claim is bounded by it),
    # so the balance is not below zero.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_minimum_tax_carryover_from_previous_years",
            "less": "ca/amt_minimum_tax_carryover_within_maximum",
        },
        produces={"output": "ca/amt_carryover_balance"},
    ),
    # Part 5 "If line 11 is positive, complete parts 6 and 7." Part 8 line 14 "Additional 2025 taxes
    # for carryover to later years from line 14 of Part 7": line 14 of Part 7 when line 11 is
    # positive (the count is 1), and 0 otherwise.
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/amt_additional_taxes_for_carryover",
            "count": "ca/amt_part_5_line_11_is_positive",
        },
        produces={"output": "ca/amt_part_8_additional_taxes"},
    ),
    # Part 8 line 15 "Line 13 plus line 14": line 13 and line 14, the additional 2025 taxes of Part
    # 8 line 14, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_carryover_balance",
                "ca/amt_part_8_additional_taxes",
            )
        },
        produces={"output": "ca/amt_carryover_balance_with_additional_taxes"},
    ),
    # Part 8 line 16 "Unapplied 2018 minimum tax carryover" is part of line 13, so at most line 13
    # (`ca/amt_carryover_balance`): an amount above it is an input error, not capped. Line 17 reads
    # the checked amount.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_unapplied_2018_carryover",
            "bound": "ca/amt_carryover_balance",
        },
        produces={"output": "ca/amt_unapplied_2018_carryover_checked"},
    ),
    # Part 8 line 17 "Total minimum tax carryover available for 2026: line 15 minus line 16": line
    # 15 less line 16, the unapplied 2018 minimum tax carryover. The form prints no floor, so the
    # difference may be negative.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/amt_carryover_balance_with_additional_taxes",
            "less": "ca/amt_unapplied_2018_carryover_checked",
        },
        produces={"output": "ca/amt_carryover_available_for_2026"},
    ),
    # Part 1 lines 39 and 40 "complete line 39 or 40 depending on your situation": the count is 1
    # when line 39 (no election) and line 40 (election) are each more than 0, else 0. A count of 1
    # is refused, an input error naming both lines (not capped, and not a printed line), because
    # lines 43 and 46 add both. The checked count is read by nothing on the return.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/amt_lines_39_and_40_both_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/amt_limited_partnership_difference_no_election",
                "ca/amt_limited_partnership_difference_election",
            ),
        },
        produces={"output": "ca/amt_lines_39_and_40_both"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/amt_lines_39_and_40_both_refused"},
        consumes={"count": "ca/amt_lines_39_and_40_both"},
        produces={"output": "ca/amt_lines_39_and_40_both_checked"},
    ),
    # Part 1 line 59 "(Quebec only)": the count is 1 when line 59 is more than 0 and the filer was a
    # resident of Ontario on December 31, 2025, else 0. A count of 1 is refused, an input error
    # (not capped, and not a printed line), because the Quebec line 22300 is no Ontario line. The
    # checked count is read by nothing on the return.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/amt_ppip_premiums_in_ontario_conditions"},
        consumes={
            "counts": ("ca-on/not_resident_of_ontario_at_year_end_checked",),
            "amounts": ("ca/amt_ppip_premiums_deduction",),
        },
        produces={"output": "ca/amt_ppip_premiums_in_ontario"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/amt_ppip_premiums_in_ontario_refused"},
        consumes={"count": "ca/amt_ppip_premiums_in_ontario"},
        produces={"output": "ca/amt_ppip_premiums_in_ontario_checked"},
    ),
    # Form T691 Part 1 line 10 "Carrying charges (2) for acquiring an interest in a partnership of
    # which you are a limited or non-active partner, or which owns a rental or leasing property or a
    # film property (included on line 22100 of your return) (6)" and lines 64 to 67, each "included
    # on line 22100 of your return": their sum is at most line 22100 of the return, the Federal
    # Worksheet's carrying charges, interest expenses and other expenses. Note (11) makes lines 64
    # to 67 apart from line 2, 5 and 10, so the sum is the bound. An amount above it is an input
    # error, not capped; the checked amount is read by nothing on the return.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/amt_limited_partner_carrying_charges",
                "ca/amt_non_deductible_property_expenses",
            )
        },
        produces={"output": "ca/amt_expenses_included_on_line_22100"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_expenses_included_on_line_22100",
            "bound": "ca/carrying_charges_interest_expenses_and_other_expenses",
        },
        produces={"output": "ca/amt_expenses_included_on_line_22100_checked"},
    ),
    # Form T691 Part 9 line 1 "Total of all resource expenditures, depletion allowances and carrying
    # charges for resource property and flow-through shares (included on lines 22100, 22400, and
    # 23200 of your return)": the sum of the three lines (line 22100, line 22400 and line 23200, the
    # other deductions and the total split income) is the bound. Line 6 reads the checked amount.
    # An amount above it is an input error, not capped.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/carrying_charges_interest_expenses_and_other_expenses",
                "ca/exploration_and_development_expenses",
                "ca/other_deductions",
                "ca/total_split_income",
            )
        },
        produces={"output": "ca/amt_lines_22100_22400_and_23200"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/amt_resource_expenditures",
            "bound": "ca/amt_lines_22100_22400_and_23200",
        },
        produces={"output": "ca/amt_resource_expenditures_checked"},
    ),
}

WIRING = {
    (
        SubtractNotBelowZero,
        frozenset(
            {AMT_FILM_PROPERTY_CCA_AND_CARRYING_CHARGES, AMT_FILM_PROPERTY_INCOME_BEFORE_CCA}
        ),
        frozenset({AMT_FILM_PROPERTY_ADJUSTMENT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {AMT_RENTAL_PROPERTY_CCA_AND_CARRYING_CHARGES, AMT_RENTAL_PROPERTY_INCOME_BEFORE_CCA}
        ),
        frozenset({AMT_RENTAL_PROPERTY_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_TAX_SHELTER_LOSSES,
                AMT_TAX_SHELTER_DEDUCTIBLE_AMOUNTS,
                AMT_LIMITED_PARTNER_CARRYING_CHARGES,
            }
        ),
        frozenset({AMT_TAX_SHELTER_ADJUSTMENTS}),
    ),
    (
        Sum,
        frozenset(
            {
                TAXABLE_INCOME_SIGNED,
                AMT_FILM_PROPERTY_ADJUSTMENT,
                AMT_RENTAL_PROPERTY_ADJUSTMENT,
                AMT_TAX_SHELTER_ADJUSTMENTS,
            }
        ),
        frozenset({AMT_PART_1_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_RESOURCE_PRODUCTION_INCOME,
                AMT_RESOURCE_FOREIGN_PROPERTY_INCOME,
                AMT_CLASS_43_1_INCOME,
            }
        ),
        frozenset({AMT_RESOURCE_INCOME_TOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_RESOURCE_EXPENDITURES_CHECKED, AMT_RESOURCE_INCOME_TOTAL}),
        frozenset({AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES}),
    ),
    (
        Sum,
        frozenset({QFFP_FORECLOSURE_GAIN_OR_LOSS, OTHER_FORECLOSURE_GAIN_OR_LOSS}),
        frozenset({AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS,
                AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS,
                AMT_GRADUATED_RATE_ESTATE_CAPITAL_GAINS,
            }
        ),
        frozenset({AMT_CAPITAL_GAINS_ADJUSTMENTS}),
    ),
    (
        SumNotBelowZero,
        frozenset({CAPITAL_GAIN}),
        frozenset({AMT_CAPITAL_GAIN_NOT_BELOW_ZERO}),
    ),
    (
        AtMost,
        frozenset({AMT_TREATY_EXEMPT_CAPITAL_GAINS, AMT_CAPITAL_GAIN_NOT_BELOW_ZERO}),
        frozenset({AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED}),
    ),
    (
        AtMost,
        frozenset({AMT_TREATY_EXEMPT_CAPITAL_GAINS_CHECKED, ADDITIONAL_DEDUCTIONS_TOTAL}),
        frozenset({AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS}),
    ),
    (
        Subtract,
        frozenset({CAPITAL_GAIN, AMT_CAPITAL_GAINS_ADJUSTMENTS}),
        frozenset({AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS}),
    ),
    (
        Subtract,
        frozenset({AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS, TAXABLE_CAPITAL_GAINS}),
        frozenset({AMT_CAPITAL_GAINS_DIFFERENCE}),
    ),
    (
        SignChosenDifference,
        frozenset(
            {
                AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS,
                TAXABLE_CAPITAL_GAINS,
                AMT_CAPITAL_GAINS_DIFFERENCE,
            }
        ),
        frozenset({AMT_CAPITAL_GAINS_ADDED}),
    ),
    (
        Subtract,
        frozenset({AMT_PUBLICLY_LISTED_GIFTS_TOTAL, AMT_PUBLICLY_LISTED_GIFTS_T1170_LINE_68231}),
        frozenset({AMT_PUBLICLY_LISTED_GIFTS_NET}),
    ),
    (
        ApplyRate,
        frozenset({AMT_PUBLICLY_LISTED_GIFTS_NET}),
        frozenset({AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_PART_1_SUBTOTAL,
                AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES,
                AMT_CAPITAL_GAINS_ADDED,
                AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT,
            }
        ),
        frozenset({AMT_ADJUSTED_INCOME_WITH_GAINS}),
    ),
    (
        Sum,
        frozenset(
            {T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL, AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS}
        ),
        frozenset({AMT_SECURITY_OPTIONS_D_TOTAL}),
    ),
    (
        ApplyRate,
        frozenset({AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS}),
        frozenset({AMT_SECURITY_OPTION_GIFTS_DEDUCTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_SECURITY_OPTIONS_D_TOTAL, AMT_SECURITY_OPTION_GIFTS_DEDUCTION}),
        frozenset({AMT_SECURITY_OPTIONS_NET}),
    ),
    (
        Sum,
        frozenset(
            {
                T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
                AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION,
                AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION,
            }
        ),
        frozenset({AMT_SECURITY_OPTIONS_D1_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION,
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION,
                AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
                AMT_NET_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
            }
        ),
        frozenset({AMT_OTHER_YEARS_LOSSES_TOTAL}),
    ),
    (
        AtMost,
        frozenset({AMT_NON_CAPITAL_LOSSES_DIFFERENCE, NON_CAPITAL_LOSSES_ON_LINE_25200}),
        frozenset({AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({AMT_NET_CAPITAL_LOSSES_DIFFERENCE, NET_CAPITAL_LOSSES_OF_OTHER_YEARS}),
        frozenset({AMT_NET_CAPITAL_LOSSES_DIFFERENCE_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION,
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION,
            }
        ),
        frozenset({AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED}),
    ),
    (
        AtMost,
        frozenset(
            {
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED,
                LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
            }
        ),
        frozenset({AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED_CHECKED}),
    ),
    (
        Subtract,
        frozenset(
            {
                LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED_CHECKED,
            }
        ),
        frozenset({AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT}),
    ),
    (
        Subtract,
        frozenset({NON_CAPITAL_LOSSES_ON_LINE_25200, AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED}),
        frozenset({AMT_NON_CAPITAL_LOSSES_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT,
                AMT_NON_CAPITAL_LOSSES_ADJUSTMENT,
                UNION_DUES,
                CHILD_CARE_EXPENSES,
            }
        ),
        frozenset({AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL,
                DISABILITY_SUPPORTS_DEDUCTION,
                MOVING_EXPENSES_DEDUCTION,
                CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
                CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
                AMT_PPIP_PREMIUMS_DEDUCTION,
                CLERGY_RESIDENCE_DEDUCTION,
                CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
                NORTHERN_RESIDENTS_DEDUCTIONS,
            }
        ),
        frozenset({AMT_DEDUCTIONS_TOTAL}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_NON_DEDUCTIBLE_INTEREST,
                AMT_LIFE_INSURANCE_PREMIUMS_AS_COLLATERAL,
                AMT_FINANCING_EXPENSES,
                AMT_INVESTMENT_COUNSEL_FEES,
            }
        ),
        frozenset({AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_COMMISSION_EMPLOYMENT_EXPENSES,
                AMT_LEGAL_AND_ACCOUNTING_EXPENSES,
                AMT_REPAYMENT_OF_SALARY_AND_WAGES,
                AMT_EXCESS_EPSP_AMOUNTS,
                AMT_FORFEITED_SALARY_DEFERRAL_AMOUNTS,
                AMT_REPAYMENT_OF_WAGE_LOSS_REPLACEMENT,
            }
        ),
        frozenset({AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES}),
    ),
    (
        AtMost,
        frozenset({AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES, OTHER_EMPLOYMENT_EXPENSES}),
        frozenset({AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED}),
    ),
    (
        Subtract,
        frozenset({OTHER_EMPLOYMENT_EXPENSES, AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED}),
        frozenset({AMT_OFFICE_EXPENSES_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_DEDUCTIONS_TOTAL,
                AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES,
                AMT_OFFICE_EXPENSES_ADJUSTMENT,
            }
        ),
        frozenset({AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL}),
    ),
    (
        ApplyRate,
        frozenset({AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL}),
        frozenset({AMT_APPLICABLE_RATE_AMOUNT}),
    ),
    (
        Sum,
        frozenset({AMT_ADJUSTED_INCOME_WITH_GAINS, AMT_SECURITY_OPTIONS_NET}),
        frozenset({AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS,
                AMT_SECURITY_OPTIONS_D1_TOTAL,
                AMT_OTHER_YEARS_LOSSES_TOTAL,
            }
        ),
        frozenset({AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL}),
    ),
    (
        Sum,
        frozenset({AMT_APPLICABLE_RATE_AMOUNT, AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL}),
        frozenset({AMT_ADJUSTMENTS_AFTER_RATE_TOTAL}),
    ),
    (
        ApplyRate,
        frozenset({TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE}),
        frozenset({AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT}),
    ),
    (
        Subtract,
        frozenset({TAXABLE_DIVIDENDS, TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE}),
        frozenset({AMT_AMOUNT_A_MINUS_AMOUNT_B}),
    ),
    (
        ApplyRate,
        frozenset({AMT_AMOUNT_A_MINUS_AMOUNT_B}),
        frozenset({AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT, AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT}
        ),
        frozenset({AMT_DIVIDENDS_ADJUSTMENTS_TOTAL}),
    ),
    (
        ApplyRate,
        frozenset({CAPITAL_GAINS_DEDUCTION}),
        frozenset({AMT_LIFETIME_EXEMPTION_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset({AMT_DIVIDENDS_ADJUSTMENTS_TOTAL, AMT_LIFETIME_EXEMPTION_ADJUSTMENT}),
        frozenset({AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL}),
    ),
    (
        ApplyFraction,
        frozenset({QBT_CAPITAL_GAINS_DEDUCTION}),
        frozenset({AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED}),
    ),
    (
        Subtract,
        frozenset({AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED, QBT_CAPITAL_GAINS_DEDUCTION}),
        frozenset({AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL,
                AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE,
            }
        ),
        frozenset({AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_ADJUSTMENTS_AFTER_RATE_TOTAL, AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL}),
        frozenset({AMT_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        CreditAmount,
        frozenset({}),
        frozenset({AMT_BASIC_EXEMPTION}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_ADJUSTED_TAXABLE_INCOME, AMT_BASIC_EXEMPTION}),
        frozenset({AMT_NET_ADJUSTED_TAXABLE_INCOME}),
    ),
    (
        ApplyRate,
        frozenset({AMT_NET_ADJUSTED_TAXABLE_INCOME}),
        frozenset({AMT_GROSS_MINIMUM_AMOUNT}),
    ),
    (
        ApplyRate,
        frozenset({CREDIT_AMOUNTS_AT_CREDIT_RATE}),
        frozenset({AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT}),
    ),
    (
        ApplyRate,
        frozenset({DONATIONS_AND_GIFTS_CREDIT}),
        frozenset({AMT_DONATIONS_AND_GIFTS_ADJUSTMENT}),
    ),
    (
        Sum,
        frozenset(
            {
                AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT,
                AMT_DONATIONS_AND_GIFTS_ADJUSTMENT,
                FEDERAL_LOGGING_TAX_CREDIT,
                AMT_SECTION_119_FORMER_RESIDENT_CREDIT,
            }
        ),
        frozenset({AMT_CREDITS_ADJUSTMENTS_TOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_GROSS_MINIMUM_AMOUNT, AMT_CREDITS_ADJUSTMENTS_TOTAL}),
        frozenset({AMT_MINIMUM_AMOUNT}),
    ),
    (
        Sum,
        frozenset({NON_REFUNDABLE_TAX_CREDITS, DIVIDEND_TAX_CREDIT}),
        frozenset({AMT_CREDITS_TOTAL}),
    ),
    (
        Subtract,
        frozenset({FEDERAL_TAX_WITH_SPLIT_INCOME, AMT_CREDITS_TOTAL}),
        frozenset({AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER}),
    ),
    (
        Subtract,
        frozenset(
            {AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER, AMT_MINIMUM_TAX_CARRYOVER_APPLIED}
        ),
        frozenset({AMT_BASIC_FEDERAL_TAX}),
    ),
    (
        Sum,
        frozenset({AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER, ITC_RECAPTURE}),
        frozenset({AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE}),
    ),
    (
        Sum,
        frozenset(
            {
                FEDERAL_TAX_ON_SPLIT_INCOME,
                FEDERAL_LOGGING_TAX_CREDIT,
                CREDITS_AGAINST_FEDERAL_TAX,
            }
        ),
        frozenset({AMT_SPLIT_INCOME_AND_CREDITS_TOTAL}),
    ),
    (
        Subtract,
        frozenset({AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE, AMT_SPLIT_INCOME_AND_CREDITS_TOTAL}),
        frozenset({AMT_TAX_PAYABLE_AFTER_CREDITS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_TAX_PAYABLE_AFTER_CREDITS, AMT_MINIMUM_AMOUNT}),
        frozenset({AMT_MAXIMUM_CARRYOVER_APPLIED}),
    ),
    (
        LesserOf,
        frozenset({AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS, AMT_MAXIMUM_CARRYOVER_APPLIED}),
        frozenset({AMT_MAXIMUM_CARRYOVER_CLAIM}),
    ),
    (
        AtMost,
        frozenset({AMT_MINIMUM_TAX_CARRYOVER_APPLIED, AMT_MAXIMUM_CARRYOVER_CLAIM}),
        frozenset({AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM}),
    ),
    (
        ApplyRate,
        frozenset({AMT_BASIC_FEDERAL_TAX}),
        frozenset({AMT_FEDERAL_SURTAX_AT_48_PERCENT}),
    ),
    (
        ApplyPercentage,
        frozenset({AMT_FEDERAL_SURTAX_AT_48_PERCENT, AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED}),
        frozenset({AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS}),
    ),
    (
        CountByConditions,
        frozenset({AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS}),
        frozenset({AMT_LINE_3_HAS_AMOUNT}),
    ),
    (
        YesOrNoCount,
        frozenset({AMT_NON_RESIDENT_OR_DEEMED_RESIDENT}),
        frozenset({AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({AMT_FEDERAL_SURTAX_AT_48_PERCENT, AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED}),
        frozenset({AMT_FEDERAL_SURTAX_IF_NON_RESIDENT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                AMT_LINE_3_HAS_AMOUNT,
                AMT_FEDERAL_SURTAX_IF_NON_RESIDENT,
                AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS,
            }
        ),
        frozenset({AMT_FEDERAL_SURTAX}),
    ),
    (
        Sum,
        frozenset({AMT_BASIC_FEDERAL_TAX, AMT_FEDERAL_SURTAX, ITC_RECAPTURE}),
        frozenset({AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE}),
    ),
    (
        Sum,
        frozenset({FEDERAL_FOREIGN_TAX_CREDIT, FEDERAL_LOGGING_TAX_CREDIT}),
        frozenset({AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE, AMT_FOREIGN_AND_LOGGING_CREDITS_TOTAL}
        ),
        frozenset({AMT_FEDERAL_TAX_PAYABLE}),
    ),
    (
        AtMost,
        frozenset({AMT_INVESTMENT_TAX_CREDIT_CLAIM, ITC_AMOUNT_I}),
        frozenset({AMT_INVESTMENT_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset({POLITICAL_CREDIT, LABOUR_SPONSORED_FUNDS_CREDIT, AMT_INVESTMENT_TAX_CREDIT}),
        frozenset({AMT_REGULAR_TAX_CREDITS_TOTAL}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_FEDERAL_TAX_PAYABLE, AMT_REGULAR_TAX_CREDITS_TOTAL}),
        frozenset({AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE}),
    ),
    (
        SumNotBelowZero,
        frozenset({AMT_CAPITAL_GAINS_ADDED}),
        frozenset({AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO}),
    ),
    (
        AtMost,
        frozenset(
            {AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE_CLAIM, AMT_CAPITAL_GAINS_ADDED_NOT_BELOW_ZERO}
        ),
        frozenset({AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE}),
    ),
    (
        SumNotBelowZero,
        frozenset(
            {
                AMT_FOREIGN_BUSINESS_INCOME,
                AMT_FOREIGN_NON_BUSINESS_INCOME,
                AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE,
            }
        ),
        frozenset({AMT_TOTAL_FOREIGN_INCOME}),
    ),
    (
        ApplyRate,
        frozenset({AMT_TOTAL_FOREIGN_INCOME}),
        frozenset({AMT_FOREIGN_INCOME_LIMIT}),
    ),
    (
        ApplyRate,
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_PAID}),
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS}),
    ),
    (
        SumNotBelowZero,
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS, AMT_FOREIGN_BUSINESS_TAX_PAID}),
        frozenset({AMT_FOREIGN_TAXES_PAID}),
    ),
    (
        LesserOf,
        frozenset({AMT_FOREIGN_INCOME_LIMIT, AMT_FOREIGN_TAXES_PAID}),
        frozenset({AMT_FOREIGN_TAX_CREDIT_LESSER}),
    ),
    (
        GreaterOf,
        frozenset({FEDERAL_FOREIGN_TAX_CREDIT, AMT_FOREIGN_TAX_CREDIT_LESSER}),
        frozenset({AMT_SPECIAL_FOREIGN_TAX_CREDIT}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_MINIMUM_AMOUNT, AMT_SPECIAL_FOREIGN_TAX_CREDIT}),
        frozenset({AMT_NET_MINIMUM_TAX_PAYABLE}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE, AMT_FEDERAL_SURTAX}),
        frozenset({AMT_REGULAR_NET_TAX_LESS_SURTAX}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_NET_MINIMUM_TAX_PAYABLE, AMT_REGULAR_NET_TAX_LESS_SURTAX}),
        frozenset({AMT_MINIMUM_TAX_AFTER_REGULAR_TAX}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_INVESTMENT_TAX_CREDIT, INVESTMENT_TAX_CREDIT}),
        frozenset({AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_MINIMUM_TAX_AFTER_REGULAR_TAX, AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D}),
        frozenset({AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_BASIC_FEDERAL_TAX, SPLIT_INCOME_LINE_22}),
        frozenset({AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX}),
    ),
    (
        GreaterOf,
        frozenset({AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX, AMT_MINIMUM_AMOUNT}),
        frozenset({AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT}),
    ),
    (
        Sum,
        frozenset({AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT, SPLIT_INCOME_LINE_22}),
        frozenset({AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX}),
    ),
    (
        ApplyRate,
        frozenset({AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX}),
        frozenset({AMT_PART_6_SURTAX_AT_48_PERCENT}),
    ),
    (
        ApplyPercentage,
        frozenset({AMT_PART_6_SURTAX_AT_48_PERCENT, AMT_T2203_COLUMN_5_PERCENTAGE_CHECKED}),
        frozenset({AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS}),
    ),
    (
        CountByConditions,
        frozenset({AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS}),
        frozenset({AMT_PART_6_HAS_AMOUNT_ON_LINE_10}),
    ),
    (
        TimesCount,
        frozenset({AMT_PART_6_SURTAX_AT_48_PERCENT, AMT_NON_RESIDENT_OR_DEEMED_RESIDENT_CHECKED}),
        frozenset({AMT_PART_6_SURTAX_IF_NON_RESIDENT}),
    ),
    (
        ChooseByCount,
        frozenset(
            {
                AMT_PART_6_HAS_AMOUNT_ON_LINE_10,
                AMT_PART_6_SURTAX_IF_NON_RESIDENT,
                AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS,
            }
        ),
        frozenset({AMT_PART_6_FEDERAL_SURTAX}),
    ),
    (
        Sum,
        frozenset({AMT_NET_MINIMUM_TAX_PAYABLE, AMT_PART_6_FEDERAL_SURTAX}),
        frozenset({AMT_PART_6_TAX_WITH_SURTAX}),
    ),
    (
        GreaterOf,
        frozenset({AMT_PART_6_TAX_WITH_SURTAX, SPLIT_INCOME_LINE_24}),
        frozenset({AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX}),
    ),
    (
        Sum,
        frozenset({ITC_RECAPTURE, AMT_BASIC_FEDERAL_TAX}),
        frozenset({AMT_PART_7_BASIC_TAX_WITH_RECAPTURE}),
    ),
    (
        Sum,
        frozenset({FEDERAL_LOGGING_TAX_CREDIT, CREDITS_AGAINST_FEDERAL_TAX}),
        frozenset({AMT_PART_7_CREDITS_TOTAL}),
    ),
    (
        Subtract,
        frozenset({AMT_PART_7_BASIC_TAX_WITH_RECAPTURE, AMT_PART_7_CREDITS_TOTAL}),
        frozenset({AMT_PART_7_TAX_LESS_CREDITS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_SPECIAL_FOREIGN_TAX_CREDIT, FEDERAL_FOREIGN_TAX_CREDIT}),
        frozenset({AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE}),
    ),
    (
        Sum,
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_PAID, AMT_FOREIGN_BUSINESS_TAX_PAID}),
        frozenset({AMT_PART_7_FOREIGN_TAXES_PAID}),
    ),
    (
        ApplyRatioOrZero,
        frozenset(
            {
                AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE,
                AMT_FOREIGN_TAXES_PAID,
                AMT_PART_7_FOREIGN_TAXES_PAID,
            }
        ),
        frozenset({AMT_PART_7_FOREIGN_CREDIT_SHARE}),
    ),
    (
        Sum,
        frozenset({AMT_PART_7_TAX_LESS_CREDITS, AMT_PART_7_FOREIGN_CREDIT_SHARE}),
        frozenset({AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({AMT_MINIMUM_AMOUNT, AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE}),
        frozenset({AMT_ADDITIONAL_TAXES_FOR_CARRYOVER}),
    ),
    (
        Subtract,
        frozenset(
            {
                AMT_MINIMUM_TAX_CARRYOVER_FROM_PREVIOUS_YEARS,
                AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
            }
        ),
        frozenset({AMT_CARRYOVER_BALANCE}),
    ),
    (
        AtMost,
        frozenset({AMT_UNAPPLIED_2018_CARRYOVER, AMT_CARRYOVER_BALANCE}),
        frozenset({AMT_UNAPPLIED_2018_CARRYOVER_CHECKED}),
    ),
    (
        TimesCount,
        frozenset({AMT_ADDITIONAL_TAXES_FOR_CARRYOVER, AMT_PART_5_LINE_11_IS_POSITIVE}),
        frozenset({AMT_PART_8_ADDITIONAL_TAXES}),
    ),
    (
        Sum,
        frozenset({AMT_CARRYOVER_BALANCE, AMT_PART_8_ADDITIONAL_TAXES}),
        frozenset({AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES}),
    ),
    (
        Subtract,
        frozenset(
            {AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES, AMT_UNAPPLIED_2018_CARRYOVER_CHECKED}
        ),
        frozenset({AMT_CARRYOVER_AVAILABLE_FOR_2026}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_NO_ELECTION,
                AMT_LIMITED_PARTNERSHIP_DIFFERENCE_ELECTION,
            }
        ),
        frozenset({AMT_LINES_39_AND_40_BOTH}),
    ),
    (
        CountRefusedByConditions,
        frozenset({AMT_LINES_39_AND_40_BOTH}),
        frozenset({AMT_LINES_39_AND_40_BOTH_CHECKED}),
    ),
    (
        CountByConditions,
        frozenset({NOT_RESIDENT_OF_ONTARIO_AT_YEAR_END_CHECKED, AMT_PPIP_PREMIUMS_DEDUCTION}),
        frozenset({AMT_PPIP_PREMIUMS_IN_ONTARIO}),
    ),
    (
        CountRefusedByConditions,
        frozenset({AMT_PPIP_PREMIUMS_IN_ONTARIO}),
        frozenset({AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED}),
    ),
    (
        Sum,
        frozenset({AMT_LIMITED_PARTNER_CARRYING_CHARGES, AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES}),
        frozenset({AMT_EXPENSES_INCLUDED_ON_LINE_22100}),
    ),
    (
        AtMost,
        frozenset(
            {
                AMT_EXPENSES_INCLUDED_ON_LINE_22100,
                CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
            }
        ),
        frozenset({AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
                EXPLORATION_AND_DEVELOPMENT_EXPENSES,
                OTHER_DEDUCTIONS,
                TOTAL_SPLIT_INCOME,
            }
        ),
        frozenset({AMT_LINES_22100_22400_AND_23200}),
    ),
    (
        AtMost,
        frozenset({AMT_RESOURCE_EXPENDITURES, AMT_LINES_22100_22400_AND_23200}),
        frozenset({AMT_RESOURCE_EXPENDITURES_CHECKED}),
    ),
    (
        ForeignNetNonBusinessIncomeTotal,
        frozenset({FOREIGN_TAX_COUNTRIES}),
        frozenset({AMT_FOREIGN_NON_BUSINESS_INCOME}),
    ),
    (
        ForeignNonBusinessTaxPaidTotal,
        frozenset({FOREIGN_TAX_COUNTRIES}),
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS, FOREIGN_PROPERTY_TAX_OVER_LIMIT}
        ),
        frozenset({AMT_FOREIGN_NON_BUSINESS_TAX_PAID}),
    ),
    (
        ForeignBusinessTaxPaidTotal,
        frozenset({FOREIGN_TAX_COUNTRIES}),
        frozenset({AMT_FOREIGN_BUSINESS_TAX_PAID}),
    ),
}
