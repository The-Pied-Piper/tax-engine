"""Amount by band: a printed chart of figures by income band, the `amount_by_band` values.

See docs/parameter-data.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidAmountByBandError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate


@dataclass(frozen=True)
class AmountBand:
    """One row of a chart: from `over` (exclusive), a flat `amount` or a sloped `minus`, `rate`
    and `plus`, checked when built."""

    over: Decimal
    amount: Decimal | None = None
    minus: Decimal | None = None
    rate: Rate | None = None
    plus: Decimal | None = None

    def __post_init__(self) -> None:
        """Check the types and finiteness of the figures, then the row's shape."""
        self._check_figure("over", self.over)
        for name, figure in (("amount", self.amount), ("minus", self.minus), ("plus", self.plus)):
            if figure is not None:
                self._check_figure(name, figure)
        if self.rate is not None and not isinstance(self.rate, Rate):
            raise TypeError(f"band rate must be a Rate, got {type(self.rate).__name__}")
        if not self._has_flat_shape() and not self._has_sloped_shape():
            raise InvalidAmountByBandError(
                f"a band from {self.over} gives either amount alone or minus, rate and plus "
                "together"
            )
        # A zero figure is a plain zero (its scale kept), never a negative zero.
        if not self.over:
            object.__setattr__(self, "over", self.over.copy_abs())
        if self.amount is not None and not self.amount:
            object.__setattr__(self, "amount", self.amount.copy_abs())
        if self.minus is not None and not self.minus:
            object.__setattr__(self, "minus", self.minus.copy_abs())
        if self.plus is not None and not self.plus:
            object.__setattr__(self, "plus", self.plus.copy_abs())

    def _has_flat_shape(self) -> bool:
        return (
            self.amount is not None
            and self.minus is None
            and self.rate is None
            and self.plus is None
        )

    def _has_sloped_shape(self) -> bool:
        return (
            self.amount is None
            and self.minus is not None
            and self.rate is not None
            and self.plus is not None
        )

    @staticmethod
    def _check_figure(name: str, figure: Decimal) -> None:
        if not isinstance(figure, Decimal):
            raise TypeError(f"band {name} must be a Decimal, got {type(figure).__name__}")
        if not figure.is_finite():
            raise InvalidAmountByBandError(f"band {name} must be finite, got {figure}")
        if figure < 0:
            raise InvalidAmountByBandError(f"band {name} must not be negative, got {figure}")

    def amount_at(self, income: Decimal) -> Decimal:
        """The band's figure at `income`, unrounded: its flat amount, or the sloped figure."""
        if self.amount is not None:
            return self.amount
        if self.minus is None or self.rate is None or self.plus is None:
            # Unreachable: __post_init__ gives a row either a flat amount or all three sloped
            # figures.
            raise InvalidAmountByBandError(f"a band from {self.over} has no figure")
        return (income - self.minus) * self.rate.value + self.plus


@dataclass(frozen=True)
class AmountByBand:
    """At least one band, the first from 0, each `over` strictly above the one before."""

    bands: tuple[AmountBand, ...]

    def __post_init__(self) -> None:
        """Check the bands are present, start at 0 and have strictly increasing `over`s."""
        if not self.bands:
            raise InvalidAmountByBandError("amount by band must not be empty")
        if self.bands[0].over != 0:
            raise InvalidAmountByBandError(
                f"the first band must start at 0, got {self.bands[0].over}"
            )
        for index, (below, above) in enumerate(zip(self.bands, self.bands[1:], strict=False)):
            if above.over <= below.over:
                raise InvalidAmountByBandError(
                    f"bands[{index + 1}] over {above.over} does not exceed bands[{index}] over "
                    f"{below.over}; overs must be strictly increasing"
                )

    def band_for(self, income: Decimal) -> AmountBand:
        """The band `income` falls in: the one whose `over` is the highest strictly below it, so
        an income at a boundary falls in the lower band, as in `BracketSchedule.column_for`."""
        if not isinstance(income, Decimal):
            raise TypeError(f"income must be a Decimal, got {type(income).__name__}")
        if income < 0:
            raise ValueError(f"income must not be negative, got {income}")
        chosen = self.bands[0]
        for band in self.bands[1:]:
            if income <= band.over:
                break
            chosen = band
        return chosen


AMOUNT_BY_BAND: ParameterKind[AmountByBand] = ParameterKind("amount_by_band", AmountByBand)
