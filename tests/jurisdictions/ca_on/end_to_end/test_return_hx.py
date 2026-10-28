"""CA-ON 2025 end to end: return HX."""

from __future__ import annotations

import re

import pytest

from tax_calculator.domain.errors import InputOutOfRangeError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    UNDER_18_AND_AGED_18_OR_OLDER_CHECKED,
    UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

BORN_REFUSED = (
    "under 18 years of age on December 31, 2025 and born in 1960 or earlier are both entered, but "
    "a filer born in 1960 or earlier is 65 or older"
)
AGED_REFUSED = (
    "under 18 years of age on December 31, 2025 and 18 years of age or older at the end of 2025 "
    "are both entered, but a filer cannot be both"
)


def return_hx(born_in_1960_or_earlier: int = 0, aged_18_or_older: int = 0) -> Worksheet:
    """Employment income 60000 with the amounts of `returns/2025_return_hx.yaml` (under 18 on
    December 31, 2025, eligible for the disability amount), with `born_in_1960_or_earlier` and
    `aged_18_or_older` varied (both 0 in the file)."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_for_disability_amount=1,
        under_18_on_december_31=1,
        born_in_1960_or_earlier=born_in_1960_or_earlier,
        aged_18_or_older_at_end_of_2025=aged_18_or_older,
    )


def test_return_hx_under_18_alone_gives_ontario_tax_of_2211_92() -> None:
    worksheet = return_hx()

    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("1611.92")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2211.92")
    assert worksheet.get(UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED).value == 0
    assert worksheet.get(UNDER_18_AND_AGED_18_OR_OLDER_CHECKED).value == 0


def test_return_hx_under_18_with_born_in_1960_or_earlier_is_refused_not_given_the_age_amount() -> (
    None
):
    # Without the guard the Ontario age amount of 4257.25 is claimed as well and Ontario tax is
    # 1996.92 (215.00 less); the return is refused as an input error naming both instead.
    message = "ca/under_18_and_born_in_1960_or_earlier 1 is refused: " + BORN_REFUSED

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        return_hx(born_in_1960_or_earlier=1)


def test_return_hx_under_18_with_18_or_older_is_refused_naming_both() -> None:
    message = "ca/under_18_and_aged_18_or_older 1 is refused: " + AGED_REFUSED

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        return_hx(aged_18_or_older=1)
