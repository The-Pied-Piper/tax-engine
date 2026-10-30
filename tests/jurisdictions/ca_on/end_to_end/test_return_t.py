"""CA-ON 2025 end to end: return t."""

from __future__ import annotations

import re

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.trace import (
    SumLine,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CANADA_TRAINING_CREDIT,
    CANADA_WORKERS_BENEFIT,
    CPP_OVERPAYMENT,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EDUCATOR_SUPPLIES_EXPENSES,
    EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
    EI_OVERPAYMENT,
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    FUEL_CHARGE_CREDIT_FARMERS_TOTAL,
    INCOME_TAX_DEDUCTED,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    INVESTMENT_TAX_CREDIT_REFUND,
    JOURNALISM_LABOUR_TAX_CREDIT,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
    PART_XII_2_TAX_CREDIT,
    PROVINCIAL_CREDITS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    TAX_PAID_BY_INSTALMENTS,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, return_a


def return_t(
    *,
    income_tax_deducted: str = "4929.83",
    part_xii_2_tax_credit: str = "50",
    employee_and_partner_gst_hst_rebate: str = "150",
    educator_supplies_expenses: str = "1200",
    journalism_labour_tax_credit: str = "75",
    tax_paid_by_instalments: str = "2000",
    opportunities_fund_donation: str = "100",
) -> Worksheet:
    """Return T's inputs, as in `returns/2025_return_t.yaml`: Return C's with the Step 6 lines.

    Employment income of 50000 gives a total payable of 6454.83 and no Canada workers benefit. The
    Part XII.2 credit (45600) is 50, the GST/HST rebate (45700) 150, the supplies paid (46800)
    1200, the instalments (47600) 2000 and the journalism labour credit (47555) 75, which is the
    amount 5B of one T2125 statement whose other amounts deductible (9943) are 75 too, so it adds
    no net income; the income tax deducted (43700) of 4929.83 makes the refund (48400) 1000.00, of
    which 100 is donated (46500).
    """
    return compute(
        "50000",
        (),
        "0",
        "0",
        "9000",
        "0",
        "0",
        income_tax_deducted=income_tax_deducted,
        part_xii_2_tax_credit=part_xii_2_tax_credit,
        employee_and_partner_gst_hst_rebate=employee_and_partner_gst_hst_rebate,
        educator_supplies_expenses=educator_supplies_expenses,
        business_statements=(
            {
                "business": {
                    "journalism_labour_tax_credit": journalism_labour_tax_credit,
                    "partner_other_amount_a": journalism_labour_tax_credit,
                },
                "business_partner": 1,
            },
        ),
        tax_paid_by_instalments=tax_paid_by_instalments,
        opportunities_fund_donation=opportunities_fund_donation,
    )


def test_return_ts_lines_46800_and_46900_are_1000_and_250() -> None:
    # Line 46800, the supplies paid, is 1200: it counts as 1000, the maximum, and line 46900 is
    # 1000 x 25% = 250.00.
    worksheet = return_t()

    assert worksheet.get(EDUCATOR_SUPPLIES_EXPENSES).value == D("1200")
    assert worksheet.get(EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM).value == D("1000")
    assert worksheet.get(EDUCATOR_SCHOOL_SUPPLY_CREDIT).value == D("250.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "educator_supplies_expenses_at_most_maximum: lesser of educator_supplies_expenses 1200 "
        "and 1000 (half-up to 0.01)"
    ) in rendered
    assert (
        "educator_school_supply_credit: 25% of educator_supplies_expenses_at_most_maximum 1000 "
        "(half-up to 0.01)"
    ) in rendered


def test_return_ts_total_credits_add_lines_150_to_165_in_line_order() -> None:
    # 4929.83 (43700) + 0 (45300, the benefit) + 50 (45600) + 150 (45700) + 250.00 (46900) + 75
    # (47555) + 2000 (47600) + 0 (47900) = 7454.83: 2525 more than the tax deducted, the added
    # credits being 50 + 150 + 250 + 75 + 2000.
    worksheet = return_t()

    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("0")
    assert worksheet.get(TOTAL_CREDITS).value == D("7454.83")
    assert worksheet.get(TOTAL_CREDITS).value - worksheet.get(INCOME_TAX_DEDUCTED).value == D(
        "2525.00"
    )
    (line,) = [
        line
        for line in worksheet.trace
        if isinstance(line, SumLine) and line.output == TOTAL_CREDITS
    ]
    assert line.parts == (
        (INCOME_TAX_DEDUCTED_AFTER_ELECTION, D("4929.83")),
        (CPP_OVERPAYMENT, D("0")),
        (EI_OVERPAYMENT, D("0")),
        (REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT, D("0.00")),
        (CANADA_WORKERS_BENEFIT, D("0")),
        (CANADA_TRAINING_CREDIT, D("0")),
        (MULTIGENERATIONAL_HOME_RENOVATION_CREDIT, D("0.00")),
        (INVESTMENT_TAX_CREDIT_REFUND, D("0.00")),
        (PART_XII_2_TAX_CREDIT, D("50")),
        (EMPLOYEE_AND_PARTNER_GST_HST_REBATE, D("150")),
        (EDUCATOR_SCHOOL_SUPPLY_CREDIT, D("250.00")),
        (JOURNALISM_LABOUR_TAX_CREDIT, D("75")),
        (FUEL_CHARGE_CREDIT_FARMERS_TOTAL, D("0")),
        (TAX_PAID_BY_INSTALMENTS, D("2000")),
        (PROVINCIAL_CREDITS, D("0")),
    )
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "total_credits: income_tax_deducted_after_election 4929.83 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 0 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 50 + "
        "employee_and_partner_gst_hst_rebate 150 "
        "+ educator_school_supply_credit 250 + journalism_labour_tax_credit 75 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 2000 + provincial_credits 0 = 7454.83"
    ) in rendered


def test_return_ts_refund_is_1000_and_the_net_refund_after_a_donation_of_100_is_900() -> None:
    # Line 167 is 6454.83 - 7454.83 = -1000.00, negative so a refund, entered on line 48400 as a
    # positive 1000.00; the opportunities fund page's line 1 is that, line 2 (46500) is 100 and
    # line 3 (46600) is 900.00.
    worksheet = return_t()

    assert worksheet.get(TOTAL_PAYABLE).value == D("6454.83")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1000.00")
    assert worksheet.get(REFUND).value == D("1000.00")
    assert worksheet.get(ontario.REFUND_BEFORE_DONATION).value == D("1000.00")
    assert worksheet.get(ontario.OPPORTUNITIES_FUND_DONATION).value == D("100")
    assert worksheet.get(ontario.NET_REFUND).value == D("900.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "refund: total_credits 7454.83 less total_payable 6454.83, not below 0 = 1000"
    ) in rendered
    assert "refund_before_donation: refund 1000 = 1000" in rendered
    assert (
        "opportunities_fund_donation_checked: opportunities_fund_donation 100, "
        "at most refund_before_donation 1000"
    ) in rendered
    assert (
        "net_refund: refund_before_donation 1000 less opportunities_fund_donation_checked 100 = 900"
    ) in rendered


def test_a_balance_owing_gives_a_refund_of_zero_and_a_net_refund_of_zero() -> None:
    # Return T with 3929.82 deducted, 0.01 short of the total payable once the 2525.00 of other
    # credits are added: line 167 is +0.01 (line 48500), so line 48400 is 0
    # and the page's line 1 is 0; with no donation line 3 is 0.
    worksheet = return_t(income_tax_deducted="3929.82", opportunities_fund_donation="0")

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0.01")
    assert worksheet.get(REFUND).value == D("0")
    assert worksheet.get(ontario.REFUND_BEFORE_DONATION).value == D("0")
    assert worksheet.get(ontario.NET_REFUND).value == D("0")


def test_total_credits_equal_to_the_total_payable_give_a_refund_of_zero() -> None:
    worksheet = return_t(income_tax_deducted="3929.83", opportunities_fund_donation="0")

    assert worksheet.get(TOTAL_CREDITS).value == D("6454.83")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0.00")
    assert worksheet.get(REFUND).value == D("0")


def test_donating_the_whole_refund_leaves_a_net_refund_of_zero() -> None:
    worksheet = return_t(opportunities_fund_donation="1000.00")

    assert worksheet.get(ontario.NET_REFUND).value == D("0.00")


@pytest.mark.parametrize("donation", ["0", "1000"])
def test_a_donation_of_0_or_all_of_the_refund_is_accepted_and_checked_as_given(
    donation: str,
) -> None:
    # Line 2 and line 46500 "donate some or all of your 2025 tax refund": 0 and the whole refund of
    # 1000.00 are both at most line 1, so the checked amount is the donation as given and line 3 is
    # 1000.00 less it.
    worksheet = return_t(opportunities_fund_donation=donation)

    assert worksheet.get(ontario.OPPORTUNITIES_FUND_DONATION_CHECKED).value == D(donation)
    assert worksheet.get(ontario.NET_REFUND).value == D("1000.00") - D(donation)


@pytest.mark.parametrize("donation", ["1000.01", "10000"])
def test_a_donation_above_the_refund_is_refused_as_an_input_error_naming_both_kinds(
    donation: str,
) -> None:
    # Line 2 and line 46500 above line 1 "Amount from line 48400 above" (1000.00): refused, not
    # capped and not left to give a negative net refund. The message names the donation and the
    # refund before it.
    message = (
        f"ca-on/opportunities_fund_donation {donation} is above "
        "ca-on/refund_before_donation 1000.00"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message) + "$"):
        return_t(opportunities_fund_donation=donation)


def test_a_balance_owing_refuses_a_donation_of_100_as_above_a_refund_of_0() -> None:
    # Return T with 3929.82 deducted: the balance owing is 0.01, so line 48400 is 0 and a donation
    # of 100 is above it. Refused, not capped to 0.
    message = "ca-on/opportunities_fund_donation 100 is above ca-on/refund_before_donation 0"

    with pytest.raises(InputAboveBoundError, match=re.escape(message) + "$"):
        return_t(income_tax_deducted="3929.82", opportunities_fund_donation="100")


def test_a_balance_owing_accepts_a_donation_of_0_as_the_checked_amount() -> None:
    worksheet = return_t(income_tax_deducted="3929.82", opportunities_fund_donation="0")

    assert worksheet.get(ontario.OPPORTUNITIES_FUND_DONATION_CHECKED).value == D("0")
    assert worksheet.get(ontario.NET_REFUND).value == D("0")


def test_each_credit_line_enters_the_total_credits_once() -> None:
    # Distinct figures for each line, so a line left out or added twice changes the total:
    # 1 (43700) + 2 (45600) + 4 (45700) + 200.00 (46900, 25% of the 800 paid) + 8 (47555) + 16
    # (47600) = 231.00.
    worksheet = return_t(
        income_tax_deducted="1",
        part_xii_2_tax_credit="2",
        employee_and_partner_gst_hst_rebate="4",
        educator_supplies_expenses="800",
        journalism_labour_tax_credit="8",
        tax_paid_by_instalments="16",
        opportunities_fund_donation="0",
    )

    assert worksheet.get(EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM).value == D("800")
    assert worksheet.get(EDUCATOR_SCHOOL_SUPPLY_CREDIT).value == D("200.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("231.00")


@pytest.mark.parametrize(
    ("supplies_paid", "credit"),
    [
        ("0", "0"),
        ("800", "200.00"),
        ("1000", "250.00"),
        ("1000.01", "250.00"),
        ("1200", "250.00"),
        ("100000", "250.00"),
        # 0.02 x 25% = 0.005, a tie, rounded half-up to 0.01.
        ("0.02", "0.01"),
    ],
)
def test_line_46900_is_25_percent_of_line_46800_at_most_1000(
    supplies_paid: str, credit: str
) -> None:
    worksheet = return_t(educator_supplies_expenses=supplies_paid)

    assert worksheet.get(EDUCATOR_SCHOOL_SUPPLY_CREDIT).value == D(credit)


def test_the_new_lines_do_not_change_a_return_that_does_not_take_them() -> None:
    # Return A's balance owing is unchanged: 25897.15 less 25000 with every new line 0.
    worksheet = return_a()

    assert worksheet.get(TOTAL_CREDITS).value == D("25000")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("897.15")
    assert worksheet.get(REFUND).value == D("0")
    assert worksheet.get(ontario.NET_REFUND).value == D("0")
