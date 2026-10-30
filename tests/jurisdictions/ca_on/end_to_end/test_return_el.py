"""CA-ON 2025 end to end: return EL, the share disposition of Guide T4037 (Capital Gains, 2025).

Return EL is `returns/2025_return_el.yaml`: one disposition of 400 XYZ shares for $6,500 with a
commission of $60 and an adjusted cost base of $4,000, the guide's capital gain of $2,440 and
taxable capital gain of $1,220 on line 12700. The tests here check the guide's figures from that
one row, with the same starting values for everything else (no income).
"""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    SHARE_GAIN_OR_LOSS,
    SHARE_PROCEEDS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# The T4037 example, page 11: "Proceeds of disposition $ 6,500 A", "Adjusted cost base $ 4,000 B",
# "Outlays and expenses on disposition + $ 60 C", "Capital gain (line A minus line D) = $ 2,440 E".
XYZ_SHARES = (("6500", "4000", "60"),)


def return_el() -> Worksheet:
    """The worksheet of the return EL: the XYZ share row and the return's other starting values
    (none)."""
    result = service().compute(
        CA_ON,
        2025,
        *starting("0", XYZ_SHARES, "0", "0", "0", "0", "0"),
    )
    (worksheet,) = result["ca-on/return"]
    return worksheet


def test_the_share_row_is_the_guide_capital_gain_of_2440() -> None:
    # Column 5 is 6,500 - 4,000 - 60 = 2,440, the guide's capital gain of $2,440 (its line E).
    worksheet = return_el()

    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("2440")
    assert worksheet.get(CAPITAL_GAIN).value == D("2440")


def test_the_proceeds_of_the_row_are_6500() -> None:
    # Line 13199, "Total proceeds of disposition", is the row's proceeds of $6,500.
    worksheet = return_el()

    assert worksheet.get(SHARE_PROCEEDS).value == D("6500")


def test_half_of_the_gain_is_the_taxable_capital_gain_of_1220_on_line_12700() -> None:
    # "Fifty percent of the capital gain would be taxable and you would report $1,220 as your
    # taxable capital gain on line 12700 of your 2025 Income Tax and Benefit Return."
    worksheet = return_el()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("1220.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("1220.00")
