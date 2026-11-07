"""BracketColumnFigure: one printed figure of the bracket column a base falls in, unrounded.

A form's bracket table prints, per column, a lower bound, a rate and a tax at the column's start;
a form line reads one of them for the column its taxable base falls in. The three capabilities
here are thin subclasses of one undecorated base, each giving one figure: BracketColumnLowerBound
its lower bound, BracketColumnRate its rate, BracketColumnTaxAtStart its tax at the start. The
manifest's params carry only datasets, so the figure is chosen by the class, not by an option.

The column is chosen as in `progressive_tax`: a base exactly at a threshold falls in the lower
column. The figure is the schedule's own, printed as it is: the capability never rounds it, since
the schedule already rounds its tax at each start by its own rule.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.brackets import BRACKETS, BracketColumn, BracketSchedule
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import BracketColumnFigureLine, TraceLine


class BracketColumnFigure(Capability):
    """Produces `output`: one figure of the `schedule` column that the consumed `base` falls in.

    Undecorated: a subclass gives the figure's `FIGURE_NAME` and `_figure`, and carries the
    identifier. Consumes `base` and produces `output`, both Decimal.
    """

    FIGURE_NAME: ClassVar[str]
    """The figure's name as the trace and its English text give it, e.g. "lower bound"."""

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

    @abstractmethod
    def _figure(self, column: BracketColumn) -> Decimal:
        """The one figure of `column` this class produces."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        column = self._schedule.values.column_for(base)
        figure = self._figure(column)
        trace: tuple[TraceLine, ...] = (
            BracketColumnFigureLine(base_amount=base, name=self.FIGURE_NAME, figure=figure),
        )
        return CapabilityResult(outputs=(Artifact(self._output, figure),), trace=trace)


@capability(identifier="bracket_column_lower_bound")
class BracketColumnLowerBound(BracketColumnFigure):
    """Produces `output`: the lower bound of the column the consumed `base` falls in."""

    FIGURE_NAME = "lower bound"

    def _figure(self, column: BracketColumn) -> Decimal:
        return column.lower


@capability(identifier="bracket_column_rate")
class BracketColumnRate(BracketColumnFigure):
    """Produces `output`: the rate of the column the consumed `base` falls in."""

    FIGURE_NAME = "rate"

    def _figure(self, column: BracketColumn) -> Decimal:
        return column.rate


@capability(identifier="bracket_column_tax_at_start")
class BracketColumnTaxAtStart(BracketColumnFigure):
    """Produces `output`: the tax at the start of the column the consumed `base` falls in."""

    FIGURE_NAME = "tax at start"

    def _figure(self, column: BracketColumn) -> Decimal:
        return column.tax_at_start
