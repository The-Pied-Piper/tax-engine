"""Shared test data for the DispositionGains and DispositionGainsOnly capabilities, Schedule 3
Part 3 (form 5000-S3).

Each record of a list holds one disposition: "(Column 2): Proceeds of disposition", "(Column 3):
Adjusted cost base" and "(Column 4): Outlays and expenses"; "(Column 5): Gain or loss (column 2
minus columns 3 and 4)" is worked out. The rows below are (proceeds, adjusted cost base, outlays).
A real estate row also holds the filer's 0 or 1 "depreciable property" answer, as a fourth item
(`FlaggedRow`).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    DISPOSITION_ADJUSTED_COST_BASE,
    DISPOSITION_DEPRECIABLE_PROPERTY,
    DISPOSITION_FARM_LOSS_INTEREST,
    DISPOSITION_FARM_LOSS_PROPERTY_TAXES,
    DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST,
    DISPOSITION_OUTLAYS,
    DISPOSITION_PROCEEDS,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    QFFP_DISPOSITIONS,
    REAL_ESTATE_DISPOSITIONS,
    SHARE_DISPOSITIONS,
)

D = Decimal

# One disposition: proceeds (column 2), adjusted cost base (column 3), outlays (column 4).
Row = tuple[str, str, str]
# One real estate disposition: a `Row` and the 0 or 1 depreciable property answer.
FlaggedRow = tuple[str, str, str, int]
# A real estate disposition with a restricted farm loss: a `FlaggedRow`, the property taxes and
# interest part of the loss, and the Guide's line C property taxes and line D interest added.
FarmLossRow = tuple[str, str, str, int, str, str, str]
# A qualified farm or fishing property disposition with a restricted farm loss: a `Row`, the
# property taxes and interest part of the loss, and the property taxes and interest applied.
QffpRow = tuple[str, str, str, str, str, str]
GAIN: Row = ("1500.00", "1000.00", "50.00")  # column 5: 450.00
LOSS: Row = ("800.00", "1000.00", "30.00")  # column 5: -230.00
NOTHING: Row = ("500.00", "400.00", "100.00")  # column 5: 0.00


def rows(kind: RecordListKind, *given: Row) -> Artifact[Any]:
    """A record list of `kind` with one record per row, in the order given."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DISPOSITION_PROCEEDS: D(proceeds),
            DISPOSITION_ADJUSTED_COST_BASE: D(cost_base),
            DISPOSITION_OUTLAYS: D(outlays),
        }
        for proceeds, cost_base, outlays in given
    ]
    return Artifact(kind, RecordList(kind.fields, records))


def shares(*given: Row) -> Artifact[Any]:
    return rows(SHARE_DISPOSITIONS, *given)


def personal_use(*given: Row) -> Artifact[Any]:
    return rows(PERSONAL_USE_PROPERTY_DISPOSITIONS, *given)


def real_estate(*given: FlaggedRow | FarmLossRow) -> Artifact[Any]:
    """A real estate record list: each record holds the three figures, the 0 or 1 answer and the
    restricted farm loss (0 and 0 for a `FlaggedRow`)."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DISPOSITION_PROCEEDS: D(row[0]),
            DISPOSITION_ADJUSTED_COST_BASE: D(row[1]),
            DISPOSITION_OUTLAYS: D(row[2]),
            DISPOSITION_DEPRECIABLE_PROPERTY: row[3],
            DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST: D(row[4]) if len(row) == 7 else D("0"),
            DISPOSITION_FARM_LOSS_PROPERTY_TAXES: D(row[5]) if len(row) == 7 else D("0"),
            DISPOSITION_FARM_LOSS_INTEREST: D(row[6]) if len(row) == 7 else D("0"),
        }
        for row in given
    ]
    return Artifact(REAL_ESTATE_DISPOSITIONS, RecordList(REAL_ESTATE_DISPOSITIONS.fields, records))


def qffp(*given: Row | QffpRow) -> Artifact[Any]:
    """A qualified farm or fishing property record list: each record holds the three figures and
    the restricted farm loss (0, 0 and 0 for a `Row`)."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DISPOSITION_PROCEEDS: D(row[0]),
            DISPOSITION_ADJUSTED_COST_BASE: D(row[1]),
            DISPOSITION_OUTLAYS: D(row[2]),
            DISPOSITION_FARM_LOSS_TAXES_AND_INTEREST: D(row[3]) if len(row) == 6 else D("0"),
            DISPOSITION_FARM_LOSS_PROPERTY_TAXES: D(row[4]) if len(row) == 6 else D("0"),
            DISPOSITION_FARM_LOSS_INTEREST: D(row[5]) if len(row) == 6 else D("0"),
        }
        for row in given
    ]
    return Artifact(QFFP_DISPOSITIONS, RecordList(QFFP_DISPOSITIONS.fields, records))
