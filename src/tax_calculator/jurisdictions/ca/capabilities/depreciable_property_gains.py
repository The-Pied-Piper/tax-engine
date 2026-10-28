"""DepreciablePropertyGains: the gain or loss of real estate rows, a depreciable property loss
counting 0.

For Schedule 3 (form 5000-S3) Part 3, line 5 "Real estate, depreciable property and other
properties": "Total gain or loss (add all the amounts under column 5)". Each row's column 5 is its
proceeds less its adjusted cost base and its outlays. The form prints no line for a loss on
depreciable property, but Guide T4037 p.19 says "A loss from the sale of depreciable property is
not considered to be a capital loss. However, you may be able to claim a terminal loss." and Guide
T4036 p.44 says "You cannot have a capital loss when you sell depreciable property". The filer
says so with the row's 0 or 1 `ca/disposition_depreciable_property` answer: a row answered 1
counts its gain not below 0, and a row answered 0 counts its signed gain, as `DispositionGains`
does. An answer above 1 is an `InputAboveBoundError` naming the item. The terminal loss itself is
computed on the CCA table, not here.

A row may also apply some of the filer's unapplied restricted farm loss against a gain on farmland.
Guide T4037 p.34 says "Reduce your capital gain by adding these amounts to the adjusted cost base
(ACB) of your farmland.", "The amount of RFLs that you can apply cannot be more than the property
taxes and interest on money you borrowed to buy the farmland that were included in the calculation
of the RFLs for each year." and p.36 "You cannot use it to create or increase a capital loss."
The row holds the part of the loss that is property taxes and interest (`ca/disposition_farm_loss_
taxes_and_interest`) and the Guide's two printed lines, C property taxes
(`ca/disposition_farm_loss_property_taxes`) and D interest (`ca/disposition_farm_loss_interest`).
Their total, the Guide's line E less the original cost base, is added to column 3 before column 5
is worked out. A total above that part, or above the row's gain before it is added (0 when the row
is a loss), is an `InputAboveBoundError` naming the item, never capped. See `DispositionRows`
for the slots and the trace.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.capability import capability
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.record_list import Record
from tax_calculator.domain.trace import TraceLine
from tax_calculator.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_calculator.jurisdictions.ca.catalog import (
    DISPOSITION_ADJUSTED_COST_BASE,
    DISPOSITION_DEPRECIABLE_PROPERTY,
    DISPOSITION_FARM_LOSS_INTEREST,
    DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
    DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
    DISPOSITION_OUTLAYS,
    DISPOSITION_PROCEEDS,
)
from tax_calculator.jurisdictions.ca.trace import DepreciablePropertyGainLine


@capability(identifier="depreciable_property_gains")
class DepreciablePropertyGains(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' gains or losses, a loss on
    depreciable property counting 0."""

    def _record_row(self, position: int, record: Record) -> tuple[TraceLine, Decimal]:
        proceeds = Decimal(record[DISPOSITION_PROCEEDS])
        cost_base = Decimal(record[DISPOSITION_ADJUSTED_COST_BASE])
        outlays = Decimal(record[DISPOSITION_OUTLAYS])
        farm_loss_part = Decimal(record[DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST])
        farm_loss_taxes = Decimal(record[DISPOSITION_FARM_LOSS_PROPERTY_TAXES])
        farm_loss_interest = Decimal(record[DISPOSITION_FARM_LOSS_INTEREST])
        farm_loss_applied = farm_loss_taxes + farm_loss_interest
        gain_before_farm_loss = proceeds - cost_base - outlays
        if farm_loss_applied > farm_loss_part:
            raise InputAboveBoundError(
                f"item {position}: {DISPOSITION_FARM_LOSS_PROPERTY_TAXES.identifier} plus "
                f"{DISPOSITION_FARM_LOSS_INTEREST.identifier} {farm_loss_applied} "
                f"is above the property taxes and interest part of the restricted farm loss "
                f"{farm_loss_part}"
            )
        if farm_loss_applied > max(Decimal(0), gain_before_farm_loss):
            raise InputAboveBoundError(
                f"item {position}: {DISPOSITION_FARM_LOSS_PROPERTY_TAXES.identifier} plus "
                f"{DISPOSITION_FARM_LOSS_INTEREST.identifier} {farm_loss_applied} "
                f"is above the gain {max(Decimal(0), gain_before_farm_loss)}: a restricted farm "
                "loss cannot create or increase a capital loss"
            )
        gain = gain_before_farm_loss - farm_loss_applied
        flag = record[DISPOSITION_DEPRECIABLE_PROPERTY]
        if flag > 1:
            raise InputAboveBoundError(
                f"item {position}: {DISPOSITION_DEPRECIABLE_PROPERTY.identifier} {flag} is above "
                "a yes or no answer of 1"
            )
        counted = max(Decimal(0), gain) if flag else gain
        line = DepreciablePropertyGainLine(
            self._output,
            position,
            proceeds,
            cost_base,
            outlays,
            farm_loss_taxes,
            farm_loss_interest,
            farm_loss_applied,
            flag,
            gain,
            counted,
        )
        return line, counted
