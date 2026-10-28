"""CA-ON 2025 end to end: return cm."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLAIM,
    BUSINESS_CCA_TABLE_CLAIM,
    BUSINESS_CLOSING_UCC,
    BUSINESS_GROSS_INCOME_BEFORE_EXPENSES,
    BUSINESS_INCOME,
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
from tax_calculator.jurisdictions.ca_on.catalog import ONTARIO_BASIC_TAX
from tests.jurisdictions.ca_on.end_to_end.support import BusinessCcaRow, D, run

# Return CM's T2125: gross sales of 41400 (a chosen figure, so that line 9369 is 30000.00, as is
# Return BB's line 9946) and the three expense lines 1500 + 1200 + 4300 = 7000, with no motor
# vehicle (no Charts A to C) and no business-use-of-home expenses.
BUSINESS = {
    "gross_sales": "41400",
    "advertising": "1500",
    "insurance": "1200",
    "rent": "4300",
    "vehicle_sales_tax_rate": "13",
}


def area_a_row(
    class_number: str, additions: str, claim: str, differs: int
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, int]:
    """Area A row as (column 1, column 2, column 3, column 5, column 11, column 12, the claim, no
    property left, column 4, column 6, column 9, whether the row's additions follow the other
    half-year treatment than their class): additions bought in the year, nothing at the start."""
    return (class_number, "0", additions, "0", "0", "0", claim, 0, "0", "0", "0", differs)


MOULD = area_a_row("12", "3000", "1500", 1)
SOFTWARE = area_a_row("12", "1000", "500", 1)
SMALL_TOOLS = area_a_row("12", "400", "400", 0)
NON_ARMS_LENGTH_CLASS_8 = area_a_row("8", "10000", "2000", 1)
ROWS: tuple[BusinessCcaRow, ...] = (MOULD, SOFTWARE, SMALL_TOOLS, NON_ARMS_LENGTH_CLASS_8)


def run_cm(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return CM's inputs, as in `returns/2025_return_cm.yaml`: a sole proprietor with four rows of
    additions in Area A.

    One T2125 statement for the business: gross sales of 41400 (amount 3A, and so line 8299 and T1
    line 13499), expenses of 7000 on three lines and 4400 of capital cost allowance (a Class 12
    mould and a piece of Class 12 software, subject to the half-year rule, Class 12 small tools,
    and Class 8 property bought in a non-arm's length transaction, exempt from it), 11400 in all
    (line 9368), so line 9369 is 30000.00; no business-use-of-home expenses, so line 9946 and T1
    line 13500 are 30000.00, Return BB's.
    """
    statement: dict[str, Any] = {"business": BUSINESS, "business_cca_classes_rows": ROWS}
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


def statement_cm(changes: Mapping[str, Any] | None = None) -> Worksheet:
    """The worksheet of Return CM's one T2125 statement: its lines, as the form computes them."""
    return run_cm(changes)["ca/t2125"][0]


def closing(statement: Worksheet) -> list[tuple[Any, Any]]:
    records = statement.get(BUSINESS_CLOSING_UCC).value.records
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in records]


def test_return_cms_class_12_mould_is_subject_to_the_half_year_rule() -> None:
    # Guide T4002 "Class 12 (100%)": tools that are subject to the half-year rule include moulds.
    # Column 7 is 0 + 3000 - 0 = 3000; column 10 is 3000 and column 13 is 3000. The row says its
    # additions are subject to the rule though Class 12 is exempt, so column 18 is 50% of 3000,
    # 1500, column 19 is 3000 - 1500 = 1500 and the maximum is 1500 x 100% = 1500.
    rendered = EnglishTraceRenderer().render_all(statement_cm().trace)

    assert (
        "business_cca_table_claim: item 1 class 12: column 7 3000, column 14 0, "
        "column 15 0, column 16 0, column 17 0, column 18 1500, column 19 1500, "
        "maximum 100% of column 19 = 1500 (half-up to 0.01), claim 1500"
    ) in rendered


def test_return_cms_class_12_software_is_subject_to_the_half_year_rule() -> None:
    # Guide T4002: "Software in Class 12 is subject to the half-year rule": column 18 is 500,
    # column 19 is 1000 - 500 = 500 and the maximum is 500.
    rendered = EnglishTraceRenderer().render_all(statement_cm().trace)

    assert (
        "business_cca_table_claim: item 2 class 12: column 7 1000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 500, column 19 500, "
        "maximum 100% of column 19 = 500 (half-up to 0.01), claim 500"
    ) in rendered


def test_return_cms_class_12_small_tools_are_exempt_as_their_class_is() -> None:
    # Most of Class 12, "such as small tools", is not subject to the rule: column 18 is 0, column
    # 19 is 400 and the maximum is 400.
    rendered = EnglishTraceRenderer().render_all(statement_cm().trace)

    assert (
        "business_cca_table_claim: item 3 class 12: column 7 400, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 400, "
        "maximum 100% of column 19 = 400 (half-up to 0.01), claim 400"
    ) in rendered


def test_return_cms_non_arms_length_class_8_property_is_exempt_though_its_class_is_not() -> None:
    # Guide T4002 "Column 18": in a non-arm's length transaction the half-year rule may not apply.
    # Class 8 is subject to it, so the row says it is exempt: column 18 is 0, column 19 is 10000
    # and the maximum is 10000 x 20% = 2000.00 (1000.00 if the class's own treatment applied).
    rendered = EnglishTraceRenderer().render_all(statement_cm().trace)

    assert (
        "business_cca_table_claim: item 4 class 8: column 7 10000, column 14 0, column 15 0, "
        "column 16 0, column 17 0, column 18 0, column 19 10000, "
        "maximum 20% of column 19 = 2000 (half-up to 0.01), claim 2000"
    ) in rendered


def test_return_cms_line_9936_is_4400_and_line_9369_is_30000() -> None:
    # Amount ii, the total of column 21, is 1500 + 500 + 400 + 2000 = 4400, so is line 9936 (no
    # personal part of CCA, no CCA for business-use-of-home expenses). Line 9368 is 7000 + 4400 +
    # 0 = 11400 and line 9369 is 41400 - 11400 = 30000.00.
    statement = statement_cm()

    assert statement.get(BUSINESS_GROSS_INCOME_BEFORE_EXPENSES).value == D("41400")
    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("4400")
    assert statement.get(BUSINESS_CCA_CLAIM).value == D("4400")
    assert statement.get(BUSINESS_TOTAL_EXPENSES).value == D("11400")
    assert statement.get(BUSINESS_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("30000.00")
    assert statement.get(BUSINESS_RECAPTURED_CCA).value == D("0")
    assert statement.get(BUSINESS_TERMINAL_LOSS).value == D("0")


def test_return_cms_closing_ucc_is_each_rows_column_7_less_its_claim() -> None:
    # Column 22 is column 7 less column 21: 3000 - 1500, 1000 - 500, 400 - 400 and 10000 - 2000.
    assert closing(statement_cm()) == [
        (D("12"), D("1500")),
        (D("12"), D("500")),
        (D("12"), D("0")),
        (D("8"), D("8000")),
    ]


def test_return_cms_figures_that_depend_on_income_are_return_bbs() -> None:
    # Line 9946 is Return BB's 30000.00, so total income, net income and taxable income are
    # 30000.00 and the tax lines are Return BB's: the federal tax 30000.00 x 14.5% = 4350.00, the
    # Ontario tax 30000.00 x 5.05% = 1515.00 and the total payable 3182.57.
    result = run_cm()
    worksheet = result["ca-on/return"][0]

    assert result["ca/t2125"][0].get(BUSINESS_INCOME).value == D("30000.00")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("30000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("30000.00")
    assert worksheet.get(NET_INCOME).value == D("30000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("30000.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("4350.00")
    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("1515.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3182.57")
    # The Canada workers benefit of 1161.25 (1633.00 less 471.75, which is 15% of 30000.00
    # over 26855.00) is a refund against the total payable of 3182.57: 2021.32 owing.
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("2021.32")


def test_without_the_flag_the_mould_and_the_non_arms_length_row_follow_their_class() -> None:
    # Flag 0: Class 12 is exempt, so a mould of 3000 and software of 1000 have column 18 0 and
    # maximums 3000 and 1000, claimed in full, 4000. Class 8 is subject, so 10000 has column 18 50%
    # of 10000, 5000, column 19 5000 and a maximum of 5000 x 20% = 1000.00: a claim of 2000 is
    # refused.
    rows = (area_a_row("12", "3000", "3000", 0), area_a_row("12", "1000", "1000", 0))
    statement = statement_cm({"business_cca_classes_rows": rows})

    assert statement.get(BUSINESS_CCA_TABLE_CLAIM).value == D("4000")
    with pytest.raises(InputAboveBoundError) as raised:
        run_cm({"business_cca_classes_rows": (area_a_row("8", "10000", "2000", 0),)})
    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 2000 is above the maximum 1000.00"
    )


def test_a_claim_above_the_maximum_of_a_flagged_row_is_refused() -> None:
    # The mould's maximum is 1500; a claim of 1500.01 is one cent more.
    rows = (area_a_row("12", "3000", "1500.01", 1),)
    with pytest.raises(InputAboveBoundError) as raised:
        run_cm({"business_cca_classes_rows": rows})

    assert str(raised.value) == (
        "ca/t2125, instance 1: item 1: ca/cca_claimed 1500.01 is above the maximum 1500.00"
    )
