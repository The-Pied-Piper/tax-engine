"""CA-ON 2025 end to end: return bb."""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_ADJUSTED_GROSS_SALES,
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_COST_OF_GOODS_SOLD,
    BUSINESS_COST_OF_GOODS_SUBTOTAL,
    BUSINESS_GROSS_INCOME,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT,
    BUSINESS_GROSS_PROFIT,
    BUSINESS_HOME_ALLOWABLE_CLAIM,
    BUSINESS_HOME_CARRY_FORWARD,
    BUSINESS_HOME_CCA,
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_AVAILABLE,
    BUSINESS_HOME_EXPENSES_BUSINESS_PART,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_HOME_INCOME_LIMIT,
    BUSINESS_HOME_PERSONAL_USE_PART,
    BUSINESS_INCOME,
    BUSINESS_MOTOR_VEHICLE_EXPENSES,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    BUSINESS_OTHER_INCOME_WITH_RECAPTURE,
    BUSINESS_PARTNER_OTHER_AMOUNTS,
    BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL,
    BUSINESS_PARTNERSHIP_TOTAL,
    BUSINESS_QUICK_METHOD_ASSISTANCE,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_RESERVES_AND_OTHER_INCOME,
    BUSINESS_SALES_SUBTOTAL,
    BUSINESS_SHARE_OF_NET_INCOME,
    BUSINESS_TERMINAL_LOSS,
    BUSINESS_TOTAL_EXPENSES,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BB's T2125: gross sales 50000, the six expense lines 1500 + 1200 + 800 + 2500 + 6000 +
# 1500 = 13500 and the motor vehicle expenses of 2500 from Charts A to C (the seven lines 16000),
# and the business-use-of-home expenses 600 + 500 + 300 + 200 + 400 = 2000.
BUSINESS = {
    "gross_sales": "50000",
    "advertising": "1500",
    "insurance": "1200",
    "office_expenses": "800",
    "professional_fees": "2500",
    "rent": "6000",
    "utilities": "1500",
    # Charts A to C: the sales tax rate of the province (the HST of 13%); the vehicle is in
    # `VEHICLE`.
    "vehicle_sales_tax_rate": "13",
    "home_heat": "600",
    "home_electricity": "500",
    "home_insurance": "300",
    "home_maintenance": "200",
    "home_property_taxes": "400",
}
FURNITURE = ("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0")
# Charts A to C for one leased passenger vehicle used half for business: Chart A line 16 (line
# 9281) is 2500, from the interest of Chart B (400) and the leasing cost of Chart C (2147).
VEHICLE = {
    "business_kilometres": "5000",
    "total_kilometres": "10000",
    "fuel_and_oil": "1000",
    "insurance": "600",
    "maintenance_and_repairs": "200",
    "other_expenses_10": "653",
    "interest_payable": "400",
    "interest_days": "183",
    "lease_charges": "2550",
    "lease_days": "183",
    "list_price": "60000",
}


def run_bb(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return BB's inputs, as in `returns/2025_return_bb.yaml`: a sole proprietor whose only
    activity is a business.

    One T2125 statement for the business: gross sales of 50000 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 16000 on seven lines (the motor vehicle line, 2500, from Charts A to C)
    and 2000 of capital cost allowance (Class 8, opening UCC 10000, claim 2000), 18000 in all (line
    9368), so line 9369 is 32000; business-use-of-home
    expenses of 2000, so line 9945 is 2000 and line 9946 and T1 line 13500 are 30000.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (FURNITURE,),
        "business_vehicles_rows": (VEHICLE,),
    }
    return run("0", (), "0", "0", "0", "0", "0", business_statements=(statement,), **overrides)


def return_bb(**overrides: Any) -> Worksheet:
    """The return form's worksheet of `run_bb`: T1 lines 13500, 27 and below."""
    return run_bb(**overrides)["ca-on/return"][0]


def statement_bb(**overrides: Any) -> Worksheet:
    """The worksheet of Return BB's one T2125 statement: its lines, as the form computes them."""
    return run_bb(**overrides)["ca/t2125"][0]


def test_return_bbs_gross_business_income_is_50000_on_line_8299_and_t1_line_13499() -> None:
    # Part 3A: amount 3A 50000 less amount 3B 0 is amount 3C 50000; the quick method is not used
    # (amounts 3D and 3E 0), so amount 3F is 0 and amount 3G, which is line 8000, is 50000 + 0.
    # Line 8290 and line 8230 are 0 (no reserves, other income or recapture), so amount 3O is 0
    # and line 8299, "Line 8000 plus amount 3O", is 50000. T1 line 13499 is line 8299.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_SALES_SUBTOTAL).value == D("50000")
    assert worksheet.get(BUSINESS_QUICK_METHOD_ASSISTANCE).value == D("0")
    assert worksheet.get(BUSINESS_ADJUSTED_GROSS_SALES).value == D("50000")
    assert worksheet.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(BUSINESS_OTHER_INCOME_WITH_RECAPTURE).value == D("0")
    assert worksheet.get(BUSINESS_RESERVES_AND_OTHER_INCOME).value == D("0")
    assert worksheet.get(BUSINESS_GROSS_INCOME).value == D("50000")


def test_return_bbs_gross_profit_is_the_gross_income_with_no_cost_of_goods_sold() -> None:
    # Part 3D: amount 3P is line 8299, 50000; amounts 3Q to 3U and line 8500 are 0, so amount 3V
    # and line 8518 are 0 and line 8519 is 50000 - 0, which is amount 4A.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT).value == D("50000")
    assert worksheet.get(BUSINESS_COST_OF_GOODS_SUBTOTAL).value == D("0")
    assert worksheet.get(BUSINESS_COST_OF_GOODS_SOLD).value == D("0")
    assert worksheet.get(BUSINESS_GROSS_PROFIT).value == D("50000")
    assert worksheet.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("50000")


def test_return_bbs_area_a_claims_2000_on_line_9936() -> None:
    # Area A, Class 8: column 7 is 10000 + 0 - 0 = 10000; with no additions column 18 is 0,
    # column 19 is 10000 and the maximum is 10000 x 20% = 2000.00; 2000 is claimed. Amount ii
    # is 2000; with no personal part or business-use-of-home CCA (amount 7K), line 9936 is 2000.
    # No class has a negative column 7 or is empty, so there is no recapture and no terminal loss.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("2000")
    assert worksheet.get(BUSINESS_CCA_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("0")


def test_return_bbs_closing_ucc_is_8000_for_class_8() -> None:
    # Column 22 is column 7 less column 21: 10000 - 2000 = 8000, next year's column 2.
    worksheet = statement_bb()

    closing = worksheet.get(BUSINESS_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records] == [[D("8"), D("8000")]]


def test_return_bbs_total_expenses_are_18000_and_net_income_before_adjustments_32000() -> None:
    # Amounts 4B to 4T add to 16000 (the seven lines entered), amount 4U (line 9936) is 2000 and
    # amount 4V (line 9270) is 0: line 9368 is 18000. Line 9369 is 50000 - 18000 = 32000.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("18000")
    assert worksheet.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000")


def test_return_bbs_sole_proprietor_has_no_partnership_amounts() -> None:
    # No partner (count 0): amount 5A is line 9369, 32000; amounts 5B and 9974 and 6A to 6E are 0,
    # so amount 5C is 32000, line 9943 is 0 and amount 5D is 32000.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_SHARE_OF_NET_INCOME).value == D("32000")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("0")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS).value == D("0")
    assert worksheet.get(BUSINESS_PARTNERSHIP_TOTAL).value == D("32000")
    assert worksheet.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("32000")


def test_return_bbs_business_use_of_home_claim_is_2000() -> None:
    # Part 7: amount 7H is 600 + 500 + 300 + 200 + 0 + 400 + 0 = 2000, amount 7I is 0, so amount
    # 7J is 2000; amounts 7K and 7L are 0, so amount 7M is 2000. Amount 7N is amount 5D, 32000.
    # Amount 7O is 2000 - 32000, negative, so 0. Amount 7P, the lesser of 2000 and 32000, is 2000,
    # which is line 9945.
    worksheet = statement_bb()

    assert worksheet.get(BUSINESS_HOME_EXPENSES_SUBTOTAL).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_AVAILABLE).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_INCOME_LIMIT).value == D("32000")
    assert worksheet.get(BUSINESS_HOME_CARRY_FORWARD).value == D("0")
    assert worksheet.get(BUSINESS_HOME_ALLOWABLE_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES).value == D("2000")


def test_return_bbs_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Line 9946 is amount 5D less line 9945: 32000 - 2000 = 30000, T1 line 22 and line 13500; the
    # net self-employment income (line 27) is 30000 + 0 + 0 + 0 + 0.
    result = run_bb()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000")


def test_return_bbs_line_27_is_in_total_income_and_flows_down() -> None:
    # Line 27 (30000) is in total income (line 15000) and there is no other income, so total
    # income, net income and taxable income are 30000. With no employment income and Schedule 8
    # Part 4 not completed, no CPP or EI is computed.
    worksheet = return_bb()

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_return_bbs_motor_vehicle_line_9281_is_2500_from_charts_a_to_c() -> None:
    # Chart B: 350 ÷ 30 × 183 days = 2135.00, and the lesser of that and 400 is 400. Chart C: 44706
    # plus 13% is 50517.78 and 1100 plus 13% is 1243.00 (38000 plus 13% is 42940.00); 60000 is the
    # greater of 60000 and 50517.78, 85% of it is 51000.00, 1243.00 x 183 ÷ 30 is 7582.30, and
    # 42940.00 x 2550 ÷ 51000.00 is 2147.00, so the leasing cost is the lesser of 7582.30 and
    # 2147.00. Chart A: 1000 + 400 + 600 + 200 + 2147 + 653 = 5000, and 5000 x 5000 ÷ 10000 = 2500.
    worksheet = statement_bb()

    (vehicle,) = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert vehicle.line_19 == D("400.00")
    assert vehicle.line_28 == D("2147.00")
    assert vehicle.line_12 == D("5000.00")
    assert vehicle.line_13 == D("2500.00")
    assert vehicle.line_16 == D("2500.00")
    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("2500.00")


def test_return_bbs_trace_names_each_line_of_the_business_statement() -> None:
    # The lines of the one T2125 statement, then those of the return form.
    result = run_bb()
    trace = (*result["ca/t2125"][0].trace, *result["ca-on/return"][0].trace)
    rendered = EnglishTraceRenderer().render_all(trace)

    for rendered_line in (
        "business_sales_subtotal: business_gross_sales 50000 less business_sales_adjustments 0 "
        "= 50000",
        "business_quick_method_assistance: business_quick_method_gst_hst 0 "
        "less business_quick_method_remitted 0 = 0",
        "business_adjusted_gross_sales: business_sales_subtotal 50000 "
        "+ business_quick_method_assistance 0 = 50000",
        "business_recaptured_cca: item 1 class 8: column 7 10000 is not negative: recapture 0",
        "business_other_income_with_recapture: business_other_income 0 "
        "+ business_recaptured_cca 0 = 0",
        "business_reserves_and_other_income: business_reserves_deducted_last_year 0 "
        "+ business_other_income_with_recapture 0 = 0",
        "business_gross_income: business_adjusted_gross_sales 50000 "
        "+ business_reserves_and_other_income 0 = 50000",
        "business_gross_income_for_gross_profit: business_gross_income 50000 = 50000",
        "business_cost_of_goods_sold: business_cost_of_goods_subtotal 0 "
        "less business_closing_inventory 0 = 0",
        "business_gross_profit: business_gross_income_for_gross_profit 50000 "
        "less business_cost_of_goods_sold 0 = 50000",
        "business_gross_income_before_expenses: business_gross_profit 50000 = 50000",
        "business_cca_table_claim: item 1 class 8: column 7 10000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 10000, "
        "maximum 20% of column 19 = 2000 (half-up to 0.01), claim 2000",
        "business_cca_claim_less_personal_part: business_cca_table_claim 2000 "
        "less business_cca_personal_part 0 = 2000",
        "business_cca_claim: business_cca_claim_less_personal_part 2000 "
        "less business_home_cca 0 = 2000",
        "business_terminal_loss: item 1 class 8: column 7 10000 with property left: "
        "terminal loss 0",
        "business_other_expenses_with_terminal_loss: business_other_expenses 0 "
        "+ business_terminal_loss 0 = 0",
        "business_closing_ucc: item 1 class 8: column 7 10000 less claim 2000 = 8000",
        "business_motor_vehicle_expenses: item 1: line 12 5000, line 13 2500, line 19 400, "
        "line 28 2147, line 16 2500",
        "business_motor_vehicle_expenses: item 1 2500 = 2500",
        "business_net_income_before_adjustments: business_gross_income_before_expenses 50000 "
        "less business_total_expenses 18000 = 32000",
        "business_share_of_net_income: business_net_income_before_adjustments 32000, "
        "chosen as business_partner_checked is 0",
        "business_partnership_total: business_share_of_net_income 32000 "
        "+ business_journalism_labour_tax_credit 0 + business_partner_gst_hst_rebate 0 = 32000",
        "business_net_income_after_adjustments: business_partnership_total 32000 "
        "less business_partner_other_amounts 0 = 32000",
        "business_home_expenses_available: business_home_expenses_business_part 2000 "
        "+ business_home_cca 0 + business_home_carried_forward 0 = 2000",
        "business_home_income_limit: business_net_income_after_adjustments 32000, "
        "not below 0 = 32000",
        "business_home_carry_forward: business_home_expenses_available 2000 "
        "less business_home_income_limit 32000, not below 0 = 0",
        "business_home_allowable_claim: lesser of business_home_expenses_available 2000 "
        "and business_home_income_limit 32000 = 2000",
        "business_home_expenses: business_home_allowable_claim 2000 = 2000",
        "business_income: business_net_income_after_adjustments 32000 "
        "less business_home_expenses 2000 = 30000",
        'business_line_is_business: condition 1 "business income on line 13500": '
        "business_income_line_checked 1, applies",
        "business_line_is_business: condition 1 applies, so 1",
        'business_line_is_professional: condition 1 "professional income on line 13700": '
        "business_income_line_checked 1, does not apply",
        "business_line_is_professional: no condition applies, so 0",
        'business_line_is_commission: condition 1 "commission income on line 13900": '
        "business_income_line_checked 1, does not apply",
        "business_line_is_commission: no condition applies, so 0",
        "net_on_business_line: business_income 30000 for each of 1 "
        "business_line_is_business = 30000",
        "net_on_professional_line: business_income 30000 for each of 0 "
        "business_line_is_professional = 0",
        "net_on_commission_line: business_income 30000 for each of 0 "
        "business_line_is_commission = 0",
        "gross_on_business_line: business_gross_income 50000 for each of 1 "
        "business_line_is_business = 50000",
        "gross_on_professional_line: business_gross_income 50000 for each of 0 "
        "business_line_is_professional = 0",
        "gross_on_commission_line: business_gross_income 50000 for each of 0 "
        "business_line_is_commission = 0",
        "business_income: item 1 t1139_business_income_on_return 30000 = 30000",
        "net_self_employment_income: business_income 30000 + professional_income 0 "
        "+ commission_income 0 + farming_income 0 + fishing_income 0 = 30000",
    ):
        assert rendered_line in rendered, rendered_line


def personal_part_statement_bb(personal_part: str, **business: str) -> Worksheet:
    """Return BB's T2125 statement with a personal part of CCA entered (line 9936)."""
    statement: dict[str, Any] = {
        "business": {**BUSINESS, "cca_personal_part": personal_part, **business},
        "business_cca_classes_rows": (FURNITURE,),
        "business_vehicles_rows": (VEHICLE,),
    }
    result = run("0", (), "0", "0", "0", "0", "0", business_statements=(statement,))
    return result["ca/t2125"][0]


def test_a_personal_part_equal_to_amount_ii_is_accepted_and_leaves_line_9936_at_zero() -> None:
    # Amount ii is 2000, so a personal part of 2000 is at most amount ii: 2000 - 2000 = 0.
    statement = personal_part_statement_bb("2000")

    assert statement.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("0")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("0")


def test_a_personal_part_above_amount_ii_is_not_refused_and_the_form_arithmetic_stands() -> None:
    # 2000.01 is more than the 2000 of amount ii, and no printed bound applies: line 9936 is
    # 2000 less 2000.01 = -0.01, and amount 7K is 0, so the claim is -0.01 as printed.
    statement = personal_part_statement_bb("2000.01")

    assert statement.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("-0.01")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("-0.01")


def test_amount_7k_above_the_limit_is_not_refused_and_the_form_arithmetic_stands() -> None:
    # Amount ii is 2000 and the personal part 0, so line 9936 is 2000; amount 7K of 2000.01 is no
    # longer refused against that 2000, and line 9936 is 2000 less 2000.01 = -0.01 as printed.
    statement = personal_part_statement_bb("0", home_cca="2000.01")

    assert statement.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("2000")
    assert statement.get(BUSINESS_HOME_CCA).value == D("2000.01")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("-0.01")


def test_amount_7i_above_amount_7h_is_not_refused_and_amount_7j_is_negative() -> None:
    # 2000.01 is more than the 2000 of amount 7H, and no printed bound applies: amount 7J would be
    # 2000 less 2000.01 = -0.01, which the lesser of it and the income limit takes as the claim.
    statement = personal_part_statement_bb("0", home_personal_use_part="2000.01")

    assert statement.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("-0.01")
    assert statement.get(BUSINESS_HOME_ALLOWABLE_CLAIM).value == D("-0.01")


def test_amount_7i_equal_to_amount_7h_is_accepted_and_leaves_amount_7j_at_zero() -> None:
    # Amount 7H is 600 + 500 + 300 + 200 + 400 = 2000, so amount 7I may be 2000: 7J is 0.
    statement = personal_part_statement_bb("0", home_personal_use_part="2000")

    assert statement.get(BUSINESS_HOME_PERSONAL_USE_PART).value == D("2000")
    assert statement.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("0")
