"""Trace lines for rentals: the non-compliant amounts of short-term rentals, Charts A and B, and the
equipment and building additions of Form T776 Areas B and C."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactKind, Money
from tax_calculator.domain.parameters.rounding import RoundingRule
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace.base import TraceLine

__all__ = [
    "RentalAdditionLine",
    "ShortTermRentalNonCompliantCcaByClassLine",
    "ShortTermRentalNonCompliantCcaLine",
    "ShortTermRentalNonCompliantLine",
]


@dataclass(frozen=True)
class RentalAdditionLine(TraceLine):
    """The rental portion `result` of one addition of Form T776 Area B or Area C, by `position`
    (from 1), for `output`: the `total_cost` (column 3) less the `personal_portion` (column 4);
    `class_number` is its column 1.
    """

    output: Money
    position: int
    class_number: Decimal
    total_cost: Decimal
    personal_portion: Decimal
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The addition's rental portion."""
        return self.result


@dataclass(frozen=True)
class ShortTermRentalNonCompliantLine(TraceLine):
    """The non-compliant amount `result` of one short-term rental row, by `position` (from 1),
    for `output`.

    It is the row's `related_expenses` times its `non_compliant_days` divided by its `days`, as an
    exact fraction rounded once with `rounding`.
    """

    output: Money
    position: int
    related_expenses: Decimal
    non_compliant_days: int
    days: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The row's non-compliant amount."""
        return self.result


@dataclass(frozen=True)
class ShortTermRentalNonCompliantCcaLine(TraceLine):
    """The non-compliant amount `result` of one Chart B row, by `position` (from 1), for `output`.

    It is the row's `related_cca` (column 4) times its `non_compliant_days` (column 5) divided by
    its `days` (column 6), as an exact fraction rounded once with `rounding`; `class_number` is
    its column 1.
    """

    output: Money
    position: int
    class_number: Decimal
    related_cca: Decimal
    non_compliant_days: int
    days: int
    rounding: RoundingRule
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The row's non-compliant amount."""
        return self.result


@dataclass(frozen=True)
class ShortTermRentalNonCompliantCcaByClassLine(TraceLine):
    """The column 22 total `result` of one class of Chart B, by `position` (from 1), for `output`.

    It is the total of the `amounts`, the rounded column 7 amounts of the rows of `class_number`.
    """

    output: ArtifactKind[RecordList]
    position: int
    class_number: Decimal
    amounts: tuple[Decimal, ...]
    result: Decimal

    @property
    def amount(self) -> Decimal:
        """The class's column 22 total."""
        return self.result
