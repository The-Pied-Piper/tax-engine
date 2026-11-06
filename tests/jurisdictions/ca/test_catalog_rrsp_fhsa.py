"""Registered and money kinds of the federal catalog family `rrsp_fhsa`."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    FHSA_FIRST_OPENED_IN_YEAR,
    FHSA_HOME_ADDRESS_SAME,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    FHSA_QUALIFYING_WITHDRAWALS,
    PENSION_ADJUSTMENT,
    RRSP_AMOUNT_DEDUCTED,
    RRSP_CONTRIBUTIONS,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_LIMIT,
    RRSP_DEDUCTION_MAXIMUM,
    UNUSED_RRSP_CONTRIBUTIONS,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
)
from tests.kinds import non_negative


def test_the_rrsp_fhsa_kinds_are_money() -> None:
    for kind in (
        UNUSED_RRSP_CONTRIBUTIONS,
        RRSP_CONTRIBUTIONS,
        RRSP_CONTRIBUTIONS_AVAILABLE,
        RRSP_DEDUCTION_LIMIT,
        RRSP_DEDUCTION_MAXIMUM,
        RRSP_AMOUNT_DEDUCTED,
        RRSP_DEDUCTION,
        UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
    ):
        assert kind.value_type is Decimal, kind.identifier


# T1 line 20600 "Pension adjustment" and the Schedule 15 memo lines (68930, 59 and 68960, 68965),
# each a caller's input and a declared output that no step reads. The three FHSA ticks are 0 or 1
# counts.
def test_the_pension_adjustment_and_fhsa_memo_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/pension_adjustment") is PENSION_ADJUSTMENT
    assert registry.get("ca/fhsa_first_opened_in_year") is FHSA_FIRST_OPENED_IN_YEAR
    assert registry.get("ca/fhsa_qualifying_withdrawals") is FHSA_QUALIFYING_WITHDRAWALS
    assert registry.get("ca/fhsa_home_address_same") is FHSA_HOME_ADDRESS_SAME


def test_the_pension_adjustment_and_qualifying_withdrawals_are_non_negative_money() -> None:
    for kind in (PENSION_ADJUSTMENT, FHSA_QUALIFYING_WITHDRAWALS):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier


def test_the_fhsa_ticks_are_non_negative_int_counts() -> None:
    for kind in (FHSA_FIRST_OPENED_IN_YEAR, FHSA_HOME_ADDRESS_SAME):
        assert kind.value_type is int, kind.identifier
        assert non_negative(kind) is True, kind.identifier


# Schedule 15 line 2 is checked against line 1, line 8 against line 7 and line 44 against line 42,
# each by `core/at_most`: the checked amount is that step's output, which line 3, line 9, and
# lines 45 and 48 read in place of the input. The checked amounts are registered beside the inputs.
def test_the_fhsa_checked_amounts_are_the_registered_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.kind("ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked")
        is FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED
    )
    assert (
        registry.kind("ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked")
        is FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED
    )
    assert (
        registry.kind("ca/fhsa_deductions_for_2024_and_prior_years_checked")
        is FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED
    )
    for kind in (
        FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
        FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
        FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
    # The checked amounts are not the inputs they check.
    assert (
        FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED
        is not FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL
    )


YES_OR_NO_CHECKED = (
    (FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED, FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED),
)


@pytest.mark.parametrize(("raw", "checked"), YES_OR_NO_CHECKED, ids=lambda kind: kind.identifier)
def test_each_yes_or_no_checked_kind_is_a_non_negative_count_named_after_its_input(
    raw: ArtifactKind[int], checked: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the steps that read it; a count of 2 or
    # more is refused, not capped.
    assert checked.identifier == f"{raw.identifier}_checked"
    assert registry.get(checked.identifier) is checked
    assert checked.value_type is int
    assert non_negative(checked) is True
