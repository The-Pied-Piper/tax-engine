"""Unit tests for the remaining personal part in the closing UCC of the CCA table, T776 Area A
Note 9.

T776 2025 Area A: "Column 24: UCC at the end of the year (column 7 minus column 23) (Note 9)." and
"Note 9: If, in the year, you disposed of a property that you used for both personal and rental
use, and your rental use of that property changed from year to year, you must subtract any
remaining personal part of this property's cost from the UCC at the end of the year. For more
information, see "Special situations" in Chapter 4 of Guide T4002."

The closing UCC (`ClosingUcc` and so `ClosingUccAfterColumn22` and the two prorated ones) works
column 24 as column 7 less the claim less the remaining personal part when the consumed `classes`
record-list kind lists `ca/cca_personal_part_remaining`; a kind that does not list it leaves the
part as 0 and the results unchanged. A row whose part is above column 7 less the claim is refused
(`InvalidRecordError`, naming the item and both figures). A row that closes at 0 (column 7
negative, or positive with no property left) is unaffected. The part changes only column 24: the
claim (column 23), the recapture and the terminal loss do not depend on it. The `ClosingUccLine`
carries it as `personal_part_remaining`.

Worked rows, by hand:
P: Class 1 (4%), column 2 100,000, column 5 40,000, property left: column 7 60,000; no additions,
so column 18 0 and column 19 60,000; maximum 4% of 60,000 = 2,400.00; claim 2,400; remaining
personal part 5,000: column 24 60,000 - 2,400 - 5,000 = 52,600. Largest part allowed: 57,600.
Q: Class 8 (20%), column 2 10,000, column 3 3,000, claim 2,300 (see `cca_table`): column 7
13,000; column 24 13,000 - 2,300 = 10,700 without a part, 9,700 with a part of 1,000; largest
part 10,700.
Q after column 22 of 500: the limit is 2,300 - 500 = 1,800, claim 1,800; column 24 13,000 - 1,800
= 11,200; with a part of 1,000, 10,200.
G, prorated over 214 days (see `test_cca_table_proration`): Class 8, column 2 17,500, claim
2,052.05, column 24 15,447.95; with a part of 1,000, 14,447.95. After a column 22
of 500.00 the claim is 1,552.05, column 24 15,947.95 and, with a part of 1,000, 14,947.95.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InvalidRecordError
from tax_calculator.domain.jurisdiction_code import JurisdictionCode
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc_after_column_22 import (
    ClosingUccAfterColumn22,
)
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc_after_column_22_prorated import (
    ClosingUccAfterColumn22Prorated,
)
from tax_calculator.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_calculator.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_PERSONAL_PART_REMAINING,
    CCA_UCC_AT_END,
)
from tax_calculator.jurisdictions.ca.trace import CcaZeroReason, ClosingUccLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CLASS_1,
    CLASS_8,
    CLASSES,
    CLOSING_UCC,
    NO_COLUMN_22,
    NON_COMPLIANT,
    TERMINAL_LOSS,
    WITH_ADDITIONS,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    non_compliant_cca,
    row,
    service,
)
from tests.jurisdictions.ca.capabilities.cca_table_personal_part import (
    PERSONAL_CLASSES,
    personal_classes,
    personal_row,
)

D = Decimal

FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)

Row = dict[Any, Decimal | int]

# Row P: column 7 60,000, claim 2,400, part 5,000.
P = personal_row("1", "100000", proceeds="40000", claimed="2400", personal_part="5000")
# Row Q: column 7 13,000, claim 2,300, part 1,000.
Q = personal_row("8", "10000", "3000", claimed="2300", personal_part="1000")
# Row G, prorated over 214 days: column 7 17,500.
G = personal_row("8", "17500", claimed="2052.05", personal_part="1000")


def with_part(base: Row, part: str, claimed: str | None = None) -> Row:
    """`base` with the remaining personal part `part` and, when given, the claim `claimed`."""
    changed = {**base, CCA_PERSONAL_PART_REMAINING: D(part)}
    if claimed is not None:
        changed[CCA_CLAIMED] = D(claimed)
    return changed


def figures(value: RecordList) -> list[tuple[Decimal | int, Decimal | int]]:
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in value.records]


def closing(*rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    (output,) = (
        ClosingUcc(class_rates(), PERSONAL_CLASSES, CLOSING_UCC)
        .compute((personal_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_after_column_22(
    column_22: Artifact[Any], *rows: Row
) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccAfterColumn22(
        class_rates(), PERSONAL_CLASSES, NON_COMPLIANT, CLOSING_UCC
    )
    (output,) = capability.compute((column_22, personal_classes(*rows))).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def days(count: int) -> Artifact[Any]:
    return Artifact(FISCAL_PERIOD_DAYS, count)


def closing_prorated(count: int, *rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccProrated(
        class_rates(),
        PERSONAL_CLASSES,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CLOSING_UCC,
    )
    (output,) = capability.compute((personal_classes(*rows), days(count))).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_prorated_after_column_22(
    count: int, column_22: Artifact[Any], *rows: Row
) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccAfterColumn22Prorated(
        class_rates(),
        PERSONAL_CLASSES,
        non_compliant=NON_COMPLIANT,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CLOSING_UCC,
    )
    (output,) = capability.compute((personal_classes(*rows), days(count), column_22)).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


# --- the closing UCC ----------------------------------------------------------------------------


def test_the_closing_ucc_subtracts_the_remaining_personal_part() -> None:
    # Row P: 60,000 - 2,400 - 5,000.
    assert closing(P) == [(D("1"), D("52600"))]


def test_a_part_of_0_leaves_column_7_less_the_claim() -> None:
    assert closing(personal_row("8", "10000", "3000", claimed="2300")) == [(D("8"), D("10700"))]


def test_the_part_is_subtracted_with_no_claim() -> None:
    # Column 7 13,000 less a part of 1,000.
    assert closing(personal_row("8", "10000", "3000", personal_part="1000")) == [
        (D("8"), D("12000"))
    ]


def test_each_class_takes_its_own_part_in_the_callers_order() -> None:
    assert closing(P, Q, personal_row("8", "10000", "3000", claimed="2300")) == [
        (D("1"), D("52600")),
        (D("8"), D("9700")),
        (D("8"), D("10700")),
    ]


def test_a_part_equal_to_column_7_less_the_claim_closes_at_zero() -> None:
    assert closing(with_part(P, "57600")) == [(D("1"), D("0"))]
    assert closing(with_part(Q, "10700")) == [(D("8"), D("0"))]


def test_a_part_above_column_7_less_the_claim_is_refused() -> None:
    with pytest.raises(InvalidRecordError) as raised:
        closing(with_part(P, "57600.01"))

    assert str(raised.value) == (
        "item 1: personal part (57600.01) is above column 7 less the claim (57600)"
    )


def test_the_refusal_names_the_item_and_both_figures() -> None:
    with pytest.raises(InvalidRecordError) as raised:
        closing(P, with_part(Q, "10700.01"))

    assert str(raised.value) == (
        "item 2: personal part (10700.01) is above column 7 less the claim (10700)"
    )


def test_a_part_above_column_7_with_no_claim_is_refused() -> None:
    with pytest.raises(InvalidRecordError) as raised:
        closing(personal_row("8", "10000", "3000", personal_part="13000.01"))

    assert str(raised.value) == (
        "item 1: personal part (13000.01) is above column 7 less the claim (13000)"
    )


def test_a_smaller_claim_leaves_room_for_a_larger_part() -> None:
    # Claim 1,000 instead of 2,300: the largest part is 12,000.
    small = personal_row("8", "10000", "3000", claimed="1000", personal_part="12000")

    assert closing(small) == [(D("8"), D("0"))]
    with pytest.raises(InvalidRecordError, match=re.escape("less the claim (12000)")):
        closing(with_part(small, "12000.01"))


def test_a_class_with_a_negative_column_7_closes_at_zero_whatever_its_part() -> None:
    recapture = personal_row("10", "5000", proceeds="8000", personal_part="1000")

    assert closing(recapture) == [(D("10"), D("0"))]


def test_a_class_with_no_property_left_closes_at_zero_whatever_its_part() -> None:
    # Column 7 5,000 with no property left: a terminal loss, a UCC of 0.
    left = personal_row("1", "20000", proceeds="15000", no_property_left=1, personal_part="9000")

    assert closing(left) == [(D("1"), D("0"))]


def test_a_class_closing_at_zero_does_not_hide_a_refusal_of_another() -> None:
    recapture = personal_row("10", "5000", proceeds="8000", personal_part="1000")

    with pytest.raises(InvalidRecordError, match=r"^item 2: personal part \(57600.01\)"):
        closing(recapture, with_part(P, "57600.01"))


def test_a_list_that_does_not_list_the_part_leaves_the_results_unchanged() -> None:
    # `ex/cca_classes` does not list the field: the part is 0 and the closing UCC is column 7 less
    # the claim.
    capability = ClosingUcc(class_rates(), CLASSES, CLOSING_UCC)
    plain = capability.compute(
        (classes(row("1", "100000", proceeds="40000", claimed="2400"), WITH_ADDITIONS),)
    )
    listed = ClosingUcc(class_rates(), PERSONAL_CLASSES, CLOSING_UCC).compute(
        (
            personal_classes(
                personal_row("1", "100000", proceeds="40000", claimed="2400"),
                personal_row("8", "10000", "3000", claimed="2300"),
            ),
        )
    )

    assert plain.outputs == listed.outputs
    assert plain.trace == listed.trace
    assert figures(plain.outputs[0].value) == [(D("1"), D("57600")), (D("8"), D("10700"))]
    for line in plain.trace:
        assert isinstance(line, ClosingUccLine)
        assert line.personal_part_remaining == D("0")


# --- after column 22 ----------------------------------------------------------------------------


def test_the_closing_ucc_after_column_22_subtracts_the_part() -> None:
    column_22 = non_compliant_cca(("8", "500"))

    assert closing_after_column_22(column_22, with_part(Q, "1000", "1800")) == [
        (D("8"), D("10200"))
    ]


def test_the_closing_ucc_after_column_22_takes_the_part_off_column_7_less_the_claim() -> None:
    column_22 = non_compliant_cca(("8", "500"))

    assert closing_after_column_22(column_22, with_part(Q, "11200", "1800")) == [(D("8"), D("0"))]
    with pytest.raises(InvalidRecordError) as raised:
        closing_after_column_22(column_22, with_part(Q, "11200.01", "1800"))

    assert str(raised.value) == (
        "item 1: personal part (11200.01) is above column 7 less the claim (11200)"
    )


def test_the_closing_ucc_after_column_22_without_a_column_22_is_the_closing_ucc() -> None:
    assert closing_after_column_22(NO_COLUMN_22, P, Q) == closing(P, Q)


# --- prorated -----------------------------------------------------------------------------------


def test_the_prorated_closing_ucc_subtracts_the_part() -> None:
    # Row G: 17,500 - 2,052.05 - 1,000.
    assert closing_prorated(214, G) == [(D("8"), D("14447.95"))]


def test_the_prorated_closing_ucc_takes_the_part_off_column_7_less_the_prorated_claim() -> None:
    assert closing_prorated(214, with_part(G, "15447.95")) == [(D("8"), D("0"))]
    with pytest.raises(InvalidRecordError) as raised:
        closing_prorated(214, with_part(G, "15447.96"))

    assert str(raised.value) == (
        "item 1: personal part (15447.96) is above column 7 less the claim (15447.95)"
    )


def test_the_prorated_closing_ucc_after_column_22_subtracts_the_part() -> None:
    column_22 = non_compliant_cca(("8", "500.00"))
    given = with_part(G, "1000", "1552.05")

    assert closing_prorated_after_column_22(214, column_22, given) == [(D("8"), D("14947.95"))]
    with pytest.raises(InvalidRecordError) as raised:
        closing_prorated_after_column_22(214, column_22, with_part(given, "15947.96"))

    assert str(raised.value) == (
        "item 1: personal part (15947.96) is above column 7 less the claim (15947.95)"
    )


# --- the claim, the recapture and the terminal loss are unchanged --------------------------------


def test_the_claim_does_not_depend_on_the_part() -> None:
    # A part far above column 7 changes no claim and is not refused by the claim.
    capability = CcaClaim(class_rates(), PERSONAL_CLASSES, CCA_CLAIM)
    big = with_part(P, "99999")

    (output,) = capability.compute((personal_classes(big),)).outputs
    (plain,) = (
        CcaClaim(class_rates(), CLASSES, CCA_CLAIM)
        .compute((classes(row("1", "100000", proceeds="40000", claimed="2400")),))
        .outputs
    )

    assert output.value == D("2400")
    assert output == plain
    assert (
        CcaClaim(class_rates(), PERSONAL_CLASSES, CCA_CLAIM).compute((personal_classes(P),)).trace
        == CcaClaim(class_rates(), CLASSES, CCA_CLAIM)
        .compute((classes(row("1", "100000", proceeds="40000", claimed="2400")),))
        .trace
    )


def test_the_terminal_loss_does_not_depend_on_the_part() -> None:
    given = personal_row("1", "20000", proceeds="15000", no_property_left=1, personal_part="9000")
    (output,) = (
        TerminalLoss(class_rates(), PERSONAL_CLASSES, TERMINAL_LOSS)
        .compute((personal_classes(given),))
        .outputs
    )
    (plain,) = (
        TerminalLoss(class_rates(), CLASSES, TERMINAL_LOSS)
        .compute((classes(WITH_TERMINAL_LOSS),))
        .outputs
    )

    assert output.value == D("5000")
    assert output == plain


# --- the trace ----------------------------------------------------------------------------------


def test_the_closing_line_carries_the_part() -> None:
    result = ClosingUcc(class_rates(), PERSONAL_CLASSES, CLOSING_UCC).compute(
        (personal_classes(P),)
    )

    assert result.trace == (
        ClosingUccLine(
            CLOSING_UCC,
            1,
            CLASS_1,
            0,
            D("60000"),
            CcaZeroReason.NONE,
            D("2400"),
            D("52600"),
            personal_part_remaining=D("5000"),
        ),
    )


def test_the_prorated_closing_line_carries_the_part_and_the_days() -> None:
    capability = ClosingUccProrated(
        class_rates(), PERSONAL_CLASSES, fiscal_period_days=FISCAL_PERIOD_DAYS, output=CLOSING_UCC
    )
    result = capability.compute((personal_classes(G), days(214)))

    assert result.trace == (
        ClosingUccLine(
            CLOSING_UCC,
            1,
            CLASS_8,
            0,
            D("17500"),
            CcaZeroReason.NONE,
            D("2052.05"),
            D("14447.95"),
            fiscal_period_days=214,
            full_year_days=365,
            personal_part_remaining=D("1000"),
        ),
    )


def test_a_class_with_a_part_of_0_traces_0() -> None:
    result = ClosingUcc(class_rates(), PERSONAL_CLASSES, CLOSING_UCC).compute(
        (personal_classes(with_part(P, "0")),)
    )

    (line,) = result.trace
    assert isinstance(line, ClosingUccLine)
    assert line.personal_part_remaining == D("0")
    assert line.result == D("57600")


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_closing_list_less_the_part() -> None:
    worksheet = service("ca/closing_ucc", CLOSING_UCC, classes_kind=PERSONAL_CLASSES).compute(
        JurisdictionCode("CA-ON"), 2025, personal_classes(P, Q)
    )["ca-on/return"][0]

    assert figures(worksheet.get(CLOSING_UCC).value) == [
        (D("1"), D("52600")),
        (D("8"), D("9700")),
    ]


def test_a_computation_refuses_a_part_above_column_7_less_the_claim() -> None:
    computing = service("ca/closing_ucc", CLOSING_UCC, classes_kind=PERSONAL_CLASSES)

    with pytest.raises(InvalidRecordError, match=r"item 1: personal part \(57600.01\)"):
        computing.compute(
            JurisdictionCode("CA-ON"), 2025, personal_classes(with_part(P, "57600.01"))
        )
