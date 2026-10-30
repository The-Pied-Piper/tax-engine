"""Tapered amount: a base amount plus a supplement reduced as a money artifact passes a threshold.

For amounts made of a base plus a supplement that is reduced in proportion to how far a figure
sits above a threshold, over a stated range, not below zero: the reduction is
`supplement × max(base − threshold, 0) / range`, computed as an exact fraction so nothing is
rounded before the rule. The output is
`rounding.apply(taper.base + max(supplement − reduction, 0))`, rounded once with the `taper`
dataset's rule, which defaults to no rounding; under no rounding a reduction with no finite
decimal expansion raises `decimal.Inexact`. At or below the threshold the output is base plus
supplement; at or above threshold plus range it is the base.

The class is `TaperedAmount` so that it does not share a name with the `Taper` value object it
reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.taper import TAPER, Taper
from tax_engine.domain.trace import TaperedAmountLine


@capability(identifier="tapered_amount")
class TaperedAmount(Capability):
    """Produces `output`: the `taper`'s base plus its supplement, tapered by `base`, rounded."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Taper]]] = {"taper": TAPER}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, taper: ParameterDataset[Taper], base: Money, output: Money) -> None:
        """Wire the capability: its taper dataset, the figure it reads, the kind it produces."""
        super().__init__(base=base, output=output)
        self._taper = taper
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        taper, rounding = self._taper.values, self._taper.rounding
        over = ExactFraction(base - taper.threshold)
        # Like the floored subtraction: a tie at zero gives a plain 0, never a signed one.
        excess = over if over > 0 else ExactFraction(0)
        reduction = ExactFraction(taper.supplement) * excess / ExactFraction(taper.range)
        remaining = ExactFraction(taper.supplement) - reduction
        kept = remaining if remaining > 0 else ExactFraction(0)
        result = rounding.apply(ExactFraction(taper.base) + kept)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                TaperedAmountLine(
                    self._output, self._base, base, taper, rounding, reduction, result
                ),
            ),
        )
