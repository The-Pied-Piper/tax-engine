"""Trace line for a surtax factor: 1 plus the rate of each surtax tier a base is over."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import Money
from tax_engine.domain.parameters.surcharge_tiers import SurchargeTier
from tax_engine.domain.trace.base import TraceLine

__all__ = ["SurtaxFactorLine"]


@dataclass(frozen=True)
class SurtaxFactorLine(TraceLine):
    """The `factor` produced as `output`: 1 plus the rate of each of `tiers`, the tiers `base` is
    over, in the order of the capability's slots and of each dataset.

    `tiers` is empty when `base` is at or below every threshold. The factor is exact.
    """

    output: Money
    base: Money
    base_amount: Decimal
    tiers: tuple[SurchargeTier, ...]
    factor: Decimal

    @property
    def amount(self) -> Decimal:
        """The surtax factor."""
        return self.factor

    @property
    def label(self) -> str | None:
        """The label of the figure this line is about."""
        return self.output.label
