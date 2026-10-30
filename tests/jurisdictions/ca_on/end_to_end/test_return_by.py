"""CA-ON 2025 end to end: return by."""

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
    FEDERAL_BASIC_TAX,
    FISH_CCA_CLAIM,
    FISH_CCA_TABLE_CLAIM,
    FISH_CLOSING_UCC,
    FISH_EPOP_PERCENTAGE_MAXIMUM,
    FISH_EPOP_PERCENTAGE_ROOM,
    FISH_EXPENSES_SUBTOTAL,
    FISH_GROSS_INCOME,
    FISH_GROSS_INCOME_BEFORE_EXPENSES,
    FISH_IMMEDIATE_EXPENSING_ALLOCATED,
    FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    FISH_IMMEDIATE_EXPENSING_CAP,
    FISH_IMMEDIATE_EXPENSING_CLAIM,
    FISH_IMMEDIATE_EXPENSING_LIMIT,
    FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    FISH_IMMEDIATE_EXPENSING_SHARE,
    FISH_INCOME_BEFORE_CCA,
    FISH_NET_INCOME_AFTER_ADJUSTMENTS,
    FISH_NET_INCOME_BEFORE_ADJUSTMENTS,
    FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS,
    FISH_TERMINAL_LOSS,
    FISH_TOTAL_EXPENSES,
    FISHING_INCOME,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BY's T2121, Return BD's with the fish products raised by 9150 to 49150 (a chosen figure,
# so that line 9946 stays Return BD's 15000): income of 49150 (fish products, amount 3A) and
# expenses of 25000 (salt, bait and ice 10000 on line 9138, fishing gear 15000 on line 9136), with
# no partner or business-use-of-home amounts.
FISH = {
    "fish_products": "49150",
    "salt_bait_and_ice": "10000",
    "fishing_gear": "15000",
    # Charts A to C for one leased passenger vehicle that is used for no fishing: business
    # kilometres 0 (amount 1), so line 9281 (amount 16 of Chart A) is 0, as in Return BD.
    "vehicle_sales_tax_rate": "13",
}
# Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9): class 7 with a UCC of 20000 and additions of 8000,
# all DIEPs (column 4 8000), of which 6000 is expensed at once (column 9): column 21 is 21000.00 x
# 15% = 3150.00 plus 6000, so 9150.00, claimed in full.
BOAT = ("7", "20000", "8000", "0", "0", "0", "9150.00", 0, "8000", "0", "6000")
# Charts A to C for one leased passenger vehicle used for no fishing, as in Return BD.
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
# the percentage assigned to your business 40 and the total of column 3 100, so amount iii is
# 1500000 x 40% = 600000.00; no amount allocated by the minister.
AREA_G = {
    "fish_epop_associated": 1,
    "fish_epop_agreement_filed": 1,
    "fish_epop_percentage": "40",
    "fish_epop_percentage_total": "100",
}


def run_by(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return BY's inputs, as in `returns/2025_return_by.yaml`: Return BD's sole proprietor with
    one DIEP expensed at once and Area G.

    One T2121 statement for the fishing business: income of 49150 (line 8299 and T1 line 14299),
    expenses of 25000 (4Q) and 9150.00 of capital cost allowance (Class 7, opening UCC 20000,
    additions 8000, all DIEPs, 6000 expensed at once, claim 9150.00), 34150.00 in all (line 9368),
    so line 9369 is 15000.00, which is line 9946 and T1 line 14300, Return BD's.
    """
    statement: dict[str, Any] = {
        "fish": FISH,
        "fish_cca_classes_rows": (BOAT,),
        "fish_vehicles_rows": (VEHICLE,),
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
        fish_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_by(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return BY's one T2121 statement: its lines, as the form computes them."""
    return run_by(changes)["ca/t2121"][0]


def class_7_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 7 of Return BY with the given claim (column 21) and column 9."""
    return ("7", "20000", "8000", "0", "0", "0", claim, 0, "8000", "0", expensed)


def large_class_7_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 7 with additions of 30000, all DIEPs, and the given claim (column 21) and column 9."""
    return ("7", "20000", "30000", "0", "0", "0", claim, 0, "30000", "0", expensed)


def test_return_bys_class_7_works_the_diep_columns_to_a_column_21_of_9150() -> None:
    # Area A, class 7: column 7 is 20000 + 8000 - 0 = 28000; column 8 is column 4 minus column 6,
    # 8000 - 0 = 8000, not more than column 7; column 9 is a chosen 6000, not more than column 8;
    # column 10 is 8000 - 6000 = 2000 and column 13 is 28000 - 6000 = 22000; columns 11, 12, 14,
    # 15, 16 and 17 are 0; column 18 is one half x (2000 - 0 - 0 - 0) = 1000.00; column 19 is
    # 22000 + 0 + 0 - 1000.00 = 21000.00; the maximum (column 19 x column 20) is 21000.00 x 15% =
    # 3150.00 and column 21 is 3150.00 + 6000 = 9150.00, the claim.
    statement = statement_by()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "fish_cca_table_claim: item 1 class 7: column 7 28000, column 9 6000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 1000, column 19 21000, "
        "maximum 15% of column 19 = 3150 (half-up to 0.01), claim 9150"
    ) in rendered
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("9150.00")


def test_return_bys_line_i_is_6000_the_total_of_column_9() -> None:
    # Line i "Total immediate expensing claim for the year: Total of column 9" is 6000, within the
    # least of endnote 5's three amounts: the immediate expensing limit 600000.00, the UCC of
    # DIEPs in column 8 (8000) and the income before CCA, 24150.00.
    statement = statement_by()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("6000")
    assert isinstance(
        statement.producer_of(FISH_IMMEDIATE_EXPENSING_CLAIM), ImmediateExpensingClaim
    )
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")
    assert statement.get(FISH_INCOME_BEFORE_CCA).value == D("24150.00")
    assert (
        "fish_immediate_expensing_claim: item 1 class 7: column 4 8000 less column 6 0, "
        "column 7 28000: column 8 8000, column 9 6000"
    ) in rendered


def test_return_bys_income_before_cca_is_line_9369_plus_line_9936_not_below_zero() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the form
    # names no line for it; Guide T4002 (page 61) names line 9369 as the "Net income (loss) before
    # adjustments" of Form T2121. Line 9369 is 49150 - 34150.00 = 15000.00, which is after the
    # 9150.00 of line 9936; adding it back, 15000.00 + 9150.00 = 24150.00, which is the gross income
    # 49150 less the other expenses 25000 (the recapture on line 9600 is in gross income, the
    # terminal loss on line 9270 an expense, both 0 here).
    statement = statement_by()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("15000.00")
    assert statement.get(FISH_CCA_CLAIM).value == D("9150.00")
    assert statement.get(FISH_INCOME_BEFORE_CCA).value == D("24150.00")
    assert (
        "fish_income_before_cca: fish_net_income_before_boat_limit 15000 "
        "+ fish_cca_claim 9150, not below 0 = 24150"
    ) in rendered


def test_return_bys_amount_iii_is_600000_from_40_percent_of_1_5_million() -> None:
    # Endnote 5 and Area G: the fishing business is associated with one EPOP (1) and an agreement
    # was filed (1), so the limit is amount iii. "Immediate expensing limit allocated to your
    # business: Multiply $1.5 million by the percentage assigned to your business in column 3**":
    # 1500000 x 40% = 600000.00. The total of column 3 is 100, so 100% less it is 0, not negative,
    # and the footnote ("** If the total of column 3 is more than 100%, enter "0."") does not
    # apply. Amount iii times the 1 agreement filed is 600000.00, chosen by the 1 for associated
    # over the $1.5 million; no amount is allocated by the minister (0), so the limit is
    # 600000.00.
    statement = statement_by()

    assert statement.get(FISH_IMMEDIATE_EXPENSING_CAP).value == D("1500000")
    assert statement.get(FISH_EPOP_PERCENTAGE_MAXIMUM).value == D("100")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_SHARE).value == D("600000.00")
    assert statement.get(FISH_EPOP_PERCENTAGE_ROOM).value == D("0")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_ALLOCATED).value == D("600000.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT).value == D("600000.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("600000.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")


def test_return_bys_trace_shows_the_limit_chain() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_by().trace)

    for line in (
        "fish_immediate_expensing_cap: credit amount 1500000 (half-up to 0.01)",
        "fish_epop_percentage_maximum: credit amount 100 (half-up to 0.01)",
        "fish_immediate_expensing_share: fish_epop_percentage 40% of "
        "fish_immediate_expensing_cap 1500000 = 600000 (half-up to 0.01)",
        "fish_epop_percentage_room: fish_epop_percentage_maximum 100 less "
        "fish_epop_percentage_total 100 = 0",
        "fish_immediate_expensing_allocated: fish_immediate_expensing_share 600000, "
        "chosen as fish_epop_percentage_room 0 is zero",
        "fish_immediate_expensing_associated_limit: fish_immediate_expensing_allocated "
        "600000 for each of 1 fish_epop_agreement_filed_checked = 600000",
        "fish_immediate_expensing_limit_before_minister: "
        "fish_immediate_expensing_associated_limit 600000, chosen as "
        "fish_epop_associated_checked is 1",
        "fish_immediate_expensing_limit_before_proration: "
        "fish_immediate_expensing_limit_before_minister 600000, chosen as "
        "fish_minister_allocation_given_checked is 0",
        "fish_immediate_expensing_limit: fish_immediate_expensing_limit_before_proration "
        "600000 = 600000, not prorated as fish_fiscal_period_days 365 is not below 357 days",
    ):
        assert line in rendered, line


def test_return_bys_line_ii_and_line_9936_are_9150_and_line_9369_is_15000() -> None:
    # Line ii, the total of column 21, is 9150.00, so is line 9936 (no personal part of CCA, no
    # CCA for business-use-of-home expenses). Line 9368 is 25000 + 9150.00 = 34150.00 (the terminal
    # loss on line 9270 is 0) and line 9369 is 49150 - 34150.00 = 15000.00.
    statement = statement_by()

    assert statement.get(FISH_GROSS_INCOME).value == D("49150")
    assert statement.get(FISH_GROSS_INCOME_BEFORE_EXPENSES).value == D("49150")
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("9150.00")
    assert statement.get(FISH_CCA_CLAIM).value == D("9150.00")
    assert statement.get(FISH_TERMINAL_LOSS).value == D("0")
    assert statement.get(FISH_OTHER_EXPENSES_WITH_TERMINAL_LOSS).value == D("0")
    assert statement.get(FISH_EXPENSES_SUBTOTAL).value == D("25000")
    assert statement.get(FISH_TOTAL_EXPENSES).value == D("34150.00")
    assert statement.get(FISH_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("15000.00")


def test_return_bys_closing_ucc_is_18850_for_class_7() -> None:
    # Column 22 is column 7 less column 21: 28000 - 9150.00 = 18850.00 (the claim includes the 6000
    # of column 9), next year's column 2.
    statement = statement_by()

    records = statement.get(FISH_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("7"), D("18850.00")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "fish_closing_ucc: item 1 class 7: column 7 28000 less claim 9150 "
        "(including column 9 6000) = 18850"
    ) in rendered


def test_return_bys_net_fishing_income_is_15000_on_line_9946_and_t1_line_14300() -> None:
    # Part 5: no partner (count 0), so amount 5A is line 9369, 15000.00, and amounts 5B and 5C are
    # 15000.00. Part 7 is nil. Line 9946 is 15000.00 - 0 = 15000.00, T1 line 26 and line 14300;
    # the net self-employment income (line 27) is 0 + 0 + 0 + 0 + 15000.00.
    result = run_by()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2121"][0].get(FISH_NET_INCOME_AFTER_ADJUSTMENTS).value == D("15000.00")
    assert result["ca/t2121"][0].get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(FISHING_INCOME).value == D("15000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("15000.00")


def test_return_bys_figures_that_depend_on_income_are_return_bds() -> None:
    # Line 9946 is Return BD's 15000.00, so total income, net income and taxable income are
    # 15000.00 and the tax lines are Return BD's: the federal basic tax 15000.00 x 14.5% =
    # 2175.00, the Ontario basic tax 15000.00 x 5.05% = 757.50, and no balance owing.
    worksheet = run_by()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("15000.00")
    assert worksheet.get(NET_INCOME).value == D("15000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("15000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("2175.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("757.50")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0.00")
    # The Canada workers benefit of 1633.00 (27% of the working income over 3000.00 is capped
    # at 1633.00, and the adjusted family net income is under 26855.00) is a refund: the
    # total payable of 0.00 less 1633.00 is -1633.00.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1633.00")


def test_a_fishing_business_not_associated_with_an_epop_has_the_whole_1_5_million() -> None:
    # Endnote 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year": the Area G figures are left blank.
    statement = statement_by(
        {
            "fish_epop_associated": 0,
            "fish_epop_agreement_filed": 0,
            "fish_epop_percentage": "0",
            "fish_epop_percentage_total": "0",
        }
    )

    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("6000")


def test_area_g_percentages_with_the_associated_answer_no_leave_the_limit_at_1_5_million() -> None:
    # Area G is only filled in "If you answered yes", and endnote 5 gives $1.5 million when the
    # filer is not associated: a percentage (40) and a total of percentages (150) typed with the
    # associated answer no are not read.
    statement = statement_by(
        {
            "fish_epop_associated": 0,
            "fish_epop_agreement_filed": 0,
            "fish_epop_percentage": "40",
            "fish_epop_percentage_total": "150",
        }
    )

    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("6000")


def test_an_associated_fishing_business_with_no_agreement_filed_has_a_limit_of_zero() -> None:
    # Endnote 5 "zero, if you are associated with one or more EPOPs and an agreement that assigns
    # a percentage to one or more of the associated EPOPs was not filed with the minister in a
    # prescribed form": the limit is 0, below the 6000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish_epop_agreement_filed": 0})

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (6000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_above_100_gives_a_limit_of_zero() -> None:
    # "** If the total of column 3 is more than 100%, enter "0."": 100% less 100.01 is negative,
    # so amount iii is 0.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish_epop_percentage_total": "100.01"})

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (6000) is above the immediate expensing limit (0)"
    )


def test_a_percentage_of_exactly_100_is_not_more_than_100() -> None:
    # 100% less 100 is 0, which is not negative: amount iii is 1500000 x 100% = 1500000.00.
    statement = statement_by({"fish_epop_percentage": "100"})

    assert statement.get(FISH_IMMEDIATE_EXPENSING_ALLOCATED).value == D("1500000.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000.00")


def test_a_percentage_of_0_4_gives_a_limit_of_exactly_the_6000_of_column_9() -> None:
    # Amount iii is 1500000 x 0.4% = 6000.00; a total above the limit is refused, not one equal to
    # it.
    statement = statement_by({"fish_epop_percentage": "0.4"})

    assert statement.get(FISH_IMMEDIATE_EXPENSING_ALLOCATED).value == D("6000.00")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("6000")


def test_a_percentage_of_0_3_gives_a_limit_of_4500_so_column_9_is_refused() -> None:
    # Amount iii is 1500000 x 0.3% = 4500.00, below the 6000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish_epop_percentage": "0.3"})

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (6000) is above the immediate expensing limit "
        "(4500.00)"
    )


def test_an_amount_allocated_by_the_minister_replaces_the_limit() -> None:
    # Endnote 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": with no agreement filed the limit would be 0, but the minister's 9000 is the
    # limit; 5000 is below the 6000 of column 9.
    statement = statement_by(
        {
            "fish_epop_agreement_filed": 0,
            "fish_minister_allocation_given": 1,
            "fish_minister_allocation": "9000",
        }
    )

    assert statement.get(FISH_IMMEDIATE_EXPENSING_LIMIT).value == D("9000")
    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("6000")
    with pytest.raises(InputAboveBoundError) as raised:
        run_by(
            {
                "fish_epop_agreement_filed": 0,
                "fish_minister_allocation_given": 1,
                "fish_minister_allocation": "5000",
            }
        )
    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (6000) is above the immediate expensing limit "
        "(5000)"
    )


def test_a_column_9_total_equal_to_the_income_before_cca_is_allowed() -> None:
    # Class 7 with additions of 30000, all DIEPs, expensed at once 24150: the income before CCA is
    # 24150.00, which the total of column 9 equals; the limit 600000.00 and the UCC of DIEPs 30000
    # are not passed. Column 7 is 50000; column 10 is 30000 - 24150 = 5850; column 13 is 50000 -
    # 24150 = 25850; column 18 is one half x 5850 = 2925.00; column 19 is 25850 - 2925.00 =
    # 22925.00; column 21 is 22925.00 x 15% = 3438.75 + 24150 = 27588.75. The income before CCA
    # does not move with the claim (line 9369 plus line 9936 is the gross income less amount 4Q).
    statement = statement_by({"fish_cca_classes_rows": (large_class_7_row("27588.75", "24150"),)})

    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("24150")
    assert statement.get(FISH_INCOME_BEFORE_CCA).value == D("24150.00")


def test_a_column_9_total_above_the_income_before_cca_is_refused() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the income
    # before CCA is 24150.00. A column 9 of 24152 passes the limit 600000.00 and the UCC of DIEPs
    # 30000 but not the income. Column 10 is 5848; column 13 is 50000 - 24152 = 25848; column 18
    # is 2924.00; column 19 is 25848 - 2924.00 = 22924.00; column 21 is 3438.60 + 24152 =
    # 27590.60.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish_cca_classes_rows": (large_class_7_row("27590.60", "24152"),)})

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (24152) is above the income before CCA (24150.00)"
    )


def test_a_loss_before_cca_gives_an_income_before_cca_of_zero() -> None:
    # "income, if any": with no fish products the income is 0, line 9369 is 0 - 34150.00 =
    # -34150.00 and adding back the 9150.00 of line 9936 is -25000.00, so the income before CCA is
    # 0 and the 6000 of column 9 is refused.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish": {**FISH, "fish_products": "0"}})

    assert str(raised.value) == (
        "ca/t2121, instance 1: total of column 9 (6000) is above the income before CCA (0)"
    )


def test_a_column_9_above_column_8_is_refused_naming_the_class() -> None:
    # Endnote 4 and endnote 5: column 8 is 8000, so a column 9 of 8001 is refused.
    with pytest.raises(InvalidRecordError) as raised:
        run_by({"fish_cca_classes_rows": (class_7_row("9150.00", "8001"),)})

    assert (
        str(raised.value)
        == "ca/t2121, instance 1: item 1: column 9 (8001) is above column 8 (8000)"
    )


def test_a_class_7_claim_below_column_9_is_refused() -> None:
    # Column 21 includes column 9 (6000), so the claim is at least the 6000.
    with pytest.raises(InputBelowBoundError) as raised:
        run_by({"fish_cca_classes_rows": (class_7_row("5999.99", "6000"),)})

    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: ca/cca_claimed 5999.99 is below the minimum 6000"
    )


def test_a_class_7_claim_above_column_21_is_refused() -> None:
    # Column 21 is 3150.00 + 6000 = 9150.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_by({"fish_cca_classes_rows": (class_7_row("9150.01", "6000"),)})

    assert str(raised.value) == (
        "ca/t2121, instance 1: item 1: ca/cca_claimed 9150.01 is above the maximum 9150.00"
    )


def test_a_return_with_no_diep_has_a_line_i_of_zero() -> None:
    # Class 7 without column 4 and column 9 (a plain 20000 + 8000 of additions): line i is 0 and
    # the claim is the maximum, column 19 = 28000 - 4000.00 = 24000.00 x 15% = 3600.00.
    statement = statement_by(
        {
            "fish_cca_classes_rows": (
                ("7", "20000", "8000", "0", "0", "0", "3600.00", 0, "0", "0", "0"),
            )
        }
    )

    assert statement.get(FISH_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(FISH_CCA_TABLE_CLAIM).value == D("3600.00")
