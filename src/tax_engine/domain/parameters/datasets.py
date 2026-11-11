"""Parameter datasets: one family's values of one kind for one tax year (design.md §4).

Every covered tax year needs its own dataset; an absent year is never carried
forward. `sources` records where the values came from.
"""

from __future__ import annotations

from dataclasses import dataclass

from tax_engine.domain.errors import InvalidParameterDataError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import RoundingRule


@dataclass(frozen=True)
class ParameterDataset[T]:
    """One family's parameter values of one kind for one tax year, with rounding and sources.

    `title` is the wording the form prints for the figure, if any ("maximum per slip"). Raises if
    the values are not of its kind's type.
    """

    family: str
    tax_year: int
    kind: ParameterKind[T]
    values: T
    rounding: RoundingRule
    sources: tuple[str, ...]
    title: str | None = None

    def __post_init__(self) -> None:
        if self.title is not None and not self.title.strip():
            raise InvalidParameterDataError("a dataset title, when given, must not be blank")
        if not isinstance(self.values, self.kind.value_type):
            raise TypeError(
                f"{self.kind.name} dataset values must be a {self.kind.value_type.__name__}, "
                f"got {type(self.values).__name__}"
            )
