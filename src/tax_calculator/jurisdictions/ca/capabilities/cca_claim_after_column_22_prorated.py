"""CcaClaimAfterColumn22Prorated: the total CCA claim of the T776 CCA table, limited by column 22,
for a fiscal period shorter than a full year.

Guide T4002 2025, "You were asking?": "Since your fiscal period is less than 365 days, you have to
prorate your CCA claim. Calculate your CCA using the rules discussed in this chapter. However, base
your CCA claim on the number of days in your fiscal period compared to 365 days. In this case, your
fiscal period is 214 days. Suppose you calculate your CCA to be $3,500. The amount of CCA you can
claim is $2,052 ($3,500 × 214 ÷ 365)." `CcaClaimAfterColumn22` with the consumed int
`fiscal_period_days` (the days of the fiscal period, from 1 to the `class_rates` dataset's
`longest_fiscal_period_days`), each class's maximum prorated by it as `CcaTable` prorates it;
column 9 is not.
It subclasses `CcaClaimAfterColumn22` alone and adds the slot; the output and the trace are those of
`CcaClaimAfterColumn22`, whose lines hold the days.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import ClassVar

from tax_calculator.domain.artifact import ArtifactKind, Money
from tax_calculator.domain.capability import capability
from tax_calculator.domain.parameters.class_rates import ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_after_column_22 import CcaClaimAfterColumn22


@capability(identifier="cca_claim_after_column_22_prorated")
class CcaClaimAfterColumn22Prorated(CcaClaimAfterColumn22):
    """Produces `output`: the total, over the consumed `classes`, of each class's CCA claimed, at
    most its prorated maximum from the `class_rates` dataset for the days of
    `fiscal_period_days`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {
        "classes": RecordList,
        "non_compliant": RecordList,
        "fiscal_period_days": int,
    }
    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        class_rates: ParameterDataset[ClassRates],
        classes: ArtifactKind[RecordList],
        non_compliant: ArtifactKind[RecordList],
        fiscal_period_days: ArtifactKind[int],
        output: Money,
    ) -> None:
        """Wire the capability: its class-rate dataset, the record list it reads, the record list
        of column 22 amounts, the int kind of the days of the fiscal period, the kind
        produced."""
        super().__init__(
            class_rates, classes, non_compliant, output, fiscal_period_days=fiscal_period_days
        )
