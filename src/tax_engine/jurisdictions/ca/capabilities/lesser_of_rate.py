"""Lesser of rate: the rate of a further dollar of the least of several amounts.

Each amount comes with the rate a further dollar adds to it. The output is the rate of the least
amount; of equal least amounts, the smallest of their rates, since the lesser of lines that meet
follows the one that rises slowest.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.jurisdictions.ca.trace.marginal_rate import LesserOfRateLine


@capability(identifier="lesser_of_rate")
class LesserOfRate(Capability):
    """Produces `output`: the rate paired with the least of the consumed `amounts`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"amounts": list[Decimal], "rates": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, amounts: tuple[Money, ...], rates: tuple[Money, ...], output: Money) -> None:
        """Wire the capability: the kinds it compares and the kind of each one's rate, in manifest
        order, and the kind it produces.

        Raises InvalidCapabilityError when `amounts` is empty or the two lists differ in length.
        """
        super().__init__(amounts=amounts, rates=rates, output=output)
        if not amounts or len(amounts) != len(rates):
            raise InvalidCapabilityError(
                f"{type(self).__name__}: slots 'amounts' and 'rates' need the same, non-zero "
                "number of kinds, since each amount is paired with its rate"
            )
        self._amounts = amounts
        self._rates = rates
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple(
            (amount, self._input(inputs, amount).value, self._input(inputs, rate).value)
            for amount, rate in zip(self._amounts, self._rates, strict=True)
        )
        least = min(value for _kind, value, _rate in parts)
        rate = min(rate for _kind, value, rate in parts if value == least)
        return CapabilityResult(
            outputs=(Artifact(self._output, rate),),
            trace=(LesserOfRateLine(self._output, parts, rate),),
        )
