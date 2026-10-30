"""CA-ON 2025 end to end: return bg."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
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
    AMT_CAPITAL_GAINS_ADDED,
    AMT_CAPITAL_GAINS_ADJUSTMENTS,
    AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL,
    AMT_CAPITAL_GAINS_DIFFERENCE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_CARRYOVER_BALANCE,
    AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES,
    AMT_CREDITS_ADJUSTMENTS_TOTAL,
    AMT_CREDITS_TOTAL,
    AMT_DEDUCTIONS_TOTAL,
    AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION,
    AMT_DIVIDENDS_ADJUSTMENTS_TOTAL,
    AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT,
    AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT,
    AMT_DONATIONS_AND_GIFTS_ADJUSTMENT,
    AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED,
    AMT_FEDERAL_SURTAX,
    AMT_FEDERAL_SURTAX_AT_48_PERCENT,
    AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS,
    AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX,
    AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX,
    AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE,
    AMT_FILM_PROPERTY_ADJUSTMENT,
    AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE,
    AMT_FOREIGN_INCOME_LIMIT,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_FOREIGN_TAX_CREDIT_LESSER,
    AMT_FOREIGN_TAXES_PAID,
    AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT,
    AMT_GROSS_MINIMUM_AMOUNT,
    AMT_INVESTMENT_TAX_CREDIT,
    AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D,
    AMT_LIFETIME_EXEMPTION_ADJUSTMENT,
    AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED,
    AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT,
    AMT_LINE_3_HAS_AMOUNT,
    AMT_LINES_39_AND_40_BOTH_CHECKED,
    AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL,
    AMT_MAXIMUM_CARRYOVER_APPLIED,
    AMT_MAXIMUM_CARRYOVER_CLAIM,
    AMT_MINIMUM_AMOUNT,
    AMT_MINIMUM_TAX_AFTER_REGULAR_TAX,
    AMT_MINIMUM_TAX_CARRYOVER_APPLIED,
    AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM,
    AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS,
    AMT_NET_ADJUSTED_TAXABLE_INCOME,
    AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS,
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_NON_CAPITAL_LOSSES_ADJUSTMENT,
    AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES,
    AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED,
    AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES,
    AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT,
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
    AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED,
    AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION,
    AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT,
    AMT_PUBLICLY_LISTED_GIFTS_NET,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE,
    AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED,
    AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE,
    AMT_REGULAR_NET_TAX_LESS_SURTAX,
    AMT_REGULAR_TAX_CREDITS_TOTAL,
    AMT_RENTAL_PROPERTY_ADJUSTMENT,
    AMT_RESOURCE_EXPENDITURES_CHECKED,
    AMT_RESOURCE_INCOME_TOTAL,
    AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES,
    AMT_SECURITY_OPTION_GIFTS_DEDUCTION,
    AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS,
    AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL,
    AMT_SECURITY_OPTIONS_D1_TOTAL,
    AMT_SECURITY_OPTIONS_D_TOTAL,
    AMT_SECURITY_OPTIONS_NET,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    AMT_SPLIT_INCOME_AND_CREDITS_TOTAL,
    AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS,
    AMT_TAX_PAYABLE_AFTER_CREDITS,
    AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER,
    AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE,
    AMT_TAX_SHELTER_ADJUSTMENTS,
    AMT_TOTAL_FOREIGN_INCOME,
    AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS,
    CAPITAL_GAIN,
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LINE_41700,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    NET_FEDERAL_TAX,
    OTHER_EMPLOYMENT_EXPENSES,
    REFUND_OR_BALANCE_OWING,
    SECURITY_OPTIONS_DEDUCTIONS,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, Disposition, compute


def _logging_provinces(credit: str) -> tuple[dict[str, str], ...]:
    """The province records that give line 133 `credit`: one province whose logging tax paid is
    1.5 times the credit (66.6667% of it is the credit, 1800.00 for 2700) and whose net logging
    income is 30,000 (6.6667% of it is 2000.01, above the credit, so the tax side is the lesser).
    No credit gives no province."""
    if credit == "0":
        return ()
    return ({"tax_paid": str(int(credit) * 3 // 2), "net_logging_income": "30000"},)


def return_bg(
    film_cca: str = "9000.00",
    film_income: str = "4000.00",
    rental_cca: str = "7000.00",
    rental_income: str = "9000.00",
    shelter_losses: str = "1000.00",
    shelter_deductible: str = "500.00",
    limited_partner_carrying: str = "250.00",
    *,
    share_dispositions: tuple[Disposition, ...] = (("5000", "3000", "0"),),
    qffp_foreclosure_dispositions: tuple[Disposition, ...] = (),
    resource_expenditures: str = "5000.00",
    resource_production: str = "2000.00",
    resource_foreign: str = "1000.00",
    class_43_1: str = "500.00",
    treaty_exempt: str = "200.00",
    # T1 line 25600 "Additional deductions": the treaty-exempt gains of line 17 are included on it,
    # so the default is the 200.00 of `treaty_exempt`.
    additional_deductions: str = "200.00",
    graduated_rate_estate: str = "100.00",
    gifts_total: str = "3000.00",
    gifts_line_68231: str = "1000.00",
    security_t4_39_and_91: str = "1000.00",
    security_t1212_line_2: str = "800.00",
    security_gifts: str = "500.00",
    security_t4_41_and_92: str = "300.00",
    prospector: str = "100.00",
    deferred_profit_sharing: str = "50.00",
    limited_partnership_no_election: str = "600.00",
    ppip_premiums: str = "0",
    not_resident_of_ontario: int = 0,
    non_capital_difference: str = "100.00",
    net_capital_difference: str = "50.00",
    limited_partnership_election: str = "0",
    limited_partnership_losses_of_other_years: str = "600.00",
    limited_partnership_at_risk_amount: str = "800.00",
    non_capital_losses_of_other_years: str = "100.00",
    net_capital_losses_claimed: str = "50.00",
    unapplied_net_capital_losses_2001_to_2024: str = "50.00",
    moving_expenses: str = "200.00",
    non_deductible_interest: str = "300.00",
    life_insurance_premiums: str = "100.00",
    financing_expenses: str = "0",
    investment_counsel_fees: str = "50.00",
    commission_employment: str = "150.00",
    legal_and_accounting: str = "0",
    repayment_of_salary_and_wages: str = "0",
    excess_epsp: str = "0",
    forfeited_salary_deferral: str = "0",
    wage_loss_replacement: str = "0",
    # T1 line 22900 (other employment expenses, Form T777 line 17), entered as the "Other expenses"
    # of T777 line 8: a chosen figure of 150.00, the bound of the T691 lines 70 to 75 (line 76).
    other_employment_expenses: str = "150.00",
    employment_income: str = "60000",
    # The part of the employment income that is T4 pensionable and insurable earnings, when it is
    # not all of it (the security option benefits are neither).
    salary: str | None = None,
    carryover_from_previous_years: str = "0",
    carryover_claim: str = "0",
    t2203_percentage: str = "0",
    non_resident: int = 0,
    itc_claim: str = "0",
    amount_i: str = "0",
    foreign_business_income: str = "0",
    foreign_capital_gains_claim: str = "0",
    foreign_tax_countries: tuple[tuple[str, ...], ...] = (),
    part_d_amount_15: str = "0",
    logging_credit: str = "0",
    split_income_dividends: str = "0",
    split_income_dividends_other_than_eligible: str = "0",
    other_dividends_received_without_a_slip: str = "0",
    unapplied_2018_carryover: str = "0",
    t5_taxable_dividends: str = "0",
    t5_dividend_tax_credit: str = "0",
    # T1 line 22100 (total interest expenses, Federal Worksheet line 2): the T691 lines 10 and 64
    # to 67 of 250.00, 300.00, 100.00 and 50.00, a chosen figure of 700.00 that the lines are
    # included on.
    total_interest_expenses: str = "700.00",
    # T1 line 23200 (other deductions): the T691 Part 9 line 1 amount of 5000.00, a chosen figure.
    other_deductions: str = "5000.00",
) -> Worksheet:
    """Return BG's inputs (`returns/2025_return_bg.yaml`), with the Part 1 amounts given."""
    return compute(
        employment_income,
        share_dispositions,
        "0",
        "0",
        "0",
        "0",
        "0",
        qffp_foreclosure_dispositions=qffp_foreclosure_dispositions,
        salary=salary,
        amt_film_property_cca_and_carrying_charges=film_cca,
        amt_film_property_income_before_cca=film_income,
        amt_rental_property_cca_and_carrying_charges=rental_cca,
        amt_rental_property_income_before_cca=rental_income,
        amt_tax_shelter_losses=shelter_losses,
        amt_tax_shelter_deductible_amounts=shelter_deductible,
        amt_limited_partner_carrying_charges=limited_partner_carrying,
        amt_resource_expenditures=resource_expenditures,
        amt_resource_production_income=resource_production,
        amt_resource_foreign_property_income=resource_foreign,
        amt_class_43_1_income=class_43_1,
        amt_treaty_exempt_capital_gains=treaty_exempt,
        additional_deductions=additional_deductions,
        amt_graduated_rate_estate_capital_gains=graduated_rate_estate,
        amt_publicly_listed_gifts_total=gifts_total,
        amt_publicly_listed_gifts_t1170_line_68231=gifts_line_68231,
        t4_security_options_boxes_39_and_91=security_t4_39_and_91,
        t1212_line_1_opening_balance=security_t1212_line_2,
        t1212_line_2_benefits_no_longer_deferred=security_t1212_line_2,
        amt_security_option_publicly_listed_gifts=security_gifts,
        t4_security_options_boxes_41_and_92=security_t4_41_and_92,
        amt_prospector_or_grubstaker_deduction=prospector,
        amt_deferred_profit_sharing_plan_deduction=deferred_profit_sharing,
        amt_limited_partnership_difference_no_election=limited_partnership_no_election,
        amt_ppip_premiums_deduction=ppip_premiums,
        not_resident_of_ontario_at_year_end=not_resident_of_ontario,
        amt_non_capital_losses_difference=non_capital_difference,
        amt_net_capital_losses_difference=net_capital_difference,
        amt_limited_partnership_difference_election=limited_partnership_election,
        # T1 lines 25100 and 25200: the losses of other years that lines 39 to 50 of the T691 are at
        # most (600.00 and 100.00, the amounts of lines 39 and 41 above).
        limited_partnership_losses_of_other_years=limited_partnership_losses_of_other_years,
        limited_partnership_at_risk_amount=limited_partnership_at_risk_amount,
        non_capital_losses_of_other_years=non_capital_losses_of_other_years,
        # T1 line 25300: the net capital losses claimed (T1436 line 7) of 50.00, at most line 6,
        # which is the 50.00 of unapplied losses of 2001 to 2024 (factor 1), so line 10 is 50.00.
        net_capital_losses_claimed=net_capital_losses_claimed,
        unapplied_net_capital_losses_2001_to_2024=unapplied_net_capital_losses_2001_to_2024,
        # Form T1-M, one move: 100 and 10 kilometres (line 3 is 90), transportation and storage of
        # moving_expenses (line 4), no reimbursement, and 60000 of employment income at the new
        # work location as the net eligible income (line 28, the whole employment income of the
        # return). Line 29 is
        # moving_expenses, and it is the moving expenses deduction of line 21900 that the
        # alternative minimum tax reads (line 56).
        moving_moves=(
            {
                "old_home_distance": "100",
                "new_home_distance": "10",
                "transportation_and_storage": moving_expenses,
                "net_eligible_income": employment_income,
            },
        ),
        other_income=moving_expenses,
        amt_non_deductible_interest=non_deductible_interest,
        amt_life_insurance_premiums_as_collateral=life_insurance_premiums,
        amt_financing_expenses=financing_expenses,
        amt_investment_counsel_fees=investment_counsel_fees,
        amt_commission_employment_expenses=commission_employment,
        amt_legal_and_accounting_expenses=legal_and_accounting,
        amt_repayment_of_salary_and_wages=repayment_of_salary_and_wages,
        amt_excess_epsp_amounts=excess_epsp,
        amt_forfeited_salary_deferral_amounts=forfeited_salary_deferral,
        amt_repayment_of_wage_loss_replacement=wage_loss_replacement,
        t777_other_expenses=other_employment_expenses,
        amt_minimum_tax_carryover_from_previous_years=carryover_from_previous_years,
        amt_minimum_tax_carryover_applied=carryover_claim,
        amt_t2203_column_5_percentage=t2203_percentage,
        amt_non_resident_or_deemed_resident=non_resident,
        amt_investment_tax_credit_claim=itc_claim,
        # Form T2038(IND) Part D: amount I is the lesser of G and H. G is the opening balance (no
        # credit of Parts A and B, no graduated rate estate), and H is the federal tax of line 40600
        # less lines 41000 and 41400 (none here), which is above the amounts given, so I is G.
        itc_opening_balance=amount_i,
        # Part D amount 15: the claim the filer chooses (a separate election from the claim of Form
        # T691 Part 3 line 12, `itc_claim` above). It is up to I when AMT does not apply, and up to
        # K when T691 Part 5 line 7 is more than 0 (K is the lesser of G and J, J being the federal
        # tax of line 40600 less the T691 minimum amount of line 103); see `logging_credit`.
        itc_claim=part_d_amount_15,
        # The federal logging tax credit (T1 line 133, `logging_credit` above) is computed from the
        # province records: one province, see `_logging_provinces`. It lowers the federal tax of
        # line 134 (40600) and so Form T2038 amount J's starting figure, and it is the T691 Part 1
        # line 100 and Part 3 line 8 amount: it lowers the minimum amount (line 103) and the
        # regular net federal tax payable (line 15) alike, so Part 5 line 7 does not change by it.
        # J is then line 132 less the T691 minimum amount before the credit, whatever the credit.
        logging_provinces=_logging_provinces(logging_credit),
        amt_foreign_business_income=foreign_business_income,
        amt_foreign_capital_gains_non_taxable_claim=foreign_capital_gains_claim,
        foreign_tax_countries_rows=foreign_tax_countries,
        split_income_dividends=split_income_dividends,
        split_income_dividends_other_than_eligible=split_income_dividends_other_than_eligible,
        other_dividends_received_without_a_slip=other_dividends_received_without_a_slip,
        amt_unapplied_2018_carryover=unapplied_2018_carryover,
        t5_taxable_dividends=t5_taxable_dividends,
        t5_dividend_tax_credit=t5_dividend_tax_credit,
        total_interest_expenses=total_interest_expenses,
        other_deductions=other_deductions,
    )


def return_bg_with_security_options(
    box_39_and_91: str, *, employment_income: str = "60000", **overrides: Any
) -> Worksheet:
    """Return BG with the T4 boxes 39 and 91 at `box_39_and_91` instead of 1000.00.

    The benefit is employment income (line 10100): `employment_income`, which includes the
    1000.00 of the default boxes, less 1000.00 plus the boxes. The pensionable and insurable
    earnings of the T4 stay `employment_income`, the salary: the benefits are neither. Line 24900
    deducts the boxes (and the other T691 amounts it is made of), so the taxable income is that of
    the salary alone and what the boxes change is the adjusted taxable income of Form T691 (line 30
    adds them back) and, through the net income, the basic personal amount.
    """
    income = D(employment_income) - D("1000") + D(box_39_and_91)
    return return_bg(
        security_t4_39_and_91=box_39_and_91,
        employment_income=str(income),
        salary=employment_income,
        **overrides,
    )


def test_return_bg_line_1_is_the_taxable_income_with_the_cpp_deduction_and_the_gain() -> None:
    # Return BG: 60000.00 less the CPP enhanced contribution of 565.00 (line 22215) is 59435.00;
    # the taxable capital gains of 1000.00 (half the 2000.00 gain) make 60435.00, less the losses of
    # other years deducted on lines 25100 (600.00), 25200 (100.00) and 25300 (50.00), 750.00 in all,
    # is 59685.00, less the 200.00 of additional deductions (line 25600) is 59485.00, less the
    # 700.00 of line 22100 and the 5000.00 of line 23200 is 53785.00, less the 150.00 of other
    # employment expenses (line 23300, from T777 line 8 of 150.00) is 53635.00. Line 24900 is the
    # total of Form T691 lines 28, 29, 31, 35, 36 and 37, each included on it: 1000.00 + 400.00 +
    # 500.00 + 300.00 + 100.00 + 50.00 = 2350.00, so taxable
    # income is 53635.00 less 2350.00, 51285.00.
    worksheet = return_bg()

    assert worksheet.get(TAXABLE_INCOME).value == D("51285.00")


def test_return_bg_line_21_is_the_taxable_capital_gains_of_half_the_gain() -> None:
    # Return BG's share gain of 5000.00 less 3000.00 is 2000.00; at the 50% inclusion rate, 1000.00.
    worksheet = return_bg()

    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("1000.00")


def test_return_bg_line_4_is_the_film_cca_less_the_film_income() -> None:
    # Line 2 9000.00 minus line 3 4000.00 is 5000.00, not below zero.
    worksheet = return_bg()

    assert worksheet.get(AMT_FILM_PROPERTY_ADJUSTMENT).value == D("5000.00")


def test_return_bg_line_4_is_zero_when_the_film_income_is_more_than_the_cca() -> None:
    # Line 2 2000.00 minus line 3 4000.00 is -2000.00, which is entered as "0".
    worksheet = return_bg(film_cca="2000.00", film_income="4000.00")

    assert worksheet.get(AMT_FILM_PROPERTY_ADJUSTMENT).value == D("0")


def test_return_bg_line_7_is_zero_when_the_rental_income_is_more_than_the_cca() -> None:
    # Line 5 7000.00 minus line 6 9000.00 is -2000.00, which is entered as "0".
    worksheet = return_bg()

    assert worksheet.get(AMT_RENTAL_PROPERTY_ADJUSTMENT).value == D("0")


def test_return_bg_line_7_is_the_rental_cca_less_the_rental_income_when_it_is_positive() -> None:
    # Line 5 9000.00 minus line 6 7000.00 is 2000.00.
    worksheet = return_bg(rental_cca="9000.00", rental_income="7000.00")

    assert worksheet.get(AMT_RENTAL_PROPERTY_ADJUSTMENT).value == D("2000.00")


def test_return_bg_line_11_adds_lines_8_to_10() -> None:
    # Lines 8, 9 and 10 of 1000.00, 500.00 and 250.00 are 1750.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_TAX_SHELTER_ADJUSTMENTS).value == D("1750.00")


def test_return_bg_line_12_adds_lines_1_4_7_and_11() -> None:
    # Line 1 51285.00 plus line 4 5000.00, line 7 0 and line 11 1750.00 is 58035.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_PART_1_SUBTOTAL).value == D("58035.00")


def test_return_bg_line_12_with_no_film_rental_or_tax_shelter_amounts_is_line_1() -> None:
    # With every amount of lines 2, 3, 5, 6, 8, 9 and 10 at 0, line 12 is the taxable income.
    worksheet = return_bg(
        film_cca="0.00",
        film_income="0.00",
        rental_cca="0.00",
        rental_income="0.00",
        shelter_losses="0.00",
        shelter_deductible="0.00",
        limited_partner_carrying="0.00",
    )

    assert worksheet.get(AMT_PART_1_SUBTOTAL).value == D("51285.00")


def test_return_bg_part_9_line_5_adds_lines_2_to_4() -> None:
    # Part 9 line 2 2000.00, line 3 1000.00 and line 4 500.00 are 3500.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_RESOURCE_INCOME_TOTAL).value == D("3500.00")


def test_return_bg_part_9_line_6_is_line_1_less_line_5() -> None:
    # Part 9 line 1 5000.00 less line 5 3500.00 is 1500.00, not below zero.
    worksheet = return_bg()

    assert worksheet.get(AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES).value == D("1500.00")


def test_return_bg_part_9_line_6_is_zero_when_the_income_is_more_than_the_expenditures() -> None:
    # Part 9 line 1 2000.00 less line 5 3500.00 is -1500.00, which is entered as "0".
    worksheet = return_bg(resource_expenditures="2000.00")

    assert worksheet.get(AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES).value == D("0")


def test_return_bg_line_16_adds_the_foreclosure_gains_and_losses() -> None:
    # A foreclosure of proceeds 1000.00 with an adjusted cost base of 1500.00 is a loss of
    # 500.00, so line 16 is -500.00 (a loss in brackets) and the other foreclosure amount is 0.
    worksheet = return_bg(qffp_foreclosure_dispositions=(("1000", "1500", "0"),))

    assert worksheet.get(AMT_MORTGAGE_FORECLOSURE_CAPITAL_GAINS).value == D("-500.00")


def test_return_bg_line_19_adds_lines_16_to_18() -> None:
    # Line 16 0 plus line 17 200.00 plus line 18 100.00 is 300.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_CAPITAL_GAINS_ADJUSTMENTS).value == D("300.00")


def test_return_bg_line_15_is_the_capital_gain_of_the_share_disposition() -> None:
    # The share disposition's gain of 5000.00 less 3000.00 is line 19700 and line 15, 2000.00.
    worksheet = return_bg()

    assert worksheet.get(CAPITAL_GAIN).value == D("2000.00")


def test_return_bg_line_20_is_the_capital_gain_less_line_19() -> None:
    # Line 15 2000.00 minus line 19 300.00 is 1700.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS).value == D("1700.00")


def test_return_bg_line_20_nets_the_foreclosure_loss_through_lines_15_and_19() -> None:
    # The capital gain of 2000.00 less the 500.00 foreclosure loss is 1500.00, and line 19 is
    # -500.00 + 300.00 = -200.00, so line 20 is 1500.00 minus -200.00, which is 1700.00.
    worksheet = return_bg(qffp_foreclosure_dispositions=(("1000", "1500", "0"),))

    assert worksheet.get(CAPITAL_GAIN).value == D("1500.00")
    assert worksheet.get(AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS).value == D("1700.00")


def test_return_bg_line_20_shows_a_loss_in_brackets() -> None:
    # A share disposition of proceeds 1000.00 with an adjusted cost base of 3000.00 is a loss of
    # 2000.00, so line 15 is -2000.00 and line 17 is 0.00 (a part of a loss cannot be exempt); line
    # 19 is 100.00 and line 20 is -2000.00 minus 100.00, which is -2100.00.
    worksheet = return_bg(
        share_dispositions=(("1000", "3000", "0"),),
        treaty_exempt="0.00",
        additional_deductions="0.00",
        net_capital_losses_claimed="0.00",
        net_capital_difference="0.00",
    )

    assert worksheet.get(AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS).value == D("-2100.00")


def test_return_bg_line_22_is_line_20_less_line_21() -> None:
    # Line 20 1700.00 minus line 21 1000.00 (the taxable capital gains, line 12700) is 700.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_CAPITAL_GAINS_DIFFERENCE).value == D("700.00")


def test_return_bg_line_23_is_line_22_when_line_20_is_positive() -> None:
    # Line 20 is 1700.00, positive, so line 23 is the amount from line 22, 700.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_CAPITAL_GAINS_ADDED).value == D("700.00")


def test_return_bg_line_23_is_the_lesser_figure_in_brackets_when_line_20_is_negative() -> None:
    # Lines 17 and 18 of 200.00 and 3000.00 make line 19 3200.00, so line 20 is 2000.00 minus
    # 3200.00 = -1200.00; line 21 is 1000.00 and line 22 is -1200.00 minus 1000.00 = -2200.00
    # (2200.00 without brackets); the lesser of 1000.00 and 2200.00 is 1000.00, in brackets.
    worksheet = return_bg(graduated_rate_estate="3000.00")

    assert worksheet.get(AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS).value == D("-1200.00")
    assert worksheet.get(AMT_CAPITAL_GAINS_DIFFERENCE).value == D("-2200.00")
    assert worksheet.get(AMT_CAPITAL_GAINS_ADDED).value == D("-1000.00")


def test_return_bg_line_23_is_zero_when_line_20_and_line_21_are_zero() -> None:
    # With no share disposition and lines 17 and 18 at 0, lines 15, 19, 20 and 21 are 0, and so
    # are lines 22 and 23.
    worksheet = return_bg(
        share_dispositions=(),
        treaty_exempt="0.00",
        additional_deductions="0.00",
        graduated_rate_estate="0.00",
        net_capital_losses_claimed="0.00",
        net_capital_difference="0.00",
    )

    assert worksheet.get(AMT_NET_CAPITAL_GAINS_AFTER_ADJUSTMENTS).value == D("0")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(AMT_CAPITAL_GAINS_DIFFERENCE).value == D("0")
    assert worksheet.get(AMT_CAPITAL_GAINS_ADDED).value == D("0")


def test_return_bg_line_27_adds_lines_13_14_23_and_26() -> None:
    # Line 13 58035.00 (line 12) plus line 14 1500.00 plus line 23 700.00 plus line 26 600.00 is
    # 60835.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_ADJUSTED_INCOME_WITH_GAINS).value == D("60835.00")


def test_return_bg_line_27_takes_line_23_in_brackets_when_line_20_is_negative() -> None:
    # 58035.00 plus 1500.00 plus -1000.00 plus 600.00 is 59135.00.
    worksheet = return_bg(graduated_rate_estate="3000.00")

    assert worksheet.get(AMT_ADJUSTED_INCOME_WITH_GAINS).value == D("59135.00")


def test_return_bg_line_27_with_no_capital_gain() -> None:
    # Taxable income is 50535.00 with no gain (60000.00 less 565.00 less the losses of other years
    # of 600.00 and 100.00, less the 700.00 of line 22100 and the 5000.00 of line 23200, is
    # 53035.00, less the 150.00 of line 23300, 52885.00, less the 2350.00 of line 24900), so line 12
    # is 50535.00 + 5000.00 + 0.00 + 1750.00 = 57285.00; plus line 14 1500.00, line 23 0 and line
    # 26 600.00 is 59385.00.
    worksheet = return_bg(
        share_dispositions=(),
        treaty_exempt="0.00",
        additional_deductions="0.00",
        graduated_rate_estate="0.00",
        net_capital_losses_claimed="0.00",
        net_capital_difference="0.00",
    )

    assert worksheet.get(AMT_PART_1_SUBTOTAL).value == D("57285.00")
    assert worksheet.get(AMT_ADJUSTED_INCOME_WITH_GAINS).value == D("59385.00")


def test_return_bg_line_24_less_line_25_is_the_gifts_net() -> None:
    # Line 24 3000.00 minus line 25 1000.00 is 2000.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_PUBLICLY_LISTED_GIFTS_NET).value == D("2000.00")


def test_return_bg_line_26_is_30_percent_of_line_24_less_line_25() -> None:
    # 30% of 2000.00 is 600.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT).value == D("600.00")


def test_return_bg_line_26_is_negative_when_line_25_is_more_than_line_24() -> None:
    # Line 24 500.00 minus line 25 1000.00 is -500.00, and 30% of it is -150.00 (not floored).
    worksheet = return_bg(gifts_total="500.00", gifts_line_68231="1000.00")

    assert worksheet.get(AMT_PUBLICLY_LISTED_GIFTS_ADJUSTMENT).value == D("-150.00")


def test_return_bg_line_30_adds_lines_28_and_29() -> None:
    # The T4 slips' boxes 39 and 91 of 1000.00 plus the Form T1212 amount (50% of line 2 of 800.00,
    # 400.00) are 1400.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_SECURITY_OPTIONS_D_TOTAL).value == D("1400.00")


def test_return_bg_line_31_is_40_percent_of_the_security_option_gifts() -> None:
    # 40% of the gifts of 500.00 under a security option plan is 200.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_SECURITY_OPTION_GIFTS_DEDUCTION).value == D("200.00")


def test_return_bg_line_32_is_line_30_less_line_31() -> None:
    # Line 30 1400.00 minus line 31 200.00 is 1200.00, not below zero.
    worksheet = return_bg()

    assert worksheet.get(AMT_SECURITY_OPTIONS_NET).value == D("1200.00")


def test_return_bg_line_32_is_zero_when_the_gifts_are_more_than_line_30() -> None:
    # 40% of the gifts of 4000.00 is 1600.00; line 30 of 1400.00 less 1600.00 is -200.00: "0".
    worksheet = return_bg(security_gifts="4000.00")

    assert worksheet.get(AMT_SECURITY_OPTIONS_NET).value == D("0")


def test_return_bg_line_38_adds_lines_35_to_37() -> None:
    # Lines 35, 36 and 37 of 300.00, 100.00 and 50.00 are 450.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_SECURITY_OPTIONS_D1_TOTAL).value == D("450.00")


def test_return_bg_line_24900_is_the_sum_of_t691_lines_28_29_31_35_36_and_37() -> None:
    # Form T691 Part 1 says each of lines 28 (boxes 39 and 91), 29 (50% of Form T1212 line 2), 31
    # (gifts of publicly listed securities under a security option plan), 35 (boxes 41 and 92), 36
    # (prospector or grubstaker) and 37 (deferred profit-sharing plan) is "included on line 24900 of
    # your return": the return has no separate input for line 24900, it is 1000.00 + 400.00 + 500.00
    # + 300.00 + 100.00 + 50.00 = 2350.00.
    worksheet = return_bg()

    assert worksheet.get(T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL).value == D("1000.00")
    assert worksheet.get(AMT_T1212_LINE_29_DEFERRED_SECURITY_OPTIONS).value == D("400.00")
    assert worksheet.get(AMT_SECURITY_OPTION_PUBLICLY_LISTED_GIFTS).value == D("500.00")
    assert worksheet.get(T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL).value == D("300.00")
    assert worksheet.get(AMT_PROSPECTOR_OR_GRUBSTAKER_DEDUCTION).value == D("100.00")
    assert worksheet.get(AMT_DEFERRED_PROFIT_SHARING_PLAN_DEDUCTION).value == D("50.00")
    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("2350.00")


def test_return_bg_a_filer_who_enters_only_the_t691_boxes_gets_a_line_24900() -> None:
    # A filer who entered only the T4 boxes 39 and 91 of Form T691 line 28 (1000.00) and nothing on
    # the other lines used to have a line 24900 of 0, as the return took it as a separate input. It
    # is now the sum of lines 28, 29, 31, 35, 36 and 37: 1000.00 + 0 + 0 + 0 + 0 + 0 = 1000.00,
    # above 0. It lowers the taxable income, which is the 53635.00 of the return without a line
    # 24900 less 1000.00 (the 400.00 and 500.00 of lines 29 and 31 and the 450.00 of lines 35 to 37
    # of the default return are not entered here): 52635.00.
    worksheet = return_bg(
        security_t1212_line_2="0",
        security_gifts="0",
        security_t4_41_and_92="0",
        prospector="0",
        deferred_profit_sharing="0",
    )

    assert worksheet.get(T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL).value == D("1000.00")
    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("1000.00")
    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value > 0
    assert worksheet.get(TAXABLE_INCOME).value == D("52635.00")


def test_return_bg_line_43_adds_line_39_or_40_and_lines_41_and_42() -> None:
    # Line 39 600.00 (line 40 not applicable), plus line 41 100.00 and line 42 50.00, is 750.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_OTHER_YEARS_LOSSES_TOTAL).value == D("750.00")


def test_return_bg_line_46_is_the_line_39_amount_as_applicable() -> None:
    # Line 39 is 600.00 and line 40 is not applicable, so line 46 is 600.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED).value == D("600.00")


def test_return_bg_line_47_is_zero_when_line_46_is_all_of_line_45() -> None:
    # Line 45, the limited partnership losses of other years, is 600.00 (line 25100, claimed); line
    # 46 is 600.00, so line 47 is 600.00 minus 600.00, 0.00. Line 46 above line 45 is refused as an
    # input error (`ca/amt_limited_partnership_difference_applied` is at most line 45), so line 47
    # is never a loss in brackets.
    worksheet = return_bg()

    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_47_is_line_45_less_line_46_with_a_part_difference() -> None:
    # Line 45 is 800.00 (line 25100, claimed) and line 46 is 600.00, so line 47 is 200.00.
    worksheet = return_bg(
        limited_partnership_losses_of_other_years="800.00",
        limited_partnership_no_election="600.00",
    )

    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT).value == D("200.00")


def test_return_bg_line_50_is_line_48_less_line_49_with_a_part_difference() -> None:
    # Line 48 is 150.00 (line 25200, claimed) and line 49 is 100.00, so line 50 is 50.00.
    worksheet = return_bg(non_capital_losses_of_other_years="150.00")

    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_ADJUSTMENT).value == D("50.00")


def test_return_bg_line_50_is_zero_when_line_49_is_all_of_line_48() -> None:
    # Line 48, the non-capital losses of other years, is 100.00 (line 25200, claimed); line 49 is
    # 100.00, so line 50 is 100.00 minus 100.00, 0.00. Line 49 above line 48 is refused as an input
    # error, so line 50 is never a loss in brackets.
    worksheet = return_bg()

    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_53_adds_lines_47_50_51_and_52() -> None:
    # Lines 47 and 50 of 0.00 and 0.00, and lines 51 and 52 of 0, are 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_LOSSES_AND_DEDUCTIONS_SUBTOTAL).value == D("0.00")


def test_return_bg_line_63_adds_line_53_and_lines_55_to_62() -> None:
    # Line 53 of 0.00, the moving expenses of 200.00 (line 56) and the enhanced CPP
    # contributions of 565.00 (line 58) are 765.00; the other lines are 0.
    worksheet = return_bg()

    assert worksheet.get(AMT_DEDUCTIONS_TOTAL).value == D("765.00")


def test_return_bg_line_68_adds_lines_64_to_67() -> None:
    # Lines 64 to 67 of 300.00, 100.00, 0 and 50.00 are 450.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_NON_DEDUCTIBLE_PROPERTY_EXPENSES).value == D("450.00")


def test_return_bg_line_76_adds_lines_70_to_75() -> None:
    # Line 70 of 150.00, and lines 71 to 75 not applicable, are 150.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES).value == D("150.00")


def test_return_bg_line_77_is_line_69_less_line_76() -> None:
    # Line 69 is 150.00 (the T777 line 17 total of the "Other expenses" of line 8) and line 76 is
    # 150.00, at most it: line 77 is 150.00 minus 150.00, 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_77_is_line_69_less_a_line_76_below_it() -> None:
    # Line 76 of 100.00 (line 70) is below line 69 of 150.00: line 77 is 150.00 minus 100.00, 50.00.
    worksheet = return_bg(commission_employment="100.00")

    assert worksheet.get(AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED).value == D("100.00")
    assert worksheet.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("50.00")


def test_return_bg_line_78_adds_lines_63_68_and_77() -> None:
    # Lines 63, 68 and 77 of 765.00, 450.00 and 0.00 are 1215.00; line 77 is line 69 of 150.00 less
    # line 76 of 150.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_ADJUSTMENTS_BEFORE_RATE_TOTAL).value == D("1215.00")


def test_return_bg_line_80_is_50_percent_of_line_78() -> None:
    # 50% of line 78 of 1215.00 is 607.50.
    worksheet = return_bg()

    assert worksheet.get(AMT_APPLICABLE_RATE_AMOUNT).value == D("607.50")


def test_return_bg_line_80_is_50_percent_of_line_78_with_line_76_equal_to_line_69() -> None:
    # Line 76 of 2000.00 is equal to line 69 of 2000.00 (accepted), so line 77 is 0.00 and line 78
    # is 765.00 plus 450.00 plus 0.00, 1215.00; 50% of it is 607.50.
    worksheet = return_bg(commission_employment="2000.00", other_employment_expenses="2000.00")

    assert worksheet.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("0.00")
    assert worksheet.get(AMT_APPLICABLE_RATE_AMOUNT).value == D("607.50")


def test_return_bg_line_33_adds_line_27_and_line_32() -> None:
    # Line 27 of 60835.00 and line 32 of 1200.00 are 62035.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_ADJUSTED_INCOME_WITH_SECURITY_OPTIONS).value == D("62035.00")


def test_return_bg_line_44_adds_lines_34_38_and_43() -> None:
    # Line 34, the amount from line 33 of 62035.00, line 38 of 450.00 and line 43 of 750.00 are
    # 63235.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL).value == D("63235.00")


def test_return_bg_line_82_adds_line_80_and_line_44() -> None:
    # Line 80 of 607.50 and line 81, the amount from line 44 of 63235.00, are 63842.50.
    worksheet = return_bg()

    assert worksheet.get(AMT_ADJUSTMENTS_AFTER_RATE_TOTAL).value == D("63842.50")


def test_return_bg_lines_84_to_92_are_zero_with_no_dividends_or_capital_gains_deduction() -> None:
    # Return BG claims no dividends, so lines 12000 and 12010 are 0 and lines 84 to 86 are 0; it
    # claims no capital gains deduction (lines 25400 and 25395), so lines 87 to 92 are 0 too.
    worksheet = return_bg()

    for kind in (
        AMT_DIVIDENDS_OTHER_THAN_ELIGIBLE_ADJUSTMENT,
        AMT_AMOUNT_A_MINUS_AMOUNT_B,
        AMT_DIVIDENDS_DIFFERENCE_ADJUSTMENT,
        AMT_DIVIDENDS_ADJUSTMENTS_TOTAL,
        AMT_LIFETIME_EXEMPTION_ADJUSTMENT,
        AMT_ADJUSTMENTS_WITH_LIFETIME_EXEMPTION_TOTAL,
        AMT_QBT_CAPITAL_GAINS_DEDUCTION_DOUBLED,
        AMT_QBT_CAPITAL_GAINS_DEDUCTION_DIFFERENCE,
        AMT_CAPITAL_GAINS_DEDUCTIONS_TOTAL,
    ):
        assert worksheet.get(kind).value == D("0"), kind.identifier


def test_return_bg_line_93_is_line_83_less_line_92() -> None:
    # Line 83, the amount from line 82 of 63842.50, less line 92 of 0, is 63842.50.
    worksheet = return_bg()

    assert worksheet.get(AMT_ADJUSTED_TAXABLE_INCOME).value == D("63842.50")


def test_return_bg_line_94_is_the_basic_exemption_of_177882() -> None:
    worksheet = return_bg()

    assert worksheet.get(AMT_BASIC_EXEMPTION).value == D("177882.00")


def test_return_bg_line_95_is_zero_when_line_93_is_under_the_basic_exemption() -> None:
    # Line 93 of 63842.50 less 177882.00 is below zero, so line 95 is 0 and the filer is not
    # subject to alternative minimum tax.
    worksheet = return_bg()

    assert worksheet.get(AMT_NET_ADJUSTED_TAXABLE_INCOME).value == D("0")


def test_return_bg_line_97_is_zero_when_line_95_is_zero() -> None:
    worksheet = return_bg()

    assert worksheet.get(AMT_GROSS_MINIMUM_AMOUNT).value == D("0")


def test_return_bg_line_98_is_50_percent_of_line_33800_rounded_half_up() -> None:
    # Line 33800 of 3100.21, the credit amounts at the credit rate, times 50% is 1550.105, a tie,
    # rounded half-up to 1550.11.
    worksheet = return_bg()

    assert worksheet.get(AMT_NON_REFUNDABLE_CREDITS_ADJUSTMENT).value == D("1550.11")


def test_return_bg_line_99_is_zero_with_no_donations_and_gifts() -> None:
    worksheet = return_bg()

    assert worksheet.get(AMT_DONATIONS_AND_GIFTS_ADJUSTMENT).value == D("0")


def test_return_bg_line_102_adds_lines_98_to_101() -> None:
    # Line 98 of 1550.11, line 99 of 0, and the caller's lines 100 and 101 not given (0), are
    # 1550.11.
    worksheet = return_bg()

    assert worksheet.get(AMT_CREDITS_ADJUSTMENTS_TOTAL).value == D("1550.11")


def test_return_bg_line_103_is_zero_when_line_97_is_less_than_line_102() -> None:
    # Line 97 of 0 less line 102 of 1550.11 is below zero, so the minimum amount is 0.
    worksheet = return_bg()

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("0")


def test_return_bg_with_200000_employment_income_line_1_is_the_taxable_income() -> None:
    # 200000.00 less the enhanced CPP contributions of 1074.00 (678.00 first additional, the
    # maximum, and 396.00 second additional, the maximum) is 198926.00; plus the 1000.00 taxable
    # capital gains is 199926.00, less the losses of other years of 750.00 (lines 25100, 25200 and
    # 25300: 600.00, 100.00 and 50.00) is 199176.00, less the 200.00 of additional deductions
    # (line 25600) it is 198976.00, less the 700.00 of line 22100 and the 5000.00 of line 23200, it
    # is 193126.00, less the 2350.00 of line 24900, it is
    # 190776.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(TAXABLE_INCOME).value == D("190776.00")


def test_return_bg_with_200000_employment_income_line_63_adds_the_enhanced_cpp() -> None:
    # Line 53 of 0.00, the moving expenses of 200.00 and the enhanced CPP contributions of
    # 1074.00 are 1274.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_DEDUCTIONS_TOTAL).value == D("1274.00")


def test_return_bg_with_200000_employment_income_line_80_is_50_percent_of_line_78() -> None:
    # Line 78 of 1724.00 (1274.00 plus 450.00 plus 0.00, line 77 being 0.00) at 50% is 862.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_APPLICABLE_RATE_AMOUNT).value == D("862.00")


def test_return_bg_with_200000_employment_income_line_82_adds_lines_80_and_81() -> None:
    # Line 1 of 190776.00 plus lines 4, 7 and 11 (5000.00, 0 and 1750.00) is 197526.00; plus lines
    # 14, 23 and 26 (1500.00, 700.00 and 600.00) is 200326.00 and plus line 32 of 1200.00 is
    # 201526.00; plus lines 38 and 43 (450.00 and 750.00) line 44 is 202726.00. Line 80 of 862.00
    # and line 81, the amount from line 44, are 203588.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_ADJUSTMENTS_AFTER_RATE_TOTAL).value == D("203588.00")


def test_return_bg_with_200000_employment_income_line_95_is_over_the_basic_exemption() -> None:
    # Line 93 of 203588.00 less the basic exemption of 177882.00 is 25706.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_NET_ADJUSTED_TAXABLE_INCOME).value == D("25706.00")


def test_return_bg_with_200000_employment_income_line_97_is_20_5_percent_of_line_95() -> None:
    # 20.5% of 25706.00 is 5269.73 exactly.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_GROSS_MINIMUM_AMOUNT).value == D("5269.73")


def test_return_bg_with_200000_employment_income_line_103_is_line_97_less_line_102() -> None:
    # Line 97 of 5269.73 less line 102 of 1572.71 (line 98, 50% of line 33800 of 3145.41, a tie
    # rounded half-up to 1572.71, and lines 99 to 101 of 0) is 3697.02. Line 33800 is 3145.41
    # (21692.47 at the credit rate), 17.41 more than the 3128.00 (21572.42) at the 5700.00 higher
    # income, as the basic personal amount is reduced by income above 177882.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_CREDITS_ADJUSTMENTS_TOTAL).value == D("1572.71")
    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("3697.02")


def test_return_bg_part_2_line_4_adds_the_credits_of_lines_35000_and_40425() -> None:
    # Line 2, the total non-refundable tax credits of line 35000, is 3100.21 (21380.75 at the credit
    # rate, rounded half-up); line 3, the dividend tax credit of line 40425, is 0.00. Line 4 is
    # 3100.21 plus 0.00, 3100.21.
    worksheet = return_bg()

    assert worksheet.get(AMT_CREDITS_TOTAL).value == D("3100.21")


def test_return_bg_part_2_line_5_is_the_federal_tax_less_line_4() -> None:
    # Line 1, the federal tax of line 40400, is 7436.33 on taxable income of 51285.00 (14.5% of it,
    # 7436.325, rounded half-up); line 4 is 3100.21, so line 5 is 7436.33 minus 3100.21, 4336.12.
    worksheet = return_bg()

    assert worksheet.get(AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER).value == D("4336.12")


def test_return_bg_part_2_line_7_is_the_basic_federal_tax() -> None:
    # Line 5 of 4336.12 less line 6, the minimum tax carryover applied of 0.00, is 4336.12.
    worksheet = return_bg()

    assert worksheet.get(AMT_BASIC_FEDERAL_TAX).value == D("4336.12")


def test_return_bg_part_8_lines_4_and_8_add_their_lines() -> None:
    # Line 4 is line 2, the tax payable of 4336.12, plus line 3, the recapture of 0.00: 4336.12.
    # Line 8 adds lines 5 to 7, the split income tax, the logging tax credit and line 41600, all 0:
    # 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_TAX_PAYABLE_WITH_ITC_RECAPTURE).value == D("4336.12")
    assert worksheet.get(AMT_SPLIT_INCOME_AND_CREDITS_TOTAL).value == D("0")


def test_return_bg_part_8_line_9_is_line_4_less_line_8_and_line_11_is_line_9_less_line_10() -> None:
    # Line 9 is 4336.12 minus 0.00, 4336.12. Line 10 is the minimum amount of line 103 of Part 1,
    # 0.00, so line 11 is 4336.12 minus 0.00, 4336.12, not below zero.
    worksheet = return_bg()

    assert worksheet.get(AMT_TAX_PAYABLE_AFTER_CREDITS).value == D("4336.12")
    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_APPLIED).value == D("4336.12")


def test_return_bg_part_8_line_12_claims_nothing_when_no_carryover_is_entered() -> None:
    # The cap is the lesser of line 1, 0.00, and line 11, 4336.12: 0.00. The claim is 0.00, so
    # nothing is applied on line 40427 and basic federal tax is unchanged.
    worksheet = return_bg()

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("0")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("0")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("0")
    assert worksheet.get(CREDITS_AGAINST_BASIC_FEDERAL_TAX).value == D("3100.21")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("4336.12")


def test_return_bg_with_200000_part_2_line_5_is_the_federal_tax_less_line_4() -> None:
    # Line 1, the federal tax of line 40400 on taxable income of 193126.00, is 40234.83; line 4 is
    # 3145.41 (21692.47 at the credit rate), so line 5 is 40234.83 minus 3145.41, 37089.42.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_TAX_PAYABLE_BEFORE_MINIMUM_TAX_CARRYOVER).value == D("37089.42")


def test_return_bg_with_200000_part_8_line_11_is_line_9_less_the_minimum() -> None:
    # Line 9, line 4 of 37089.42 less line 8 of 0.00, is 37089.42; line 10, the minimum amount of
    # 3697.02, leaves line 11 at 37089.42 minus 3697.02, 33392.40.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_APPLIED).value == D("33392.40")


def test_return_bg_with_a_carryover_and_a_claim_within_the_cap_applies_the_claim() -> None:
    # Line 1 is the carryover from 2018 to 2024 of 1000.00; line 11 is 33392.40. The cap is the
    # lesser of them, 1000.00, and the claim of 400.00 is within it, so 400.00 is applied on line 12
    # (line 40427).
    worksheet = return_bg(
        employment_income="200000",
        carryover_from_previous_years="1000",
        carryover_claim="400",
    )

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("1000")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("400")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("400")


def test_return_bg_with_a_carryover_claim_lowers_basic_federal_tax_and_the_t1_line_126() -> None:
    # Part 2 line 7 is line 5 of 37089.42 less line 6 of 400.00: 36689.42. T1 line 124 is 400.00, so
    # line 125 is 3145.41 plus 0.00 plus 400.00, 3545.41, and line 126 is 40234.83 minus 3545.41,
    # 36689.42.
    worksheet = return_bg(
        employment_income="200000",
        carryover_from_previous_years="1000",
        carryover_claim="400",
    )

    assert worksheet.get(AMT_BASIC_FEDERAL_TAX).value == D("36689.42")
    assert worksheet.get(CREDITS_AGAINST_BASIC_FEDERAL_TAX).value == D("3545.41")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("36689.42")


def test_return_bg_with_a_claim_at_the_cap_is_applied_in_full() -> None:
    # The claim of 33392.40 is the line 11 cap when line 1 is larger, so it is applied in full.
    worksheet = return_bg(
        employment_income="200000",
        carryover_from_previous_years="50000",
        carryover_claim="33392.40",
    )

    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("33392.40")


def test_a_carryover_claim_above_line_1_is_refused_naming_both_kinds() -> None:
    # Line 12 "not more than line 1 or 11, whichever is less": the cap is the carryover of 1000.00,
    # and 1000.01 is above it, an input error, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(
            employment_income="200000",
            carryover_from_previous_years="1000",
            carryover_claim="1000.01",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/amt_minimum_tax_carryover_applied 1000.01 is above ca/amt_maximum_carryover_claim 1000"
    )


def test_a_carryover_claim_above_line_11_is_refused_when_line_11_is_the_lesser() -> None:
    # Line 1 of 50000.00 is more than line 11 of 33392.40, so the cap is line 11: 33392.41 is
    # above it.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(
            employment_income="200000",
            carryover_from_previous_years="50000",
            carryover_claim="33392.41",
        )

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: ca/amt_minimum_tax_carryover_applied 33392.41 is above "
        "ca/amt_maximum_carryover_claim 33392.40"
    )


def test_a_claim_is_refused_when_no_carryover_is_available() -> None:
    # With no carryover from earlier years, line 1 is 0.00 and so is the cap: a claim of 0.01 is
    # above it.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(carryover_claim="0.01")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/amt_minimum_tax_carryover_applied 0.01 is above ca/amt_maximum_carryover_claim 0"
    )


def test_return_bg_a_carryover_claim_at_the_cap_flows_to_t1_line_124() -> None:
    # Line 1 is the carryover from 2018 to 2024 of 1000.00 and line 11 is 33392.40, so the cap is
    # 1000.00. The claim of 1000.00 is at the cap, not above it, so it is kept and applied in full
    # on line 40427, T1 line 124. T1 line 125 is 3145.41 plus 0.00 plus 1000.00, 4145.41, and Part 2
    # line 7 is line 5 of 37089.42 less 1000.00, 36089.42; T1 line 126 is 40234.83 minus 4145.41,
    # 36089.42.
    worksheet = return_bg(
        employment_income="200000",
        carryover_from_previous_years="1000",
        carryover_claim="1000",
    )

    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("1000")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_WITHIN_MAXIMUM).value == D("1000")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("1000")
    assert worksheet.get(CREDITS_AGAINST_BASIC_FEDERAL_TAX).value == D("4145.41")
    assert worksheet.get(AMT_BASIC_FEDERAL_TAX).value == D("36089.42")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("36089.42")


def test_return_bg_line_2_is_48_percent_of_the_basic_federal_tax() -> None:
    # Line 2 is 48% of the basic federal tax of 4336.12 (Part 2 line 7): 4336.12 x 0.48 is
    # 2081.3376, rounded to 2081.34.
    worksheet = return_bg()

    assert worksheet.get(AMT_FEDERAL_SURTAX_AT_48_PERCENT).value == D("2081.34")


def test_return_bg_line_3_and_line_4_are_zero_by_default() -> None:
    # No T2203 percentage (line 3 is 0.00), so line 3 has no amount; the filer is not
    # non-resident, so line 4 is the surtax if non-resident, 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS).value == D("0.00")
    assert worksheet.get(AMT_LINE_3_HAS_AMOUNT).value == D("0")
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("0.00")


def test_return_bg_line_4_is_line_2_for_a_non_resident_with_no_line_3_amount() -> None:
    # No line 3 amount, so line 4 is the surtax if non-resident: line 2 of 2081.34 for a
    # non-resident. Line 15 is line 1 of 4336.12 plus 2081.34, which is 6417.46.
    worksheet = return_bg(non_resident=1)

    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("2081.34")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("6417.46")


def test_return_bg_line_3_is_half_of_line_2_when_the_t2203_percentage_is_50() -> None:
    # Line 2 of 2081.34 at 50% is 1040.67, so line 3 has an amount, so line 4 is line 3, 1040.67.
    # Line 15 is 4336.12 plus 1040.67, 5376.79.
    worksheet = return_bg(t2203_percentage="50")

    assert worksheet.get(AMT_FEDERAL_SURTAX_MULTIPLE_JURISDICTIONS).value == D("1040.67")
    assert worksheet.get(AMT_LINE_3_HAS_AMOUNT).value == D("1")
    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("1040.67")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("5376.79")


def test_return_bg_line_4_takes_line_3_over_the_non_resident_surtax() -> None:
    # A non-resident who also has a line 3 amount: line 3 has an amount, so line 4 is line 3,
    # 1040.67, not line 2 of 2081.34. Line 15 is 4336.12 plus 1040.67, 5376.79.
    worksheet = return_bg(t2203_percentage="50", non_resident=1)

    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("1040.67")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("5376.79")


def test_return_bg_line_6_is_the_basic_federal_tax_with_no_surtax() -> None:
    # Line 6 is the basic federal tax (Part 2 line 7) of 4336.12 plus line 4 of 0.00 and the
    # recapture of 0.00: 4336.12.
    worksheet = return_bg()

    assert worksheet.get(AMT_FEDERAL_TAX_WITH_SURTAX_AND_RECAPTURE).value == D("4336.12")


def test_return_bg_line_15_is_line_6_with_no_regular_tax_credits() -> None:
    # Line 15 is line 1 of 4336.12 less line 14, the regular tax credits total of 0.00: 4336.12.
    worksheet = return_bg()

    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("4336.12")


def test_return_bg_line_12_is_the_investment_tax_credit_claim_when_it_is_within_line_i() -> None:
    # The investment tax credit claim of 100.00 is within the T2038 amount I of 150.00, so line 12
    # is 100.00. Line 14 is line 12 of 100.00 plus line 13 of 0.00, 100.00. Line 15 is line 6 of
    # 4336.12 less 100.00, 4236.12.
    worksheet = return_bg(itc_claim="100", amount_i="150")

    assert worksheet.get(AMT_INVESTMENT_TAX_CREDIT).value == D("100")
    assert worksheet.get(AMT_REGULAR_TAX_CREDITS_TOTAL).value == D("100")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("4236.12")


def test_an_investment_tax_credit_claim_above_t2038_amount_i_is_refused() -> None:
    # The claim of 200.00 is above the T2038 amount I of 150.00, an input error, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(itc_claim="200", amount_i="150")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: "
        "ca/amt_investment_tax_credit_claim 200 is above ca/itc_amount_i 150"
    )


def test_return_bg_part_4_is_zero_by_default() -> None:
    # No foreign income, tax or claim, and no T2209 credit: lines 3, 4, 6, 7, 9, 10 and 11 are 0.
    worksheet = return_bg()

    assert worksheet.get(AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE).value == D("0")
    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("0")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("0")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("0")
    assert worksheet.get(AMT_FOREIGN_TAXES_PAID).value == D("0")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("0")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("0")


def test_return_bg_part_4_worked_case_is_line_by_line() -> None:
    # Line 1 1500.00 and line 2 500.00; line 3 is a claim of 300.00, at most line 23 of Part 1
    # (700.00). Line 4 is 1500.00 + 500.00 + 300.00 = 2300.00, and line 6 is 2300.00 times 20.5%,
    # 471.50. Line 7 is 600.00 times 66.6666%, 399.9996, rounded to 400.00; line 8 is 100.00, so
    # line 9 is 500.00. Line 10 is the lesser of 471.50 and 500.00, 471.50. Line 11 is the greater
    # of the federal foreign tax credit, 41.55 (line 3 of Form T2209: 500.00 x 4336.12 / 52185.00
    # = 41.5457, for 600.00 of tax), and 471.50: 471.50. Lines 1, 2, 7 and 8 come from the one
    # country's record: 600.00 of tax on 500.00 of income, with 100.00 of business tax.
    worksheet = return_bg(
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("600", "500", "100"),),
    )

    assert worksheet.get(AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE).value == D("300.00")
    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("2300.00")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("471.50")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("400.00")
    assert worksheet.get(AMT_FOREIGN_TAXES_PAID).value == D("500.00")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("471.50")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("471.50")


def test_return_bg_line_3_accepts_a_claim_equal_to_line_23() -> None:
    # A claim of 700.00 is equal to line 23 of Part 1 (700.00), so it is not above it: line 3 is
    # 700.00, line 4 is 700.00 and line 6 is 700.00 times 20.5%, 143.50.
    worksheet = return_bg(foreign_capital_gains_claim="700")

    assert worksheet.get(AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE).value == D("700")
    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("700")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("143.50")


def test_return_bg_line_3_refuses_a_claim_above_line_23_and_does_not_cap_it() -> None:
    # A claim of 800.00 is above line 23 of Part 1 (700.00): an input error, not capped to 700.00.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(foreign_capital_gains_claim="800")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: ca/amt_foreign_capital_gains_non_taxable_claim 800 is above "
        "ca/amt_capital_gains_added_not_below_zero 700.00"
    )


def test_return_bg_line_3_refuses_a_claim_when_line_23_is_negative() -> None:
    # With graduated rate estate amounts of 3000.00, line 23 of Part 1 is -1000.00 (see the test
    # above it). The most line 3 may claim is line 23 taken as 0, so a claim of 100.00 is above it
    # and is refused, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        return_bg(graduated_rate_estate="3000.00", foreign_capital_gains_claim="100")

    assert str(raised.value).startswith(
        "ca-on/return, instance 1: ca/amt_foreign_capital_gains_non_taxable_claim 100 is above "
        "ca/amt_capital_gains_added_not_below_zero 0"
    )


def test_return_bg_line_3_accepts_a_zero_claim_when_line_23_is_negative() -> None:
    # Line 23 of Part 1 is -1000.00, so the bound of line 3 is 0: a claim of 0.00 is not above it,
    # and line 3 is 0.00, so line 4 and line 6 are 0.00 as well.
    worksheet = return_bg(graduated_rate_estate="3000.00", foreign_capital_gains_claim="0")

    assert worksheet.get(AMT_FOREIGN_CAPITAL_GAINS_NON_TAXABLE).value == D("0")
    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("0")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("0")


def test_return_bg_line_4_takes_a_negative_business_income_into_account() -> None:
    # Foreign business income of -300.00 (a loss, net of expenses) and 500.00 of non-business
    # income: line 4 is 200.00, and line 6 is 200.00 times 20.5%, 41.00.
    worksheet = return_bg(foreign_business_income="-300", foreign_tax_countries=(("0", "500"),))

    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("200.00")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("41.00")


def test_return_bg_line_4_is_zero_when_the_total_of_the_foreign_income_is_below_zero() -> None:
    # Line 1 of -2500.00 and line 2 of 500.00 add to -2000.00, which is not above zero: line 4 is
    # 0, and line 6 is 0 times 20.5%, 0.00.
    worksheet = return_bg(foreign_business_income="-2500", foreign_tax_countries=(("0", "500"),))

    assert worksheet.get(AMT_TOTAL_FOREIGN_INCOME).value == D("0")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("0")


def test_return_bg_line_10_is_line_9_when_the_taxes_paid_are_lower() -> None:
    # Non-business tax of 30.00 is line 7, 30.00 times 66.6666%, 19.99998, rounded to 20.00; with no
    # business tax, line 8 is 0.00, so line 9 is 20.00. Line 6 is 471.50 (for 2300.00 of line 4),
    # so line 10 is the lesser, 20.00. The federal foreign tax credit is the lesser of the 30.00 of
    # tax and line 2 of Form T2209, 500.00 x 4336.12 / 52185.00 = 41.55, so 30.00; line 11 is the
    # greater of 30.00 and 20.00: 30.00.
    worksheet = return_bg(
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("30", "500"),),
    )

    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("20.00")
    assert worksheet.get(AMT_FOREIGN_TAXES_PAID).value == D("20.00")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("20.00")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("30.00")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("30.00")


def test_return_bg_line_11_is_the_t2209_credit_when_it_is_more_than_line_10() -> None:
    # One country with 100.00 of tax on 1000.00 of foreign non-business income: the Form T2209 line
    # 2 is 1000.00 times the basic federal tax of 4336.12 over the net income of 52185.00 (54585.00
    # less the 2350.00 on line 24900 and the 50.00 on line 25300, as Form T2209 note (3) directs),
    # 83.09 (83.0916), and line 3 is the lesser of 100.00 and 83.09, 83.09: the federal foreign tax
    # credit. Part 4 line 2 is 1000.00, so line 4 is 1500.00 + 1000.00 + 300.00 = 2800.00 and line
    # 6 is 574.00; line 7 is 100.00 x 66.6666%, 66.67, so line 9 and line 10 are 66.67, below the
    # credit; line 11 is the greater of 83.09 and 66.67: 83.09.
    worksheet = return_bg(
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("100", "1000"),),
    )

    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("83.09")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("66.67")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("83.09")


def test_return_bg_part_5_is_zero_by_default() -> None:
    # Line 1 is 0.00 (line 103 of Part 1) and line 2 is 0.00, so line 3 is 0.00. Line 4 is the
    # regular net federal tax payable of 4336.12 and line 5 is the surtax of 0.00, so line 6 is
    # 4336.12. Line 7 is 0.00 less 4336.12, below zero, so 0.00. Lines 8 to 11 are 0.00: the filer
    # is not subject to alternative minimum tax.
    worksheet = return_bg()

    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(AMT_REGULAR_NET_TAX_LESS_SURTAX).value == D("4336.12")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("0")
    assert worksheet.get(AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D).value == D("0")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")


def test_return_bg_part_5_line_3_is_line_1_less_the_special_foreign_tax_credit() -> None:
    # The security options of boxes 39 and 91 at 150000.00 (in place of 1000.00) are part of an
    # employment income of 209000.00, so the net income is 203585.00 and line 24900 (151350.00)
    # leaves the taxable income at 51285.00. They add 149000.00 to line 32 of Part 1: line 93 is
    # 212842.50, line 95 is 34960.50 (less the exemption of 177882.00) and line 97 is 20.5% of it,
    # 7166.9025, rounded to 7166.90. The net income is over 177882.00, which takes 541.41 off the
    # supplement of 1591.00 of the basic personal amount (1591.00 x 25703.00 / 75532.00), so it is
    # 15587.59; line 33800 is 3021.70 (20839.34 at the credit rate), line 98 is 1510.85 and line
    # 103 (line 1 of Part 5) is 7166.90 less 1510.85, 5656.05. The foreign figures of the Part 4
    # case above give line 2, the special foreign tax credit, of 471.50, so line 3 is 5656.05 less
    # 471.50, 5184.55. Line 6 is the regular net federal tax payable, 4414.63 (7436.33 on taxable
    # income of 51285.00, less 3021.70), which the federal foreign tax credit lowers: line 3 of
    # Form T2209 is the lesser of the 600.00 of tax and line 2, 500.00 x 4414.63 / 52185.00 =
    # 42.2979, 42.30 (the basic federal tax over the net income of 203585.00 less the 151350.00 of
    # line 24900 and the 50.00 of line 25300), so line 6 is 4414.63 less 42.30, 4372.33, and line 7
    # is 5184.55 less 4372.33, 812.22, which is then line 11 as no investment tax credit is
    # claimed.
    worksheet = return_bg_with_security_options(
        "150000",
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("600", "500", "100"),),
    )

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("5656.05")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("471.50")
    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("5184.55")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("812.22")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("812.22")


def test_return_bg_part_5_line_7_is_line_3_less_line_6_when_it_is_positive() -> None:
    # With the security options at 150000.00 (the case above), line 1 of Part 5 is 5656.05 and line
    # 3 is the same, with no foreign tax credit. Line 6 is the regular net federal tax payable of
    # 4414.63 less a surtax of 0.00, 4414.63, so line 7 is 5656.05 less 4414.63, 1241.42, and line
    # 11 is the same.
    worksheet = return_bg_with_security_options("150000")

    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("5656.05")
    assert worksheet.get(AMT_REGULAR_NET_TAX_LESS_SURTAX).value == D("4414.63")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("1241.42")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1241.42")


def test_return_bg_part_5_line_7_is_zero_when_the_regular_net_tax_is_more() -> None:
    # With employment income of 200000.00, line 1 of Part 5 is the minimum amount of 3697.02 and
    # line 6 is the regular net federal tax payable of 37089.42 (line 5, the surtax, is 0.00). Line
    # 7 is 3697.02 less 37089.42, below zero, so 0.00, and line 11 is 0.00.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("3697.02")
    assert worksheet.get(AMT_REGULAR_NET_TAX_LESS_SURTAX).value == D("37089.42")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("0")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")


def test_return_bg_part_5_line_6_adds_back_a_negative_surtax() -> None:
    # A non-resident with employment income of 8000.00: the total income is 9200.00 (8000.00, the
    # taxable capital gain of 1000.00 and the other income of 200.00) and the net income 3105.00
    # (less the enhanced CPP contributions of 45.00, 1% of 4500.00, the moving expenses of 200.00,
    # the 700.00 of line 22100, the 5000.00 of line 23200 and the 150.00 of line 23300). Taxable
    # income is that less the losses of other years of 750.00, the 200.00 of additional deductions
    # (line 25600) and the 2350.00 of line 24900: -195.00, which line
    # 26000 enters as 0.00. The federal tax is 0.00. The credit amounts are 17953.95 (the basic
    # personal amount of 16129.00, the CPP base contributions of 222.75, the EI premiums of 131.20
    # and the Canada employment amount of 1471.00), at 14.5% 2603.32 (2603.32275), so the basic
    # federal tax is 0.00 less 2603.32, -2603.32. Line 5, the surtax, is 48% of that, -1249.5936,
    # rounded to -1249.59, a negative amount, so line 6 is 0.00 less -1249.59, 1249.59, and line 7
    # is 0.00 with no minimum amount.
    worksheet = return_bg(employment_income="8000", non_resident=1)

    assert worksheet.get(AMT_FEDERAL_SURTAX).value == D("-1249.59")
    assert worksheet.get(AMT_REGULAR_NET_TAX_LESS_SURTAX).value == D("1249.59")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("0")


def test_return_bg_part_5_line_10_is_line_8_less_amount_15_of_part_d() -> None:
    # With the security options at 142000.00 (an employment income of 201000.00 and a net income of
    # 195585.00), line 93 of Part 1 is 204842.50, so line 95 is 26960.50 (less the exemption of
    # 177882.00) and line 97 is 20.5% of it, 5526.9025, rounded to 5526.90. The basic personal
    # amount is 15756.11 and line 33800 is 3046.14, so line 98 is 1523.07; with the federal logging
    # tax credit of 1800.00 (line 100) line 102 is 3323.07 and the minimum amount of line 103 is
    # 2203.83. The federal tax of line 132 is 4390.19 (7436.33 on taxable income of 51285.00 less
    # 3046.14), so line 134 (40600) is 4390.19 less 1800.00, 2590.19. With an investment tax credit
    # claim of 100.00 (within amount I of 150.00), the claim is line 12 of Part 3, and the regular
    # net federal tax payable (line 15) is 4390.19 less 1800.00 less 100.00, 2490.19, which is more
    # than the minimum amount of 2203.83, so line 7 is 0.00. Amount J is the 2590.19 of line 40600
    # less the minimum amount 2203.83, 386.36, so K is the lesser of G (150.00) and J, which is
    # 150.00; amount 15 of 5.00 is within it. Line 8 is the claim, 100.00, and line 9, amount 15 of
    # Part D of Form T2038(IND), is 5.00: line 10 is 95.00 and line 11 is line 7 (0.00) less 95.00,
    # below zero, so 0.00.
    worksheet = return_bg_with_security_options(
        "142000",
        itc_claim="100",
        amount_i="150",
        part_d_amount_15="5",
        logging_credit="1800",
    )

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("2203.83")
    assert worksheet.get(FEDERAL_TAX).value == D("2590.19")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("2490.19")
    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("0")
    assert worksheet.get(ITC_AMOUNT_J).value == D("386.36")
    assert worksheet.get(ITC_AMOUNT_K).value == D("150.00")
    assert worksheet.get(AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D).value == D("95.00")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")


def test_return_bg_part_5_line_10_is_zero_when_amount_15_of_part_d_is_more_than_the_claim() -> None:
    # With line 7 of Part 5 more than 0, amount 15 is limited by K, which is less than the claim
    # (J is line 40600 less the minimum amount and line 7 is the claim less J, so K is below the
    # claim), so amount 15 cannot be above the claim there. With the default security options of
    # 1000.00 the minimum amount is 0.00 and AMT does not apply (line 7 is 0.00), so amount 15 is
    # limited by amount I of 150.00 instead: the claim of 100.00 (line 8) with amount 15 of 150.00,
    # the claim limit I and above the claim, makes line 10 100.00 less 150.00, below zero, so 0.00,
    # and line 11 is line 7, 0.00.
    worksheet = return_bg(
        itc_claim="100",
        amount_i="150",
        part_d_amount_15="150",
        logging_credit="1800",
    )

    assert worksheet.get(AMT_MINIMUM_TAX_AFTER_REGULAR_TAX).value == D("0")
    assert worksheet.get(ITC_AMOUNT_I).value == D("150.00")
    assert worksheet.get(AMT_INVESTMENT_TAX_CREDIT_LESS_PART_D).value == D("0")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")


def test_return_bg_part_6_line_9_is_the_surtax_on_line_7_and_line_14_is_zero_by_default() -> None:
    # Line 1 is the basic federal tax of 4336.12 and line 2 is 0.00 (no split income), so line 3 is
    # 4336.12. Line 4 is 0.00, so line 5 is 4336.12, and line 7 is 4336.12 plus 0.00. Line 8 is
    # 0.00. Line 9 is 48% of line 7: 4336.12 times 0.48 is 2081.3376, rounded half-up to 2081.34.
    # Line 10 is 0.00 (a chosen percentage of 0, as no tax is payable to multiple jurisdictions).
    # Line 11 is 0.00: no amount is on line 10, and the filer is not a non-resident. Line 12 is 0.00
    # and line 13 is 0.00, so line 14 is 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX).value == D("4336.12")
    assert worksheet.get(AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT).value == D("4336.12")
    assert worksheet.get(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX).value == D("4336.12")
    assert worksheet.get(AMT_PART_6_SURTAX_AT_48_PERCENT).value == D("2081.34")
    assert worksheet.get(AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS).value == D("0")
    assert worksheet.get(AMT_PART_6_HAS_AMOUNT_ON_LINE_10).value == 0
    assert worksheet.get(AMT_PART_6_FEDERAL_SURTAX).value == D("0")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("0")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("0")


def test_return_bg_part_6_line_5_is_the_minimum_amount_when_it_is_more_than_line_3() -> None:
    # With the security options of boxes 39 and 91 at 150000.00 and no foreign figures, line 3 is
    # 4414.63 less 0.00, and line 4, the minimum amount, is 5656.05, so line 5 is 5656.05 and line 7
    # is 5656.05 plus 0.00. Line 9 is 48% of 5656.05, 2714.904, rounded to 2714.90. Line 8 is
    # 5656.05 (no special foreign tax credit), so line 12 is 5656.05 with no amount on line 11, and
    # line 14 is 5656.05.
    worksheet = return_bg_with_security_options("150000")

    assert worksheet.get(AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX).value == D("4414.63")
    assert worksheet.get(AMT_GREATER_OF_BASIC_TAX_AND_MINIMUM_AMOUNT).value == D("5656.05")
    assert worksheet.get(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX).value == D("5656.05")
    assert worksheet.get(AMT_PART_6_SURTAX_AT_48_PERCENT).value == D("2714.90")
    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("5656.05")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("5656.05")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("5656.05")


def test_return_bg_part_6_line_12_is_line_8_when_line_11_is_zero() -> None:
    # The security options of 150000.00 with the foreign figures of the Part 5 case above: line 5 is
    # the minimum amount of 5656.05 and line 7 is the same. Line 8 is the net minimum tax payable of
    # 5184.55 (5656.05 less the special foreign tax credit of 471.50), line 9 is 2714.90, and line
    # 10 and line 11 are 0.00, so line 12 is 5184.55 and line 14 is 5184.55.
    worksheet = return_bg_with_security_options(
        "150000",
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("600", "500", "100"),),
    )

    assert worksheet.get(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX).value == D("5656.05")
    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("5184.55")
    assert worksheet.get(AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS).value == D("0")
    assert worksheet.get(AMT_PART_6_FEDERAL_SURTAX).value == D("0")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("5184.55")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("5184.55")


def test_return_bg_part_6_line_11_is_line_9_for_a_non_resident_with_no_amount_on_line_10() -> None:
    # With the security options at 150000.00 and a non-resident (a count of 1), line 10 is 0.00, so
    # the condition on line 10 does not apply, and line 11 is line 9, 2714.90, times the count. Line
    # 12 is 5656.05 plus 2714.90, 8370.95, and line 14 is the same. Line 9 is the surtax on line 7
    # of Part 6, 2714.90, not the surtax on line 2 of Part 3 (2118.90, 48% of 4414.63) that Part 3
    # takes for a non-resident.
    worksheet = return_bg_with_security_options("150000", non_resident=1)

    assert worksheet.get(AMT_PART_6_SURTAX_AT_48_PERCENT).value == D("2714.90")
    assert worksheet.get(AMT_PART_6_HAS_AMOUNT_ON_LINE_10).value == 0
    assert worksheet.get(AMT_PART_6_SURTAX_IF_NON_RESIDENT).value == D("2714.90")
    assert worksheet.get(AMT_PART_6_FEDERAL_SURTAX).value == D("2714.90")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("8370.95")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("8370.95")


def test_return_bg_part_6_line_11_is_line_10_when_line_10_has_an_amount() -> None:
    # With the security options at 150000.00 and 50 as the percentage of Column 5 of line 52220 on
    # Form T2203 (a figure the caller gives), line 10 is 2714.90 times 50%, 1357.45, which is an
    # amount, so line 11 is line 10, 1357.45. Line 12 is 5656.05 plus 1357.45, 7013.50, and line 14
    # is the same.
    worksheet = return_bg_with_security_options("150000", t2203_percentage="50")

    assert worksheet.get(AMT_PART_6_SURTAX_MULTIPLE_JURISDICTIONS).value == D("1357.45")
    assert worksheet.get(AMT_PART_6_HAS_AMOUNT_ON_LINE_10).value == 1
    assert worksheet.get(AMT_PART_6_FEDERAL_SURTAX).value == D("1357.45")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("7013.50")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("7013.50")


def test_return_bg_part_6_line_14_is_line_13_when_the_split_income_tax_is_more_than_line_12() -> (
    None
):
    # Split dividends of 11500.00, as on Return AL: Form T1206 line 22 is 2756.54 (3795.00 less
    # 1038.46) and line 24 is the same. Line 3 is the basic federal tax of line 1 less 2756.54, and
    # line 5 is line 3, as the minimum amount is 0.00, and line 7 is line 5 plus line 6, the basic
    # federal tax again. Line 8 is 0.00 and line 11
    # is 0.00 (a resident, with no tax to multiple jurisdictions), so line 12 is 0.00 and line 14
    # is line 13, 2756.54.
    worksheet = return_bg(
        split_income_dividends="11500",
        split_income_dividends_other_than_eligible="11500",
        other_dividends_received_without_a_slip="10000",
    )
    basic = worksheet.get(AMT_BASIC_FEDERAL_TAX).value

    assert worksheet.get(SPLIT_INCOME_LINE_22).value == D("2756.54")
    assert worksheet.get(AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX).value == basic - D("2756.54")
    assert worksheet.get(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX).value == basic
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("2756.54")
    assert worksheet.get(AMT_PART_6_TAX_WITH_SURTAX).value == D("0")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("2756.54")


def test_return_bg_part_6_line_3_is_floored_for_a_non_resident_with_negative_basic_tax() -> None:
    # A non-resident with employment income of 8000.00, whose basic federal tax is -2603.32 (as the
    # Part 5 case above): line 3 is -2603.32 less 0.00, not below zero, so 0.00, and line 5 is 0.00.
    # Line 7 is 0.00 plus 0.00, so line 9 is 0.00 and line 11, the non-resident's amount, is 0.00
    # too. Part 3 line 2 is -1249.59 for this return, but Part 6 does not take that: line 5, the
    # greater of line 3 and the minimum amount, is 0.00.
    worksheet = return_bg(employment_income="8000", non_resident=1)

    assert worksheet.get(AMT_BASIC_FEDERAL_TAX_LESS_SPLIT_INCOME_TAX).value == D("0")
    assert worksheet.get(AMT_FEDERAL_TAX_UNDER_MINIMUM_TAX).value == D("0")
    assert worksheet.get(AMT_PART_6_SURTAX_AT_48_PERCENT).value == D("0")
    assert worksheet.get(AMT_PART_6_FEDERAL_SURTAX).value == D("0")
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("0")


def test_return_bg_line_41700_is_the_line_139_figure_when_part_5_line_11_is_zero() -> None:
    # Part 5 line 11 is 0.00 (the Part 5 case above), so the condition "line 11 is positive" counts
    # 0 and T1 line 41700 is the line 139 figure: line 132 (the federal tax with the ITC recapture,
    # 4336.12) less line 138 (0.00), 4336.12. Part 6 line 14, 0.00, is not entered on the return.
    # Line 29 of Form T1206 Part 2 is then 4336.12 plus 0.00, and the net federal tax is the same.
    worksheet = return_bg()

    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 0
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("4336.12")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("4336.12")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("4336.12")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("4336.12")


def test_return_bg_line_41700_is_part_6_line_14_when_part_5_line_11_is_positive() -> None:
    # The security options of boxes 39 and 91 at 150000.00 and a non-resident (a count of 1): Part 5
    # line 11 is 1241.42 (line 7, 5656.05 less 4414.63 of line 6, with line 10 at 0.00), which is
    # positive, so the condition "line 11 is positive" counts 1 and T1 line 41700 takes Part 6 line
    # 14 of 8370.95 (the Part 6 case above) in place of the line 139 figure of 4414.63. Line 29 of
    # Form T1206 Part 2 is 8370.95 plus 0.00, and line 30 is the greater of line 24 (0.00) and line
    # 29, 8370.95, so the net federal tax is 8370.95 plus the special taxes of 0.00. The balance
    # owing is 11031.95: the net federal tax of 8370.95 (3956.32 more than the 4414.63 of the return
    # without the minimum tax), the Ontario tax of 2061.00 (line 73: the 1755.24 of line 71 plus the
    # 305.76 of line 72) and the Ontario health premium of 600.00. The Ontario line 72, 24.63% of
    # the Part 5 line 11 of 1241.42, is 305.76 (the worksheet line 3, 2061.00, is under 5710.00, so
    # line 72 is the worksheet line 1).
    worksheet = return_bg_with_security_options("150000", non_resident=1)

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1241.42")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 1
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("8370.95")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("4414.63")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("8370.95")
    assert worksheet.get(SPLIT_INCOME_LINE_29).value == D("8370.95")
    assert worksheet.get(SPLIT_INCOME_LINE_30).value == D("8370.95")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("8370.95")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("11031.95")


def test_return_bg_line_41700_keeps_line_139_when_regular_tax_is_more_than_minimum() -> None:
    # Employment income of 200000.00: the minimum amount on line 103 of Part 1 is 3697.02, but the
    # regular net federal tax less the surtax, line 6 of Part 5, is 37089.42, more than the minimum,
    # so line 7 and line 11 are 0.00 and the condition "line 11 is positive" counts 0. Part 6 line
    # 14 is still computed, 3697.02 (line 12 is the net minimum tax of 3697.02, with no amount on
    # line 11), but it is not entered on line 41700: the line 139 figure, 37089.42, is.
    worksheet = return_bg(employment_income="200000")

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("3697.02")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 0
    assert worksheet.get(AMT_FEDERAL_TAX_PAYABLE_UNDER_MINIMUM_TAX).value == D("3697.02")
    assert worksheet.get(FEDERAL_TAX_LINE_41700).value == D("37089.42")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("37089.42")


def test_return_bg_part_7_lines_are_the_basic_tax_by_default() -> None:
    # Line 1 is 0.00 (no minimum amount) and line 2 is the basic federal tax of 4336.12; line 3 is
    # 0.00, so line 4 is 4336.12. Lines 5 and 6 are 0.00, so line 7 is 0.00 and line 8 is 4336.12.
    # Lines 9 and 10 are 0.00, so line 11 is 0.00. With no foreign taxes paid, the denominator of
    # line 12 is 0.00, so line 12 is 0.00. Line 13 is 4336.12 plus 0.00, 4336.12, and line 14 is
    # 0.00 less 4336.12, below zero, so 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_PART_7_BASIC_TAX_WITH_RECAPTURE).value == D("4336.12")
    assert worksheet.get(AMT_PART_7_CREDITS_TOTAL).value == D("0")
    assert worksheet.get(AMT_PART_7_TAX_LESS_CREDITS).value == D("4336.12")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE).value == D("0")
    assert worksheet.get(AMT_PART_7_FOREIGN_TAXES_PAID).value == D("0")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_SHARE).value == D("0")
    assert worksheet.get(AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE).value == D("4336.12")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("0")


def test_return_bg_part_8_lines_13_to_17_are_zero_by_default() -> None:
    # With no carryover from earlier years, line 1 and line 12 are 0.00, so line 13 is 0.00. Line
    # 14 is the additional 2025 taxes of Part 7 line 14, 0.00, so line 15 is 0.00. No unapplied 2018
    # carryover is entered, so line 16 is 0.00 and line 17 is 0.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("0")
    assert worksheet.get(AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES).value == D("0")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("0")


def test_return_bg_part_7_line_14_is_the_minimum_amount_less_line_13_when_positive() -> None:
    # The security options of boxes 39 and 91 at 150000.00 make the minimum amount on line 1
    # 5656.05. Line 13 is 4414.63 (line 8 of 4414.63 plus line 12 of 0.00), so line 14 is 5656.05
    # less 4414.63, 1241.42, and the same carries into Part 8: line 13 is 0.00, line 15 is 1241.42
    # and line 17, with no unapplied 2018 carryover, is 1241.42.
    worksheet = return_bg_with_security_options("150000")

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("5656.05")
    assert worksheet.get(AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE).value == D("4414.63")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("1241.42")
    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("0")
    assert worksheet.get(AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES).value == D("1241.42")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("1241.42")


def test_return_bg_part_7_line_12_is_line_11_times_the_foreign_credit_share() -> None:
    # The foreign figures of the Part 4 case: 1500.00 and 500.00 of income, a claim of 300.00,
    # 600.00 of non-business tax and 100.00 of business tax, with the security options of 150000.00.
    # Line 9 is the special foreign tax credit of 471.50 (line 11 of Part 4) and line 10 is the
    # federal foreign tax credit, 42.30 (line 3 of Form T2209 for the 600.00 of tax, as in the Part
    # 5 case), so line 11 is 471.50 less 42.30, 429.20. The denominator of line 12 is the foreign
    # taxes paid, 600.00 plus 100.00, 700.00, and the numerator is the foreign taxes paid for the
    # special foreign tax credit, 500.00 (line 9 of Part 4). Line 12 is 429.20 times 500.00 over
    # 700.00, 306.5714, rounded half-up to 306.57. Line 8 is 4414.63, the basic federal tax (Part 7
    # reads line 7 of Part 2, which the federal foreign tax credit does not lower), so line 13 is
    # 4414.63 plus 306.57, 4721.20, and line 14 is 5656.05 less 4721.20, 934.85.
    worksheet = return_bg_with_security_options(
        "150000",
        foreign_business_income="1500",
        foreign_capital_gains_claim="300",
        foreign_tax_countries=(("600", "500", "100"),),
    )

    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("471.50")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("42.30")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_DIFFERENCE).value == D("429.20")
    assert worksheet.get(AMT_PART_7_FOREIGN_TAXES_PAID).value == D("700.00")
    assert worksheet.get(AMT_FOREIGN_TAXES_PAID).value == D("500.00")
    assert worksheet.get(AMT_PART_7_FOREIGN_CREDIT_SHARE).value == D("306.57")
    assert worksheet.get(AMT_PART_7_TAX_LESS_CREDITS_PLUS_SHARE).value == D("4721.20")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("934.85")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("934.85")


def test_return_bg_part_8_line_17_is_line_15_less_the_unapplied_2018_carryover() -> None:
    # The carryover from 2018 to 2024 of 1000.00 with a claim of 400.00 (line 12, within line 1 and
    # line 11) leaves 600.00 on line 13. The claim lowers the basic federal tax to 3936.12, so Part
    # 7 line 8 is 3936.12 and line 13 is 3936.12 with no foreign or recapture amounts. The minimum
    # amount is 0.00, so Part 7 line 14 is 0.00. Line 15 is 600.00 plus 0.00, and the unapplied 2018
    # carryover of 100.00 (line 16) leaves 500.00 on line 17.
    worksheet = return_bg(
        carryover_from_previous_years="1000",
        carryover_claim="400",
        unapplied_2018_carryover="100",
    )

    assert worksheet.get(AMT_PART_7_BASIC_TAX_WITH_RECAPTURE).value == D("3936.12")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("0")
    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("600.00")
    assert worksheet.get(AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES).value == D("600.00")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("500.00")


def test_return_bg_part_8_line_14_adds_the_additional_taxes_when_no_carryover_is_claimed() -> None:
    # The carryover of 1000.00 with no claim leaves line 13 at 1000.00 (line 12 is 0.00). The
    # security options of 150000.00 give Part 7 line 14 of 1241.42, as above, since the basic
    # federal tax of 4414.63 is unchanged with no claim. Line 15 is 1000.00 plus 1241.42, 2241.42,
    # and line 17 is 2241.42 less the unapplied 2018 carryover of 100.00, 2141.42.
    worksheet = return_bg_with_security_options(
        "150000",
        carryover_from_previous_years="1000",
        unapplied_2018_carryover="100",
    )

    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("1241.42")
    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("1000.00")
    assert worksheet.get(AMT_CARRYOVER_BALANCE_WITH_ADDITIONAL_TAXES).value == D("2241.42")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("2141.42")


def test_return_bg_on428_lines_59_to_61_and_72_are_zero_and_line_61_is_line_55_by_default() -> None:
    # No minimum tax carryover is applied (line 40427 is 0.00), so line 59 is 24.63% x 0.00, 0.00,
    # and line 60, the lesser of line 58 (1755.24) and line 59, is 0.00. Line 61 is line 55 less
    # line 60: 1755.24, which lines 62 and 63 carry; line 65 is line 63 less line 64 (0.00), and
    # the surtax on 1755.24 is 0.00. Part 5 line 11 is 0.00, so Worksheet ON428 line 1 is 0.00, line
    # 2 is line 65 (1755.24), line 3 is 1755.24, not more than $5,710, so lines 4 to 6 are 0.00,
    # line 7 (line 68) is 0.00, line 8 is 0.00 less 0.00 and line 9, ON428 line 72, is 0.00 plus
    # 0.00: line 73 is 1755.24 plus 0.00, 1755.24.
    worksheet = return_bg()

    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("1755.24")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("1755.24")
    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("1755.24")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("1755.24")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SURTAX).value == D("1755.24")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("1755.24")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("1755.24")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_6).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_8).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("1755.24")


def test_return_bg_on428_line_59_is_24_63_percent_of_the_carryover_applied() -> None:
    # A carryover from previous years of 3000.00 with a claim of 2000.00 (within line 1 and Part 8
    # line 11): line 40427 is 2000.00. Line 59 is 24.63% x 2000.00 = 492.60; line 58 is 1755.24 (the
    # federal carryover claim does not change the Ontario tax), so line 60, the lesser, is line 59,
    # 492.60, and line 61 is 1755.24 - 492.60 = 1262.64. Lines 62 and 63 carry it, line 64 is 0.00
    # so line 65 is 1262.64, under $5,710, with no surtax: line 69 is 1262.64, line 71 the same (no
    # dividend tax credit), and Worksheet ON428 (Part 5 line 11 is 0.00) gives line 72 of 0.00 whose
    # line 2 is the new line 65, 1262.64, so line 73 is 1262.64.
    worksheet = return_bg(carryover_from_previous_years="3000", carryover_claim="2000")

    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("2000")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("1755.24")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("1755.24")
    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("492.60")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("492.60")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("1262.64")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("1262.64")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SURTAX).value == D("1262.64")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("1262.64")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("1262.64")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("1262.64")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("1262.64")


def test_return_bg_on428_line_60_is_line_58_when_line_58_is_less_than_line_59() -> None:
    # No employment income and 310000.00 of eligible taxable dividends (T5, with the federal credit
    # of 15.0198% x 310000.00 = 46561.38): total income is 311000.00 with the taxable capital gain,
    # the net income 305150.00 and taxable income 301850.00 (less the losses of other years of
    # 750.00, the 200.00 of line 25600 and the 2350.00 of line 24900). The Ontario tax on it is
    # 31729.06 (5.05% to 52886.00, 9.15% to 105775.00, 11.16% to 150000.00, 12.16% to 220000.00 and
    # 13.16% above), and less the credit of 5.05% x 12747.00, 643.72, the tax of line 55 is
    # 31085.34. The Ontario dividend tax credit (10% x 310000.00 = 31000.00) leaves line 58 at
    # 85.34. A carryover from previous years of 20000.00 with a claim of 10000.00 (within line 1 and
    # Part 8 line 11, 16358.29: the basic federal tax 25714.34, which is 74383.73 on taxable income
    # less the credits of 2108.01 and 46561.38, less the minimum amount of 9356.05) makes line 40427
    # 10000.00, so line 59 is 24.63% x 10000.00 = 2463.00, more than line 58: line 60 is line 58,
    # 85.34 (the Ontario tax less the dividend credit, not the whole of line 59). Line 61 is
    # 31085.34 - 85.34 = 31000.00. Line 65 is 31000.00 (line 64 is 0.00): line 66 is 20% x (31000.00
    # - 5710) = 5058.00, line 67 is 36% x (31000.00 - 7307) = 8529.48 and line 68 is 13587.48, so
    # line 69 is 31000.00 + 13587.48 = 44587.48 and line 71 is that less the dividend tax credit of
    # 31000.00, 13587.48. Part 5 line 11 is 0.00: Worksheet ON428 line 1 is 0.00, line 3 is line 2
    # (31000.00), line 6 is line 4 (5058.00) plus line 5 (8529.48), 13587.48, line 7 is 13587.48 and
    # line 8 is 0.00, so line 72 is 0.00 and line 73 is 13587.48.
    # The move of the return takes its line 28 from the employment income, which is 0.00 here, so it
    # claims nothing: the moving expenses and the other income they stand for are 0.00 as well.
    worksheet = return_bg(
        employment_income="0",
        moving_expenses="0",
        carryover_from_previous_years="20000",
        carryover_claim="10000",
        t5_taxable_dividends="310000",
        t5_dividend_tax_credit="46561.38",
    )

    assert worksheet.get(TAXABLE_INCOME).value == D("301850.00")
    assert worksheet.get(AMT_MAXIMUM_CARRYOVER_CLAIM).value == D("16358.29")
    assert worksheet.get(AMT_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("10000")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("31085.34")
    assert worksheet.get(ontario.ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("85.34")
    assert worksheet.get(ontario.MINIMUM_TAX_CARRYOVER_CREDIT).value == D("2463.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX_CARRYOVER_APPLIED).value == D("85.34")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_MINIMUM_TAX_CARRYOVER).value == D("31000.00")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("31000.00")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("13587.48")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SURTAX).value == D("44587.48")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("13587.48")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("31000.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("31000.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_6).value == D("13587.48")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("13587.48")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_8).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("13587.48")


def test_return_bg_worksheet_on428_line_72_is_line_1_when_line_3_is_not_more_than_5710() -> None:
    # The security options of boxes 39 and 91 at 150000.00 make Part 5 line 11 1241.42 (the Part 7
    # case above). Worksheet ON428 line 1 is 24.63% x 1241.42 = 305.76; line 2 is line 65, 1755.24
    # (the taxable income is 51285.00, as in Return BG), and line 3 is 305.76 + 1755.24 = 2061.00,
    # not more than $5,710, so lines 4 and 5 are 0.00 (if negative, enter 0), line 6 is 0.00, line 7
    # (the surtax on line 65) is 0.00, line 8 is 0.00 and line 9 is 305.76 + 0.00: line 72 is line
    # 1, 305.76. Line 73 is line 71 (1755.24) plus line 72, 2061.00.
    worksheet = return_bg_with_security_options("150000")

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1241.42")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("305.76")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("1755.24")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("2061.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_6).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_8).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("305.76")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("1755.24")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("2061.00")


def test_return_bg_worksheet_on428_line_3_over_5710_adds_the_surtax_on_the_additional_tax() -> None:
    # Security options of 250000.00 (an employment income of 309000.00, a net income of 303585.00
    # and so the basic personal amount of 14538.00 and credits of 2869.51) give a minimum amount of
    # 26232.14 (line 93 of 312842.50, line 95 of 134960.50, line 97 of 27666.90 less line 102 of
    # 1434.76) and a basic federal tax of 4566.82, so Part 5 line 11 is 21665.32. Worksheet ON428
    # line 1 is 24.63% x 21665.32 = 5336.17; line 2 is line 65, 1755.24; line 3 is 5336.17 +
    # 1755.24 = 7091.41, more than $5,710: line 4 is 20% x (7091.41 - 5710) = 276.28; line 5 is 36%
    # x (7091.41 - 7307), which is below $7,307, so 0.00; line 6 is 276.28. Line 7 is the surtax of
    # ON428 line 68 on 1755.24, 0.00, so line 8 is 276.28 and line 9, line 72, is 5336.17 + 276.28 =
    # 5612.45. Line 73 is 1755.24 + 5612.45 = 7367.69.
    worksheet = return_bg_with_security_options("250000")

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("21665.32")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("5336.17")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("1755.24")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("7091.41")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_6).value == D("276.28")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("0.00")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_8).value == D("276.28")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("5612.45")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("7367.69")


def test_return_bg_worksheet_on428_line_8_takes_the_surtax_of_line_68_off_line_6() -> None:
    # A salary of 120000.00 with security options of 150000.00 (an employment income of 269000.00,
    # the pensionable and insurable earnings being the salary): taxable income is 110776.00 and the
    # Ontario tax of line 55 is 7200.58 (8068.20 less the credit of 867.62, 5.05% x (12747.00 +
    # 3356.10 + 1077.48)), line 65 is 7200.58 and the surtax of line 68 is 298.12 (20% x 1490.58 =
    # 298.12; the 36% rate starts above 7307.00). The basic federal tax is 16302.42 (19266.59 less
    # the credits of 2964.17) and the minimum amount 17932.64 (line 93 of 272588.00, line 97 of
    # 19414.73 less line 102 of 1482.09), so Part 5 line 11 is 1630.22. Worksheet ON428 line 1 is
    # 24.63% x 1630.22 = 401.52; line 2 is 7200.58; line 3 is 7602.10. Line 4 is 20% x (7602.10 -
    # 5710) = 378.42; line 5 is 36% x (7602.10 - 7307) = 106.24; line 6 is 484.66. Line 7 is the
    # 298.12 of line 68, so line 8 is 484.66 - 298.12 = 186.54 and line 9, line 72, is 401.52 +
    # 186.54 = 588.06. Line 69 is 7200.58 + 298.12 = 7498.70, line 71 the same, and line 73 is
    # 7498.70 + 588.06 = 8086.76.
    worksheet = return_bg_with_security_options("150000", employment_income="120000")

    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SPLIT_INCOME).value == D("7200.58")
    assert worksheet.get(ontario.ONTARIO_SURTAX_BASE).value == D("7200.58")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("298.12")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1630.22")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_1).value == D("401.52")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_2).value == D("7200.58")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_3).value == D("7602.10")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_6).value == D("484.66")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_7).value == D("298.12")
    assert worksheet.get(ontario.WORKSHEET_ON428_LINE_8).value == D("186.54")
    assert worksheet.get(ontario.ONTARIO_MINIMUM_TAX).value == D("588.06")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("7498.70")
    assert worksheet.get(ontario.ONTARIO_TAX_BEFORE_REDUCTION).value == D("8086.76")


# The input errors of `core/at_most` on the T691 Part 1 lines that are parts of the losses of other
# years (T1 lines 25100, 25200 and 25300) and of line 15: "<amount kind> <amount> is above <bound
# kind> <bound>". The amounts are given as the form takes them; a figure above its bound is refused,
# not capped.
ABOVE_LINE_17 = (
    r"ca/amt_treaty_exempt_capital_gains \S+ is above ca/amt_capital_gain_not_below_zero \S+"
)
ABOVE_LINE_25100 = r"ca/amt_limited_partnership_difference_applied \S+ is above ca/limited_partnership_losses_of_other_years_checked \S+"  # noqa: E501
ABOVE_LINE_25200 = (
    r"ca/amt_non_capital_losses_difference \S+ is above ca/non_capital_losses_on_line_25200 \S+"  # noqa: E501
)
ABOVE_LINE_25300 = (
    r"ca/amt_net_capital_losses_difference \S+ is above ca/net_capital_losses_of_other_years \S+"  # noqa: E501
)


def test_return_bg_line_17_of_200_within_line_15_of_2000_is_accepted() -> None:
    # Form T691 Part 1 line 17, the capital gains exempt under a tax treaty, is 200.00 against the
    # 2000.00 capital gain of line 15: line 19 is 200.00 plus 0.00 plus 100.00, 300.00.
    worksheet = return_bg()

    assert worksheet.get(AMT_CAPITAL_GAINS_ADJUSTMENTS).value == D("300.00")


def test_return_bg_line_17_above_line_15_is_refused_not_capped() -> None:
    # 2500.00 of treaty-exempt gains is more than the 2000.00 capital gain of line 15: refused as an
    # input error, not capped to 2000.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_17):
        return_bg(treaty_exempt="2500")


def test_return_bg_line_17_equal_to_line_15_is_accepted() -> None:
    # 2000.00 of treaty-exempt gains is equal to the 2000.00 capital gain of line 15 and to the
    # 2000.00 on line 25600: accepted, and line 19 is 2000.00 plus 0.00 plus 100.00, 2100.00.
    worksheet = return_bg(treaty_exempt="2000", additional_deductions="2000")

    assert worksheet.get(AMT_CAPITAL_GAINS_ADJUSTMENTS).value == D("2100.00")


@pytest.mark.parametrize("election", [False, True], ids=["no_election", "election"])
def test_return_bg_lines_39_or_40_above_line_25100_is_refused(election: bool) -> None:
    # Form T691 Part 1 line 39 or 40, "the difference between those losses and the losses that are
    # deductible for AMT purposes", is at most the limited partnership losses of other years on T1
    # line 25100 (600.00). Line 46 is the one of lines 39 and 40 that applies, so 601.00 in either
    # position is refused, not capped.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_25100):
        if election:
            return_bg(limited_partnership_no_election="0", limited_partnership_election="601")
        else:
            return_bg(limited_partnership_no_election="601", limited_partnership_election="0")


@pytest.mark.parametrize("election", [False, True], ids=["no_election", "election"])
def test_return_bg_lines_39_or_40_equal_to_line_25100_is_accepted(election: bool) -> None:
    # 600.00 of line 39 or line 40 is equal to the 600.00 of T1 line 25100: accepted, and line 46
    # is 600.00, so line 47 is 0.00.
    if election:
        worksheet = return_bg(
            limited_partnership_no_election="0", limited_partnership_election="600"
        )
    else:
        worksheet = return_bg(
            limited_partnership_no_election="600", limited_partnership_election="0"
        )

    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED).value == D("600.00")
    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_41_above_line_25200_is_refused_not_capped() -> None:
    # Form T691 Part 1 line 41, the difference of the non-capital losses of other years, is 101.00
    # against the 100.00 of T1 line 25200: refused as an input error, not capped to 100.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_25200):
        return_bg(non_capital_difference="101")


def test_return_bg_line_41_equal_to_line_25200_is_accepted() -> None:
    # 100.00 of line 41 is equal to the 100.00 of T1 line 25200: accepted, and line 50 is 0.00.
    worksheet = return_bg(non_capital_difference="100")

    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_42_above_line_25300_is_refused_not_capped() -> None:
    # Form T691 Part 1 line 42, the difference of the net capital losses of other years, is 51.00
    # against the 50.00 of T1 line 25300 (line 10 of Form T1436): refused as an input error, not
    # capped to 50.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_25300):
        return_bg(net_capital_difference="51")


def test_return_bg_line_42_equal_to_line_25300_is_accepted() -> None:
    # 50.00 of line 42 is equal to the 50.00 of T1 line 25300: accepted, and line 43 is the 750.00
    # of lines 39, 41 and 42 (600.00, 100.00 and 50.00).
    worksheet = return_bg(net_capital_difference="50")

    assert worksheet.get(AMT_OTHER_YEARS_LOSSES_TOTAL).value == D("750.00")


def test_return_bg_lines_39_and_40_both_filled_in_are_refused_not_added() -> None:
    # Form T691 Part 1 "complete line 39 or 40 depending on your situation": 300.00 on line 39 (no
    # election) and 300.00 on line 40 (election) are each within the 600.00 of T1 line 25100 and
    # together equal to it, but the form asks for one of the two, so lines 43 and 46 would add the
    # second on top of the first. Refused as an input error naming both lines, not added.
    with pytest.raises(
        InputOutOfRangeError,
        match=r"ca/amt_lines_39_and_40_both 1 is refused: line 39 and line 40 are both filled in",
    ):
        return_bg(limited_partnership_no_election="300", limited_partnership_election="300")


def test_return_bg_lines_39_and_40_with_line_40_of_0_are_accepted() -> None:
    # Line 39 of 600.00 with line 40 of 0.00 is the single claim of Return BG: the count of both is
    # 0 and line 46 is 600.00.
    worksheet = return_bg(limited_partnership_no_election="600", limited_partnership_election="0")

    assert worksheet.get(AMT_LINES_39_AND_40_BOTH_CHECKED).value == 0
    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_DIFFERENCE_APPLIED).value == D("600.00")


ABOVE_LINE_13 = r"ca/amt_unapplied_2018_carryover \S+ is above ca/amt_carryover_balance \S+"


def test_return_bg_line_16_above_line_13_is_refused_not_capped() -> None:
    # Form T691 Part 8 line 17 subtracts line 16 from line 15 (line 13 plus line 14), so the
    # unapplied 2018 carryover is part of line 13. The carryover of 1000.00 with a claim of 400.00
    # leaves 600.00 on line 13; 601.00 on line 16 is refused, not capped to 600.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_13):
        return_bg(
            carryover_from_previous_years="1000",
            carryover_claim="400",
            unapplied_2018_carryover="601",
        )


def test_return_bg_line_16_with_no_carryover_balance_is_refused() -> None:
    # With no carryover from previous years line 13 is 0.00, so any unapplied 2018 carryover is
    # refused; it would otherwise take the additional taxes of line 14 down with it.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_13):
        return_bg(unapplied_2018_carryover="50")


def test_return_bg_line_16_equal_to_line_13_is_accepted() -> None:
    # 600.00 on line 16 is equal to the 600.00 on line 13: accepted, and line 17 is 0.00.
    worksheet = return_bg(
        carryover_from_previous_years="1000",
        carryover_claim="400",
        unapplied_2018_carryover="600",
    )

    assert worksheet.get(AMT_CARRYOVER_BALANCE).value == D("600.00")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("0.00")


# Form T691 Part 1 line 17 "Part of total capital gains included on line 15 that is exempt from
# Canadian tax under a tax treaty (included on line 25600 of your return)": the amount is at most
# line 25600 "Additional deductions" (`ca/additional_deductions_total`), which the return deducts it
# in.
# An amount above it is refused, not capped.
ABOVE_LINE_25600 = (
    r"ca/amt_treaty_exempt_capital_gains_checked \S+ is above ca/additional_deductions_total \S+"
)


def test_return_bg_line_17_of_200_above_line_25600_of_0_is_refused_not_capped() -> None:
    # The treaty-exempt gains of 200.00 on line 17 are included on line 25600, so with no
    # additional deductions on line 25600 the amount is refused, not taken as 0.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_25600):
        return_bg(additional_deductions="0")


def test_return_bg_line_17_one_cent_above_line_25600_is_refused_not_capped() -> None:
    # The bound is inclusive: 200.01 on line 17 against 200.00 on line 25600 is refused as an
    # input error, not capped to 200.00.
    with pytest.raises(
        InputAboveBoundError,
        match=(
            r"ca/amt_treaty_exempt_capital_gains_checked 200\.01 "
            r"is above ca/additional_deductions_total 200\.00"
        ),
    ):
        return_bg(treaty_exempt="200.01", additional_deductions="200.00")


def test_return_bg_line_17_equal_to_line_25600_is_accepted() -> None:
    # 200.00 on line 17 is equal to the 200.00 on line 25600: accepted, and the amount on line 17
    # is kept at 200.00.
    worksheet = return_bg(treaty_exempt="200.00", additional_deductions="200.00")

    assert worksheet.get(AMT_TREATY_EXEMPT_CAPITAL_GAINS_WITHIN_ADDITIONAL_DEDUCTIONS).value == D(
        "200.00"
    )


# The input errors of the two T691 checks against T1 lines 22100, 22400 and 23200: the sum of the
# T691 amounts that are included on line 22100 (lines 10 and 64 to 67) against line 22100, and
# Part 9 line 1 against the sum of lines 22100, 22400 and 23200 (the return's
# `ca/amt_lines_22100_22400_and_23200`). The message names the amount kind of the sum, not the
# single line.
ABOVE_LINE_22100 = (
    r"ca/amt_expenses_included_on_line_22100 \S+ is above "
    r"ca/carrying_charges_interest_expenses_and_other_expenses \S+"
)
ABOVE_LINES_22100_22400_23200 = (
    r"ca/amt_resource_expenditures \S+ is above ca/amt_lines_22100_22400_and_23200 \S+"
)


@pytest.mark.parametrize(
    ("line", "value"),
    [
        ("limited_partner_carrying", "251"),
        ("non_deductible_interest", "301"),
        ("life_insurance_premiums", "101"),
        ("financing_expenses", "1"),
        ("investment_counsel_fees", "51"),
    ],
    ids=[
        "line_10_limited_partner_carrying_charges",
        "line_64_interest",
        "line_65_life_insurance_premiums",
        "line_66_financing_expenses",
        "line_67_investment_counsel_fees",
    ],
)
def test_return_bg_t691_line_10_or_64_to_67_with_the_sum_above_line_22100_is_refused(
    line: str, value: str
) -> None:
    # The four T691 lines 64 to 67 and line 10 are each "included on line 22100 of your return".
    # Line 22100 is 700.00 here (the T691 amounts of 250.00, 300.00, 100.00 and 50.00), so one
    # dollar more on any of them makes their sum 701.00, above 700.00: refused as an input error,
    # not capped to 700.00.
    overrides: dict[str, Any] = {line: value}
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_22100):
        return_bg(**overrides)


def test_return_bg_t691_sum_equal_to_line_22100_is_accepted() -> None:
    # 300.00 on line 10 and 250.00 on line 64 make the same 700.00 as the 100.00 of line 65 and the
    # 50.00 of line 67 with line 22100 at 700.00: accepted, and the checked amount is 700.00.
    worksheet = return_bg(limited_partner_carrying="300", non_deductible_interest="250")

    assert worksheet.get(AMT_EXPENSES_INCLUDED_ON_LINE_22100_CHECKED).value == D("700.00")


def test_return_bg_part_9_line_1_above_lines_22100_22400_and_23200_is_refused() -> None:
    # Part 9 line 1 is 5701.00 against 700.00 of line 22100, 0.00 of line 22400 and 5000.00 of line
    # 23200 (the 5700.00 of the three lines): refused as an input error, not capped.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINES_22100_22400_23200):
        return_bg(resource_expenditures="5701")


def test_return_bg_part_9_line_1_equal_to_lines_22100_22400_and_23200_is_accepted() -> None:
    # 5700.00 on Part 9 line 1 is equal to the 5700.00 of the three lines: accepted, the checked
    # amount is 5700.00, and line 6 is 5700.00 less the 3500.00 of line 5, 2200.00.
    worksheet = return_bg(resource_expenditures="5700")

    assert worksheet.get(AMT_RESOURCE_EXPENDITURES_CHECKED).value == D("5700.00")
    assert worksheet.get(AMT_RESOURCE_PROPERTY_AND_FLOW_THROUGH_SHARES).value == D("2200.00")


ABOVE_LINE_69 = (
    r"ca/amt_non_deductible_office_expenses \S+ is above ca/other_employment_expenses \S+"
)


def test_return_bg_line_70_above_line_69_is_refused_not_capped() -> None:
    # Line 70 of 151.00 is above line 69, the other employment expenses of line 22900 (the T777
    # line 17 total of 150.00): an input error, refused and not capped to 150.00.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_69):
        return_bg(commission_employment="151.00")


@pytest.mark.parametrize(
    "line",
    [
        "legal_and_accounting",
        "repayment_of_salary_and_wages",
        "excess_epsp",
        "forfeited_salary_deferral",
        "wage_loss_replacement",
    ],
)
def test_return_bg_lines_71_to_75_pushing_the_sum_above_line_69_are_refused(line: str) -> None:
    # The sum of lines 70 to 75 is 150.00 plus 1.00, 151.00, above line 69 of 150.00 (line 22900):
    # refused as an input error, whichever of lines 71 to 75 is 1.00 more.
    overrides: dict[str, Any] = {line: "1.00"}
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_69):
        return_bg(**overrides)


def test_return_bg_a_total_of_600000_against_line_69_of_0_is_refused() -> None:
    # Lines 70 to 75 of 600000.00 in all (legal and accounting expenses, line 71) against line 69
    # of 0.00 (no T777 line 17 total): line 77 would be -600000.00, and the check refuses it.
    with pytest.raises(InputAboveBoundError, match=ABOVE_LINE_69):
        return_bg(
            commission_employment="0",
            legal_and_accounting="600000",
            other_employment_expenses="0",
        )


def test_return_bg_lines_70_to_75_equal_to_line_69_are_accepted() -> None:
    # Line 70 of 100.00 and line 71 of 50.00 add to 150.00, equal to line 69 of 150.00: accepted,
    # the checked amount is 150.00 and line 77 is 0.00.
    worksheet = return_bg(commission_employment="100.00", legal_and_accounting="50.00")

    assert worksheet.get(OTHER_EMPLOYMENT_EXPENSES).value == D("150.00")
    assert worksheet.get(AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED).value == D("150.00")
    assert worksheet.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_zero_against_zero_is_accepted() -> None:
    # No lines 70 to 75 and no line 22900: 0.00 is at most 0.00, accepted, and line 77 is 0.00.
    worksheet = return_bg(commission_employment="0", other_employment_expenses="0")

    assert worksheet.get(AMT_NON_DEDUCTIBLE_OFFICE_EXPENSES_CHECKED).value == D("0.00")
    assert worksheet.get(AMT_OFFICE_EXPENSES_ADJUSTMENT).value == D("0.00")


def test_return_bg_line_59_for_a_resident_of_ontario_is_refused_not_added() -> None:
    # Form T691 Part 1 line 59 "Deduction for PPIP premiums on self-employment income from line
    # 22300 of your return (Quebec only)": Return BG's filer is a resident of Ontario on December
    # 31, 2025 (not resident 0), who has no Quebec line 22300, so 100000.00 on line 59 is refused as
    # an input error, not added to line 63.
    with pytest.raises(
        InputOutOfRangeError,
        match=r"ca/amt_ppip_premiums_in_ontario 1 is refused: line 59 is Quebec only",
    ):
        return_bg(ppip_premiums="100000")


def test_return_bg_line_59_of_0_is_accepted() -> None:
    worksheet = return_bg(ppip_premiums="0")

    assert worksheet.get(AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED).value == 0


def test_return_bg_line_59_of_a_filer_who_is_not_a_resident_of_ontario_is_accepted() -> None:
    # The filer was not a resident of Ontario on December 31, 2025 (not resident 1), so line 59 is
    # not refused for being an Ontario return.
    worksheet = return_bg(ppip_premiums="100000", not_resident_of_ontario=1)

    assert worksheet.get(AMT_PPIP_PREMIUMS_IN_ONTARIO_CHECKED).value == 0
