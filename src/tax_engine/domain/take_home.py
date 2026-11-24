"""Take-home pay: where a jurisdiction's figures are read and the rules that combine them.

A jurisdiction's manifest declares where each take-home figure is read (`TakeHomeFigures`). What a
caller asks and is answered, and how the answer is worded, belong to the application layer; the
rules that make the answer right are here: a figure is a decimal read from one worksheet, the
figures taken off share one unit, and the total and the take-home are plain sums of them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.errors import InvalidManifestError
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet

CENTS = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class FigureValue:
    """A figure as read: its exact amount and its unit, `None` when the figure has none."""

    amount: Decimal
    unit: Unit | None


@dataclass(frozen=True, slots=True)
class FigureReference:
    """Where a figure is read: the form whose worksheet holds it and its kind, by identifier."""

    form: str
    kind: str

    def read(
        self, sheets: Mapping[str, Sequence[Worksheet]], kinds: ArtifactRegistry
    ) -> FigureValue:
        """The figure off the one worksheet of its form.

        Raises InvalidManifestError if the form does not have exactly one worksheet or the figure
        is not a decimal.
        """
        found = sheets[self.form]
        if len(found) != 1:
            raise InvalidManifestError(
                f"take_home: form {self.form!r} has {len(found)} worksheets, not one"
            )
        artifact = found[0].get(kinds.kind(self.kind))
        if not isinstance(artifact.value, Decimal):
            raise InvalidManifestError(f"take_home: {self.kind!r} is not a decimal")
        return FigureValue(artifact.value, artifact.unit)


@dataclass(frozen=True, slots=True)
class TakeHomeFigures:
    """The figures a jurisdiction's take-home answer is made of, by identifier.

    `salary` is the kind of the one input the caller gives. `income_tax` is the figure of that
    name; `deductions` are the other figures taken off the salary, each under the name its answer
    carries. The total taken off the salary is `income_tax` plus every one of them. The marginal
    rates are declared only where the jurisdiction's return computes them.
    """

    salary: str
    income_tax: FigureReference
    deductions: tuple[tuple[str, FigureReference], ...]
    average_tax_rate: FigureReference | None = None
    marginal_tax_rate: FigureReference | None = None

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
        """Every figure that is read, the rates included."""
        rates = (self.average_tax_rate, self.marginal_tax_rate)
        return (
            *(reference for _, reference in self.figures),
            *(rate for rate in rates if rate is not None),
        )


def shared_unit(who: str, values: Iterable[FigureValue]) -> Unit:
    """The one unit every figure in `values` is in; `who` names the answer in the error.

    Raises InvalidManifestError if they are in different units or any has none.
    """
    units = {value.unit for value in values}
    if len(units) != 1 or None in units:
        raise InvalidManifestError(f"{who}: the figures do not share one unit")
    (unit,) = units
    assert unit is not None  # `None in units` was refused above
    return unit


def rate_unit(who: str, value: FigureValue) -> Unit:
    """The unit of a rate; a rate without one is refused as InvalidManifestError."""
    if value.unit is None:
        raise InvalidManifestError(f"{who}: the rate has no unit")
    return value.unit


@dataclass(frozen=True, slots=True)
class Totals:
    """The salary less the figures taken off it: plain sums of printed cent lines.

    The salary is written to the cent (a salary is refused below a cent, so nothing is rounded).
    """

    salary: Decimal
    income_tax: Decimal
    total_deductions: Decimal
    take_home: Decimal

    @classmethod
    def of(cls, salary: Decimal, figures: Iterable[tuple[str, Decimal]]) -> Totals:
        """Take-home is the salary less the sum of the figures; only the salary is set to cents."""
        kept = tuple(figures)
        total = sum((amount for _, amount in kept), Decimal(0))
        income_tax = sum(
            (amount for name, amount in kept if name == TakeHomeFigures.INCOME_TAX), Decimal(0)
        )
        return cls(
            salary=salary.quantize(CENTS),
            income_tax=income_tax,
            total_deductions=total,
            take_home=salary - total,
        )
