"""CA-ON 2025 end to end: return ad."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.errors import NegativeArtifactError, ValidationError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    GROSS_RENTAL_INCOME,
    NET_INCOME,
    NET_RENTAL_INCOME,
    REFUND_OR_BALANCE_OWING,
    RENTAL_CCA_CLAIM,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_EXPENSES_LESS_PERSONAL_PORTION,
    RENTAL_GROSS_RENTS,
    RENTAL_NET_INCOME_AFTER_CCA,
    RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES,
    RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NET_INCOME_SHARE,
    RENTAL_NET_INCOME_WITH_RECAPTURE,
    RENTAL_NON_COMPLIANT_EXPENSES,
    RENTAL_PARTNER_AMOUNT_7,
    RENTAL_PARTNER_SHARE_WITH_REBATE,
    RENTAL_PARTNERSHIP_NET_INCOME,
    RENTAL_PERSONAL_PORTION,
    RENTAL_RECAPTURED_CCA,
    RENTAL_SHORT_TERM_PORTION,
    RENTAL_TERMINAL_LOSS,
    RENTAL_TOTAL_EXPENSES,
    SHORT_TERM_RENTAL_GROSS_RENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, rental_return

# Area A rows for a co-owner's shares of the recapture and the terminal loss and of amount ii (Form
# T776 lines 9947 and 9948 and amount ii): class 10 with a UCC of 1000.00 and proceeds of 1500.00,
# so
# column 7 is -500.00 and the recapture is 500.00; class 9 with no property left and a UCC of
# 1000.00, so the terminal loss is 1000.00; and class 1 with the claim of 2400.00 (amount ii).
RECAPTURE_ROW = ("10", "1000.00", "0", "1500.00", "0", "0", "0", 0, "0", "0", "0", "0")
TERMINAL_LOSS_ROW = ("9", "1000.00", "0", "0", "0", "0", "0", 1, "0", "0", "0", "0")
CLAIM_ROW = ("1", "100000.00", "0", "40000.00", "0", "0", "2400.00", 0, "0", "0", "0", "5000.00")

RETURN_AD_STATEMENT: dict[str, Any] = {
    "rental_properties": ((2, "0", "24000"),),
    "rental_expenses": {
        "insurance": ("1200", "0", "0"),
        "interest_and_bank_charges": ("6000", "0", "0"),
        "repairs_and_maintenance": ("1300", "0", "0"),
        "property_taxes": ("3500", "0", "0"),
    },
}


def return_ad(
    changes: Mapping[str, Any] | None = None, **overrides: Any
) -> dict[str, tuple[Worksheet, ...]]:
    """Return AD's inputs, as in `returns/2025_return_ad.yaml`: a landlord with two rental units.

    Gross rents of 24000 (one property, two units) are the only income; the expenses are the
    insurance 1200, the interest 6000, the property taxes 3500 and the repairs 1300, 12000 in all,
    with no personal or short-term portion, so line 9946 and T1 line 12600 are 12000.
    """
    return rental_return(RETURN_AD_STATEMENT, changes, **overrides)


def test_return_ads_gross_rents_are_24000_on_line_12599() -> None:
    # Form T776 Part 3: one property of two units, gross rents for all units 24000 and none for
    # short-term rentals, so line 8140 is 0 and line 8141 is 24000; with no other income (line
    # 8230) line 8299, and so T1 line 12599, is 24000.
    result = return_ad()
    statement = result["ca/t776"][0]

    assert statement.get(SHORT_TERM_RENTAL_GROSS_RENTS).value == D("0")
    assert statement.get(RENTAL_GROSS_RENTS).value == D("24000")
    assert statement.get(GROSS_RENTAL_INCOME).value == D("24000")


def test_return_ads_net_rental_income_is_12000_on_line_12600() -> None:
    # Part 4: the expenses total 1200 + 6000 + 3500 + 1300 = 12000 (line A), with no personal
    # portion (line 9949), no short-term portion (line 9365) and no Chart A rows (line 9366 is 0),
    # so line 1 is 12000 and line 9369 is 24000 - 12000 = 12000. Sole proprietor, so amount 2 is
    # line 9369; with no co-owner expenses, recapture, terminal loss or CCA, amounts 3 to 6 are
    # 12000 too, and line 9946, T1 line 12600, is amount 6.
    result = return_ad()
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_TOTAL_EXPENSES).value == D("12000")
    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("0")
    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("0")
    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("0")
    assert statement.get(RENTAL_EXPENSES_LESS_PERSONAL_PORTION).value == D("12000")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_SHARE).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("12000")
    assert statement.get(RENTAL_PARTNERSHIP_NET_INCOME).value == D("0")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("12000")


def test_return_ads_net_rental_income_is_the_only_income_on_line_15000() -> None:
    # T1 line 13 "Rental income" is line 12600 (net), not line 12599 (gross): total income is the
    # 12000, and so are net income and taxable income, below every tax threshold.
    result = return_ad()
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(TOTAL_INCOME).value == D("12000")
    assert worksheet.get(NET_INCOME).value == D("12000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("12000.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("0")


def test_return_ads_trace_names_each_line_of_the_rental_income() -> None:
    result = return_ad()
    rendered = EnglishTraceRenderer().render_all(result["ca/t776"][0].trace)

    for line in (
        "short_term_rental_gross_rents: item 1 rental_property_short_term_rents 0 = 0",
        "rental_gross_rents: item 1 rental_property_gross_rents 24000 = 24000",
        "gross_rental_income: rental_gross_rents 24000 + rental_other_income 0 = 24000",
        "rental_total_expenses: rental_advertising 0 + rental_insurance 1200 "
        "+ rental_interest_and_bank_charges 6000 + rental_office_expenses 0 "
        "+ rental_professional_fees 0 + rental_management_and_administration_fees 0 "
        "+ rental_repairs_and_maintenance 1300 + rental_salaries_wages_and_benefits 0 "
        "+ rental_property_taxes 3500 + rental_travel 0 + rental_utilities 0 "
        "+ rental_motor_vehicle_expenses 0 + rental_other_expenses 0 = 12000",
        "rental_non_compliant_expenses: no items = 0",
        "rental_expenses_less_personal_portion: rental_total_expenses 12000 "
        "less rental_personal_portion 0 = 12000",
        "rental_deductible_expenses: rental_expenses_less_personal_portion 12000 "
        "less rental_non_compliant_expenses_checked 0 = 12000",
        "rental_net_income_before_adjustments: gross_rental_income 24000 "
        "less rental_deductible_expenses 12000 = 12000",
        "rental_net_income_share: rental_net_income_before_adjustments 12000, "
        "chosen as rental_coowner_checked is 0",
        "rental_net_income_after_coowner_expenses: rental_net_income_share 12000 "
        "less rental_coowner_other_expenses 0 = 12000",
        "rental_net_income_with_recapture: rental_net_income_after_coowner_expenses 12000 "
        "+ rental_recaptured_cca 0 = 12000",
        "rental_net_income_after_terminal_loss: rental_net_income_with_recapture 12000 "
        "less rental_terminal_loss 0 = 12000",
        "rental_net_income_after_cca: rental_net_income_after_terminal_loss 12000 "
        "less rental_cca_claim 0 = 12000",
        "net_rental_income: rental_net_income_after_cca 12000, "
        "chosen as rental_partner_checked is 0",
    ):
        assert line in rendered, line
    returned = EnglishTraceRenderer().render_all(result["ca-on/return"][0].trace)
    assert "net_rental_income: item 1 net_rental_income 12000 = 12000" in returned
    total_income = [text for text in returned if text.startswith("total_income: ")]
    assert len(total_income) == 1
    assert "+ rdsp_income 0 + net_rental_income 12000 + taxable_capital_gains 0 " in total_income[0]
    assert total_income[0].endswith("= 12000")


def test_a_short_term_rental_of_900_with_30_of_90_days_non_compliant_is_300_on_line_9366() -> None:
    # Chart A: one row of related expenses 900, 30 non-compliant days of 90 short-term days:
    # 900 x 30 / 90 = 300.00. The insurance's short-term portion of 900 (line 9365) is the row's
    # column 3; line 1 is the total expenses of 1200 less line 9949 (0) less line 9366 (300.00),
    # 900.00, so line 9369 is 24000 - 900.00 = 23100.00.
    result = return_ad(
        {
            "rental_expenses": {"insurance": ("1200", "0", "900")},
            "short_term_rental_units_rows": (("900", 30, 90),),
        }
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_SHORT_TERM_PORTION).value == D("900")
    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("300.00")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("900.00")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("23100.00")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("23100.00")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_non_compliant_expenses: row 1: expenses 900 for 30 non-compliant days of 90 "
        "short-term days = 300 (half-up to 0.01)"
    ) in rendered
    assert "rental_non_compliant_expenses: item 1 300 = 300" in rendered


def test_each_chart_a_row_is_worked_on_its_own_and_added_into_line_9366() -> None:
    result = return_ad(
        {
            "rental_expenses": {"insurance": ("1200", "0", "1000")},
            "short_term_rental_units_rows": (("900", 30, 90), ("100", 2, 3)),
        }
    )
    statement = result["ca/t776"][0]

    # 300.00 + 66.67, each row rounded half-up to the cent before the total.
    assert statement.get(RENTAL_NON_COMPLIANT_EXPENSES).value == D("366.67")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert "rental_non_compliant_expenses: item 1 300 + item 2 66.67 = 366.67" in rendered


def test_a_personal_portion_comes_off_the_expenses_before_line_9366() -> None:
    # Line 1 is amount A minus line 9949 minus line 9366: 1200 - 200 = 1000, then 1000 - 0.
    result = return_ad({"rental_expenses": {"insurance": ("1200", "200", "0")}})
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_PERSONAL_PORTION).value == D("200")
    assert statement.get(RENTAL_EXPENSES_LESS_PERSONAL_PORTION).value == D("1000")
    assert statement.get(RENTAL_DEDUCTIBLE_EXPENSES).value == D("1000")


def test_other_income_on_line_8230_adds_to_line_8299_but_not_to_line_8141() -> None:
    result = return_ad({"rental_other_income": "500"})
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_GROSS_RENTS).value == D("24000")
    assert statement.get(GROSS_RENTAL_INCOME).value == D("24500")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("12500")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("12500")


def test_short_term_rents_are_not_added_to_line_8141() -> None:
    # Line 8141 adds the "Gross rents for all units" column; line 8140 the short-term column.
    result = return_ad({"rental_properties": ((2, "8000", "24000"), (1, "0", "6000"))})
    statement = result["ca/t776"][0]

    assert statement.get(SHORT_TERM_RENTAL_GROSS_RENTS).value == D("8000")
    assert statement.get(RENTAL_GROSS_RENTS).value == D("30000")
    assert statement.get(GROSS_RENTAL_INCOME).value == D("30000")


def test_a_rental_loss_of_2000_is_line_12600_of_minus_2000_and_lowers_total_income() -> None:
    # Gross rents of 10000 and expenses of 12000: line 9369 is a loss of 2000.00, kept with its
    # sign through amounts 2 to 6 and line 9946 (T1 line 12600), and added to the 50000 of
    # employment income on line 15000.
    result = return_ad(
        {
            "rental_properties": ((1, "0", "10000"),),
            "rental_expenses": {"insurance": ("12000", "0", "0")},
        },
        employment_income="50000",
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(GROSS_RENTAL_INCOME).value == D("10000")
    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-2000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("-2000")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-2000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("48000")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "net_rental_income: rental_net_income_after_cca -2000, "
        "chosen as rental_partner_checked is 0"
    ) in rendered


def test_a_rental_loss_with_no_other_income_is_a_negative_total_income() -> None:
    # Total income (line 15000) is not floored, as the form prints it: with no other income the
    # loss of 10000 - 12000 = -2000 on line 12600 is the whole of total income.
    result = return_ad(
        {
            "rental_properties": ((1, "0", "10000"),),
            "rental_expenses": {"insurance": ("12000", "0", "0")},
        }
    )
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(NET_RENTAL_INCOME).value == D("-2000")
    assert worksheet.get(TOTAL_INCOME).value == D("-2000")


def test_a_co_owners_share_replaces_line_9369_and_runs_through_amounts_3_to_6() -> None:
    # Line 2 is the co-owner's own 6000 of the 12000 (count 1); line 9945 takes 500 off (amount
    # 3 is 5500), line 9947 adds 200 (amount 4, 5700), line 9948 takes 100 off (amount 5, 5600)
    # and line 9936 takes 300 off (amount 6, 5300): line 9946 and T1 line 12600 are 5300. The
    # shares are within their wholes: the classes give a recapture of 500, a terminal loss of
    # 1000 and an amount ii of 2400, and the co-owner's shares of them are 200, 100 and 300.
    result = return_ad(
        {
            "rental_cca_classes_rows": (RECAPTURE_ROW, TERMINAL_LOSS_ROW, CLAIM_ROW),
            "rental_coowner": 1,
            "rental_coowner_share": "6000",
            "rental_coowner_other_expenses": "500",
            "rental_coowner_recaptured_cca": "200",
            "rental_coowner_terminal_loss": "100",
            "rental_coowner_cca_claim": "300",
        }
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS).value == D("12000")
    assert statement.get(RENTAL_NET_INCOME_SHARE).value == D("6000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_COOWNER_EXPENSES).value == D("5500")
    assert statement.get(RENTAL_NET_INCOME_WITH_RECAPTURE).value == D("5700")
    assert statement.get(RENTAL_NET_INCOME_AFTER_TERMINAL_LOSS).value == D("5600")
    assert statement.get(RENTAL_RECAPTURED_CCA).value == D("200")
    assert statement.get(RENTAL_TERMINAL_LOSS).value == D("100")
    assert statement.get(RENTAL_CCA_CLAIM).value == D("300")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("5300")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("5300")
    assert worksheet.get(TOTAL_INCOME).value == D("5300")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "rental_net_income_share: rental_coowner_share_checked 6000, "
        "chosen as rental_coowner_checked is 1"
    ) in rendered


def test_a_sole_proprietor_with_the_co_owners_share_keeps_amount_2_and_subtracts_9945() -> None:
    # Answer 0: amount 2 is line 9369 (12000), not the 6000 typed; line 9945 (500) is subtracted
    # as line 3 prints, so line 9946 is 11500.
    result = return_ad(
        {
            "rental_coowner": 0,
            "rental_coowner_share": "6000",
            "rental_coowner_other_expenses": "500",
        }
    )
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_SHARE).value == D("12000")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("11500")


def test_a_partners_line_9946_is_amount_7_plus_line_9974_minus_line_9943() -> None:
    # No T5013 slip: amount 7 is "your share of amount 6", 25% of 12000 = 3000; line 9974 adds 50
    # and line 9943 takes 30 off: 3000 + 50 - 30 = 3020, which replaces amount 6 (12000) on line
    # 9946.
    result = return_ad(
        {
            "rental_partner": 1,
            "rental_partner_percentage": "25",
            "rental_partner_gst_hst_rebate": "50",
            "rental_partner_other_expenses": "30",
        }
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("12000")
    assert statement.get(RENTAL_PARTNER_AMOUNT_7).value == D("3000")
    assert statement.get(RENTAL_PARTNER_SHARE_WITH_REBATE).value == D("3050")
    assert statement.get(RENTAL_PARTNERSHIP_NET_INCOME).value == D("3020")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("3020")
    assert worksheet.get(TOTAL_INCOME).value == D("3020")
    rendered = EnglishTraceRenderer().render_all(statement.trace)
    assert (
        "net_rental_income: rental_partnership_net_income 3020, "
        "chosen as rental_partner_checked is 1"
    ) in rendered


def test_a_sole_proprietor_with_the_partners_figures_keeps_amount_6_on_line_9946() -> None:
    # Answer 0: line 7 (4000), line 9974 (50) and line 9943 (30) are not in line 9946.
    result = return_ad(
        {
            "rental_partner": 0,
            "rental_partner_share": "4000",
            "rental_partner_gst_hst_rebate": "50",
            "rental_partner_other_expenses": "30",
        }
    )

    assert result["ca/t776"][0].get(RENTAL_NET_INCOME_AFTER_CCA).value == D("12000")
    assert result["ca-on/return"][0].get(NET_RENTAL_INCOME).value == D("12000")


def test_a_partners_loss_is_negative_on_line_9946() -> None:
    # No rents, so amount 6 is -12000 (the expenses); 25% of it is -3000, line 9943 takes 20 more.
    result = return_ad(
        {
            "rental_partner": 1,
            "rental_partner_percentage": "25",
            "rental_partner_other_expenses": "20",
            "rental_properties": ((2, "0", "0"),),
        },
        employment_income="50000",
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_PARTNERSHIP_NET_INCOME).value == D("-3020")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-3020")
    assert worksheet.get(TOTAL_INCOME).value == D("46980")


def test_a_co_owners_loss_is_negative_on_amount_2() -> None:
    # The property as a whole makes a loss (insurance 32000 is the only expense, against
    # rents of 24000, so line 9369 is -8000); the co-owner's share of that loss is -3000.
    result = return_ad(
        {
            "rental_coowner": 1,
            "rental_coowner_share": "-3000",
            "rental_expenses": {"insurance": ("32000", "0", "0")},
        },
        employment_income="50000",
    )
    worksheet = result["ca-on/return"][0]
    statement = result["ca/t776"][0]

    assert statement.get(RENTAL_NET_INCOME_SHARE).value == D("-3000")
    assert statement.get(RENTAL_NET_INCOME_AFTER_CCA).value == D("-3000")
    assert worksheet.get(NET_RENTAL_INCOME).value == D("-3000")


def test_a_chart_a_row_with_no_short_term_days_is_refused_naming_the_row() -> None:
    with pytest.raises(ValidationError, match="row 1: ca/short_term_rental_days cannot be 0"):
        return_ad({"short_term_rental_units_rows": (("900", 0, 0),)})


def test_a_negative_expense_box_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        return_ad({"rental_expenses": {"insurance": ("-1", "0", "0")}})
