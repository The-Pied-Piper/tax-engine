"""Tiered surcharge: a rate on the part of a money artifact over each tier's threshold, summed.

For the return lines that read "(base minus threshold) multiplied by rate (if negative, enter 0)",
one per tier, then added; a tier with a maximum charges at most that (a schedule of plateaus). The
tiers give each tier's unrounded, capped charge (`SurchargeTiers.charges`); the capability rounds
each with the `tiers` dataset's rule, which defaults to no rounding, and outputs the sum of the
rounded parts. Where it is used the base is never negative (a tax after credits, floored at zero);
a negative base yields zero parts.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.surcharge_tiers import SURCHARGE_TIERS, SurchargeTiers
from tax_calculator.domain.trace import SurchargeTierLine


@capability(identifier="tiered_surcharge")
class TieredSurcharge(Capability):
    """Produces `output`: each tier's rate on the consumed `base` over its threshold, summed."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[SurchargeTiers]]] = {"tiers": SURCHARGE_TIERS}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, tiers: ParameterDataset[SurchargeTiers], base: Money, output: Money) -> None:
        """Wire the capability: its tiers dataset, the kind it surcharges, the kind it produces."""
        super().__init__(base=base, output=output)
        self._tiers = tiers
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        rounding = self._tiers.rounding
        parts = tuple(
            (tier, rounding.apply(charge)) for tier, charge in self._tiers.values.charges(base)
        )
        total = sum((part for _, part in parts), Decimal(0))
        lines = tuple(
            SurchargeTierLine(
                output=self._output,
                base=self._base,
                base_amount=base,
                threshold=tier.threshold,
                rate=tier.rate,
                rounding=rounding,
                part=part,
                maximum=tier.maximum,
            )
            for tier, part in parts
        )
        return CapabilityResult(outputs=(Artifact(self._output, total),), trace=lines)
