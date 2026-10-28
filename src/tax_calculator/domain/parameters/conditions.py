"""Conditions: a form's list of conditions, copied condition by condition in the form's order.

A form line that is switched on or off by a list of conditions (enter 0 if any of them applies, or
complete a chart if any applies) is copied as printed. A `ConditionList` holds
`count_when_any_applies` (0 or 1) and one or more `Condition`s; when no condition applies the count
is the other one of 0 and 1. A `Condition` holds its printed `text`, word for word, and `parts`, all
of which must hold; a `ConditionPart` holds `tests`, any one of which holds ("and" joins parts, "or"
joins tests). A `ConditionTest` compares one figure with a printed figure (`than`) or with another
amount (`against`). The figures are named by position (from 1) in the capability's list of counts or
of amounts, so a figure read by several tests is listed once. The code holds no jurisdiction's
conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from tax_calculator.domain.errors import InvalidConditionsError
from tax_calculator.domain.parameters.kind import ParameterKind

_READS = ("count", "amount")
_RELATIONS = ("equal_to", "not_equal_to", "more_than")


@dataclass(frozen=True)
class ConditionTest:
    """One comparison: the figure at `position` (from 1) among the `reads` kind ("count" or
    "amount") stands in `relation` ("equal_to", "not_equal_to" or "more_than") to exactly one of
    `than`, a printed figure, and `against`, the position (from 1) of another amount.

    `against` is only for a test that reads an amount, and names an amount other than its own. The
    figures are exact.
    """

    reads: str
    position: int
    relation: str
    than: Decimal | None
    against: int | None

    def __post_init__(self) -> None:
        """Check: a known `reads` and `relation`, positions from 1, a finite `than` and exactly
        one of `than` and `against`, `against` only for another amount."""
        if not isinstance(self.reads, str):
            raise TypeError(f"reads must be a str, got {type(self.reads).__name__}")
        if self.reads not in _READS:
            raise InvalidConditionsError(f"reads must be 'count' or 'amount', got {self.reads!r}")
        self._check_position("position", self.position)
        if not isinstance(self.relation, str):
            raise TypeError(f"relation must be a str, got {type(self.relation).__name__}")
        if self.relation not in _RELATIONS:
            raise InvalidConditionsError(
                f"relation must be 'equal_to', 'not_equal_to' or 'more_than', got {self.relation!r}"
            )
        if self.than is not None:
            if not isinstance(self.than, Decimal):
                raise TypeError(f"than must be a Decimal, got {type(self.than).__name__}")
            if not self.than.is_finite():
                raise InvalidConditionsError(f"than must be finite, got {self.than}")
        if self.against is not None:
            self._check_position("against", self.against)
        if (self.than is None) == (self.against is None):
            raise InvalidConditionsError("a test needs exactly one of than and against")
        if self.against is not None and self.reads != "amount":
            raise InvalidConditionsError(f"against needs reads 'amount', got {self.reads!r}")
        if self.against == self.position:
            raise InvalidConditionsError(
                f"against must name another amount than position {self.position}"
            )

    @staticmethod
    def _check_position(name: str, value: object) -> None:
        # bool is an int subclass but not a position.
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int, got {type(value).__name__}")
        if value < 1:
            raise InvalidConditionsError(f"{name} must be 1 or more, got {value}")

    def holds(self, figure: Decimal, counterpart: Decimal) -> bool:
        """Whether `figure` stands in this test's relation to `counterpart`, the `than` figure or
        the amount at `against`. A tie is not "more than"."""
        if self.relation == "equal_to":
            return figure == counterpart
        if self.relation == "not_equal_to":
            return figure != counterpart
        return figure > counterpart


@dataclass(frozen=True)
class ConditionPart:
    """At least one test, any one of which holds."""

    tests: tuple[ConditionTest, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.tests, tuple):
            raise TypeError(f"tests must be a tuple, got {type(self.tests).__name__}")
        for index, test in enumerate(self.tests):
            if not isinstance(test, ConditionTest):
                raise TypeError(
                    f"tests[{index}] must be a ConditionTest, got {type(test).__name__}"
                )
        if not self.tests:
            raise InvalidConditionsError("a part needs at least one test")


@dataclass(frozen=True)
class Condition:
    """A printed condition: its `text`, word for word, and at least one part, all of which hold."""

    text: str
    parts: tuple[ConditionPart, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError(f"text must be a str, got {type(self.text).__name__}")
        if not self.text:
            raise InvalidConditionsError("text must not be empty")
        if not isinstance(self.parts, tuple):
            raise TypeError(f"parts must be a tuple, got {type(self.parts).__name__}")
        for index, part in enumerate(self.parts):
            if not isinstance(part, ConditionPart):
                raise TypeError(
                    f"parts[{index}] must be a ConditionPart, got {type(part).__name__}"
                )
        if not self.parts:
            raise InvalidConditionsError("a condition needs at least one part")

    @property
    def tests(self) -> tuple[ConditionTest, ...]:
        """Every test of every part, in the order printed."""
        return tuple(test for part in self.parts for test in part.tests)


@dataclass(frozen=True)
class ConditionList:
    """`count_when_any_applies` (0 or 1) and at least one condition, in the form's order."""

    count_when_any_applies: int
    conditions: tuple[Condition, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.count_when_any_applies, int) or isinstance(
            self.count_when_any_applies, bool
        ):
            raise TypeError(
                "count_when_any_applies must be an int, "
                f"got {type(self.count_when_any_applies).__name__}"
            )
        if self.count_when_any_applies not in (0, 1):
            raise InvalidConditionsError(
                f"count_when_any_applies must be 0 or 1, got {self.count_when_any_applies}"
            )
        if not isinstance(self.conditions, tuple):
            raise TypeError(f"conditions must be a tuple, got {type(self.conditions).__name__}")
        for index, condition in enumerate(self.conditions):
            if not isinstance(condition, Condition):
                raise TypeError(
                    f"conditions[{index}] must be a Condition, got {type(condition).__name__}"
                )
        if not self.conditions:
            raise InvalidConditionsError("a list needs at least one condition")

    @property
    def count_when_none_applies(self) -> int:
        """The other one of 0 and 1."""
        return 1 - self.count_when_any_applies

    @property
    def count_positions_read(self) -> frozenset[int]:
        """The positions in the list of counts that some test reads."""
        return frozenset(
            test.position
            for condition in self.conditions
            for test in condition.tests
            if test.reads == "count"
        )

    @property
    def amount_positions_read(self) -> frozenset[int]:
        """The positions in the list of amounts that some test reads or compares against."""
        read: set[int] = set()
        for condition in self.conditions:
            for test in condition.tests:
                if test.reads == "amount":
                    read.add(test.position)
                if test.against is not None:
                    read.add(test.against)
        return frozenset(read)

    @property
    def highest_count_position(self) -> int:
        """The highest position read in the list of counts, 0 when none is read."""
        return max(self.count_positions_read, default=0)

    @property
    def highest_amount_position(self) -> int:
        """The highest position read in the list of amounts, 0 when none is read."""
        return max(self.amount_positions_read, default=0)


CONDITIONS: ParameterKind[ConditionList] = ParameterKind("conditions", ConditionList)
