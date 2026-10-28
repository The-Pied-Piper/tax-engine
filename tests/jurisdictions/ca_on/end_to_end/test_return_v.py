"""CA-ON 2025 end to end: return v."""

from __future__ import annotations

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace import (
    SumLine,
)
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ACWB_PAID,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    CREDITS_AGAINST_FEDERAL_TAX,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LINE_41700,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    ITC_RECAPTURE,
    ITC_RECAPTURE_AT_15_PERCENT,
    ITC_RECAPTURE_AT_20_PERCENT,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
    LABOUR_SPONSORED_FUNDS_NET_COST,
    NET_FEDERAL_TAX,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    RESP_AIPS_ADDITIONAL_TAX,
    RESP_AIPS_CONTRIBUTIONS_COUNTED,
    RESP_AIPS_LIFETIME_LIMIT,
    RESP_AIPS_LIMIT_REMAINING,
    RESP_AIPS_PART_A_APPLIES,
    RESP_AIPS_PART_A_TAX,
    RESP_AIPS_PART_B_TAX,
    RESP_AIPS_RECEIVED_PART_B,
    RESP_AIPS_REDUCTION,
    RESP_AIPS_SUBJECT_TO_TAX,
    RL_10_LABOUR_SPONSORED_FUND_AMOUNT,
    SPECIAL_TAXES,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute, return_a


def return_v(
    *,
    income_tax_deducted: str = "6929.83",
    opportunities_fund_donation: str = "100",
    itc_recapture_expenditure_at_15_percent: str = "2000",
    itc_recapture_expenditure_at_20_percent: str = "500",
    labour_sponsored_funds_net_cost: str = "4000",
    acwb_paid_to_you: str = "300",
    resp_aips_received_part_a: str = "0",
    resp_aips_rrsp_contributions: str = "0",
    resp_aips_reduction_used_in_previous_years: str = "0",
    resp_aips_received_part_b: str = "10000",
    resp_aips_part_a_applies: int = 0,
    rl_10_labour_sponsored_fund_amount: str = "150",
) -> Worksheet:
    """Return V's inputs, as in `returns/2025_return_v.yaml`: Return T's with the special lines.

    Return T's filer (employment income of 50000, the federal tax after credits of 4177.93, the
    Ontario tax of 2276.90 and the Step 6 credits of 2525.00 besides the tax deducted) with the
    recapture of an investment tax credit on 2000 at 15% and 500 at 20% (line 131, 400.00), a net
    cost of 4000 of labour-sponsored fund shares (line 41400, 600.00), the advanced Canada workers
    benefit of 0 (line 41500, from 300 in box 10 and a benefit of 0) and special taxes (line 41800)
    of 2000.00 from Form T1172 Part B on 10000 of AIPs and 150 from the RL-10 slip. The net
    federal tax (line 42000) is 6127.93, the total payable 8404.83 and, with 6929.83 deducted,
    the refund (line 48400) is 1050.00.
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
        part_xii_2_tax_credit="50",
        employee_and_partner_gst_hst_rebate="150",
        educator_supplies_expenses="1200",
        business_statements=(
            {
                "business": {
                    "journalism_labour_tax_credit": "75",
                    "partner_other_amount_a": "75",
                },
                "business_partner": 1,
            },
        ),
        tax_paid_by_instalments="2000",
        opportunities_fund_donation=opportunities_fund_donation,
        itc_recapture_expenditure_at_15_percent=itc_recapture_expenditure_at_15_percent,
        itc_recapture_expenditure_at_20_percent=itc_recapture_expenditure_at_20_percent,
        labour_sponsored_funds_net_cost=labour_sponsored_funds_net_cost,
        acwb_paid_to_you=acwb_paid_to_you,
        resp_aips_received_part_a=resp_aips_received_part_a,
        resp_aips_rrsp_contributions=resp_aips_rrsp_contributions,
        resp_aips_reduction_used_in_previous_years=resp_aips_reduction_used_in_previous_years,
        resp_aips_received_part_b=resp_aips_received_part_b,
        resp_aips_part_a_applies=resp_aips_part_a_applies,
        rl_10_labour_sponsored_fund_amount=rl_10_labour_sponsored_fund_amount,
    )


def test_return_vs_line_41400_is_600_for_a_net_cost_of_4000() -> None:
    # Line 41300 is 4000: 15% is 600.00, below the maximum of 750, so line 41400 is 600.00.
    worksheet = return_v()

    assert worksheet.get(LABOUR_SPONSORED_FUNDS_NET_COST).value == D("4000")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM).value == D("600.00")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("600.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "labour_sponsored_funds_credit_before_maximum: 15% of labour_sponsored_funds_net_cost 4000 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "labour_sponsored_funds_credit: lesser of labour_sponsored_funds_credit_before_maximum 600 "
        "and 750 (half-up to 0.01)"
    ) in rendered


def test_a_net_cost_of_6000_gives_900_capped_at_750() -> None:
    worksheet = return_v(labour_sponsored_funds_net_cost="6000")

    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM).value == D("900.00")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("750.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "labour_sponsored_funds_credit: lesser of labour_sponsored_funds_credit_before_maximum 900 "
        "and 750 (half-up to 0.01)"
    ) in rendered


@pytest.mark.parametrize(
    ("net_cost", "credit"),
    [
        ("0", "0"),
        ("4000", "600.00"),
        # 4999.90 x 15% = 749.985, a tie, rounded half-up to 749.99, below the maximum.
        ("4999.90", "749.99"),
        # 5000 x 15% is 750.00 exactly, the net cost at which the maximum starts.
        ("5000", "750.00"),
        ("5000.01", "750.00"),
        ("6000", "750.00"),
        ("100000", "750.00"),
        # 0.10 x 15% = 0.015, a tie, rounded half-up to 0.02.
        ("0.10", "0.02"),
    ],
)
def test_line_41400_is_15_percent_of_line_41300_at_most_750(net_cost: str, credit: str) -> None:
    worksheet = return_v(labour_sponsored_funds_net_cost=net_cost)

    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D(credit)


def test_return_vs_recapture_is_300_plus_100_and_adds_to_the_federal_tax_on_line_132() -> None:
    # T2038(IND) Part C: amount 1 is 2000 x 0.15 = 300.00, amount 2 is 500 x 0.20 = 100.00 and
    # amount 3, line 131, is 400.00; line 132 is line 126 (4177.93) plus it, 4577.93.
    worksheet = return_v()

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("4177.93")
    assert worksheet.get(ITC_RECAPTURE_AT_15_PERCENT).value == D("300.00")
    assert worksheet.get(ITC_RECAPTURE_AT_20_PERCENT).value == D("100.00")
    assert worksheet.get(ITC_RECAPTURE).value == D("400.00")
    assert worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value == D("4577.93")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "itc_recapture_at_15_percent: 15% of itc_recapture_expenditure_at_15_percent 2000 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "itc_recapture_at_20_percent: 20% of itc_recapture_expenditure_at_20_percent 500 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "itc_recapture: itc_recapture_at_15_percent 300 + itc_recapture_at_20_percent 100 = 400"
    ) in rendered
    assert (
        "federal_tax_with_itc_recapture: federal_tax_less_foreign_tax_credit 4177.93 "
        "+ itc_recapture 400 = 4577.93"
    ) in rendered


def test_each_recapture_rate_applies_to_its_own_expenditure() -> None:
    # Distinct figures, so an expenditure at the wrong rate changes the total: 1000 x 0.15 =
    # 150.00 and 3000 x 0.20 = 600.00, not 1000 x 0.20 + 3000 x 0.15 = 650.00.
    worksheet = return_v(
        itc_recapture_expenditure_at_15_percent="1000",
        itc_recapture_expenditure_at_20_percent="3000",
    )

    assert worksheet.get(ITC_RECAPTURE_AT_15_PERCENT).value == D("150.00")
    assert worksheet.get(ITC_RECAPTURE_AT_20_PERCENT).value == D("600.00")
    assert worksheet.get(ITC_RECAPTURE).value == D("750.00")


def test_no_expenditure_leaves_line_132_at_line_126() -> None:
    worksheet = return_v(
        itc_recapture_expenditure_at_15_percent="0", itc_recapture_expenditure_at_20_percent="0"
    )

    assert worksheet.get(ITC_RECAPTURE).value == D("0")
    assert worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value == D("4177.93")


def test_return_vs_credit_comes_off_line_132_and_line_139_is_3977_93() -> None:
    # Line 138 (41600) is line 137 (41400) alone, 600.00; line 139 (41700) is line 134, which
    # carries line 132 (4577.93), less it: 3977.93.
    worksheet = return_v()

    assert worksheet.get(CREDITS_AGAINST_FEDERAL_TAX).value == D("600.00")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("3977.93")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "credits_against_federal_tax: political_credit 0 + investment_tax_credit 0 "
        "+ labour_sponsored_funds_credit 600 = 600"
    ) in rendered
    assert (
        "federal_tax: federal_tax_with_itc_recapture 4577.93 "
        "less federal_logging_tax_credit 0, not below 0 = 4577.93"
    ) in rendered
    assert (
        "federal_tax_less_credits: federal_tax 4577.93 "
        "less credits_against_federal_tax 600, not below 0 = 3977.93"
    ) in rendered


def test_a_credit_above_the_federal_tax_with_the_recapture_leaves_zero_on_line_139() -> None:
    # Employment income of 10000 leaves the federal tax after credits at 0 (see the credit larger
    # than the tax above); a recapture of 500 x 0.20 = 100.00 makes line 132 100.00, and the
    # credit of 6000 x 15% = 900.00, at most 750.00, is more than that: line 139 is 0, not
    # -650.00, and the unused credit is lost.
    worksheet = compute(
        "10000",
        (),
        "0",
        "0",
        "1800",
        "0",
        "0",
        itc_recapture_expenditure_at_20_percent="500",
        labour_sponsored_funds_net_cost="6000",
    )

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("0")
    assert worksheet.get(ITC_RECAPTURE).value == D("100.00")
    assert worksheet.get(FEDERAL_TAX_WITH_ITC_RECAPTURE).value == D("100.00")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("750.00")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("0")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("0")


def test_return_vs_t1172_part_b_on_10000_of_aips_is_2000_on_line_13_and_line_41800() -> None:
    # Part A does not apply (the count is 0): line 13 is line 11 (10000) x 20% = 2000.00, the
    # amount for line 41800; the RL-10 amount of 150 is added: 2150.00.
    worksheet = return_v()

    assert worksheet.get(RESP_AIPS_RECEIVED_PART_B).value == D("10000")
    assert worksheet.get(RESP_AIPS_PART_B_TAX).value == D("2000.00")
    assert worksheet.get(RESP_AIPS_PART_A_APPLIES).value == 0
    assert worksheet.get(RESP_AIPS_ADDITIONAL_TAX).value == D("2000.00")
    assert worksheet.get(RL_10_LABOUR_SPONSORED_FUND_AMOUNT).value == D("150")
    assert worksheet.get(SPECIAL_TAXES).value == D("2150.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "resp_aips_part_b_tax: 20% of resp_aips_received_part_b 10000 (half-up to 0.01)"
    ) in rendered
    assert (
        "resp_aips_additional_tax: resp_aips_part_b_tax 2000, chosen as "
        "resp_aips_part_a_applies_checked "
        "is 0"
    ) in rendered
    assert (
        "special_taxes: resp_aips_additional_tax 2000 + rl_10_labour_sponsored_fund_amount 150 "
        "+ rc359_tax_total 0 = 2150"
    ) in rendered


def test_part_a_is_not_applicable_so_its_lines_are_computed_on_figures_of_0() -> None:
    # Return V enters 0 on lines 1, 2 and 5: line 3 is 0, line 4 is 50,000.00, line 6 is
    # 50,000.00 less 0, line 7 is the lesser of 0 and 50,000.00, line 8 is 0 less 0 and line 10
    # is 0.00.
    worksheet = return_v()

    assert worksheet.get(RESP_AIPS_CONTRIBUTIONS_COUNTED).value == D("0")
    assert worksheet.get(RESP_AIPS_LIFETIME_LIMIT).value == D("50000.00")
    assert worksheet.get(RESP_AIPS_LIMIT_REMAINING).value == D("50000.00")
    assert worksheet.get(RESP_AIPS_REDUCTION).value == D("0")
    assert worksheet.get(RESP_AIPS_SUBJECT_TO_TAX).value == D("0")
    assert worksheet.get(RESP_AIPS_PART_A_TAX).value == D("0.00")


def test_a_count_of_1_takes_part_a_and_line_10_for_line_41800() -> None:
    # Part A: 10000 of AIPs (line 1) and 4000 contributed to an RRSP and deducted (line 2): line
    # 3 is 4000, line 4 50,000.00, line 6 50,000.00 less the 0 used before, line 7 the lesser of
    # 4000 and 50,000.00, line 8 10000 - 4000 = 6000 and line 10 6000 x 20% = 1200.00. Part B's
    # line 11 is 0: with Part A applying, a Part B figure is refused, so Part B's 2000.00 is not
    # entered.
    worksheet = return_v(
        resp_aips_received_part_a="10000",
        resp_aips_rrsp_contributions="4000",
        resp_aips_received_part_b="0",
        resp_aips_part_a_applies=1,
    )

    assert worksheet.get(RESP_AIPS_CONTRIBUTIONS_COUNTED).value == D("4000")
    assert worksheet.get(RESP_AIPS_LIFETIME_LIMIT).value == D("50000.00")
    assert worksheet.get(RESP_AIPS_LIMIT_REMAINING).value == D("50000.00")
    assert worksheet.get(RESP_AIPS_REDUCTION).value == D("4000")
    assert worksheet.get(RESP_AIPS_SUBJECT_TO_TAX).value == D("6000")
    assert worksheet.get(RESP_AIPS_PART_A_TAX).value == D("1200.00")
    assert worksheet.get(RESP_AIPS_PART_B_TAX).value == D("0.00")
    assert worksheet.get(RESP_AIPS_ADDITIONAL_TAX).value == D("1200.00")
    assert worksheet.get(SPECIAL_TAXES).value == D("1350.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "resp_aips_contributions_counted: lesser of resp_aips_received_part_a 10000 "
        "and resp_aips_rrsp_contributions 4000 = 4000"
    ) in rendered
    assert (
        "resp_aips_reduction: lesser of resp_aips_contributions_counted 4000 "
        "and resp_aips_limit_remaining 50000 = 4000"
    ) in rendered
    assert (
        "resp_aips_subject_to_tax: resp_aips_received_part_a 10000 less resp_aips_reduction 4000 "
        "= 6000"
    ) in rendered
    assert (
        "resp_aips_part_a_tax: 20% of resp_aips_subject_to_tax 6000 (half-up to 0.01)"
    ) in rendered
    assert (
        "resp_aips_additional_tax: resp_aips_part_a_tax 1200, chosen as "
        "resp_aips_part_a_applies_checked "
        "is 1"
    ) in rendered


@pytest.mark.parametrize(
    ("aips", "contributions", "used_before", "reduction", "subject", "tax"),
    [
        # Contributions below the AIPs and the room: the contributions reduce the AIPs.
        ("10000", "4000", "0", "4000", "6000", "1200.00"),
        # No contributions: nothing reduces the AIPs, all of them are taxed.
        ("10000", "0", "0", "0", "10000", "2000.00"),
        # Contributions above the AIPs: line 3 is the AIPs, so the whole amount is reduced.
        ("10000", "12000", "0", "10000", "0", "0.00"),
        # 48,000 of the lifetime limit used before leaves 2,000 of room, below the contributions.
        ("10000", "4000", "48000", "2000", "8000", "1600.00"),
        # The whole 50,000.00 used before leaves no room: line 6 is 0.
        ("10000", "4000", "50000", "0", "10000", "2000.00"),
        # Room of exactly the contributions: either line gives the same line 7.
        ("10000", "4000", "46000", "4000", "6000", "1200.00"),
    ],
)
def test_part_a_reduces_the_aips_by_the_lesser_of_the_contributions_and_the_lifetime_room(
    aips: str, contributions: str, used_before: str, reduction: str, subject: str, tax: str
) -> None:
    worksheet = return_v(
        resp_aips_received_part_a=aips,
        resp_aips_rrsp_contributions=contributions,
        resp_aips_reduction_used_in_previous_years=used_before,
        resp_aips_received_part_b="0",
        resp_aips_part_a_applies=1,
    )

    assert worksheet.get(RESP_AIPS_REDUCTION).value == D(reduction)
    assert worksheet.get(RESP_AIPS_SUBJECT_TO_TAX).value == D(subject)
    assert worksheet.get(RESP_AIPS_PART_A_TAX).value == D(tax)
    assert worksheet.get(RESP_AIPS_ADDITIONAL_TAX).value == D(tax)


def test_line_6_may_be_negative_as_the_form_prints_no_floor() -> None:
    # T1172 line 6 "Line 4 minus line 5" prints no "(if negative, enter "0")": 60,000 used before
    # gives -10,000.00, and line 7, the lesser of 4000 and that, is -10000.00, as the form prints:
    # line 8 is 10000 less that, 20000.00, and line 10 is 20% of it, 4000.00.
    worksheet = return_v(
        resp_aips_received_part_a="10000",
        resp_aips_rrsp_contributions="4000",
        resp_aips_reduction_used_in_previous_years="60000",
        resp_aips_received_part_b="0",
        resp_aips_part_a_applies=1,
        opportunities_fund_donation="0",
    )

    assert worksheet.get(RESP_AIPS_LIMIT_REMAINING).value == D("-10000.00")
    assert worksheet.get(RESP_AIPS_REDUCTION).value == D("-10000.00")
    assert worksheet.get(RESP_AIPS_SUBJECT_TO_TAX).value == D("20000.00")
    assert worksheet.get(RESP_AIPS_PART_A_TAX).value == D("4000.00")


@pytest.mark.parametrize(
    ("part_a_applies", "aips", "contributions", "part_b", "additional"),
    [
        # Part A applies: its figures give 1200.00 and Part B's line 11 is 0, as a Part B figure
        # is refused then.
        (1, "10000", "4000", "0", "1200.00"),
        # Part A does not apply: Part A's figures are 0, and Part B's line 11 gives 2000.00.
        (0, "0", "0", "10000", "2000.00"),
    ],
)
def test_only_the_chosen_part_is_the_additional_tax(
    part_a_applies: int, aips: str, contributions: str, part_b: str, additional: str
) -> None:
    # The count picks the part: the figures of the part that does not apply are entered as 0.
    worksheet = return_v(
        resp_aips_received_part_a=aips,
        resp_aips_rrsp_contributions=contributions,
        resp_aips_received_part_b=part_b,
        resp_aips_part_a_applies=part_a_applies,
    )

    assert worksheet.get(RESP_AIPS_PART_A_TAX).value == D("1200.00" if part_a_applies else "0.00")
    assert worksheet.get(RESP_AIPS_PART_B_TAX).value == D("0.00" if part_a_applies else "2000.00")
    assert worksheet.get(RESP_AIPS_ADDITIONAL_TAX).value == D(additional)


@pytest.mark.parametrize(
    ("aips", "tax"),
    [
        ("10000", "2000.00"),
        ("0", "0"),
        # 0.02 x 20% = 0.004, rounded half-up to 0.00; 0.03 x 20% = 0.006, to 0.01.
        ("0.02", "0.00"),
        ("0.03", "0.01"),
    ],
)
def test_line_13_is_20_percent_of_line_11(aips: str, tax: str) -> None:
    worksheet = return_v(resp_aips_received_part_b=aips)

    assert worksheet.get(RESP_AIPS_PART_B_TAX).value == D(tax)


def test_return_vs_net_federal_tax_adds_t1206_line_30_and_line_41800_in_that_order() -> None:
    # Box 10 of 300 is not charged back: Schedule 6 line 49 is the lesser of line 43 (0, the benefit
    # is 0 at 50000) and line 48 (300), so line 41500 is 0. Form T1206 Part 2 line 29 is 3977.93
    # (139) + 0 (140) = 3977.93, which is more than line 24 (0.00), so line 30 is 3977.93; adding
    # line 41800, 2150.00 (141), gives 6127.93.
    worksheet = return_v()

    assert worksheet.get(ACWB_PAID).value == D("300")
    assert worksheet.get(ADVANCED_CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("6127.93")
    (line,) = [
        line
        for line in worksheet.trace
        if isinstance(line, SumLine) and line.output == NET_FEDERAL_TAX
    ]
    assert line.parts == (
        (SPLIT_INCOME_LINE_30, D("3977.93")),
        (SPECIAL_TAXES, D("2150.00")),
    )
    assert worksheet.get(SPLIT_INCOME_LINE_24).value == D("0.00")
    (line_29,) = [
        line
        for line in worksheet.trace
        if isinstance(line, SumLine) and line.output == SPLIT_INCOME_LINE_29
    ]
    assert line_29.parts == (
        (FEDERAL_TAX_LINE_41700, D("3977.93")),
        (ADVANCED_CANADA_WORKERS_BENEFIT, D("0")),
    )
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "split_income_line_29: federal_tax_line_41700 3977.93 "
        "+ advanced_canada_workers_benefit 0 = 3977.93"
    ) in rendered
    assert (
        "net_federal_tax: split_income_line_30 3977.93 + special_taxes 2150 = 6127.93"
    ) in rendered


def test_each_line_between_126_and_142_enters_the_net_federal_tax_once() -> None:
    # Distinct figures for each line, so a line left out or added twice changes the total: 4177.93
    # (126) + 3 x 0.15 = 0.45 (131 from 3) - 0.15 x 100 = 15.00 (137 from 100) + 0 (140) + 20% of
    # 100 = 20.00 (141, Part B) + 7 (141, RL-10) = 4190.38.
    worksheet = return_v(
        itc_recapture_expenditure_at_15_percent="3",
        itc_recapture_expenditure_at_20_percent="0",
        labour_sponsored_funds_net_cost="100",
        resp_aips_received_part_b="100",
        rl_10_labour_sponsored_fund_amount="7",
    )

    assert worksheet.get(ITC_RECAPTURE).value == D("0.45")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("15.00")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("4163.38")
    assert worksheet.get(SPECIAL_TAXES).value == D("27.00")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("4190.38")


def test_return_vs_total_payable_is_8404_83_and_the_refund_is_1050() -> None:
    # Line 148 is 6127.93 + 2276.90 = 8404.83; the total credits are the 6929.83 deducted plus
    # 2525.00 of the Step 6 credits, 9454.83; line 167 is 8404.83 - 9454.83 = -1050.00, a refund
    # of 1050.00, of which 100 is donated: the net refund is 950.00.
    worksheet = return_v()

    assert worksheet.get(ONTARIO_TAX).value == D("2276.90")
    assert worksheet.get(TOTAL_PAYABLE).value == D("8404.83")
    assert worksheet.get(TOTAL_CREDITS).value == D("9454.83")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1050.00")
    assert worksheet.get(REFUND).value == D("1050.00")
    assert worksheet.get(ontario.NET_REFUND).value == D("950.00")


def test_the_special_and_credit_lines_do_not_change_a_return_that_does_not_take_them() -> None:
    # Return A's balance owing is unchanged: 25897.15 less 25000 with every new line 0.
    worksheet = return_a()

    assert worksheet.get(ITC_RECAPTURE).value == D("0")
    assert worksheet.get(LABOUR_SPONSORED_FUNDS_CREDIT).value == D("0")
    assert worksheet.get(SPECIAL_TAXES).value == D("0")
    assert worksheet.get(FEDERAL_TAX_LESS_CREDITS).value == D("16951.38")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("16951.38")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("897.15")
