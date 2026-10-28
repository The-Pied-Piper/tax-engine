"""CA-ON 2025 end to end: return du, a T2125 statement's line code sends it to its own T1 line.

Return DU is `returns/2025_return_du.yaml`: one business statement (code 1, net and gross 3,000),
one professional statement (code 2, gross 6,000 less expenses of 2,000, so net 4,000) and one
commission statement (code 3, net and gross 1,500). Line 27 totals the three nets to 8,500. The
tests here vary the statements: a professional loss, a business statement alone, the order of the
statements, a code outside 1 to 3 (which is refused), and a sub-cent amount, which stays
unrounded through the return.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    COMMISSION_INCOME,
    GROSS_BUSINESS_INCOME,
    GROSS_COMMISSION_INCOME,
    GROSS_PROFESSIONAL_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    PROFESSIONAL_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

BUSINESS = {"business": {"gross_sales": "3000"}, "business_income_line": 1}
PROFESSIONAL = {
    "business": {"gross_sales": "6000", "office_expenses": "2000"},
    "business_income_line": 2,
}
COMMISSION = {"business": {"gross_sales": "1500"}, "business_income_line": 3}


def return_du(
    business_statements: tuple[dict[str, Any], ...] = (BUSINESS, PROFESSIONAL, COMMISSION),
    **overrides: Any,
) -> Worksheet:
    """Return DU's inputs, as in `returns/2025_return_du.yaml`, over the keyword overrides given.

    No employment income and no CPP or QPP deducted at source (T4 box 16 and box 22, chosen $0),
    Schedule 8 Part 5 completed for the self-employment income, and the three statements.
    """
    inputs: dict[str, Any] = {
        "business_statements": business_statements,
        "cpp_part_5_completed": 1,
        "cpp_t4_base_and_first_additional_contributions": "0",
        "cpp_t4_second_additional_contributions": "0",
    }
    inputs.update(overrides)
    return compute("0", (), "0", "0", "0", "0", "0", **inputs)


def test_each_statement_goes_to_the_t1_line_of_its_code() -> None:
    worksheet = return_du()

    # T1 line 22 (13500), line 23 (13700) and line 24 (13900): the net of each statement, by code.
    assert worksheet.get(BUSINESS_INCOME).value == D("3000")
    assert worksheet.get(PROFESSIONAL_INCOME).value == D("4000")
    assert worksheet.get(COMMISSION_INCOME).value == D("1500")


def test_the_gross_boxes_13499_13699_and_13899_each_total_line_8299_of_their_statements() -> None:
    worksheet = return_du()

    assert worksheet.get(GROSS_BUSINESS_INCOME).value == D("3000")
    assert worksheet.get(GROSS_PROFESSIONAL_INCOME).value == D("6000")
    assert worksheet.get(GROSS_COMMISSION_INCOME).value == D("1500")


def test_line_27_includes_the_professional_and_commission_nets_and_line_15000_the_total() -> None:
    worksheet = return_du()

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("8500")
    assert worksheet.get(TOTAL_INCOME).value == D("8500")


def test_a_business_statement_alone_goes_to_line_13500_and_nothing_on_the_other_lines() -> None:
    worksheet = return_du(business_statements=(BUSINESS,))

    assert worksheet.get(BUSINESS_INCOME).value == D("3000")
    assert worksheet.get(PROFESSIONAL_INCOME).value == D("0")
    assert worksheet.get(COMMISSION_INCOME).value == D("0")
    assert worksheet.get(GROSS_PROFESSIONAL_INCOME).value == D("0")
    assert worksheet.get(GROSS_COMMISSION_INCOME).value == D("0")


def test_a_professional_loss_is_negative_on_13700_and_reduces_net_self_employment_income() -> None:
    # Gross 0 less expenses of 1,000 is a loss of 1,000: line 13700 "Net" prints no floor, so it is
    # negative, and line 27 takes it in: $3,000 plus minus $1,000 plus $1,500, which is $3,500.
    loss = {"business": {"gross_sales": "0", "office_expenses": "1000"}, "business_income_line": 2}
    worksheet = return_du(business_statements=(BUSINESS, loss, COMMISSION))

    assert worksheet.get(PROFESSIONAL_INCOME).value == D("-1000")
    assert worksheet.get(GROSS_PROFESSIONAL_INCOME).value == D("0")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("3500")


def test_the_split_follows_the_code_not_the_order_of_the_statements() -> None:
    worksheet = return_du(business_statements=(COMMISSION, PROFESSIONAL, BUSINESS))

    assert worksheet.get(BUSINESS_INCOME).value == D("3000")
    assert worksheet.get(PROFESSIONAL_INCOME).value == D("4000")
    assert worksheet.get(COMMISSION_INCOME).value == D("1500")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("8500")


@pytest.mark.parametrize("code", [0, 4, 9])
def test_a_code_outside_1_to_3_is_refused_not_dropped(code: int) -> None:
    # The code names no T1 line, so the statement's $4,000 net would go to none of lines 13500,
    # 13700 or 13900 and line 27 and everything below it would leave it out, with no error shown:
    # the statement is refused instead.
    unknown = {"business": {"gross_sales": "4000"}, "business_income_line": code}

    with pytest.raises(InputOutOfRangeError, match=f"ca/business_income_line {code} is refused"):
        return_du(business_statements=(unknown,))


def test_a_code_outside_1_to_3_on_one_of_several_statements_refuses_the_return() -> None:
    unknown = {"business": {"gross_sales": "4000"}, "business_income_line": 4}

    with pytest.raises(InputOutOfRangeError, match="ca/business_income_line 4 is refused"):
        return_du(business_statements=(BUSINESS, unknown, COMMISSION))


@pytest.mark.parametrize(
    ("code", "line"), [(1, BUSINESS_INCOME), (2, PROFESSIONAL_INCOME), (3, COMMISSION_INCOME)]
)
def test_a_listed_code_is_not_refused_and_its_net_reaches_line_27(code: int, line: Any) -> None:
    statement = {"business": {"gross_sales": "4000"}, "business_income_line": code}
    worksheet = return_du(business_statements=(statement,))

    assert worksheet.get(line).value == D("4000")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("4000")


def test_a_sub_cent_amount_stays_unrounded_through_the_whole_return() -> None:
    # The form prints no rounding rule for these lines, so a net or gross of 1000.005 reaches line
    # 13700, line 27 and line 15000 as it is, not as 1000.00 or 1000.01.
    sub_cent = {"business": {"gross_sales": "1000.005"}, "business_income_line": 2}
    worksheet = return_du(business_statements=(sub_cent,))

    assert worksheet.get(PROFESSIONAL_INCOME).value == D("1000.005")
    assert worksheet.get(GROSS_PROFESSIONAL_INCOME).value == D("1000.005")
    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("1000.005")
    assert worksheet.get(TOTAL_INCOME).value == D("1000.005")
