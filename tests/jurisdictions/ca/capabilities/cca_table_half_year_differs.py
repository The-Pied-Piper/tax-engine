"""Shared test data for the half-year rule that differs from a class's own, T776 and T2125 Area A
column 18.

Guide T4002 2025, "Column 18": "Also, some properties are not subject to the half-year rule. Some
examples are those in Classes 13, 14, 23, 24, 27, 34, and 52, as well as most of those in Class 12,
such as small tools." and "Class 12 tools that are subject to the half-year rule include dies, jigs,
patterns, moulds, and lasts, as well as the cutting or shaping part of a machine." and "Include in
Class 12 with a CCA rate of 100% computer software that is not systems software. Software in Class
12 is subject to the half-year rule."

The caller marks a row whose additions are treated the opposite way from their class: a class the
`class_rates` dataset marks exempt (Class 12) is then subject, and a class marked subject (Class 8)
is then exempt. The field is `ca/cca_half_year_rule_differs`, the last field of each of the four
class record-list kinds (T776, T2125, T2042 and T2121); the `ex/` kind here lists it, and the rows
are those of `cca_table`, whose class-rate dataset and helpers they use. A list kind that does not
list the field, as the `ex/cca_classes` kind of `cca_table`, leaves every row with its class's own
treatment.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import CCA_HALF_YEAR_RULE_DIFFERS
from tests.jurisdictions.ca.capabilities.cca_table import CLASS_FIELDS, row

HALF_YEAR_CLASSES = RecordListKind(
    "ex/cca_half_year_classes", fields=(*CLASS_FIELDS, CCA_HALF_YEAR_RULE_DIFFERS)
)


def half_year_row(
    number: str,
    ucc_at_start: str = "0",
    additions: str = "0",
    proceeds: str = "0",
    claimed: str = "0",
    no_property_left: int = 0,
    differs: int = 0,
    aiip_additions: str = "0",
    riip_additions: str = "0",
) -> dict[ArtifactKind[Any], Decimal | int]:
    """One Area A row with the half-year flag `differs`: `row`'s columns and the flag."""
    return {
        **row(
            number,
            ucc_at_start,
            additions,
            proceeds,
            aiip_additions=aiip_additions,
            riip_additions=riip_additions,
            claimed=claimed,
            no_property_left=no_property_left,
        ),
        CCA_HALF_YEAR_RULE_DIFFERS: differs,
    }


def half_year_classes(*rows: dict[ArtifactKind[Any], Decimal | int]) -> Artifact[Any]:
    """An `ex/cca_half_year_classes` artifact of one record per `half_year_row`, in order."""
    return Artifact(HALF_YEAR_CLASSES, RecordList(HALF_YEAR_CLASSES.fields, rows))
