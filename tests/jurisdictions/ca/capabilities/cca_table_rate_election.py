"""Shared test data for a CCA rate chosen by election, T776 and T2125 Area A column 20.

Guide T4036 2025, "Class 1 (4%)": "Under proposed changes, new buildings or parts of a building that
are built for use as a purpose-built residential rental (see definition on page 8) may now be
eligible for an accelerated CCA rate of 10%." and "The CCA rate for eligible non-residential
buildings acquired by a taxpayer after March 18, 2007, and used in Canada to manufacture or process
goods for sale or lease includes an additional allowance of 6% for a total rate of 10%. The CCA rate
for other eligible non-residential buildings includes an additional allowance of 2% for a total rate
of 6%." and "To be eligible for one of the additional allowances, you must elect to put a building
in a separate class. ... If you do not file an election to put it in a separate class, the 4% rate
will apply."

The caller marks a row with the election it makes, `ca/cca_rate_election`: 0 for none (the class's
own rate), else a code the row's class lists in the `class_rates` dataset. The made-up Class 1 here
lists three, as the 2025 dataset does: 1 (purpose-built residential rental) at 10%, 2 (separate
class, other non-residential building) at 6% and 3 (separate class, manufacturing or processing
building) at 10%. Class 8 lists none. The field is the last of each of the four class
record-list kinds; the `ex/` kind here lists it, and the rows are those of `cca_table`, whose
helpers they use. A list kind that does not list the field, as the `ex/cca_classes` kind of
`cca_table`, leaves every row at its class's own rate.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.class_rates import ClassElection, ClassRate, ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.catalog import CCA_RATE_ELECTION
from tests.jurisdictions.ca.capabilities.cca_table import (
    ALL_CLASSES,
    APPLIES,
    CLASS_1,
    CLASS_FIELDS,
    INCLUDED,
    NOT_ON_SALE,
    D,
    F,
    class_rates,
    row,
)

RATE_CLASSES = RecordListKind("ex/cca_rate_classes", fields=(*CLASS_FIELDS, CCA_RATE_ELECTION))

PURPOSE_BUILT = ClassElection(1, Rate(D("0.10")))
SEPARATE_OTHER = ClassElection(2, Rate(D("0.06")))
SEPARATE_MANUFACTURING = ClassElection(3, Rate(D("0.10")))

# Class 1 at 4% as `cca_table` has it, with the three elections.
CLASS_1_ELECTIONS = ClassRate(
    D("1"),
    Rate(D("0.04")),
    APPLIES,
    INCLUDED,
    F(0, 1),
    F(1, 2),
    NOT_ON_SALE,
    (PURPOSE_BUILT, SEPARATE_OTHER, SEPARATE_MANUFACTURING),
)


def election_class_rates() -> ParameterDataset[ClassRates]:
    """The classes of `cca_table`, Class 1 with its three elections, to the cent."""
    return class_rates(
        classes=tuple(CLASS_1_ELECTIONS if each is CLASS_1 else each for each in ALL_CLASSES)
    )


def election_row(
    number: str,
    ucc_at_start: str = "0",
    additions: str = "0",
    proceeds: str = "0",
    claimed: str = "0",
    no_property_left: int = 0,
    election: int = 0,
    aiip_additions: str = "0",
    riip_additions: str = "0",
) -> dict[ArtifactKind[Any], Decimal | int]:
    """One Area A row with the rate election `election`: `row`'s columns and the election."""
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
        CCA_RATE_ELECTION: election,
    }


def election_classes(*rows: dict[ArtifactKind[Any], Decimal | int]) -> Artifact[Any]:
    """An `ex/cca_rate_classes` artifact of one record per `election_row`, in order."""
    return Artifact(RATE_CLASSES, RecordList(RATE_CLASSES.fields, rows))
