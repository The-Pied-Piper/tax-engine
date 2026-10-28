"""MoreThanPerUnit: a total that must be more than an amount for each unit, passed on unchanged.

Schedule 11 line 1 and T1 line 32000 "Eligible tuition fees paid to Canadian educational
institutions for 2025 (fees for each institution must be more than $100)"
(docs/cra-forms-2025/5000-s11-25e.txt): the form takes one total, so the caller also gives the
count of units (institutions). The minimum is `rounding.apply(amount x count)`, the product
`core/per_unit_amount` takes, rounded once with the `amount` dataset's rule.

With a count of 0 the total must be 0: any other total is an input error, `InputAboveBoundError`.
With a count above 0 the total must be strictly more than the minimum, as the form prints "more
than": a total equal to it is refused too, as `InputBelowBoundError`. The output is the total,
unchanged and not rounded, so a total with a fraction of a cent is compared as entered. It
records one `MoreThanPerUnitLine` when it produces the output, and none when it raises.

Known limit: the check only refuses totals too small for the count. It sees one total, not each
unit's fees, so two institutions and $201 pass although one fee may have been $60.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult, capability
from tax_calculator.domain.errors import InputAboveBoundError, InputBelowBoundError
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import MoreThanPerUnitLine


@capability(identifier="more_than_per_unit")
class MoreThanPerUnit(Capability):
    """Produces `output`: the consumed `total`, unchanged, when more than `amount` x `count`."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"amount": AMOUNT}
    CONSUMES: ClassVar[Mapping[str, type]] = {"total": Decimal, "count": int}
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        amount: ParameterDataset[Amount],
        total: Money,
        count: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its per-unit dataset, the total checked, the count of units, the
        total produced."""
        super().__init__(total=total, count=count, output=output)
        self._amount = amount
        self._total = total
        self._count = count
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        total = self._input(inputs, self._total).value
        count = self._input(inputs, self._count).value
        per_unit, rounding = self._amount.values, self._amount.rounding
        product = per_unit.value * count
        if not product:
            product = product.copy_abs()  # a zero product is a plain 0, never a signed one
        minimum_total = rounding.apply(product)
        if count == 0:
            if total:
                raise InputAboveBoundError(
                    f"{self._total.identifier} {total} is above 0 with "
                    f"{self._count.identifier} {count}"
                )
        elif total <= minimum_total:
            raise InputBelowBoundError(
                f"{self._total.identifier} {total} is not more than {minimum_total} "
                f"({per_unit.value} for each of {count} {self._count.identifier})"
            )
        return CapabilityResult(
            outputs=(Artifact(self._output, total),),
            trace=(
                MoreThanPerUnitLine(
                    output=self._output,
                    total_kind=self._total,
                    total=total,
                    count_kind=self._count,
                    count=count,
                    per_unit=per_unit,
                    rounding=rounding,
                    minimum_total=minimum_total,
                ),
            ),
        )
