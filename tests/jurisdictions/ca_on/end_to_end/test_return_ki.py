"""CA-ON 2025 end to end: return KI, Form T1032 Note 1 on line 18 (the transferring spouse died) and
the conditions of page 1 (not living separate and apart for 90 days or more including December 31,
2025, and residents of Canada on December 31, 2025).

The worked return `returns/2025_return_ki.yaml` is checked by `test_worked_returns.py`. This module
pins the two ways the denominator of line 18 goes and the refusals of an election when a condition
of page 1 is not met.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import T1032_LINE_18, T1032_LINE_21
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

FORM = "ca/t1032"


def form(
    *,
    transferring_spouse_died: int = 1,
    not_separated_90_days: int = 1,
    residents_of_canada: int = 1,
    elected_deduction: str = "5000",
) -> Worksheet:
    """The T1032 worksheet of return KI: pension 30,000.00, 3 months married, 5 to the death."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_pensions_and_superannuation="30000",
        t1032_line_22=elected_deduction,
        spouse_or_common_law_partner_on_december_31=1,
        t1032_eligible_pension_income="30000",
        t1032_marital_status_changed=1,
        t1032_filer_is_transferring_spouse=1,
        t1032_months_married="3",
        t1032_months_in_tax_year="5",
        t1032_transferring_spouse_died=transferring_spouse_died,
        t1032_not_separated_90_days=not_separated_90_days,
        t1032_residents_of_canada=residents_of_canada,
        t1032_income_tax_deducted_on_pension="3000",
        income_tax_deducted="3000",
    )
    (worksheet,) = service().compute(CA_ON, 2025, *artifacts)[FORM]
    return worksheet


def test_a_deceased_transferring_spouse_divides_line_18_by_the_months_to_death() -> None:
    found = form()

    assert found.get(T1032_LINE_18).value == D("18000.00")
    assert found.get(T1032_LINE_21).value == D("9000.00")


def test_a_living_transferring_spouse_divides_line_18_by_the_printed_12() -> None:
    found = form(transferring_spouse_died=0, elected_deduction="3000")

    assert found.get(T1032_LINE_18).value == D("7500.00")
    assert found.get(T1032_LINE_21).value == D("3750.00")


@pytest.mark.parametrize("answers", [{"not_separated_90_days": 0}, {"residents_of_canada": 0}])
def test_an_election_is_refused_when_a_condition_of_page_1_is_not_met(
    answers: dict[str, Any],
) -> None:
    with pytest.raises(InputAboveBoundError):
        form(**answers)


def test_no_election_is_accepted_when_a_condition_of_page_1_is_not_met() -> None:
    found = form(not_separated_90_days=0, elected_deduction="0")

    assert found.get(T1032_LINE_21).value == D("9000.00")
