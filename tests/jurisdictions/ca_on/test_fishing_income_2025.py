"""The 2025 fishing income lines (T2121 Parts 3 to 7 and Area A, T1 lines 14299 and 14300), checked
against CRA's form.

2025 Form T2121 (Statement of Fishing Activities), Part 3 "Gross income: Total of amounts 3A to 3F
and line 9600 (enter this amount on line 14299 of your income tax and benefit return)"; Part 4
"Gross income (line 8299 of Part 3)" (4A), "Subtotal: Add amounts 4B to 4P." (4Q), "Total expenses:
Amount 4Q plus line 9936" (9368) and "Net income (loss) before adjustments: Amount 4A minus line
9368"
(9369); "Your cost (amount 4 minus amount 5)" (line 8963, amount 4O); Part 5 "Your share of line
9369
or the amount from your T5013 slip, Statement of Partnership Income" (5A), "Total: Amount 5A plus
line 9974" (5B) and "Your net income (loss): Amount 5C minus line 9945 (enter this amount on line
14300
of your income tax and benefit return)" (9946); Part 7 "Net income (loss) after adjustments (amount
5C) (if negative, enter "0")." and "Allowable claim: Amount 7M or 7N above, whichever is less (enter
your share of this amount on line 9945 of Part 5)"; Area A endnote 3: "If you have a negative amount
in column 7, add it to income as a recapture in Part 3 on line 9600. If no property is left in the
class and there is a positive amount in this column, deduct the amount from income as a terminal
loss
in Part 4 on line 9270. Recapture and terminal loss do not apply to a Class 10.1 property unless it
is
a DIEP." Every amount of the form is a dollars-and-cents box, and these lines only add and subtract
amounts already in cents (the capital cost allowance columns round with the `ca/cca_class_rates`
dataset, tested in test_rental_cca_2025.py), so the lines have no dataset of their own.

The lines are tested here one rule at a time on the registered kinds; the lines together, from the
income lines to T1 lines 14299 and 14300, are in `end_to_end/test_return_bd.py` and
`returns/2025_return_bd.yaml`. Form T2121 Charts A to C (the motor vehicle expenses, line 9281 of
Part 4, and the Chart B and C figures of a leased passenger vehicle) are at the end of this module;
the printed constants of the charts are the T2125's datasets, tested in
`test_t2125_motor_vehicle_2025.py`.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FISH_CCA_CLAIM,
    FISH_CCA_CLAIM_LESS_PERSONAL_PART,
    FISH_CCA_TABLE_CLAIM,
    FISH_EXPENSES_SUBTOTAL,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_HOME_ALLOWABLE_CLAIM,
    FISH_HOME_CARRY_FORWARD,
    FISH_HOME_EXPENSES,
    FISH_HOME_EXPENSES_AVAILABLE,
    FISH_HOME_INCOME_LIMIT,
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
)
from tax_calculator.jurisdictions.ca.trace import BusinessVehicleLine
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BD's statement, the default of these tests: one fish products amount of 40000 (amount 3A),
# expenses of 25000 (salt, bait and ice 10000 on line 9138, fishing gear 15000 on line 9136), so
# line
# 9369 is 15000, and no CCA, repairs, partner or business-use-of-home amounts.
DEFAULT_FISH = {"fish_products": "40000", "salt_bait_and_ice": "10000", "fishing_gear": "15000"}

# The 13 expense amounts of Part 4 that are entered directly, in the form's order: lines 4B to 4N
# (line 9281, the motor vehicle expenses, is the Chart A line below and not an amount here) and the
# other expenses of line 9270 (4P).
EXPENSE_NAMES = (
    "salt_bait_and_ice",
    "crew_shares",
    "fuel_costs",
    "fishing_gear",
    "insurance",
    "interest_and_bank_charges",
    "meals_and_entertainment",
    "business_taxes_licences_and_memberships",
    "office_expenses",
    "nets_and_traps",
    "professional_fees",
    "salaries_wages_and_benefits",
    "other_expenses",
)

CcaRow = tuple[str, str, str, str, str, str, str, int, str, str, str]


def statement(
    fish: dict[str, str] | None = None,
    partner: int = 0,
    cca_classes: tuple[CcaRow, ...] = (),
    vehicles: tuple[dict[str, str], ...] = (),
    fiscal_period_days_entered: int = 0,
    **overrides: Any,
) -> Worksheet:
    """Return BD's statement with `fish` changing or adding its amounts, `partner` the partner
    count (amount 5A) and `cca_classes` the Area A rows."""
    amounts = {**DEFAULT_FISH, **(fish or {})}
    result = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        fish_statements=(
            {
                "fish": amounts,
                "fish_partner": partner,
                "fish_cca_classes_rows": cca_classes,
                "fish_vehicles_rows": vehicles,
                "fish_fiscal_period_days_entered": fiscal_period_days_entered,
            },
        ),
        **overrides,
    )
    return result["ca/t2121"][0]


def line(worksheet: Worksheet, kind: ArtifactKind[Any]) -> Any:
    return worksheet.get(kind).value


def test_the_income_lines_3a_to_3f_and_line_9600_add_to_line_8299() -> None:
    # Amounts 3B "Other marine products" 1000, 3C "Grants, credits, and rebates" 2000 and 3D
    # "Subsidies" 4000 are entry lines, so line 8299 is 40000 + 1000 + 2000 + 4000 = 47000, and
    # amount
    # 4A is the same.
    worksheet = statement(
        {
            "other_marine_products": "1000",
            "grants_credits_and_rebates": "2000",
            "subsidies": "4000",
        }
    )

    assert line(worksheet, FISH_GROSS_INCOME) == D("47000")
    assert line(worksheet, FISH_GROSS_INCOME_BEFORE_EXPENSES) == D("47000")


def test_a_statement_with_no_other_amounts_is_the_income_less_the_expenses() -> None:
    # Income 40000 (line 8299 and T1 line 14299); expenses 25000 (4B and 4E), no CCA, so line 9368
    # is
    # 25000 and line 9369 is 40000 - 25000 = 15000, which is line 9946 and T1 line 14300.
    worksheet = statement()

    assert line(worksheet, FISH_GROSS_INCOME_BEFORE_EXPENSES) == D("40000")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("25000")
    assert line(worksheet, FISH_TOTAL_EXPENSES) == D("25000")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("15000")
    assert line(worksheet, FISHING_INCOME) == D("15000")


def test_a_recapture_row_adds_the_negative_column_7_to_line_9600() -> None:
    # Class 8: UCC at the start 1000, proceeds of dispositions 4000, so column 7 is
    # 1000 + 0 - 4000 = -3000, "a negative amount in column 7", added to income as a recapture on
    # line 9600: 3000. Other income of 500 makes line 9600 3500 (500 + 3000), so line 8299 is
    # 40000 + 3500 = 43500 and line 9369 is 43500 - 25000 = 18500. No claim is allowed on a
    # negative column 7.
    worksheet = statement(
        {"other_income": "500"},
        cca_classes=(("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),),
    )

    assert line(worksheet, FISH_RECAPTURED_CCA) == D("3000")
    assert line(worksheet, FISH_OTHER_INCOME_WITH_RECAPTURE) == D("3500")
    assert line(worksheet, FISH_GROSS_INCOME_BEFORE_EXPENSES) == D("43500")
    assert line(worksheet, FISH_CCA_CLAIM) == D("0")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("18500")


def test_a_terminal_loss_row_takes_the_positive_column_7_off_on_line_9270() -> None:
    # Class 8 with no property left: column 7 is 1000 + 0 - 0 = 1000, positive, so it is deducted
    # from income as a terminal loss in Part 4 on line 9270 (4P), with no CCA claimed on the class.
    # Line 9270 is 0 + 1000 = 1000, so 4Q is 25000 + 1000 = 26000 and line 9369 is
    # 40000 - 26000 = 14000.
    worksheet = statement(
        cca_classes=(("8", "1000", "0", "0", "0", "0", "0", 1, "0", "0", "0"),),
    )

    assert line(worksheet, FISH_TERMINAL_LOSS) == D("1000")
    assert line(worksheet, FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("1000")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("26000")
    assert line(worksheet, FISH_CCA_CLAIM) == D("0")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("14000")


def test_a_class_with_property_left_has_no_terminal_loss() -> None:
    # Column 7 is positive but property is left in the class, so no terminal loss: line 9270 is 0.
    worksheet = statement(cca_classes=(("8", "1000", "0", "0", "0", "0", "0", 0, "0", "0", "0"),))

    assert line(worksheet, FISH_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("25000")


def test_class_10_1_has_no_recapture_or_terminal_loss() -> None:
    # Class 10.1, column 7 is 1000 + 0 - 4000 = -3000 and no property is left: "Recapture and
    # terminal loss do not apply to a Class 10.1 property unless it is a DIEP", so both are 0.
    worksheet = statement(
        cca_classes=(("10.1", "1000", "0", "4000", "0", "0", "0", 1, "0", "0", "0"),)
    )

    assert line(worksheet, FISH_RECAPTURED_CCA) == D("0")
    assert line(worksheet, FISH_TERMINAL_LOSS) == D("0")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("15000")


def test_one_class_list_gives_a_claim_a_recapture_and_a_terminal_loss_together() -> None:
    # Class 8: UCC 10000, a claim of 2000 (the maximum, 10000 x 20%); class 10: column 7 of
    # -3000, a recapture of 3000 on line 9600; class 6: column 7 of 500 with no property left, a
    # terminal loss of 500 on line 9270. Line 9936 is 2000; line 9270 is 500; 4Q is 25000 + 500 =
    # 25500; line 9368 is 25500 + 2000 = 27500; line 8299 is 40000 + 3000 = 43000, so line 9369 is
    # 43000 - 27500 = 15500.
    worksheet = statement(
        cca_classes=(
            ("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0"),
            ("10", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),
            ("6", "500", "0", "0", "0", "0", "0", 1, "0", "0", "0"),
        ),
    )

    assert line(worksheet, FISH_CCA_TABLE_CLAIM) == D("2000")
    assert line(worksheet, FISH_CCA_CLAIM) == D("2000")
    assert line(worksheet, FISH_RECAPTURED_CCA) == D("3000")
    assert line(worksheet, FISH_TERMINAL_LOSS) == D("500")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("25500")
    assert line(worksheet, FISH_TOTAL_EXPENSES) == D("27500")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("15500")


def test_the_personal_part_and_the_business_use_of_home_cca_come_off_line_9936() -> None:
    # Amount ii is 2000; the personal part (a caller's 500) comes off to give 1500, and the CCA for
    # business-use-of-home expenses (amount 7K, a caller's 300) comes off to give line 9936, 1200.
    # Line 9368 is 25000 + 1200 = 26200, so line 9369 is 40000 - 26200 = 13800. Amount 7M is
    # 0 + 300 + 0 = 300 and line 9945 is 300, so line 9946 is 13800 - 300 = 13500.
    worksheet = statement(
        {"cca_personal_part": "500", "home_cca": "300"},
        cca_classes=(("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0"),),
    )

    assert line(worksheet, FISH_CCA_CLAIM_LESS_PERSONAL_PART) == D("1500")
    assert line(worksheet, FISH_CCA_CLAIM) == D("1200")
    assert line(worksheet, FISH_TOTAL_EXPENSES) == D("26200")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("13800")
    assert line(worksheet, FISH_HOME_EXPENSES_AVAILABLE) == D("300")
    assert line(worksheet, FISH_HOME_EXPENSES) == D("300")
    assert line(worksheet, FISHING_INCOME) == D("13500")


def test_every_expense_line_and_other_expenses_add_to_4q() -> None:
    # Each of the 13 amounts of Part 4 that is entered (lines 4B to 4N and the other expenses of
    # line 9270, 4P) is 100: 4Q is 1300, and with the income of 40000, line 9369 is 40000 - 1300 =
    # 38700.
    worksheet = statement({name: "100" for name in EXPENSE_NAMES})

    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("1300")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("38700")


def test_the_repairs_total_less_the_insurance_recovery_is_line_8963_and_adds_to_4q() -> None:
    # Repairs of the fishing boat 1000, engine 2000 and electrical equipment 500 are amount 4, 3500;
    # with an insurance recovery of 800 (amount 5), "Your cost" (amount 4O, line 8963) is 2700,
    # which
    # adds to 4Q: 25000 + 2700 = 27700, so line 9369 is 40000 - 27700 = 12300.
    worksheet = statement(
        {
            "repairs_fishing_boat": "1000",
            "repairs_engine": "2000",
            "repairs_electrical_equipment": "500",
            "insurance_recovery": "800",
        }
    )

    assert line(worksheet, FISH_REPAIRS_TOTAL) == D("3500")
    assert line(worksheet, FISH_REPAIRS_YOUR_COST) == D("2700")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("27700")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("12300")


def test_an_insurance_recovery_above_the_repairs_is_not_refused() -> None:
    # Amount 4 is 3500 and amount 5 is 4000: no printed bound limits the recovery to the repairs, so
    # your cost is 3500 less 4000 = -500 as printed and the expenses are 25000 less 500 = 24500.
    worksheet = statement(
        {
            "repairs_fishing_boat": "1000",
            "repairs_engine": "2000",
            "repairs_electrical_equipment": "500",
            "insurance_recovery": "4000",
        }
    )

    assert line(worksheet, FISH_REPAIRS_YOUR_COST) == D("-500")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("24500")


def test_a_recovery_equal_to_the_repairs_gives_a_line_8963_of_zero() -> None:
    worksheet = statement(
        {
            "salt_bait_and_ice": "0",
            "fishing_gear": "0",
            "repairs_fishing_boat": "100",
            "insurance_recovery": "100",
        }
    )

    assert line(worksheet, FISH_REPAIRS_YOUR_COST) == D("0")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("0")


def test_a_partner_takes_the_t5013_amount_for_amount_5a() -> None:
    # One partner (count 1): amount 5A is the T5013 amount, 12000, as entered; line 9946 is then
    # 12000 - 0 = 12000.
    worksheet = statement({"partner_share": "12000"}, partner=1)

    assert line(worksheet, FISH_SHARE_OF_NET_INCOME) == D("12000")
    assert line(worksheet, FISH_PARTNERSHIP_TOTAL) == D("12000")
    assert line(worksheet, FISH_NET_INCOME_AFTER_ADJUSTMENTS) == D("12000")
    assert line(worksheet, FISHING_INCOME) == D("12000")


def test_a_sole_proprietor_ignores_the_t5013_amount() -> None:
    # No partner (count 0): amount 5A is line 9369, 15000.
    worksheet = statement()

    assert line(worksheet, FISH_SHARE_OF_NET_INCOME) == D("15000")
    assert line(worksheet, FISHING_INCOME) == D("15000")


def test_the_gst_hst_rebate_for_partners_comes_into_amount_5b() -> None:
    # Amount 5B is amount 5A (15000) plus line 9974 (GST/HST rebate for partners, 200): 15200, and
    # with no partner amounts it is line 9946.
    worksheet = statement({"partner_share": "15000", "partner_gst_hst_rebate": "200"}, partner=1)

    assert line(worksheet, FISH_PARTNERSHIP_TOTAL) == D("15200")
    assert line(worksheet, FISHING_INCOME) == D("15200")


def test_a_loss_is_line_9369_below_zero_and_line_14300_in_brackets() -> None:
    # Income of 10000 (fish products) against expenses of 25000: line 9369 is -15000, and so are
    # amount 5A and line 9946, which is T1 line 14300 "(loss)"; the form prints no floor.
    worksheet = statement({"fish_products": "10000"})

    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("-15000")
    assert line(worksheet, FISH_SHARE_OF_NET_INCOME) == D("-15000")
    assert line(worksheet, FISH_NET_INCOME_AFTER_ADJUSTMENTS) == D("-15000")
    assert line(worksheet, FISHING_INCOME) == D("-15000")


def test_amount_7o_carries_the_whole_claim_forward_when_amount_5c_is_negative() -> None:
    # A loss of 15000 (amount 5C is -15000): business-use-of-home expenses of 2000 (amount 7A, heat)
    # give 7M of 2000. Amount 7N is 0 (not negative) "if negative, enter "0"", so amount 7P is the
    # lesser of 2000 and 0, 0, line 9945 is 0 and amount 7O carries the whole 2000 forward.
    worksheet = statement({"fish_products": "10000", "home_heat": "2000"})

    assert line(worksheet, FISH_HOME_EXPENSES_AVAILABLE) == D("2000")
    assert line(worksheet, FISH_HOME_INCOME_LIMIT) == D("0")
    assert line(worksheet, FISH_HOME_CARRY_FORWARD) == D("2000")
    assert line(worksheet, FISH_HOME_ALLOWABLE_CLAIM) == D("0")
    assert line(worksheet, FISH_HOME_EXPENSES) == D("0")
    assert line(worksheet, FISHING_INCOME) == D("-15000")


def test_amount_7o_is_0_when_amount_7n_is_larger_and_amount_7p_is_amount_7m() -> None:
    # Amount 7M is 2000 and amount 7N is amount 5C, 15000, so amount 7O is 0 and amount 7P, the
    # allowable claim, is 2000, which is line 9945; line 9946 is 15000 - 2000 = 13000.
    worksheet = statement({"home_heat": "2000"})

    assert line(worksheet, FISH_HOME_CARRY_FORWARD) == D("0")
    assert line(worksheet, FISH_HOME_ALLOWABLE_CLAIM) == D("2000")
    assert line(worksheet, FISH_HOME_EXPENSES) == D("2000")
    assert line(worksheet, FISHING_INCOME) == D("13000")


def test_amount_7p_is_amount_7n_when_the_home_expenses_exceed_the_net_income() -> None:
    # Net income of 1000 (amount 5C), amount 7M 3000 (heat): amount 7N is 1000, amount 7O is
    # 3000 - 1000 = 2000 carried forward and amount 7P, the lesser, is 1000, which is line 9945, so
    # line 9946 is 1000 - 1000 = 0.
    worksheet = statement({"fish_products": "26000", "home_heat": "3000"})

    assert line(worksheet, FISH_NET_INCOME_AFTER_ADJUSTMENTS) == D("1000")
    assert line(worksheet, FISH_HOME_CARRY_FORWARD) == D("2000")
    assert line(worksheet, FISH_HOME_ALLOWABLE_CLAIM) == D("1000")
    assert line(worksheet, FISHING_INCOME) == D("0")


def test_the_partner_other_amounts_come_off_at_line_9943() -> None:
    # Amounts 6A and 6B (100 and 200) make amount 6F and line 9943, 300; amount 5C is 15000 - 300.
    worksheet = statement(
        {
            "partner_share": "15000",
            "partner_other_amount_a": "100",
            "partner_other_amount_b": "200",
        },
        partner=1,
    )

    assert line(worksheet, FISH_PARTNER_OTHER_AMOUNTS_TOTAL) == D("300")
    assert line(worksheet, FISH_PARTNER_OTHER_AMOUNTS) == D("300")
    assert line(worksheet, FISH_NET_INCOME_AFTER_ADJUSTMENTS) == D("14700")
    assert line(worksheet, FISHING_INCOME) == D("14700")


# Form T2121 Charts A to C: one leased passenger vehicle used half for fishing, a record of the
# statement's `ca/business_vehicles`. The statement is fish products of 40000 and fishing gear of
# 20000, so the other amounts are 0, and the sales tax rate of the province is 13%.
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
    """A T2121 of fish products of 40000 and fishing gear of 20000, with one record of
    `ca/business_vehicles` for each vehicle given (the amounts not given are 0)."""
    return statement(
        {"salt_bait_and_ice": "0", "fishing_gear": "20000", "vehicle_sales_tax_rate": "13"},
        vehicles=vehicles,
        fiscal_period_days_entered=fiscal_period_days_entered,
    )


def vehicle_lines(worksheet: Worksheet) -> list[BusinessVehicleLine]:
    return [each for each in worksheet.trace if isinstance(each, BusinessVehicleLine)]


def test_a_leased_vehicle_gives_line_9281_of_2500_and_the_expenses_of_22500() -> None:
    # Chart A: line 12 is 1000 (3) + 400 (4, line 19) + 600 (5) + 200 (7) + 2147 (8, line 28)
    # + 653 (10) = 5000; line 13 is 5000 x 5000 / 10000 = 2500; line 16 is 2500 + 0 + 0 = 2500,
    # line 9281. Amount 4Q is 20000 + 2500 = 22500 and line 9369 is 40000 - 22500 = 17500.
    worksheet = vehicle_statement(LEASED)

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_12 == D("5000")
    assert vehicle.line_13 == D("2500")
    assert line(worksheet, FISH_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("22500")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("17500")


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
    # 3435.30 x 5000 / 10000 = 1717.65, line 9281.
    worksheet = vehicle_statement({**LEASED, "lease_payments_before": "7000"})

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_28 == D("582.30")
    assert vehicle.line_12 == D("3435.30")
    assert line(worksheet, FISH_MOTOR_VEHICLE_EXPENSES) == D("1717.65")


def test_chart_c_line_28_below_zero_is_refused() -> None:
    # Line 25 is 7582.30 and line 21 (payments before the year) is 9000, so line 26 is
    # 7582.30 - 9000 = -1417.70. The form prints no floor, but the eligible leasing cost (line 28)
    # is a non-negative amount, so the computation refuses it rather than inventing a floor.
    with pytest.raises(InputAboveBoundError, match="Chart C amount 21"):
        vehicle_statement({**LEASED, "lease_payments_before": "9000"})


def test_chart_a_business_use_part_is_rounded_half_up_to_the_cent() -> None:
    # Amount 1 of 1 and amount 2 of 3: 100 x 1 ÷ 3 = 33.333..., which rounds to 33.33 (line 13),
    # and line 16 is 33.33 + 0 + 0.
    worksheet = vehicle_statement(
        {"business_kilometres": "1", "total_kilometres": "3", "fuel_and_oil": "100"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("33.33")
    assert line(worksheet, FISH_MOTOR_VEHICLE_EXPENSES) == D("33.33")


def test_chart_a_business_use_part_is_0_when_there_are_no_total_kilometres() -> None:
    # A total of 0 kilometres gives a business use part of 0 (no division), so line 16 is only
    # the parking fees of 300.
    worksheet = vehicle_statement(
        {"business_kilometres": "0", "total_kilometres": "0", "parking_fees": "300"}
    )

    (vehicle,) = vehicle_lines(worksheet)
    assert vehicle.line_13 == D("0")
    assert line(worksheet, FISH_MOTOR_VEHICLE_EXPENSES) == D("300")


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


def test_two_vehicles_give_line_9281_of_the_line_16_amounts_added() -> None:
    # Owned: line 19 is 600 (less than 2135.00), line 12 is 1200 + 600 + 900 + 150 + 450 = 3300,
    # line 13 is 3300 x 7000 / 16000 = 1443.75 and line 16 is 1443.75 + 120 = 1563.75. Leased:
    # line 26 is 7582.30 - 1000 = 6582.30, line 28 is 2147.00, line 12 is 600 + 450 + 108 + 2147 +
    # 200 = 3505, line 13 is 3505 x 3000 / 12000 = 876.25 and line 16 is 876.25 + 60 = 936.25.
    # Line 9281 is 1563.75 + 936.25 = 2500.00; amount 4Q is 20000 + 2500 = 22500 and line 9369 is
    # 40000 - 22500 = 17500.
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
    assert line(worksheet, FISH_MOTOR_VEHICLE_EXPENSES) == D("2500")
    assert line(worksheet, FISH_EXPENSES_SUBTOTAL) == D("22500")
    assert line(worksheet, FISH_NET_INCOME_BEFORE_ADJUSTMENTS) == D("17500")


def test_interest_days_above_the_fiscal_period_days_are_refused() -> None:
    # A fiscal period of 100 days (entered on the statement): the vehicle's 183 days of interest
    # are more days than the period has, so the vehicle is refused, naming both.
    with pytest.raises(InputAboveBoundError, match=r"item 1: (?=.*\b183\b)(?=.*\b100\b)"):
        vehicle_statement(LEASED, fiscal_period_days_entered=100)
