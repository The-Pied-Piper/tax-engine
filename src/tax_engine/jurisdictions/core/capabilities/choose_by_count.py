"""ChooseByCount: one of two money artifacts, chosen by a count artifact.

The output is `when_none` for a count of 0, else `when_any`, unchanged. A `compute` candidate is
read only if chosen.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.trace import ChosenByCountLine


@capability(identifier="choose_by_count")
class ChooseByCount(Capability):
    """Produces `output`: the consumed `when_none` if the consumed `count` is 0, else `when_any`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "count": int,
        "when_none": Decimal,
        "when_any": Decimal,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"count", "when_none", "when_any"})

    def __init__(
        self, count: ArtifactKind[int], when_none: Money, when_any: Money, output: Money
    ) -> None:
        """Wire the capability: the count it reads, the two candidates, the kind produced."""
        super().__init__(count=count, when_none=when_none, when_any=when_any, output=output)
        self._count = count
        self._when_none = when_none
        self._when_any = when_any
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        count_artifact = self._input(inputs, self._count)
        if count_artifact.is_blank:
            raise BlankNotAllowedError(
                f"{type(self).__name__}: {self._count.label!r} was left blank, so it cannot choose "
                f"{self._output.label!r}"
            )
        count = count_artifact.value
        chosen_kind = self._when_none if count == 0 else self._when_any
        chosen_artifact = self._input(inputs, chosen_kind)
        if chosen_artifact.is_blank:
            raise BlankNotAllowedError(
                f"{type(self).__name__}: {chosen_kind.label!r} was left blank and was the one "
                f"chosen for {self._output.label!r}"
            )
        chosen = chosen_artifact.value
        return CapabilityResult(
            outputs=(Artifact(self._output, chosen),),
            trace=(
                ChosenByCountLine(
                    output=self._output,
                    count_kind=self._count,
                    count=count,
                    chosen_kind=chosen_kind,
                    chosen_value=chosen,
                ),
            ),
        )
