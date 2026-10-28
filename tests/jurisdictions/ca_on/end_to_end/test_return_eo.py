"""CA-ON 2025 end to end: return EO, the T-bill of Guide T4037 (Capital Gains, 2025).

Return EO is `returns/2025_return_eo.yaml`: a T-bill bought on May 1, 2025 for $49,500 and sold on
June 13, 2025 for $49,750. The guide's interest of $241.67 is the filer's figure, entered as
investment income without a slip, and it is line 12100 of the return. The sale's net proceeds,
$49,508.33 (the price less the interest), against the cost of $49,500 give the guide's gain of
$8.33. The other starting values are none.
"""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BOND_GAIN_OR_LOSS,
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# The T4037 example, pages 20 and 21: "Minus: Interest - $241.67", "Net proceeds of disposition =
# $49,508.33", "Minus: Adjusted cost base - $49,500.00", "Capital gain = $8.33". The interest is
# 49,500 x 4.05% x 44 / 365.
T_BILL_ROWS = (("49508.33", "49500", "0"),)


def return_eo() -> Worksheet:
    """The worksheet of the return EO: the T-bill row, the filer's interest of 241.67 without a
    slip and the return's other starting values (none)."""
    result = service().compute(
        CA_ON,
        2025,
        *starting(
            "0",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            bond_dispositions=T_BILL_ROWS,
            investment_income_without_a_slip="241.67",
        ),
    )
    (worksheet,) = result["ca-on/return"]
    return worksheet


def test_the_interest_of_241_67_is_on_line_12100() -> None:
    # Federal Worksheet line 7 takes treasury bills not reported on a slip, and line 11 "Enter this
    # amount on line 12100 of your return" gives the interest of $241.67 the guide includes.
    worksheet = return_eo()

    assert worksheet.get(INTEREST_AND_OTHER_INVESTMENT_INCOME).value == D("241.67")


def test_the_t_bill_gain_is_the_guide_capital_gain_of_8_33() -> None:
    # Net proceeds 49,508.33 less the adjusted cost base 49,500.00 is the guide's capital gain of
    # $8.33.
    worksheet = return_eo()

    assert worksheet.get(BOND_GAIN_OR_LOSS).value == D("8.33")
    assert worksheet.get(CAPITAL_GAIN).value == D("8.33")


def test_half_of_the_gain_is_the_taxable_capital_gain_of_4_17_by_engine_rounding() -> None:
    # The guide prints only the $8.33 gain. Half of it is 4.165, which the engine rounds half up
    # to 4.17.
    worksheet = return_eo()

    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("4.17")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("4.17")
