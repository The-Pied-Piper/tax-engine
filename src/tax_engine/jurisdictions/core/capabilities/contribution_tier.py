"""Contribution tier: a rate on the part of a money artifact inside a band, capped, exactly.

For contributions charged on the earnings between two bounds, up to a maximum: the contributory
earnings are `max(min(earnings, upper) - lower, 0)`, so earnings below the band (negative ones
too) contribute nothing and earnings above it count only up to the band. The output is
`min(rounding.apply(contributory × rate), maximum)`, rounded only with the `tier` dataset's rule,
which defaults to no rounding; the maximum applies after rounding and as given.

The class is `TieredContribution` so that it does not share a name with the `ContributionTier`
value object it reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import ContributionTierLine


@capability(identifier="contribution_tier")
class TieredContribution(Capability):
    """Produces `output`: the `tier` rate on the `earnings` inside its band, rounded and capped."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ContributionTier]]] = {
        "tier": CONTRIBUTION_TIER
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"earnings": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, tier: ParameterDataset[ContributionTier], earnings: Money, output: Money
    ) -> None:
        """Wire the capability: its tier dataset, the earnings it reads, the kind it produces."""
        super().__init__(earnings=earnings, output=output)
        self._tier = tier
        self._earnings = earnings
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        earnings = self._input(inputs, self._earnings).value
        tier, rounding = self._tier.values, self._tier.rounding
        inside = min(earnings, tier.upper) - tier.lower
        # Like the floored subtraction: a tie at zero produces a plain 0, never a signed one.
        contributory = inside if inside > 0 else Decimal(0)
        result = min(rounding.apply(contributory * tier.rate.value), tier.maximum)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                ContributionTierLine(
                    self._output, self._earnings, earnings, tier, rounding, contributory, result
                ),
            ),
        )
