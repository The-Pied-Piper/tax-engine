"""Contribution tier rate: the rate a further dollar of earnings is charged by a contribution tier.

The output is the tier's rate when the earnings are at least its lower bound and under its upper
bound, otherwise 0: the rate of the next dollar, read from the same dataset the contribution reads.
A figure at the lower bound is inside, because the next dollar is the first of the band. A form line
that stops at its maximum equals the upper bound from there on, so a figure at the upper bound is
outside: the next dollar adds nothing to the contribution.
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
from tax_engine.jurisdictions.ca.trace.contribution_tier_rate import ContributionTierRateLine


@capability(identifier="contribution_tier_rate")
class TieredContributionRate(Capability):
    """Produces `output`: the `tier` rate when `earnings` is at least its lower bound and under
    its upper bound, otherwise 0."""

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
        values = self._tier.values
        rate = values.next_dollar_rate(earnings)
        return CapabilityResult(
            outputs=(Artifact(self._output, rate),),
            trace=(ContributionTierRateLine(self._output, self._earnings, earnings, values, rate),),
        )
