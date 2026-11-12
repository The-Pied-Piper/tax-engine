"""Surtax factor: 1 plus the rate of each surtax tier whose threshold a money artifact is over.

ON428 line 66 "(Line 65 minus $5,710) multiplied by 20%" and line 67 "(Line 65 minus $7,307)
multiplied by 36%" each charge a rate on line 65 above a threshold, so one more dollar of Ontario
tax adds 1 plus the rate of every tier line 65 is over. A base exactly at a threshold is not over
it (that tier's charge is 0). The factor is exact: no rounding rule is applied to it.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.surcharge_tiers import SURCHARGE_TIERS, SurchargeTiers
from tax_engine.jurisdictions.ca_on.trace import SurtaxFactorLine


@capability(identifier="surtax_factor")
class SurtaxFactor(Capability):
    """Produces `output`: 1 plus the rate of each tier of `line_66` and `line_67` that `base` is
    over."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[SurchargeTiers]]] = {
        "line_66": SURCHARGE_TIERS,
        "line_67": SURCHARGE_TIERS,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        line_66: ParameterDataset[SurchargeTiers],
        line_67: ParameterDataset[SurchargeTiers],
        base: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its two tier datasets, the figure it reads, the kind it makes."""
        super().__init__(base=base, output=output)
        self._line_66 = line_66
        self._line_67 = line_67
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        over = tuple(
            tier
            for dataset in (self._line_66, self._line_67)
            for tier, charge in dataset.values.charges(base)
            if charge > 0
        )
        factor = Decimal(1) + sum((tier.rate.value for tier in over), Decimal(0))
        return CapabilityResult(
            outputs=(Artifact(self._output, factor),),
            trace=(SurtaxFactorLine(self._output, self._base, base, over, factor),),
        )
