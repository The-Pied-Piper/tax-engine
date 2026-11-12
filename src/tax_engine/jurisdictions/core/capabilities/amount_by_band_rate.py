"""AmountByBandRate: the rate of the band of a chart that a base falls in.

An income at a boundary is in the lower band. A flat band has no rate, so it gives 0. The rate is
never rounded, whatever the `table` dataset's rounding rule. Records one `AmountByBandRateLine`.
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
from tax_engine.domain.trace import AmountByBandRateLine


@capability(identifier="amount_by_band_rate")
class AmountByBandRate(Capability):
    """Produces `output`: the rate of the `table`'s band that the consumed `base` falls in."""

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
        band = self._table.values.band_for(base)
        result = band.rate.value if band.rate is not None else Decimal(0)
        line = AmountByBandRateLine(
            output=self._output,
            base=self._base,
            base_amount=base,
            over=band.over,
            rate=band.rate,
            result=result,
        )
        return CapabilityResult(outputs=(Artifact(self._output, result),), trace=(line,))
