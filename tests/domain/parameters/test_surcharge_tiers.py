"""Unit tests for SurchargeTiers: the `surcharge_tiers` kind's values, with made-up figures.

A surcharge is charged at each tier's rate on the part of a base over the tier's threshold, at
most the tier's optional maximum. The value objects only hold and check the tiers: at least one
tier, thresholds non-negative and strictly increasing, each rate a `Rate`, each maximum absent or
a non-negative finite Decimal. Each tier computes its unrounded charge and the tiers their
charges, in order; the capability rounds and sums them.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_engine.domain.errors import DomainError, InvalidSurchargeTiersError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

D = Decimal

LOW = SurchargeTier(D(100), Rate(D("0.10")))
HIGH = SurchargeTier(D(300), Rate(D("0.25")))
# 10% of the base over 100, at most 15: the charge stops growing once the base reaches 250.
CAPPED = SurchargeTier(D(100), Rate(D("0.10")), D(15))


# --- one tier ---------------------------------------------------------------------------------


def test_a_tier_holds_its_threshold_and_rate() -> None:
    tier = SurchargeTier(threshold=D("100.50"), rate=Rate(D("0.125")))

    assert tier.threshold == D("100.50")
    assert tier.rate == Rate(D("0.125"))


def test_a_tier_holds_its_threshold_rate_and_maximum_only_in_that_order() -> None:
    assert [field.name for field in fields(SurchargeTier)] == ["threshold", "rate", "maximum"]


def test_a_tier_has_no_maximum_by_default() -> None:
    assert SurchargeTier(D(100), Rate(D("0.1"))).maximum is None


def test_a_tier_holds_its_maximum() -> None:
    tier = SurchargeTier(threshold=D(100), rate=Rate(D("0.1")), maximum=D("150.50"))

    assert tier.maximum == D("150.50")


def test_a_tier_keeps_its_maximum_exact() -> None:
    assert str(SurchargeTier(D(100), Rate(D("0.1")), D("150.50")).maximum) == "150.50"


def test_a_tier_may_have_a_zero_maximum() -> None:
    assert SurchargeTier(D(100), Rate(D("0.1")), D(0)).maximum == D(0)


def test_a_tier_may_take_no_maximum_explicitly() -> None:
    assert SurchargeTier(D(100), Rate(D("0.1")), None) == SurchargeTier(D(100), Rate(D("0.1")))


def test_a_tier_keeps_its_threshold_exact() -> None:
    assert str(SurchargeTier(D("100.50"), Rate(D("0.1"))).threshold) == "100.50"


def test_equal_tiers_are_equal() -> None:
    assert SurchargeTier(D(100), Rate(D("0.1"))) == SurchargeTier(D("100.0"), Rate(D("0.10")))
    assert SurchargeTier(D(100), Rate(D("0.1"))) != SurchargeTier(D(100), Rate(D("0.2")))


def test_tiers_differ_by_maximum() -> None:
    assert SurchargeTier(D(100), Rate(D("0.1")), D(15)) == SurchargeTier(
        D(100), Rate(D("0.1")), D("15.00")
    )
    assert SurchargeTier(D(100), Rate(D("0.1")), D(15)) != SurchargeTier(
        D(100), Rate(D("0.1")), D(20)
    )
    assert SurchargeTier(D(100), Rate(D("0.1")), D(15)) != SurchargeTier(D(100), Rate(D("0.1")))


def test_a_tier_with_a_maximum_is_hashable() -> None:
    assert hash(CAPPED) == hash(SurchargeTier(D(100), Rate(D("0.10")), D(15)))


def test_a_tier_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, LOW).threshold = D(1)


def test_a_tier_may_start_at_zero() -> None:
    assert SurchargeTier(D(0), Rate(D("0.1"))).threshold == D(0)


@pytest.mark.parametrize(
    ("threshold", "message"),
    [
        (D(-1), "threshold must not be negative"),
        (D("-0.01"), "threshold must not be negative"),
        (D("NaN"), "threshold must be finite"),
        (D("Infinity"), "threshold must be finite"),
    ],
)
def test_rejects_an_invalid_threshold(threshold: Decimal, message: str) -> None:
    with pytest.raises(InvalidSurchargeTiersError, match=message):
        SurchargeTier(threshold, Rate(D("0.1")))


@pytest.mark.parametrize("threshold", [100, 100.0, "100"])
def test_rejects_a_threshold_that_is_not_a_decimal(threshold: object) -> None:
    with pytest.raises(TypeError, match="threshold must be a Decimal"):
        SurchargeTier(threshold, Rate(D("0.1")))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("maximum", "message"),
    [
        (D(-1), "maximum must not be negative"),
        (D("-0.01"), "maximum must not be negative"),
        (D("NaN"), "maximum must be finite"),
        (D("Infinity"), "maximum must be finite"),
        (D("-Infinity"), "maximum must be finite"),
    ],
)
def test_rejects_an_invalid_maximum(maximum: Decimal, message: str) -> None:
    with pytest.raises(InvalidSurchargeTiersError, match=message):
        SurchargeTier(D(100), Rate(D("0.1")), maximum)


@pytest.mark.parametrize("maximum", [15, 15.0, "15"])
def test_rejects_a_maximum_that_is_not_a_decimal(maximum: object) -> None:
    with pytest.raises(TypeError, match="maximum must be a Decimal"):
        SurchargeTier(D(100), Rate(D("0.1")), maximum)  # type: ignore[arg-type]


@pytest.mark.parametrize("rate", [D("0.1"), 0.1, "0.1"])
def test_rejects_a_rate_that_is_not_a_rate(rate: object) -> None:
    with pytest.raises(TypeError, match="rate must be a Rate"):
        SurchargeTier(D(100), rate)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("base", "charge"),
    [
        pytest.param(D("99.99"), D(0), id="below"),
        pytest.param(D(0), D(0), id="zero-base"),
        pytest.param(D(100), D(0), id="at"),
        pytest.param(D("100.01"), D("0.0010"), id="just-above"),
        pytest.param(D(250), D("15.00"), id="above"),
    ],
)
def test_a_tier_charges_its_rate_on_the_part_of_a_base_over_its_threshold(
    base: Decimal, charge: Decimal
) -> None:
    assert LOW.charge_on(base) == charge


def test_a_tier_charges_an_unrounded_part() -> None:
    assert str(LOW.charge_on(D("100.01"))) == "0.0010"


@pytest.mark.parametrize("base", [D(100), D("100.00"), D(50)])
def test_a_tier_charges_a_plain_unsigned_zero_at_or_below_its_threshold(base: Decimal) -> None:
    charge = LOW.charge_on(base)

    assert str(charge) == "0"
    assert not charge.is_signed()


@pytest.mark.parametrize(
    ("base", "charge"),
    [
        pytest.param(D("99.99"), D(0), id="below"),
        pytest.param(D(100), D(0), id="at"),
        pytest.param(D("100.01"), D("0.0010"), id="just-above"),
        pytest.param(D(200), D("10.00"), id="under-the-maximum"),
        pytest.param(D(250), D(15), id="reaching-the-maximum"),
        pytest.param(D("250.01"), D(15), id="just-past-the-maximum"),
        pytest.param(D(1000), D(15), id="far-past-the-maximum"),
    ],
)
def test_a_tier_with_a_maximum_charges_its_rate_on_the_part_over_its_threshold_at_most_the_maximum(
    base: Decimal, charge: Decimal
) -> None:
    assert CAPPED.charge_on(base) == charge


def test_a_charge_exactly_at_the_maximum_keeps_its_computed_scale() -> None:
    assert str(CAPPED.charge_on(D(250))) == "15.00"


def test_a_tier_with_a_maximum_charges_an_unrounded_part_under_the_maximum() -> None:
    assert str(CAPPED.charge_on(D("100.01"))) == "0.0010"


def test_a_capped_charge_is_the_maximum_exactly() -> None:
    tier = SurchargeTier(D(100), Rate(D("0.10")), D("15.50"))

    assert str(tier.charge_on(D(1000))) == "15.50"


def test_a_zero_maximum_charges_nothing() -> None:
    tier = SurchargeTier(D(100), Rate(D("0.10")), D(0))

    assert tier.charge_on(D(1000)) == D(0)
    assert tier.charge_on(D(50)) == D(0)


@pytest.mark.parametrize("base", [D(100), D("100.00"), D(50)])
def test_a_tier_with_a_maximum_charges_a_plain_unsigned_zero_at_or_below_its_threshold(
    base: Decimal,
) -> None:
    charge = CAPPED.charge_on(base)

    assert str(charge) == "0"
    assert not charge.is_signed()


# --- the tiers --------------------------------------------------------------------------------


def test_holds_its_tiers_in_order() -> None:
    assert SurchargeTiers((LOW, HIGH)).tiers == (LOW, HIGH)


def test_holds_the_tiers_only() -> None:
    assert [field.name for field in fields(SurchargeTiers)] == ["tiers"]


def test_a_single_tier_is_enough() -> None:
    assert SurchargeTiers((LOW,)).tiers == (LOW,)


def test_equal_tiers_make_equal_values() -> None:
    assert SurchargeTiers((LOW, HIGH)) == SurchargeTiers(
        (SurchargeTier(D(100), Rate(D("0.10"))), SurchargeTier(D(300), Rate(D("0.25"))))
    )
    assert SurchargeTiers((LOW, HIGH)) != SurchargeTiers((LOW,))


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, SurchargeTiers((LOW,))).tiers = (HIGH,)


def test_is_hashable() -> None:
    assert hash(SurchargeTiers((LOW, HIGH))) == hash(SurchargeTiers((LOW, HIGH)))


def test_rejects_no_tiers() -> None:
    with pytest.raises(InvalidSurchargeTiersError, match="at least one tier"):
        SurchargeTiers(())


@pytest.mark.parametrize(
    "tiers",
    [
        pytest.param((HIGH, LOW), id="descending"),
        pytest.param((LOW, SurchargeTier(D(100), Rate(D("0.25")))), id="equal"),
        pytest.param(
            (LOW, SurchargeTier(D(500), Rate(D("0.2"))), HIGH), id="descending-after-ascending"
        ),
    ],
)
def test_rejects_thresholds_that_are_not_strictly_increasing(
    tiers: tuple[SurchargeTier, ...],
) -> None:
    with pytest.raises(InvalidSurchargeTiersError, match="strictly increasing"):
        SurchargeTiers(tiers)


@pytest.mark.parametrize(
    ("base", "charges"),
    [
        pytest.param(D(50), (D(0), D(0)), id="below-both"),
        pytest.param(D(250), (D("15.00"), D(0)), id="between"),
        pytest.param(D("300.01"), (D("20.0010"), D("0.0025")), id="just-above-both"),
        pytest.param(D(400), (D("30.00"), D("25.00")), id="above-both"),
    ],
)
def test_the_tiers_pair_each_tier_with_its_unrounded_charge_in_order(
    base: Decimal, charges: tuple[Decimal, ...]
) -> None:
    pairs = SurchargeTiers((LOW, HIGH)).charges(base)

    assert pairs == ((LOW, charges[0]), (HIGH, charges[1]))
    assert [str(charge) for _, charge in pairs] == [str(charge) for charge in charges]


@pytest.mark.parametrize(
    ("base", "charges"),
    [
        pytest.param(D(200), (D("10.00"), D(0)), id="under-the-maximum"),
        pytest.param(D(350), (D(15), D("12.50")), id="first-capped-second-not"),
        pytest.param(D(1000), (D(15), D(20)), id="both-capped"),
    ],
)
def test_the_tiers_pair_each_tier_with_its_capped_charge_in_order(
    base: Decimal, charges: tuple[Decimal, ...]
) -> None:
    # 10% over 100 at most 15, then 25% over 300 at most 20: a schedule of plateaus.
    top = SurchargeTier(D(300), Rate(D("0.25")), D(20))

    assert SurchargeTiers((CAPPED, top)).charges(base) == (
        (CAPPED, charges[0]),
        (top, charges[1]),
    )


def test_tiers_with_and_without_a_maximum_mix() -> None:
    assert SurchargeTiers((CAPPED, HIGH)).charges(D(400)) == (
        (CAPPED, D(15)),
        (HIGH, D("25.00")),
    )


def test_a_maximum_does_not_relax_the_threshold_order() -> None:
    with pytest.raises(InvalidSurchargeTiersError, match="strictly increasing"):
        SurchargeTiers((SurchargeTier(D(300), Rate(D("0.1")), D(5)), CAPPED))


def test_rates_need_not_increase() -> None:
    falling = (SurchargeTier(D(100), Rate(D("0.3"))), SurchargeTier(D(300), Rate(D("0.1"))))

    assert SurchargeTiers(falling).tiers == falling


# --- the kind ---------------------------------------------------------------------------------


def test_surcharge_tiers_kind() -> None:
    assert SURCHARGE_TIERS == ParameterKind("surcharge_tiers", SurchargeTiers)
    assert SURCHARGE_TIERS.name == "surcharge_tiers"
    assert SURCHARGE_TIERS.value_type is SurchargeTiers


def test_invalid_surcharge_tiers_is_a_domain_error() -> None:
    assert issubclass(InvalidSurchargeTiersError, DomainError)
