"""Shared test data for the DIEP columns of the CCA table, T776 Area A columns 4, 6 and 9.

The rows are those of `cca_table`, whose class-rate dataset and helpers they use, with the three
catalog fields "Column 4: Cost of additions from column 3 that are DIEPs (property must be
available for use before 2025)", "Column 6: Proceeds of dispositions of DIEP (enter amount from
column 5 that relates to DIEP from column 4)" and "Column 9: Immediate expensing amount for
DIEPs". A list kind that lists the three fields makes the table work columns 8, 10 and 13; the
`ex/cca_classes` kind of `cca_table`, which does not, leaves them as 0.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_DIEP_ADDITIONS,
    CCA_DIEP_PROCEEDS,
    CCA_IMMEDIATE_EXPENSING,
)
from tests.jurisdictions.ca.capabilities.cca_table import CLASS_FIELDS, D, row

DIEP_FIELDS = (CCA_DIEP_ADDITIONS, CCA_DIEP_PROCEEDS, CCA_IMMEDIATE_EXPENSING)
DIEP_CLASSES = RecordListKind("ex/cca_diep_classes", fields=(*CLASS_FIELDS, *DIEP_FIELDS))
LIMIT = ArtifactKind("ex/immediate_expensing_limit", Decimal, non_negative=True)
INCOME = ArtifactKind("ex/income_before_cca", Decimal)
IMMEDIATE_EXPENSING = ArtifactKind("ex/immediate_expensing_claim", Decimal, non_negative=True)


def diep_row(
    number: str,
    ucc_at_start: str = "0",
    additions: str = "0",
    proceeds: str = "0",
    aiip_additions: str = "0",
    riip_additions: str = "0",
    claimed: str = "0",
    no_property_left: int = 0,
    diep_additions: str = "0",
    diep_proceeds: str = "0",
    immediate_expensing: str = "0",
) -> dict[ArtifactKind[Any], Decimal | int]:
    """One Area A row with the DIEP columns: `row`'s columns and column 4, column 6 and column 9.
    The claim is column 23, which includes column 9."""
    return {
        **row(
            number,
            ucc_at_start,
            additions,
            proceeds,
            aiip_additions,
            riip_additions,
            claimed,
            no_property_left,
        ),
        CCA_DIEP_ADDITIONS: D(diep_additions),
        CCA_DIEP_PROCEEDS: D(diep_proceeds),
        CCA_IMMEDIATE_EXPENSING: D(immediate_expensing),
    }


def diep_classes(*rows: dict[ArtifactKind[Any], Decimal | int]) -> Artifact[Any]:
    """An `ex/cca_diep_classes` artifact of one record per `diep_row`, in order."""
    return Artifact(DIEP_CLASSES, RecordList(DIEP_CLASSES.fields, rows))


def money(kind: ArtifactKind[Any], amount: str) -> Artifact[Any]:
    """A money artifact of `kind`."""
    return Artifact(kind, D(amount))
