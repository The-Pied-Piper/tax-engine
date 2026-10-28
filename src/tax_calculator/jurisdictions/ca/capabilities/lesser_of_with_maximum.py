"""LesserOfWithMaximum: the least of a list of money artifacts and an `amount` dataset's figure.

For a line such as T1436 line 9, "Enter whichever is less: amount from line 3, line 8, or $2,000."
It is the "whichever is less" of `lesser_of` with a dataset figure among the candidates, as
`capped_amount` has for one base. At or below the maximum the least amount is produced as it is
(keeping its scale, the first listed winning a tie); above it, the maximum's value. The result is
rounded only with the dataset's rule, which defaults to no rounding. It records one
`LesserOfWithMaximumLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InvalidCapabilityError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import LesserOfWithMaximumLine


@capability(identifier="lesser_of_with_maximum")
class LesserOfWithMaximum(Capability):
    """Produces `output`: the least of the consumed `amounts` and the `maximum` dataset's amount."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"maximum": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"amounts": list[Decimal]}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self, maximum: ParameterDataset[Amount], amounts: tuple[Money, ...], output: Money
    ) -> None:
        """Wire the capability: its maximum dataset, the kinds it compares, in manifest order, and
        the kind it produces.

        Raises InvalidCapabilityError when `amounts` is empty: the maximum alone is no comparison.
        """
        super().__init__(amounts=amounts, output=output)
        if not amounts:
            raise InvalidCapabilityError(
                f"{type(self).__name__}: CONSUMES slot 'amounts' needs at least one kind, "
                "since the maximum alone is not a comparison"
            )
        self._maximum = maximum
        self._amounts = amounts
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        parts = tuple((kind, self._input(inputs, kind).value) for kind in self._amounts)
        maximum, rounding = self._maximum.values, self._maximum.rounding
        # `min` keeps the first of equal values, so the first listed wins a tie; at or below the
        # maximum the amount itself is the lesser, so its scale is kept.
        _kind, least = min(parts, key=lambda part: part[1])
        lesser = maximum.value if least > maximum.value else least
        result = rounding.apply(lesser)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(LesserOfWithMaximumLine(self._output, parts, maximum, rounding, result),),
        )
