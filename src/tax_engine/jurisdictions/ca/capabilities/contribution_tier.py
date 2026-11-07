"""Contribution tier: a rate on the part of a money artifact inside a band, capped, exactly.

For contributions charged on the earnings between two bounds, up to a maximum: the contributory
earnings are `max(min(earnings, upper) - lower, 0)`, so earnings below the band (negative ones
too) contribute nothing and earnings above it count only up to the band. The output is
`min(rounding.apply(contributory × rate), maximum)`, rounded only with the `tier` dataset's rule,
which defaults to no rounding; the maximum applies after rounding and as given.

The class is `TieredContribution` so that it does not share a name with the `ContributionTier`
value object it reads. The calculation lives in `TierCalculation`, a parent class with no
identifier, so the capabilities that compute a tier result share it and each names its own slots.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tax_engine.jurisdictions.ca.trace import ContributionTierLine


class TierCalculation(Capability):
    """The tier calculation shared by the capabilities that compute a tier result on earnings.

    Has no identifier, so it is not registered; a subclass is decorated with `@capability`, names
    its own slots in `__init__`, and calls `_tier_result` with the earnings it read.
    """

    def _tier_result(
        self,
        tier: ParameterDataset[ContributionTier],
        earnings_kind: Money,
        output: Money,
        earnings: Decimal,
    ) -> CapabilityResult:
        """Produce `output`: the `tier` rate on the part of `earnings` inside its band, rounded and
        capped, with the `ContributionTierLine` that records it."""
        values, rounding = tier.values, tier.rounding
        inside = min(earnings, values.upper) - values.lower
        # Like the floored subtraction: a tie at zero produces a plain 0, never a signed one.
        contributory = inside if inside > 0 else Decimal(0)
        result = min(rounding.apply(contributory * values.rate.value), values.maximum)
        return CapabilityResult(
            outputs=(Artifact(output, result),),
            trace=(
                ContributionTierLine(
                    output, earnings_kind, earnings, values, rounding, contributory, result
                ),
            ),
        )


@capability(identifier="contribution_tier")
class TieredContribution(TierCalculation):
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
        return self._tier_result(self._tier, self._earnings, self._output, earnings)
