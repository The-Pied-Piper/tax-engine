"""CA-ON 2025 end to end: return bx."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidRecordError,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FARM_CCA_CLAIM,
    FARM_CCA_TABLE_CLAIM,
    FARM_CLOSING_UCC,
    FARM_EPOP_PERCENTAGE_MAXIMUM,
    FARM_EPOP_PERCENTAGE_ROOM,
    FARM_GROSS_INCOME,
    FARM_GROSS_INCOME_BEFORE_EXPENSES,
    FARM_IMMEDIATE_EXPENSING_ALLOCATED,
    FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FARM_IMMEDIATE_EXPENSING_CAP,
    FARM_IMMEDIATE_EXPENSING_CLAIM,
    FARM_IMMEDIATE_EXPENSING_LIMIT,
    FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FARM_IMMEDIATE_EXPENSING_SHARE,
    FARM_INCOME_BEFORE_CCA,
    FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS,
    FARM_NET_INCOME_BEFORE_ADJUSTMENTS,
    FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FARM_TERMINAL_LOSS,
    FARM_TOTAL_EXPENSES,
    FARMING_INCOME,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BX's T2042, Return BC's with the wheat raised by 5200 to 55200 (a chosen figure, so that
# line 9946 stays Return BC's 30000): income lines of 85200 (wheat 55200 on line 9371, cattle
# 30000 on line 9471) and expenses of 50000 (fertilizers and lime 20000 on line 9662, seeds and
# plants 30000 on line 9664), with no inventory adjustment or partner.
FARM = {
    "wheat": "55200",
    "cattle": "30000",
    "fertilizers_and_lime": "20000",
    "seeds_and_plants": "30000",
    # Charts A to C for one leased passenger vehicle that is used for no farming: business
    # kilometres 0 (amount 1), so line 9819 (amount 16 of Chart A) is 0, as in Return BC.
    "vehicle_sales_tax_rate": "13",
}

# The farm of Return BX with lines 9941 (optional) 1000 and 9942 (mandatory) 500, which make
# amount 4C 31500 against line 9899, 30000.00.
INVENTORY_ADJUSTMENTS = {
    "farm": {
        **FARM,
        "optional_inventory_adjustment_current_year": "1000",
        "mandatory_inventory_adjustment_current_year": "500",
    }
}
# Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9): class 8 with a UCC of 10000 and additions of 5000,
# all DIEPs (column 4 5000), of which 3000 is expensed at once (column 9): column 21 is 11000.00 x
# 20% = 2200.00 plus 3000, so 5200.00, claimed in full.
FURNITURE = ("8", "10000", "5000", "0", "0", "0", "5200.00", 0, "5000", "0", "3000")
# Charts A to C for one leased passenger vehicle used for no farming, as in Return BC.
VEHICLE = {
    "business_kilometres": "0",
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
# Area G and endnote 5: associated with one other EPOP (1) under an agreement that was filed (1),
# the percentage assigned to your business 50 and the total of column 3 100, so amount iv is
# 1500000 x 50% = 750000.00; no amount allocated by the minister.
AREA_G = {
    "farm_epop_associated": 1,
    "farm_epop_agreement_filed": 1,
    "farm_epop_percentage": "50",
    "farm_epop_percentage_total": "100",
}


def run_bx(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return BX's inputs, as in `returns/2025_return_bx.yaml`: Return BC's sole proprietor with
    one DIEP expensed at once and Area G.

    One T2042 statement for the farm: income of 85200 (line 9659 and T1 line 14099), expenses of
    50000 (4B) and 5200.00 of capital cost allowance (Class 8, opening UCC 10000, additions 5000,
    all DIEPs, 3000 expensed at once, claim 5200.00), 55200.00 in all (line 9898), so line 9899 and
    amount 4C are 30000.00, which is line 9946 and T1 line 14100, Return BC's.
    """
    statement: dict[str, Any] = {
        "farm": FARM,
        "farm_cca_classes_rows": (FURNITURE,),
        "farm_vehicles_rows": (VEHICLE,),
        **AREA_G,
    }
    return run(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_bx(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return BX's one T2042 statement: its lines, as the form computes them."""
    return run_bx(changes)["ca/t2042"][0]


def class_8_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 8 of Return BX with the given claim (column 21) and column 9."""
    return ("8", "10000", "5000", "0", "0", "0", claim, 0, "5000", "0", expensed)


def large_class_8_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 8 with additions of 40000, all DIEPs, and the given claim (column 21) and column 9."""
    return ("8", "10000", "40000", "0", "0", "0", claim, 0, "40000", "0", expensed)


def test_return_bxs_class_8_works_the_diep_columns_to_a_column_21_of_5200() -> None:
    # Area A, class 8: column 7 is 10000 + 5000 - 0 = 15000; column 8 is column 4 minus column 6,
    # 5000 - 0 = 5000, not more than column 7; column 9 is a chosen 3000, not more than column 8;
    # column 10 is 5000 - 3000 = 2000 and column 13 is 15000 - 3000 = 12000; columns 11, 12, 14,
    # 15, 16 and 17 are 0; column 18 is one half x (2000 - 0 - 0 - 0) = 1000.00; column 19 is
    # 12000 + 0 + 0 - 1000.00 = 11000.00; the maximum (column 19 x column 20) is 11000.00 x 20% =
    # 2200.00 and column 21 is 2200.00 + 3000 = 5200.00, the claim.
    statement = statement_bx()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "farm_cca_table_claim: item 1 class 8: column 7 15000, column 9 3000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 1000, column 19 11000, "
        "maximum 20% of column 19 = 2200 (half-up to 0.01), claim 5200"
    ) in rendered
    assert statement.get(FARM_CCA_TABLE_CLAIM).value == D("5200.00")


def test_return_bxs_line_i_is_3000_the_total_of_column_9() -> None:
    # Line i "Total immediate expensing claim for the year: Total of column 9" is 3000, within the
    # least of endnote 5's three amounts: the immediate expensing limit 750000.00, the UCC of
    # DIEPs in column 8 (5000) and the income before CCA, 35200.00.
    statement = statement_bx()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    assert isinstance(
        statement.producer_of(FARM_IMMEDIATE_EXPENSING_CLAIM), ImmediateExpensingClaim
    )
    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("750000.00")
    assert statement.get(FARM_INCOME_BEFORE_CCA).value == D("35200.00")
    assert (
        "farm_immediate_expensing_claim: item 1 class 8: column 4 5000 less column 6 0, "
        "column 7 15000: column 8 5000, column 9 3000"
    ) in rendered


def test_return_bxs_income_before_cca_is_line_9899_plus_line_9936_not_below_zero() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the form
    # names no line for it. Guide T4002 2025, "Line 9899 or 9369 - Net income (loss) before
    # adjustments": "For business and professional income, use line 9369 on Form T2125. For
    # farming income, use line 9899 on Form T2042. For fishing income, use line 9369 on Form
    # T2121." - the pairing with the line 9369 that T2125 and T2121 use, so line 9899 is the
    # figure. Line 9899 is 85200 - 55200.00 = 30000.00, after the 5200.00 of line 9936; adding it
    # back, 30000.00 + 5200.00 = 35200.00, which is the gross income 85200 less the other expenses
    # 50000 (the recapture on line 9600 is in gross income, the terminal loss on line 9790 an
    # expense, both 0 here). With no inventory adjustment amount 4C is equal to line 9899.
    statement = statement_bx()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(FARM_CCA_CLAIM).value == D("5200.00")
    assert statement.get(FARM_INCOME_BEFORE_CCA).value == D("35200.00")
    assert (
        "farm_income_before_cca: farm_net_income_before_adjustments 30000 "
        "+ farm_cca_claim 5200, not below 0 = 35200"
    ) in rendered


def test_an_inventory_adjustment_moves_amount_4c_but_not_the_income_before_cca() -> None:
    # Amount 4C is the total of lines 9899, 9941 and 9942: 30000.00 + 1000 + 500 = 31500.00. The
    # income before CCA follows line 9899 (Guide T4002 2025, "Line 9899 or 9369 - Net income
    # (loss) before adjustments": "For farming income, use line 9899 on Form T2042"), before the
    # inventory adjustments: 30000.00 + 5200.00 = 35200.00, not 31500.00 + 5200.00 = 36700.00.
    statement = statement_bx(INVENTORY_ADJUSTMENTS)
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("31500.00")
    assert statement.get(FARM_CCA_CLAIM).value == D("5200.00")
    assert statement.get(FARM_INCOME_BEFORE_CCA).value == D("35200.00")
    assert (
        "farm_income_before_cca: farm_net_income_before_adjustments 30000 "
        "+ farm_cca_claim 5200, not below 0 = 35200"
    ) in rendered


def test_with_an_inventory_adjustment_a_column_9_equal_to_line_9899_plus_line_9936_is_allowed() -> (
    None
):
    # Class 8 with additions of 40000, all DIEPs, expensed at once 35200, claim 37680.00 (column
    # 21, as in the test of a column 9 equal to the income before CCA without an adjustment): line
    # 9898 is 50000 + 37680.00 = 87680.00, line 9899 is 85200 - 87680.00 = -2480.00 and amount 4C
    # is -2480.00 + 1000 + 500 = -980.00. The income before CCA is line 9899 + line 9936 =
    # -2480.00 + 37680.00 = 35200.00, which the total of column 9 equals (the limit 750000.00 and
    # the UCC of DIEPs 40000 are not passed); amount 4C + line 9936 would be 36700.00.
    statement = statement_bx(
        {
            **INVENTORY_ADJUSTMENTS,
            "farm_cca_classes_rows": (large_class_8_row("37680.00", "35200"),),
        }
    )

    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-2480.00")
    assert statement.get(FARM_NET_INCOME_AFTER_INVENTORY_ADJUSTMENTS).value == D("-980.00")
    assert statement.get(FARM_INCOME_BEFORE_CCA).value == D("35200.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("35200")


def test_with_an_inventory_adjustment_a_column_9_above_line_9899_plus_line_9936_is_refused() -> (
    None
):
    # A column 9 of 35201 passes the limit 750000.00 and the UCC of DIEPs 40000 and is below
    # amount 4C plus line 9936, -980.90 + 37680.90 = 36700.00 (amount 4C is -2480.90 + 1500), but
    # is above line 9899 plus line 9936, -2480.90 + 37680.90 = 35200.00, the income before CCA that
    # endnote 5 names (Guide T4002 2025, "For farming income, use line 9899 on Form T2042"). The
    # claim is as in the refused column 9 of 35201 without an adjustment.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx(
            {
                **INVENTORY_ADJUSTMENTS,
                "farm_cca_classes_rows": (large_class_8_row("37680.90", "35201"),),
            }
        )

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (35201) is above the income before CCA (35200.00)"
    )


def test_return_bxs_amount_iv_is_750000_from_50_percent_of_1_5_million() -> None:
    # Endnote 5 and Area G: the farm is associated with one EPOP (1) and an agreement was filed
    # (1), so the limit is amount iv. "Immediate expensing limit allocated to your business:
    # Multiply $1.5 million by the percentage assigned to your business in column 3**": 1500000 x
    # 50% = 750000.00. The total of column 3 is 100, so 100% less it is 0, not negative, and the
    # footnote ("** If the total of column 3 is more than 100%, enter "0."") does not apply.
    # Amount iv times the 1 agreement filed is 750000.00, chosen by the 1 for associated over the
    # $1.5 million; no amount is allocated by the minister (0), so the limit is 750000.00.
    statement = statement_bx()

    assert statement.get(FARM_IMMEDIATE_EXPENSING_CAP).value == D("1500000")
    assert statement.get(FARM_EPOP_PERCENTAGE_MAXIMUM).value == D("100")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_SHARE).value == D("750000.00")
    assert statement.get(FARM_EPOP_PERCENTAGE_ROOM).value == D("0")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_ALLOCATED).value == D("750000.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT).value == D("750000.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("750000.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("750000.00")


def test_return_bxs_trace_shows_the_limit_chain() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_bx().trace)

    for line in (
        "farm_immediate_expensing_cap: credit amount 1500000 (half-up to 0.01)",
        "farm_epop_percentage_maximum: credit amount 100 (half-up to 0.01)",
        "farm_immediate_expensing_share: farm_epop_percentage 50% of "
        "farm_immediate_expensing_cap 1500000 = 750000 (half-up to 0.01)",
        "farm_epop_percentage_room: farm_epop_percentage_maximum 100 less "
        "farm_epop_percentage_total 100 = 0",
        "farm_immediate_expensing_allocated: farm_immediate_expensing_share 750000, "
        "chosen as farm_epop_percentage_room 0 is zero",
        "farm_immediate_expensing_associated_limit: farm_immediate_expensing_allocated "
        "750000 for each of 1 farm_epop_agreement_filed_checked = 750000",
        "farm_immediate_expensing_limit_before_minister: "
        "farm_immediate_expensing_associated_limit 750000, chosen as "
        "farm_epop_associated_checked is 1",
        "farm_immediate_expensing_limit_before_proration: "
        "farm_immediate_expensing_limit_before_minister 750000, chosen as "
        "farm_minister_allocation_given_checked is 0",
        "farm_immediate_expensing_limit: farm_immediate_expensing_limit_before_proration "
        "750000 = 750000, not prorated as farm_fiscal_period_days 365 is not below 357 days",
    ):
        assert line in rendered, line


def test_return_bxs_line_ii_and_line_9936_are_5200_and_line_9899_is_30000() -> None:
    # Line ii, the total of column 21, is 5200.00, so is line 9936 (no personal part of CCA, no
    # CCA for business-use-of-home expenses). Line 9898 is 50000 + 5200.00 = 55200.00 (the terminal
    # loss on line 9790 is 0) and line 9899 is 85200 - 55200.00 = 30000.00.
    statement = statement_bx()

    assert statement.get(FARM_GROSS_INCOME).value == D("85200")
    assert statement.get(FARM_GROSS_INCOME_BEFORE_EXPENSES).value == D("85200")
    assert statement.get(FARM_CCA_TABLE_CLAIM).value == D("5200.00")
    assert statement.get(FARM_CCA_CLAIM).value == D("5200.00")
    assert statement.get(FARM_TERMINAL_LOSS).value == D("0")
    assert statement.get(FARM_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("0")
    assert statement.get(FARM_TOTAL_EXPENSES).value == D("55200.00")
    assert statement.get(FARM_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")


def test_return_bxs_closing_ucc_is_9800_for_class_8() -> None:
    # Column 22 is column 7 less column 21: 15000 - 5200.00 = 9800.00 (the claim includes the 3000
    # of column 9), next year's column 2.
    statement = statement_bx()

    records = statement.get(FARM_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("8"), D("9800.00")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "farm_closing_ucc: item 1 class 8: column 7 15000 less claim 5200 "
        "(including column 9 3000) = 9800"
    ) in rendered


def test_return_bxs_net_farming_income_is_30000_on_line_9946_and_t1_line_14100() -> None:
    # Part 5: no partner (count 0), so amount 5A is amount 4C, 30000.00, and amounts 5B and 5C are
    # 30000.00. Part 7 is nil. Line 9946 is 30000.00 - 0 = 30000.00, T1 line 25 and line 14100;
    # the net self-employment income (line 27) is 0 + 0 + 0 + 30000.00 + 0.
    result = run_bx()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2042"][0].get(FARMING_INCOME).value == D("30000.00")
    assert worksheet.get(FARMING_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_bxs_figures_that_depend_on_income_are_return_bcs() -> None:
    # Line 9946 is Return BC's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BC's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_bx()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_farm_not_associated_with_an_epop_has_the_whole_1_5_million() -> None:
    # Endnote 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year": the Area G figures are left blank.
    statement = statement_bx(
        {
            "farm_epop_associated": 0,
            "farm_epop_agreement_filed": 0,
            "farm_epop_percentage": "0",
            "farm_epop_percentage_total": "0",
        }
    )

    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_area_g_percentages_with_the_associated_answer_no_leave_the_limit_at_1_5_million() -> None:
    # Area G is only filled in "If you answered yes", and endnote 5 gives $1.5 million when the
    # filer is not associated: a percentage (40) and a total of percentages (100) typed with the
    # associated answer no are not read (reading the table would give 600000).
    statement = statement_bx(
        {
            "farm_epop_associated": 0,
            "farm_epop_agreement_filed": 0,
            "farm_epop_percentage": "40",
            "farm_epop_percentage_total": "100",
        }
    )

    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_an_associated_farm_with_no_agreement_filed_has_a_limit_of_zero() -> None:
    # Endnote 5 "zero, if you are associated with one or more EPOPs and an agreement that assigns
    # a percentage to one or more of the associated EPOPs was not filed with the minister in a
    # prescribed form": the limit is 0, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm_epop_agreement_filed": 0})

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_above_100_gives_a_limit_of_zero() -> None:
    # "** If the total of column 3 is more than 100%, enter "0."": 100% less 100.01 is negative,
    # so amount iv is 0.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm_epop_percentage_total": "100.01"})

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_of_exactly_100_is_not_more_than_100() -> None:
    # 100% less 100 is 0, which is not negative: amount iv is 1500000 x 100% = 1500000.00.
    statement = statement_bx({"farm_epop_percentage": "100"})

    assert statement.get(FARM_IMMEDIATE_EXPENSING_ALLOCATED).value == D("1500000.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000.00")


def test_a_percentage_of_0_2_gives_a_limit_of_exactly_the_3000_of_column_9() -> None:
    # Amount iv is 1500000 x 0.2% = 3000.00; a total above the limit is refused, not one equal to
    # it.
    statement = statement_bx({"farm_epop_percentage": "0.2"})

    assert statement.get(FARM_IMMEDIATE_EXPENSING_ALLOCATED).value == D("3000.00")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_a_percentage_of_0_1_gives_a_limit_of_1500_so_column_9_is_refused() -> None:
    # Amount iv is 1500000 x 0.1% = 1500.00, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm_epop_percentage": "0.1"})

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(1500.00)"
    )


def test_an_amount_allocated_by_the_minister_replaces_the_limit() -> None:
    # Endnote 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": with no agreement filed the limit would be 0, but the minister's 5000 is the
    # limit; 2000 is below the 3000 of column 9.
    statement = statement_bx(
        {
            "farm_epop_agreement_filed": 0,
            "farm_minister_allocation_given": 1,
            "farm_minister_allocation": "5000",
        }
    )

    assert statement.get(FARM_IMMEDIATE_EXPENSING_LIMIT).value == D("5000")
    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx(
            {
                "farm_epop_agreement_filed": 0,
                "farm_minister_allocation_given": 1,
                "farm_minister_allocation": "2000",
            }
        )
    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(2000)"
    )


def test_a_column_9_total_equal_to_the_income_before_cca_is_allowed() -> None:
    # Class 8 with additions of 40000, all DIEPs, expensed at once 35200: the income before CCA is
    # 35200.00, which the total of column 9 equals; the limit 750000.00 and the UCC of DIEPs 40000
    # are not passed. Column 7 is 50000; column 10 is 40000 - 35200 = 4800; column 13 is 50000 -
    # 35200 = 14800; column 18 is one half x 4800 = 2400.00; column 19 is 14800 - 2400.00 =
    # 12400.00; column 21 is 12400.00 x 20% = 2480.00 + 35200 = 37680.00. The income before CCA
    # does not move with the claim (amount 4C plus line 9936 is the gross income less amount 4B).
    statement = statement_bx({"farm_cca_classes_rows": (large_class_8_row("37680.00", "35200"),)})

    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("35200")
    assert statement.get(FARM_INCOME_BEFORE_CCA).value == D("35200.00")


def test_a_column_9_total_above_the_income_before_cca_is_refused() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the income
    # before CCA is 35200.00. A column 9 of 35201 passes the limit 750000.00 and the UCC of DIEPs
    # 40000 but not the income. Column 10 is 4799; column 13 is 50000 - 35201 = 14799; column 18
    # is 2399.50; column 19 is 14799 - 2399.50 = 12399.50; column 21 is 2479.90 + 35201 =
    # 37680.90.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm_cca_classes_rows": (large_class_8_row("37680.90", "35201"),)})

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (35201) is above the income before CCA (35200.00)"
    )


def test_a_loss_before_cca_gives_an_income_before_cca_of_zero() -> None:
    # "income, if any": with no wheat the income lines are 30000, amount 4C is 30000 - 55200.00 =
    # -25200.00 and adding back the 5200.00 of line 9936 is -20000.00, so the income before CCA is
    # 0 and the 3000 of column 9 is refused.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm": {**FARM, "wheat": "0"}})

    assert str(raised.value) == (
        "ca/t2042, instance 1: total of column 9 (3000) is above the income before CCA (0)"
    )


def test_a_column_9_above_column_8_is_refused_naming_the_class() -> None:
    # Endnote 4 and endnote 5: column 8 is 5000, so a column 9 of 5001 is refused.
    with pytest.raises(InvalidRecordError) as raised:
        run_bx({"farm_cca_classes_rows": (class_8_row("5200.00", "5001"),)})

    assert (
        str(raised.value)
        == "ca/t2042, instance 1: item 1: column 9 (5001) is above column 8 (5000)"
    )


def test_a_class_8_claim_below_column_9_is_refused() -> None:
    # Column 21 includes column 9 (3000) and the claim is column 21 (T2042 has no column 22 of
    # non-compliant CCA), so the claim is at least the 3000.
    with pytest.raises(InputBelowBoundError) as raised:
        run_bx({"farm_cca_classes_rows": (class_8_row("2999.99", "3000"),)})

    assert str(raised.value) == (
        "ca/t2042, instance 1: item 1: ca/cca_claimed 2999.99 is below the minimum 3000"
    )


def test_a_class_8_claim_above_column_21_is_refused() -> None:
    # Column 21 is 2200.00 + 3000 = 5200.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bx({"farm_cca_classes_rows": (class_8_row("5200.01", "3000"),)})

    assert str(raised.value) == (
        "ca/t2042, instance 1: item 1: ca/cca_claimed 5200.01 is above the maximum 5200.00"
    )


def test_a_return_with_no_diep_has_a_line_i_of_zero() -> None:
    # Class 8 without column 4 and column 9 (a plain 10000 + 5000 of additions): line i is 0 and
    # the claim is the maximum, column 19 = 15000 - 2500.00 = 12500.00 x 20% = 2500.00.
    statement = statement_bx(
        {
            "farm_cca_classes_rows": (
                ("8", "10000", "5000", "0", "0", "0", "2500.00", 0, "0", "0", "0"),
            )
        }
    )

    assert statement.get(FARM_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(FARM_CCA_TABLE_CLAIM).value == D("2500.00")
