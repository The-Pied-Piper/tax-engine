"""CA-ON 2025 end to end: return p."""

from __future__ import annotations

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace import (
    ChosenByRangeLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    NET_INCOME,
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_FOOD_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import POLITICAL_COLUMN_LINES, D, compute


def test_return_ps_political_contribution_credit_is_1402_76_and_lowers_the_refund() -> None:
    # Return P is Return I without the community food program donations and with Ontario political
    # contributions of 3000 (ON479 line 15, line 63100; the worksheet reads it as line 63110):
    # employment income of 48000, as Return I, to line 86 of 1484.56 and, with no donations, line
    # 88 of 1484.56; the health premium of 450 gives the Ontario tax 1934.56. The federal tax after
    # credits is 3909.94, so the total payable is 3909.94 + 1934.56 = 5844.50.
    # Worksheet ON479 line 16: 3000 is more than 1,666.82, so column 3 applies. Line 2 is 1,666.82,
    # line 3 is 3000 - 1,666.82 = 1,333.18, line 5 is 1,333.18 x 33.33% = 444.3494, rounded
    # half-up to the cent: 444.35, line 6 is the printed 958.41 and line 7 is 444.35 + 958.41 =
    # 1,402.76, below the maximum of 1,666.82, so ON479 line 16 is 1,402.76. (Columns 1 and 2 are
    # also built: column 1 line 7 is 75% x 3000 = 2,250.00 and column 2 line 7 is 50% x 2,499.95 =
    # 1,249.975, up to 1,249.98, + 375.03 = 1,625.01; neither applies.) Line 18 is the sum of
    # lines 1, 2, 14 and 16, 0 + 0 + 0 + 1,402.76 (no child care expenses), line 21 and T1 line
    # 47900 are 1,402.76; the total credits are 4800 + 0 + 1,402.76 = 6,202.76 and line 167 is
    # 5,844.50 - 6,202.76 = -358.26, a refund.
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        income_tax_deducted="4800",
        political_contributions="3000",
    )

    assert worksheet.get(NET_INCOME).value == D("47555.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("1484.56")
    assert worksheet.get(ONTARIO_TAX).value == D("1934.56")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5844.50")
    assert worksheet.get(ontario.POLITICAL_CONTRIBUTIONS).value == D("3000")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_3_LINE_2).value == D("1666.82")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_3_LINE_3).value == D("1333.18")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_3_LINE_5).value == D("444.35")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_3_LINE_6).value == D("958.41")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_3_LINE_7).value == D("1402.76")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_1_LINE_7).value == D("2250.00")
    assert worksheet.get(ontario.POLITICAL_CREDIT_COLUMN_2_LINE_7).value == D("1625.01")
    assert worksheet.get(ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM).value == D("1402.76")
    assert worksheet.get(ontario.POLITICAL_CREDIT).value == D("1402.76")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("1402.76")
    assert worksheet.get(ONTARIO_CREDITS).value == D("1402.76")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("1402.76")
    assert worksheet.get(TOTAL_CREDITS).value == D("6202.76")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-358.26")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "political_credit_column_3_line_3: political_contributions 3000 "
        "less political_credit_column_3_line_2 1666.82, not below 0 = 1333.18"
    ) in rendered
    assert (
        "political_credit_column_3_line_5: 33.33% of political_credit_column_3_line_3 1333.18 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "political_credit_column_3_line_7: political_credit_column_3_line_5 444.35 "
        "+ political_credit_column_3_line_6 958.41 = 1402.76"
    ) in rendered
    assert (
        "political_credit_before_maximum: political_credit_column_3_line_7 1402.76, "
        "chosen as political_contributions is 3000"
    ) in rendered
    assert (
        "political_credit: lesser of political_credit_before_maximum 1402.76 and 1666.82 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "ontario_credits_subtotal: fertility_credit 0 + care_credit 0 + seniors_care_credit 0 "
        "+ seniors_transit_credit 0 "
        "+ political_credit 1402.76 + flow_through_share_credit 0 = 1402.76"
    ) in rendered
    assert (
        "total_credits: income_tax_deducted_after_election 4800 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 0 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 0 + "
        "employee_and_partner_gst_hst_rebate 0 "
        "+ educator_school_supply_credit 0 + journalism_labour_tax_credit 0 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 0 + provincial_credits 1402.76 = 6202.76"
    ) in rendered


@pytest.mark.parametrize(
    ("contributions", "column", "credit"),
    [
        ("0", 1, "0.00"),
        ("300", 1, "225.00"),
        ("500.05", 1, "375.04"),
        ("500.06", 2, "375.04"),
        ("1000", 2, "625.01"),
        ("1666.82", 2, "958.42"),
        ("1666.83", 3, "958.41"),
        ("3000", 3, "1402.76"),
        ("3793", 3, "1666.82"),
        ("4000", 3, "1666.82"),
    ],
)
def test_the_credit_is_the_applicable_columns_line_7_at_most_1666_82(
    contributions: str, column: int, credit: str
) -> None:
    worksheet = compute(
        "48000", (), "0", "0", "8640", "0", "0", political_contributions=contributions
    )

    (picked,) = [
        line
        for line in worksheet.trace
        if isinstance(line, ChosenByRangeLine)
        and line.output == ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM
    ]
    assert picked.chosen_kind == POLITICAL_COLUMN_LINES[column][7]
    assert worksheet.get(ontario.POLITICAL_CREDIT).value == D(credit)
    assert worksheet.get(ONTARIO_CREDITS).value == D(credit)
    assert worksheet.get(PROVINCIAL_CREDITS).value == D(credit)


def test_no_contributions_leave_the_ontario_credits_at_zero() -> None:
    # The default of 0 contributions, as for Returns A to N: column 1 applies and line 16 is 0.
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(ontario.POLITICAL_CONTRIBUTIONS).value == D("0")
    assert worksheet.get(ontario.POLITICAL_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS).value == D("0")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("0")
