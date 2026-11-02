"""Apply fraction: multiplies a money artifact by a fraction from a `fraction` dataset.

For form lines such as "multiplied by two-thirds", whose fraction is not a finite decimal: the
output is `rounding.apply(base × numerator / denominator)`, the division done as an exact fraction
so nothing is rounded before the rule. It is rounded only with the `fraction` dataset's rule, which
defaults to no rounding; under no rounding a quotient with no finite decimal expansion raises
`decimal.Inexact`.

A blank `base` is allowed. What it does is the manifest step's `blank:` rule: `pass_on` gives a
blank `output` (a fraction of a line left blank is blank, and there is nothing to round); with no
rule it is refused. `compute` never sees a blank.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import FractionAppliedLine


@capability(identifier="apply_fraction")
class ApplyFraction(Capability):
    """Produces `output`: the consumed `base` × the `fraction` dataset's fraction, rounded."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Fraction]]] = {"fraction": FRACTION}
    CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"base"})
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(self, fraction: ParameterDataset[Fraction], base: Money, output: Money) -> None:
        """Wire the capability: its fraction dataset, the kind it multiplies, the kind it makes."""
        super().__init__(base=base, output=output)
        self._fraction = fraction
        self._base = base
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        base = self._input(inputs, self._base).value
        fraction, rounding = self._fraction.values, self._fraction.rounding
        result = rounding.apply(ExactFraction(base) * fraction.numerator / fraction.denominator)
        return CapabilityResult(
            outputs=(Artifact(self._output, result),),
            trace=(
                FractionAppliedLine(self._output, self._base, base, fraction, rounding, result),
            ),
        )
