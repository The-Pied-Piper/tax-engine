"""CA-ON 2025 end to end: return m."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace import (
    RecordTotalLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    FERTILITY_CREDIT,
    FLOW_THROUGH_SHARE_CREDIT,
    FLOW_THROUGH_SHARE_EXPENSES,
    FLOW_THROUGH_SHARE_SLIP_EXPENSES,
    FLOW_THROUGH_SHARE_SLIPS,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    ONTARIO_TAX,
    SENIORS_TRANSIT_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, return_f_with_credits, slips


def test_return_ms_flow_through_share_credit_is_500_and_lowers_the_refund_by_that_much() -> None:
    # Return M is Return G with two Form T1221 slips, of 6000 and 4000 (two corporations). T1221
    # line 4 is 6000 + 4000 = 10000, entered on ON479 line 17 and line 63220, x 5% = 500.00. Line
    # 18 is 5000 + 2550.00 + 180.00 + 500.00 = 8230.00, line 19 carries it, line 21 and T1 line
    # 47900 are 8230.00; the total credits are 8000 + 0 + 8230.00 = 16230.00 and line 167 is
    # 4240.69 - 16230.00 = -11989.31, Return G's -11489.31 less 500.00.
    return_g = return_f_with_credits("24000", "1200")
    worksheet = return_f_with_credits("24000", "1200", ("6000", "4000"))

    assert worksheet.get(FLOW_THROUGH_SHARE_SLIPS) == slips("6000", "4000")
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("10000")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("500.00")
    assert worksheet.get(FERTILITY_CREDIT).value == D("5000")
    assert worksheet.get(SENIORS_TRANSIT_CREDIT).value == D("180.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("8230.00")
    assert worksheet.get(ONTARIO_CREDITS).value == D("8230.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("8230.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4240.69")
    assert worksheet.get(TOTAL_CREDITS).value == D("16230.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-11989.31")
    assert return_g.get(FLOW_THROUGH_SHARE_CREDIT).value == D("0")
    assert return_g.get(REFUND_OR_BALANCE_OWING).value == D("-11489.31")
    assert return_g.get(REFUND_OR_BALANCE_OWING).value - worksheet.get(
        REFUND_OR_BALANCE_OWING
    ).value == D("500.00")
    (total,) = [
        line
        for line in worksheet.trace
        if isinstance(line, RecordTotalLine) and line.output == FLOW_THROUGH_SHARE_EXPENSES
    ]
    assert total == RecordTotalLine(
        FLOW_THROUGH_SHARE_EXPENSES,
        FLOW_THROUGH_SHARE_SLIP_EXPENSES,
        (D("6000"), D("4000")),
        D("10000"),
    )
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "flow_through_share_expenses: item 1 flow_through_share_slip_expenses 6000 "
        "+ item 2 flow_through_share_slip_expenses 4000 = 10000"
    ) in rendered
    assert (
        "flow_through_share_credit: 5% of flow_through_share_expenses_claimed 10000 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "ontario_credits_subtotal: fertility_credit 5000 + care_credit 2550 "
        "+ seniors_care_credit 0 + seniors_transit_credit 180 "
        "+ political_credit 0 + flow_through_share_credit 500 = 8230"
    ) in rendered
    assert (
        "ontario_credits: ontario_credits_subtotal 8230 + coop_education_credit 0 = 8230"
    ) in rendered
    assert "provincial_credits: ontario_credits 8230 = 8230" in rendered
    assert (
        "total_credits: income_tax_deducted_after_election 8000 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 0 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 0 + "
        "employee_and_partner_gst_hst_rebate 0 "
        "+ educator_school_supply_credit 0 + journalism_labour_tax_credit 0 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 0 + provincial_credits 8230 = 16230"
    ) in rendered
    assert (
        "refund_or_balance_owing: total_payable 4240.69 less total_credits 16230 = -11989.31"
    ) in rendered


def test_no_slips_leave_the_flow_through_share_credit_at_zero() -> None:
    worksheet = return_f_with_credits("0", "0")

    assert worksheet.get(FLOW_THROUGH_SHARE_SLIPS) == slips()
    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("0")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS).value == D("2550.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6309.31")
    assert "flow_through_share_expenses: no items = 0" in EnglishTraceRenderer().render_all(
        worksheet.trace
    )


def test_a_single_slip_gives_its_own_5_percent_as_the_only_ontario_credit() -> None:
    # T1221 line 4 is the one slip, 6000; ON479 line 17 is 6000 x 5% = 300.00 with no lines 1
    # or 14, and line 2 is Return F's care credit of 2550.00, so lines 18 and 21 and T1 line 47900
    # are 2550.00 + 300.00 = 2850.00.
    worksheet = return_f_with_credits("0", "0", ("6000",))

    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("6000")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("300.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("2850.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("2850.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6609.31")
    assert "flow_through_share_expenses: item 1 flow_through_share_slip_expenses 6000 = 6000" in (
        EnglishTraceRenderer().render_all(worksheet.trace)
    )


def test_each_slip_is_an_item_named_by_its_position_and_added_before_the_rate() -> None:
    # Four slips, one of them 0: 1000.10 + 0 + 2000.20 + 3000.30 = 6000.60, x 5% = 300.03 exactly.
    worksheet = return_f_with_credits("0", "0", ("1000.10", "0", "2000.20", "3000.30"))

    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("6000.60")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("300.03")
    assert (
        "flow_through_share_expenses: item 1 flow_through_share_slip_expenses 1000.1 "
        "+ item 2 flow_through_share_slip_expenses 0 "
        "+ item 3 flow_through_share_slip_expenses 2000.2 "
        "+ item 4 flow_through_share_slip_expenses 3000.3 = 6000.6"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_the_5_percent_is_applied_once_to_the_total_not_to_each_slip() -> None:
    # Two slips of 0.10: the total 0.20 x 5% = 0.01 exactly. Rounding each slip's 0.005 half-up
    # (0.01 each) would give 0.02.
    worksheet = return_f_with_credits("0", "0", ("0.10", "0.10"))

    assert worksheet.get(FLOW_THROUGH_SHARE_EXPENSES).value == D("0.20")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("0.01")


def test_the_flow_through_share_credit_is_not_limited_by_the_tax() -> None:
    # ON479 is a refundable-credits form: line 17 is not taken off the Ontario tax. Slips of
    # 200000 give 200000 x 5% = 10000.00, far above Return F's Ontario tax of 1786.52, and it is
    # added to the credits whole with the care credit of 2550.00: 12550.00.
    worksheet = return_f_with_credits("0", "0", ("200000",))

    assert worksheet.get(ONTARIO_TAX).value == D("1786.52")
    assert worksheet.get(FLOW_THROUGH_SHARE_CREDIT).value == D("10000.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("12550.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("20550.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-16309.31")
