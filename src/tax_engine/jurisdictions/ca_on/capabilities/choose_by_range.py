"""ChooseByRange: one of three money artifacts, chosen by the range a money artifact is in.

For a line computed once for each of three alternative columns, where the amount a column is
headed by decides which column applies (column 1 if at most one limit, column 2 if more than that
but at most the next limit, column 3 if more): the output is `first` when `amount` is at most
`first_limit`, `second` when it is more than `first_limit` but at most `second_limit`, and `third`
when it is more than `second_limit`; each limit belongs to the range below it. The chosen value is
unchanged with its scale kept. It has no dataset, so it never rounds, and no floor; the amount
only chooses, it never scales. Only the limits it needs and the chosen candidate are read.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.trace import ChosenByRangeLine


@capability(identifier="choose_by_range")
class ChooseByRange(Capability):
    """Produces `output`: the consumed `first` if the consumed `amount` is at most `first_limit`,
    else `second` if it is at most `second_limit`, else `third`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "amount": Decimal,
        "first_limit": Decimal,
        "second_limit": Decimal,
        "first": Decimal,
        "second": Decimal,
        "third": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        amount: Money,
        first_limit: Money,
        second_limit: Money,
        first: Money,
        second: Money,
        third: Money,
        output: Money,
    ) -> None:
        """Wire the capability: the amount it tests, the two limits, the three candidates, the
        kind produced."""
        super().__init__(
            amount=amount,
            first_limit=first_limit,
            second_limit=second_limit,
            first=first,
            second=second,
            third=third,
            output=output,
        )
        self._amount = amount
        self._first_limit = first_limit
        self._second_limit = second_limit
        self._first = first
        self._second = second
        self._third = third
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        tested = self._input(inputs, self._amount).value
        if tested <= self._input(inputs, self._first_limit).value:
            chosen_kind = self._first
        elif tested <= self._input(inputs, self._second_limit).value:
            chosen_kind = self._second
        else:
            chosen_kind = self._third
        chosen = self._input(inputs, chosen_kind).value
        return CapabilityResult(
            outputs=(Artifact(self._output, chosen),),
            trace=(
                ChosenByRangeLine(
                    output=self._output,
                    tested_kind=self._amount,
                    tested_value=tested,
                    chosen_kind=chosen_kind,
                    chosen_value=chosen,
                ),
            ),
        )
