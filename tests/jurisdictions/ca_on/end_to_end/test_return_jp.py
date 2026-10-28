"""CA-ON 2025 end to end: Return JP (returns/2025_return_jp.yaml), the 15% limit on foreign tax on
income from property.

Return JP is an Ontario resident with employment income of 300,000 and 20,000 of foreign dividends
from one country, which withheld 6,000 (30%). Form T2209 (page 1 note, confirmed from the PDF, no
.txt published): "If you paid tax on income from property sourced outside of Canada (other than
real or immovable property), your non-business foreign tax credit for that income cannot be more
than 15% of your net income from that property. However, you may be able to deduct the part of the
foreign taxes you paid over 15% on line 23200 of your return." The tax over 15% is deducted on
line 23200 and is left out of line 1 of the credit, and so of Form T2036.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID,
    AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS,
    AMT_PART_7_FOREIGN_TAXES_PAID,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FOREIGN_PROPERTY_TAX_OVER_LIMIT,
    FOREIGN_TAX_CREDIT_SHEET_LINE_3,
    FOREIGN_TAX_CREDIT_SHEETS,
    NET_INCOME_BEFORE_ADJUSTMENTS,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# (tax paid, net foreign non-business income, the four business figures, then the tax paid on
# income from property and that income.)
DIVIDENDS = ("6000", "20000", "0", "0", "0", "0", "6000", "20000")


def return_jp(*countries: tuple[str, ...], **overrides: Any) -> Worksheet:
    """Return JP: employment income of 300,000 and 20,000 of foreign dividends, with `countries`
    as the countries of Form T2209."""
    inputs: dict[str, Any] = {
        "employment_income": "300000",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "foreign_investment_income": "20000",
        "income_tax_deducted": "100000",
        "foreign_tax_countries_rows": countries or (DIVIDENDS,),
    }
    return compute(**{**inputs, **overrides})


def test_tax_over_15_percent_of_property_income_is_deducted_on_line_23200() -> None:
    # 6,000 of tax on 20,000 of property income: 15% is 3,000, so 3,000 is over. The line 23300
    # deductions are the enhanced CPP (678.00 + 396.00) and the 3,000.00.
    worksheet = return_jp()

    assert worksheet.get(FOREIGN_PROPERTY_TAX_OVER_LIMIT).value == D("3000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("4074.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("315926.00")


def test_the_credit_for_property_income_is_at_most_15_percent_of_it() -> None:
    # Line 2 would be 20,000 x 76,064.64 / 315,926.00 = 4,815.35, above the 3,000.00 that is left of
    # line 1: the credit is 3,000.00.
    worksheet = return_jp()

    assert worksheet.get(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT).value == D("3000.00")
    (sheet,) = worksheet.get(FOREIGN_TAX_CREDIT_SHEETS).value.records
    assert sheet[FOREIGN_TAX_CREDIT_SHEET_LINE_3] == D("3000.00")


def test_ontario_gives_no_credit_for_the_tax_over_the_limit() -> None:
    # Form T2036 line 1 is line 1 of Form T2209, 3,000.00, less its line 3, 3,000.00.
    worksheet = return_jp()

    assert worksheet.get(ontario.PROVINCIAL_FOREIGN_TAX_CREDIT).value == D("0.00")


def test_the_alternative_minimum_tax_leaves_out_the_tax_over_the_limit() -> None:
    # Form T691 note (12): the tax paid less the part deductible under subsection 20(11). Line 7 is
    # 6,000 - 3,000 = 3,000.00 and the Part 7 line 12 denominator is that plus the 0 business tax.
    worksheet = return_jp()

    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_PAID_BEFORE_EXCESS).value == D("6000")
    assert worksheet.get(AMT_FOREIGN_NON_BUSINESS_TAX_PAID).value == D("3000.00")
    assert worksheet.get(AMT_PART_7_FOREIGN_TAXES_PAID).value == D("3000.00")


def test_tax_at_15_percent_has_nothing_over_the_limit() -> None:
    worksheet = return_jp(("3000", "20000", "0", "0", "0", "0", "3000", "20000"))

    assert worksheet.get(FOREIGN_PROPERTY_TAX_OVER_LIMIT).value == D("0")
    assert worksheet.get(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT).value == D("3000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("1074.00")


def test_dividends_not_entered_as_property_income_are_not_limited() -> None:
    # The same 6,000 on 20,000 with nothing entered as income from property: line 2 limits it.
    worksheet = return_jp(("6000", "20000"))

    assert worksheet.get(FOREIGN_PROPERTY_TAX_OVER_LIMIT).value == D("0")
    assert worksheet.get(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT).value > D("3000")


def test_property_tax_above_the_tax_paid_is_refused() -> None:
    with pytest.raises(ValidationError, match="foreign_property_tax_paid"):
        return_jp(("1000", "20000", "0", "0", "0", "0", "6000", "20000"))


def test_property_income_above_the_foreign_income_is_refused() -> None:
    with pytest.raises(ValidationError, match="net_foreign_property_income"):
        return_jp(("6000", "20000", "0", "0", "0", "0", "6000", "30000"))
