"""Registered and money kinds of the federal catalog family `rrsp_fhsa`."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    FHSA_ANNUAL_AMOUNT,
    FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
    FHSA_ANNUAL_AMOUNT_FOR_2024,
    FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
    FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CARRYFORWARD_FOR_2024,
    FHSA_CARRYFORWARD_FOR_2025,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_DEDUCTED,
    FHSA_CONTRIBUTIONS_IN_2024,
    FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_LIMIT,
    FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
    FHSA_DEDUCTION,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
    FHSA_DESIGNATED_TRANSFERS_IN_2025,
    FHSA_DESIGNATED_WITHDRAWALS_IN_2025,
    FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
    FHSA_FIRST_OPENED_IN_YEAR,
    FHSA_HOME_ADDRESS_SAME,
    FHSA_LIFETIME_LIMIT,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
    FHSA_MAXIMUM_DEDUCTION,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    FHSA_NET_RRSP_TRANSFER_AMOUNT,
    FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
    FHSA_QUALIFYING_WITHDRAWALS,
    FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS,
    FHSA_RRSP_TRANSFERS_IN_2025,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TOTAL_DESIGNATED_TRANSFERS,
    FHSA_TOTAL_RRSP_TRANSFERS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_BROUGHT_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
    FHSA_VARIABLE_B_AMOUNT,
    FHSA_VARIABLE_F_AMOUNT,
    FHSA_VARIABLE_H_AMOUNT,
    PENSION_ADJUSTMENT,
    RPP_DEDUCTION,
    RRSP_AMOUNT_DEDUCTED,
    RRSP_CONTRIBUTIONS,
    RRSP_CONTRIBUTIONS_AVAILABLE,
    RRSP_DEDUCTION,
    RRSP_DEDUCTION_LIMIT,
    RRSP_DEDUCTION_MAXIMUM,
    UNUSED_RRSP_CONTRIBUTIONS,
    UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD,
)


def test_the_rrsp_fhsa_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/rpp_deduction") is RPP_DEDUCTION
    assert registry.get("ca/unused_rrsp_contributions") is UNUSED_RRSP_CONTRIBUTIONS
    assert registry.get("ca/rrsp_contributions") is RRSP_CONTRIBUTIONS
    assert registry.get("ca/rrsp_contributions_available") is RRSP_CONTRIBUTIONS_AVAILABLE
    assert registry.get("ca/rrsp_deduction_limit") is RRSP_DEDUCTION_LIMIT
    assert registry.get("ca/rrsp_deduction_maximum") is RRSP_DEDUCTION_MAXIMUM
    assert registry.get("ca/rrsp_amount_deducted") is RRSP_AMOUNT_DEDUCTED
    assert registry.get("ca/rrsp_deduction") is RRSP_DEDUCTION
    assert (
        registry.get("ca/unused_rrsp_contributions_carried_forward")
        is UNUSED_RRSP_CONTRIBUTIONS_CARRIED_FORWARD
    )
    assert registry.get("ca/fhsa_contributions_in_2025") is FHSA_CONTRIBUTIONS_IN_2025
    assert (
        registry.get("ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal")
        is FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL
    )
    assert (
        registry.get("ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal")
        is FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL
    )
    assert registry.get("ca/fhsa_variable_b_amount") is FHSA_VARIABLE_B_AMOUNT
    assert (
        registry.get("ca/fhsa_contributions_plus_variable_b_amount")
        is FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT
    )
    assert (
        registry.get("ca/fhsa_designated_withdrawals_in_2025")
        is FHSA_DESIGNATED_WITHDRAWALS_IN_2025
    )
    assert registry.get("ca/fhsa_contributions_in_2024") is FHSA_CONTRIBUTIONS_IN_2024
    assert (
        registry.get("ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal")
        is FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL
    )
    assert (
        registry.get("ca/fhsa_contributions_in_2024_after_first_qualifying_withdrawal")
        is FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL
    )
    assert (
        registry.get("ca/fhsa_contributions_after_first_qualifying_withdrawal")
        is FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL
    )
    assert (
        registry.get("ca/fhsa_excess_designated_withdrawals") is FHSA_EXCESS_DESIGNATED_WITHDRAWALS
    )
    assert registry.get("ca/fhsa_contributions_limit") is FHSA_CONTRIBUTIONS_LIMIT
    assert registry.get("ca/fhsa_annual_amount") is FHSA_ANNUAL_AMOUNT
    assert registry.get("ca/fhsa_carryforward_for_2025") is FHSA_CARRYFORWARD_FOR_2025
    assert (
        registry.get("ca/fhsa_annual_amount_with_carryforward")
        is FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD
    )
    assert (
        registry.get("ca/fhsa_rrsp_transfers_in_2024_and_prior_years")
        is FHSA_RRSP_TRANSFERS_IN_2024_AND_PRIOR_YEARS
    )
    assert registry.get("ca/fhsa_rrsp_transfers_in_2025") is FHSA_RRSP_TRANSFERS_IN_2025
    assert registry.get("ca/fhsa_total_rrsp_transfers") is FHSA_TOTAL_RRSP_TRANSFERS
    assert (
        registry.get("ca/fhsa_designated_transfers_in_2024_and_prior_years")
        is FHSA_DESIGNATED_TRANSFERS_IN_2024_AND_PRIOR_YEARS
    )
    assert registry.get("ca/fhsa_designated_transfers_in_2025") is FHSA_DESIGNATED_TRANSFERS_IN_2025
    assert registry.get("ca/fhsa_total_designated_transfers") is FHSA_TOTAL_DESIGNATED_TRANSFERS
    assert registry.get("ca/fhsa_net_rrsp_transfer_amount") is FHSA_NET_RRSP_TRANSFER_AMOUNT
    assert (
        registry.get("ca/fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years")
        is FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS
    )
    assert registry.get("ca/fhsa_variable_h_amount") is FHSA_VARIABLE_H_AMOUNT
    assert (
        registry.get("ca/fhsa_net_transfer_amount_less_variable_h_amount")
        is FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT
    )
    assert registry.get("ca/fhsa_annual_amount_for_2024") is FHSA_ANNUAL_AMOUNT_FOR_2024
    assert registry.get("ca/fhsa_carryforward_for_2024") is FHSA_CARRYFORWARD_FOR_2024
    assert (
        registry.get("ca/fhsa_annual_amount_for_2024_with_carryforward")
        is FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD
    )
    assert (
        registry.get("ca/fhsa_transfer_amount_at_most_limit") is FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT
    )
    assert registry.get("ca/fhsa_variable_f_amount") is FHSA_VARIABLE_F_AMOUNT
    assert (
        registry.get("ca/fhsa_transfer_amount_plus_variable_f_amount")
        is FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT
    )
    assert (
        registry.get("ca/fhsa_net_transfer_amount_after_prior_years")
        is FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS
    )
    assert (
        registry.get("ca/fhsa_annual_amount_after_transfers") is FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS
    )
    assert (
        registry.get("ca/fhsa_maximum_participation_period_ended")
        is FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED
    )
    assert registry.get("ca/fhsa_annual_limit_from_step_2") is FHSA_ANNUAL_LIMIT_FROM_STEP_2
    assert (
        registry.get("ca/fhsa_annual_limit_after_maximum_participation_period")
        is FHSA_ANNUAL_LIMIT_AFTER_MAXIMUM_PARTICIPATION_PERIOD
    )
    assert registry.get("ca/fhsa_annual_limit") is FHSA_ANNUAL_LIMIT
    assert (
        registry.get("ca/fhsa_annual_limits_for_2024_and_prior_years")
        is FHSA_ANNUAL_LIMITS_FOR_2024_AND_PRIOR_YEARS
    )
    assert registry.get("ca/fhsa_total_annual_limits") is FHSA_TOTAL_ANNUAL_LIMITS
    assert (
        registry.get("ca/fhsa_deductions_for_2024_and_prior_years")
        is FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS
    )
    assert (
        registry.get("ca/fhsa_annual_limits_less_deductions") is FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS
    )
    assert registry.get("ca/fhsa_lifetime_limit") is FHSA_LIFETIME_LIMIT
    assert (
        registry.get("ca/fhsa_lifetime_limit_less_deductions")
        is FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS
    )
    assert (
        registry.get("ca/fhsa_lifetime_limit_less_deductions_and_transfers")
        is FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS
    )
    assert registry.get("ca/fhsa_maximum_deduction") is FHSA_MAXIMUM_DEDUCTION
    assert (
        registry.get("ca/fhsa_unused_contributions_brought_forward")
        is FHSA_UNUSED_CONTRIBUTIONS_BROUGHT_FORWARD
    )
    assert (
        registry.get("ca/fhsa_unused_contributions_plus_contributions")
        is FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS
    )
    assert registry.get("ca/fhsa_contributions_available") is FHSA_CONTRIBUTIONS_AVAILABLE
    assert registry.get("ca/fhsa_contributions_deducted") is FHSA_CONTRIBUTIONS_DEDUCTED
    assert registry.get("ca/fhsa_deduction") is FHSA_DEDUCTION
    assert (
        registry.get("ca/fhsa_unused_contributions_carried_forward")
        is FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD
    )


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
        assert kind.non_negative is True, kind.identifier


def test_the_fhsa_ticks_are_non_negative_int_counts() -> None:
    for kind in (FHSA_FIRST_OPENED_IN_YEAR, FHSA_HOME_ADDRESS_SAME):
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


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
        assert kind.non_negative is True, kind.identifier
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
    assert checked.non_negative is True
