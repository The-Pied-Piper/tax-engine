"""Given or contribution tier: a figure the filer gives, else a tier result on the earnings.

For a form line that is given on the form when the filer has it, and computed from the earnings
when left blank, such as T2204 line 4. A given figure is the output unchanged: no rounding, no cap,
its scale kept. A blank `given` (its rule is `compute` in the manifest) is the tier result on the
`earnings`, exactly as `TieredContribution` computes it. Only `given` may be blank; `earnings` is
refused when blank.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.jurisdictions.ca.capabilities.contribution_tier import _TierCalculation
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tax_engine.jurisdictions.ca.trace import GivenAmountLine


@capability(identifier="given_or_contribution_tier")
class GivenOrTieredContribution(_TierCalculation):
    """Produces `output`: the `given` figure unchanged, or, when `given` is blank, the `tier` rate
    on the `earnings` inside its band, rounded and capped."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[ContributionTier]]] = {
        "tier": CONTRIBUTION_TIER
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"given": Decimal, "earnings": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"given"})

    def __init__(
        self,
        tier: ParameterDataset[ContributionTier],
        given: Money,
        earnings: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its tier dataset, the figure given, the earnings it reads, the kind
        it produces."""
        super().__init__(given=given, earnings=earnings, output=output)
        self._tier = tier
        self._given = given
        self._earnings = earnings
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        given = self._input(inputs, self._given)
        if not given.is_blank:
            return CapabilityResult(
                outputs=(Artifact(self._output, given.value),),
                trace=(
                    GivenAmountLine(
                        output=self._output,
                        given=self._given,
                        given_amount=given.value,
                    ),
                ),
            )
        earnings = self._input(inputs, self._earnings).value
        return self._tier_result(self._tier, self._earnings, self._output, earnings)
