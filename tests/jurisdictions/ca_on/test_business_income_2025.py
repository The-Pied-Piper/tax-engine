"""The 2025 business income lines (T2125 Parts 3A to 7 and Area A, T1 lines 13499 and 13500),
checked against CRA's form.

2025 Form T2125 (Statement of Business or Professional Activities), "Part 3C - Gross business or
professional income": "Other income (specify): 8230" and "Subtotal: Line 8290 plus line 8230 3O";
Area A endnote 3: "If you have a negative amount in column 7, add it to income as a recapture in
Part 3C on line 8230. If no property is left in the class and there is a positive amount in this
column, deduct the amount from income as a terminal loss in Part 4 on line 9270. Recapture and
terminal loss do not apply to a Class 10.1 property unless it is a DIEP."; Part 5 "Your share of
line 9369 or the amount from your T5013 slip, Statement of Partnership Income."; Part 7 "Net income
(loss) after adjustments (amount 5D) (if negative, enter "0")." and "Business-use-of-home
expenses available to carry forward: Amount 7M minus amount 7N (if negative, enter "0")". Every
amount of the form is a dollars-and-cents box, and these lines only add and subtract amounts
already in cents (the capital cost allowance columns round with the `ca/cca_class_rates`
dataset, tested in test_rental_cca_2025.py), so the lines have no dataset of their own.

The lines are tested here one rule at a time on the registered kinds; the lines together, from
the gross sales to T1 lines 13499 and 13500, are in `end_to_end/test_return_bb.py` and
`returns/2025_return_bb.yaml`.
"""

from __future__ import annotations

from typing import Any

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_ADJUSTED_GROSS_SALES,
    BUSINESS_ADVERTISING,
    BUSINESS_BAD_DEBTS,
    BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_COST_OF_GOODS_SOLD,
    BUSINESS_COST_OF_GOODS_SUBTOTAL,
    BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS,
    BUSINESS_FUEL_COSTS,
    BUSINESS_GROSS_INCOME,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_GROSS_PROFIT,
    BUSINESS_HOME_ALLOWABLE_CLAIM,
    BUSINESS_HOME_CARRY_FORWARD,
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_AVAILABLE,
    BUSINESS_HOME_EXPENSES_BUSINESS_PART,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_HOME_INCOME_LIMIT,
    BUSINESS_INCOME,
    BUSINESS_INSURANCE,
    BUSINESS_INTEREST_AND_BANK_CHARGES,
    BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES,
    BUSINESS_MEALS_AND_ENTERTAINMENT,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_OFFICE_EXPENSES,
    BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES,
    BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    BUSINESS_OTHER_INCOME_WITH_RECAPTURE,
    BUSINESS_PARTNER_OTHER_AMOUNTS,
    BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL,
    BUSINESS_PARTNERSHIP_TOTAL,
    BUSINESS_PROFESSIONAL_FEES,
    BUSINESS_PROPERTY_TAXES,
    BUSINESS_QUICK_METHOD_ASSISTANCE,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_RENT,
    BUSINESS_REPAIRS_AND_MAINTENANCE,
    BUSINESS_RESERVES_AND_OTHER_INCOME,
    BUSINESS_SALARIES_WAGES_AND_BENEFITS,
    BUSINESS_SALES_SUBTOTAL,
    BUSINESS_SHARE_OF_NET_INCOME,
    BUSINESS_TERMINAL_LOSS,
    BUSINESS_TOTAL_EXPENSES,
    BUSINESS_TRAVEL_EXPENSES,
    BUSINESS_UTILITIES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

ROW_8 = ("8", "10000", "0", "0", "0", "0", "2000", 0, "0", "0", "0")

# The 18 expense lines of Part 4, amounts 4B to 4T except 4T (motor vehicle expenses, amount 16
# of Chart A, see test_t2125_motor_vehicle_2025.py).
EXPENSE_KINDS: tuple[ArtifactKind[Any], ...] = (
    BUSINESS_ADVERTISING,  # advertising
    BUSINESS_MEALS_AND_ENTERTAINMENT,  # meals_and_entertainment
    BUSINESS_BAD_DEBTS,  # bad_debts
    BUSINESS_INSURANCE,  # insurance
    BUSINESS_INTEREST_AND_BANK_CHARGES,  # interest_and_bank_charges
    BUSINESS_BUSINESS_TAXES_LICENCES_AND_MEMBERSHIPS,  # business_taxes_licences_and_memberships
    BUSINESS_OFFICE_EXPENSES,  # office_expenses
    BUSINESS_OFFICE_STATIONERY_AND_SUPPLIES,  # office_stationery_and_supplies
    BUSINESS_PROFESSIONAL_FEES,  # professional_fees
    BUSINESS_MANAGEMENT_AND_ADMINISTRATION_FEES,  # management_and_administration_fees
    BUSINESS_RENT,  # rent
    BUSINESS_REPAIRS_AND_MAINTENANCE,  # repairs_and_maintenance
    BUSINESS_SALARIES_WAGES_AND_BENEFITS,  # salaries_wages_and_benefits
    BUSINESS_PROPERTY_TAXES,  # property_taxes
    BUSINESS_TRAVEL_EXPENSES,  # travel_expenses
    BUSINESS_UTILITIES,  # utilities
    BUSINESS_FUEL_COSTS,  # fuel_costs
    BUSINESS_DELIVERY_FREIGHT_AND_EXPRESS,  # delivery_freight_and_express
)


CcaRow = tuple[str, str, str, str, str, str, str, int, str, str, str]


def statement(
    business: dict[str, str] | None = None,
    partner: int = 0,
    cca_classes: tuple[CcaRow, ...] = (),
    **overrides: Any,
) -> Worksheet:
    """A T2125 of gross sales of 50000 and office expenses of 20000, so line 9369 is 30000,
    with `business` changing or adding its amounts and `overrides` the other inputs."""
    amounts = {"gross_sales": "50000", "office_expenses": "20000", **(business or {})}
    result = run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(
            {
                "business": amounts,
                "business_partner": partner,
                "business_cca_classes_rows": cca_classes,
            },
        ),
        **overrides,
    )
    return result["ca/t2125"][0]


def line(worksheet: Worksheet, kind: ArtifactKind[Any]) -> Any:
    return worksheet.get(kind).value


def test_a_statement_with_no_other_amounts_is_gross_sales_less_expenses() -> None:
    worksheet = statement()

    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30000")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000")


def test_a_recapture_row_adds_the_negative_column_7_to_line_8230() -> None:
    # Class 8: UCC at the start 1000, proceeds of dispositions 4000, so column 7 is
    # 1000 + 0 - 4000 = -3000, "a negative amount in column 7", added to income as a recapture
    # on line 8230: 3000. Other income (specified) of 500 makes line 8230 3500, and with line
    # 8290 (reserves deducted last year) of 200, amount 3O is 3700. Line 8299 is 50000 + 3700 =
    # 53700, and line 9369 is 53700 - 20000 = 33700. No claim is allowed on a negative column 7.
    worksheet = statement(
        {"other_income": "500", "reserves_deducted_last_year": "200"},
        cca_classes=(("8", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),),
    )

    assert line(worksheet, BUSINESS_RECAPTURED_CCA) == D("3000")
    assert line(worksheet, BUSINESS_OTHER_INCOME_WITH_RECAPTURE) == D("3500")
    assert line(worksheet, BUSINESS_RESERVES_AND_OTHER_INCOME) == D("3700")
    assert line(worksheet, BUSINESS_GROSS_INCOME) == D("53700")
    assert line(worksheet, BUSINESS_CCA_CLAIM) == D("0")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("33700")
    assert worksheet.get(BUSINESS_INCOME).value == D("33700")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "business_recaptured_cca: item 1 class 8: column 7 -3000 is negative: recapture 3000"
    ) in rendered
    assert (
        "business_other_income_with_recapture: business_other_income 500 "
        "+ business_recaptured_cca 3000 = 3500"
    ) in rendered


def test_a_terminal_loss_row_takes_the_positive_column_7_off_on_line_9270() -> None:
    # Class 1: UCC at the start 2000, no additions or dispositions, no property left in the
    # class: column 7 is 2000, "a positive amount in this column" with "no property left in the
    # class", deducted as a terminal loss on line 9270. With other expenses (specified) of 300,
    # line 9270 is 2300, line 9368 is 20000 + 2300 = 22300 and line 9369 is 50000 - 22300 = 27700.
    worksheet = statement(
        {"other_expenses": "300"},
        cca_classes=(("1", "2000", "0", "0", "0", "0", "0", 1, "0", "0", "0"),),
    )

    assert line(worksheet, BUSINESS_TERMINAL_LOSS) == D("2000")
    assert line(worksheet, BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("2300")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("22300")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("27700")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "business_terminal_loss: item 1 class 1: column 7 2000 with no property left: "
        "terminal loss 2000"
    ) in rendered


def test_a_class_with_property_left_has_no_terminal_loss() -> None:
    worksheet = statement(cca_classes=(("1", "2000", "0", "0", "0", "0", "0", 0, "0", "0", "0"),))

    assert line(worksheet, BUSINESS_TERMINAL_LOSS) == D("0")
    assert line(worksheet, BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS) == D("0")


def test_class_10_1_has_no_recapture_or_terminal_loss() -> None:
    # Endnote 3: "Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP", and DIEPs (columns 4, 6, 8 and 9) are not modelled.
    recapture = statement(
        cca_classes=(("10.1", "1000", "0", "4000", "0", "0", "0", 0, "0", "0", "0"),)
    )
    terminal = statement(cca_classes=(("10.1", "2000", "0", "0", "0", "0", "0", 1, "0", "0", "0"),))

    assert line(recapture, BUSINESS_RECAPTURED_CCA) == D("0")
    assert line(terminal, BUSINESS_TERMINAL_LOSS) == D("0")


def test_one_class_list_gives_a_claim_a_recapture_and_a_terminal_loss_together() -> None:
    # Class 8 (claim 2000 of its maximum 2000.00), Class 10 (UCC 500, proceeds 1500: column 7
    # -1000, a recapture of 1000) and Class 1 (UCC 3000, no property left: a terminal loss of
    # 3000). Line 9936 is 2000; line 8230 is 1000 and line 8299 is 51000; line 9270 is 3000; line
    # 9368 is 20000 + 2000 + 3000 = 25000 and line 9369 is 51000 - 25000 = 26000.
    worksheet = statement(
        cca_classes=(
            ROW_8,
            ("10", "500", "0", "1500", "0", "0", "0", 0, "0", "0", "0"),
            ("1", "3000", "0", "0", "0", "0", "0", 1, "0", "0", "0"),
        ),
    )

    assert line(worksheet, BUSINESS_CCA_TABLE_CLAIM) == D("2000")
    assert line(worksheet, BUSINESS_CCA_CLAIM) == D("2000")
    assert line(worksheet, BUSINESS_RECAPTURED_CCA) == D("1000")
    assert line(worksheet, BUSINESS_GROSS_INCOME) == D("51000")
    assert line(worksheet, BUSINESS_TERMINAL_LOSS) == D("3000")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("25000")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("26000")
    closing = line(worksheet, BUSINESS_CLOSING_UCC)
    assert [list(record.values()) for record in closing.records] == [
        [D("8"), D("8000")],
        [D("10"), D("0")],
        [D("1"), D("0")],
    ]


def test_the_personal_part_and_the_business_use_of_home_cca_come_off_line_9936() -> None:
    # Line 9936 is "amount ii of Area A minus any personal part and any CCA for business-use-of-home
    # expenses": 2000 - 300 - 200 = 1500, so line 9368 is 20000 + 1500 = 21500 and line 9369
    # is 28500. The 200 of CCA for business-use-of-home expenses (amount 7K) is added to amount
    # 7M: 0 + 200 + 0.
    worksheet = statement({"cca_personal_part": "300", "home_cca": "200"}, cca_classes=(ROW_8,))

    assert line(worksheet, BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART) == D("1700")
    assert line(worksheet, BUSINESS_CCA_CLAIM) == D("1500")
    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("21500")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("28500")
    assert line(worksheet, BUSINESS_HOME_EXPENSES_AVAILABLE) == D("200")


def test_every_expense_line_from_4b_to_4t_adds_to_line_9368() -> None:
    # 18 lines of 100, 200 ... 1800 (4B to 4T except 4T), which add to 17100; 4T is 0 with no
    # Chart A amounts. Plus 4U (line 9936) 2000 and 4V (line 9270) 50: line 9368 is 19150, and line
    # 9369 is 50000 - 19150 = 30850.
    amounts = {
        kind.identifier.removeprefix("ca/business_"): str(100 * (index + 1))
        for index, kind in enumerate(EXPENSE_KINDS)
    }
    assert sum(D(amount) for amount in amounts.values()) == D("17100")

    worksheet = statement(
        {**amounts, "other_expenses": "50"},
        cca_classes=(ROW_8,),
    )

    assert line(worksheet, BUSINESS_TOTAL_EXPENSES) == D("19150")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30850")


def test_the_cost_of_goods_sold_comes_off_the_gross_income_before_the_expenses() -> None:
    # Part 3D: amounts 3Q to 3U 1000 + 8000 + 500 + 300 + 200 = 10000 (amount 3V); line 8500
    # 2500; line 8518 is 10000 - 2500 = 7500; line 8519 is 50000 - 7500 = 42500, which is amount
    # 4A; with the 20000 of expenses line 9369 is 22500.
    worksheet = statement(
        {
            "opening_inventory": "1000",
            "purchases": "8000",
            "direct_wage_costs": "500",
            "subcontracts": "300",
            "other_costs": "200",
            "closing_inventory": "2500",
        }
    )

    assert line(worksheet, BUSINESS_COST_OF_GOODS_SUBTOTAL) == D("10000")
    assert line(worksheet, BUSINESS_COST_OF_GOODS_SOLD) == D("7500")
    assert line(worksheet, BUSINESS_GROSS_PROFIT) == D("42500")
    assert line(worksheet, BUSINESS_GROSS_INCOME_BEFORE_EXPENSES) == D("42500")
    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("22500")


def test_the_quick_method_assistance_is_amount_3d_less_amount_3e() -> None:
    # Amount 3A 11300 (with the GST/HST collected), amount 3B 0: amount 3C 11300. Amount 3D 1300
    # less amount 3E 406.80 (entered: no capability multiplies by a rate the caller enters) is
    # amount 3F, 893.20; amount 3G, and so line 8000, is 11300 + 893.20 = 12193.20.
    worksheet = statement(
        {
            "gross_sales": "11300",
            "office_expenses": "0",
            "quick_method_gst_hst": "1300",
            "quick_method_remitted": "406.80",
        }
    )

    assert line(worksheet, BUSINESS_SALES_SUBTOTAL) == D("11300")
    assert line(worksheet, BUSINESS_QUICK_METHOD_ASSISTANCE) == D("893.20")
    assert line(worksheet, BUSINESS_ADJUSTED_GROSS_SALES) == D("12193.20")
    assert line(worksheet, BUSINESS_GROSS_INCOME) == D("12193.20")


def test_a_partner_takes_the_t5013_amount_for_amount_5a() -> None:
    # A partner (count 1) enters the amount from the T5013 slip, 12000, for amount 5A, though
    # line 9369 is 30000. Amount 5B 100 and line 9974 50 make amount 5C 12150; amounts 6A and
    # 6B 200 and 100 make amount 6F, and so line 9943, 300; amount 5D is 12150 - 300 = 11850,
    # which is line 9946 with no business-use-of-home expenses.
    worksheet = statement(
        {
            "partner_share": "12000",
            "journalism_labour_tax_credit": "100",
            "partner_gst_hst_rebate": "50",
            "partner_other_amount_a": "200",
            "partner_other_amount_b": "100",
        },
        partner=1,
    )

    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("30000")
    assert line(worksheet, BUSINESS_SHARE_OF_NET_INCOME) == D("12000")
    assert line(worksheet, BUSINESS_PARTNERSHIP_TOTAL) == D("12150")
    assert line(worksheet, BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL) == D("300")
    assert line(worksheet, BUSINESS_PARTNER_OTHER_AMOUNTS) == D("300")
    assert line(worksheet, BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS) == D("11850")
    assert worksheet.get(BUSINESS_INCOME).value == D("11850")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "business_share_of_net_income: business_partner_share 12000, "
        "chosen as business_partner_checked is 1"
    ) in rendered


def test_a_sole_proprietor_ignores_the_t5013_amount() -> None:
    worksheet = statement(partner=0)

    assert line(worksheet, BUSINESS_SHARE_OF_NET_INCOME) == D("30000")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000")


def test_a_partners_t5013_amount_may_be_a_loss() -> None:
    # Amount 5A is "Your share of line 9369 or the amount from your T5013 slip": a loss on the
    # slip is entered as a negative figure, and line 9946, "Your net income (loss)", is negative.
    worksheet = statement({"partner_share": "-4000"}, partner=1)

    assert line(worksheet, BUSINESS_SHARE_OF_NET_INCOME) == D("-4000")
    assert line(worksheet, BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS) == D("-4000")
    assert worksheet.get(BUSINESS_INCOME).value == D("-4000")


def test_a_loss_is_line_9369_below_zero_and_line_13500_in_brackets() -> None:
    # Gross sales 1000 less expenses 5000: line 9369 is -4000, "Net income (loss) before
    # adjustments", with no floor, and so is line 9946 and T1 line 13500.
    worksheet = statement({"gross_sales": "1000", "office_expenses": "5000"})

    assert line(worksheet, BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS) == D("-4000")
    assert line(worksheet, BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS) == D("-4000")
    assert worksheet.get(BUSINESS_INCOME).value == D("-4000")


def test_amount_7n_is_0_when_amount_5d_is_negative_and_the_whole_claim_is_carried_forward() -> None:
    # Part 7 amount 7N is "Net income (loss) after adjustments (amount 5D) (if negative, enter
    # "0")": amount 5D is -4000, so amount 7N is 0. Amount 7M is 1500 (heat) + 100 carried forward
    # from the previous year = 1600, so amount 7O, 7M minus 7N, is 1600 to carry forward, and
    # amount 7P, the lesser of 7M and 7N, is 0: line 9945 is 0 and line 9946 is -4000 - 0.
    worksheet = statement(
        {
            "gross_sales": "1000",
            "office_expenses": "5000",
            "home_heat": "1500",
            "home_carried_forward": "100",
        }
    )

    assert line(worksheet, BUSINESS_HOME_INCOME_LIMIT) == D("0")
    assert line(worksheet, BUSINESS_HOME_EXPENSES_AVAILABLE) == D("1600")
    assert line(worksheet, BUSINESS_HOME_CARRY_FORWARD) == D("1600")
    assert line(worksheet, BUSINESS_HOME_ALLOWABLE_CLAIM) == D("0")
    assert line(worksheet, BUSINESS_HOME_EXPENSES) == D("0")
    assert worksheet.get(BUSINESS_INCOME).value == D("-4000")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "business_home_income_limit: business_net_income_after_adjustments -4000, not below 0 = 0"
    ) in rendered
    assert (
        "business_home_carry_forward: business_home_expenses_available 1600 "
        "less business_home_income_limit 0, not below 0 = 1600"
    ) in rendered


def test_amount_7o_is_0_when_amount_7n_is_larger_and_amount_7p_is_amount_7m() -> None:
    # Amount 7M 2000 (7A to 7G 2400 less 7I 400), amount 7N 30000: amount 7O is 2000 - 30000,
    # negative, so 0; amount 7P, the lesser of 2000 and 30000, is 2000 = line 9945.
    worksheet = statement(
        {"home_heat": "1400", "home_electricity": "1000", "home_personal_use_part": "400"}
    )

    assert line(worksheet, BUSINESS_HOME_EXPENSES_SUBTOTAL) == D("2400")
    assert line(worksheet, BUSINESS_HOME_EXPENSES_BUSINESS_PART) == D("2000")
    assert line(worksheet, BUSINESS_HOME_CARRY_FORWARD) == D("0")
    assert line(worksheet, BUSINESS_HOME_ALLOWABLE_CLAIM) == D("2000")
    assert line(worksheet, BUSINESS_HOME_EXPENSES) == D("2000")
    assert worksheet.get(BUSINESS_INCOME).value == D("28000")


def test_amount_7p_is_amount_7n_when_the_home_expenses_exceed_the_net_income() -> None:
    # Amount 7M 40000 exceeds amount 7N 30000: amount 7P is 30000 (the lesser), amount 7O is
    # 40000 - 30000 = 10000 to carry forward, and line 9946 is 30000 - 30000 = 0.
    worksheet = statement({"home_heat": "40000"})

    assert line(worksheet, BUSINESS_HOME_ALLOWABLE_CLAIM) == D("30000")
    assert line(worksheet, BUSINESS_HOME_CARRY_FORWARD) == D("10000")
    assert worksheet.get(BUSINESS_INCOME).value == D("0")
