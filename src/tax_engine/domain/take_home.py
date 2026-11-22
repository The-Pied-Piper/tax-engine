"""Take-home pay: what a jurisdiction declares, what is asked and what is answered.

A jurisdiction's manifest declares where each take-home figure is read (`TakeHomeFigures`); the
request and the result carry only what a caller gives and gets. The sum and the rounding to cents
are the domain's own rule, in `TakeHomeResult.of`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.errors import InvalidManifestError
from tax_engine.domain.jurisdiction_code import JurisdictionCode

CENTS = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class FigureReference:
    """Where a figure is read: the form that exports it and its kind, by identifier."""

    form: str
    kind: str


@dataclass(frozen=True, slots=True)
class TakeHomeFigures:
    """The figures a jurisdiction's take-home answer is made of, by identifier.

    `salary` is the kind of the one input the caller gives. `income_tax` is the figure of that
    name; `deductions` are the other figures taken off the salary, each under the name its answer
    carries. The total taken off the salary is `income_tax` plus every one of them.
    """

    salary: str
    income_tax: FigureReference
    deductions: tuple[tuple[str, FigureReference], ...]
    average_income_tax_rate: FigureReference
    marginal_income_tax_rate: FigureReference

    INCOME_TAX = "income_tax"

    def __post_init__(self) -> None:
        object.__setattr__(self, "deductions", tuple(self.deductions))
        names = [name for name, _ in self.deductions]
        for name in names:
            if names.count(name) > 1 or name == self.INCOME_TAX:
                raise InvalidManifestError(f"take_home: deduction {name!r} is named twice")

    @property
    def figures(self) -> tuple[tuple[str, FigureReference], ...]:
        """Each figure of the total with its name: the income tax, then the deductions."""
        return ((self.INCOME_TAX, self.income_tax), *self.deductions)

    @property
    def references(self) -> tuple[FigureReference, ...]:
        """Every figure that is read, rates included."""
        return (
            *(reference for _, reference in self.figures),
            self.average_income_tax_rate,
            self.marginal_income_tax_rate,
        )


@dataclass(frozen=True, slots=True)
class TakeHomeRequest:
    """The jurisdiction, tax year and salary to answer for; the trace only when asked."""

    jurisdiction: JurisdictionCode
    tax_year: int
    salary: Decimal
    include_trace: bool = False


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
    """The answer: figures exact, the total and the take-home in whole cents.

    `figures` holds the income tax then each deduction, as computed; `income_tax` is the first of
    them in whole cents. `trace` is `None` unless it was asked for.
    """

    salary: Decimal
    figures: tuple[DeductionFigure, ...]
    total_deductions: Decimal
    income_tax: Decimal
    take_home: Decimal
    unit: UnitDescription
    average_income_tax_rate: Rate
    marginal_income_tax_rate: Rate
    trace: tuple[FormTrace, ...] | None

    @classmethod
    def of(
        cls,
        salary: Decimal,
        figures: Iterable[DeductionFigure],
        unit: UnitDescription,
        average_income_tax_rate: Rate,
        marginal_income_tax_rate: Rate,
        trace: tuple[FormTrace, ...] | None,
    ) -> TakeHomeResult:
        """Take-home pay is the salary minus the sum of the figures, in whole cents."""
        kept = tuple(figures)
        total = sum((figure.amount for figure in kept), Decimal(0))
        income_tax = sum(
            (figure.amount for figure in kept if figure.name == TakeHomeFigures.INCOME_TAX),
            Decimal(0),
        )
        return cls(
            salary=salary.quantize(CENTS),
            figures=kept,
            total_deductions=total.quantize(CENTS),
            income_tax=income_tax.quantize(CENTS),
            take_home=(salary - total).quantize(CENTS),
            unit=unit,
            average_income_tax_rate=average_income_tax_rate,
            marginal_income_tax_rate=marginal_income_tax_rate,
            trace=trace,
        )
