"""CA-ON 2025 end to end: return bv."""

from __future__ import annotations

from fractions import Fraction as ExactFraction
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import ValidationError
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_FOREIGN_INCOME_LIMIT,
    AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS,
    AMT_FOREIGN_TAX_CREDIT_LESSER,
    AMT_MINIMUM_AMOUNT,
    AMT_NET_MINIMUM_TAX_PAYABLE,
    AMT_PART_5_LINE_11_IS_POSITIVE,
    AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE,
    AMT_SPECIAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_AFTER_CREDITS,
    FOREIGN_TAX_CREDIT_NET_INCOME,
    NET_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.trace import (
    PooledProvincialForeignTaxCreditLine,
    ProvincialForeignTaxCreditLine,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute

US = ("300", "3000")
UK = ("150", "300")
RATE = ExactFraction(D("0.666666"))


def return_bv(**overrides: Any) -> Worksheet:
    """Return BV's inputs, as in `returns/2025_return_bv.yaml`.

    A filer with no employment income, a capital gain on shares of 360000 (proceeds, no cost
    base) and 3300 of foreign investment income in two countries of Form T2209: the United
    States, 300 of tax paid on 3000 of net foreign non-business income, and the United Kingdom,
    150 on 300. Form T691 Part 4 lines 2, 7 and 8 are the sheets' 3300 and 450 and no business
    tax, 0.
    """
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (("360000", "0", "0"),),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "foreign_investment_income": "3300",
        "foreign_tax_countries_rows": (US, UK),
    }
    return compute(**{**inputs, **overrides})


def sheet_lines(worksheet: Worksheet) -> list[ProvincialForeignTaxCreditLine]:
    return [line for line in worksheet.trace if isinstance(line, ProvincialForeignTaxCreditLine)]


def test_return_bvs_taxable_income_and_basic_federal_tax_are_183300_and_35744_63() -> None:
    # The gain is 360000 - 0 - 0; at the 50% inclusion rate the taxable capital gains (line 12700)
    # are 180000.00. Total income: 3300 (line 12100) + 180000.00 = 183300.00, with no deduction:
    # net income and taxable income are 183300.00. Federal tax: 29% x (183300.00 - 177882.00) +
    # 36495.57 = 1571.22 + 36495.57 = 38066.79. The basic personal amount, net income being
    # between 177882 and 253414: 14538 + 1591 - 5418 x 1591 / 75532 = 16014.8756..., half-up
    # 16014.88; at 14.5% 2322.1576, half-up 2322.16 (the top-up credit is 0). Line 42900 is
    # 38066.79 - 2322.16 = 35744.63.
    worksheet = return_bv()

    assert worksheet.get(TOTAL_INCOME).value == D("183300.00")
    assert worksheet.get(NET_INCOME).value == D("183300.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("183300.00")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("35744.63")
    assert worksheet.get(FOREIGN_TAX_CREDIT_NET_INCOME).value == D("183300.00")


def test_minimum_tax_is_payable_because_t691_part_5_line_11_is_1104_98() -> None:
    # Part 1: line 27 = 183300.00 + 0 + 180000.00 (line 23, the non-taxable part of the gain) +
    # 0 = 363300.00, which is line 93; line 95 = 363300.00 - 177882.00 = 185418.00; line 97 =
    # 185418.00 x 20.5% = 38010.69; line 98 = 2322.16 x 50% = 1161.08; line 103 = 36849.61.
    # Part 4: line 6 = 3300 x 20.5% = 676.50; line 7 = 450 x 66.6666% = 299.9997, half-up 300.00;
    # line 9 = 300.00 + 0; line 10 = lesser(676.50, 300.00) = 300.00. The federal credit of
    # Form T2209 is 358.50 (below), so line 11 = more(358.50, 300.00) = 358.50. Part 5: line 3 =
    # 36849.61 - 358.50 = 36491.11; line 6 = 35386.13 (Part 3 line 15 = 35744.63 - 358.50, with
    # no surtax); line 7 = 36491.11 - 35386.13 = 1104.98 = line 11 (lines 8 to 10 are 0).
    worksheet = return_bv()

    assert worksheet.get(AMT_MINIMUM_AMOUNT).value == D("36849.61")
    assert worksheet.get(AMT_FOREIGN_INCOME_LIMIT).value == D("676.50")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("300.00")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("300.00")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("358.50")
    assert worksheet.get(AMT_NET_MINIMUM_TAX_PAYABLE).value == D("36491.11")
    assert worksheet.get(AMT_REGULAR_NET_FEDERAL_TAX_PAYABLE).value == D("35386.13")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1104.98")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 1


def test_form_t2209_gives_300_and_58_50_for_the_two_countries() -> None:
    # Basic federal tax (note 4) 35744.63. United States: line 2 = 3000 x 35744.63 / 183300.00 =
    # 585.0185..., half-up 585.02; line 3 = lesser(300, 585.02) = 300. United Kingdom: line 2 =
    # 300 x 35744.63 / 183300.00 = 58.5018..., half-up 58.50; line 3 = lesser(150, 58.50) =
    # 58.50. The total, line 13, is 358.50.
    worksheet = return_bv()

    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("358.50")


def test_two_countries_over_200_take_line_2_of_form_t2036_from_the_special_credit() -> None:
    # Minimum tax is payable and the total tax, 300 + 150 = 450, is more than 200, so by note (1)
    # each country's line 2 is its line 1 / (line 7 / 66.6666% + line 8) x line 11, with the
    # divisor 300.00 / 0.666666 + 0.00 = 450.00045000045...: United States 300 x 358.50 / divisor
    # = 238.9997..., half-up 239.00; United Kingdom 150 x 358.50 / divisor = 119.4998..., half-up
    # 119.50. Line 3 = 61.00 and 30.50. Line 4: 3000 x 20955.29 / 183300.00 = 342.9671..., half-up
    # 342.97, and 300 x 20955.29 / 183300.00 = 34.2967..., half-up 34.30. Line 5 = 61.00 and
    # 30.50, total 91.50 (line 2 from Form T2209, 300 and 58.50, would give 0.00 and 34.30).
    worksheet = return_bv()

    divisor = ExactFraction(D("300.00")) / RATE
    assert sheet_lines(worksheet) == [
        ProvincialForeignTaxCreditLine(
            output=ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            position=1,
            tax_paid=D("300"),
            federal_credit=D("239.00"),
            line_3=D("61.00"),
            income=D("3000"),
            net_income=D("183300.00"),
            provincial_tax=D("20955.29"),
            rounding=CENT,
            line_4=D("342.97"),
            result=D("61.00"),
            special_credit=D("358.50"),
            divisor=divisor,
            separate_sheet=True,
        ),
        ProvincialForeignTaxCreditLine(
            output=ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            position=2,
            tax_paid=D("150"),
            federal_credit=D("119.50"),
            line_3=D("30.50"),
            income=D("300"),
            net_income=D("183300.00"),
            provincial_tax=D("20955.29"),
            rounding=CENT,
            line_4=D("34.30"),
            result=D("30.50"),
            special_credit=D("358.50"),
            divisor=divisor,
            separate_sheet=True,
        ),
    ]
    totals = [line for line in worksheet.trace if isinstance(line, ItemsTotalLine)]
    assert (
        ItemsTotalLine(
            ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            ((1, D("61.00")), (2, D("30.50"))),
            D("91.50"),
        )
        in totals
    )
    assert worksheet.get(ontario.TAX_OTHERWISE_PAYABLE).value == D("20955.29")
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT).value == D("91.50")
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("91.50")


def test_the_trace_names_which_line_2_each_sheet_used() -> None:
    worksheet = return_bv()

    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    # The divisor 300.00 / 0.666666 is 50000000/111111, which does not terminate.
    assert (
        "provincial_foreign_tax_credit_before_limit: sheet 1: tax paid 300 less minimum tax line 2 "
        "239 (300 tax paid x 358.5 special foreign tax credit / 50000000/111111 total foreign "
        "taxes paid, separate sheet, half-up to 0.01) = 61; "
        "3000 net foreign income x 20955.29 provincial tax / 183300 net income = 342.97 "
        "(half-up to 0.01); credit 61"
    ) in rendered
    assert (
        "provincial_foreign_tax_credit_before_limit: sheet 2: tax paid 150 less minimum tax line 2 "
        "119.5 (150 tax paid x 358.5 special foreign tax credit / 50000000/111111 total foreign "
        "taxes paid, separate sheet, half-up to 0.01) = 30.5; "
        "300 net foreign income x 20955.29 provincial tax / 183300 net income = 34.3 "
        "(half-up to 0.01); credit 30.5"
    ) in rendered


def test_non_business_tax_of_150_with_business_tax_of_60_is_one_pooled_form_on_the_totals() -> None:
    # Form T2209 counts the business tax too: 100 + 50 + 30 + 30 = 210 is more than 200, so each
    # country has its own sheet. Form T2036 counts the non-business tax only: 100 + 50 = 150 is not
    # more than 200, so it is one form on the totals. Business income is 0, so the business credit
    # of each sheet is 0.
    # Sheets (basic federal tax 35744.63, net income 183300.00): United States, line 2 = 3000 x
    # 35744.63 / 183300.00 = 585.0185..., half-up 585.02, line 3 = lesser(100, 585.02) = 100;
    # United Kingdom, line 2 = 300 x 35744.63 / 183300.00 = 58.5018..., half-up 58.50, line 3 =
    # lesser(50, 58.50) = 50. The federal foreign tax credit is 150.
    # Form T691 Part 4: line 6 = 3300 x 20.5% = 676.50; line 7 = 150 x 66.6666% = 99.9999, half-up
    # 100.00; line 8 = the business tax, 30 + 30 = 60.00; line 9 = 160.00; line 10 = lesser(676.50,
    # 160.00) = 160.00; line 11 = more(150.00, 160.00) = 160.00. Part 5: line 3 = 36849.61 -
    # 160.00 = 36689.61; line 6 = 35744.63 - 150.00 = 35594.63; line 7 = 36689.61 - 35594.63 =
    # 1094.98, so minimum tax is payable.
    # Form T2036, one form on the totals: line 1 = 100 + 50 = 150; line 2 = 150 x 160.00 /
    # (150 + 60) = 114.2857..., half-up 114.29; line 3 = 35.71. Income 3000 + 300 = 3300, which is
    # not more than net income; line 4 = 3300 x 20955.29 / 183300.00 = 377.2638..., half-up 377.26;
    # line 5 = lesser(35.71, 377.26) = 35.71.
    worksheet = return_bv(
        foreign_tax_countries_rows=(("100", "3000", "30"), ("50", "300", "30")),
    )

    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("150")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_TWO_THIRDS).value == D("100.00")
    assert worksheet.get(AMT_FOREIGN_TAX_CREDIT_LESSER).value == D("160.00")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("160.00")
    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1094.98")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 1
    assert sheet_lines(worksheet) == []
    assert [
        line for line in worksheet.trace if isinstance(line, PooledProvincialForeignTaxCreditLine)
    ] == [
        PooledProvincialForeignTaxCreditLine(
            output=ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            sheets=2,
            tax_paid=D("150"),
            federal_credit=D("114.29"),
            line_3=D("35.71"),
            income=D("3300"),
            net_income=D("183300.00"),
            provincial_tax=D("20955.29"),
            threshold=D("200"),
            rounding=CENT,
            line_4=D("377.26"),
            result=D("35.71"),
            special_credit=D("160.00"),
            divisor=ExactFraction(210),
        )
    ]
    assert not [
        line
        for line in worksheet.trace
        if isinstance(line, ItemsTotalLine)
        and line.output == ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "provincial_foreign_tax_credit_before_limit: all 2 sheets pooled, tax paid 150 is not more "
        "than 200: tax paid 150 less minimum tax line 2 114.29 (150 tax paid x 160 special foreign "
        "tax credit / 210 total tax paid plus business tax, half-up to 0.01) = 35.71; "
        "3300 net foreign income x 20955.29 provincial tax / 183300 net income = 377.26 "
        "(half-up to 0.01); credit 35.71"
    ) in rendered
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT).value == D("35.71")
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("35.71")


# --- the other variants: a total at or under 200, minimum tax not payable, a zero divisor --------


def test_one_sheet_with_exactly_200_of_tax_is_one_form_with_line_2_at_the_special_credit() -> None:
    # The United States alone, 200 paid on 660 of income (Part 4 lines 2 and 7 are 660 and 200).
    # Net income 180000.00 + 660 = 180660.00; federal tax 29% x 2778.00 + 36495.57 = 37301.19;
    # the basic personal amount 16129 - 2778 x 1591 / 75532 = 16070.4752..., half-up 16070.48, at
    # 14.5% 2330.2196, half-up 2330.22; line 42900 = 37301.19 - 2330.22 = 34970.97. Form T2209:
    # line 2 = 660 x 34970.97 / 180660.00 = 127.7..., half-up 127.76, line 3 = lesser(200,
    # 127.76) = 127.76. Part 1 line 93 = 360660.00, line 95 = 182778.00, line 97 = 37469.49, line
    # 98 = 1165.11, line 103 = 36304.38. Part 4: line 6 = 660 x 20.5% = 135.30, line 7 = 200 x
    # 66.6666% = 133.3332, half-up 133.33, line 10 = 133.33, line 11 = more(127.76, 133.33) =
    # 133.33. Part 5: line 3 = 36304.38 - 133.33 = 36171.05, line 6 = 34970.97 - 127.76 =
    # 34843.21, line 11 = 1327.84, so minimum tax is payable. The total, 200, is "$200 or less":
    # line 2 = 200 / (200 + 0) x 133.33 = 133.33; line 3 = 66.67; the tax otherwise payable is
    # 20454.50 (Ontario tax 16173.86 - 643.72 = 15530.14 plus the surtax 4924.36), so line 4 =
    # 660 x 20454.50 / 180660.00 = 74.72..., half-up 74.73; line 5 = 66.67.
    worksheet = return_bv(
        foreign_investment_income="660",
        foreign_tax_countries_rows=(("200", "660"),),
    )

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1327.84")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("127.76")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("133.33")
    assert sheet_lines(worksheet) == [
        ProvincialForeignTaxCreditLine(
            output=ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            position=1,
            tax_paid=D("200"),
            federal_credit=D("133.33"),
            line_3=D("66.67"),
            income=D("660"),
            net_income=D("180660.00"),
            provincial_tax=D("20454.50"),
            rounding=CENT,
            line_4=D("74.73"),
            result=D("66.67"),
            special_credit=D("133.33"),
            divisor=ExactFraction(200),
            separate_sheet=False,
        )
    ]
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("66.67")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "provincial_foreign_tax_credit_before_limit: sheet 1: tax paid 200 less minimum tax line 2 "
        "133.33 (200 tax paid x 133.33 special foreign tax credit / 200 total tax paid plus "
        "business tax, half-up to 0.01) = 66.67; "
        "660 net foreign income x 20454.5 provincial tax / 180660 net income = 74.73 "
        "(half-up to 0.01); credit 66.67"
    ) in rendered


def test_two_countries_with_150_of_tax_are_one_pooled_sheet_with_line_2_at_the_special_credit() -> (
    None
):
    # Two countries with 100 on 240 and 50 on 240 (lines 2 and 7 of Part 4 are 480 and 150).
    # Their total, 150, is not more than 200, so Form T2209 is one calculation on the totals and
    # its one sheet carries 150 and 480. Net income 180000.00 + 480 = 180480.00; federal tax 29% x
    # 2598.00 + 36495.57 = 37248.99; the basic personal amount 16129 - 2598 x 1591 / 75532 =
    # 16074.2751..., half-up 16074.28, at 14.5% 2330.7706, half-up 2330.77; line 42900 = 37248.99
    # - 2330.77 = 34918.22. Form T2209: line 2 = 480 x 34918.22 / 180480.00 = 92.8697..., half-up
    # 92.87; line 3 = lesser(150, 92.87) = 92.87. Part 1 line 93 = 360480.00, line 95 =
    # 182598.00, line 97 = 37432.59, line 98 = 2330.77 x 50% = 1165.385, half-up 1165.39, line
    # 103 = 36267.20. Part 4: line 6 = 480 x 20.5% = 98.40; line 7 = 150 x 66.6666% = 99.9999,
    # half-up 100.00; line 10 = lesser(98.40, 100.00) = 98.40; line 11 = more(92.87, 98.40) =
    # 98.40. Part 5: line 3 = 36267.20 - 98.40 = 36168.80; line 6 = 34918.22 - 92.87 =
    # 34825.35; line 7 = 1343.45 = line 11: minimum tax is payable. Form T2036 has the one sheet,
    # whose total, 150, is "$200 or less": line 2 = 150 / (150 + 0) x 98.40 = 98.40; line 3 =
    # 51.60; the tax otherwise payable is 20420.35 (Ontario tax 16151.97 - 643.72 = 15508.25 plus
    # the surtax 4912.10), so line 4 = 480 x 20420.35 / 180480.00 = 54.30..., half-up 54.31;
    # line 5 = 51.60.
    worksheet = return_bv(
        foreign_investment_income="480",
        foreign_tax_countries_rows=(("100", "240"), ("50", "240")),
    )

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("1343.45")
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("92.87")
    assert worksheet.get(AMT_SPECIAL_FOREIGN_TAX_CREDIT).value == D("98.40")
    assert sheet_lines(worksheet) == [
        ProvincialForeignTaxCreditLine(
            output=ontario.PROVINCIAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
            position=1,
            tax_paid=D("150"),
            federal_credit=D("98.40"),
            line_3=D("51.60"),
            income=D("480"),
            net_income=D("180480.00"),
            provincial_tax=D("20420.35"),
            rounding=CENT,
            line_4=D("54.31"),
            result=D("51.60"),
            special_credit=D("98.40"),
            divisor=ExactFraction(150),
            separate_sheet=False,
        )
    ]
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("51.60")


def test_minimum_tax_not_payable_keeps_line_2_as_the_t2209_line_3() -> None:
    # A gain of 300000 instead: taxable capital gains 150000.00, net income 150000.00 + 3300 =
    # 153300.00 (below 177882, so the basic personal amount is 16129). Federal tax: 26% x
    # (153300.00 - 114750.00) + 20081.25 = 30104.25; the credit 16129 x 14.5% = 2338.705, half-up
    # 2338.71; line 42900 = 27765.54. Form T2209: line 2 = 3000 x 27765.54 / 153300.00 = 543.3...,
    # half-up 543.36, line 3 = 300; 300 x 27765.54 / 153300.00 = 54.34, line 3 = 54.34; total
    # 354.34. T691: line 93 = 153300.00 + 150000.00 = 303300.00, line 95 = 125418.00, line 97 =
    # 25710.69, line 98 = 2338.71 x 50% = 1169.355, half-up 1169.36, line 103 = 24541.33. Part 4:
    # line 10 = lesser(676.50, 300.00) = 300.00, line 11 = more(354.34, 300.00) = 354.34. Part 5:
    # line 3 = 24541.33 - 354.34 = 24186.99; line 6 = 27765.54 - 354.34 = 27411.20; line 7 =
    # 24186.99 - 27411.20, negative: 0, so line 11 is 0 and minimum tax is not payable. Line 2
    # of Form T2036 is the sheet's line 3 of Form T2209: 300 and 54.34; line 3 = 0.00 and 95.66;
    # Ontario tax 12846.88 - 643.72 = 12203.16 plus the surtax 3061.25 = 15264.41, so line 4 =
    # 3000 x 15264.41 / 153300.00 = 298.72 and 300 x 15264.41 / 153300.00 = 29.87; line 5 = 0.00
    # and lesser(95.66, 29.87) = 29.87.
    worksheet = return_bv(share_dispositions=(("300000", "0", "0"),))

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(AMT_PART_5_LINE_11_IS_POSITIVE).value == 0
    assert worksheet.get(FEDERAL_FOREIGN_TAX_CREDIT).value == D("354.34")
    lines = sheet_lines(worksheet)
    assert [(line.federal_credit, line.line_3, line.line_4, line.result) for line in lines] == [
        (D("300"), D("0"), D("298.72"), D("0")),
        (D("54.34"), D("95.66"), D("29.87"), D("29.87")),
    ]
    assert [(line.special_credit, line.divisor, line.separate_sheet) for line in lines] == [
        (None, None, False)
    ] * 2
    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("29.87")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "provincial_foreign_tax_credit_before_limit: sheet 2: tax paid 150 less federal credit "
        "54.34 = 95.66; 300 net foreign income x 15264.41 provincial tax / 153300 net income = "
        "29.87 (half-up to 0.01); credit 29.87"
    ) in rendered


def test_no_tax_paid_and_no_business_tax_is_a_zero_divisor_and_refused() -> None:
    # Minimum tax is payable (the gain), the one country paid no tax, so Part 4 line 7 is 0.00
    # and line 8 is 0.00: the divisor of note (1) is 0 and line 2 is undefined.
    with pytest.raises(ValidationError, match="line 2 of Form T2036"):
        return_bv(
            foreign_tax_countries_rows=(("0", "3000"),),
            foreign_investment_income="3000",
        )
