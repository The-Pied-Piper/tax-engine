"""CA-ON 2025 end to end: return HW."""

from __future__ import annotations

import re

import pytest

from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED,
    ELIGIBLE_DEPENDANT_AMOUNT,
    SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

DEPENDANT_REFUSED = (
    "line 51100 is entered (the Canada caregiver amount for a dependant) but line 30400 is nil, "
    "and line 30425 applies only if you can claim an amount for an eligible dependant 18 years of "
    "age or older on line 30400 of your return"
)
SPOUSE_REFUSED = (
    "line 51090 is entered (the Canada caregiver amount for the spouse) but line 30300 is nil, and "
    "line 30425 applies only if you can claim an amount for your spouse or common-law partner on "
    "line 30300 of your return"
)


def return_hw(eligible_dependants: int = 1, dependant_caregiver: int = 1) -> Worksheet:
    """Employment income 60000 with the amounts of `returns/2025_return_hw.yaml` (one eligible
    dependant, 18 years of age or older, with the Canada caregiver amount for that dependant on line
    51100, nil spouse amount), with `eligible_dependants` and `dependant_caregiver` varied."""
    return compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        eligible_dependants=eligible_dependants,
        dependant_caregiver_eligible=dependant_caregiver,
        dependant_caregiver_aged_18_or_older=1,
    )


def test_return_hw_dependant_with_its_caregiver_amount_gives_18816_on_line_30400() -> None:
    worksheet = return_hw()

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("18816.00")
    assert worksheet.get(ontario.ONTARIO_TAX).value == D("2488.76")
    assert worksheet.get(DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED).value == 0


def test_return_hw_spouse_caregiver_with_the_spouse_amount_is_not_refused() -> None:
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        spouses_claimed=1,
        spouse_caregiver_eligible=1,
    )

    assert worksheet.get(SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED).value == 0


def test_return_hw_dependant_caregiver_without_the_eligible_dependant_is_refused_naming_both() -> (
    None
):
    message = "ca/dependant_caregiver_without_dependant_amount 1 is refused: " + DEPENDANT_REFUSED

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        return_hw(eligible_dependants=0, dependant_caregiver=1)


def test_return_hw_spouse_caregiver_without_the_spouse_amount_is_refused_naming_both() -> None:
    message = "ca/spouse_caregiver_without_spouse_amount 1 is refused: " + SPOUSE_REFUSED

    with pytest.raises(InputOutOfRangeError, match=re.escape(message)):
        compute(
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            spouses_claimed=0,
            spouse_caregiver_eligible=1,
        )
