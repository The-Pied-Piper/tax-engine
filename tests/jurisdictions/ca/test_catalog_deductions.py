"""Registered and money kinds of the federal catalog family `deductions`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_SIGNED,
    OAS_BENEFITS_BASE_AMOUNT,
    SOCIAL_BENEFITS_REPAYMENT,
)
from tests.jurisdictions.ca.catalog_snapshot import REGISTERED, SIGNED
from tests.kinds import non_negative


def test_the_net_income_signed_is_the_signed_twin_of_the_net_income(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 56 and line 23600 "Line 54 minus line 55 (if negative, enter "0")" stays the
    # non-negative `ca/net_income`; Form T1206 Part 1 line 5 "Net income from line 23600 of your
    # tax return (or the amount you would have entered if the instructions on line 23600 read "if
    # negative, show in brackets")" and Schedule ON479-A column 1 line 1 read the amount before
    # that floor, a kind of its own that is signed.
    assert NET_INCOME_SIGNED is not NET_INCOME
    assert NET_INCOME_SIGNED is not NET_INCOME_BEFORE_ADJUSTMENTS
    assert NET_INCOME_SIGNED.identifier == "ca/net_income_signed"
    assert non_negative(NET_INCOME_SIGNED) is False
    assert registry.kind("ca/net_income_signed") is NET_INCOME_SIGNED
    assert "ca/net_income_signed" in SIGNED
    assert non_negative(NET_INCOME) is True
    assert "ca/net_income" not in SIGNED


def test_the_other_social_benefits_chart_lines_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Lines 5 and 17 print "(if negative, enter "0")"; the others add, take 15% of, or compare
    # non-negative figures. The two caller inputs are slip boxes.
    for kind in (
        OAS_BENEFITS_BASE_AMOUNT,
        SOCIAL_BENEFITS_REPAYMENT,
    ):
        assert kind.identifier not in SIGNED, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_cpp_part_3b_lines_and_the_three_return_lines_are_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    # The zero of "enter "0"", lines 30 to 48 of Part 3b (each is a chosen non-negative amount, a
    # sum of them, or a difference that cannot go below zero) and T1 line 30800, line 22215 and
    # line 44800 as the form routes them: none prints brackets.
    for identifier in (
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
        assert identifier in REGISTERED, identifier


def test_part_3_line_2_is_a_non_negative_amount_of_employment_earnings(
    registry: ArtifactRegistry,
) -> None:
    # Part 3 line 2 "Enter whichever is less: amount from line D of Part 2 or line 1": the lesser
    # of two non-negative amounts, read by Part 5 line 32 ("Amount from line 2 of Part 3").
    kind = registry.kind("ca/cpp_part_3_line_2")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert "ca/cpp_part_3_line_2" not in SIGNED
    assert "ca/cpp_part_3_line_2" in REGISTERED


def test_the_lines_the_part_5_routing_reads_are_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    # The Part 3 route of lines 30800, 22215 and 44800 keeps the PR 2 steps under a name of its
    # own; the kinds the readers (ON428, Schedule 8's credit, the deductions, the refund total)
    # read keep their names and choose between the Part 3 route and Part 5 lines 57, 69 and 50 by
    # the Part 5 completed count. Lines 31000, 22200 and 42100 are the Part 4 route plus the Part
    # 5 route (Part 5 line 70, line 88 and line 49 if positive, once for each Part 5 completed).
    for identifier in (
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
        "ca/cpp_part_5_base_contributions_on_self_employment",
        "ca/cpp_base_contributions_on_self_employment",
        "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
        "ca/cpp_part_5_payable_on_self_employment",
        "ca/cpp_payable_on_self_employment",
        "ca/cpp_payable_on_self_employment_and_other_earnings",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
        assert identifier in REGISTERED, identifier


# Form T1223 Part C, 2025: the clergy residence deduction, T1 line 23100. The six inputs are the
# figures the form takes from the filer (Part C (A), lines 1, 3, 6 and 7, and the Part C (B)
# choice); the lines 2 to 10 and the totals are calculated from them and the datasets. Line 23100
# was a starting amount (an input) until it was calculated here.


# --- moving expenses, Form T1-M (T1 line 21900) -----------------------------------------------


def kind_of(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    """The registered kind `identifier`; the registry raises for a kind it does not hold."""
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind


def test_the_amt_moving_expenses_stand_in_is_no_longer_a_kind(registry: ArtifactRegistry) -> None:
    # Form T691 Part 1 line 56 is "Moving expenses deduction from line 21900": the alternative
    # minimum tax reads the computed line 21900, so the caller's stand-in is removed.
    assert "ca/amt_moving_expenses_deduction" not in registry.identifiers()
