"""Unit tests for the ApplyPercentage capability (`ca/apply_percentage`), made-up kinds.

For Form T2048 line 3 "Line 1 multiplied by the percentage from line 2", where line 2 "Percentage
allocated to you" is a number the filer enters as printed (50 for 50%). It mirrors
`core/apply_ratio`: one parameter slot `rounding` (a `rounding_only` dataset), two consumed
`Decimal` slots, `amount` and `percentage`, and one produced slot `output`. The output is
`rounding.apply(amount × percentage / 100)`, formed as an exact fraction and rounded once by the
dataset's rule. A percentage above 100 is not capped. It records one `PercentageAppliedLine` (new;
in `tax_calculator.domain.trace`) with the output, the amount's kind and value, the
percentage's kind and value, the rounding rule and the result, in that order.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.trace import PercentageAppliedLine
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

ELECTED = ArtifactKind("ex/elected", Decimal)
SHARE = ArtifactKind("ex/share", Decimal)
ALLOCATED = ArtifactKind("ex/allocated", Decimal)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half-up to the cent."""
    return ParameterDataset(
        "ex/allocated_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> ApplyPercentage:
    return ApplyPercentage(rounding_data or rounding(), ELECTED, SHARE, ALLOCATED)


def inputs(amount: str, percentage: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(ELECTED, D(amount)), Artifact(SHARE, D(percentage)))


def compute(wired: ApplyPercentage, amount: str, percentage: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, percentage)).outputs
    return output


def test_is_registered_as_ca_apply_percentage() -> None:
    assert CapabilityRegistry.shared().get("ca/apply_percentage") is ApplyPercentage


def test_declares_its_slots() -> None:
    assert ApplyPercentage.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert ApplyPercentage.CONSUMES == {"amount": Decimal, "percentage": Decimal}
    assert ApplyPercentage.PRODUCES == {"output": Decimal}
    assert capability().consumes == frozenset({ELECTED, SHARE})
    assert capability().produces == frozenset({ALLOCATED})


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyPercentage(rounding=rounding(), amount=ELECTED, percentage=SHARE, output=ALLOCATED)

    assert compute(wired, "600000", "50") == Artifact(ALLOCATED, D("300000"))


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyPercentage") as raised:
        ApplyPercentage(rounding(), ELECTED, SHARE, ELECTED)

    assert "'amount'" in str(raised.value)
    assert "'output'" in str(raised.value)


def test_rejects_one_kind_as_both_amount_and_percentage() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyPercentage") as raised:
        ApplyPercentage(rounding(), ELECTED, ELECTED, ALLOCATED)

    assert "'amount'" in str(raised.value)
    assert "'percentage'" in str(raised.value)


@pytest.mark.parametrize(
    ("amount", "percentage", "expected"),
    [
        # Return BE: 600000 allocated 50%.
        ("600000", "50", "300000"),
        ("600000", "100", "600000"),
        ("600000", "0", "0"),
        ("0", "50", "0"),
        # A percentage above 100 is not capped.
        ("1000", "150", "1500"),
        # 33.33% of 1000.01 = 333.3033..., half-up to the cent.
        ("1000.01", "33.33", "333.30"),
        # A tie rounds up: 1000.01 x 50% = 500.005.
        ("1000.01", "50", "500.01"),
    ],
)
def test_multiplies_by_the_percentage_over_100_and_rounds_once(
    amount: str, percentage: str, expected: str
) -> None:
    assert compute(capability(), amount, percentage) == Artifact(ALLOCATED, D(expected))


def test_under_no_rounding_the_result_stays_exact() -> None:
    assert compute(capability(rounding(NO_ROUNDING)), "1", "1").value == D("0.01")
    assert compute(capability(rounding(NO_ROUNDING)), "1000.01", "33.33").value == D("333.303333")


@pytest.mark.parametrize("missing", [0, 1])
def test_a_missing_consumed_artifact_is_a_missing_artifact(missing: int) -> None:
    given = tuple(a for i, a in enumerate(inputs("1", "1")) if i != missing)

    with pytest.raises(MissingArtifactError):
        capability().compute(given)


def test_traces_one_percentage_applied_line() -> None:
    result = capability().compute(inputs("600000", "50"))

    assert result.trace == (
        PercentageAppliedLine(ALLOCATED, ELECTED, D("600000"), SHARE, D("50"), CENT, D("300000")),
    )
