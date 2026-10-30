"""CA-ON 2025 end to end: return cd."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_IMMEDIATE_EXPENSING_CLAIM,
    BUSINESS_INCOME,
    BUSINESS_INCOME_BEFORE_CCA,
    BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS,
    BUSINESS_RECAPTURED_CCA,
    BUSINESS_TERMINAL_LOSS,
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
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# Return CD's T2125: gross sales of 40000 (a chosen figure) and the three expense lines 1500 +
# 1200 + 4300 = 7000, with no motor vehicle (no Charts A to C) and no business-use-of-home
# expenses.
BUSINESS = {
    "gross_sales": "40000",
    "advertising": "1500",
    "insurance": "1200",
    "rent": "4300",
    "vehicle_sales_tax_rate": "13",
}


def sold_vehicle(
    claim: str,
    column_2: str = "20000.00",
    column_3: str = "0",
    column_5: str = "12000.00",
    class_number: str = "10.1",
    no_property_left: int = 1,
) -> tuple[str, str, str, str, str, str, str, int, str, str, str]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9): Return CD's Class 10.1 vehicle, owned at the start
    (column 2 20000.00), sold for 12000.00 with no property left, so column 7 is 8000.00."""
    return (
        class_number,
        column_2,
        column_3,
        column_5,
        "0",
        "0",
        claim,
        no_property_left,
        "0",
        "0",
        "0",
    )


def run_cd(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CD's inputs, as in `returns/2025_return_cd.yaml`: a sole proprietor with one Class
    10.1 vehicle sold.

    One T2125 statement for the business: gross sales of 40000 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 7000 on three lines and 3000.00 of capital cost allowance (Class
    10.1, column 2 20000.00, proceeds 12000.00, no property left, claim 3000.00), 10000.00 in all
    (line 9368), so line 9369 is 30000.00; no business-use-of-home expenses, so line 9946 and T1
    line 13500 are 30000.00, Return BB's.
    """
    statement: dict[str, Any] = {
        "business": BUSINESS,
        "business_cca_classes_rows": (sold_vehicle("3000.00"),),
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


def statement_cd(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CD's one T2125 statement: its lines, as the form computes them."""
    return run_cd(changes)["ca/t2125"][0]


def test_return_cds_class_10_1_works_column_19_as_half_of_column_2() -> None:
    # Area A, Class 10.1 (30%): column 7 is 20000.00 + 0 - 12000.00 = 8000.00; columns 4, 6, 8, 9,
    # 10, 11, 12, 15, 17 and 18 are 0, column 14 is 12000.00 and column 16 is 12000.00. The vehicle
    # was owned at the end of 2024 (column 2 is above 0) and no property is left, so by the
    # half-year rule on sale column 19 is 50% of column 2, 20000.00 / 2 = 10000.00; the maximum
    # (column 19 x column 20) is 10000.00 x 30% = 3000.00 and column 21 is 3000.00, the claim.
    statement = statement_cd()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert (
        "business_cca_table_claim: item 1 class 10.1: column 7 8000, column 14 12000, "
        "column 15 0, column 16 12000, column 17 0, column 18 0, "
        "column 19 10000 (half-year rule on sale), "
        "maximum 30% of column 19 = 3000 (half-up to 0.01), claim 3000"
    ) in rendered
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("3000.00")


def test_return_cds_closing_ucc_is_zero_as_the_rest_is_not_deductible_later() -> None:
    # Column 7 less column 21 is 8000.00 - 3000.00 = 5000.00, but Regulation 1100(2.5) allows no
    # deduction in a later year and Folio S3-F4-C1 paragraph 1.106 reduces it to nil: column 22
    # is 0.
    statement = statement_cd()

    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records] == [
        (D("10.1"), D("0")),
    ]
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "business_closing_ucc: item 1 class 10.1: column 7 8000 less claim 3000 "
        "(half-year rule on sale), the rest is not deductible later: 0"
    ) in rendered


def test_return_cds_vehicle_has_no_recapture_and_no_terminal_loss() -> None:
    # Endnote 3 and Note 3: recapture and terminal loss do not apply to Class 10.1 (not a DIEP),
    # and column 7 is positive.
    statement = statement_cd()
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert (
        "business_recaptured_cca: item 1 class 10.1: column 7 8000 is not negative: recapture 0"
    ) in rendered
    assert (
        "business_terminal_loss: item 1 class 10.1: column 7 8000 with no property left, but a "
        "terminal loss does not apply to class 10.1 (half-year rule on sale used): "
        "terminal loss 0"
    ) in rendered


def test_return_cds_line_9936_is_3000_and_line_9369_is_30000() -> None:
    # Line ii, the total of column 21, is 3000.00, so is line 9936 (no personal part of CCA, no CCA
    # for business-use-of-home expenses). Line 9368 is 7000 + 3000.00 + 0 = 10000.00 and line 9369
    # is 40000 - 10000.00 = 30000.00.
    statement = statement_cd()

    assert statement.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("40000")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("3000.00")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("10000.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(BUSINESS_IMMEDIATE_EXPENSING_CLAIM).value == D("0")
    assert statement.get(BUSINESS_INCOME_BEFORE_CCA).value == D("33000.00")


def test_return_cds_net_business_income_is_30000_on_line_9946_and_t1_line_13500() -> None:
    # Part 7: no business-use-of-home expenses (0), so line 9946 is 30000.00 - 0 = 30000.00, T1
    # line 22 and line 13500; the net self-employment income (line 27) is 30000.00 + 0 + 0 + 0 +
    # 0.
    result = run_cd()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")


def test_return_cds_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BB's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    worksheet = run_cd()["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_a_claim_below_the_maximum_still_closes_the_class_at_zero() -> None:
    # A claim of 2000.00: line 9936 is 2000.00, line 9368 is 7000 + 2000.00 = 9000.00, line 9369
    # is 40000 - 9000.00 = 31000.00; column 22 is 0 (the 6000.00 left is lost).
    statement = statement_cd({"business_cca_classes_rows": (sold_vehicle("2000.00"),)})

    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("31000.00")
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("0")]


def test_a_class_10_1_claim_above_3000_is_refused() -> None:
    # Column 21 is 10000.00 x 30% = 3000.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_cd({"business_cca_classes_rows": (sold_vehicle("3000.01"),)})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 3000.01 is above the maximum 3000.00"
    )


def test_an_odd_cent_in_column_2_is_halved_and_rounded_once() -> None:
    # Column 2 20001.01: column 19 is 20001.01 / 2 = 10000.505, rounded half-up to 10000.51; the
    # maximum is 10000.51 x 30% = 3000.153, rounded half-up to 3000.15. Column 22 is 0.
    statement = statement_cd(
        {"business_cca_classes_rows": (sold_vehicle("3000.15", column_2="20001.01"),)}
    )

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("3000.15")
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("0")]
    with pytest.raises(InputAboveBoundError) as raised:
        run_cd({"business_cca_classes_rows": (sold_vehicle("3000.16", column_2="20001.01"),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 3000.16 is above the maximum 3000.15"
    )


def test_a_vehicle_bought_and_sold_in_the_year_has_no_claim() -> None:
    # Column 2 is 0 (not owned at the end of 2024): the rule is not used. Column 3 30000, column 5
    # 25000, so column 7 is 5000.00, positive with no property left: no claim, a UCC of 0 at the
    # end of the year and, as Class 10.1 is excluded, no terminal loss; line 9369 is 40000 - 7000
    # = 33000.00.
    row = sold_vehicle("0", column_2="0", column_3="30000", column_5="25000")
    statement = statement_cd({"business_cca_classes_rows": (row,)})

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("0")
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("33000.00")
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("0")]
    with pytest.raises(InputAboveBoundError) as raised:
        run_cd(
            {
                "business_cca_classes_rows": (
                    sold_vehicle("0.01", column_2="0", column_3="30000", column_5="25000"),
                )
            }
        )
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 0.01 is above the maximum 0"
    )


def test_a_vehicle_sold_for_more_than_column_2_has_no_claim_and_no_recapture() -> None:
    # Column 7 is 20000.00 - 25000.00 = -5000.00: no claim and a UCC of 0; as Class 10.1 is
    # excluded from recapture (Note 3) line 8230 stays 0, so line 9369 is 40000 - 7000 = 33000.00.
    row = sold_vehicle("0", column_5="25000.00")
    statement = statement_cd({"business_cca_classes_rows": (row,)})

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("0")
    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("33000.00")
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("0")]


def test_a_vehicle_with_property_left_in_the_class_is_worked_as_before() -> None:
    # No property left (0): column 19 is column 13, 20000.00 + 0 - 12000.00 = 8000.00 (column 2 is
    # not halved), the maximum 8000.00 x 30% = 2400.00; column 22 with the full claim is 8000.00
    # - 2400.00 = 5600.00.
    row = sold_vehicle("2400.00", no_property_left=0)
    statement = statement_cd({"business_cca_classes_rows": (row,)})
    rendered = EnglishTraceRenderer().render_all(statement.trace)

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("2400.00")
    assert (
        "business_cca_table_claim: item 1 class 10.1: column 7 8000, column 14 12000, "
        "column 15 0, column 16 12000, column 17 0, column 18 0, column 19 8000, "
        "maximum 30% of column 19 = 2400 (half-up to 0.01), claim 2400"
    ) in rendered
    with pytest.raises(InputAboveBoundError):
        run_cd({"business_cca_classes_rows": (sold_vehicle("2400.01", no_property_left=0),)})


def test_another_class_with_no_property_left_keeps_its_terminal_loss() -> None:
    # Class 8 with the same figures: column 7 is 8000.00, positive with no property left, so no
    # claim, a UCC of 0 and a terminal loss of 8000.00 on line 9270; line 9368 is 7000 + 0 +
    # 8000.00 = 15000.00 and line 9369 is 40000 - 15000.00 = 25000.00.
    row = sold_vehicle("0", class_number="8")
    statement = statement_cd({"business_cca_classes_rows": (row,)})

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("0")
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("8000.00")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("25000.00")
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    assert [record[CCA_UCC_AT_END] for record in records] == [D("0")]
