"""Claim reductions: what a form takes off an expense claim before it counts.

A reduction is the lesser of a `ceiling` and a `rate` of a figure (such as a person's net income),
and the claim may also have an optional per-claim `maximum` on what is left. Like `Rate`, the
value object checks itself. The code holds no jurisdiction's figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidClaimReductionError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate


@dataclass(frozen=True)
class ClaimReduction:
    """A `rate`, a `ceiling` of zero or more and an optional `maximum` of zero or more, exact.

    A non-finite or negative ceiling or maximum is refused when it is built.
    """

    rate: Rate
    ceiling: Decimal
    maximum: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Rate):
            raise TypeError(f"rate must be a Rate, got {type(self.rate).__name__}")
        self._check("ceiling", self.ceiling)
        if self.maximum is not None:
            self._check("maximum", self.maximum)

    @staticmethod
    def _check(name: str, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError(f"{name} must be a Decimal, got {type(value).__name__}")
        if not value.is_finite():
            raise InvalidClaimReductionError(f"{name} must be finite, got {value}")
        if value < 0:
            raise InvalidClaimReductionError(f"{name} must not be negative, got {value}")


CLAIM_REDUCTION: ParameterKind[ClaimReduction] = ParameterKind("claim_reduction", ClaimReduction)
