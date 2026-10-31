"""ChooseByCount: one of two money artifacts, chosen by a count artifact.

For a line computed once for each of two columns, where a count of persons decides which column
applies (one amount when there are none, another when there are any): the output is `when_none`
when the count is 0 and `when_any` for any other count, the chosen value unchanged with its scale
kept. It has no dataset, so it never rounds, and no floor; the count only chooses, it never
scales. `compute` reads only the chosen candidate, but a blank in either candidate meets its rule
first: a blank unchosen candidate is refused unless its slot has a rule, and with `pass_on` it
blanks the output.

Any of its three inputs may be left blank: the count (the box not ticked, the part left blank), a
candidate (a skipped line). The class only allows it (`BLANK_ALLOWED`); what a blank does at each
step, a fallback such as "0" or passing the blank on, is the manifest's `blank:` line, so one class
serves every use. A blank in an input without such a line is refused.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
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
        count = self._input(inputs, self._count).value
        chosen_kind = self._when_none if count == 0 else self._when_any
        chosen = self._input(inputs, chosen_kind).value
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
