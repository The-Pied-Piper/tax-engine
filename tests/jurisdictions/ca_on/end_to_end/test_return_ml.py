"""CA-ON 2025 end to end: return ml (Form T2048 line 26 carried with its sign).

Form T2048 (2025), Part 3: line 26 "Line 17 minus line 25" prints no floor, and line 27 reads
"Enter whichever is less: amount from line 7 or line 26. Enter all or part of the amount you want
to claim on line 25395 of your return." When the losses on line 25 pass line 17, the paper form
shows a negative on line 26 and on the lesser-of of line 27, and the filer claims 0.

The worked return `returns/2025_return_ml.yaml` (Return MD with net capital losses of other years
of 100,000 claimed and a claim of 0; the cases below run Return BE's Form T2048, which has the
same line 24) is checked by `test_worked_returns.py`. This module reads the
claims it does not express: a claim above 0 against the negative maximum is refused, not capped.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    QBT_CAPITAL_GAINS_DEDUCTION,
    QBT_DEDUCTION_LIMIT,
    QBT_MAXIMUM_DEDUCTION,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, form_be

LOSSES = {
    "unapplied_net_capital_losses_2001_to_2024": "110000",
    "net_capital_losses_claimed": "100000",
}


def test_lines_26_and_27_are_negative_and_the_claim_of_0_is_accepted() -> None:
    # Line 25 is 80000.00 + 4000.00 + 5500.00 = 89500.00 and line 17 is 80000.00, so line 26 is
    # 80000.00 - 89500.00 = -9500.00; line 27's lesser of 130000.00 and -9500.00 is -9500.00.
    worksheet = form_be(qbt_deduction_claimed="0", **LOSSES)

    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("-9500.00")
    assert worksheet.get(QBT_MAXIMUM_DEDUCTION).value == D("-9500.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("0")


def test_a_claim_above_0_against_the_negative_maximum_is_refused_not_capped() -> None:
    # 0.01 is above the negative maximum of -9500.00 and above 0: an input error, not lowered to 0.
    with pytest.raises(InputAboveBoundError) as raised:
        form_be(qbt_deduction_claimed="0.01", **LOSSES)

    assert str(raised.value).startswith(
        "ca/t2048, instance 1: ca/qbt_deduction_claimed 0.01 is above "
        "ca/qbt_maximum_deduction -9500.00"
    )


def test_line_26_is_not_signed_when_the_losses_do_not_pass_line_17() -> None:
    # Return BE's own losses: line 25 is 19500.00, line 26 is 60500.00 and the whole is claimed.
    worksheet = form_be()

    assert worksheet.get(QBT_DEDUCTION_LIMIT).value == D("60500.00")
    assert worksheet.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("60500")
