"""The 2025 farming income lines (T2042 Parts 3 to 7 and Area A, T1 lines 14099 and 14100), checked
against CRA's form.

2025 Form T2042 (Statement of Farming Activities), Part 3 "Gross income: Total of the income
lines (enter this amount on line 14099 of your income tax and benefit return)"; Part 4 "Subtotal of
expenses 4B", "Total farm expenses: Amount 4B plus line 9936" and "Net income (loss) before
inventory adjustments: Amount 4A minus line 9898"; Part 5 "Total: Amount 5A plus line 9951 plus
line 9974" and "Your net income (loss): Amount 5C minus line 9945 (enter this amount on line 14100
of your income tax and benefit return)"; Part 7 "Net income (loss) after adjustments (amount 5C)
(if negative, enter "0")." and "Allowable claim: Amount 7M or 7N above, whichever is less (enter
your share of this amount on line 9945 of Part 5)"; Area A endnote 3: "If you have a negative
amount in column 7, add it to income as a recapture in Part 3 on line 9600. If no property is left
in the class and there is a positive amount in this column, deduct the amount from income as a
terminal loss in Part 4 on line 9790. Recapture and terminal loss do not apply to a Class 10.1
property unless it is a DIEP." Every amount of the form is a dollars-and-cents box, and these lines
only add and subtract amounts already in cents (the capital cost allowance columns round with the
`ca/cca_class_rates` dataset, tested in test_rental_cca_2025.py), so the lines have no dataset of
their own.

The lines are tested here one rule at a time on the registered kinds; the lines together, from the
income lines to T1 lines 14099 and 14100, are in `end_to_end/test_return_bc.py` and
`returns/2025_return_bc.yaml`. Form T2042 Charts A to C (the motor vehicle expenses, line 9819 of
Part 4, and the Chart B and C figures of a leased passenger vehicle) are at the end of this module;
the printed constants of the charts are the T2125's datasets, tested in
`test_t2125_motor_vehicle_2025.py`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_CCA_CLAIM,
    FARM_CCA_CLAIM_LESS_PERSONAL_PART,
    FARM_CCA_TABLE_CLAIM,
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_A_SUBTOTAL,
    FARM_EXPENSES_SUBTOTAL,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_HOME_ALLOWABLE_CLAIM,
    FARM_HOME_CARRY_FORWARD,
    FARM_HOME_EXPENSES,
    FARM_HOME_EXPENSES_AVAILABLE,
    FARM_HOME_INCOME_LIMIT,
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
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BC's statement, the default of these tests: income lines of 80000 (wheat 50000 on line
# 9371 and cattle 30000 on line 9471) and expenses of 50000 (seeds and plants, line 9664), so line
# 9899 is 30000, and no CCA, partner or business-use-of-home amounts.
DEFAULT_FARM = {"wheat": "50000", "cattle": "30000", "seeds_and_plants": "50000"}

# The 27 expense amounts of Part 4 and Part 4's adjustments and other expenses, in the form's
# order: lines 9661 to 9820 (line 9819, the motor vehicle expenses, is the Chart A line below and
# not an amount here), 9937 and 9938, and the other expenses that make up line 9790.
EXPENSE_NAMES = (
    "containers_and_twine",
    "fertilizers_and_lime",
    "pesticides",
    "seeds_and_plants",
    "feed_supplements_straw_and_bedding",
    "livestock_purchased",
    "veterinary_fees",
    "machinery_repairs_licences_and_insurance",
    "gasoline_diesel_and_oil",
    "building_repairs_and_maintenance",
    "clearing_levelling_and_draining",
    "crop_insurance_premiums",
    "custom_work_expenses",
    "electricity",
    "heating_and_curing_fuel",
    "insurance_program_overpayment_recapture",
    "insurance",
    "interest_and_bank_charges",
    "office_expenses",
    "professional_fees",
    "property_taxes",
    "rent",
    "salaries_wages_and_benefits",
    "small_tools",
    "mandatory_inventory_adjustment_previous_year",
    "optional_inventory_adjustment_previous_year",
    "other_expenses",
)

CcaRow = tuple[str, str, str, str, str, str, str, int, str, str, str]


def statement(
    farm: dict[str, str] | None = None,
    partner: int = 0,
    cca_classes: tuple[CcaRow, ...] = (),
    vehicles: tuple[dict[str, str], ...] = (),
    fiscal_period_days_entered: int = 0,
    **overrides: Any,
) -> Worksheet:
    """Return BC's statement with `farm` changing or adding its amounts, `partner` the partner
    count (amount 5A) and `cca_classes` the Area A rows."""
    amounts = {**DEFAULT_FARM, **(farm or {})}
    result = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=(
            {
                "farm": amounts,
                "farm_partner": partner,
                "farm_cca_classes_rows": cca_classes,
                "farm_vehicles_rows": vehicles,
                "farm_fiscal_period_days_entered": fiscal_period_days_entered,
            },
        ),
        **overrides,
    )
    return result["ca/t2042"][0]


def line(worksheet: Worksheet, kind: ArtifactKind[Any]) -> Any:
    return worksheet.get(kind).value


def test_the_grains_other_crops_and_livestock_subtotal_lines_add_to_line_9659() -> None:
    # Lines 9370 "Grains and oilseeds" 1000, 9420 "Other crops" 2000 and 9470 "Livestock and animal
    # products revenue" 4000 are entry lines, so line 9659 is 80000 + 1000 + 2000 + 4000 = 87000.
    worksheet = statement(
        {
            "grains_and_oilseeds": "1000",
            "other_crops": "2000",
            "livestock_and_animal_products_revenue": "4000",
        }
    )

    assert line(worksheet, FARM_GROSS_INCOME) == D("87000")
    assert line(worksheet, FARM_GROSS_INCOME_BEFORE_EXPENSES) == D("87000")


def test_a_statement_with_no_other_amounts_is_the_income_lines_less_the_expenses() -> None:
    # Income lines 50000 + 30000 = 80000 (line 9659 and T1 line 14099); expenses 50000 (4B), no CCA,
    # so line 9898 is 50000 and line 9899 is 80000 - 50000 = 30000, which is line 9946 and T1
    # line 14100.
    worksheet = statement()

    assert line(worksheet, FARM_GROSS_INCOME_BEFORE_EXPENSES) == D("80000")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("50000")
    assert line(worksheet, FARM_TOTAL_EXPENSES) == D("50000")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30000")
    assert line(worksheet, FARMING_INCOME) == D("30000")


def test_a_recapture_row_adds_the_negative_column_7_to_line_9600() -> None:
    # Class 8: UCC at the start 1000, proceeds of dispositions 4000, so column 7 is
    # 1000 + 0 - 4000 = -3000, "a negative amount in column 7", added to income as a recapture on
    # line 9600: 3000. Other income of 500 makes line 9600 3500 (500 + 3000), so line 9659 is
    # 80000 + 3500 = 83500 and line 9899 is 83500 - 50000 = 33500. No claim is allowed on a
    # negative column 7.
    worksheet = statement(
        {"other_income": "500"},
        cca_classes=(("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),),
    )

    assert line(worksheet, FARM_RECAPTURED_CCA) == D("3000")
    assert line(worksheet, FARM_OTHER_INCOME_WITH_RECAPTURE) == D("3500")
    assert line(worksheet, FARM_GROSS_INCOME_BEFORE_EXPENSES) == D("83500")
    assert line(worksheet, FARM_CCA_CLAIM) == D("0")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("33500")


def test_a_terminal_loss_row_takes_the_positive_column_7_off_on_line_9790() -> None:
    # Class 8 with no property left: column 7 is 1000 + 0 - 0 = 1000, positive, so it is deducted
    # from income as a terminal loss in Part 4 on line 9790, with no CCA claimed on the class. Line
    # 9790 is 0 + 1000 = 1000, so 4B is 50000 + 1000 = 51000 and line 9899 is 80000 - 51000 = 29000.
    worksheet = statement(
        cca_classes=(("8", "1000", "0", "0", "0", "0", "0", 1, "0", "0", "0"),),
    )

    assert line(worksheet, FARM_TERMINAL_LOSS) == D("1000")
    assert line(worksheet, FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("1000")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("51000")
    assert line(worksheet, FARM_CCA_CLAIM) == D("0")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("29000")


def test_a_class_with_property_left_has_no_terminal_loss() -> None:
    # Column 7 is positive but property is left in the class, so no terminal loss: line 9790 is 0.
    worksheet = statement(cca_classes=(("8", "1000", "0", "0", "0", "0", "0", 0, "0", "0", "0"),))

    assert line(worksheet, FARM_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("50000")


def test_class_10_1_has_no_recapture_or_terminal_loss() -> None:
    # Class 10.1, column 7 is 1000 + 0 - 4000 = -3000 and no property is left: "Recapture and
    # terminal loss do not apply to a Class 10.1 property unless it is a DIEP", so both are 0.
    worksheet = statement(
        cca_classes=(("10.1", "1000", "0", "4000", "0", "0", "0", 1, "0", "0", "0"),)
    )

    assert line(worksheet, FARM_RECAPTURED_CCA) == D("0")
    assert line(worksheet, FARM_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30000")


def test_one_class_list_gives_a_claim_a_recapture_and_a_terminal_loss_together() -> None:
    # Class 8: UCC 10000, a claim of 2000 (the maximum, 10000 x 20%); class 10: column 7 of
    # -3000, a recapture of 3000 on line 9600; class 14: column 7 of 500 with no property left, a
    # terminal loss of 500 on line 9790. Line 9936 is 2000; line 9790 is 500; 4B is 50000 + 500 =
    # 50500; 9898 is 50500 + 2000 = 52500; line 9659 is 80000 + 3000 = 83000, so line 9899 is
    # 83000 - 52500 = 30500.
    worksheet = statement(
        cca_classes=(
            ("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0"),
            ("10", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),
            ("6", "500", "0", "0", "0", "0", "0", 1, "0", "0", "0"),
        ),
    )

    assert line(worksheet, FARM_CCA_TABLE_CLAIM) == D("2000")
    assert line(worksheet, FARM_CCA_CLAIM) == D("2000")
    assert line(worksheet, FARM_RECAPTURED_CCA) == D("3000")
    assert line(worksheet, FARM_TERMINAL_LOSS) == D("500")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("50500")
    assert line(worksheet, FARM_TOTAL_EXPENSES) == D("52500")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30500")


def test_the_personal_part_and_the_business_use_of_home_cca_come_off_line_9936() -> None:
    # Amount ii is 2000; the personal part (a caller's 500) comes off to give 1500, and the CCA for
    # business-use-of-home expenses (amount 7K, a caller's 300) comes off to give line 9936, 1200.
    # Line 9898 is 50000 + 1200 = 51200, so line 9899 is 80000 - 51200 = 28800. Amount 7M is
    # 0 + 300 + 0 = 300 and line 9945 is 300, so line 9946 is 28800 - 300 = 28500.
    worksheet = statement(
        {"cca_personal_part": "500", "home_cca": "300"},
        cca_classes=(("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0"),),
    )

    assert line(worksheet, FARM_CCA_CLAIM_LESS_PERSONAL_PART) == D("1500")
    assert line(worksheet, FARM_CCA_CLAIM) == D("1200")
    assert line(worksheet, FARM_TOTAL_EXPENSES) == D("51200")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("28800")
    assert line(worksheet, FARM_HOME_EXPENSES_AVAILABLE) == D("300")
    assert line(worksheet, FARM_HOME_EXPENSES) == D("300")
    assert line(worksheet, FARMING_INCOME) == D("28500")


def test_every_expense_line_and_adjustment_adds_to_4b() -> None:
    # Each of the 27 amounts of Part 4 (lines 9661 to 9820, the previous year's inventory
    # adjustments 9937 and 9938, and the other expenses of line 9790) is 100: 4B is 2700, and with
    # the income of 80000 (none of it from seeds or cattle), line 9899 is 80000 - 2700 = 77300.
    worksheet = statement(
        {**{name: "100" for name in EXPENSE_NAMES}, "wheat": "80000", "cattle": "0"}
    )

    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("2700")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("77300")


def test_the_current_year_inventory_adjustments_add_to_line_4c() -> None:
    # Line 9941 (optional) 1000 and line 9942 (mandatory) 500 are added to line 9899, 30000, to
    # give 4C of 31500, which is line 9946 with no partner.
    worksheet = statement(
        {
            "optional_inventory_adjustment_current_year": "1000",
            "mandatory_inventory_adjustment_current_year": "500",
        }
    )

    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30000")
    assert line(worksheet, FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS) == D("31500")
    assert line(worksheet, FARMING_INCOME) == D("31500")


def test_a_partner_takes_the_t5013_amount_for_amount_5a() -> None:
    # One partner (count 1): amount 5A is the T5013 amount, 12000, as entered; line 9946 is then
    # 12000 - 0 = 12000.
    worksheet = statement({"partner_share": "12000"}, partner=1)

    assert line(worksheet, FARM_SHARE_OF_NET_INCOME) == D("12000")
    assert line(worksheet, FARM_PARTNERSHIP_TOTAL) == D("12000")
    assert line(worksheet, FARM_NET_INCOME_AFTER_ADJUSTMENTS) == D("12000")
    assert line(worksheet, FARMING_INCOME) == D("12000")


def test_a_sole_proprietor_ignores_the_t5013_amount() -> None:
    # No partner (count 0): amount 5A is amount 4C, 30000.
    worksheet = statement()

    assert line(worksheet, FARM_SHARE_OF_NET_INCOME) == D("30000")
    assert line(worksheet, FARMING_INCOME) == D("30000")


def test_a_loss_is_line_9899_below_zero_and_line_14100_in_brackets() -> None:
    # Income of 10000 (wheat) against expenses of 50000: line 9899 is -40000, and so are 4C, amount
    # 5A and line 9946, which is T1 line 14100 "(loss)"; the form prints no floor.
    worksheet = statement({"wheat": "10000", "cattle": "0"})

    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("-40000")
    assert line(worksheet, FARM_SHARE_OF_NET_INCOME) == D("-40000")
    assert line(worksheet, FARM_NET_INCOME_AFTER_ADJUSTMENTS) == D("-40000")
    assert line(worksheet, FARMING_INCOME) == D("-40000")


def test_amount_7n_is_0_when_amount_5c_is_negative_and_the_whole_claim_is_carried_forward() -> None:
    # A loss of 40000 (amount 5C is -40000): business-use-of-home expenses of 2000 (amount 7H,
    # heat) give 7J and 7M of 2000. Amount 7N is 0 (not negative) "if negative, enter "0"", so
    # amount 7P is the lesser of 2000 and 0, 0, line 9945 is 0 and amount 7O carries the whole 2000
    # forward.
    worksheet = statement({"wheat": "10000", "cattle": "0", "home_heat": "2000"})

    assert line(worksheet, FARM_HOME_EXPENSES_AVAILABLE) == D("2000")
    assert line(worksheet, FARM_HOME_INCOME_LIMIT) == D("0")
    assert line(worksheet, FARM_HOME_CARRY_FORWARD) == D("2000")
    assert line(worksheet, FARM_HOME_ALLOWABLE_CLAIM) == D("0")
    assert line(worksheet, FARM_HOME_EXPENSES) == D("0")
    assert line(worksheet, FARMING_INCOME) == D("-40000")


def test_amount_7o_is_0_when_amount_7n_is_larger_and_amount_7p_is_amount_7m() -> None:
    # Amount 7M is 2000 and amount 7N is amount 5C, 30000, so amount 7O is 0 and amount 7P, the
    # allowable claim, is 2000, which is line 9945; line 9946 is 30000 - 2000 = 28000.
    worksheet = statement({"home_heat": "2000"})

    assert line(worksheet, FARM_HOME_CARRY_FORWARD) == D("0")
    assert line(worksheet, FARM_HOME_ALLOWABLE_CLAIM) == D("2000")
    assert line(worksheet, FARM_HOME_EXPENSES) == D("2000")
    assert line(worksheet, FARMING_INCOME) == D("28000")


def test_amount_7p_is_amount_7n_when_the_home_expenses_exceed_the_net_income() -> None:
    # Net income of 1000 (line 9899, amount 5C), amount 7M 3000 (heat): amount 7N is 1000, amount
    # 7O is 3000 - 1000 = 2000 carried forward and amount 7P, the lesser, is 1000, which is line
    # 9945, so line 9946 is 1000 - 1000 = 0.
    worksheet = statement(
        {"wheat": "80000", "seeds_and_plants": "79000", "cattle": "0", "home_heat": "3000"}
    )

    assert line(worksheet, FARM_NET_INCOME_AFTER_ADJUSTMENTS) == D("1000")
    assert line(worksheet, FARM_HOME_CARRY_FORWARD) == D("2000")
    assert line(worksheet, FARM_HOME_ALLOWABLE_CLAIM) == D("1000")
    assert line(worksheet, FARMING_INCOME) == D("0")


def test_the_fuel_charge_credit_and_the_gst_rebate_come_into_amount_5b() -> None:
    # Amount 5B is amount 5A (30000) plus line 9951 (fuel charge credit, 300) plus line 9974
    # (GST/HST rebate for partners, 200): 30500, and with no partner amounts it is line 9946. Form
    # T2043 amount 5C may not be below line 9951 over the statements, so its Ontario credit is 300.
    worksheet = statement(
        {"fuel_charge_credit": "300", "partner_gst_hst_rebate": "200", "partner_share": "30000"},
        partner=1,
        fuel_charge_partnership_credit_on="300",
    )

    assert line(worksheet, FARM_PARTNERSHIP_TOTAL) == D("30500")
    assert line(worksheet, FARMING_INCOME) == D("30500")


def test_the_partner_other_amounts_come_off_at_line_9943() -> None:
    # Amounts 6A and 6B (100 and 200) make amount 6F and line 9943, 300; amount 5C is 30000 - 300.
    worksheet = statement(
        {
            "partner_share": "30000",
            "partner_other_amount_a": "100",
            "partner_other_amount_b": "200",
        },
        partner=1,
    )

    assert line(worksheet, FARM_PARTNER_OTHER_AMOUNTS_TOTAL) == D("300")
    assert line(worksheet, FARM_PARTNER_OTHER_AMOUNTS) == D("300")
    assert line(worksheet, FARM_NET_INCOME_AFTER_ADJUSTMENTS) == D("29700")
    assert line(worksheet, FARMING_INCOME) == D("29700")


# Form T2042 Charts A to C: one leased passenger vehicle used half for farming, a record of the
# statement's `ca/business_vehicles`. The statement is income of 50000 (wheat) and seeds and plants
# of 20000, so the other amounts are 0, and the sales tax rate of the province is 13%.
LEASED: dict[str, str] = {
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


def vehicle_statement(*vehicles: dict[str, str], fiscal_period_days_entered: int = 0) -> Worksheet:
    """A T2042 of income of 50000 (wheat) and seeds and plants of 20000, with one record of
    `ca/business_vehicles` for each vehicle given (the amounts not given are 0)."""
    return statement(
        {"cattle": "0", "seeds_and_plants": "20000", "vehicle_sales_tax_rate": "13"},
        vehicles=vehicles,
        fiscal_period_days_entered=fiscal_period_days_entered,
    )


def vehicle_lines(worksheet: Worksheet) -> list[BusinessVehicleLine]:
    return [each for each in worksheet.trace if isinstance(each, BusinessVehicleLine)]


def test_a_leased_vehicle_gives_line_9819_of_2500_and_the_expenses_of_22500() -> None:
    # Chart A: line 12 is 1000 (3) + 400 (4, line 19) + 600 (5) + 200 (7) + 2147 (8, line 28)
    # + 653 (10) = 5000; line 13 is 5000 x 5000 / 10000 = 2500; line 16 is 2500 + 0 + 0 = 2500,
    # line 9819. Amount 4B is 20000 + 2500 = 22500 and line 9899 is 50000 - 22500 = 27500.
    worksheet = vehicle_statement(LEASED)

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_12 == D("5000")
    assert vehicle.line_13 == D("2500")
    assert line(worksheet, FARM_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("22500")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("27500")


def test_chart_b_interest_is_the_amount_payable_when_that_is_the_lesser() -> None:
    # Chart B line 18: 350 ÷ 30 × 183 days = 64050 ÷ 30 = 2135.00; line 17 is 400, the lesser, so
    # line 19, the available interest expense, is 400.
    (vehicle,) = vehicle_lines(vehicle_statement(LEASED))

    assert vehicle.line_19 == D("400.00")


def test_chart_b_interest_is_capped_at_the_350_over_30_a_day_amount() -> None:
    # Line 17 is 3000, more than line 18 of 2135.00 (350 ÷ 30 × 183), so line 19 is 2135.00.
    (vehicle,) = vehicle_lines(vehicle_statement({**LEASED, "interest_payable": "3000"}))

    assert vehicle.line_19 == D("2135.00")


def test_chart_c_takes_the_price_plus_tax_when_it_is_more_than_the_list_price() -> None:
    # Line 23 is 40000; 44706 plus 13% (5811.78) is 50517.78, the greater, and 85% of it is
    # 42940.113, which rounds to 42940.11 (line 24). Line 27 is 42940.00 x 2550 / 42940.11 =
    # 2549.99 and line 28 is the lesser of it and line 26 (7582.30): 2549.99.
    (vehicle,) = vehicle_lines(vehicle_statement({**LEASED, "list_price": "40000"}))

    assert vehicle.line_28 == D("2549.99")


def test_chart_c_takes_the_list_price_when_it_is_more_than_the_price_plus_tax() -> None:
    # Line 23 is 60000, more than 50517.78, so line 24 is 60000 x 85% = 51000.00.
    (vehicle,) = vehicle_lines(vehicle_statement(LEASED))

    assert vehicle.line_28 == D("2147.00")


def test_chart_c_leasing_cost_is_the_lesser_of_line_26_and_line_27() -> None:
    # Line 25 is (1100 + 13% of 1100 = 1243.00) x 183 days = 227469.00 ÷ 30 = 7582.30, so line 26 is
    # 7582.30 - 0 = 7582.30; line 27 is (38000 + 13% = 42940.00) x 2550 lease charges = 109497000
    # ÷ 51000.00 = 2147.00, so line 28, the leasing cost, is the lesser, 2147.00.
    (vehicle,) = vehicle_lines(vehicle_statement(LEASED))

    assert vehicle.line_28 == D("2147.00")


def test_chart_c_leasing_cost_is_line_26_when_the_payments_before_make_it_the_lesser() -> None:
    # Line 25 is 7582.30 and line 21 is 7000, so line 26 is 582.30, less than line 27 (2147.00):
    # line 28 is 582.30, line 12 is 1000 + 400 + 600 + 200 + 582.30 + 653 = 3435.30 and line 13 is
    # 3435.30 x 5000 / 10000 = 1717.65, line 9819.
    worksheet = vehicle_statement({**LEASED, "lease_payments_before": "7000"})

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_28 == D("582.30")
    assert vehicle.line_12 == D("3435.30")
    assert line(worksheet, FARM_MOTOR_VEHICLE_EXPENSES) == D("1717.65")


def test_chart_c_line_28_below_zero_is_refused() -> None:
    # Line 25 is 7582.30 and line 21 (payments before the year) is 9000, so line 26 is
    # 7582.30 - 9000 = -1417.70. The form prints no floor, but the eligible leasing cost (line 28)
    # is a non-negative amount, so the computation refuses it rather than inventing a floor.
    with pytest.raises(InputAboveBoundError, match="Chart C amount 21"):
        vehicle_statement({**LEASED, "lease_payments_before": "9000"})


NEGATIVE_NON_ARMS_LENGTH: dict[str, Any] = {
    "farm": {"wheat": "0", "cattle": "0", "seeds_and_plants": "1000"},
    "farm_non_arms_length_expenses": "5000",
}
POSITIVE_STATEMENT: dict[str, Any] = {"farm": {}}


def statement_with_non_arms_length(
    non_arms_length: str, farm: dict[str, str] | None = None
) -> Worksheet:
    """Return BC's statement with its T2042 Part 4 amount 4 (non-arm's length) set to
    `non_arms_length`, and `farm` changing or adding its amounts over `DEFAULT_FARM`."""
    amounts = {**DEFAULT_FARM, **(farm or {})}
    result = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": amounts, "farm_non_arms_length_expenses": non_arms_length},),
    )
    return result["ca/t2042"][0]


@pytest.mark.parametrize(
    ("statements", "amounts"),
    [
        ((NEGATIVE_NON_ARMS_LENGTH, POSITIVE_STATEMENT), (D("-4000"), D("0"))),
        ((POSITIVE_STATEMENT, NEGATIVE_NON_ARMS_LENGTH), (D("0"), D("-4000"))),
    ],
    ids=["above_first", "above_second"],
)
def test_a_non_arms_length_subtotal_above_the_expenses_is_worked_beside_a_positive_statement(
    statements: tuple[dict[str, Any], ...], amounts: tuple[Decimal, Decimal]
) -> None:
    # Statement one has line 9898 of 1000 and a non-arm's length amount 4 of 5000, so amount 5 is
    # 5000, above amount 1 of 1000: the form prints no maximum for amount 5, so its amount 6 is
    # 1000 - 5000 = -4000 whichever statement it is on, and Form T2043 line 67061 adds the amounts
    # 6 of both statements as printed.
    result = run("0", (), "0", "0", "0", "0", "0", farm_statements=statements)

    assert (
        tuple(worksheet.get(FARM_CHART_A_GROSS_EXPENSES).value for worksheet in result["ca/t2042"])
        == amounts
    )
    assert result["ca/t2043"][0].get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("-4000")


def test_a_non_arms_length_amount_above_the_expenses_of_50000_is_worked_as_printed() -> None:
    # Return BC's statement: line 9898 of 50000 (amount 1) and a non-arm's length amount 4 of 99999,
    # so amount 5 is 99999; the form prints no maximum for amount 5, so amount 6 "Amount 1 minus
    # amount 5" is 50000 - 99999 = -49999, signed.
    worksheet = statement_with_non_arms_length("99999")

    assert line(worksheet, FARM_CHART_A_SUBTOTAL) == D("99999")
    assert line(worksheet, FARM_CHART_A_GROSS_EXPENSES) == D("-49999")


def test_an_amount_5_equal_to_amount_1_is_accepted_and_gives_gross_0() -> None:
    # Amount 5 is 0 + 0 + 50000 and amount 1 is 50000: equal is valid, and amount 6 "Amount 1
    # minus amount 5" is 0.
    worksheet = statement_with_non_arms_length("50000")

    assert line(worksheet, FARM_CHART_A_SUBTOTAL) == D("50000")
    assert line(worksheet, FARM_CHART_A_GROSS_EXPENSES) == D("0")


def test_an_amount_5_of_40000_and_10000_of_mandatory_adjustment_is_accepted() -> None:
    # The mandatory inventory adjustment of the previous year (line 9937) is an expense, so line
    # 9898 is 50000 + 10000 = 60000 (amount 1). Amount 5 is 40000 + 10000 = 50000, at most 60000,
    # so it is accepted and amount 6 is 60000 - 50000 = 10000.
    worksheet = statement_with_non_arms_length(
        "40000", {"mandatory_inventory_adjustment_previous_year": "10000"}
    )

    assert line(worksheet, FARM_TOTAL_EXPENSES) == D("60000")
    assert line(worksheet, FARM_CHART_A_SUBTOTAL) == D("50000")
    assert line(worksheet, FARM_CHART_A_GROSS_EXPENSES) == D("10000")


def test_chart_a_business_use_part_is_rounded_half_up_to_the_cent() -> None:
    # Amount 1 of 1 and amount 2 of 3: 100 x 1 ÷ 3 = 33.333..., which rounds to 33.33 (line 13),
    # and line 16 is 33.33 + 0 + 0.
    worksheet = vehicle_statement(
        {"business_kilometres": "1", "total_kilometres": "3", "fuel_and_oil": "100"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("33.33")
    assert line(worksheet, FARM_MOTOR_VEHICLE_EXPENSES) == D("33.33")


def test_chart_a_business_use_part_is_0_when_there_are_no_total_kilometres() -> None:
    # A total of 0 kilometres gives a business use part of 0 (no division), so line 16 is only
    # the parking fees of 300.
    worksheet = vehicle_statement(
        {"business_kilometres": "0", "total_kilometres": "0", "parking_fees": "300"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("0")
    assert line(worksheet, FARM_MOTOR_VEHICLE_EXPENSES) == D("300")


# Two vehicles, as in Return BQ (returns/2025_return_bq.yaml) and the T2125 tests: an owned one
# with Chart B interest and a leased one with Chart C leasing.
OWNED: dict[str, str] = {
    "business_kilometres": "7000",
    "total_kilometres": "16000",
    "fuel_and_oil": "1200",
    "insurance": "900",
    "licence_and_registration": "150",
    "maintenance_and_repairs": "450",
    "interest_payable": "600",
    "interest_days": "183",
    "parking_fees": "120",
}
SECOND: dict[str, str] = {
    "business_kilometres": "3000",
    "total_kilometres": "12000",
    "fuel_and_oil": "600",
    "insurance": "450",
    "maintenance_and_repairs": "108",
    "other_expenses_10": "200",
    "lease_charges": "2550",
    "lease_payments_before": "1000",
    "lease_days": "183",
    "list_price": "60000",
    "supplementary_insurance": "60",
}


def test_two_vehicles_give_line_9819_of_the_line_16_amounts_added() -> None:
    # Owned: line 19 is 600 (less than 2135.00), line 12 is 1200 + 600 + 900 + 150 + 450 = 3300,
    # line 13 is 3300 x 7000 / 16000 = 1443.75 and line 16 is 1443.75 + 120 = 1563.75. Leased:
    # line 26 is 7582.30 - 1000 = 6582.30, line 28 is 2147.00, line 12 is 600 + 450 + 108 + 2147 +
    # 200 = 3505, line 13 is 3505 x 3000 / 12000 = 876.25 and line 16 is 876.25 + 60 = 936.25.
    # Line 9819 is 1563.75 + 936.25 = 2500.00; amount 4B is 20000 + 2500 = 22500 and line 9899 is
    # 50000 - 22500 = 27500.
    worksheet = vehicle_statement(OWNED, SECOND)

    first, second = vehicle_lines(worksheet)
    assert (first.line_12, first.line_13, first.line_19, first.line_28, first.line_16) == (
        D("3300"),
        D("1443.75"),
        D("600"),
        D("0"),
        D("1563.75"),
    )
    assert (second.line_12, second.line_13, second.line_19, second.line_28, second.line_16) == (
        D("3505"),
        D("876.25"),
        D("0"),
        D("2147.00"),
        D("936.25"),
    )
    assert line(worksheet, FARM_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, FARM_EXPENSES_SUBTOTAL) == D("22500")
    assert line(worksheet, FARM_NET_INCOME_BEFORE_ADJUSTMENTS) == D("27500")


def test_interest_days_above_the_fiscal_period_days_are_refused() -> None:
    # A fiscal period of 153 days (entered on the statement): the vehicle's 183 days of interest
    # are more days than the period has, so the vehicle is refused, naming both.
    with pytest.raises(InputAboveBoundError, match=r"item 1: (?=.*\b183\b)(?=.*\b153\b)"):
        vehicle_statement(LEASED, fiscal_period_days_entered=153)
