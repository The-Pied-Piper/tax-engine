"""CA-ON 2025 end to end: return ex, the branches no earlier worked return reaches.

Return EX is `returns/2025_return_ex.yaml`: a business (T2125 statement 1) with the GST/HST quick
method, reserves, other income, a recapture and a terminal loss of capital cost allowance, a cost of
goods sold, a minister's allocation and a business-use-of-home claim; a professional partnership
(statement 2) with other amounts deductible and a home claim carried forward; a rental property
(T776 statement 1) with a personal portion and a terminal loss; and a rental partnership (statement
2). Net business income 48,528.00, net rental income 25,900.00, total income 74,428.00, balance
owing 14,224.65.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
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
    BUSINESS_HOME_CARRY_FORWARD,
    BUSINESS_HOME_EXPENSES,
    BUSINESS_HOME_EXPENSES_AVAILABLE,
    BUSINESS_HOME_EXPENSES_BUSINESS_PART,
    BUSINESS_HOME_EXPENSES_SUBTOTAL,
    BUSINESS_HOME_INCOME_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    BUSINESS_INCOME,
    BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED,
    BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    BUSINESS_OTHER_INCOME_WITH_RECAPTURE,
    BUSINESS_PARTNER_CHECKED,
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
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    GROSS_BUSINESS_INCOME,
    GROSS_ON_BUSINESS_LINE,
    GROSS_RENTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_ON_BUSINESS_LINE,
    NET_RENTAL_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_PAYMENTS_LIMIT_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_CCA_CLAIM_SHARE,
    RENTAL_CCA_LIMIT,
    RENTAL_CCA_TABLE_CLAIM,
    RENTAL_CCA_TABLE_TERMINAL_LOSS,
    RENTAL_CLOSING_UCC,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_EXPENSES_LESS_PERSONAL_PORTION,
    RENTAL_GROSS_RENTS,
    RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED,
    RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_PARTNER_SHARE_WITH_REBATE,
    RENTAL_PARTNERSHIP_NET_INCOME,
    RENTAL_PERSONAL_PORTION,
    RENTAL_TERMINAL_LOSS,
    RENTAL_TOTAL_EXPENSES,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    NON_REFUNDABLE_TAX_CREDITS as ONTARIO_NON_REFUNDABLE_TAX_CREDITS,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_BASIC_TAX,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    ONTARIO_TAX_LESS_DIVIDEND_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return EX's T2125 statement 1, a business (line code 1). The amounts are by the name after
# `ca/business_`; the amounts not listed are 0. Gross sales 113000 with HST 13000 (amounts 3A and
# 3B); the quick method on the HST of 13000 with 4972 remitted; reserves deducted last year 2000
# and other income 500; the cost of goods sold lines; seven expense lines; and the business-use-of-
# home expenses of 5500 (1500 personal part) with 500 carried forward from last year.
BUSINESS_ONE: dict[str, Any] = {
    "business": {
        "gross_sales": "113000",
        "sales_adjustments": "13000",
        "quick_method_gst_hst": "13000",
        "quick_method_remitted": "4972",
        "reserves_deducted_last_year": "2000",
        "other_income": "500",
        "opening_inventory": "8000",
        "purchases": "30000",
        "direct_wage_costs": "6000",
        "subcontracts": "4000",
        "other_costs": "1000",
        "closing_inventory": "9000",
        "advertising": "1500",
        "meals_and_entertainment": "900",
        "insurance": "1200",
        "office_expenses": "800",
        "professional_fees": "2500",
        "rent": "6000",
        "utilities": "1500",
        "vehicle_sales_tax_rate": "13",
        "other_expenses": "300",
        "home_heat": "900",
        "home_electricity": "700",
        "home_insurance": "300",
        "home_maintenance": "400",
        "home_mortgage_interest": "1800",
        "home_property_taxes": "1200",
        "home_other_expenses": "200",
        "home_personal_use_part": "1500",
        "home_carried_forward": "500",
    },
    "business_cca_classes_rows": (
        ("8", "3000", "0", "7000", "0", "0", "0", 0, "0", "0", "0"),
        ("10", "3500", "0", "1000", "0", "0", "0", 1, "0", "0", "0"),
        ("14.1", "20000", "0", "0", "0", "0", "1000", 0, "0", "0", "0"),
        ("50", "5000", "2000", "0", "0", "0", "3300", 0, "0", "0", "0"),
    ),
    "business_minister_allocation_given": 1,
    "business_minister_allocation": "1100000",
}

# Return EX's T2125 statement 2, a professional partnership (line code 2) with no gross income and
# no expenses of its own: the partner's share is the T5013 slip amount 18000, with the journalism
# labour tax credit 400, the GST/HST rebate for partners 350, the other amounts 600, 450, 300, 200
# and 100, and the business-use-of-home expenses (15000, 2000 personal part) with 5000 carried.
BUSINESS_TWO: dict[str, Any] = {
    "business": {
        "journalism_labour_tax_credit": "400",
        "partner_gst_hst_rebate": "350",
        "partner_other_amount_a": "600",
        "partner_other_amount_b": "450",
        "partner_other_amount_c": "300",
        "partner_other_amount_d": "200",
        "partner_other_amount_e": "100",
        "home_heat": "3000",
        "home_electricity": "2500",
        "home_insurance": "600",
        "home_maintenance": "1200",
        "home_mortgage_interest": "4000",
        "home_property_taxes": "3000",
        "home_other_expenses": "700",
        "home_personal_use_part": "2000",
        "home_carried_forward": "5000",
        "partner_share": "18000",
    },
    "business_partner": 1,
    "business_income_line": 2,
}

# Return EX's T776 statement 1, a sole owner's rental: three units with gross rents of 36000 (none
# short-term) and other income of 600; the expenses of Part 4 with their personal portions; a Class
# 1 and a Class 8 row of Area A; and the minister's allocation of 800000.
RENTAL_ONE: dict[str, Any] = {
    "rental_properties": ((3, "0", "36000"),),
    "rental_other_income": "600",
    "rental_expenses": {
        "advertising": ("400", "0", "0"),
        "insurance": ("1800", "300", "0"),
        "interest_and_bank_charges": ("5000", "0", "0"),
        "office_expenses": ("200", "0", "0"),
        "professional_fees": ("700", "0", "0"),
        "repairs_and_maintenance": ("1500", "0", "0"),
        "property_taxes": ("3200", "400", "0"),
        "utilities": ("2400", "600", "0"),
    },
    "rental_cca_classes_rows": (
        ("1", "100000", "0", "0", "0", "0", "4000", 0, "0", "0", "0", "0"),
        ("8", "2400", "0", "1500", "0", "0", "0", 1, "0", "0", "0", "0"),
    ),
    "rental_minister_allocation_given": 1,
    "rental_minister_allocation": "800000",
}

# Return EX's T776 statement 2, a rental partnership: no rents or expenses of its own; the partner's
# share is the T5013 slip amount 9000, with the GST/HST rebate for partners 250 and the partner's
# other expenses 1150.
RENTAL_TWO: dict[str, Any] = {
    "rental_partner": 1,
    "rental_partner_t5013_slip": 1,
    "rental_partner_share": "9000",
    "rental_partner_gst_hst_rebate": "250",
    "rental_partner_other_expenses": "1150",
}


def run_ex(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return EX's inputs, as in `returns/2025_return_ex.yaml`, with `overrides` over them.

    Two T2125 statements (a business and a professional partnership) and two T776 statements (a
    sole owner's rental and a rental partnership). The CPP and QPP months (12), the Schedule 8
    instance (one, empty), and the residence and age flags (1) are `run`'s defaults, as in the YAML.
    """
    inputs: dict[str, Any] = {
        "business_statements": (BUSINESS_ONE, BUSINESS_TWO),
        "rental_statements": (RENTAL_ONE, RENTAL_TWO),
    }
    return run("0", (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def return_ex(**overrides: Any) -> Worksheet:
    """The return form's worksheet of `run_ex`: T1 lines 13499 to the balance owing."""
    return run_ex(**overrides)["ca-on/return"][0]


def statement_ex(index: int, **overrides: Any) -> Worksheet:
    """The worksheet of Return EX's T2125 statement `index` (0 the business, 1 the partnership)."""
    return run_ex(**overrides)["ca/t2125"][index]


def rental_ex(index: int, **overrides: Any) -> Worksheet:
    """The worksheet of Return EX's T776 statement `index` (0 the sole owner's, 1 partnership)."""
    return run_ex(**overrides)["ca/t776"][index]


def test_return_exs_part_3a_quick_method_gives_adjusted_gross_sales_108028() -> None:
    # Part 3A: amount 3A 113000 less amount 3B 13000 is amount 3C 100000. Quick method: amount 3D
    # 13000 less amount 3E 4972 is amount 3F 8028. Amount 3G, line 8000, is 100000 + 8028 = 108028.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_SALES_SUBTOTAL).value == D("100000")
    assert worksheet.get(BUSINESS_QUICK_METHOD_ASSISTANCE).value == D("8028")
    assert worksheet.get(BUSINESS_ADJUSTED_GROSS_SALES).value == D("108028")


def test_return_exs_part_3c_reserves_other_income_and_recapture_give_gross_income_114528() -> None:
    # Part 3C: line 8290 (reserves deducted last year) is 2000; line 8230 is the other income 500
    # plus the recapture 4000 of Class 8 (endnote 3), 4500. Amount 3O is 2000 + 4500 = 6500, and
    # line 8299 is 108028 + 6500 = 114528, which is T1 line 13499.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_RECAPTURED_CCA).value == D("4000")
    assert worksheet.get(BUSINESS_OTHER_INCOME_WITH_RECAPTURE).value == D("4500")
    assert worksheet.get(BUSINESS_RESERVES_AND_OTHER_INCOME).value == D("6500")
    assert worksheet.get(BUSINESS_GROSS_INCOME).value == D("114528")
    assert worksheet.get(BUSINESS_GROSS_INCOME_FOR_GROSS_PROFIT).value == D("114528")


def test_return_exs_part_3d_cost_of_goods_sold_is_40000_and_gross_profit_74528() -> None:
    # Part 3D: amounts 3Q to 3U are 8000 + 30000 + 6000 + 4000 + 1000, so amount 3V is 49000; line
    # 8500 (closing inventory) is 9000, so line 8518 (cost of goods sold) is 49000 - 9000 = 40000.
    # Line 8519 (gross profit) is amount 3P less line 8518: 114528 - 40000 = 74528 (amount 4A).
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_COST_OF_GOODS_SUBTOTAL).value == D("49000")
    assert worksheet.get(BUSINESS_COST_OF_GOODS_SOLD).value == D("40000")
    assert worksheet.get(BUSINESS_GROSS_PROFIT).value == D("74528")
    assert worksheet.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("74528")


def test_return_exs_area_a_class_10_is_a_terminal_loss_of_2500_on_line_9270() -> None:
    # Area A, Class 10: column 2 3500, column 5 1000, column 7 2500, positive with no property left
    # in the class (column 3 is 0): a terminal loss of 2500, deducted in Part 4 on line 9270, with
    # no claim and 0 at the end of the year. Line 9270 is the other expenses 300 plus 2500, 2800.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_TERMINAL_LOSS).value == D("2500")
    assert worksheet.get(BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("2800")


def test_return_exs_area_a_claims_4300_on_line_9936_from_classes_14_1_and_50() -> None:
    # Area A, Class 14.1: column 2 20000, column 7 20000, column 19 20000; the maximum is 20000 x
    # 5% = 1000.00 and 1000 is claimed. Class 50: column 2 5000, column 3 2000, column 7 7000;
    # column 18 is one half of 2000, 1000.00; column 19 is 7000 - 1000 = 6000.00; the maximum is
    # 6000 x 55% = 3300.00 and 3300 is claimed. Classes 8 and 10 claim nothing (the recapture and
    # the terminal loss). Amount ii is 1000 + 3300 = 4300, and with no personal part or business-
    # use-of-home CCA, line 9936 is 4300.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_CCA_TABLE_CLAIM).value == D("4300")
    assert worksheet.get(BUSINESS_CCA_CLAIM_LESS_PERSONAL_PART).value == D("4300")
    assert worksheet.get(BUSINESS_CCA_CLAIM).value == D("4300")


def test_return_exs_closing_ucc_is_0_0_19000_and_3700_by_class() -> None:
    # Column 22 is column 7 less the claim: Class 8 is 0 (recaptured), Class 10 is 0 (terminal
    # loss), Class 14.1 is 20000 - 1000 = 19000 and Class 50 is 7000 - 3300 = 3700.
    worksheet = statement_ex(0)

    closing = worksheet.get(BUSINESS_CLOSING_UCC).value
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in closing.records] == [
        (D("8"), D("0")),
        (D("10"), D("0")),
        (D("14.1"), D("19000")),
        (D("50"), D("3700")),
    ]


def test_return_exs_part_4_expenses_are_21500_and_net_income_before_adjustments_53028() -> None:
    # Part 4: advertising 1500, meals and entertainment 900, insurance 1200, office expenses 800,
    # professional fees 2500, rent 6000 and utilities 1500 are 14400; line 9270 is 2800 and line
    # 9936 is 4300, so line 9368 is 14400 + 2800 + 4300 = 21500. Line 9369 is 74528 - 21500 = 53028.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("21500")
    assert worksheet.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("53028")


def test_return_exs_part_5_sole_proprietor_statement_has_no_partnership_amounts() -> None:
    # No partner (count 0): amount 5A is line 9369, 53028; amounts 5B and 9974 and 6A to 6E are 0,
    # so amount 5C is 53028 and amount 5D is 53028, with line 9943 at 0.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_SHARE_OF_NET_INCOME).value == D("53028")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("0")
    assert worksheet.get(BUSINESS_PARTNERSHIP_TOTAL).value == D("53028")
    assert worksheet.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("53028")


def test_return_exs_part_7_home_expenses_claim_4500_and_business_income_48528() -> None:
    # Part 7: amounts 7A to 7G are 900 + 700 + 300 + 400 + 1800 + 1200 + 200 = 5500 (7H); amount 7I
    # is the personal part 1500, so 7J is 4000; amount 7K is 0 and 7L is 500 carried forward, so 7M
    # is 4500. Amount 7N is 53028 and 7O is 0; 7P, the lesser of 4500 and 53028, is 4500 (line
    # 9945). Line 9946 is 53028 - 4500 = 48528, which is T1 line 13500.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_HOME_EXPENSES_SUBTOTAL).value == D("5500")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("4000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_AVAILABLE).value == D("4500")
    assert worksheet.get(BUSINESS_HOME_INCOME_LIMIT).value == D("53028")
    assert worksheet.get(BUSINESS_HOME_EXPENSES).value == D("4500")
    assert worksheet.get(BUSINESS_INCOME).value == D("48528")


def test_return_exs_minister_allocation_1100000_is_the_immediate_expensing_limit() -> None:
    # Endnote 5: the immediate expensing limit is the amount allocated by the minister, 1100000
    # (count 1), and not the $1.5 million; no class has DIEP additions, so nothing is expensed.
    worksheet = statement_ex(0)

    assert worksheet.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1100000")
    assert worksheet.get(BUSINESS_MINISTER_ALLOCATION_GIVEN_CHECKED).value == 1


def test_return_exs_business_line_of_statement_1_is_gross_114528_and_net_48528() -> None:
    # Line code 1: the gross on the business line is line 8299, 114528; the net is line 9946,
    # 48528, both reported on the business line (T1 line 13500 for the net).
    worksheet = statement_ex(0)

    assert worksheet.get(GROSS_ON_BUSINESS_LINE).value == D("114528")
    assert worksheet.get(NET_ON_BUSINESS_LINE).value == D("48528")


def test_return_exs_partner_other_amounts_are_1650_and_partnership_total_18750() -> None:
    # Part 5: amount 5A is the T5013 amount 18000 (count 1); amount 5B is the journalism labour tax
    # credit 400 and line 9974 the GST/HST rebate for partners 350, so amount 5C is
    # 18000 + 400 + 350 = 18750. Part 6: amounts 6A to 6E are 600 + 450 + 300 + 200 + 100 = 1650
    # (amount 6F, line 9943).
    worksheet = statement_ex(1)

    assert worksheet.get(BUSINESS_SHARE_OF_NET_INCOME).value == D("18000")
    assert worksheet.get(BUSINESS_PARTNERSHIP_TOTAL).value == D("18750")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS).value == D("1650")
    assert worksheet.get(BUSINESS_PARTNER_OTHER_AMOUNTS_TOTAL).value == D("1650")


def test_return_exs_partner_net_income_is_17100_and_line_9946_is_0() -> None:
    # Part 5: amount 5D is 18750 - 1650 = 17100, which is the partner's net income after the
    # adjustments. Line 9946 is amount 5D less line 9945 (the home claim, 17100): 0 (T1 line 13700).
    worksheet = statement_ex(1)

    assert worksheet.get(BUSINESS_NET_INCOME_AFTER_ADJUSTMENTS).value == D("17100")
    assert worksheet.get(BUSINESS_INCOME).value == D("0")


def test_return_exs_partner_home_expenses_carry_900_forward() -> None:
    # Part 7: amounts 7A to 7G are 3000 + 2500 + 600 + 1200 + 4000 + 3000 + 700 = 15000 (7H); amount
    # 7I is the personal part 2000, so 7J is 13000; amount 7L is 5000 carried forward, so 7M is
    # 18000. Amount 7N is 17100, so amount 7O (carried forward) is 18000 - 17100 = 900, and amount
    # 7P, the lesser of 18000 and 17100, is 17100 (line 9945).
    worksheet = statement_ex(1)

    assert worksheet.get(BUSINESS_HOME_EXPENSES_SUBTOTAL).value == D("15000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_BUSINESS_PART).value == D("13000")
    assert worksheet.get(BUSINESS_HOME_EXPENSES_AVAILABLE).value == D("18000")
    assert worksheet.get(BUSINESS_HOME_INCOME_LIMIT).value == D("17100")
    assert worksheet.get(BUSINESS_HOME_CARRY_FORWARD).value == D("900")
    assert worksheet.get(BUSINESS_HOME_EXPENSES).value == D("17100")


def test_return_exs_partner_statement_has_the_1500000_immediate_expensing_limit() -> None:
    # No minister's allocation (count 0) and no EPOP: the limit is $1.5 million, not prorated.
    worksheet = statement_ex(1)

    assert worksheet.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1500000")


def test_return_exs_line_27_is_48528_from_the_business_lines_alone() -> None:
    # Statement 1 gives line 9946 of 48528 (T1 line 13500); statement 2 gives 0 (line 13700); there
    # is no commission, farming or fishing income. The gross on T1 line 13499 is 114528 (statement
    # 1 line 8299; statement 2 has no gross), so line 27 is 48528 + 0 + 0 + 0 + 0 = 48528.
    worksheet = return_ex()

    assert worksheet.get(GROSS_BUSINESS_INCOME).value == D("114528")
    assert worksheet.get(BUSINESS_INCOME).value == D("48528")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("48528")


def test_return_exs_t776_income_is_25900_and_total_income_74428() -> None:
    # T776 line 9946 gives 17800 (statement 1) and 8100 (statement 2), so the rental income of T1
    # line 12600 is 25900. Total income (line 15000) is 48528 + 25900 = 74428, which is net income
    # and taxable income, there being no deduction.
    worksheet = return_ex()

    assert worksheet.get(NET_RENTAL_INCOME).value == D("25900")
    assert worksheet.get(TOTAL_INCOME).value == D("74428")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("74428")
    assert worksheet.get(OTHER_PAYMENTS_LIMIT_INCOME).value == D("74428")
    assert worksheet.get(NET_INCOME).value == D("74428")
    assert worksheet.get(TAXABLE_INCOME).value == D("74428")


def test_return_exs_federal_tax_after_credits_is_9476_54() -> None:
    # Part A, column 2: line 72 is 74428.00 - 57375.00 = 17053.00, times 20.5% is 3495.865, rounded
    # half-up 3495.87; plus line 75 (8319.38) is 11815.25. The basic personal amount 16129.00 times
    # 14.5% is 2338.705, rounded 2338.71; 11815.25 - 2338.71 = 9476.54.
    worksheet = return_ex()

    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("11815.25")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("2338.71")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("9476.54")


def test_return_exs_ontario_tax_is_4748_11_with_the_health_premium_of_750() -> None:
    # ON428 Part A: 74428.00 - 52886.00 = 21542.00 times 9.15% is 1971.093, rounded 1971.09; plus
    # line 7 (2670.74) is 4641.83. The basic personal amount 12747.00 times 5.05% is 643.7235,
    # rounded 643.72; 4641.83 - 643.72 = 3998.11, below the surtax threshold 5710, so no surtax and
    # no tax reduction (twice the basic reduction 588.00 is below 3998.11, so line 80 is 0). The
    # Ontario health premium for taxable income of 72600 to 200000 is 750; line 42800 is
    # 3998.11 + 750 = 4748.11.
    worksheet = return_ex()

    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("4641.83")
    assert worksheet.get(ONTARIO_NON_REFUNDABLE_TAX_CREDITS).value == D("643.72")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("3998.11")
    assert worksheet.get(ONTARIO_TAX_LESS_DIVIDEND_CREDIT).value == D("3998.11")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("750")
    assert worksheet.get(ONTARIO_TAX).value == D("4748.11")


def test_return_exs_balance_owing_is_13824_65_after_the_journalism_credit_of_400() -> None:
    # The total payable is the federal tax after credits 9476.54 plus the Ontario tax 4748.11,
    # 14224.65; line 162 takes the journalism labour tax credit, the amount 5B of statement 2 (400),
    # so the balance owing is 14224.65 - 400 = 13824.65.
    worksheet = return_ex()

    assert worksheet.get(TOTAL_PAYABLE).value == D("14224.65")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("13824.65")


def test_return_exs_cpp_second_additional_maximum_is_9900_with_no_cpp_computed() -> None:
    # The CPP second additional earnings maximum is the year's parameter, 9900.00. No CPP is
    # computed: the 12 months of CPP are on Schedule 8 box A, and Part 4 is not completed.
    worksheet = return_ex()

    assert worksheet.get(CPP_SECOND_ADDITIONAL_EARNINGS_MAXIMUM).value == D("9900.00")


def test_return_exs_t776_personal_portion_1300_and_deductible_expenses_13900() -> None:
    # Expenses: 400 + 1800 + 5000 + 200 + 700 + 1500 + 3200 + 2400 = 15200 (amount A). The personal
    # portion (line 9949) is 300 of the insurance, 400 of the property taxes and 600 of the
    # utilities, 1300. Amount 1 is 15200 - 1300 - 0 = 13900 (no short-term portion). Gross income is
    # 36000 + 600 = 36600 (line 8299), so line 9369 is 36600 - 13900 = 22700.
    worksheet = rental_ex(0)

    assert worksheet.get(RENTAL_TOTAL_EXPENSES).value == D("15200")
    assert worksheet.get(RENTAL_PERSONAL_PORTION).value == D("1300")
    assert worksheet.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("13900")
    assert worksheet.get(RENTAL_EXPENSES_LESS_PERSONAL_PORTION).value == D("13900")
    assert worksheet.get(GROSS_RENTAL_INCOME).value == D("36600")
    assert worksheet.get(RENTAL_GROSS_RENTS).value == D("36000")
    assert worksheet.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("22700")


def test_return_exs_t776_terminal_loss_900_on_class_8_leaves_21800() -> None:
    # Area A, Class 8: column 2 2400, column 5 1500, column 7 900, positive with no property left in
    # the class: a terminal loss of 900 (line 9948), no claim and 0 at the end of the year. Amount 5
    # is 22700 - 900 = 21800.
    worksheet = rental_ex(0)

    assert worksheet.get(RENTAL_CCA_TABLE_TERMINAL_LOSS).value == D("900")
    assert worksheet.get(RENTAL_TERMINAL_LOSS).value == D("900")
    assert worksheet.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("21800")


def test_return_exs_t776_cca_claim_4000_on_class_1_leaves_net_17800() -> None:
    # Area A, Class 1: column 2 100000, column 7 100000; the maximum is 100000 x 4% = 4000.00 and
    # 4000 is claimed. Line 9936 is 4000, less than amount 5 (21800), which limits it; amount 6,
    # line 9946, is 21800 - 4000 = 17800, the statement's net rental income.
    worksheet = rental_ex(0)

    assert worksheet.get(RENTAL_CCA_TABLE_CLAIM).value == D("4000")
    assert worksheet.get(RENTAL_CCA_CLAIM).value == D("4000")
    assert worksheet.get(RENTAL_CCA_CLAIM_SHARE).value == D("4000")
    assert worksheet.get(RENTAL_CCA_LIMIT).value == D("21800")
    assert worksheet.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("17800")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("17800")


def test_return_exs_t776_sole_owner_has_no_co_owner_or_recapture_adjustments() -> None:
    # No co-owner (count 0): amount 2 is 22700, line 9945 is 0, and amount 3 is 22700; line 9947
    # (recapture) is 0, so amount 4 is 22700. The co-owner expenses leave 22700 unchanged.
    worksheet = rental_ex(0)

    assert worksheet.get(RENTAL_NET_INCOME_SHARE).value == D("22700")
    assert worksheet.get(RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES).value == D("22700")
    assert worksheet.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("22700")


def test_return_exs_t776_closing_ucc_is_96000_for_class_1_and_0_for_class_8() -> None:
    # Column 22 is column 7 less the claim: Class 1 is 100000 - 4000 = 96000; Class 8 is 0 (the
    # terminal loss takes the whole of its UCC).
    worksheet = rental_ex(0)

    closing = worksheet.get(RENTAL_CLOSING_UCC).value
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in closing.records] == [
        (D("1"), D("96000")),
        (D("8"), D("0")),
    ]


def test_return_exs_t776_minister_allocation_800000_is_the_rental_limit() -> None:
    # The minister allocated a chosen 800000 (count 1): the rental's immediate expensing limit.
    worksheet = rental_ex(0)

    assert worksheet.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("800000")
    assert worksheet.get(RENTAL_MINISTER_ALLOCATION_GIVEN_CHECKED).value == 1


def test_return_exs_t776_rental_partnership_is_9250_share_and_net_8100() -> None:
    # Statement 2, a partner: the partner's share is the T5013 amount 9000 plus the GST/HST rebate
    # for partners 250, so line 9974 gives 9250 (line 7 plus line 9974). Line 9943 (the partner's
    # other expenses) is 1150, so line 9946 is 9000 + 250 - 1150 = 8100 (T1 line 12600). With no
    # minister allocation (count 0), the limit is $1.5 million.
    worksheet = rental_ex(1)

    assert worksheet.get(RENTAL_PARTNER_SHARE_WITH_REBATE).value == D("9250")
    assert worksheet.get(RENTAL_PARTNERSHIP_NET_INCOME).value == D("8100")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("8100")
    assert worksheet.get(RENTAL_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1500000")


def test_variant_a_class_10_with_property_left_claims_750_and_has_no_terminal_loss() -> None:
    # Class 10 with the same 3500 start, proceeds 1000, but property left in the class (no property
    # left is 0): column 7 is 3500 - 1000 = 2500, positive, but no terminal loss (line 9270 is not
    # used). Column 19 is 2500 and the maximum is 2500 x 30% = 750.00, claimed 750; column 22 is
    # 2500 - 750 = 1750. Line 9936 is 1000 + 3300 + 750 = 5050 (no personal part). Part 4 is
    # 14400 + 300 + 5050 = 19750 (other expenses 300, no terminal loss). Line 9369 is
    # 74528 - 19750 = 54778; amount 7N is 54778, not below 4500, so the home claim is 4500 and line
    # 9946 is 54778 - 4500 = 50278.
    class_10_open = ("10", "3500", "0", "1000", "0", "0", "750", 0, "0", "0", "0")
    statement = {
        **BUSINESS_ONE,
        "business_cca_classes_rows": (
            ("8", "3000", "0", "7000", "0", "0", "0", 0, "0", "0", "0"),
            class_10_open,
            ("14.1", "20000", "0", "0", "0", "0", "1000", 0, "0", "0", "0"),
            ("50", "5000", "2000", "0", "0", "0", "3300", 0, "0", "0", "0"),
        ),
    }
    worksheet = statement_ex(0, business_statements=(statement, BUSINESS_TWO))

    assert worksheet.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(BUSINESS_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("300")
    assert worksheet.get(BUSINESS_CCA_CLAIM).value == D("5050")
    assert worksheet.get(BUSINESS_TOTAL_EXPENSES).value == D("19750")
    assert worksheet.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("54778")
    assert worksheet.get(BUSINESS_INCOME).value == D("50278")
    _class_8, class_10, _class_14_1, _class_50 = worksheet.get(BUSINESS_CLOSING_UCC).value.records
    assert class_10[CCA_UCC_AT_END] == D("1750")


def test_variant_b_without_a_minister_allocation_the_limit_is_1500000() -> None:
    # Statement 1 with no minister's allocation (count 0) and no EPOP: the immediate expensing limit
    # is the $1.5 million of endnote 5, not the 1100000 given.
    statement = {
        **BUSINESS_ONE,
        "business_minister_allocation_given": 0,
        "business_minister_allocation": "0",
    }
    worksheet = statement_ex(0, business_statements=(statement, BUSINESS_TWO))

    assert worksheet.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_UNPRORATED).value == D("1500000")


def test_variant_c_t776_class_8_with_property_left_claims_180_and_has_no_terminal_loss() -> None:
    # Class 8 with the 2400 start and proceeds 1500, but property left in the class: column 7 is
    # 2400 - 1500 = 900, positive, but no terminal loss (line 9948 is not used). Column 19 is 900
    # and the maximum is 900 x 20% = 180.00, claimed 180; column 22 is 900 - 180 = 720. Line 9936 is
    # 4000 + 180 = 4180. Amount 5 is 22700 (no terminal loss), so amount 6, line 9946, is
    # 22700 - 4180 = 18520, the statement's net rental income.
    class_8_open = ("8", "2400", "0", "1500", "0", "0", "180", 0, "0", "0", "0", "0")
    statement = {
        **RENTAL_ONE,
        "rental_cca_classes_rows": (
            ("1", "100000", "0", "0", "0", "0", "4000", 0, "0", "0", "0", "0"),
            class_8_open,
        ),
    }
    worksheet = rental_ex(0, rental_statements=(statement, RENTAL_TWO))

    assert worksheet.get(RENTAL_TERMINAL_LOSS).value == D("0")
    assert worksheet.get(RENTAL_CCA_CLAIM).value == D("4180")
    assert worksheet.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("18520")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("18520")
    (closing_1, closing_8) = worksheet.get(RENTAL_CLOSING_UCC).value.records
    assert closing_8[CCA_UCC_AT_END] == D("720")
    assert closing_1[CCA_UCC_AT_END] == D("96000")


def test_variant_d_partner_count_0_with_the_partner_figures_gives_amount_6_on_line_9946() -> None:
    # Statement 2 with no partner (count 0) but the partner's lines (the share 9000, the rebate
    # 250 and the other expenses 1150) entered: line 9946 is amount 6, which is 0 here, and not
    # the partnership's 8100 (9000 + 250 - 1150).
    statement = {**RENTAL_TWO, "rental_partner": 0, "rental_partner_t5013_slip": 0}
    worksheet = rental_ex(1, rental_statements=(RENTAL_ONE, statement))

    assert worksheet.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("0")


# --- the partner figures of the business's partner (Part 5 of T2125) with the partner answer. A
# partner figure (the T5013 share, the journalism labour tax credit, the GST/HST rebate for partners
# and the other amounts A to E) is a partner's: the form prints no rule against typing one with the
# partner answer 0, so it is not refused.

BUSINESS_PARTNER_FIGURES = (
    "partner_share",
    "journalism_labour_tax_credit",
    "partner_gst_hst_rebate",
    "partner_other_amount_a",
    "partner_other_amount_e",
)


def run_business_partner(answer: int, **figures: str) -> dict[str, tuple[Worksheet, ...]]:
    """Return EX with the business's partner answer `answer` and the partner figures `figures`,
    the others (the statement's own) given as 0."""
    partner_figures = {
        name: "0"
        for name in (
            *BUSINESS_PARTNER_FIGURES,
            "partner_other_amount_b",
            "partner_other_amount_c",
            "partner_other_amount_d",
        )
    }
    business = {**BUSINESS_TWO["business"], **partner_figures, **figures}
    statement = {**BUSINESS_TWO, "business": business, "business_partner": answer}
    return run_ex(business_statements=(BUSINESS_ONE, statement))


@pytest.mark.parametrize(
    ("figure", "total"),
    [
        ("partner_share", "400"),
        ("journalism_labour_tax_credit", "400"),
        ("partner_gst_hst_rebate", "400"),
        ("partner_other_amount_a", "0"),
        ("partner_other_amount_e", "0"),
    ],
)
def test_a_business_partner_figure_with_the_partner_answer_1_is_accepted(
    figure: str, total: str
) -> None:
    statement = run_business_partner(1, **{figure: "400"})["ca/t2125"][1]

    assert statement.get(BUSINESS_PARTNER_CHECKED).value == 1
    assert statement.get(BUSINESS_PARTNERSHIP_TOTAL).value == D(total)


@pytest.mark.parametrize(
    ("figure", "total"),
    [
        ("partner_share", "0"),
        ("journalism_labour_tax_credit", "400"),
        ("partner_gst_hst_rebate", "400"),
        ("partner_other_amount_a", "0"),
        ("partner_other_amount_e", "0"),
    ],
)
def test_a_business_partner_figure_with_the_partner_answer_0_is_accepted(
    figure: str, total: str
) -> None:
    statement = run_business_partner(0, **{figure: "400"})["ca/t2125"][1]

    assert statement.get(BUSINESS_PARTNER_CHECKED).value == 0
    assert statement.get(BUSINESS_PARTNERSHIP_TOTAL).value == D(total)


def test_a_business_partner_answer_above_1_is_refused() -> None:
    # The partner answer of Part 5 is a yes or no answer: 2 is refused, not read as yes.
    with pytest.raises(
        InputAboveBoundError, match="business_partner 2 is above a yes or no answer of 1"
    ):
        run_business_partner(2)


def test_the_trace_checks_the_business_partner_answer_as_a_yes_or_no_count() -> None:
    statement = run_business_partner(1)["ca/t2125"][1]
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert "business_partner_checked: business_partner 1, a yes or no answer of 0 or 1" in rendered
