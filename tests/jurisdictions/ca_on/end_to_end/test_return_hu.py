"""CA-ON 2025 end to end: return hu."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputOutOfRangeError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
    REFUND_OR_BALANCE_OWING,
    SEARCH_AND_RESCUE_CONDITIONS_MET,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
    VOLUNTEER_FIREFIGHTERS_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

CONFLICT = "ca/emergency_services_volunteer_conflict 1 is refused"


def return_hu(
    *,
    exempt_income: str = "0",
    volunteer_firefighters: int = 0,
    search_and_rescue: int = 0,
) -> Worksheet:
    """Return HU's inputs, as in `returns/2025_return_hu.yaml`, over the keyword inputs given.

    The filer is Return Y's: a single parent with 60,000 of employment income, and no volunteer
    claim unless one is given. `exempt_income` is the box 87 exemption on line 10105 (0 when the
    line is absent), `volunteer_firefighters` and `search_and_rescue` the two condition flags.
    """
    base = starting(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
        emergency_services_volunteer_exempt_income=exempt_income,
    )
    flags: list[Artifact[Any]] = [
        Artifact(VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET, volunteer_firefighters),
        Artifact(SEARCH_AND_RESCUE_CONDITIONS_MET, search_and_rescue),
    ]
    given = {artifact.kind for artifact in flags}
    rest = [artifact for artifact in base if artifact.kind not in given]
    return service().compute(CA_ON, 2025, *rest, *flags)["ca-on/return"][0]


# --- the $1,000 exemption on line 10105 alone, and the VFA or SRVA alone ---------------------


def test_return_hu_the_exemption_alone_is_accepted_and_changes_no_tax() -> None:
    # Form 5000-G: the exemption is reported on line 10105 and the VFA and SRVA are not claimed. The
    # exemption is a memo input, so the refund is Return Y's, -5409.31 (a refund of 5,409.31).
    worksheet = return_hu(exempt_income="1000")

    assert worksheet.get(EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME).value == D("1000")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-5409.31")


def test_return_hu_the_vfa_alone_with_line_10105_absent_still_gives_6000() -> None:
    # Form 5000-G: the VFA is claimed on line 31220 with no exemption on line 10105 (absent, 0).
    worksheet = return_hu(volunteer_firefighters=1)

    assert worksheet.get(VOLUNTEER_FIREFIGHTERS_CREDIT).value == D("6000.00")


# --- the exemption with the VFA or the SRVA, or both, is refused ------------------------------


def test_return_hu_the_exemption_with_the_vfa_is_refused_naming_the_conflict() -> None:
    # Form 5000-G: "you must choose which one you want to claim".
    with pytest.raises(InputOutOfRangeError, match=re.escape(CONFLICT)):
        return_hu(exempt_income="1000", volunteer_firefighters=1)


def test_return_hu_the_exemption_with_the_srva_is_refused_naming_the_conflict() -> None:
    with pytest.raises(InputOutOfRangeError, match=re.escape(CONFLICT)):
        return_hu(exempt_income="1000", search_and_rescue=1)


def test_return_hu_the_exemption_with_both_the_vfa_and_the_srva_is_refused() -> None:
    # Both checks refuse this return; the conflict check is ready first and speaks first.
    with pytest.raises(InputOutOfRangeError, match=re.escape(CONFLICT)):
        return_hu(exempt_income="1000", volunteer_firefighters=1, search_and_rescue=1)
