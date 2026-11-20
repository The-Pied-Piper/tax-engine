"""DivideByCount: a money artifact shared among a count of people, rounding the exact quotient once.

Revenu Quebec's solidarity tax credit (fiche 110201, Table C.9) shares the basic housing amount for
multiple owners or tenants (906) among the number of owners or tenants. No other capability divides
an amount by a count: `core/divide` takes a money divisor and `ca/amount_by_count` reads a table.

The output is `rounding.apply(amount / count)`, the quotient formed once as an exact fraction; with
no rounding an inexact quotient raises `decimal.Inexact`. A count of 0 is not an error: the output
is 0, and the trace line still records the rounding rule. A blank amount or count is refused unless
the manifest's `blank:` rule gives it a value.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca_qc.trace import DivideByCountLine


@capability(identifier="divide_by_count")
class DivideByCount(Capability):
    """Produces `output`: the consumed `amount` divided by the consumed `count`, rounded once
    (0 if the count is 0)."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[RoundingOnly]]] = {"rounding": ROUNDING_ONLY}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amount": Decimal, "count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"amount", "count"})

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        amount: Money,
        count: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the amount shared, the count it is shared
        among, the kind produced."""
        super().__init__(amount=amount, count=count, output=output)
        self._rounding = rounding
        self._amount = amount
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        amount = self._input(inputs, self._amount).value
        count = self._input(inputs, self._count).value
        rounding = self._rounding.rounding
        result = Decimal(0) if count == 0 else rounding.apply(ExactFraction(amount) / count)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                DivideByCountLine(
                    output=self._output,
                    amount_kind=self._amount,
                    amount_value=amount,
                    count_kind=self._count,
                    count=count,
                    rounding=rounding,
                    result=result,
                ),
            ),
        )
