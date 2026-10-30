"""CA-ON 2025 end to end: return HV."""

from __future__ import annotations

import re

import pytest

from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import SPOUSE_AND_DEPENDANT_BOTH_CHECKED
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_hv(spouses_claimed: int = 0) -> Worksheet:
    """Employment income 60000 with the amounts of `returns/2025_return_hv.yaml` (one eligible
    dependant, and the spouse or common-law partner amount `spouses_claimed`, nil in the file)."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_dependants=1,
        spouses_claimed=spouses_claimed,
    )


def test_return_hv_eligible_dependant_alone_gives_ontario_tax_of_2488_76() -> None:
    worksheet = return_hv()

    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2488.76")
    assert worksheet.get(SPOUSE_AND_DEPENDANT_BOTH_CHECKED).value == 0


def test_return_hv_spouse_amount_alone_gives_the_same_ontario_tax() -> None:
    worksheet = compute("60000", (), "0", "0", "0", "0", "0", spouses_claimed=1)

    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2488.76")
    assert worksheet.get(SPOUSE_AND_DEPENDANT_BOTH_CHECKED).value == 0


def test_return_hv_with_a_spouse_amount_as_well_is_refused_not_credited_twice() -> None:
    # Schedule 5 line 30400: "If you did not claim an amount on line 30300 of your return, you may
    # be able to claim the amount for one eligible dependant". Both claimed would give Ontario tax
    # of 1942.20 (a second 10823.00 credited), so the return is refused as an input error naming
    # both.
    with pytest.raises(
        InputOutOfRangeError,
        match=re.escape(
            "ca/spouse_and_dependant_both 1 is refused: line 30300 and line 30400 are "
            "both claimed, but line 30400 applies only if you did not claim an amount on "
            "line 30300 of your return"
        ),
    ):
        return_hv(spouses_claimed=1)
