"""CA-ON 2025 end to end: return EM, the listed personal property of Guide T4037 (2025).

Return EM is `returns/2025_return_em.yaml`: three dispositions of listed personal property, a
jewellery gain of $200, a coin collection gain of $300 and a painting loss of $4,000, a net LPP
loss of $3,500. The tests here check the guide's figures: the loss stays on the LPP line, the net
gain is 0 and no capital gain or taxable amount results. The other starting values are none.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS,
    LISTED_PERSONAL_PROPERTY_NET_GAIN,
    SHARE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# The T4037 example, page 33: "your loss was $4,000; your total gain was $500 ($200 + $300). As a
# result, your net loss was $3,500 ($4,000 - $500)." Each row has no outlays and expenses.
LPP_ROWS = (
    ("6000", "5800", "0"),
    ("2000", "1700", "0"),
    ("8000", "12000", "0"),
)


def return_em(*share_dispositions: tuple[str, str, str]) -> Worksheet:
    """The worksheet of the return EM: the three LPP rows, with the given share rows (none by
    default) and the return's other starting values (none)."""
    result = service().compute(
        CA_ON,
        2025,
        *starting(
            "0",
            share_dispositions,
            "0",
            "0",
            "0",
            "0",
            "0",
            listed_personal_property_dispositions=LPP_ROWS,
        ),
    )
    (worksheet,) = result["ca-on/return"]
    return worksheet


def test_the_three_lpp_rows_net_to_a_loss_of_3500() -> None:
    # 200 + 300 - 4,000 = -3,500: the guide's "your net loss was $3,500".
    worksheet = return_em()

    assert worksheet.get(LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS).value == D("-3500")


def test_the_lpp_net_gain_is_0_and_no_capital_gain_or_taxable_amount_results() -> None:
    # With no LPP gain left after the loss, line 15900 is 0 and nothing is taxable.
    worksheet = return_em()

    assert worksheet.get(LISTED_PERSONAL_PROPERTY_NET_GAIN).value == D("0")
    assert worksheet.get(CAPITAL_GAIN).value == D("0")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")


def test_the_lpp_loss_does_not_offset_a_gain_on_other_property() -> None:
    # "You cannot use the difference to offset your capital gain on the sale of a property other
    # than on LPP in the year": a share gain of 1,000.00 (proceeds 1,000.00, a cost base of 0)
    # stays a gain of 1,000.00 beside the LPP loss of -3,500.
    worksheet = return_em(("1000", "0", "0"))

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("1000")
    assert worksheet.get(CAPITAL_GAIN).value == D("1000")
