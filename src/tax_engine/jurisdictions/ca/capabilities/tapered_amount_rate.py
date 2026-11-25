"""Tapered amount rate: how fast a tapered amount falls for a further dollar of its base.

The output is the `taper`'s supplement over its range while the base is over the taper's threshold
and at most the end of its range, otherwise 0, rounded once with the `rounding` dataset's rule (the
quotient is generally inexact). A base at the threshold is outside, a base at the end of the range
is inside: a bracket or taper reads the band below at an exact edge.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.parameter_shapes.taper import TAPER, Taper
from tax_engine.jurisdictions.ca.trace.tapered_amount_rate import TaperedAmountRateLine


@capability(identifier="tapered_amount_rate")
class TaperedAmountRate(Capability):
    """Produces `output`: the `taper`'s supplement over its range inside its taper, else 0."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Any]]] = {
        "taper": TAPER,
        "rounding": ROUNDING_ONLY,
    }
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        taper: ParameterDataset[Taper],
        rounding: ParameterDataset[RoundingOnly],
        base: Money,
        output: Money,
    ) -> None:
        """Wire the capability: its taper and rounding datasets, the figure it reads, the output."""
        super().__init__(base=base, output=output)
        self._taper = taper
        self._rounding = rounding
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        taper, rounding = self._taper.values, self._rounding.rounding
        result = rounding.apply(taper.supplement_per_dollar) if taper.falls_at(base) else Decimal(0)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(TaperedAmountRateLine(self._output, self._base, base, taper, rounding, result),),
        )
