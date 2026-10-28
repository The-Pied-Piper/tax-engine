"""Shared test data for the remaining personal part of the CCA table, T776 Area A Note 9.

The rows are those of `cca_table`, whose class-rate dataset and helpers they use, with the catalog
field "Remaining personal part" (`ca/cca_personal_part_remaining`) of Note 9 for column 24: "If, in
the year, you disposed of a property that you used for both personal and rental use, and your
rental use of that property changed from year to year, you must subtract any remaining personal
part of this property's cost from the UCC at the end of the year." A list kind that lists the
field makes the closing UCC subtract it; the `ex/cca_classes` kind of `cca_table`, which does not,
leaves it as 0.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import CCA_PERSONAL_PART_REMAINING
from tests.jurisdictions.ca.capabilities.cca_table import CLASS_FIELDS, D, row

PERSONAL_CLASSES = RecordListKind(
    "ex/cca_personal_part_classes", fields=(*CLASS_FIELDS, CCA_PERSONAL_PART_REMAINING)
)


def personal_row(
    number: str,
    ucc_at_start: str = "0",
    additions: str = "0",
    proceeds: str = "0",
    claimed: str = "0",
    no_property_left: int = 0,
    personal_part: str = "0",
) -> dict[ArtifactKind[Any], Decimal | int]:
    """One Area A row with Note 9's remaining personal part: `row`'s columns and the part."""
    return {
        **row(
            number,
            ucc_at_start,
            additions,
            proceeds,
            claimed=claimed,
            no_property_left=no_property_left,
        ),
        CCA_PERSONAL_PART_REMAINING: D(personal_part),
    }


def personal_classes(*rows: dict[ArtifactKind[Any], Decimal | int]) -> Artifact[Any]:
    """An `ex/cca_personal_part_classes` artifact of one record per `personal_row`, in order."""
    return Artifact(PERSONAL_CLASSES, RecordList(PERSONAL_CLASSES.fields, rows))
