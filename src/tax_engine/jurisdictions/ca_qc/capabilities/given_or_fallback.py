"""GivenOrFallback: a figure the filer gives, else another figure of the return.

Schedule 10 line 13 "Enter the amount from box 56 of all of your T4 slips where Quebec is the
province of employment (if box 56 is blank, enter the amount from box 14 of the T4 slip)": no
capability takes one figure, or another when that one is blank (`ca/given_or_contribution_tier`
falls back to a tier calculation, not to a figure). A given figure is produced unchanged; a blank
`given` (rule `compute`) produces the `fallback`, which may not be blank.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.jurisdictions.ca_qc.trace import GivenOrFallbackLine


@capability(identifier="given_or_fallback")
class GivenOrFallback(Capability):
    """Produces `output`: the `given` figure unchanged, or, when `given` is blank, the
    `fallback`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"given": Decimal, "fallback": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"given"})

    def __init__(self, given: Money, fallback: Money, output: Money) -> None:
        """Wire the capability: the kind the filer may give, the kind taken when it is blank, and
        the kind it produces."""
        super().__init__(given=given, fallback=fallback, output=output)
        self._given = given
        self._fallback = fallback
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        given = self._input(inputs, self._given)
        given_was_blank = given.is_blank
        value = self._input(inputs, self._fallback).value if given_was_blank else given.value
        return CapabilityResult(
            outputs=(Artifact(self._output, value),),
            trace=(
                GivenOrFallbackLine(
                    output=self._output,
                    given=self._given,
                    fallback=self._fallback,
                    given_was_blank=given_was_blank,
                    result=value,
                ),
            ),
        )
