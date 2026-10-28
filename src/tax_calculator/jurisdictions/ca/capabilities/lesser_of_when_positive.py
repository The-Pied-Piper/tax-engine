"""LesserOfWhenPositive: the least of a list of money artifacts, but only if every one is positive.

For a line that reads "enter whichever is less" when it applies only to amounts above zero: it is
`core/lesser_of` behind a gate. When every amount is above zero the least is produced, exactly
and with its scale kept (the first listed wins a tie); otherwise the output is a plain
`Decimal(0)`. `LesserOfWhenPositiveInBrackets` shares the implementation for a line that "shows in
brackets": it produces the negative of that least. It has no dataset, so it never rounds. Each
records one `LesserOfWhenPositiveLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError
from tax_calculator.domain.trace import LesserOfWhenPositiveLine


@capability(identifier="lesser_of_when_positive")
class LesserOfWhenPositive(Capability):
    """Produces `output`: the least of the consumed `amounts`, of which there is at least one,
    when every one is above zero, otherwise 0."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amounts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    _BRACKET: ClassVar[bool] = False

    def __init__(self, amounts: tuple[Money, ...], output: Money) -> None:
        """Wire the capability: the kinds it compares, in manifest order, and the kind it produces.

        Raises InvalidCapabilityError when `amounts` is empty: there is no lesser of nothing.
        """
        super().__init__(amounts=amounts, output=output)
        if not amounts:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'amounts' needs at least one kind, "
                "since there is no lesser of nothing"
            )
        self._amounts = amounts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._amounts)
        all_positive = all(value > 0 for _kind, value in parts)
        # `min` keeps the first of equal values, so the first listed wins a tie.
        _kind, lesser = min(parts, key=lambda part: part[1])
        result = Decimal(0)
        if all_positive:
            # `copy_negate` is exact; unary minus would round to the context's precision.
            result = lesser.copy_negate() if self._BRACKET else lesser
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                LesserOfWhenPositiveLine(self._output, parts, all_positive, self._BRACKET, result),
            ),
        )


@capability(identifier="lesser_of_when_positive_in_brackets")
class LesserOfWhenPositiveInBrackets(LesserOfWhenPositive):
    """Produces `output`: the negative of the least of the consumed `amounts` when every one is
    above zero, otherwise 0."""

    _BRACKET: ClassVar[bool] = True
