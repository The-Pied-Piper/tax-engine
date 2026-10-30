"""CA-ON 2025 end to end: return FF, the Schedule 11 carry-forward and transfer chain.

Return FF is `returns/2025_return_ff.yaml`: a single student with employment income of 20000 and
income tax deducted of 1000 (both chosen figures), whose tax is too small to use the tuition. The
inputs that matter are Canadian tuition fees of 9000, a tuition amount of 3000 elected to be
transferred (`tuition_transfer_elected`) and 2 months enrolled full time
(`tuition_full_time_months`). So Schedule 11 shows the unused federal tuition, the amount
available to transfer, the amount transferred and the amount carried forward, which no other
worked return reaches. The figures are chosen (no CRA example exists) and worked out by hand from
the form text, as the description of the return shows. The tests check the hand figure of each
line; the engine's tax figures are checked in the YAML only.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CURRENT_YEAR_TUITION_CLAIMED,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TUITION_AMOUNT,
    REFUND_OR_BALANCE_OWING,
    TUITION_AVAILABLE_TO_TRANSFER,
    TUITION_CARRIED_FORWARD,
    TUITION_FULL_TIME_MONTHS,
    TUITION_INCOME_LESS_CREDITS,
    TUITION_TRANSFER_LIMIT,
    TUITION_TRANSFERRED,
    UNUSED_FEDERAL_TUITION,
    UNUSED_TUITION_CLAIMED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ff(tuition_transfer_elected: str = "3000") -> Worksheet:
    """Return FF's inputs, as in `returns/2025_return_ff.yaml`.

    The filer is a single student with employment income of 20000 and income tax deducted of 1000,
    with Canadian tuition fees of 9000 and no Canada training credit or foreign fees. They elect to
    transfer `tuition_transfer_elected` (3000) to a designated individual and were enrolled full
    time for 2 months. The CPP, EI and residence inputs are the ones `starting(...)` gives for that
    employment income.
    """
    return compute(
        employment_income="20000",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        income_tax_deducted="1000",
        canadian_tuition_fees="9000",
        canadian_tuition_institutions=1,
        tuition_transfer_elected=tuition_transfer_elected,
        tuition_full_time_months=2,
    )


def test_the_federal_tuition_amount_is_1090_25_on_line_17() -> None:
    # Line 13 is taxable income 19835.00 - T1 line 101 18744.75 = 1090.25. Line 14 is the lesser of
    # line 9 (0) and line 13: 0.00. Line 16 is the lesser of line 8 (9000.00) and line 15 (1090.25):
    # 1090.25. Line 17 is line 14 + line 16 = 0.00 + 1090.25 = 1090.25 (line 32300).
    worksheet = return_ff()

    assert worksheet.get(TUITION_INCOME_LESS_CREDITS).value == D("1090.25")
    assert worksheet.get(UNUSED_TUITION_CLAIMED).value == D("0.00")
    assert worksheet.get(CURRENT_YEAR_TUITION_CLAIMED).value == D("1090.25")
    assert worksheet.get(FEDERAL_TUITION_AMOUNT).value == D("1090.25")


def test_the_unused_federal_tuition_is_7909_75_on_line_20() -> None:
    # Line 18 is line 10, 9000.00. Line 19 is line 17, 1090.25. Line 20 is the total unused federal
    # tuition amount: 9000.00 - 1090.25 = 7909.75.
    worksheet = return_ff()

    assert worksheet.get(UNUSED_FEDERAL_TUITION).value == D("7909.75")


def test_the_amount_available_to_transfer_is_3909_75_after_the_5000_limit() -> None:
    # Line 21 is the lesser of line 8 (9000.00) and the maximum of 5000: 5000.00. Line 22 is line
    # 16, 1090.25. Line 23 is the amount available to transfer: 5000.00 - 1090.25 = 3909.75.
    worksheet = return_ff()

    assert worksheet.get(TUITION_TRANSFER_LIMIT).value == D("5000.00")
    assert worksheet.get(TUITION_AVAILABLE_TO_TRANSFER).value == D("3909.75")


def test_3000_is_transferred_and_4909_75_is_carried_forward() -> None:
    # Line 24 and line 32700: the amount elected to transfer, 3000.00, at most line 23 (3909.75).
    # Line 25 is the amount carried forward to a future year: line 20 minus line 24, that is
    # 7909.75 - 3000.00 = 4909.75.
    worksheet = return_ff()

    assert worksheet.get(TUITION_TRANSFERRED).value == D("3000.00")
    assert worksheet.get(TUITION_CARRIED_FORWARD).value == D("4909.75")


def test_the_student_was_enrolled_full_time_for_2_months() -> None:
    # Line 32020: the number of months enrolled full time, 2 (box 25 of the T2202, at most 12). It
    # is carried as entered, with no arithmetic.
    worksheet = return_ff()

    assert worksheet.get(TUITION_FULL_TIME_MONTHS).value == 2


def test_the_federal_tax_after_credits_is_zero_as_the_tuition_amount_uses_the_tax() -> None:
    # Line 33500 is the credit amounts 18744.75 + 1090.25 = 19835.00, and line 33800 is 19835.00 x
    # 14.5% = 2876.075, rounded half-up to 2876.08, which is the federal tax on taxable income. So
    # the federal tax after credits is 2876.08 - 2876.08 = 0.00.
    worksheet = return_ff()

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("0.00")


def test_the_net_refund_is_2633_00_as_the_credits_are_1000_and_1633() -> None:
    # The total credits are the income tax deducted 1000 plus the Canada workers benefit 1633.00,
    # that is 2633.00. The total payable is 0.00 (Federal tax after credits is 0.00 and the Ontario
    # tax is cleared by the Ontario credits). So the refund or balance owing is 0.00 - 2633.00 =
    # -2633.00, a refund of 2633.00.
    worksheet = return_ff()

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2633.00")


def test_a_transfer_over_line_23_is_refused() -> None:
    # Line 24 "cannot be more than the amount on line 23": line 23 is 3909.75 here, so the largest
    # transfer is 3909.75 and 3909.76 is an input above its bound.
    assert return_ff(tuition_transfer_elected="3909.75").get(TUITION_TRANSFERRED).value == D(
        "3909.75"
    )
    with pytest.raises(InputAboveBoundError, match="ca/tuition_transfer_elected"):
        return_ff(tuition_transfer_elected="3909.76")
