"""CA-ON 2025 end to end: return ey (returns/2025_return_ey.yaml).

Return EY has two Form T2042 (farming) statements and two Form T2121 (fishing) statements. Statement
1 of each form is a sole proprietor's business with a recapture and a terminal loss of capital cost
allowance, a motor vehicle (Chart A), a minister's allocation of the immediate expensing limit and,
on the T2042, the previous year's inventory adjustments and the non-arm's length expenses of the
T2043 Chart A; on the T2121 the repairs. Statement 2 of each form is a partner whose
business-use-of-home expenses exceed the income that limits them.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    FARM_CCA_CLAIM,
    FARM_CCA_CLAIM_LESS_PERSONAL_PART,
    FARM_CCA_TABLE_CLAIM,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_SUBTOTAL,
    FARM_CLOSING_UCC,
    FARM_EXPENSES_SUBTOTAL,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_HOME_CARRY_FORWARD,
    FARM_HOME_EXPENSES,
    FARM_HOME_EXPENSES_AVAILABLE,
    FARM_HOME_EXPENSES_BUSINESS_PART,
    FARM_HOME_EXPENSES_SUBTOTAL,
    FARM_HOME_INCOME_LIMIT,
    FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FARM_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FARM_MOTOR_VEHICLE_EXPENSES,
    FARM_NET_INCOME_AFTER_ADJUSTMENTS,
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FARM_OTHER_INCOME_WITH_RECAPTURE,
    FARM_PARTNER_OTHER_AMOUNTS,
    FARM_PARTNER_OTHER_AMOUNTS_TOTAL,
    FARM_PARTNERSHIP_TOTAL,
    FARM_RECAPTURED_CCA,
    FARM_SHARE_OF_NET_INCOME,
    FARM_TERMINAL_LOSS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FISH_CCA_CLAIM,
    FISH_CCA_CLAIM_LESS_PERSONAL_PART,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_EXPENSES_SUBTOTAL,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_HOME_CARRY_FORWARD,
    FISH_HOME_EXPENSES,
    FISH_HOME_EXPENSES_AVAILABLE,
    FISH_HOME_EXPENSES_BUSINESS_PART,
    FISH_HOME_EXPENSES_SUBTOTAL,
    FISH_HOME_INCOME_LIMIT,
    FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    FISH_MINISTER_ALLOCATION_GIVEN_CHECKED,
    FISH_MOTOR_VEHICLE_EXPENSES,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FISH_OTHER_INCOME_WITH_RECAPTURE,
    FISH_PARTNER_OTHER_AMOUNTS,
    FISH_PARTNER_OTHER_AMOUNTS_TOTAL,
    FISH_PARTNERSHIP_TOTAL,
    FISH_RECAPTURED_CCA,
    FISH_REPAIRS_TOTAL,
    FISH_REPAIRS_YOUR_COST,
    FISH_SHARE_OF_NET_INCOME,
    FISH_TERMINAL_LOSS,
    FISH_TOTAL_EXPENSES,
    FISHING_INCOME,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_SELF_EMPLOYMENT_INCOME,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_PAYMENTS_LIMIT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tax_calculator.jurisdictions.ca_on.catalog import (
    NON_REFUNDABLE_TAX_CREDITS as ONTARIO_NON_REFUNDABLE_TAX_CREDITS,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_BASIC_TAX,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_LESS_DIVIDEND_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# T2042 statement 1, a sole proprietor's farm (returns/2025_return_ey.yaml). Part 3: wheat 80,000
# and cattle 20,000, other income 400. Part 4: the expense lines, the motor vehicle (Chart A), the
# previous year's inventory adjustments (1,500 mandatory, 500 optional) and other expenses 250.
FARM_ONE = {
    "wheat": "80000",
    "cattle": "20000",
    "other_income": "400",
    "fertilizers_and_lime": "6000",
    "seeds_and_plants": "15000",
    "veterinary_fees": "1200",
    "machinery_repairs_licences_and_insurance": "2500",
    "gasoline_diesel_and_oil": "3500",
    "electricity": "1800",
    "interest_and_bank_charges": "2000",
    "property_taxes": "1500",
    "rent": "5000",
    "salaries_wages_and_benefits": "8000",
    # Chart A: the sales tax rate of the province (the HST of 13%).
    "vehicle_sales_tax_rate": "13",
    "mandatory_inventory_adjustment_previous_year": "1500",
    "optional_inventory_adjustment_previous_year": "500",
    "other_expenses": "250",
}
# The vehicle of statement 1, a record of `ca/business_vehicles`: Chart A amounts 3, 5, 6 and 7
# are 3000 + 1200 + 300 + 1500 = 6000, the business use part 8000 / 10000 of it is 4800, and the
# parking fees (amount 14) are 100.
FARM_VEHICLE = {
    "business_kilometres": "8000",
    "total_kilometres": "10000",
    "fuel_and_oil": "3000",
    "insurance": "1200",
    "licence_and_registration": "300",
    "maintenance_and_repairs": "1500",
    "parking_fees": "100",
}
# The Area A rows of statement 1: (class, column 2, additions, proceeds, AIIP, RIIP, claimed,
# no property left, DIEP additions, DIEP proceeds, immediate expensing).
FARM_CLASS_8 = ("8", "1500", "0", "4500", "0", "0", "0", 0, "0", "0", "0")
FARM_CLASS_10 = ("10", "2000", "0", "600", "0", "0", "0", 1, "0", "0", "0")
FARM_CLASS_10_PROPERTY_LEFT = ("10", "2000", "0", "600", "0", "0", "0", 0, "0", "0", "0")
FARM_CLASS_6 = ("6", "30000", "0", "0", "0", "0", "3000", 0, "0", "0", "0")

# T2042 statement 2, a farm partner: the T5013 slip amount 15,000 (partner share), the GST/HST
# rebate 200, the partner's other amounts A to E (Part 6) and the business-use-of-home expenses
# (Part 7), with a carry forward of 6000 from the previous year.
FARM_PARTNER = {
    "partner_share": "15000",
    "partner_gst_hst_rebate": "200",
    "partner_other_amount_a": "500",
    "partner_other_amount_b": "300",
    "partner_other_amount_c": "200",
    "partner_other_amount_d": "150",
    "partner_other_amount_e": "50",
    "home_heat": "2000",
    "home_electricity": "1500",
    "home_insurance": "400",
    "home_maintenance": "800",
    "home_mortgage_interest": "3000",
    "home_property_taxes": "2200",
    "home_other_expenses": "600",
    "home_personal_use_part": "1500",
    "home_carried_forward": "6000",
}

# T2121 statement 1, a sole proprietor's fishing business. Part 3: fish products 60,000,
# sharesperson income 5,000, subsidies 2,000 and other income 300. Part 4: the expense lines, the
# repairs (3000, 1200 and 800), the insurance recovery 600 and other expenses 200.
FISH_ONE = {
    "fish_products": "60000",
    "subsidies": "2000",
    "sharesperson_income": "5000",
    "other_income": "300",
    "salt_bait_and_ice": "2000",
    "crew_shares": "8000",
    "fuel_costs": "6000",
    "fishing_gear": "2000",
    "insurance": "1500",
    "interest_and_bank_charges": "800",
    "meals_and_entertainment": "400",
    "business_taxes_licences_and_memberships": "200",
    "vehicle_sales_tax_rate": "13",
    "office_expenses": "300",
    "nets_and_traps": "1000",
    "professional_fees": "600",
    "salaries_wages_and_benefits": "3000",
    "repairs_fishing_boat": "3000",
    "repairs_engine": "1200",
    "repairs_electrical_equipment": "800",
    "insurance_recovery": "600",
    "other_expenses": "200",
}
# The vehicle of statement 1: Chart A amounts 3, 5, 6 and 7 are 2000 + 800 + 200 + 1000 = 4000,
# the business use part 6000 / 12000 of it is 2000.
FISH_VEHICLE = {
    "business_kilometres": "6000",
    "total_kilometres": "12000",
    "fuel_and_oil": "2000",
    "insurance": "800",
    "licence_and_registration": "200",
    "maintenance_and_repairs": "1000",
}
# The Area A rows of statement 1: Class 8 (recapture), Class 10 (terminal loss), Class 7 (the
# maximum of 15%, claimed in full).
FISH_CLASS_8 = ("8", "1800", "0", "4300", "0", "0", "0", 0, "0", "0", "0")
FISH_CLASS_10 = ("10", "2200", "0", "700", "0", "0", "0", 1, "0", "0", "0")
FISH_CLASS_7 = ("7", "40000", "0", "0", "0", "0", "6000", 0, "0", "0", "0")

# T2121 statement 2, a fishing partner: the T5013 slip amount 12,000, the GST/HST rebate 150, the
# partner's other amounts A to E, and the business-use-of-home expenses with a carry forward of
# 6000.
FISH_PARTNER = {
    "partner_share": "12000",
    "partner_gst_hst_rebate": "150",
    "partner_other_amount_a": "400",
    "partner_other_amount_b": "250",
    "partner_other_amount_c": "150",
    "partner_other_amount_d": "100",
    "partner_other_amount_e": "50",
    "home_heat": "1500",
    "home_electricity": "1000",
    "home_insurance": "300",
    "home_maintenance": "500",
    "home_mortgage_interest": "2500",
    "home_property_taxes": "1200",
    "home_other_expenses": "400",
    "home_personal_use_part": "1000",
    "home_carried_forward": "6000",
}

# The statements as the keywords of `t2042_statement` and `t2121_statement`. Statement 1 of each
# form has the minister's allocation given (1,250,000 on the T2042, 1,000,000 on the T2121) and,
# on the T2042, the non-arm's length expenses of Chart A (2,000).
FARM_ONE_STATEMENT: dict[str, Any] = {
    "farm": FARM_ONE,
    "farm_cca_classes_rows": (FARM_CLASS_8, FARM_CLASS_10, FARM_CLASS_6),
    "farm_vehicles_rows": (FARM_VEHICLE,),
    "farm_non_arms_length_expenses": "2000",
    "farm_minister_allocation_given": 1,
    "farm_minister_allocation": "1250000",
}
FARM_PARTNER_STATEMENT: dict[str, Any] = {"farm": FARM_PARTNER, "farm_partner": 1}
FISH_ONE_STATEMENT: dict[str, Any] = {
    "fish": FISH_ONE,
    "fish_cca_classes_rows": (FISH_CLASS_8, FISH_CLASS_10, FISH_CLASS_7),
    "fish_vehicles_rows": (FISH_VEHICLE,),
    "fish_minister_allocation_given": 1,
    "fish_minister_allocation": "1000000",
}
FISH_PARTNER_STATEMENT: dict[str, Any] = {"fish": FISH_PARTNER, "fish_partner": 1}


def run_ey(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return EY's inputs, as in `returns/2025_return_ey.yaml`: a single Ontario resident with 12
    months of CPP and QPP, one empty Schedule 8 (the `starting` defaults), and two T2042 and two
    T2121 statements (a sole proprietor and a partner of each form).

    The statement keywords of `overrides` replace the statements of the return, so a variant
    gives its own `farm_statements` or `fish_statements`.
    """
    arguments: dict[str, Any] = {
        "farm_statements": (FARM_ONE_STATEMENT, FARM_PARTNER_STATEMENT),
        "fish_statements": (FISH_ONE_STATEMENT, FISH_PARTNER_STATEMENT),
        **overrides,
    }
    return run("0", (), "0", "0", "0", "0", "0", **arguments)


def return_ey(**overrides: Any) -> Worksheet:
    """The return form's worksheet of `run_ey`: T1 lines 14100, 14300, 27 and below."""
    return run_ey(**overrides)["ca-on/return"][0]


def farm_ey(index: int, **overrides: Any) -> Worksheet:
    """The worksheet of statement `index` (0 or 1) of Form T2042 in `run_ey`."""
    return run_ey(**overrides)["ca/t2042"][index]


def fish_ey(index: int, **overrides: Any) -> Worksheet:
    """The worksheet of statement `index` (0 or 1) of Form T2121 in `run_ey`."""
    return run_ey(**overrides)["ca/t2121"][index]


# --- the return: T1 lines and the tax -------------------------------------------------------------


def test_return_eys_net_farming_and_fishing_income_total_75250_on_t1_line_27() -> None:
    # T2042 amount 5C is 45,350.00 (line 14100) and T2121 amount 5C is 29,900.00 (line 14300); lines
    # 13500, 13700 and 13900 are 0, so line 27 is 0 + 0 + 0 + 45350.00 + 29900.00 = 75250.00, which
    # is total income (line 15000), net income and taxable income, there being no deduction.
    worksheet = return_ey()

    assert worksheet.get(NET_FARMING_INCOME).value == D("45350.00")
    assert worksheet.get(NET_FISHING_INCOME).value == D("29900.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("75250.00")
    assert worksheet.get(TOTAL_INCOME).value == D("75250.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("75250.00")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("75250.00")
    assert worksheet.get(NET_INCOME).value == D("75250.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("75250.00")


def test_return_eys_federal_tax_after_credits_is_9645_05() -> None:
    # Federal tax (Part A, column 2): 75250.00 - 57375.00 = 17875.00 x 20.5% = 3664.375, rounded
    # half-up to 3664.38, plus 8319.38 is 11983.76. The basic personal amount 16129.00 x 14.5% =
    # 2338.705, rounded 2338.71; 11983.76 - 2338.71 = 9645.05.
    worksheet = return_ey()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("11983.76")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("2338.71")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("9645.05")


def test_return_eys_ontario_tax_after_credits_is_4073_33_with_no_surtax_or_reduction() -> None:
    # Ontario tax (ON428 Part A, column 2): 75250.00 - 52886.00 = 22364.00 x 9.15% = 2046.306,
    # rounded 2046.31, plus 2670.74 is 4717.05. The basic personal amount 12747.00 x 5.05% =
    # 643.7235, rounded 643.72, so the tax after credits is 4717.05 - 643.72 = 4073.33. That is
    # below the first surtax threshold of 5710 (no surtax), and the reduction (588.00 less 4073.33)
    # is below 0, so there is no Ontario tax reduction and no LIFT credit (no employment income).
    worksheet = return_ey()

    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("4717.05")
    assert worksheet.get(ONTARIO_NON_REFUNDABLE_TAX_CREDITS).value == D("643.72")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("4073.33")
    assert worksheet.get(ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("4073.33")


def test_return_eys_ontario_tax_adds_the_health_premium_of_750() -> None:
    # The Ontario health premium (row 9, more than 72600 and not more than 200000) is 750, so the
    # Ontario tax is 4073.33 + 750 = 4823.33.
    worksheet = return_ey()

    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("750")
    assert worksheet.get(ONTARIO_TAX).value == D("4823.33")


def test_return_eys_balance_owing_is_14468_38_and_the_cpp_maximum_is_9900() -> None:
    # The total payable is the federal 9645.05 plus the Ontario 4823.33, 14468.38, and with no
    # instalments or refund it is the balance owing. The CPP second additional earnings maximum is
    # the one figure of this return that is not a tax line: 81,200.00 - 71,300.00 = 9900.00.
    worksheet = return_ey()

    assert worksheet.get(TOTAL_PAYABLE).value == D("14468.38")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("14468.38")
    assert worksheet.get(CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM).value == D("9900.00")


# --- T2042 statement 1, the sole proprietor's farm ------------------------------------------------


def test_return_eys_farm_recapture_is_3000_and_gross_income_103400() -> None:
    # Class 8 has a negative column 7 (1500 - 4500 = -3000), a recapture of 3000 added to other
    # income: 400 + 3000 = 3400. Gross income (line 9659, amount 4A) is 80000 + 20000 + 3400 =
    # 103400.
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_RECAPTURED_CCA).value == D("3000")
    assert worksheet.get(FARM_OTHER_INCOME_WITH_RECAPTURE).value == D("3400")
    assert worksheet.get(FARM_GROSS_INCOME).value == D("103400")
    assert worksheet.get(FARM_GROSS_INCOME_BEFORE_EXPENSES).value == D("103400")


def test_return_eys_farm_area_a_claims_3000_for_class_6() -> None:
    # Class 6: column 2 30000 with no additions, so the maximum is 30000 x 10% = 3000.00, claimed in
    # full (the row's claim is 3000). Class 8 and Class 10 have no claim (0). Line 9936 is 3000,
    # with no personal part and no business-use-of-home CCA.
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_CCA_TABLE_CLAIM).value == D("3000")
    assert worksheet.get(FARM_CCA_CLAIM_LESS_PERSONAL_PART).value == D("3000")
    assert worksheet.get(FARM_CCA_CLAIM).value == D("3000")


def test_return_eys_farm_closing_ucc_is_0_0_and_27000() -> None:
    # Column 22 is column 7 less the claim: Class 8 is 0 (the recapture brought it to 0), Class 10
    # is 0 (no property left, the terminal loss took the balance), and Class 6 is 30000 - 3000 =
    # 27000, the opening UCC of next year.
    worksheet = farm_ey(0)

    closing = worksheet.get(FARM_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records] == [
        [D("8"), D("0")],
        [D("10"), D("0")],
        [D("6"), D("27000")],
    ]


def test_return_eys_farm_chart_a_motor_vehicle_is_4900() -> None:
    # Chart A (motor vehicle expenses): amount 12 is 3000 + 1200 + 300 + 1500 = 6000; amount 13 is
    # 6000 x 8000 / 10000 = 4800.00; the parking fees (amount 14) are 100 and the supplementary
    # insurance (amount 15) 0, so amount 16 (line 9819) is 4800 + 100 = 4900.00.
    worksheet = farm_ey(0)

    (vehicle,) = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert vehicle.line_12 == D("6000.00")
    assert vehicle.line_13 == D("4800.00")
    assert vehicle.line_16 == D("4900.00")
    assert worksheet.get(FARM_MOTOR_VEHICLE_EXPENSES).value == D("4900.00")


def test_return_eys_farm_expenses_include_the_inventory_adjustments_and_terminal_loss() -> None:
    # Part 4: seeds 15000, fertilizers 6000, veterinary 1200, machinery 2500, fuel 3500,
    # electricity 1800, interest 2000, property taxes 1500, rent 5000 and salaries 8000 are 46500;
    # motor vehicle 4900.00; the previous year's mandatory (1500) and optional (500) inventory
    # adjustments, 2000; the other expenses 250 plus the terminal loss 1400, 1650. Subtotal 4B is
    # 46500 + 4900 + 2000 + 1650 = 55050.00, and line 9898 is 55050.00 + 3000 = 58050.00.
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_TERMINAL_LOSS).value == D("1400")
    assert worksheet.get(FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("1650")
    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("55050.00")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("58050.00")


def test_return_eys_farm_net_income_is_45350_after_the_inventory_adjustments() -> None:
    # Line 9899 is 103400 - 58050.00 = 45350.00. With no current-year inventory adjustment (lines
    # 9941 and 9942 are 0), the net income after inventory adjustments and after adjustments is
    # 45350.00, and the farming income (amount 4C) is 45350.00.
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("45350.00")
    assert worksheet.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("45350.00")
    assert worksheet.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("45350.00")
    assert worksheet.get(FARMING_INCOME).value == D("45350.00")


def test_return_eys_farm_chart_a_gross_expenses_are_54050_on_t2043() -> None:
    # Chart A of the T2043: amount 2 (line 9937) 1500 + amount 3 (line 9938) 500 + amount 4 (the
    # non-arm's length expenses) 2000 is amount 5, 4000 (the subtotal). Amount 6, the gross farming
    # expenses, is line 9898 less amount 5: 58050.00 - 4000 = 54050.00.
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_CHART_A_SUBTOTAL).value == D("4000")
    assert worksheet.get(FARM_CHART_A_GROSS_EXPENSES).value == D("54050.00")


def test_return_eys_farm_sole_proprietor_has_no_partner_amounts_and_net_is_45350() -> None:
    # No partner (count 0): the Part 5 share of net income is the net income 45350.00 and the
    # partnership total is 45350.00 (amount 5C).
    worksheet = farm_ey(0)

    assert worksheet.get(FARM_SHARE_OF_NET_INCOME).value == D("45350.00")
    assert worksheet.get(FARM_PARTNERSHIP_TOTAL).value == D("45350.00")


def test_return_eys_farm_minister_allocation_sets_the_1250000_limit_and_partner_has_1500000() -> (
    None
):
    # The minister allocated a chosen 1,250,000 to statement 1 (count 1), so its immediate
    # expensing limit is 1250000 and no class has DIEP additions. Statement 2 is given no
    # allocation, so its limit is the $1.5 million of Area A endnote 5, 1500000.
    assert farm_ey(0).get(FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1250000")
    assert farm_ey(0).get(FARM_MINISTER_ALLOCATION_GIVEN_CHECKED).value == 1
    assert farm_ey(1).get(FARM_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1500000")


# --- T2042 statement 2, the farm partner ----------------------------------------------------------


def test_return_eys_farm_partner_other_amounts_are_1200() -> None:
    # Part 6: amounts 6A to 6E 500 + 300 + 200 + 150 + 50 = 1200 (line 9943), so amount 5C is
    # 15200 - 1200 = 14000 once the partnership total is known.
    worksheet = farm_ey(1)

    assert worksheet.get(FARM_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("1200")
    assert worksheet.get(FARM_PARTNER_OTHER_AMOUNTS).value == D("1200")


def test_return_eys_farm_partner_share_is_15000_and_net_income_14000() -> None:
    # Part 5: amount 5A is the T5013 slip amount 15000 (count 1); line 9951 is 0 and line 9974 is
    # 200 (the GST/HST rebate), so amount 5B is 15200. Amount 5C is 15200 - 1200 = 14000 (line
    # 9943), and line 9945 is the allowable home claim (14,000, asserted below).
    worksheet = farm_ey(1)

    assert worksheet.get(FARM_SHARE_OF_NET_INCOME).value == D("15000")
    assert worksheet.get(FARM_PARTNERSHIP_TOTAL).value == D("15200")
    assert worksheet.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("14000")


def test_return_eys_farm_partner_home_expenses_are_limited_to_14000_with_1000_carried_forward() -> (
    None
):
    # Part 7: amounts 7A to 7G 2000 + 1500 + 400 + 800 + 3000 + 2200 + 600 = 10500 (7H); amount 7I
    # 1500, so 7J is 9000. Amount 7L (carry forward) 6000, so 7M is 15000. Amount 7N is the net
    # income 14000, so 7O (carried forward) is 15000 - 14000 = 1000, and 7P, the lesser of 15000 and
    # 14000, is 14000 (line 9945).
    worksheet = farm_ey(1)

    assert worksheet.get(FARM_HOME_EXPENSES_SUBTOTAL).value == D("10500")
    assert worksheet.get(FARM_HOME_EXPENSES_BUSINESS_PART).value == D("9000")
    assert worksheet.get(FARM_HOME_EXPENSES_AVAILABLE).value == D("15000")
    assert worksheet.get(FARM_HOME_INCOME_LIMIT).value == D("14000")
    assert worksheet.get(FARM_HOME_CARRY_FORWARD).value == D("1000")
    assert worksheet.get(FARM_HOME_EXPENSES).value == D("14000")


# --- T2121 statement 1, the sole proprietor's fishing business ------------------------------------


def test_return_eys_fish_recapture_is_2500_and_gross_income_69800() -> None:
    # Class 8 has a negative column 7 (1800 - 4300 = -2500), a recapture of 2500 added to other
    # income: 300 + 2500 = 2800. Gross income (line 8299) is 60000 + 5000 + 2000 + 2800 = 69800.
    worksheet = fish_ey(0)

    assert worksheet.get(FISH_RECAPTURED_CCA).value == D("2500")
    assert worksheet.get(FISH_OTHER_INCOME_WITH_RECAPTURE).value == D("2800")
    assert worksheet.get(FISH_GROSS_INCOME).value == D("69800")
    assert worksheet.get(FISH_GROSS_INCOME_BEFORE_EXPENSES).value == D("69800")


def test_return_eys_fish_area_a_claims_6000_for_class_7() -> None:
    # Class 7: column 2 40000, the maximum 40000 x 15% = 6000.00 claimed in full, so line 9936 is
    # 6000; Class 8 and Class 10 claim nothing.
    worksheet = fish_ey(0)

    assert worksheet.get(FISH_CCA_TABLE_CLAIM).value == D("6000")
    assert worksheet.get(FISH_CCA_CLAIM_LESS_PERSONAL_PART).value == D("6000")
    assert worksheet.get(FISH_CCA_CLAIM).value == D("6000")


def test_return_eys_fish_closing_ucc_is_0_0_and_34000() -> None:
    # Class 8 is 0 (the recapture brought it to 0), Class 10 is 0 (the terminal loss), and Class 7
    # is 40000 - 6000 = 34000.
    worksheet = fish_ey(0)

    closing = worksheet.get(FISH_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records] == [
        [D("8"), D("0")],
        [D("10"), D("0")],
        [D("7"), D("34000")],
    ]


def test_return_eys_fish_chart_a_motor_vehicle_is_2000() -> None:
    # Chart A: amount 12 is 2000 + 800 + 200 + 1000 = 4000; amount 13 is 4000 x 6000 / 12000 =
    # 2000.00; with no parking or supplementary insurance, amount 16 (line 9281) is 2000.00.
    worksheet = fish_ey(0)

    (vehicle,) = [line for line in worksheet.trace if isinstance(line, BusinessVehicleLine)]
    assert vehicle.line_12 == D("4000.00")
    assert vehicle.line_13 == D("2000.00")
    assert vehicle.line_16 == D("2000.00")
    assert worksheet.get(FISH_MOTOR_VEHICLE_EXPENSES).value == D("2000.00")


def test_return_eys_fish_repairs_total_5000_and_your_cost_4400() -> None:
    # Repairs and maintenance: the fishing boat 3000, the engine 1200 and the electrical equipment
    # 800 are amounts 1 to 3, a total (amount 4) of 5000. The insurance recovery (amount 5) is 600,
    # so your cost (line 8963, amount 4 minus amount 5) is 5000 - 600 = 4400.
    worksheet = fish_ey(0)

    assert worksheet.get(FISH_REPAIRS_TOTAL).value == D("5000")
    assert worksheet.get(FISH_REPAIRS_YOUR_COST).value == D("4400")


def test_return_eys_fish_expenses_are_33900_and_net_income_29900() -> None:
    # Part 4 subtotal 4Q: salt, bait and ice 2000, crew shares 8000, fuel 6000, gear 2000, insurance
    # 1500, interest 800, meals 400, business taxes 200, office 300, nets 1000, professional fees
    # 600 and salaries 3000 are 25800; the motor vehicle 2000.00; your cost 4400; the other expenses
    # 200
    # plus the terminal loss 1500, 1700. Subtotal is 25800 + 2000 + 4400 + 1700 = 33900.00, and line
    # 9368 is 33900.00 + 6000 = 39900.00, so line 9369 is 69800 - 39900.00 = 29900.00.
    worksheet = fish_ey(0)

    assert worksheet.get(FISH_TERMINAL_LOSS).value == D("1500")
    assert worksheet.get(FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("1700")
    assert worksheet.get(FISH_EXPENSES_SUBTOTAL).value == D("33900.00")
    assert worksheet.get(FISH_TOTAL_EXPENSES).value == D("39900.00")
    assert worksheet.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("29900.00")
    assert worksheet.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("29900.00")
    assert worksheet.get(FISHING_INCOME).value == D("29900.00")


def test_return_eys_fish_sole_proprietor_share_is_29900_and_minister_limit_1000000() -> None:
    # No partner: amount 5C and line 9946 are 29900.00 (line 14300). The minister allocated a
    # chosen 1,000,000 (count 1), the immediate expensing limit.
    worksheet = fish_ey(0)

    assert worksheet.get(FISH_SHARE_OF_NET_INCOME).value == D("29900.00")
    assert worksheet.get(FISH_PARTNERSHIP_TOTAL).value == D("29900.00")
    assert worksheet.get(FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1000000")
    assert worksheet.get(FISH_MINISTER_ALLOCATION_GIVEN_CHECKED).value == 1


# --- T2121 statement 2, the fishing partner -------------------------------------------------------


def test_return_eys_fish_partner_other_amounts_are_950_and_total_is_12150() -> None:
    # Part 5: amount 5A is the T5013 slip amount 12000 (count 1), and line 9974 is 150, so amount 5B
    # is 12150. Part 6: amounts 6A to 6E 400 + 250 + 150 + 100 + 50 = 950 (line 9943), so amount 5C
    # is 12150 - 950 = 11200.
    worksheet = fish_ey(1)

    assert worksheet.get(FISH_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("950")
    assert worksheet.get(FISH_PARTNER_OTHER_AMOUNTS).value == D("950")
    assert worksheet.get(FISH_PARTNERSHIP_TOTAL).value == D("12150")
    assert worksheet.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("11200")
    assert worksheet.get(FISH_SHARE_OF_NET_INCOME).value == D("12000")


def test_return_eys_fish_partner_home_expenses_are_limited_to_11200_with_1200_carried_forward() -> (
    None
):
    # Part 7: amounts 7A to 7G 1500 + 1000 + 300 + 500 + 2500 + 1200 + 400 = 7400 (7H); amount 7I
    # 1000, so 7J is 6400. Amount 7L 6000, so 7M is 12400. Amount 7N is 11200, so 7O (carried
    # forward) is 12400 - 11200 = 1200, and 7P, the lesser of 12400 and 11200, is 11200 (line 9945).
    worksheet = fish_ey(1)

    assert worksheet.get(FISH_HOME_EXPENSES_SUBTOTAL).value == D("7400")
    assert worksheet.get(FISH_HOME_EXPENSES_BUSINESS_PART).value == D("6400")
    assert worksheet.get(FISH_HOME_EXPENSES_AVAILABLE).value == D("12400")
    assert worksheet.get(FISH_HOME_INCOME_LIMIT).value == D("11200")
    assert worksheet.get(FISH_HOME_CARRY_FORWARD).value == D("1200")
    assert worksheet.get(FISH_HOME_EXPENSES).value == D("11200")


def test_return_eys_fish_partner_minister_limit_is_the_default_1500000() -> None:
    # The partner statement is given no minister's allocation, so its immediate expensing limit is
    # the $1.5 million of Area A endnote 5, 1500000.
    assert fish_ey(1).get(FISH_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1500000")


# --- variants -------------------------------------------------------------------------------------


def test_return_eys_variant_class_10_with_property_left_has_no_terminal_loss() -> None:
    # Class 10 with no property left = 0 (property left): column 7 is 2000 - 600 = 1400, positive,
    # but a terminal loss needs no property left, so the terminal loss is 0, the other expenses
    # with terminal loss are 250 (the other expenses alone) and the claim is 0, so the closing UCC
    # is 1400. Subtotal 4B is 46500 + 4900 + 2000 + 250 = 53650.00; line 9898 is 53650 + 3000 =
    # 56650.00; line 9899 is 103400 - 56650 = 46750.00.
    statements = (
        {
            **FARM_ONE_STATEMENT,
            "farm_cca_classes_rows": (FARM_CLASS_8, FARM_CLASS_10_PROPERTY_LEFT, FARM_CLASS_6),
        },
        FARM_PARTNER_STATEMENT,
    )
    worksheet = farm_ey(0, farm_statements=statements)

    assert worksheet.get(FARM_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("250")
    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("53650.00")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("56650.00")
    assert worksheet.get(FARM_NET_INCOME_AFTER_ADJUSTMENTS).value == D("46750.00")
    closing = worksheet.get(FARM_CLOSING_UCC).value
    assert [list(record.values()) for record in closing.records][1] == [D("10"), D("1400")]


def test_return_eys_variant_fish_insurance_recovery_0_gives_repairs_cost_5000() -> None:
    # With the insurance recovery 0, your cost (amount 4 minus amount 5) is 5000 - 0 = 5000; the
    # subtotal is 25800 + 2000 + 5000 + 1700 = 34500.00; line 9368 is 34500 + 6000 = 40500.00; line
    # 9369 is 69800 - 40500 = 29300.00.
    statements = (
        {**FISH_ONE_STATEMENT, "fish": {**FISH_ONE, "insurance_recovery": "0"}},
        FISH_PARTNER_STATEMENT,
    )
    worksheet = fish_ey(0, fish_statements=statements)

    assert worksheet.get(FISH_REPAIRS_TOTAL).value == D("5000")
    assert worksheet.get(FISH_REPAIRS_YOUR_COST).value == D("5000")
    assert worksheet.get(FISH_EXPENSES_SUBTOTAL).value == D("34500.00")
    assert worksheet.get(FISH_TOTAL_EXPENSES).value == D("40500.00")
    assert worksheet.get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("29300.00")


def test_return_eys_variant_no_previous_year_inventory_leaves_chart_a_non_arms_length() -> None:
    # With the previous year's mandatory and optional inventory adjustments 0, the expenses subtotal
    # is 46500 + 4900 + 0 + 1650 = 53050.00 and line 9898 is 53050 + 3000 = 56050.00; net income
    # before adjustments is 103400 - 56050 = 47350.00. Chart A amount 5 is only the non-arm's length
    # expenses 2000, so the subtotal is 2000, and amount 6, the gross farming expenses, is
    # 56050 - 2000 = 54050.00, the same as before because the adjustments left Chart A too.
    farm = {
        **FARM_ONE,
        "mandatory_inventory_adjustment_previous_year": "0",
        "optional_inventory_adjustment_previous_year": "0",
    }
    statements = ({**FARM_ONE_STATEMENT, "farm": farm}, FARM_PARTNER_STATEMENT)
    worksheet = farm_ey(0, farm_statements=statements)

    assert worksheet.get(FARM_CHART_A_SUBTOTAL).value == D("2000")
    assert worksheet.get(FARM_CHART_A_GROSS_EXPENSES).value == D("54050.00")
    assert worksheet.get(FARM_EXPENSES_SUBTOTAL).value == D("53050.00")
    assert worksheet.get(FARM_TOTAL_EXPENSES).value == D("56050.00")
    assert worksheet.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("47350.00")
