"""CA-ON 2025 end to end: return g."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.jurisdictions.ca.catalog import (
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    CARE_CREDIT,
    FERTILITY_CREDIT,
    FERTILITY_CREDIT_BEFORE_MAXIMUM,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    SENIORS_TRANSIT_AMOUNT_PAID_CHECKED,
    SENIORS_TRANSIT_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, return_f_with_credits


def test_return_gs_ontario_credits_are_7730_and_lower_the_refund_by_that_much() -> None:
    # Return G is Return F with fertility expenses of 24000 and 1200 paid for seniors' transit.
    # ON479 line 1: 24000 x 25% = 6000.00, at most 5000: 5000. Line 14: 1200, at most 3000, x 15%
    # = 180.00. Line 2 is Return F's care credit of 2550.00. Line 18 is 5000 + 2550.00 + 180.00 =
    # 7730.00, line 19 carries it, line 21 and T1 line 47900 are 7730.00; the total credits are
    # 8000 + 0 + 7730.00 = 15730.00 and line 167 is 4240.69 - 15730.00 = -11489.31, Return F's
    # -6309.31 less 5180.00.
    without = return_f_with_credits("0", "0")
    worksheet = return_f_with_credits("24000", "1200")

    assert worksheet.get(FERTILITY_CREDIT_BEFORE_MAXIMUM).value == D("6000.00")
    assert worksheet.get(FERTILITY_CREDIT).value == D("5000")
    assert worksheet.get(SENIORS_TRANSIT_AMOUNT_PAID_CHECKED).value == D("1200")
    assert worksheet.get(SENIORS_TRANSIT_CREDIT).value == D("180.00")
    assert worksheet.get(CARE_CREDIT).value == D("2550.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("7730.00")
    assert worksheet.get(ONTARIO_CREDITS).value == D("7730.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("7730.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4240.69")
    assert worksheet.get(TOTAL_CREDITS).value == D("15730.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-11489.31")
    assert without.get(PROVINCIAL_CREDITS).value == D("2550.00")
    assert without.get(REFUND_OR_BALANCE_OWING).value == D("-6309.31")
    assert without.get(REFUND_OR_BALANCE_OWING).value - worksheet.get(
        REFUND_OR_BALANCE_OWING
    ).value == D("5180.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "fertility_credit_before_maximum: 25% of fertility_expenses 24000 (half-up to 0.01)"
    ) in rendered
    assert (
        "fertility_credit: lesser of fertility_credit_before_maximum 6000 and 5000 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "seniors_transit_amount_paid_checked: seniors_transit_paid 1200, at most "
        "seniors_transit_maximum 3000"
    ) in rendered
    assert (
        "seniors_transit_credit: 15% of seniors_transit_amount_paid_checked 1200 (half-up to 0.01)"
    ) in rendered
    assert (
        "ontario_credits_subtotal: fertility_credit 5000 + care_credit 2550 "
        "+ seniors_care_credit 0 + seniors_transit_credit 180 "
        "+ political_credit 0 + flow_through_share_credit 0 = 7730"
    ) in rendered
    assert (
        "ontario_credits: ontario_credits_subtotal 7730 + coop_education_credit 0 = 7730"
    ) in rendered
    assert "provincial_credits: ontario_credits 7730 = 7730" in rendered
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
        "+ tax_paid_by_instalments 0 + provincial_credits 7730 = 15730"
    ) in rendered
    assert (
        "refund_or_balance_owing: total_payable 4240.69 less total_credits 15730 = -11489.31"
    ) in rendered
