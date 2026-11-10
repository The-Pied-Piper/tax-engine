"""Registered and money kinds of the federal catalog family `canada_workers_benefit`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    CWB_EMPLOYMENT_INCOME,
    CWB_MAXIMUM,
    CWB_NET_INCOME_LESS_UCCB_RDSP_LINE_12,
    CWB_NET_INCOME_LINE_7,
    CWB_NET_INCOME_TOTAL_LINE_10,
    CWB_REDUCTION_THRESHOLD,
    WORKING_INCOME,
)
from tests.kinds import non_negative


def test_the_cwb_maximum_is_registered_money_and_non_negative(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 21 "If not, enter $1,633": the printed maximum of the basic benefit for a
    # filer with no eligible spouse or dependant, a dataset figure taken whole.
    assert CWB_MAXIMUM.value_type is Decimal
    assert non_negative(CWB_MAXIMUM) is True
    assert registry.get("ca/cwb_maximum") is CWB_MAXIMUM


def test_the_canada_workers_benefit_kinds_are_money() -> None:
    for kind in (
        CWB_EMPLOYMENT_INCOME,
        WORKING_INCOME,
        CWB_NET_INCOME_LINE_7,
        CWB_NET_INCOME_TOTAL_LINE_10,
        CWB_NET_INCOME_LESS_UCCB_RDSP_LINE_12,
        ADJUSTED_FAMILY_NET_INCOME,
        CWB_REDUCTION_THRESHOLD,
    ):
        assert kind.value_type is Decimal, kind.identifier


def _kind(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind


def test_the_adjusted_family_net_income_is_signed(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 15 "Line 13 minus line 14" prints no "if negative, enter "0"", unlike lines
    # 12, 18 and 25.
    assert non_negative(ADJUSTED_FAMILY_NET_INCOME) is False
    assert non_negative(registry.kind("ca/adjusted_family_net_income")) is False


def test_the_schedule_6_line_7_net_income_is_signed(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 7 "Net income from line 23600 ... if negative, show in brackets", column 1
    # (You): the form shows a negative figure, so the kind is signed.
    assert non_negative(CWB_NET_INCOME_LINE_7) is False
    assert non_negative(registry.kind("ca/cwb_net_income_line_7")) is False


def test_the_schedule_6_line_10_net_income_total_is_signed(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 10 "Add lines 7 to 9." (column 1, You) prints no floor at zero, so the kind
    # is signed.
    assert non_negative(CWB_NET_INCOME_TOTAL_LINE_10) is False
    assert non_negative(registry.kind("ca/cwb_net_income_total_line_10")) is False


def test_the_base_amount_of_schedule_6_line_17_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 17 "Base amount 3,000.00": the printed amount, a dataset figure (no salary),
    # declared non-negative like the other claimed amounts of the schedule.
    kind = _kind(registry, "ca/cwb_base_amount")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_working_income_over_the_base_amount_of_schedule_6_line_18_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 18 "Line 16 minus line 17 (if negative, enter "0")": floored at zero, so the
    # kind is non-negative.
    kind = _kind(registry, "ca/cwb_working_income_over_base_amount")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_working_income_rate_of_schedule_6_line_20_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 20 "Line 18 multiplied by the percentage from line 19": line 18 is floored at
    # zero and the rate is 27%, so the product is non-negative.
    kind = _kind(registry, "ca/cwb_working_income_rate_line_20")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_basic_benefit_before_reduction_of_schedule_6_line_22_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 22 "Enter whichever is less: amount from line 20 or line 21.": the lesser of
    # two non-negative amounts is itself non-negative.
    kind = _kind(registry, "ca/cwb_basic_benefit_line_22")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_net_income_over_the_base_amount_of_schedule_6_line_25_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 25 "Line 23 minus line 24 (if negative, enter "0")": floored at zero, so the
    # kind is non-negative.
    kind = _kind(registry, "ca/cwb_net_income_over_base_amount")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_reduction_amount_of_schedule_6_line_27_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 27 "Line 25 multiplied by the percentage from line 26": line 25 is floored at
    # zero and the rate is 15%, so the product is non-negative.
    kind = _kind(registry, "ca/cwb_reduction_line_27")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True


def test_the_benefit_on_schedule_6_line_28_is_a_non_negative_money_kind(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 28 "Line 22 minus line 27 (if negative, enter "0")": the amount that goes to
    # T1 line 45300, floored at zero, so the kind is non-negative.
    kind = _kind(registry, "ca/cwb_benefit_line_28")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
