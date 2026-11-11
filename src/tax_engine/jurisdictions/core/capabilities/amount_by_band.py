"""AmountFromBand: the amount of the band of a chart that a base falls in.

An income at a boundary is in the lower band. The band's flat or sloped figure is unrounded until
the output, which the `table` dataset's rounding rule rounds once. Records one `AmountByBandLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND, AmountByBand
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import AmountByBandLine


@capability(identifier="amount_by_band")
class AmountFromBand(Capability):
    """Produces `output`: the figure of the `table`'s band that the consumed `base` falls in."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[AmountByBand]]] = {"table": AMOUNT_BY_BAND}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, table: ParameterDataset[AmountByBand], base: Money, output: Money) -> None:
        """Wire the capability: its chart dataset, the kind it reads the band from, the kind it
        produces."""
        super().__init__(base=base, output=output)
        self._table = table
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        rounding = self._table.rounding
        band = self._table.values.band_for(base)
        result = rounding.apply(band.amount_at(base))
        line = AmountByBandLine(
            output=self._output,
            base=self._base,
            base_amount=base,
            over=band.over,
            flat_amount=band.amount,
            minus=band.minus,
            rate=band.rate,
            plus=band.plus,
            rounding=rounding,
            result=result,
        )
        return CapabilityResult(outputs=(Artifact(self._output, result),), trace=(line,))
