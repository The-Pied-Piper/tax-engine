"""Unit tests for a CCA rate chosen by election, T776 and T2125 Area A column 20, through the CCA
table (`CcaTable`).

Guide T4036 2025, "Class 1 (4%)": "Under proposed changes, new buildings or parts of a building that
are built for use as a purpose-built residential rental (see definition on page 8) may now be
eligible for an accelerated CCA rate of 10%." and "The CCA rate for eligible non-residential
buildings acquired by a taxpayer after March 18, 2007, and used in Canada to manufacture or process
goods for sale or lease includes an additional allowance of 6% for a total rate of 10%. The CCA rate
for other eligible non-residential buildings includes an additional allowance of 2% for a total rate
of 6%." and "If you do not file an election to put it in a separate class, the 4% rate will apply."
and "Property eligible for this measure continues to benefit from the accelerated investment
incentive (AII) if acquired before 2025, or benefits from the reaccelerated investment incentive
(RII) if acquired after 2024."

The caller's row `ca/cca_rate_election` is 0 for no election (the class's own rate), or a code the
row's class lists in the `class_rates` dataset: here Class 1 (4%) lists 1 at 10%, 2 at 6% and 3 at
10%, and Class 8 (20%) lists none. The row's rate is the election's rate for a code above 0, else
the class's rate, and the maximum (column 21) is column 19 times that rate, in the plain and the
prorated capabilities alike. A code above 0 the class does not list is an `InvalidRecordError`
naming the item. Everything else, the AII and RII factors, the half-year rule and recapture, is the
class's own. An absent field (a list kind that does not list it) is 0.

Worked rows, by hand (Class 1 has the half-year rule, an AII factor of 0 and an RII factor of one
half):
B, Class 1, additions 100,000: column 7 100,000; columns 15 and 17 0 (no AII or RII additions);
column 18 one half of 100,000 = 50,000; column 19 100,000 - 50,000 = 50,000. Maximum, by election:
0 or none, 4% of 50,000 = 2,000.00; 1, 10% of 50,000 = 5,000.00; 2, 6% of 50,000 = 3,000.00; 3, 10%
of 50,000 = 5,000.00.
R, Class 1, additions 100,000 of which RII additions 20,000: column 14 max(0, 0 - 100,000 + 0 +
20,000) = 0; column 15 0; column 16 0; column 17 one half of (20,000 - 0) = 10,000; column 18 one
half of 100,000 - 20,000 = 40,000; column 19 100,000 + 0 + 10,000 - 40,000 = 70,000. Maximum, by
election: none 4% of 70,000 = 2,800.00; 1, 10% of 70,000 = 7,000.00. The factors are the class's
whichever the election.
P, row B prorated over 214 days (column 19 times the rate times 214 / 365, one exact fraction
rounded once): none, 50,000 x 4% = 2,000 x 214 / 365 = 1,172.6027..., so 1,172.60; 1, 5,000 x 214 /
365 = 2,931.5068..., so 2,931.51; 2, 3,000 x 214 / 365 = 1,758.9041..., so 1,758.90.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InputAboveBoundError, InvalidRecordError
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_engine.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.catalog import CCA_CLAIMED, CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tax_engine.jurisdictions.ca.trace import CcaClaimLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CLASS_8,
    CLASSES,
    CLOSING_UCC,
    NON_COMPLIANT,
    TERMINAL_LOSS,
    classes,
    non_compliant_cca,
    row,
)
from tests.jurisdictions.ca.capabilities.cca_table_rate_election import (
    RATE_CLASSES,
    election_class_rates,
    election_classes,
    election_row,
)

D = Decimal

FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)

Row = dict[Any, Decimal | int]

# Row B: Class 1, additions 100,000, by election code.
B_NONE = election_row("1", additions="100000", election=0)
B_PURPOSE_BUILT = election_row("1", additions="100000", election=1)
B_SEPARATE_OTHER = election_row("1", additions="100000", election=2)
B_SEPARATE_MANUFACTURING = election_row("1", additions="100000", election=3)
# Row R: Class 1, additions 100,000 of which RII additions 20,000, by election code.
R_NONE = election_row("1", additions="100000", riip_additions="20000", election=0)
R_PURPOSE_BUILT = election_row("1", additions="100000", riip_additions="20000", election=1)


def with_claim(base: Row, claimed: str) -> Row:
    """`base` with the claim `claimed` (column 23)."""
    return {**base, CCA_CLAIMED: D(claimed)}


def claim_trace(*rows: Row) -> tuple[Any, ...]:
    return (
        CcaClaim(election_class_rates(), RATE_CLASSES, CCA_CLAIM)
        .compute((election_classes(*rows),))
        .trace
    )


def claim_total(*rows: Row) -> Decimal:
    (output,) = (
        CcaClaim(election_class_rates(), RATE_CLASSES, CCA_CLAIM)
        .compute((election_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, Decimal)
    return output.value


def claim_after_column_22(column_22: Artifact[Any], *rows: Row) -> Decimal:
    capability = CcaClaimAfterColumn22(
        election_class_rates(), RATE_CLASSES, NON_COMPLIANT, CCA_CLAIM
    )
    (output,) = capability.compute((column_22, election_classes(*rows))).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def claim_prorated(count: int, *rows: Row) -> Decimal:
    capability = CcaClaimProrated(
        election_class_rates(),
        RATE_CLASSES,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CCA_CLAIM,
    )
    (output,) = capability.compute(
        (election_classes(*rows), Artifact(FISCAL_PERIOD_DAYS, count))
    ).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def figures(value: RecordList) -> list[tuple[Decimal | int, Decimal | int]]:
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in value.records]


def closing(*rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    (output,) = (
        ClosingUcc(election_class_rates(), RATE_CLASSES, CLOSING_UCC)
        .compute((election_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_prorated(count: int, *rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccProrated(
        election_class_rates(),
        RATE_CLASSES,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CLOSING_UCC,
    )
    (output,) = capability.compute(
        (election_classes(*rows), Artifact(FISCAL_PERIOD_DAYS, count))
    ).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def terminal_loss(*rows: Row) -> Decimal:
    (output,) = (
        TerminalLoss(election_class_rates(), RATE_CLASSES, TERMINAL_LOSS)
        .compute((election_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, Decimal)
    return output.value


def line_of(trace: tuple[Any, ...]) -> CcaClaimLine:
    """The one claim line of a trace of one row, before its total."""
    (line, _total) = trace
    assert isinstance(line, CcaClaimLine)
    return line


# --- the maximum at the rate of the election -------------------------------------------------


def test_a_class_1_row_without_an_election_keeps_the_class_rate_of_4_percent() -> None:
    # Row B, code 0: column 19 50,000, maximum 4% of it, 2,000.00.
    line = line_of(claim_trace(with_claim(B_NONE, "2000")))

    assert line.column_18 == D("50000")
    assert line.column_19 == D("50000")
    assert line.maximum == D("2000.00")
    assert claim_total(with_claim(B_NONE, "2000")) == D("2000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2000"):
        claim_total(with_claim(B_NONE, "2000.01"))


def test_an_absent_election_keeps_the_class_rate() -> None:
    # `ex/cca_classes` does not list the field: the row is worked at the class's own rate.
    plain = CcaClaim(election_class_rates(), CLASSES, CCA_CLAIM).compute(
        (classes(row("1", additions="100000", claimed="2000")),)
    )
    (output,) = plain.outputs

    assert line_of(plain.trace).maximum == D("2000.00")
    assert output.value == D("2000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2000"):
        CcaClaim(election_class_rates(), CLASSES, CCA_CLAIM).compute(
            (classes(row("1", additions="100000", claimed="2000.01")),)
        )


def test_the_purpose_built_rental_election_gives_a_maximum_at_10_percent_not_4() -> None:
    # Row B, code 1: 10% of 50,000 = 5,000.00, where 4% would give 2,000.00.
    line = line_of(claim_trace(with_claim(B_PURPOSE_BUILT, "5000")))

    assert line.column_19 == D("50000")
    assert line.maximum == D("5000.00")
    assert claim_total(with_claim(B_PURPOSE_BUILT, "5000")) == D("5000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 5000"):
        claim_total(with_claim(B_PURPOSE_BUILT, "5000.01"))


def test_a_claim_between_the_class_rate_and_the_elected_rate_is_allowed_only_by_election() -> None:
    assert claim_total(with_claim(B_PURPOSE_BUILT, "3000")) == D("3000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2000"):
        claim_total(with_claim(B_NONE, "3000"))


def test_the_separate_class_election_for_other_buildings_gives_6_percent() -> None:
    # Row B, code 2: 6% of 50,000 = 3,000.00.
    line = line_of(claim_trace(with_claim(B_SEPARATE_OTHER, "3000")))

    assert line.maximum == D("3000.00")
    assert claim_total(with_claim(B_SEPARATE_OTHER, "3000")) == D("3000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3000"):
        claim_total(with_claim(B_SEPARATE_OTHER, "3000.01"))


def test_the_separate_class_election_for_manufacturing_buildings_gives_10_percent() -> None:
    # Row B, code 3: 10% of 50,000 = 5,000.00.
    line = line_of(claim_trace(with_claim(B_SEPARATE_MANUFACTURING, "5000")))

    assert line.maximum == D("5000.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 5000"):
        claim_total(with_claim(B_SEPARATE_MANUFACTURING, "5000.01"))


def test_each_row_takes_its_own_election() -> None:
    # Row B with code 1 and with code 0 in the same list: 5,000 and 2,000.
    assert claim_total(with_claim(B_PURPOSE_BUILT, "5000"), with_claim(B_NONE, "2000")) == D("7000")
    with pytest.raises(InputAboveBoundError, match=r"item 2: ca/cca_claimed 5000 is above"):
        claim_total(with_claim(B_PURPOSE_BUILT, "5000"), with_claim(B_NONE, "5000"))


def test_the_election_leaves_the_aii_and_rii_factors_as_the_class_has_them() -> None:
    # Row R: column 17 is one half of the RII additions, 10,000, and column 19 70,000, whichever the
    # election; the maximum is 4% (2,800.00) or 10% (7,000.00) of it.
    none = line_of(claim_trace(with_claim(R_NONE, "2800")))
    elected = line_of(claim_trace(with_claim(R_PURPOSE_BUILT, "7000")))

    for line in (none, elected):
        assert line.column_14 == D("0")
        assert line.column_15 == D("0")
        assert line.column_17 == D("10000")
        assert line.column_18 == D("40000")
        assert line.column_19 == D("70000")
    assert none.maximum == D("2800.00")
    assert elected.maximum == D("7000.00")


# --- the other capabilities that work the rows ------------------------------------------------


def test_the_election_reaches_the_claim_after_column_22() -> None:
    # Maximum 5,000 less column 22 1,000: 4,000.
    column = non_compliant_cca(("1", "1000"))

    assert claim_after_column_22(column, with_claim(B_PURPOSE_BUILT, "4000")) == D("4000")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 4000"):
        claim_after_column_22(column, with_claim(B_PURPOSE_BUILT, "4000.01"))


def test_the_election_reaches_the_prorated_claim() -> None:
    # Row P: 50,000 x 10% x 214 / 365 = 2,931.51; at 6%, 1,758.90; with no election, 1,172.60.
    assert claim_prorated(214, with_claim(B_PURPOSE_BUILT, "2931.51")) == D("2931.51")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2931.51"):
        claim_prorated(214, with_claim(B_PURPOSE_BUILT, "2931.52"))
    assert claim_prorated(214, with_claim(B_SEPARATE_OTHER, "1758.90")) == D("1758.90")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1758.90"):
        claim_prorated(214, with_claim(B_SEPARATE_OTHER, "1758.91"))
    assert claim_prorated(214, with_claim(B_NONE, "1172.60")) == D("1172.60")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1172.60"):
        claim_prorated(214, with_claim(B_NONE, "1172.61"))


def test_the_election_reaches_the_closing_ucc() -> None:
    # Column 7 100,000 less the claim 5,000.
    assert closing(with_claim(B_PURPOSE_BUILT, "5000")) == [(D("1"), D("95000"))]
    with pytest.raises(InputAboveBoundError):
        closing(with_claim(B_PURPOSE_BUILT, "5000.01"))


def test_the_election_reaches_the_prorated_closing_ucc() -> None:
    # Column 7 100,000 less the claim 2,931.51.
    assert closing_prorated(214, with_claim(B_PURPOSE_BUILT, "2931.51")) == [
        (D("1"), D("97068.49"))
    ]
    with pytest.raises(InputAboveBoundError):
        closing_prorated(214, with_claim(B_PURPOSE_BUILT, "2931.52"))


def test_the_election_does_not_change_the_terminal_loss() -> None:
    # Column 7 alone: 20,000 less proceeds 15,000 with no property left, 5,000, whichever the code.
    for code in (0, 1, 2, 3):
        left = election_row("1", "20000", proceeds="15000", no_property_left=1, election=code)
        assert terminal_loss(left) == D("5000")


# --- a code the class does not list ----------------------------------------------------------


def test_a_code_the_class_does_not_list_is_refused_naming_the_item() -> None:
    # Class 8 lists no election: code 1 is not a rate it can take.
    wrong = election_row("8", additions="10000", election=1)

    with pytest.raises(InvalidRecordError, match=r"^item 1: .*election 1\b"):
        claim_total(wrong)


def test_a_code_above_the_ones_the_class_lists_is_refused_naming_the_item() -> None:
    # Class 1 lists 1, 2 and 3.
    fine = with_claim(B_NONE, "2000")
    wrong = election_row("1", additions="100000", election=4)

    with pytest.raises(InvalidRecordError, match=r"^item 2: .*election 4\b"):
        claim_total(fine, wrong)


def test_a_code_the_class_does_not_list_is_refused_by_every_capability() -> None:
    wrong = election_row("8", additions="10000", election=2)

    with pytest.raises(InvalidRecordError, match=r"^item 1: .*election 2\b"):
        closing(wrong)
    with pytest.raises(InvalidRecordError, match=r"^item 1: .*election 2\b"):
        terminal_loss(wrong)
    with pytest.raises(InvalidRecordError, match=r"^item 1: .*election 2\b"):
        claim_prorated(214, wrong)


def test_class_8_without_an_election_is_unchanged() -> None:
    # Class 8: UCC 10,000 and additions 3,000, column 19 11,500, 20% = 2,300.00.
    plain = election_row("8", "10000", "3000", election=0)

    assert CLASS_8.rate.value == D("0.20")
    assert line_of(claim_trace(with_claim(plain, "2300"))).maximum == D("2300.00")
