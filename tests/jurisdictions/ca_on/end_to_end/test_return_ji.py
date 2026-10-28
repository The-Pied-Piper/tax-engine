"""CA-ON 2025 end to end: return ji."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_FOREIGN_BUSINESS_TAX_PAID,
    AMT_FOREIGN_INCOME_LIMIT,
    AMT_FOREIGN_NON_BUSINESS_INCOME,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_FOREIGN_TAX_CREDIT_LESSER,
    AMT_FOREIGN_TAXES_PAID,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_8,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_10,
    FOREIGN_NON_BUSINESS_TAX_PAID,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_FOREIGN_NON_BUSINESS_INCOME,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.trace import ProvincialForeignTaxCreditLine
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# The two countries, each a record of Form T2209 as (tax paid, net foreign non-business income
# and, optionally, business income tax paid): country A, then country B with business tax.
COUNTRY_A = ("1500", "10000")
COUNTRY_B = ("500", "5000", "300")


def return_ji(**overrides: Any) -> Worksheet:
    """Return JI's inputs, as in `returns/2025_return_ji.yaml`, over the keyword overrides given.

    A filer with 40000 of other income and no employment income, who entered two countries of
    Form T2209 once each, as records: country A with 1500 of tax on 10000 of net foreign
    non-business income, and country B with 500 of tax on 5000, and 300 of business income tax.
    Form T691 Part 4 lines 2, 7 and 8 are their totals and no T691 figure is entered. The filer
    is not subject to minimum tax.
    """
    inputs: dict[str, Any] = {
        "other_income": "40000",
        "foreign_tax_countries_rows": (COUNTRY_A, COUNTRY_B),
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def sheets_of(worksheet: Worksheet) -> list[tuple[Decimal, Decimal, Decimal]]:
    """The T2209 sheets (tax paid, income, line 3) the return produced, in order."""
    value = worksheet.get(FOREIGN_TAX_CREDIT_SHEETS).value
    assert isinstance(value, RecordList)
    return [
        (
            Decimal(record[FOREIGN_NON_BUSINESS_TAX_PAID]),
            Decimal(record[NET_FOREIGN_NON_BUSINESS_INCOME]),
            Decimal(record[FOREIGN_TAX_CREDIT_SHEET_LINE_3]),
        )
        for record in value.records
    ]


def t2036_lines(worksheet: Worksheet) -> list[ProvincialForeignTaxCreditLine]:
    return [line for line in worksheet.trace if isinstance(line, ProvincialForeignTaxCreditLine)]


def test_part_4_lines_2_7_and_8_are_the_totals_of_both_countries() -> None:
    # Line 2 is 10000 + 5000 = 15000; line 7 is 1500 + 500 = 2000 (the non-business tax paid);
    # line 8 is the business tax of country B, 300. Each is entered once, on its record.
    worksheet = return_ji()

    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_INCOME).value == D("15000")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_PAID).value == D("2000")
    assert worksheet.get(AMT_FOREIGN_BUSINESS_TAX_PAID).value == D("300")


def test_part_4_lines_6_to_11_give_the_special_foreign_tax_credit_of_1633_33() -> None:
    # Line 4 is 15000.00 (no business income, no capital gains claim), and line 6 is 15000.00 x
    # 20.5% = 3075.00. Line 7 is 2000 x 66.6666%, 1333.332, rounded to 1333.33; line 9 is 1333.33 +
    # 300.00 = 1633.33; line 10 is the lesser of 3075.00 and 1633.33; line 11 is the greater of the
    # federal foreign tax credit of Part 3 line 7, 1297.98, and line 10: 1633.33.
    worksheet = return_ji()

    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("3075.00")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("1333.33")
    assert worksheet.get(AMT_FOREIGN_TAXES_PAID).value == D("1633.33")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("1633.33")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("1633.33")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")


def test_the_federal_credit_is_the_line_3_of_each_sheet_added() -> None:
    # Basic federal tax 3461.29 over net income 40000.00: country A, line 2 is 10000 x 3461.29 /
    # 40000 = 865.3225, rounded to 865.32, and line 3 is the lesser of 1500 and 865.32; country B,
    # line 2 is 5000 x 3461.29 / 40000 = 432.66125, rounded to 432.66, and line 3 is 432.66.
    worksheet = return_ji()

    assert sheets_of(worksheet) == [
        (D("1500"), D("10000"), D("865.32")),
        (D("500"), D("5000"), D("432.66")),
    ]
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("1297.98")
    assert worksheet.get(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT).value == D("2163.31")


def test_the_business_credit_is_worked_sheet_by_sheet_and_is_nil() -> None:
    # Line 8 is the basic federal tax, 3461.29, on each sheet: 6922.58 in all. Line 10 is line 8
    # less the sheet's line 3: 3461.29 - 865.32 = 2595.97 and 3461.29 - 432.66 = 3028.63, 5624.60 in
    # all. Line 11 is the lesser of line 4, line 7 and line 10 on each sheet, which is 0 on both as
    # line 7 (the net foreign business income) is 0.
    worksheet = return_ji()

    assert worksheet.get(FOREIGN_BUSINESS_TAX_CREDIT_LINE_8).value == D("6922.58")
    assert worksheet.get(FOREIGN_BUSINESS_TAX_CREDIT_LINE_10).value == D("5624.60")


def test_ontario_credit_is_worked_for_each_country_on_its_own_sheet() -> None:
    # Tax otherwise payable 1376.28 (ON428 line 81, no reduction). Country A: line 1 1500, line 2
    # 865.32, line 3 634.68; line 4 is 1376.28 x 10000 / 40000 = 344.07; line 5 is 344.07. Country
    # B: line 3 is 67.34; line 4 is 1376.28 x 5000 / 40000 = 172.035, rounded to 172.04; line 5 is
    # 67.34. The credit is 344.07 + 67.34 = 411.41, and Ontario tax is 1376.28 - 411.41 + 450.00
    # (health premium) = 1414.87.
    worksheet = return_ji()

    assert [(line.line_3, line.line_4, line.result) for line in t2036_lines(worksheet)] == [
        (D("634.68"), D("344.07"), D("344.07")),
        (D("67.34"), D("172.04"), D("67.34")),
    ]
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("411.41")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOREIGN_TAX_CREDIT).value == D("964.87")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("1414.87")


def test_total_payable_is_3578_18_and_the_balance_owing_is_the_same() -> None:
    # Federal tax after the foreign tax credit, 2163.31, plus Ontario tax, 1414.87: 3578.18. No tax
    # is deducted at source, so the balance owing is 3578.18.
    worksheet = return_ji()

    assert worksheet.get(TOTAL_PAYABLE).value == D("3578.18")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("3578.18")


def test_an_empty_list_of_countries_gives_lines_2_7_and_8_of_zero() -> None:
    # With no country record, the totals of the records are 0 on each line of Part 4 that reads
    # them, and no foreign credit is given.
    worksheet = return_ji(foreign_tax_countries_rows=())

    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_INCOME).value == D("0")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_PAID).value == D("0")
    assert worksheet.get(AMT_FOREIGN_BUSINESS_TAX_PAID).value == D("0")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("0")
