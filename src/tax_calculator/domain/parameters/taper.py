"""Tapers: a base amount plus a supplement that is reduced to nothing over a range of a figure.

A taper holds the four figures a form prints, all exact: the `base` amount, the `supplement` added
to it, the `threshold` above which the supplement is reduced and the `range` over which it is
reduced to nothing. The full amount, base plus supplement, is not stored. The code holds no
jurisdiction's tapers.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidTaperError
from tax_calculator.domain.parameters.kind import ParameterKind


@dataclass(frozen=True)
class Taper:
    """`base` plus `supplement`, reduced over `range` above `threshold`; checked when built."""

    base: Decimal
    supplement: Decimal
    threshold: Decimal
    range: Decimal

    def __post_init__(self) -> None:
        """Check: finite Decimal figures, `base`, `supplement` and `threshold` >= 0, `range` > 0."""
        figures = (
            ("base", self.base),
            ("supplement", self.supplement),
            ("threshold", self.threshold),
            ("range", self.range),
        )
        for name, value in figures:
            if not isinstance(value, Decimal):
                raise TypeError(f"taper {name} must be a Decimal, got {type(value).__name__}")
            if not value.is_finite():
                raise InvalidTaperError(f"taper {name} must be finite, got {value}")
        if self.base < 0:
            raise InvalidTaperError(f"taper base must not be negative, got {self.base}")
        if self.supplement < 0:
            raise InvalidTaperError(f"taper supplement must not be negative, got {self.supplement}")
        if self.threshold < 0:
            raise InvalidTaperError(f"taper threshold must not be negative, got {self.threshold}")
        if not self.range > 0:
            raise InvalidTaperError(f"taper range must be positive, got {self.range}")


TAPER: ParameterKind[Taper] = ParameterKind("taper", Taper)
