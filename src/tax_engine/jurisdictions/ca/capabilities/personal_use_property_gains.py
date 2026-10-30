"""PersonalUsePropertyGains: the gain of each personal-use property, the $1,000 minimum applied.

For Schedule 3 (form 5000-S3) Part 3, personal-use property: "Line 9 and line 15800: Total gain
only (add all the amounts under column 5)". Guide T4037 2025, "Personal-use property" Example, p.24
(https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4037/t4037-25e.pdf) prints "Proceeds of
disposition (whichever is more: selling price or $1,000)" and "Minus: ACB (whichever is more: cost
or $1,000) plus outlays and expenses". So each row's proceeds and adjusted cost base are raised to
the `minimum` dataset's amount when they are lower; its outlays are not. The row's column 5 gain is
the proceeds used less the cost base used less the outlays, and a row with a loss counts 0, so it
does not decrease the gains of the other rows (Guide T4037 p.22: "you cannot use the loss to
decrease capital gains on other personal-use property"). See `DispositionRows` for the slots and
the trace.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import ClassVar

from tax_engine.domain.artifact import ArtifactKind, Money
from tax_engine.domain.capability import capability
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import TraceLine
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.trace import PersonalUsePropertyGainLine


@capability(identifier="personal_use_property_gains")
class PersonalUsePropertyGains(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' gains, each row's proceeds and
    adjusted cost base raised to the `minimum` dataset's amount, a loss counting 0."""

    PARAMETERS: ClassVar[Mapping[str, ParameterKind[Amount]]] = {"minimum": AMOUNT}

    def __init__(
        self,
        minimum: ParameterDataset[Amount],
        dispositions: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its minimum dataset, the record list it reads, the kind produced."""
        super().__init__(dispositions, output)
        self._minimum = minimum

    def _row(
        self, position: int, proceeds: Decimal, cost_base: Decimal, outlays: Decimal
    ) -> tuple[TraceLine, Decimal]:
        minimum = self._minimum.values.value
        proceeds_used = max(proceeds, minimum)
        cost_base_used = max(cost_base, minimum)
        gain = proceeds_used - cost_base_used - outlays
        counted = max(Decimal(0), gain)
        line = PersonalUsePropertyGainLine(
            self._output,
            position,
            proceeds,
            cost_base,
            outlays,
            minimum,
            proceeds_used,
            cost_base_used,
            gain,
            counted,
        )
        return line, counted
