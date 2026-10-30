"""Registered and money kinds of the federal catalog family `resp_aips`."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    ADVANCED_CANADA_WORKERS_BENEFIT,
    RESP_AIPS_ADDITIONAL_TAX,
    RESP_AIPS_CONTRIBUTIONS_COUNTED,
    RESP_AIPS_LIFETIME_LIMIT,
    RESP_AIPS_LIMIT_REMAINING,
    RESP_AIPS_PART_A_APPLIES,
    RESP_AIPS_PART_A_APPLIES_CHECKED,
    RESP_AIPS_PART_A_TAX,
    RESP_AIPS_PART_B_TAX,
    RESP_AIPS_RECEIVED_PART_A,
    RESP_AIPS_RECEIVED_PART_B,
    RESP_AIPS_REDUCTION,
    RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
    RESP_AIPS_RRSP_CONTRIBUTIONS,
    RESP_AIPS_SUBJECT_TO_TAX,
)


def test_the_resp_aips_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/advanced_canada_workers_benefit") is ADVANCED_CANADA_WORKERS_BENEFIT
    assert registry.get("ca/resp_aips_received_part_a") is RESP_AIPS_RECEIVED_PART_A
    assert registry.get("ca/resp_aips_rrsp_contributions") is RESP_AIPS_RRSP_CONTRIBUTIONS
    assert (
        registry.get("ca/resp_aips_reduction_used_in_previous_years")
        is RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS
    )
    assert registry.get("ca/resp_aips_received_part_b") is RESP_AIPS_RECEIVED_PART_B
    assert registry.get("ca/resp_aips_part_a_applies") is RESP_AIPS_PART_A_APPLIES
    assert registry.get("ca/resp_aips_contributions_counted") is RESP_AIPS_CONTRIBUTIONS_COUNTED
    assert registry.get("ca/resp_aips_lifetime_limit") is RESP_AIPS_LIFETIME_LIMIT
    assert registry.get("ca/resp_aips_limit_remaining") is RESP_AIPS_LIMIT_REMAINING
    assert registry.get("ca/resp_aips_reduction") is RESP_AIPS_REDUCTION
    assert registry.get("ca/resp_aips_subject_to_tax") is RESP_AIPS_SUBJECT_TO_TAX
    assert registry.get("ca/resp_aips_part_a_tax") is RESP_AIPS_PART_A_TAX
    assert registry.get("ca/resp_aips_part_b_tax") is RESP_AIPS_PART_B_TAX
    assert registry.get("ca/resp_aips_additional_tax") is RESP_AIPS_ADDITIONAL_TAX


def test_the_resp_aips_kinds_are_money() -> None:
    for kind in (
        ADVANCED_CANADA_WORKERS_BENEFIT,
        RESP_AIPS_RECEIVED_PART_A,
        RESP_AIPS_RRSP_CONTRIBUTIONS,
        RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
        RESP_AIPS_RECEIVED_PART_B,
        RESP_AIPS_CONTRIBUTIONS_COUNTED,
        RESP_AIPS_LIFETIME_LIMIT,
        RESP_AIPS_LIMIT_REMAINING,
        RESP_AIPS_REDUCTION,
        RESP_AIPS_SUBJECT_TO_TAX,
        RESP_AIPS_PART_A_TAX,
        RESP_AIPS_PART_B_TAX,
        RESP_AIPS_ADDITIONAL_TAX,
    ):
        assert kind.value_type is Decimal, kind.identifier


YES_OR_NO_CHECKED = ((RESP_AIPS_PART_A_APPLIES, RESP_AIPS_PART_A_APPLIES_CHECKED),)


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
