"""Contribution tiers: a rate on a band of earnings, with a maximum contribution.

A tier holds a `Rate`, the band's `lower` and `upper` bounds and the `maximum` contribution, all
exact, as a form states them. The code holds no jurisdiction's tiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidContributionTierError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import Rate


@dataclass(frozen=True)
class ContributionTier:
    """A rate on the earnings from `lower` to `upper`, at most `maximum`; checked when built."""

    rate: Rate
    lower: Decimal
    upper: Decimal
    maximum: Decimal

    def __post_init__(self) -> None:
        """Check: a `Rate`, finite Decimal figures, `0 <= lower < upper` and `maximum >= 0`."""
        if not isinstance(self.rate, Rate):
            raise TypeError(
                f"contribution tier rate must be a Rate, got {type(self.rate).__name__}"
            )
        figures = (("lower", self.lower), ("upper", self.upper), ("maximum", self.maximum))
        for name, value in figures:
            if not isinstance(value, Decimal):
                raise TypeError(
                    f"contribution tier {name} must be a Decimal, got {type(value).__name__}"
                )
            if not value.is_finite():
                raise InvalidContributionTierError(
                    f"contribution tier {name} must be finite, got {value}"
                )
        if self.lower < 0:
            raise InvalidContributionTierError(
                f"contribution tier lower must not be negative, got {self.lower}"
            )
        if not self.lower < self.upper:
            raise InvalidContributionTierError(
                f"contribution tier lower must be below upper, got {self.lower} and {self.upper}"
            )
        if self.maximum < 0:
            raise InvalidContributionTierError(
                f"contribution tier maximum must not be negative, got {self.maximum}"
            )


CONTRIBUTION_TIER: ParameterKind[ContributionTier] = ParameterKind(
    "contribution_tier", ContributionTier
)
