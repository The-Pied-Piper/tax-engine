"""ClosingUccProrated: the UCC at the end of the year of each class, for a fiscal period shorter
than a full year.

Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days, you have to
prorate your CCA claim. Calculate your CCA using the rules discussed in this chapter. However, base
your CCA claim on the number of days in your fiscal period compared to 365 days. In this case, your
fiscal period is 214 days. Suppose you calculate your CCA to be $3,500. The amount of CCA you can
claim is $2,052 ($3,500 × 214 ÷ 365)." `ClosingUcc` with the consumed int `fiscal_period_days` (the
days of the fiscal period, from 1 to the `class_rates` dataset's `longest_fiscal_period_days`),
each class's maximum prorated by it as `CcaTable` prorates it; column 9 is not. It
subclasses `ClosingUcc` alone and adds the slot; the output and the trace are those of
`ClosingUcc`, whose lines hold the days.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.capability import capability
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc


@capability(identifier="closing_ucc_prorated")
class ClosingUccProrated(ClosingUcc):
    """Produces `output`: for each of the consumed `classes`, its class number and its UCC at the
    end of the year, with its maximum prorated from the `class_rates` dataset for the days
    of `fiscal_period_days`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "classes": RecordList,
        "fiscal_period_days": int,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": RecordList}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        fiscal_period_days: ArtifactKind[int],
        output: ArtifactKind[RecordList],
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the int kind of
        the days of the fiscal period, the record list kind produced, of the class
        number and the UCC at the end of the year."""
        super().__init__(class_rates, classes, output, fiscal_period_days=fiscal_period_days)
