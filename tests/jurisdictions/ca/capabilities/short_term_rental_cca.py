"""Shared pieces of the tests of the Chart B capabilities of Form T776 (non-compliant CCA).

Chart B rows are column 1 "Class number", column 4 "Related portion of the available CCA from
column 21 in Area A", column 5 "Number of days the residential property was a non-compliant
short-term rental" and column 6 "Number of days the residential property was a short-term
rental". The made-up output kinds stand in for the ones the wiring gives.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundingRule, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    NON_COMPLIANT_CCA,
    SHORT_TERM_RENTAL_CCA_UNITS,
    SHORT_TERM_RENTAL_DAYS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
    SHORT_TERM_RENTAL_RELATED_CCA,
)

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# The line 9367 kind and the column 22 list kind come with the wiring; the tests use made-up ones.
LINE_9367 = ArtifactKind("ex/non_compliant_cca", Decimal, non_negative=True)
BY_CLASS = RecordListKind(
    "ex/non_compliant_cca_by_class", fields=(CCA_CLASS_NUMBER, NON_COMPLIANT_CCA)
)

# A row is (column 1, column 4, column 5, column 6).
Row = tuple[str, str, int, int]

# The ticket's example: 900 of related CCA, 30 non-compliant days of 90.
TICKET_ROW: Row = ("1", "900", 30, 90)
# 100 x 1 / 3 = 33.333..., 33.33 when rounded; 500 x 45 / 90 = 250.
THIRD_ROW: Row = ("1", "100", 1, 3)
CLASS_8_ROW: Row = ("8", "500", 45, 90)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    """By default half up to the cent."""
    return ParameterDataset(
        "ex/non_compliant_cca_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def units(*rows: Row) -> Artifact[Any]:
    """A `ca/short_term_rental_cca_units` artifact of one record per row, in order."""
    records: list[Mapping[ArtifactKind[Any], object]] = [
        {
            CCA_CLASS_NUMBER: D(class_number),
            SHORT_TERM_RENTAL_RELATED_CCA: D(related_cca),
            SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS: non_compliant,
            SHORT_TERM_RENTAL_DAYS: days,
        }
        for class_number, related_cca, non_compliant, days in rows
    ]
    return Artifact(
        SHORT_TERM_RENTAL_CCA_UNITS, RecordList(SHORT_TERM_RENTAL_CCA_UNITS.fields, records)
    )
