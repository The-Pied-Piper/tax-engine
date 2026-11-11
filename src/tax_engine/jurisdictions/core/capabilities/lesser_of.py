"""LesserOf: the least of a list of money artifacts, exactly.

Of equal amounts the first listed is produced, keeping its scale. A `pass_on` blank blanks the
output.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.trace import LesserOfLine


@capability(identifier="lesser_of")
class LesserOf(Capability):
    """Produces `output`: the least of the consumed `amounts`, of which there is at least one."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amounts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"amounts"})

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
        # `min` keeps the first of equal values, so the first listed wins a tie.
        _kind, lesser = min(parts, key=lambda part: part[1])
        return CapabilityResult(
            outputs=(Artifact(self._output, lesser),),
            trace=(LesserOfLine(self._output, parts, lesser),),
        )
