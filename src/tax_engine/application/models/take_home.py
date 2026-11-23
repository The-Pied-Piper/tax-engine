"""What a take-home answer holds, in the answer's language.

The figures and sums are the domain's (`tax_engine.domain.take_home`); these are the use case's
input and output, with the unit text and the trace sentences a `TakeHomeText` port supplies.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class UnitDescription:
    """How a figure is written with its unit, in the answer's language."""

    name: str
    placement: str
    singular: str
    plural: str
    spaced: bool
    as_percentage: bool


@dataclass(frozen=True, slots=True)
class Rate:
    value: Decimal
    unit: UnitDescription


@dataclass(frozen=True, slots=True)
class DeductionFigure:
    name: str
    amount: Decimal


@dataclass(frozen=True, slots=True)
class TraceEntry:
    """One line of a form's trace, as shown: the figure it is about, its amount and its sentence."""

    label: str | None
    name: str | None
    reference: str | None
    amount: Decimal | None
    text: str
    unit: UnitDescription | None


@dataclass(frozen=True, slots=True)
class FormTrace:
    form: str
    name: str | None
    lines: tuple[TraceEntry, ...]


@dataclass(frozen=True, slots=True)
class TakeHomeResult:
    """The answer: figures exact, the total and the take-home plain sums of them.

    `figures` holds the income tax then each deduction, as computed; `income_tax` is the first of
    them. A rate is `None` where the jurisdiction declares none; `trace` is `None`
    unless it was asked for.
    """

    salary: Decimal
    figures: tuple[DeductionFigure, ...]
    total_deductions: Decimal
    income_tax: Decimal
    take_home: Decimal
    unit: UnitDescription
    average_income_tax_rate: Rate | None
    marginal_income_tax_rate: Rate | None
    trace: tuple[FormTrace, ...] | None
