"""Tax on taxable income: the one of BC428 line 8 and line 15 that has a figure.

BC428 line 61 "British Columbia tax on taxable income from line 8 or 15": a taxable income is in
one table only, so the other line is blank. Lines 8, 15 and 61 are on one form, so the two lines
are plain amounts; a blank in either reaches `compute`. Both blank, or both with a figure, raises a
`ValidationError`. The figure is passed on as it is: no rounding rule is applied to it.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.capability import Capability, CapabilityResult, capability
from tax_engine.domain.errors import ValidationError
from tax_engine.jurisdictions.ca_bc.trace import TaxOnTaxableIncomeLine


@capability(identifier="tax_on_taxable_income")
class TaxOnTaxableIncome(Capability):
    """Produces `output`: the amount of whichever of `line_8` and `line_15` is not blank."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"line_8": Decimal, "line_15": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"line_8", "line_15"})

    def __init__(self, line_8: Money, line_15: Money, output: Money) -> None:
        """Wire the capability: the two amounts it reads, the kind it makes."""
        super().__init__(line_8=line_8, line_15=line_15, output=output)
        self._line_8 = line_8
        self._line_15 = line_15
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        name = type(self).__name__
        artifact_8 = self._input(inputs, self._line_8)
        artifact_15 = self._input(inputs, self._line_15)
        if artifact_8.is_blank and artifact_15.is_blank:
            raise ValidationError(
                f"{name}: line 8 and line 15 are both blank; one of them must have a figure"
            )
        if not artifact_8.is_blank and not artifact_15.is_blank:
            raise ValidationError(
                f"{name}: line 8 and line 15 both have a figure; only one of them may"
            )
        if artifact_15.is_blank:
            used, left_blank, amount = self._line_8, self._line_15, artifact_8.value
        else:
            used, left_blank, amount = self._line_15, self._line_8, artifact_15.value
        return CapabilityResult(
            outputs=(Artifact(self._output, amount),),
            trace=(TaxOnTaxableIncomeLine(self._output, used, amount, left_blank),),
        )
