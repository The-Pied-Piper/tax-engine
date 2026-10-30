"""QffpGains: the gain or loss of qualified farm or fishing property rows, a restricted farm loss
added to the adjusted cost base.

For Schedule 3 (form 5000-S3) Part 3, line 2 "Qualified farm or fishing property (QFFP)": "Total
gain or loss (add all the amounts under column 5)". Each row's column 5 is its proceeds less its
adjusted cost base, less the restricted farm loss applied, and less its outlays, signed, and the
total adds the rows, as `DispositionGains` does. It also serves line 3 "QFFP: Mortgage foreclosures
and conditional sales repossessions" and line 8 "Other mortgage foreclosures and conditional sales
repossessions": Guide T4037 p.22 says a mortgagor whose property is repossessed "is considered to
have sold the property". It sends QFFP to line 3 (p.22) and other farm property to line 5 (p.16)
and prints no sentence putting farmland on line 8, so entering it here is the filer's choice of
list.

A row may apply some of the filer's unapplied restricted farm loss against a gain on farmland.
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

from tax_engine.domain.capability import capability
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.record_list import Record
from tax_engine.domain.trace import TraceLine
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.catalog import (
    DISPOSITION_ADJUSTED_COST_BASE,
    DISPOSITION_FARM_LOSS_INTEREST,
    DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
    DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
    DISPOSITION_OUTLAYS,
    DISPOSITION_PROCEEDS,
)
from tax_engine.jurisdictions.ca.trace import QffpGainLine


@capability(identifier="qffp_gains")
class QffpGains(DispositionRows):
    """Produces `output`: the total of the consumed `dispositions`' column 5, losses included,
    after the restricted farm loss applied."""

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
        line = QffpGainLine(
            self._output,
            position,
            proceeds,
            cost_base,
            outlays,
            farm_loss_taxes,
            farm_loss_interest,
            farm_loss_applied,
            gain,
        )
        return line, gain
