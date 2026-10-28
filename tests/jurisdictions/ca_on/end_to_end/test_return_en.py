"""CA-ON 2025 end to end: return EN, the net capital loss of Guide T4037 (Capital Gains, 2025).

Return EN is `returns/2025_return_en.yaml`: two share dispositions with chosen figures that give the
guide's gain of $450 and loss of $750. Their net, -$300, is the total capital loss on line 21; half
of it, -$150, is the net capital loss on line 24. The guide's $225 taxable gain and $375 allowable
loss net to the same $150. The other starting values are none.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    SHARE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# The T4037 example, page 31: "taxable capital gain of $225 (50% x $450) and an allowable capital
# loss of $375 (50% x $750)"; "you are left with $150 ($375 - $225) of unapplied allowable capital
# losses for 2025". The two rows are (proceeds, adjusted cost base, outlays): a gain of
# 1,450 - 1,000 = 450 and a loss of 250 - 1,000 = -750.
SECURITIES = (
    ("1450", "1000", "0"),
    ("250", "1000", "0"),
)


def return_en() -> Worksheet:
    """The worksheet of the return EN: the two security rows and the return's other starting
    values (none)."""
    result = service().compute(
        CA_ON,
        2025,
        *starting("0", SECURITIES, "0", "0", "0", "0", "0"),
    )
    (worksheet,) = result["ca-on/return"]
    return worksheet


def test_the_two_securities_net_to_a_loss_of_300_on_line_21() -> None:
    # 450 - 750 = -300, the total capital losses on line 21 (a loss in brackets).
    worksheet = return_en()

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("-300")
    assert worksheet.get(CAPITAL_GAIN).value == D("-300")


def test_the_net_capital_loss_on_line_24_is_150() -> None:
    # 50% of -300 is -150.00: the guide's "$150 ($375 - $225) of unapplied allowable capital
    # losses".
    worksheet = return_en()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("-150.00")


def test_a_net_capital_loss_is_no_taxable_capital_gain_and_no_taxable_income() -> None:
    # "While you cannot deduct the $150 from other sources of income in 2025, it becomes part of the
    # computation of your net capital loss for 2025."
    worksheet = return_en()

    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("0")
