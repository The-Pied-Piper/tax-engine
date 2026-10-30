"""CA-ON 2025 end to end: return be (Form T2048, line 25395)."""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import (
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    DEDUCTIONS_FROM_NET_INCOME,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    QBT_ABIL_AND_NET_INVESTMENT_LOSS,
    QBT_ABIL_REDUCTION,
    QBT_ALLOCATION_LIMIT,
    QBT_ALLOCATION_TOTAL,
    QBT_AMOUNT_ALLOCATED,
    QBT_CAPITAL_GAINS_DEDUCTION,
    QBT_CAPITAL_GAINS_WITH_2024_RESERVE,
    QBT_CHART_A_NET_CAPITAL_LOSSES_USED,
    QBT_CHART_A_NET_INVESTMENT_LOSS,
    QBT_DEDUCTION_AVAILABLE,
    QBT_DEDUCTION_BASE,
    QBT_DEDUCTION_LIMIT,
    QBT_DIVIDENDS_AND_INVESTMENT_INCOME,
    QBT_ELECTION_DEDUCTION,
    QBT_EXPLORATION_EXPENSES_AT_HALF,
    QBT_INVESTMENT_EXPENSES,
    QBT_INVESTMENT_INCOME,
    QBT_MAXIMUM_DEDUCTION,
    QBT_NET_CAPITAL_LOSSES_REMAINING,
    QBT_NET_INVESTMENT_LOSS,
    QBT_NET_INVESTMENT_LOSS_REDUCTION,
    QBT_NET_RENTAL_INCOME,
    QBT_NET_RENTAL_LOSS,
    QBT_RECOVERY_OF_EXPLORATION_EXPENSES,
    QBT_REDUCTION_AMOUNT,
    QBT_REDUCTIONS_FROM_LOSSES,
    QBT_TAXABLE_AMOUNT_ALLOCATED,
    QBT_TAXABLE_CAPITAL_GAINS,
    QBT_TAXABLE_GAINS_LIMIT,
    QBT_TAXABLE_GAINS_NOT_LIMITED,
    QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    QBT_TOTAL_CAPITAL_GAINS,
    QCC_ELECTION_DEDUCTION,
    QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, form_be, return_be, run


def test_part_2_gives_line_7_of_130000_from_a_600000_election_at_50_percent() -> None:
    # Line 3 is 600000 x 50% = 300000.00; line 4 is 50%, so line 5 is 150000.00; line 6 is 20000,
    # so line 7 is 150000.00 - 20000 = 130000.00.
    worksheet = form_be()

    assert worksheet.get(QBT_AMOUNT_ALLOCATED).value == D("300000.00")
    assert worksheet.get(QBT_TAXABLE_AMOUNT_ALLOCATED).value == D("150000.00")
    assert worksheet.get(QBT_DEDUCTION_AVAILABLE).value == D("130000.00")


def test_part_3_gives_line_17_of_80000_and_line_22_of_10000() -> None:
    # Line 8 is the taxable capital gains, 100000.00. Line 11 is 180000 + 20000 = 200000; line
    # 14 is 200000 - 40000 = 160000; line 16 is 160000 x 50% = 80000.00; line 17 is the lesser of
    # line 8 and line 16, 80000.00. Line 18 is 30000 (line 25300): line 21 is 100000.00 -
    # 80000.00 = 20000.00 and line 22 is 30000 - 20000.00 = 10000.00.
    worksheet = form_be()

    assert return_be().get(TAXABLE_CAPITAL_GAINS).value == D("100000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_WITH_2024_RESERVE).value == D("200000")
    assert worksheet.get(QBT_TOTAL_CAPITAL_GAINS).value == D("160000")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("80000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_LIMIT).value == D("80000.00")
    assert return_be().get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("30000")
    assert worksheet.get(QBT_TAXABLE_GAINS_NOT_LIMITED).value == D("20000.00")
    assert worksheet.get(QBT_NET_CAPITAL_LOSSES_REMAINING).value == D("10000.00")


def test_chart_a_gives_a_net_investment_loss_of_5500_on_line_24() -> None:
    # Investment expenses (line 10): 5000 (line 22100) + 0 (net rental losses) + 2000 + 0 (line
    # 25100) + 50% of 6000 = 3000.00 + 1000 + line 9, 30000 - 10000.00 = 20000.00: 31000.00.
    # Investment income (line 19): 0.00 + 4000 (lines 12000 and 12100) + 0 + 0 + 500 + 50% of
    # 2000 = 1000.00 + line 18, 100000.00 - 80000.00 = 20000.00: 25500.00. Line 20 is 31000.00 -
    # 25500.00 = 5500.00, and the filer has investment expenses in 2025, so line 24 is 5500.00.
    worksheet = form_be()

    assert worksheet.get(QBT_NET_RENTAL_INCOME).value == D("0")
    assert worksheet.get(QBT_NET_RENTAL_LOSS).value == D("0")
    assert worksheet.get(QBT_EXPLORATION_EXPENSES_AT_HALF).value == D("3000.00")
    assert worksheet.get(QBT_CHART_A_NET_CAPITAL_LOSSES_USED).value == D("20000.00")
    assert worksheet.get(QBT_INVESTMENT_EXPENSES).value == D("31000.00")
    assert worksheet.get(QBT_DIVIDENDS_AND_INVESTMENT_INCOME).value == D("4000.00")
    assert worksheet.get(QBT_RECOVERY_OF_EXPLORATION_EXPENSES).value == D("1000.00")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("25500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("5500.00")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS).value == D("5500.00")


def test_line_26_limits_line_27_to_60500_and_line_25395_is_the_claim() -> None:
    # Line 25 is 10000.00 + 4000.00 + 5500.00 = 19500.00; line 26 is 80000.00 - 19500.00 =
    # 60500.00, less than line 7 (130000.00), so the most that can be claimed is 60500.00; the
    # filer claims it all. Line 25700 adds line 25300 (30000) and line 25395 (60500): 90500.00;
    # taxable income is net income 150435.00 - 90500.00 = 59935.00.
    worksheet = form_be()

    assert return_be().get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("4000.00")
    assert worksheet.get(QBT_REDUCTIONS_FROM_LOSSES).value == D("19500.00")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("60500.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("60500.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("60500")
    assert return_be().get(DEDUCTIONS_FROM_NET_INCOME).value == D("90500.00")
    assert return_be().get(TAXABLE_INCOME).value == D("59935.00")


def test_part_4_allocates_the_whole_abil_and_net_investment_loss() -> None:
    # Line 28 is the lesser of line 7 (130000.00) and line 17 (80000.00): 80000.00; line 30 is
    # 80000.00 - 60500 = 19500.00; line 32 is 19500.00 + 60500 = 80000.00. Line 35 is 4000.00 +
    # 5500.00 = 9500.00; line 36 is the lesser of line 30 and line 35: 9500.00. Line 39 is 9500.00
    # / 9500.00 = 1, so line 41 is 4000.00 x 1 = 4000.00 and line 42 is 9500.00 - 4000.00 =
    # 5500.00.
    worksheet = form_be()

    assert worksheet.get(QBT_DEDUCTION_BASE).value == D("80000.00")
    assert worksheet.get(QBT_REDUCTION_AMOUNT).value == D("19500.00")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("80000.00")
    assert worksheet.get(QBT_ABIL_AND_NET_INVESTMENT_LOSS).value == D("9500.00")
    assert worksheet.get(QBT_ALLOCATION_LIMIT).value == D("9500.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("4000.00")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("5500.00")


def test_part_5_reports_a_qbt_of_qsbcs_shares() -> None:
    # B (17212) is line 7, 130000.00, for a QBT and A (17211) is 0.00; C (17213) is line 16,
    # 80000.00; D (17215) is line 31 + line 36 = 60500 + 9500.00 = 70000.00 and, for QSBCS
    # shares, so is E (17216); F (17217) is line 41 and G (17218) is line 42.
    worksheet = form_be()

    assert worksheet.get(QBT_ELECTION_DEDUCTION).value == D("130000.00")
    assert worksheet.get(QCC_ELECTION_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("80000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("70000.00")
    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("70000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("4000.00")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("5500.00")


def test_line_7_limits_line_27_and_a_partial_claim_reduces_the_abil_by_a_ratio() -> None:
    # Prior claims of 120000 leave line 7 at 150000.00 - 120000 = 30000.00, below line 26
    # (60500.00), so the most that can be claimed is 30000.00; the filer claims 25000. Line 28 is
    # the lesser of line 7 and line 17: 30000.00; line 30 is 30000.00 - 25000 = 5000.00; line 32
    # is 5000.00 + 25000 = 30000.00. Line 35 is 9500.00 and line 36 is the lesser of 5000.00 and
    # 9500.00: 5000.00. Line 39 is 5000.00 / 9500.00 and line 41 is 4000.00 x 5000.00 / 9500.00 =
    # 2105.2631..., 2105.26 half-up to the cent; line 42 is 5000.00 - 2105.26 = 2894.74. D is
    # 25000 + 5000.00 = 30000.00 and so is E; B is line 7, 30000.00. Line 25700 is 30000 + 25000.
    worksheet = form_be(qbt_prior_years_claims="120000", qbt_deduction_claimed="25000")

    assert worksheet.get(QBT_DEDUCTION_AVAILABLE).value == D("30000.00")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("60500.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("30000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("25000")
    assert worksheet.get(QBT_DEDUCTION_BASE).value == D("30000.00")
    assert worksheet.get(QBT_REDUCTION_AMOUNT).value == D("5000.00")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("30000.00")
    assert worksheet.get(QBT_ALLOCATION_LIMIT).value == D("5000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("2105.26")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("2894.74")
    assert worksheet.get(QBT_ELECTION_DEDUCTION).value == D("30000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("30000.00")
    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("30000.00")
    assert return_be(qbt_prior_years_claims="120000", qbt_deduction_claimed="25000").get(
        DEDUCTIONS_FROM_NET_INCOME
    ).value == D("55000")


def test_a_qcc_election_of_other_shares_reports_on_a_and_not_on_b_or_e() -> None:
    # The election is for a QCC and the gains are not from QSBCS or QFFP shares: A (17211) is
    # line 7, 130000.00, B (17212) is 0.00 and E (17216) is 0.00; D (17215) is unchanged,
    # 70000.00.
    worksheet = form_be(qbt_election_is_qbt=0, qbt_gains_are_qsbcs_or_qffp=0)

    assert worksheet.get(QCC_ELECTION_DEDUCTION).value == D("130000.00")
    assert worksheet.get(QBT_ELECTION_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("70000.00")
    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("0")


def test_without_investment_expenses_line_24_is_0_whatever_chart_a_would_give() -> None:
    # "Otherwise, enter 0": line 24 is 0; line 25 is 10000.00 + 4000.00 + 0 = 14000.00 and line 26
    # is 80000.00 - 14000.00 = 66000.00, so the most that can be claimed is 66000.00. Line 35 is
    # 4000.00 + 0 = 4000.00; line 36 is the lesser of line 30 (80000.00 - 60500 = 19500.00) and
    # 4000.00: 4000.00; line 41 is 4000.00 x 4000.00 / 4000.00 = 4000.00 and line 42 is 0.00.
    worksheet = form_be(has_investment_expenses=0)

    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("5500.00")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS).value == D("0")
    assert worksheet.get(QBT_REDUCTIONS_FROM_LOSSES).value == D("14000.00")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("66000.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("66000.00")
    assert worksheet.get(QBT_ABIL_AND_NET_INVESTMENT_LOSS).value == D("4000.00")
    assert worksheet.get(QBT_ALLOCATION_LIMIT).value == D("4000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("4000.00")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("0")


def test_a_net_rental_loss_is_chart_a_line_2_and_not_line_12() -> None:
    # One property with rents of 1000 and insurance of 3500: net rental income (line 12600) is
    # -2500. Chart A line 2 is 2500 and line 12 is 0; line 10 is 31000.00 + 2500 = 33500.00 and
    # line 19 is still 25500.00, so line 20 is 8000.00. Line 25 is 10000.00 + 4000.00 + 8000.00 =
    # 22000.00 and line 26 is 80000.00 - 22000.00 = 58000.00; the filer claims 58000.
    worksheet = form_be(
        rental_statements=(
            {
                "rental_properties": ((1, "0", "1000"),),
                "rental_expenses": {"insurance": ("3500", "0", "0")},
            },
        ),
        qbt_deduction_claimed="58000",
    )

    assert worksheet.get(QBT_NET_RENTAL_LOSS).value == D("2500")
    assert worksheet.get(QBT_NET_RENTAL_INCOME).value == D("0")
    assert worksheet.get(QBT_INVESTMENT_EXPENSES).value == D("33500.00")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("25500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("8000.00")
    assert worksheet.get(QBT_REDUCTIONS_FROM_LOSSES).value == D("22000.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("58000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("58000")


def test_net_rental_income_is_chart_a_line_12_and_not_line_2() -> None:
    # One property with rents of 3000 and no expenses: net rental income is 3000. Chart A line 12
    # is 3000 and line 2 is 0; line 19 is 25500.00 + 3000 = 28500.00 and line 20 is 31000.00 -
    # 28500.00 = 2500.00. Line 25 is 10000.00 + 4000.00 + 2500.00 = 16500.00 and line 26 is
    # 80000.00 - 16500.00 = 63500.00; the filer claims 63500.
    worksheet = form_be(
        rental_statements=({"rental_properties": ((1, "0", "3000"),)},),
        qbt_deduction_claimed="63500",
    )

    assert worksheet.get(QBT_NET_RENTAL_INCOME).value == D("3000")
    assert worksheet.get(QBT_NET_RENTAL_LOSS).value == D("0")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("28500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("2500.00")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("63500.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("63500")


def test_a_claim_above_the_most_that_can_be_claimed_is_refused_naming_both_kinds() -> None:
    # Line 27 "Enter whichever is less: amount from line 7 or line 26. Enter all or part of the
    # amount you want to claim": 60500.01 against 60500.00 is an input error, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        form_be(qbt_deduction_claimed="60500.01")

    assert str(raised.value).startswith(
        "ca/t2048, instance 1: "
        "ca/qbt_deduction_claimed 60500.01 is above ca/qbt_maximum_deduction 60500"
    )


def test_a_return_with_no_qbt_has_every_t2048_line_at_zero() -> None:
    # Returns A to AY enter nothing on Form T2048: every input is 0, so line 25395 is 0 and Part
    # 4's lines 41 and 42 are 0 (line 36 is 0, "enter 0 on lines 41 and 42"), though line 35 is 0.
    runs = run(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        income_tax_deducted="8000",
        t2048_dispositions_rows=(),
    )
    # No disposition, so no Form T2048 worksheet: the return's nine exported totals are 0.
    assert runs.get("ca/t2048", ()) == ()
    worksheet = runs["ca-on/return"][0]

    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("0")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("0")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("0")
    assert worksheet.get(QBT_ELECTION_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("0")
    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("0")
    assert worksheet.get(QCC_ELECTION_DEDUCTION).value == D("0")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")
