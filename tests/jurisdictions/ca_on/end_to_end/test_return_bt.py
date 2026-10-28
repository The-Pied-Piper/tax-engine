"""CA-ON 2025 end to end: return bt."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidRecordError,
)
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.immediate_expensing_claim import (
    ImmediateExpensingClaim,
)
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_EPOP_PERCENTAGE_MAXIMUM,
    BUSINESS_EPOP_PERCENTAGE_ROOM,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED,
    BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_CAP,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT,
    BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER,
    BUSINESS_IMMEDIATE_EXPENSING_SHARE,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_TOTAL_EXPENSES,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_END,
    FEDERAL_BASIC_TAX,
    NET_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return BT's T2125, Return BB's with the gross sales raised by 3200 to 53200 (a chosen figure,
# so that line 9946 stays Return BB's 30000): the six expense lines 1500 + 1200 + 800 + 2500 +
# 6000 + 1500 = 13500 and the motor vehicle expenses of 2500 from Charts A to C (the seven lines
# 16000), and the business-use-of-home expenses 600 + 500 + 300 + 200 + 400 = 2000.
BUSINESS = {
    "gross_sales": "53200",
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
# Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
# property left, column 4, column 6, column 9): class 8 with a UCC of 10000 and additions of 5000,
# all DIEPs (column 4 5000), of which 3000 is expensed at once (column 9): column 21 is 11000.00 x
# 20% = 2200.00 plus 3000, so 5200.00, claimed in full.
FURNITURE = ("8", "10000", "5000", "0", "0", "0", "5200.00", 0, "5000", "0", "3000")
# Charts A to C for one leased passenger vehicle used half for business: Chart A line 16 (line
# 9281) is 2500, from the interest of Chart B (400) and the leasing cost of Chart C (2147), as in
# Return BB.
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
# Area G and endnote 5: associated with one other EPOP (1) under an agreement that was filed (1),
# the percentage assigned to your business 40 and the total of column 3 100, so amount iii is
# 1500000 x 40% = 600000.00; no amount allocated by the minister.
AREA_G = {
    "business_epop_associated": 1,
    "business_epop_agreement_filed": 1,
    "business_epop_percentage": "40",
    "business_epop_percentage_total": "100",
}


def run_bt(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return BT's inputs, as in `returns/2025_return_bt.yaml`: Return BB's sole proprietor with
    one DIEP expensed at once and Area G.

    One T2125 statement for the business: gross sales of 53200 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 16000 on seven lines (the motor vehicle line, 2500, from Charts A to
    C) and 5200.00 of capital cost allowance (Class 8, opening UCC 10000, additions 5000, all
    DIEPs, 3000 expensed at once, claim 5200.00), 21200.00 in all (line 9368), so line 9369 is
    32000.00; business-use-of-home expenses of 2000, so line 9945 is 2000 and line 9946 and T1 line
    13500 are 30000.00, Return BB's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (FURNITURE,),
        "business_vehicles_rows": (VEHICLE,),
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
        business_statements=({**statement, **(changes or {})},),
        **overrides,
    )


def statement_bt(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return BT's one T2125 statement: its lines, as the form computes them."""
    return run_bt(changes)["ca/t2125"][0]


def class_8_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 8 of Return BT with the given claim (column 21) and column 9."""
    return ("8", "10000", "5000", "0", "0", "0", claim, 0, "5000", "0", expensed)


def large_class_8_row(
    claim: str, expensed: str
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Class 8 with additions of 40000, all DIEPs, and the given claim (column 21) and column 9."""
    return ("8", "10000", "40000", "0", "0", "0", claim, 0, "40000", "0", expensed)


def test_return_bts_class_8_works_the_diep_columns_to_a_column_21_of_5200() -> None:
    # Area A, class 8: column 7 is 10000 + 5000 - 0 = 15000; column 8 is column 4 minus column 6,
    # 5000 - 0 = 5000, not more than column 7; column 9 is a chosen 3000, not more than column 8;
    # column 10 is 5000 - 3000 = 2000 and column 13 is 15000 - 3000 = 12000; columns 11, 12, 14,
    # 15, 16 and 17 are 0; column 18 is one half x (2000 - 0 - 0 - 0) = 1000.00; column 19 is
    # 12000 + 0 + 0 - 1000.00 = 11000.00; the maximum (column 19 x column 20) is 11000.00 x 20% =
    # 2200.00 and column 21 is 2200.00 + 3000 = 5200.00, the claim.
    statement = statement_bt()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "business_cca_table_claim: item 1 class 8: column 7 15000, column 9 3000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 1000, column 19 11000, "
        "maximum 20% of column 19 = 2200 (half-up to 0.01), claim 5200"
    ) in rendered
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("5200.00")


def test_return_bts_line_i_is_3000_the_total_of_column_9() -> None:
    # Line i "Total immediate expensing claim for the year: Total of column 9" is 3000, within the
    # least of endnote 5's three amounts: the immediate expensing limit 600000.00, the UCC of
    # DIEPs in column 8 (5000) and the income before CCA, 37200.00.
    statement = statement_bt()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    assert isinstance(
        statement.producer_of(BUSINESS_IMMEDIATE_EXPENSING_CLAIM), ImmediateExpensingClaim
    )
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("37200.00")
    assert (
        "business_immediate_expensing_claim: item 1 class 8: column 4 5000 less column 6 0, "
        "column 7 15000: column 8 5000, column 9 3000"
    ) in rendered


def test_return_bts_income_before_cca_is_line_9369_plus_line_9936_not_below_zero() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": line 9369
    # is 53200 - 21200.00 = 32000.00, which is after the 5200.00 of line 9936; adding it back,
    # 32000.00 + 5200.00 = 37200.00, which is the gross profit 53200 less the other expenses
    # 16000 (the recapture on line 8230 is in gross income, the terminal loss on line 9270 an
    # expense, both 0 here).
    statement = statement_bt()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000.00")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("5200.00")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("37200.00")
    assert (
        "business_income_before_cca: business_net_income_before_adjustments 32000 "
        "+ business_cca_claim 5200, not below 0 = 37200"
    ) in rendered


def test_return_bts_amount_iii_is_600000_from_40_percent_of_1_5_million() -> None:
    # Endnote 5 and Area G: the business is associated with one EPOP (1) and an agreement was
    # filed (1), so the limit is amount iii. "Immediate expensing limit allocated to your business:
    # Multiply $1.5 million by the percentage assigned to your business in column 3**": 1500000 x
    # 40% = 600000.00. The total of column 3 is 100, so 100% less it is 0, not negative, and the
    # footnote ("** If the total of column 3 is more than 100%, enter "0."") does not apply.
    # Amount iii times the 1 agreement filed is 600000.00, chosen by the 1 for associated over the
    # $1.5 million; no amount is allocated by the minister (0), so the limit is 600000.00.
    statement = statement_bt()

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CAP).value == D("1500000")
    assert statement.get(BUSINESS_EPOP_PERCENTAGE_MAXIMUM).value == D("100")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_SHARE).value == D("600000.00")
    assert statement.get(BUSINESS_EPOP_PERCENTAGE_ROOM).value == D("0")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED).value == D("600000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_ASSOCIATED_LIMIT).value == D("600000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT_BEFORE_MINISTER).value == D("600000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("600000.00")


def test_return_bts_trace_shows_the_limit_chain() -> None:
    rendered = EnglishTraceRenderer().render_all(statement_bt().trace)

    for line in (
        "business_immediate_expensing_cap: credit amount 1500000 (half-up to 0.01)",
        "business_epop_percentage_maximum: credit amount 100 (half-up to 0.01)",
        "business_immediate_expensing_share: business_epop_percentage 40% of "
        "business_immediate_expensing_cap 1500000 = 600000 (half-up to 0.01)",
        "business_epop_percentage_room: business_epop_percentage_maximum 100 less "
        "business_epop_percentage_total 100 = 0",
        "business_immediate_expensing_allocated: business_immediate_expensing_share 600000, "
        "chosen as business_epop_percentage_room 0 is zero",
        "business_immediate_expensing_associated_limit: business_immediate_expensing_allocated "
        "600000 for each of 1 business_epop_agreement_filed_checked = 600000",
        "business_immediate_expensing_limit_before_minister: "
        "business_immediate_expensing_associated_limit 600000, chosen as "
        "business_epop_associated_checked is 1",
        "business_immediate_expensing_limit_before_proration: "
        "business_immediate_expensing_limit_before_minister 600000, chosen as "
        "business_minister_allocation_given_checked is 0",
        "business_immediate_expensing_limit: business_immediate_expensing_limit_before_proration "
        "600000 = 600000, not prorated as business_fiscal_period_days 365 is not below 357 days",
    ):
        assert line in rendered, line


def test_return_bts_line_ii_and_line_9936_are_5200_and_line_9369_is_32000() -> None:
    # Line ii, the total of column 21, is 5200.00, so is line 9936 (no personal part of CCA, no
    # CCA for business-use-of-home expenses). Line 9368 is 16000 + 5200.00 + 0 = 21200.00 and line
    # 9369 is 53200 - 21200.00 = 32000.00.
    statement = statement_bt()

    assert statement.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("53200")
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("5200.00")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("5200.00")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("21200.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("32000.00")


def test_return_bts_closing_ucc_is_9800_for_class_8() -> None:
    # Column 22 is column 7 less column 21: 15000 - 5200.00 = 9800.00 (the claim includes the 3000
    # of column 9), next year's column 2.
    statement = statement_bt()

    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("8"), D("9800.00")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "business_closing_ucc: item 1 class 8: column 7 15000 less claim 5200 "
        "(including column 9 3000) = 9800"
    ) in rendered


def test_return_bts_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Part 7: the business-use-of-home expenses are 2000 (amount 7P, line 9945), the lesser of
    # 2000 and amount 5D, 32000.00. Line 9946 is 32000.00 - 2000 = 30000.00, T1 line 22 and line
    # 13500; the net self-employment income (line 27) is 30000.00 + 0 + 0 + 0 + 0.
    result = run_bt()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_bts_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BB's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_bt()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_business_not_associated_with_an_epop_has_the_whole_1_5_million() -> None:
    # Endnote 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year": the Area G answers are not read, so the 40 and the
    # total of 150 (more than 100%) change nothing.
    statement = statement_bt(
        {
            "business_epop_associated": 0,
            "business_epop_agreement_filed": 0,
            "business_epop_percentage": "40",
            "business_epop_percentage_total": "150",
        }
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_an_associated_business_with_no_agreement_filed_has_a_limit_of_zero() -> None:
    # Endnote 5 "zero, if you are associated with one or more EPOPs and an agreement that assigns
    # a percentage to one or more of the associated EPOPs was not filed with the minister in a
    # prescribed form": the limit is 0, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business_epop_agreement_filed": 0})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_above_100_gives_a_limit_of_zero() -> None:
    # "** If the total of column 3 is more than 100%, enter "0."": 100% less 100.01 is negative,
    # so amount iii is 0.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business_epop_percentage_total": "100.01"})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (3000) is above the immediate expensing limit (0)"
    )


def test_a_total_of_column_3_of_exactly_100_is_not_more_than_100() -> None:
    # 100% less 100 is 0, which is not negative: amount iii is 1500000 x 100% = 1500000.00.
    statement = statement_bt({"business_epop_percentage": "100"})

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED).value == D("1500000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("1500000.00")


def test_a_percentage_of_0_2_gives_a_limit_of_exactly_the_3000_of_column_9() -> None:
    # Amount iii is 1500000 x 0.2% = 3000.00; a total above the limit is refused, not one equal to
    # it.
    statement = statement_bt({"business_epop_percentage": "0.2"})

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_ALLOCATED).value == D("3000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")


def test_a_percentage_of_0_1_gives_a_limit_of_1500_so_column_9_is_refused() -> None:
    # Amount iii is 1500000 x 0.1% = 1500.00, below the 3000 of column 9.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business_epop_percentage": "0.1"})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(1500.00)"
    )


def test_an_amount_allocated_by_the_minister_replaces_the_limit() -> None:
    # Endnote 5 "any amount allocated by the minister under subsection 1104(3.4) of the
    # Regulations": with no agreement filed the limit would be 0, but the minister's 5000 is the
    # limit; 2000 is below the 3000 of column 9.
    statement = statement_bt(
        {
            "business_epop_agreement_filed": 0,
            "business_minister_allocation_given": 1,
            "business_minister_allocation": "5000",
        }
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_LIMIT).value == D("5000")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("3000")
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt(
            {
                "business_epop_agreement_filed": 0,
                "business_minister_allocation_given": 1,
                "business_minister_allocation": "2000",
            }
        )
    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (3000) is above the immediate expensing limit "
        "(2000)"
    )


def test_a_column_9_total_equal_to_the_income_before_cca_is_allowed() -> None:
    # Class 8 with additions of 40000, all DIEPs, expensed at once 37200: the income before CCA is
    # 37200.00, which the total of column 9 equals; the limit 600000.00 and the UCC of DIEPs 40000
    # are not passed. Column 7 is 50000; column 10 is 40000 - 37200 = 2800; column 13 is 50000 -
    # 37200 = 12800; column 18 is one half x 2800 = 1400.00; column 19 is 12800 - 1400.00 =
    # 11400.00; column 21 is 11400.00 x 20% = 2280.00 + 37200 = 39480.00.
    statement = statement_bt(
        {"business_cca_classes_rows": (large_class_8_row("39480.00", "37200"),)}
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("37200")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("37200.00")


def test_a_column_9_total_above_the_income_before_cca_is_refused() -> None:
    # Endnote 5 "the amount of income, if any, earned from the source of income that is a business
    # (before any CCA deductions) in which the relevant DIEP is used for the tax year": the income
    # before CCA is 37200.00 (it does not change with the claim, which line 9369 deducts and this
    # adds back). A column 9 of 37201 passes the limit 600000.00 and the UCC of DIEPs 40000 but not
    # the income. Column 10 is 2799; column 13 is 50000 - 37201 = 12799; column 18 is 1399.50;
    # column 19 is 12799 - 1399.50 = 11399.50; column 21 is 2279.90 + 37201 = 39480.90.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business_cca_classes_rows": (large_class_8_row("39480.90", "37201"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (37201) is above the income before CCA (37200.00)"
    )


def test_a_loss_before_cca_gives_an_income_before_cca_of_zero() -> None:
    # "income, if any": with gross sales of 10000 line 9369 is 10000 - 21200.00 = -11200.00 and
    # adding back the 5200.00 of line 9936 is -6000.00, so the income before CCA is 0 and the
    # 3000 of column 9 is refused.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business": {**BUSINESS, "gross_sales": "10000"}})

    assert str(raised.value) == (
        "ca/t2125, instance 1: total of column 9 (3000) is above the income before CCA (0)"
    )


def test_a_column_9_above_column_8_is_refused_naming_the_class() -> None:
    # Endnote 4 and endnote 5: column 8 is 5000, so a column 9 of 5001 is refused.
    with pytest.raises(InvalidRecordError) as raised:
        run_bt({"business_cca_classes_rows": (class_8_row("5200.00", "5001"),)})

    assert (
        str(raised.value)
        == "ca/t2125, instance 1: item 1: column 9 (5001) is above column 8 (5000)"
    )


def test_a_class_8_claim_below_column_9_is_refused() -> None:
    # Column 21 includes column 9 (3000) and the claim is column 21 (T2125 has no column 22 of
    # non-compliant CCA), so the claim is at least the 3000.
    with pytest.raises(InputBelowBoundError) as raised:
        run_bt({"business_cca_classes_rows": (class_8_row("2999.99", "3000"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 2999.99 is below the minimum 3000"
    )


def test_a_class_8_claim_above_column_21_is_refused() -> None:
    # Column 21 is 2200.00 + 3000 = 5200.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bt({"business_cca_classes_rows": (class_8_row("5200.01", "3000"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 5200.01 is above the maximum 5200.00"
    )


def test_a_return_with_no_diep_has_a_line_i_of_zero() -> None:
    # Class 8 without column 4 and column 9 (a plain 10000 + 5000 of additions): line i is 0 and
    # the claim is the maximum, column 19 = 15000 - 2500.00 = 12500.00 x 20% = 2500.00.
    statement = statement_bt(
        {
            "business_cca_classes_rows": (
                ("8", "10000", "5000", "0", "0", "0", "2500.00", 0, "0", "0", "0"),
            )
        }
    )

    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2500.00")


# --- the yes or no answers and the percentage are checked before the limit ---------------
#
# The endnote 5 answers are yes or no, taken as a count of 0 or 1: a 2 is refused, naming the kind
# (`ca/yes_or_no_count`). A percentage assigned to the business above the total of column 3 is
# not refused: no printed bound applies to it.


@pytest.mark.parametrize(
    "changes",
    [
        {"business_epop_associated": 2},
        {"business_epop_agreement_filed": 2},
        {"business_minister_allocation_given": 2, "business_minister_allocation": "5000"},
    ],
    ids=["associated", "agreement_filed", "minister_allocation_given"],
)
def test_a_yes_or_no_answer_of_2_is_refused_naming_its_kind(changes: Mapping[str, Any]) -> None:
    (kind,) = [key for key in changes if key != "business_minister_allocation"]

    with pytest.raises(InputAboveBoundError, match=rf"ca/{kind} 2 "):
        run_bt(changes)


def test_a_business_percentage_above_column_3_total_is_not_refused() -> None:
    # Column 3 is 150% of the 100% total, and no printed bound applies: the percentage of 150 gives
    # 150% of 1500000 = 2250000 as the share, and the room of 100 less 100 is 0 as printed.
    statement = run_bt({"business_epop_percentage": "150"})["ca/t2125"][0]

    assert statement.get(BUSINESS_EPOP_PERCENTAGE_ROOM).value == D("0")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_SHARE).value == D("2250000.00")
