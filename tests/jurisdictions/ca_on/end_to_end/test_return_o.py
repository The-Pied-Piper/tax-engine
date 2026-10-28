"""CA-ON 2025 end to end: return o."""

from __future__ import annotations

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION,
    BUSINESS_INVESTMENT_LOSS_REDUCTION,
    BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE,
    CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024,
    CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FHSA_DEDUCTION,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, step_3


def return_o() -> Worksheet:
    """Return O's inputs, as in `returns/2025_return_o.yaml`: a pension and the Step 3 lines."""
    return compute(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_pensions_and_superannuation="60000",
        rpp_deduction="3000",
        support_payments_deduction="6000",
        support_payments_made_total="6000",
        total_carrying_charges="300",
        total_interest_expenses="200",
        business_investment_loss="10000",
        income_tax_deducted="6000",
    )


def test_return_os_deductions_are_14500_and_its_net_income_before_adjustments_45500() -> None:
    # Return O: other pensions and superannuation of 60000 (line 11500), the only income, so total
    # income is 60000. RPP deduction 3000 (line 20700); a business investment loss of 10000 (line
    # 21699) with no earlier capital gains deduction, so Form T1436 line 15 is 0 and line 18 is
    # 10000, 50% of it 5000.00 (line 21700); the deductible support payments 6000 (line 22000); the
    # Federal Worksheet's carrying charges 300 and interest expenses 200 (line 22100, 500). Line
    # 23300 is 3000 + 5000.00 + 6000 + 500 = 14500.00, line 23400 is 60000 - 14500.00 = 45500.00,
    # and net income (line 23600) and taxable income are the same.
    worksheet = return_o()

    assert worksheet.get(TOTAL_INCOME).value == D("60000")
    assert worksheet.get(CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES).value == D("500.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024).value == D("0")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION_AVAILABLE).value == D("0")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION).value == D("0")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION).value == D("10000")
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("5000.00")
    assert worksheet.get(FHSA_DEDUCTION).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("14500.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("45500.00")
    assert worksheet.get(NET_INCOME).value == D("45500.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("45500.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "carrying_charges_interest_expenses_and_other_expenses: total_carrying_charges 300 "
        "+ total_interest_expenses 200 + total_other_expenses 0 = 500"
    ) in rendered
    assert (
        "business_investment_loss_reduction_available: "
        "capital_gains_deductions_claimed_1985_to_2024 0 "
        "less other_business_investment_loss_reductions_1986_to_2024 0 = 0"
    ) in rendered
    assert (
        "business_investment_loss_reduction: lesser of "
        "business_investment_loss_reduction_available 0 and business_investment_loss 10000 = 0"
    ) in rendered
    assert (
        "business_investment_loss_after_reduction: business_investment_loss 10000 "
        "less business_investment_loss_reduction 0 = 10000"
    ) in rendered
    assert (
        "allowable_business_investment_loss: 50% of business_investment_loss_after_reduction "
        "10000 (half-up to 0.01)"
    ) in rendered
    assert (
        "deductions_from_total_income: rpp_deduction 3000 + rrsp_deduction 0 "
        "+ fhsa_deduction 0 "
        "+ elected_split_pension_deduction 0 + union_dues 0 + uccb_repayment 0 "
        "+ child_care_expenses 0 + disability_supports_deduction 0 "
        "+ allowable_business_investment_loss 5000 "
        "+ moving_expenses_deduction 0 "
        "+ support_payments_deduction_checked 6000 "
        "+ carrying_charges_interest_expenses_and_other_expenses 500 "
        "+ cpp_deduction_on_self_employment_and_other_earnings 0 "
        "+ cpp_enhanced_contributions_on_return 0 + exploration_and_development_expenses 0 "
        "+ other_employment_expenses 0 "
        "+ clergy_residence_deduction 0 "
        "+ other_deductions 0 + t746_deduction_on_return 0 "
        "+ t1043_deduction_on_return 0 "
        "+ foreign_property_tax_over_limit 0 + total_split_income 0 = 14500"
    ) in rendered
    assert (
        "net_income_before_adjustments: total_income 60000 "
        "less deductions_from_total_income 14500 = 45500"
    ) in rendered
    assert (
        "net_income: net_income_before_adjustments 45500 less social_benefits_repayment 0, "
        "not below 0 = 45500"
    ) in rendered


def test_return_os_taxes_follow_from_its_taxable_income_of_45500() -> None:
    # Taxable income 45500.00: 14.5% federally, 6597.50, less 14.5% of 18129.00, the basic personal
    # amount 16129.00 plus the pension income amount 2000.00 (line 31400: 60000 of other pensions
    # on line 11500, capped at 2000), 2628.71 (the Canada employment amount is 0 with no employment
    # income): 3968.79. Ontario: 5.05% of 45500.00 is 2297.75, less 5.05% of 14509.00, the basic
    # personal amount 12747.00 plus the pension income amount 1762.00 (ON428 line 27: the lesser of
    # 1762 and line 31400), 732.70: 1565.05, no surtax, no tax reduction, no LIFT credit; the health
    # premium on taxable income of more than 38500 but not more than 48000 is 450, so the Ontario
    # tax is 2015.05 and the total payable 3968.79 + 2015.05 = 5983.84. The income tax deducted of
    # 6000 leaves a refund of 16.16.
    worksheet = return_o()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("6597.50")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3968.79")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1565.05")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("2015.05")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5983.84")
    assert worksheet.get(TOTAL_CREDITS).value == D("6000")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-16.16")


@pytest.mark.parametrize(
    ("carrying_charges", "interest_expenses", "other_expenses", "line_22100"),
    [
        # Carrying charges 300 and interest expenses 200, as in Return O.
        ("300", "200", "0", "500.00"),
        # One distinct power of two for each line, so a line left out or added twice changes it.
        ("1", "2", "4", "7"),
        ("0", "0", "0", "0"),
    ],
)
def test_line_22100_adds_the_worksheets_lines_1_to_3(
    carrying_charges: str, interest_expenses: str, other_expenses: str, line_22100: str
) -> None:
    # Federal Worksheet "Line 22100": line 4 "Add lines 1 to 3. Enter this amount on line 22100 of
    # your return."
    worksheet = step_3(
        total_carrying_charges=carrying_charges,
        total_interest_expenses=interest_expenses,
        total_other_expenses=other_expenses,
    )

    assert worksheet.get(CARRYING_CHARGES_INTEREST_EXPENSES_AND_OTHER_EXPENSES).value == D(
        line_22100
    )
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D(line_22100)
