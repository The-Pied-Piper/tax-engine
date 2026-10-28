"""Unit tests for the ApplyRatioOrZero capability (`ca/apply_ratio_or_zero`), made-up kinds.

It mirrors `core/apply_ratio` (same slots: one parameter slot `rounding`, a `rounding_only`
dataset; consumed `amount`, `numerator` and `denominator`; produced `output`), with one difference:
for Form T2048 line 36 "(if the result is "0", enter "0" on lines 41 and 42 and continue to Part
5)", a zero denominator gives 0, not an error. Otherwise the output is
`rounding.apply(amount × numerator / denominator)`, the product formed first and divided once as an
exact fraction. It records one `RatioAppliedLine` (the line `core/apply_ratio` records), with the
zero denominator and a result of 0 when the denominator is 0. `core/apply_ratio` is unchanged and
still refuses a zero denominator.
"""

from __future__ import annotations

import decimal
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
from tax_calculator.domain.trace import RatioAppliedLine
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

ABIL = ArtifactKind("ex/abil", Decimal)
ALLOCATED = ArtifactKind("ex/allocated", Decimal)
TOTAL = ArtifactKind("ex/total", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half-up to the cent."""
    return ParameterDataset(
        "ex/reduction_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> ApplyRatioOrZero:
    """By default the made-up ABIL × allocated / total, to the cent."""
    return ApplyRatioOrZero(rounding_data or rounding(), ABIL, ALLOCATED, TOTAL, REDUCTION)


def inputs(amount: str, numerator: str, denominator: str) -> tuple[Artifact[Any], ...]:
    return (
        Artifact(ABIL, D(amount)),
        Artifact(ALLOCATED, D(numerator)),
        Artifact(TOTAL, D(denominator)),
    )


def compute(
    wired: ApplyRatioOrZero, amount: str, numerator: str, denominator: str
) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, numerator, denominator)).outputs
    return output


def test_is_registered_as_ca_apply_ratio_or_zero() -> None:
    assert CapabilityRegistry.shared().get("ca/apply_ratio_or_zero") is ApplyRatioOrZero


def test_declares_the_slots_of_core_apply_ratio() -> None:
    assert ApplyRatioOrZero.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert ApplyRatioOrZero.CONSUMES == {
        "amount": Decimal,
        "numerator": Decimal,
        "denominator": Decimal,
    }
    assert ApplyRatioOrZero.PRODUCES == {"output": Decimal}
    assert capability().consumes == frozenset({ABIL, ALLOCATED, TOTAL})
    assert capability().produces == frozenset({REDUCTION})


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyRatioOrZero(
        rounding=rounding(), amount=ABIL, numerator=ALLOCATED, denominator=TOTAL, output=REDUCTION
    )

    assert compute(wired, "4000", "9500", "9500") == Artifact(REDUCTION, D("4000"))


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRatioOrZero") as raised:
        ApplyRatioOrZero(rounding(), ABIL, ALLOCATED, TOTAL, ABIL)

    assert "'amount'" in str(raised.value)
    assert "'output'" in str(raised.value)


def test_rejects_one_kind_as_both_numerator_and_denominator() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyRatioOrZero") as raised:
        ApplyRatioOrZero(rounding(), ABIL, ALLOCATED, ALLOCATED, REDUCTION)

    assert "'numerator'" in str(raised.value)
    assert "'denominator'" in str(raised.value)


@pytest.mark.parametrize(
    ("amount", "numerator", "denominator", "expected"),
    [
        # Return BE: line 36 equals line 35, so the whole ABIL.
        ("4000", "9500", "9500", "4000"),
        # 4000 x 5000 / 9500 = 2105.2631..., half-up to the cent.
        ("4000", "5000", "9500", "2105.26"),
        ("4000", "0", "9500", "0"),
        # A ratio above 1 is not capped.
        ("100", "300", "200", "150"),
    ],
)
def test_multiplies_then_divides_once_and_rounds_once(
    amount: str, numerator: str, denominator: str, expected: str
) -> None:
    assert compute(capability(), amount, numerator, denominator) == Artifact(REDUCTION, D(expected))


@pytest.mark.parametrize(
    ("amount", "numerator"), [("0", "0"), ("4000", "0"), ("0", "5"), ("4000", "5")]
)
def test_a_zero_denominator_gives_zero(amount: str, numerator: str) -> None:
    assert compute(capability(), amount, numerator, "0") == Artifact(REDUCTION, D("0"))


@pytest.mark.parametrize("denominator", ["0", "0.00", "0E+2"])
def test_a_zero_denominator_gives_zero_whatever_its_scale(denominator: str) -> None:
    assert compute(capability(), "4000", "5", denominator).value == D("0")


def test_under_no_rounding_a_quotient_without_a_finite_expansion_raises_inexact() -> None:
    with pytest.raises(decimal.Inexact):
        compute(capability(rounding(NO_ROUNDING)), "1", "1", "3")


def test_under_no_rounding_a_zero_denominator_still_gives_zero() -> None:
    assert compute(capability(rounding(NO_ROUNDING)), "1", "1", "0").value == D("0")


@pytest.mark.parametrize("missing", [0, 1, 2])
def test_a_missing_consumed_artifact_is_a_missing_artifact(missing: int) -> None:
    given = tuple(a for i, a in enumerate(inputs("1", "1", "1")) if i != missing)

    with pytest.raises(MissingArtifactError):
        capability().compute(given)


def test_traces_one_ratio_applied_line() -> None:
    result = capability().compute(inputs("4000", "5000", "9500"))

    assert result.trace == (
        RatioAppliedLine(
            REDUCTION,
            ABIL,
            D("4000"),
            ALLOCATED,
            D("5000"),
            TOTAL,
            D("9500"),
            CENT,
            D("2105.26"),
        ),
    )


def test_traces_the_zero_denominator_and_a_result_of_zero() -> None:
    result = capability().compute(inputs("4000", "0", "0"))

    (line,) = result.trace
    assert isinstance(line, RatioAppliedLine)
    assert line.output is REDUCTION
    assert line.denominator_value == D("0")
    assert line.result == D("0")
    assert line.amount == D("0")
