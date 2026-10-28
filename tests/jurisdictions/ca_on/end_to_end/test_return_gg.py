"""CA-ON 2025 end to end: return gg, the three income lines of the Canada workers benefit.

Return GG is `returns/2025_return_gg.yaml`: other employment income of 3,000 (T1 line 10400),
taxable scholarships of 2,000 (line 13010) and a T2125 net profit of 3,000 (line 13500), with no
employment income, so the working income of Schedule 6 is 8,000 and the benefit 1,350.00. The tests
here carry each line alone, which no worked return does.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    AMT_ADDITIONAL_TAXES_FOR_CARRYOVER,
    AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE,
    AMT_CARRYOVER_AVAILABLE_FOR_2026,
    AMT_PART_8_ADDITIONAL_TAXES,
    CANADA_WORKERS_BENEFIT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_EMPLOYMENT_INCOME,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    WORKING_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_gg(
    other: str = "0", scholarships: str = "0", business_gross: str | None = None
) -> Worksheet:
    """Return GG's inputs, as in `returns/2025_return_gg.yaml`, over the three income lines given.

    `business_gross` is the gross sales of one T2125 statement with no expenses, so its net profit
    (line 13500) is the same amount; None is no statement. No employment income.
    """
    overrides: dict[str, Any] = {
        "other_employment_income": other,
        "taxable_scholarships": scholarships,
    }
    if business_gross is not None:
        overrides["business_statements"] = ({"business": {"gross_sales": business_gross}},)
    return compute("0", (), "0", "0", "0", "0", "0", **overrides)


def test_the_three_lines_together_make_a_working_income_of_8000() -> None:
    # Schedule 6 line 1: 0 + 3,000 = 3,000. Line 2: 2,000. Line 3: the statement's 3,000. Line 5:
    # 3,000 + 2,000 + 3,000 = 8,000, which is also family working income (line 6). Line 18 is
    # 5,000, line 20 is 27% of it, 1,350, under the maximum of 1,633, and line 25 is 0, so line 28
    # is 1,350.
    worksheet = return_gg(other="3000", scholarships="2000", business_gross="3000")

    assert worksheet.get(CWB_EMPLOYMENT_INCOME).value == D("3000")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("3000")
    assert worksheet.get(WORKING_INCOME).value == D("8000")
    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("8000")
    assert worksheet.get(CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT).value == D("1350")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("0")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("1350")


@pytest.mark.parametrize(
    ("other", "scholarships", "business_gross", "working", "benefit"),
    [
        # Other employment income (line 10400) of 15,000 alone: 27% of 12,000 is 3,240, capped at
        # 1,633.
        ("15000", "0", None, "15000", "1633.00"),
        # Taxable scholarships (line 13010) of 15,000 alone: the same working income and benefit.
        ("0", "15000", None, "15000", "1633.00"),
        # A T2125 net profit of 30,000 alone (as Return BB): 27% of 27,000 is 7,290, capped at
        # 1,633, less 15% of 3,145 (over 26,855), 471.75, so 1,161.25.
        ("0", "0", "30000", "30000", "1161.25"),
        # A T2125 net profit of 10,000 alone: 27% of 7,000 is 1,890, capped at 1,633.
        ("0", "0", "10000", "10000", "1633.00"),
    ],
)
def test_each_income_line_alone_counts_toward_the_working_income(
    other: str,
    scholarships: str,
    business_gross: str | None,
    working: str,
    benefit: str,
) -> None:
    worksheet = return_gg(other=other, scholarships=scholarships, business_gross=business_gross)

    assert worksheet.get(WORKING_INCOME).value == D(working)
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D(benefit)


def test_the_line_1_amount_is_the_employment_income_and_the_other_employment_income() -> None:
    # Schedule 6 line 1 "Employment income and other employment income from line 10100 and line
    # 10400 of the return": with 10400 of 15,000 and no employment income, line 1 is 15,000.
    worksheet = return_gg(other="15000")

    assert worksheet.get(CWB_EMPLOYMENT_INCOME).value == D("15000")


def test_the_self_employment_profit_alone_is_reduced_by_15_percent_over_26855() -> None:
    # Schedule 6 line 23 is the adjusted family net income, 30,000 (the statement's net profit, no
    # other income); line 25 is 3,145, and line 27 is 471.75, taken from the 1,633 maximum.
    worksheet = return_gg(business_gross="30000")

    assert worksheet.get(ADJUSTED_FAMILY_NET_INCOME).value == D("30000")
    assert worksheet.get(CWB_REDUCTION_WITHOUT_DEPENDANT).value == D("471.75")


def test_no_minimum_tax_payable_so_part_7_is_not_completed_and_the_carryover_is_0() -> None:
    # T691 Part 5 line 11 is 0 on 8,000 of income: "you are not subject to alternative minimum
    # tax", and parts 6 and 7 are completed only when line 11 is positive. Part 7 line 14 worked
    # alone would be 1,392.00 (federal tax 1,160.00 less credits 2,552.00), but Part 8 line 14 is 0,
    # so the carryover for 2026 is 0.
    worksheet = return_gg(other="3000", scholarships="2000", business_gross="3000")

    assert worksheet.get(AMT_ALTERNATIVE_MINIMUM_TAX_PAYABLE).value == D("0")
    assert worksheet.get(AMT_ADDITIONAL_TAXES_FOR_CARRYOVER).value == D("1392.00")
    assert worksheet.get(AMT_PART_8_ADDITIONAL_TAXES).value == D("0")
    assert worksheet.get(AMT_CARRYOVER_AVAILABLE_FOR_2026).value == D("0")
