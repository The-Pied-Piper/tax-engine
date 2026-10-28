"""CA-ON 2025 end to end: return br (Charts B and C for a vehicle bought in 2022 and a lease entered
into in 2023)."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InvalidRecordError
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
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_AVAILABLE,
    BUSINESS_HOME_EXPENSES_BUSINESS_PART,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_HOME_INCOME_LIMIT,
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

# Return BR's T2125: gross sales 50000, the six expense lines 1500 + 1200 + 800 + 2500 + 5361.12 +
# 1500 = 12861.12 and the motor vehicle expenses of 3138.88 from Charts A to C (the seven lines
# 16000.00, as in Return BQ), and the business-use-of-home expenses 600 + 500 + 300 + 200 + 400 =
# 2000.
BUSINESS = {
    "gross_sales": "50000",
    "advertising": "1500",
    "insurance": "1200",
    "office_expenses": "800",
    "professional_fees": "2500",
    "rent": "5361.12",
    "utilities": "1500",
    # Charts A to C: the sales tax rate of the province (the HST of 13%).
    "vehicle_sales_tax_rate": "13",
    "home_heat": "600",
    "home_electricity": "500",
    "home_insurance": "300",
    "home_maintenance": "200",
    "home_property_taxes": "400",
}
FURNITURE = ("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0")
# Charts A to C for two passenger vehicles whose year chooses the figures (Chart B footnote "For
# passenger vehicles bought after 2000 and before 2024, the amount is $300"; Chart C endnotes 11 to
# 13 for leases entered into in 2023): Chart A line 16 (line 9281) is 2101.88 for the owned one,
# bought in 2022 (Chart B interest capped at 300 ÷ 30 × 183 = 1830.00, line 13 of 4530.00 x 7000 /
# 16000 = 1981.875, which rounds up to 1981.88, parking fees 120) and 1037.00 for the leased one,
# leased in 2023 (Chart C leasing cost 2550.00, line 13 of 3908 x 3000 / 12000 = 977.00,
# supplementary insurance 60): 2101.88 + 1037.00 = 3138.88. A year that does not apply is 0.
OWNED = {
    "business_kilometres": "7000",
    "total_kilometres": "16000",
    "fuel_and_oil": "1200",
    "insurance": "900",
    "licence_and_registration": "150",
    "maintenance_and_repairs": "450",
    "interest_payable": "3000",
    "interest_days": "183",
    "parking_fees": "120",
    "purchase_year": "2022",
    "lease_year": "0",
}
LEASED = {
    "business_kilometres": "3000",
    "total_kilometres": "12000",
    "fuel_and_oil": "600",
    "insurance": "450",
    "maintenance_and_repairs": "108",
    "other_expenses_10": "200",
    "lease_charges": "2550",
    "lease_payments_before": "1000",
    "lease_days": "183",
    "list_price": "40000",
    "supplementary_insurance": "60",
    "purchase_year": "0",
    "lease_year": "2023",
}


def run_br(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return BR's inputs, as in `returns/2025_return_br.yaml`: a sole proprietor whose only
    activity is a business.

    One T2125 statement for the business: gross sales of 50000 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 16000 on seven lines (the motor vehicle line, 3138.88, from Charts A to
    C)
    and 2000 of capital cost allowance (Class 8, opening UCC 10000, claim 2000), 18000 in all (line
    9368), so line 9369 is 32000; business-use-of-home
    expenses of 2000, so line 9945 is 2000 and line 9946 and T1 line 13500 are 30000.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (FURNITURE,),
        "business_vehicles_rows": (OWNED, LEASED),
    }
    return run("0", (), "0", "0", "0", "0", "0", business_statements=({**statement, **overrides},))


def return_br(**overrides: Any) -> Worksheet:
    """The return form's worksheet of `run_br`: T1 lines 13500, 27 and below."""
    return run_br(**overrides)["ca-on/return"][0]


def statement_br(**overrides: Any) -> Worksheet:
    """The worksheet of Return BR's one T2125 statement: its lines, as the form computes them."""
    return run_br(**overrides)["ca/t2125"][0]


def test_return_brs_gross_business_income_is_50000_on_line_8299_and_t1_line_13499() -> None:
    # Part 3A: amount 3A 50000 less amount 3B 0 is amount 3C 50000; the quick method is not used
    # (amounts 3D and 3E 0), so amount 3F is 0 and amount 3G, which is line 8000, is 50000 + 0.
    # Line 8290 and line 8230 are 0 (no reserves, other income or recapture), so amount 3O is 0
    # and line 8299, "Line 8000 plus amount 3O", is 50000. T1 line 13499 is line 8299.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_SALES_SUBTOTAL).value == D("50000")
    assert worksheet.get(BUSINESS_QUICK_METHOD_ASSISTANCE).value == D("0")
    assert worksheet.get(BUSINESS_ADJUSTED_GROSS_SALES).value == D("50000")
    assert worksheet.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(BUSINESS_OTHER_INCOME_WITH_RECAPTURE).value == D("0")
    assert worksheet.get(BUSINESS_RESERVES_AND_OTHER_INCOME).value == D("0")
    assert worksheet.get(BUSINESS_GROSS_INCOME).value == D("50000")


def test_return_brs_gross_profit_is_the_gross_income_with_no_cost_of_goods_sold() -> None:
    # Part 3D: amount 3P is line 8299, 50000; amounts 3Q to 3U and line 8500 are 0, so amount 3V
    # and line 8518 are 0 and line 8519 is 50000 - 0, which is amount 4A.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT).value == D("50000")
    assert worksheet.get(BUSINESS_COST_OF_GOODS_SUBTOTAL).value == D("0")
    assert worksheet.get(BUSINESS_COST_OF_GOODS_SOLD).value == D("0")
    assert worksheet.get(BUSINESS_GROSS_PROFIT).value == D("50000")
    assert worksheet.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("50000")


def test_return_brs_area_a_claims_2000_on_line_9936() -> None:
    # Area A, Class 8: column 7 is 10000 + 0 - 0 = 10000; with no additions column 18 is 0,
    # column 19 is 10000 and the maximum is 10000 x 20% = 2000.00; 2000 is claimed. Amount ii
    # is 2000; with no personal part or business-use-of-home CCA (amount 7K), line 9936 is 2000.
    # No class has a negative column 7 or is empty, so there is no recapture and no terminal loss.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("2000")
    assert worksheet.get(BUSINESS_CCA_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert worksheet.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("0")


def test_return_brs_closing_ucc_is_8000_for_class_8() -> None:
    # Column 22 is column 7 less column 21: 10000 - 2000 = 8000, next year's column 2.
    worksheet = statement_br()

    closing = worksheet.get(BUSINESS_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records] == [[D("8"), D("8000")]]


def test_return_brs_total_expenses_are_18000_and_net_income_before_adjustments_32000() -> None:
    # Amounts 4B to 4T add to 16000 (the seven lines entered), amount 4U (line 9936) is 2000 and
    # amount 4V (line 9270) is 0: line 9368 is 18000. Line 9369 is 50000 - 18000 = 32000.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("18000")
    assert worksheet.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000")


def test_return_brs_sole_proprietor_has_no_partnership_amounts() -> None:
    # No partner (count 0): amount 5A is line 9369, 32000; amounts 5B and 9974 and 6A to 6E are 0,
    # so amount 5C is 32000, line 9943 is 0 and amount 5D is 32000.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_SHARE_OF_NET_INCOME).value == D("32000")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("0")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS).value == D("0")
    assert worksheet.get(BUSINESS_PARTNERSHIP_TOTAL).value == D("32000")
    assert worksheet.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("32000")


def test_return_brs_business_use_of_home_claim_is_2000() -> None:
    # Part 7: amount 7H is 600 + 500 + 300 + 200 + 0 + 400 + 0 = 2000, amount 7I is 0, so amount
    # 7J is 2000; amounts 7K and 7L are 0, so amount 7M is 2000. Amount 7N is amount 5D, 32000.
    # Amount 7O is 2000 - 32000, negative, so 0. Amount 7P, the lesser of 2000 and 32000, is 2000,
    # which is line 9945.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_HOME_EXPENSES_SUBTOTAL).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_AVAILABLE).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_INCOME_LIMIT).value == D("32000")
    assert worksheet.get(BUSINESS_HOME_CARRY_FORWARD).value == D("0")
    assert worksheet.get(BUSINESS_HOME_ALLOWABLE_CLAIM).value == D("2000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES).value == D("2000")


def test_return_brs_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Line 9946 is amount 5D less line 9945: 32000 - 2000 = 30000, T1 line 22 and line 13500; the
    # net self-employment income (line 27) is 30000 + 0 + 0 + 0 + 0.
    result = run_br()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000")


def test_return_brs_line_27_is_in_total_income_and_flows_down() -> None:
    # Line 27 (30000) is in total income (line 15000) and there is no other income, so total
    # income, net income and taxable income are 30000. With no employment income and Schedule 8
    # Part 4 not completed, no CPP or EI is computed.
    worksheet = return_br()

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_return_brs_motor_vehicle_line_9281_is_3138_88_from_two_charts_a_to_c() -> None:
    # Owned vehicle, bought in 2022 ("bought after 2000 and before 2024, the amount is $300"):
    # Chart B 300 ÷ 30 × 183 days = 54900 ÷ 30 = 1830.00, and the lesser of that and 3000 is
    # 1830.00; no Chart C (line 28 is 0). Chart A: 1200 + 1830.00 + 900 + 150 + 450 = 4530.00, and
    # 4530 x 7000 ÷ 16000 = 1981.875, a half cent, which rounds up to 1981.88, plus parking fees of
    # 120 is 2101.88. Leased vehicle, lease entered into in 2023 (endnotes 11 to 13): no Chart B
    # (line 19 is 0). Chart C: 42353 plus 13% (5505.89) is 47858.89 and 40000 is less, so the
    # greater is 47858.89, 85% of it is 40680.0565 = 40680.06 (line 24); 950 plus 13% is 1073.50,
    # x 183 ÷ 30 is 6548.35 (line 25) and line 26 is 6548.35 - 1000 = 5548.35; 36000 plus 13% is
    # 40680.00, and 40680.00 x 2550 ÷ 40680.06 = 2549.9962 = 2550.00 (line 27), so the leasing cost
    # is the lesser of 5548.35 and 2550.00. Chart A: 600 + 450 + 108 + 2550 + 200 = 3908.00, and
    # 3908 x 3000 ÷ 12000 = 977.00, plus supplementary insurance of 60 is 1037.00. Line 9281 is
    # 2101.88 + 1037.00 = 3138.88.
    worksheet = statement_br()

    owned, leased = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert (owned.line_12, owned.line_13, owned.line_19, owned.line_28, owned.line_16) == (
        D("4530.00"),
        D("1981.88"),
        D("1830.00"),
        D("0.00"),
        D("2101.88"),
    )
    assert (leased.line_12, leased.line_13, leased.line_19, leased.line_28, leased.line_16) == (
        D("3908.00"),
        D("977.00"),
        D("0.00"),
        D("2550.00"),
        D("1037.00"),
    )
    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("3138.88")


def test_return_brs_other_expenses_still_add_to_16000_and_the_rest_is_return_bqs() -> None:
    # The six other expense lines are 1500 + 1200 + 800 + 2500 + 5361.12 + 1500 = 12861.12 and
    # line 9281 is 3138.88: 16000.00, so line 9368 is 18000.00 and line 9369 is 32000.00 as in
    # Return BQ.
    worksheet = statement_br()

    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("18000")
    assert worksheet.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000")


def test_return_brs_line_9281_is_the_same_with_the_vehicles_listed_the_other_way_round() -> None:
    worksheet = statement_br(business_vehicles_rows=(LEASED, OWNED))

    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("3138.88")
    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("18000")


def test_return_brs_one_vehicle_alone_gives_its_own_line_16() -> None:
    assert statement_br(business_vehicles_rows=(OWNED,)).get(
        BUSINESS_MOTOR_VEHICLE_EXPENSES
    ).value == D("2101.88")
    assert statement_br(business_vehicles_rows=(LEASED,)).get(
        BUSINESS_MOTOR_VEHICLE_EXPENSES
    ).value == D("1037.00")


def test_return_brs_years_choose_the_figures_so_the_2025_set_gives_other_amounts() -> None:
    # The same vehicles with the years of the chart body (2025). Owned: Chart B 350 ÷ 30 × 183 =
    # 2135.00, line 12 is 1200 + 2135.00 + 900 + 150 + 450 = 4835.00, 4835 x 7000 ÷ 16000 =
    # 2115.3125 = 2115.31, line 16 2235.31. Leased: 44706 plus 13% is 50517.78 (line 23), line 24 is
    # 42940.1130 = 42940.11, line 25 is 1243.00 x 183 ÷ 30 = 7582.30, line 26 is 6582.30, line 27 is
    # 42940.00 x 2550 ÷ 42940.11 = 2549.9935 = 2549.99, line 12 is 600 + 450 + 108 + 2549.99 + 200 =
    # 3907.99, 3907.99 x 3000 ÷ 12000 = 976.9975 = 977.00, line 16 is 1037.00. Line 9281 is
    # 2235.31 + 1037.00 = 3272.31.
    owned = {**OWNED, "purchase_year": "2025"}
    leased = {**LEASED, "lease_year": "2025"}

    worksheet = statement_br(business_vehicles_rows=(owned, leased))

    first, second = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert (first.line_19, first.line_13, first.line_16) == (
        D("2135.00"),
        D("2115.31"),
        D("2235.31"),
    )
    assert (second.line_28, second.line_12, second.line_16) == (
        D("2549.99"),
        D("3907.99"),
        D("1037.00"),
    )
    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("3272.31")


def test_return_brs_owned_vehicle_bought_in_2000_is_refused_for_its_interest() -> None:
    # No limit is printed for a vehicle bought in 2000 or earlier, and this one has interest days.
    with pytest.raises(InvalidRecordError, match="item 1: .*vehicle bought in 2000$"):
        statement_br(business_vehicles_rows=({**OWNED, "purchase_year": "2000"}, LEASED))


def test_return_brs_leased_vehicle_has_no_purchase_year_and_is_not_refused() -> None:
    # Vehicle 2 has no interest days, so its purchase year of 0 needs no limit.
    worksheet = statement_br(business_vehicles_rows=(LEASED,))

    assert worksheet.get(BUSINESS_MOTOR_VEHICLE_EXPENSES).value == D("1037.00")


def test_return_brs_trace_names_each_line_of_the_business_statement() -> None:
    # The lines of the one T2125 statement, then those of the return form.
    result = run_br()
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
        "business_motor_vehicle_expenses: item 1: line 12 4530, line 13 1981.88, line 19 1830, "
        "line 28 0, line 16 2101.88",
        "business_motor_vehicle_expenses: item 2: line 12 3908, line 13 977, line 19 0, "
        "line 28 2550, line 16 1037",
        "business_motor_vehicle_expenses: item 1 2101.88 + item 2 1037 = 3138.88",
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
