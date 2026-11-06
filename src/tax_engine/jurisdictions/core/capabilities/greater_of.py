"""GreaterOf: the greatest of a list of money artifacts, exactly.

For a form line that reads "whichever is more": the manifest decides which amounts are compared,
and in which order they are listed in the trace. It has no dataset, so it never rounds; when two
amounts are equal, the first listed is produced, keeping its scale.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.trace import GreaterOfLine


@capability(identifier="greater_of")
class GreaterOf(Capability):
    """Produces `output`: the greatest of the consumed `amounts`, of which there is at least one."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amounts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amounts: tuple[Money, ...], output: Money) -> None:
        """Wire the capability: the kinds it compares, in manifest order, and the kind it produces.

        Raises InvalidCapabilityError when `amounts` is empty: there is no greater of nothing.
        """
        super().__init__(amounts=amounts, output=output)
        if not amounts:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'amounts' needs at least one kind, "
                "since there is no greater of nothing"
            )
        self._amounts = amounts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._amounts)
        # `max` keeps the first of equal values, so the first listed wins a tie.
        _kind, greater = max(parts, key=lambda part: part[1])
        return CapabilityResult(
            outputs=(Artifact(self._output, greater),),
            trace=(GreaterOfLine(self._output, parts, greater),),
        )
