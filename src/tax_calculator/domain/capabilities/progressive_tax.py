"""Progressive tax: a bracket schedule applied to a taxable base.

One mechanism, wired per use: the same class computes, say, national and
regional basic tax from the same base, with different schedules and outputs.
It computes the form's two lines for the bracket the base falls in: the rate on the
excess over the bracket's lower, plus the tax at the bracket's start, which the schedule
computes by its own rule. Rounding happens once, on the total, using the schedule dataset's
rule.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import BracketColumnLine, RoundedTotalLine, TraceLine


@capability(identifier="progressive_tax")
class ProgressiveTax(Capability):
    """Produces `output`: tax on the consumed `base` from the `schedule` dataset's brackets."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[BracketSchedule]]] = {"schedule": BRACKETS}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, base: Money, output: Money, schedule: ParameterDataset[BracketSchedule]
    ) -> None:
        """Wire the capability: the kinds it consumes and produces, and its schedule dataset."""
        super().__init__(base=base, output=output)
        self._base = base
        self._output = output
        self._schedule = schedule

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        schedule, rounding = self._schedule.values, self._schedule.rounding
        column = schedule.column_for(base)
        tax = rounding.apply(column.tax)
        trace: tuple[TraceLine, ...] = (
            BracketColumnLine(
                column.lower, column.rate, column.excess, column.tax_at_start, column.tax
            ),
            RoundedTotalLine(self._output, self._base, base, rounding, tax),
        )
        return CapabilityResult(outputs=(Artifact(self._output, tax),), trace=trace)
