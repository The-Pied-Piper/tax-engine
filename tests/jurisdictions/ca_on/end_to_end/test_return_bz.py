"""CA-ON 2025 end to end: return bz (Form T2048 for two QBTs, notes (1) to (3), line 25395)."""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import (
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    DEDUCTIONS_FROM_NET_INCOME,
    QBT_ABIL_REDUCTION,
    QBT_ALLOCATION_TOTAL,
    QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER,
    QBT_AMOUNT_ALLOCATED,
    QBT_CAPITAL_GAINS_DEDUCTION,
    QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER,
    QBT_DEDUCTION_AVAILABLE,
    QBT_DEDUCTION_LIMIT,
    QBT_EARLIER_ABIL_REDUCTION_TOTAL,
    QBT_EARLIER_ALLOCATION_TOTAL,
    QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL,
    QBT_ELECTION_DEDUCTION,
    QBT_MAXIMUM_DEDUCTION,
    QBT_NET_INVESTMENT_LOSS,
    QBT_NET_INVESTMENT_LOSS_REDUCTION,
    QBT_REDUCTION_AMOUNT,
    QBT_TAXABLE_AMOUNT_ALLOCATED,
    QBT_TAXABLE_CAPITAL_GAINS,
    QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER,
    QBT_TAXABLE_GAINS_LIMIT,
    QBT_TAXABLE_GAINS_NOT_LIMITED,
    QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    QBT_TOTAL_CAPITAL_GAINS,
    QCC_ELECTION_DEDUCTION,
    QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, form_bz, return_bz, run_bz


def test_the_return_has_taxable_capital_gains_of_350000_and_one_form_for_each_qbt() -> None:
    # Capital gains of 700000 on Schedule 3, half taxable: line 12700 is 350000.00. The return
    # keeps its line 12700 whatever the form does with it.
    runs = run_bz()

    assert len(runs["ca/t2048"]) == 2
    assert return_bz().get(TAXABLE_CAPITAL_GAINS).value == D("350000.00")
    assert form_bz(1).get(TAXABLE_CAPITAL_GAINS).value == D("350000.00")
    assert form_bz(2).get(TAXABLE_CAPITAL_GAINS).value == D("350000.00")


def test_disposition_1_part_2_gives_line_7_of_500000() -> None:
    # Line 3 is 1000000 x 100% = 1000000.00; line 4 is 50%, so line 5 is 500000.00; line 6 is 0,
    # so line 7 is 500000.00.
    worksheet = form_bz(1)

    assert worksheet.get(QBT_AMOUNT_ALLOCATED).value == D("1000000.00")
    assert worksheet.get(QBT_TAXABLE_AMOUNT_ALLOCATED).value == D("500000.00")
    assert worksheet.get(QBT_DEDUCTION_AVAILABLE).value == D("500000.00")


def test_disposition_1_part_3_has_no_earlier_amount_and_gives_line_27_of_300000() -> None:
    # Note (1): no earlier disposition, so line 8 is line 12700, 350000.00. Line 14 is 600000 and
    # line 16 is 300000.00; line 17 is the lesser of 350000.00 and 300000.00: 300000.00. Line 21
    # is 350000.00 - 300000.00 = 50000.00; line 22 is 0. Line 23 and line 24 are 0, so line 25 is
    # 0 and line 26 is 300000.00; the lesser of line 7 (500000.00) and line 26 is 300000.00,
    # claimed in full.
    worksheet = form_bz(1)

    assert worksheet.get(QBT_EARLIER_ALLOCATION_TOTAL).value == D("0")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER).value == D("350000.00")
    assert worksheet.get(QBT_TOTAL_CAPITAL_GAINS).value == D("600000")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("300000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_LIMIT).value == D("300000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_NOT_LIMITED).value == D("50000.00")
    assert worksheet.get(QBT_EARLIER_ABIL_REDUCTION_TOTAL).value == D("0")
    assert worksheet.get(QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER).value == D("0")
    assert worksheet.get(QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL).value == D("0")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER).value == D("0")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS).value == D("0")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("300000.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("300000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("300000")


def test_disposition_1_part_4_gives_line_32_of_300000() -> None:
    # Line 28 is the lesser of line 7 and line 17: 300000.00; line 30 is 300000.00 - 300000 =
    # 0.00; line 32 is 0.00 + 300000 = 300000.00; lines 41 and 42 are 0.
    worksheet = form_bz(1)

    assert worksheet.get(QBT_REDUCTION_AMOUNT).value == D("0")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("300000.00")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("0")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("0")


def test_disposition_2_note_1_takes_300000_from_line_8_so_line_8_is_50000() -> None:
    # Part 2: line 3 is 400000 x 100% = 400000.00, line 5 is 200000.00 and line 7 is 200000.00.
    # Note (1): line 8 is 350000.00 - 300000.00 (line 32 of disposition 1) = 50000.00.
    worksheet = form_bz(2)

    assert worksheet.get(QBT_DEDUCTION_AVAILABLE).value == D("200000.00")
    assert worksheet.get(QBT_EARLIER_ALLOCATION_TOTAL).value == D("300000.00")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER).value == D("50000.00")


def test_disposition_2_gives_line_17_and_line_27_of_50000_not_100000() -> None:
    # Line 14 is 200000 and line 16 is 100000.00; line 17 is the lesser of line 8 (50000.00) and
    # line 16: 50000.00 (100000.00 without note (1), as line 8 would be 350000.00). Line 21 is
    # 50000.00 - 50000.00 = 0.00; line 26 is 50000.00 and the lesser of line 7 (200000.00) and
    # line 26 is 50000.00, claimed in full.
    worksheet = form_bz(2)

    assert worksheet.get(QBT_TOTAL_CAPITAL_GAINS).value == D("200000")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("100000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_LIMIT).value == D("50000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_NOT_LIMITED).value == D("0")
    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("50000.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("50000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("50000")


def test_disposition_2_part_4_and_notes_2_and_3_leave_lines_23_24_41_and_42_at_0() -> None:
    # Line 28 is the lesser of line 7 and line 17: 50000.00; line 30 is 0.00; line 32 is
    # 50000.00. Notes (2) and (3) subtract the earlier lines 41 and 42 (0.00 each) from the ABIL
    # (0.00) and Chart A line 20 (0.00).
    worksheet = form_bz(2)

    assert worksheet.get(QBT_REDUCTION_AMOUNT).value == D("0")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("50000.00")
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("0")
    assert worksheet.get(QBT_EARLIER_ABIL_REDUCTION_TOTAL).value == D("0")
    assert worksheet.get(QBT_ALLOWABLE_BUSINESS_INVESTMENT_LOSS_AFTER_EARLIER).value == D("0")
    assert worksheet.get(QBT_EARLIER_NET_INVESTMENT_LOSS_REDUCTION_TOTAL).value == D("0")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS_AFTER_EARLIER).value == D("0")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("0")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("0")


def test_part_5_adds_the_columns_into_the_totals_17212_17213_17215_and_17216() -> None:
    # B (17212) is line 7 of each QBT: 500000.00 + 200000.00 = 700000.00, and A (17211) is 0.00;
    # C (17213) is line 16: 300000.00 + 100000.00 = 400000.00; D (17215) is lines 31 and 36:
    # (300000 + 0.00) + (50000 + 0.00) = 350000.00; E (17216), for gains that are not QSBCS or
    # QFFP, is 0; F and G (17217 and 17218) are 0.00.
    worksheet = return_bz()

    assert worksheet.get(QCC_ELECTION_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_ELECTION_DEDUCTION).value == D("700000.00")
    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS).value == D("400000.00")
    assert worksheet.get(QBT_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("350000.00")
    assert worksheet.get(QSBCS_QFFP_TAXABLE_GAINS_RELATED_TO_DEDUCTION).value == D("0")
    assert worksheet.get(QBT_ABIL_REDUCTION).value == D("0")
    assert worksheet.get(QBT_NET_INVESTMENT_LOSS_REDUCTION).value == D("0")
    assert worksheet.get(QBT_ALLOCATION_TOTAL).value == D("350000.00")


def test_line_25395_is_350000_and_the_taxable_income_is_0() -> None:
    # Line 25395 is the sum of the two claims, 300000 + 50000 = 350000; the net income is the
    # taxable capital gains, 350000.00, and line 25700 is 350000.00, so line 26000 is 0.
    worksheet = return_bz()

    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("350000")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("350000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("0")


def test_without_note_1_the_second_disposition_would_claim_100000() -> None:
    # The same second disposition alone (the first one not listed): line 8 is 350000.00, line 17
    # is the lesser of 350000.00 and 100000.00: 100000.00, line 26 is 100000.00 and line 27 can be
    # 100000.00, twice what it can be after the first.
    worksheet = form_bz(
        1,
        t2048_dispositions_rows=(
            {
                "qbt_election_eligible_amount": "400000",
                "qbt_percentage_allocated": "100",
                "qbt_capital_gains": "200000",
                "qbt_election_is_qbt": 1,
                "qbt_deduction_claimed": "100000",
            },
        ),
    )

    assert worksheet.get(QBT_TAXABLE_CAPITAL_GAINS_AFTER_EARLIER).value == D("350000.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("100000.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("100000")


def test_a_second_claim_above_the_most_that_can_be_claimed_after_note_1_is_refused() -> None:
    # Line 27 for disposition 2 is at most 50000.00: 50000.01 is an input error, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        run_bz(
            t2048_dispositions_rows=(
                {
                    "qbt_election_eligible_amount": "1000000",
                    "qbt_percentage_allocated": "100",
                    "qbt_capital_gains": "600000",
                    "qbt_election_is_qbt": 1,
                    "qbt_deduction_claimed": "300000",
                },
                {
                    "qbt_election_eligible_amount": "400000",
                    "qbt_percentage_allocated": "100",
                    "qbt_capital_gains": "200000",
                    "qbt_election_is_qbt": 1,
                    "qbt_deduction_claimed": "50000.01",
                },
            )
        )

    assert str(raised.value).startswith(
        "ca/t2048, instance 2: "
        "ca/qbt_deduction_claimed 50000.01 is above ca/qbt_maximum_deduction 50000"
    )
