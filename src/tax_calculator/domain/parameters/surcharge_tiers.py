"""Surcharge tiers: a rate charged on the part of a base over each tier's threshold.

The tiers are parameter data, resolved per (family, tax_year); the code holds no jurisdiction's
thresholds or rates. A tier charges its rate on the part of a base over its threshold, at most its
optional maximum, unrounded; rounding the part and summing the tiers are the capability's.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidSurchargeTiersError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate


@dataclass(frozen=True)
class SurchargeTier:
    """`rate` charged on the part of a base over `threshold`, at most `maximum` when set.

    The threshold and the maximum are exact; a tier without a maximum is uncapped.
    """

    threshold: Decimal
    rate: Rate
    maximum: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.threshold, Decimal):
            raise TypeError(
                f"tier threshold must be a Decimal, got {type(self.threshold).__name__}"
            )
        if not self.threshold.is_finite():
            raise InvalidSurchargeTiersError(f"tier threshold must be finite, got {self.threshold}")
        if self.threshold < 0:
            raise InvalidSurchargeTiersError(
                f"tier threshold must not be negative, got {self.threshold}"
            )
        if not isinstance(self.rate, Rate):
            raise TypeError(f"tier rate must be a Rate, got {type(self.rate).__name__}")
        if self.maximum is not None:
            if not isinstance(self.maximum, Decimal):
                raise TypeError(
                    f"tier maximum must be a Decimal, got {type(self.maximum).__name__}"
                )
            if not self.maximum.is_finite():
                raise InvalidSurchargeTiersError(f"tier maximum must be finite, got {self.maximum}")
            if self.maximum < 0:
                raise InvalidSurchargeTiersError(
                    f"tier maximum must not be negative, got {self.maximum}"
                )
            if not self.maximum:
                # A zero maximum is a plain zero (its scale kept), never a negative zero.
                object.__setattr__(self, "maximum", self.maximum.copy_abs())

    def charge_on(self, base: Decimal) -> Decimal:
        """The unrounded charge on `base`: the rate on its part over the threshold, else zero, at
        most the maximum when set (a capped charge is the maximum itself, its scale kept)."""
        over = base - self.threshold
        # At or below the threshold the charge is a plain zero: no scale, never a negative zero.
        if over <= 0:
            return Decimal(0)
        charge = over * self.rate.value
        if self.maximum is not None and charge > self.maximum:
            return self.maximum
        return charge


@dataclass(frozen=True)
class SurchargeTiers:
    """At least one tier, thresholds strictly increasing; rates may rise or fall."""

    tiers: tuple[SurchargeTier, ...]

    def __post_init__(self) -> None:
        if not self.tiers:
            raise InvalidSurchargeTiersError("surcharge tiers need at least one tier")
        for index, (below, above) in enumerate(zip(self.tiers, self.tiers[1:], strict=False)):
            if above.threshold <= below.threshold:
                raise InvalidSurchargeTiersError(
                    f"tiers[{index + 1}] threshold {above.threshold} does not exceed "
                    f"tiers[{index}] threshold {below.threshold}; "
                    "thresholds must be strictly increasing"
                )

    def charges(self, base: Decimal) -> tuple[tuple[SurchargeTier, Decimal], ...]:
        """Each tier, in order, with its unrounded, capped charge on `base`."""
        return tuple((tier, tier.charge_on(base)) for tier in self.tiers)


SURCHARGE_TIERS: ParameterKind[SurchargeTiers] = ParameterKind("surcharge_tiers", SurchargeTiers)
