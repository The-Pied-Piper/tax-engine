"""ClaimAtMost: a claim that may not exceed a maximum, where a negative maximum allows only 0.

For a form line that reads "enter all or part of the amount you want to claim" under a maximum
the form carries with its sign (Form T2048 line 27, the lesser of line 7 and line 26, where line
26 prints no floor): the manifest decides which artifact is the claim and which is the maximum.
It is `core/at_most` for a maximum that may be negative. A claim at or below the maximum is
produced as is, and so is a claim of 0 against a negative maximum, as the filer of the paper form
claims 0. A claim above the maximum, and above 0, is not lowered to the maximum but is an input
error, `InputAboveBoundError`. It records one `ClaimAtMostLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.trace import ClaimAtMostLine


@capability(identifier="claim_at_most")
class ClaimAtMost(Capability):
    """Produces `output`: the consumed `claim`, unchanged, when it is at most the `maximum` or 0."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"claim": Decimal, "maximum": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, claim: Money, maximum: Money, output: Money) -> None:
        """Wire the capability: the kind claimed, the kind it may not exceed, the kind produced."""
        super().__init__(claim=claim, maximum=maximum, output=output)
        self._claim = claim
        self._maximum = maximum
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        claim = self._input(inputs, self._claim).value
        maximum = self._input(inputs, self._maximum).value
        if claim > maximum and claim != 0:
            raise InputAboveBoundError(
                f"{self._claim.identifier} {claim} is above {self._maximum.identifier} {maximum}"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, claim),),
            trace=(
                ClaimAtMostLine(
                    output=self._output,
                    claim_kind=self._claim,
                    claim_value=claim,
                    maximum_kind=self._maximum,
                    maximum_value=maximum,
                ),
            ),
        )
