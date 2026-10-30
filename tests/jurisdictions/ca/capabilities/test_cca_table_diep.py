"""Unit tests for the DIEP columns of the CCA table (`CcaTable`), T776 Area A columns 4, 6, 8, 9.

T776 Area A: "Column 4: Cost of additions from column 3 that are DIEPs (property must be available
for use before 2025) (Note 1)", "Column 6: Proceeds of dispositions of DIEP (enter amount from
column 5 that relates to DIEP from column 4)", "Column 8: UCC of DIEP (column 4 minus column 6)
(Note 4)" with Note 4: "The amount you enter in column 8 must not be more than the amount from
column 7. If the amount from column 7 is negative, enter "0."", "Column 9: Immediate expensing
amount for DIEPs (Note 5)", "Column 10: Cost of remaining additions after immediate expensing
(column 3 minus column 9)", "Column 13: Remaining UCC after immediate expensing (column 7 minus
column 9)", "Column 19: Base amount for CCA (column 13 plus column 15 plus column 17 minus column
18)" and "Column 21: Available CCA for the year (column 19 multiplied by column 20, or a lower
amount, plus column 9)". Guide T4036 "Column 8 - UCC of DIEP": "If the result of column 4 minus
column 6 exceeds the amount from column 7, enter in column 8 the amount from column 7. If the
amount from column 7 is negative, enter "0."".

The table works those columns when the consumed `classes` record-list kind lists the three fields
(`ca/cca_diep_additions`, `ca/cca_diep_proceeds`, `ca/cca_immediate_expensing`). The caller's claim
(column 23) includes column 9, so a class's claim is at least column 9 less column 22 (never below
0) and at most its maximum plus column 9 less column 22. A row whose column 4 is above column 3,
whose column 6 is above column 5 or whose column 9 is above column 8 is refused
(`InvalidRecordError`, naming the item). Recapture depends only on column 7. A terminal loss is
column 7 less column 9, not below 0: Regulation 1100(0.2) deducts column 9 from the UCC first, and
Guide T4036 calls it "an amount you have not deducted as CCA", so the part expensed is not lost
twice.

Worked rows, Class 8 (20%, half-year rule), by hand:

A: column 2 1,000, column 3 5,000, column 4 4,000, column 9 3,000. Column 7 6,000; column 8 4,000;
column 10 5,000 - 3,000 = 2,000; column 13 6,000 - 3,000 = 3,000; column 14 0; column 18 one half of
2,000 = 1,000; column 19 3,000 - 1,000 = 2,000; maximum 20% of 2,000 = 400.00; column 21 400 +
3,000 = 3,400; column 24 6,000 - 3,400 = 2,600.
B (fully expensed): column 2 1,000, column 3 5,000, column 4 5,000, column 9 5,000. Column 7 6,000;
column 8 5,000; column 10 0; column 13 1,000; column 18 0; column 19 1,000; maximum 200.00; column
21 5,200; column 24 800.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidRecordError,
)
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.catalog import CCA_CLAIMED, CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tax_engine.jurisdictions.ca.trace import (
    CcaClaimLine,
    CcaZeroReason,
    ClosingUccLine,
    TerminalLossLine,
)
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CENT,
    CLASS_8,
    CLASS_12,
    CLASS_43_1,
    CLASSES,
    CLOSING_UCC,
    NON_COMPLIANT,
    RECAPTURED_CCA,
    TERMINAL_LOSS,
    class_rates,
    classes,
    non_compliant_cca,
    row,
)
from tests.jurisdictions.ca.capabilities.cca_table_diep import (
    DIEP_CLASSES,
    diep_classes,
    diep_row,
)

D = Decimal

# Row A and row B of the module docstring; the claim is column 23, column 9 included.
A_ROW = diep_row("8", "1000", "5000", diep_additions="4000", immediate_expensing="3000")
B_ROW = diep_row("8", "1000", "5000", diep_additions="5000", immediate_expensing="5000")


def with_claim(base: dict[Any, Decimal | int], claimed: str) -> dict[Any, Decimal | int]:
    return {**base, CCA_CLAIMED: D(claimed)}


def claim_trace(*rows: dict[Any, Decimal | int]) -> tuple[Any, ...]:
    return CcaClaim(class_rates(), DIEP_CLASSES, CCA_CLAIM).compute((diep_classes(*rows),)).trace


def claim_total(*rows: dict[Any, Decimal | int]) -> Decimal:
    result = CcaClaim(class_rates(), DIEP_CLASSES, CCA_CLAIM).compute((diep_classes(*rows),))
    (output,) = result.outputs
    assert isinstance(output.value, Decimal)
    return output.value


def closing(*rows: dict[Any, Decimal | int]) -> list[tuple[Decimal | int, Decimal | int]]:
    result = ClosingUcc(class_rates(), DIEP_CLASSES, CLOSING_UCC).compute((diep_classes(*rows),))
    (output,) = result.outputs
    assert isinstance(output.value, RecordList)
    return [(r[CCA_CLASS_NUMBER], r[CCA_UCC_AT_END]) for r in output.value.records]


def after_column_22(column_22: Artifact[Any], *rows: dict[Any, Decimal | int]) -> Decimal:
    capability = CcaClaimAfterColumn22(class_rates(), DIEP_CLASSES, NON_COMPLIANT, CCA_CLAIM)
    (output,) = capability.compute((column_22, diep_classes(*rows))).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- column 9 in the claim and the closing UCC --------------------------------------------------


def test_a_class_with_a_diep_claims_its_maximum_plus_column_9() -> None:
    # Row A: maximum 400.00, column 21 = 400 + 3,000 = 3,400.
    assert claim_total(with_claim(A_ROW, "3400")) == D("3400")


def test_the_claim_may_be_as_low_as_column_9() -> None:
    # Column 23 is column 21 less column 22: at least column 9 (3,000) when column 22 is 0.
    assert claim_total(with_claim(A_ROW, "3000")) == D("3000")


def test_a_claim_above_the_maximum_plus_column_9_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 3400.01 is above the"):
        claim_total(with_claim(A_ROW, "3400.01"))


def test_a_claim_above_the_maximum_plus_column_9_names_the_limit() -> None:
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3400"):
        claim_total(with_claim(A_ROW, "3400.01"))


def test_a_claim_below_column_9_is_refused() -> None:
    # The immediate expensing is part of the claim, so the claim cannot be less than column 9.
    with pytest.raises(
        InputBelowBoundError, match=r"^item 1: ca/cca_claimed 2999.99 is below the minimum 3000"
    ):
        claim_total(with_claim(A_ROW, "2999.99"))


def test_a_fully_expensed_class_claims_from_column_9_to_column_21() -> None:
    # Row B: maximum 200.00, column 21 = 200 + 5,000 = 5,200; at least 5,000.
    assert claim_total(with_claim(B_ROW, "5200")) == D("5200")
    assert claim_total(with_claim(B_ROW, "5000")) == D("5000")
    with pytest.raises(InputAboveBoundError):
        claim_total(with_claim(B_ROW, "5200.01"))
    with pytest.raises(InputBelowBoundError):
        claim_total(with_claim(B_ROW, "4999.99"))


def test_the_closing_ucc_uses_the_claim_that_includes_column_9() -> None:
    # Column 24 = column 7 - column 23: A at the full claim 6,000 - 3,400 = 2,600, at the least
    # claim 6,000 - 3,000 = 3,000; B 6,000 - 5,200 = 800.
    assert closing(with_claim(A_ROW, "3400")) == [(D("8"), D("2600"))]
    assert closing(with_claim(A_ROW, "3000")) == [(D("8"), D("3000"))]
    assert closing(with_claim(B_ROW, "5200")) == [(D("8"), D("800"))]


def test_the_closing_ucc_refuses_a_claim_out_of_bounds_as_the_claim_does() -> None:
    with pytest.raises(InputAboveBoundError):
        closing(with_claim(A_ROW, "3400.01"))
    with pytest.raises(InputBelowBoundError):
        closing(with_claim(A_ROW, "2999.99"))


def test_traces_columns_7_to_19_and_column_9_of_the_claim() -> None:
    # Row A: column 7 6,000; columns 14 to 17 0; column 18 1,000; column 19 2,000; maximum 400.00;
    # claim 3,400; column_9 3,000.
    assert claim_trace(with_claim(A_ROW, "3400")) == (
        CcaClaimLine(
            output=CCA_CLAIM,
            position=1,
            class_rate=CLASS_8,
            no_property_left=0,
            column_7=D("6000"),
            column_14=D("0"),
            column_15=D("0"),
            column_16=D("0"),
            column_17=D("0"),
            column_18=D("1000"),
            column_19=D("2000"),
            zero_reason=CcaZeroReason.NONE,
            maximum=D("400.00"),
            rounding=CENT,
            claim=D("3400"),
            column_9=D("3000"),
        ),
        ItemsTotalLine(CCA_CLAIM, ((1, D("3400")),), D("3400")),
    )


def test_traces_column_9_of_the_closing_ucc() -> None:
    result = ClosingUcc(class_rates(), DIEP_CLASSES, CLOSING_UCC).compute(
        (diep_classes(with_claim(A_ROW, "3400")),)
    )

    assert result.trace == (
        ClosingUccLine(
            CLOSING_UCC,
            1,
            CLASS_8,
            0,
            D("6000"),
            CcaZeroReason.NONE,
            D("3400"),
            D("2600"),
            column_9=D("3000"),
        ),
    )


def test_a_class_without_a_diep_traces_column_9_as_0() -> None:
    # The lines of a table that has the DIEP fields with 0 in them are the lines of one without.
    plain = row("8", "10000", "3000", claimed="2300")
    diep = diep_row("8", "10000", "3000", claimed="2300")

    with_fields = claim_trace(diep)
    without = CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute((classes(plain),)).trace
    assert with_fields == without
    assert with_fields[0].column_9 == D("0")


# --- a table that does not list the DIEP fields ---------------------------------------------------


def test_a_list_kind_without_the_diep_fields_is_worked_as_before() -> None:
    # Class 8, UCC 10,000 and additions 3,000: maximum 2,300.00 and no column 9.
    plain = row("8", "10000", "3000", claimed="2300")

    result = CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute((classes(plain),))

    (output,) = result.outputs
    assert output == Artifact(CCA_CLAIM, D("2300"))
    with pytest.raises(InputAboveBoundError):
        CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute(
            (classes(row("8", "10000", "3000", claimed="2300.01")),)
        )


# --- column 8: UCC of DIEP --------------------------------------------------------------------


def test_column_9_may_be_all_of_column_8_when_column_7_limits_it() -> None:
    # Column 2 0, column 3 5,000, column 5 2,000, column 4 5,000, column 6 0: column 7 3,000,
    # column 4 less column 6 5,000, so column 8 = 3,000 (Note 4). Column 9 3,000: column 10
    # 5,000 - 3,000 = 2,000; column 13 0; column 14 2,000 - 2,000 = 0; column 18 one half of
    # (2,000 - 0 - 0 - 2,000) = 0; column 19 0; maximum 0; column 21 3,000; column 24 0.
    full = diep_row(
        "8", "0", "5000", "2000", diep_additions="5000", immediate_expensing="3000", claimed="3000"
    )

    assert claim_total(full) == D("3000")
    assert closing(full) == [(D("8"), D("0"))]


def test_column_9_above_column_8_limited_by_column_7_is_refused() -> None:
    above = diep_row(
        "8", "0", "5000", "2000", diep_additions="5000", immediate_expensing="3001", claimed="3001"
    )

    with pytest.raises(InvalidRecordError) as raised:
        claim_total(above)

    assert str(raised.value) == "item 1: column 9 (3001) is above column 8 (3000)"


def test_column_9_above_column_8_is_refused() -> None:
    # Column 8 is column 4 less column 6 = 4,000.
    above = diep_row("8", "1000", "5000", diep_additions="4000", immediate_expensing="4001")

    with pytest.raises(InvalidRecordError) as raised:
        claim_total(above)

    assert str(raised.value) == "item 1: column 9 (4001) is above column 8 (4000)"


def test_a_column_6_above_column_4_gives_a_column_8_of_0() -> None:
    # Column 2 2,000, column 3 1,000, column 5 1,500, column 4 1,000, column 6 1,500: column 7
    # 1,500, column 4 less column 6 -500 so column 8 0 (column 9 0). Column 10 1,000; column 13
    # 1,500; column 14 500 - 0 = 500; columns 15 to 17 0; column 18 0; column 19 1,500; maximum
    # 300.00; column 24 1,200.
    over = diep_row(
        "8", "2000", "1000", "1500", diep_additions="1000", diep_proceeds="1500", claimed="300"
    )

    assert claim_total(over) == D("300")
    assert closing(over) == [(D("8"), D("1200"))]


def test_a_column_9_above_a_column_8_of_0_from_column_6_is_refused() -> None:
    over = diep_row(
        "8",
        "2000",
        "1000",
        "1500",
        diep_additions="1000",
        diep_proceeds="1500",
        immediate_expensing="1",
        claimed="301",
    )

    with pytest.raises(InvalidRecordError) as raised:
        claim_total(over)

    assert str(raised.value) == "item 1: column 9 (1) is above column 8 (0)"


def test_a_negative_column_7_gives_a_column_8_of_0_so_column_9_is_refused() -> None:
    # Column 7: 1,000 + 5,000 - 7,000 = -1,000, so column 8 is 0 (Note 4), not 4,000.
    negative = diep_row(
        "8", "1000", "5000", "7000", diep_additions="4000", immediate_expensing="100", claimed="100"
    )

    with pytest.raises(InvalidRecordError) as raised:
        claim_total(negative)

    assert str(raised.value) == "item 1: column 9 (100) is above column 8 (0)"


def test_a_negative_column_7_without_column_9_allows_no_claim() -> None:
    negative = diep_row("8", "1000", "5000", "7000", diep_additions="4000")

    assert claim_total(negative) == D("0")
    assert closing(negative) == [(D("8"), D("0"))]
    assert claim_trace(negative)[0].zero_reason is CcaZeroReason.COLUMN_7_NEGATIVE
    assert claim_trace(negative)[0].column_9 == D("0")


# --- per-class refusals -------------------------------------------------------------------------


def test_a_column_4_above_column_3_is_refused() -> None:
    with pytest.raises(InvalidRecordError) as raised:
        claim_total(diep_row("8", "0", "1000", diep_additions="1001"))

    assert str(raised.value) == "item 1: column 4 (1001) is above column 3 (1000)"


def test_a_column_6_above_column_5_is_refused() -> None:
    with pytest.raises(InvalidRecordError) as raised:
        claim_total(diep_row("8", "0", "1000", "500", diep_additions="1000", diep_proceeds="501"))

    assert str(raised.value) == "item 1: column 6 (501) is above column 5 (500)"


def test_the_refusal_names_the_item() -> None:
    with pytest.raises(InvalidRecordError, match=r"^item 2: column 4 \(1001\)"):
        claim_total(with_claim(A_ROW, "3400"), diep_row("8", "0", "1000", diep_additions="1001"))


def test_columns_11_and_12_are_checked_against_column_10() -> None:
    # Column 10 is 5,000 - 3,000 = 2,000; columns 11 and 12 of 2,500 are above it though below
    # column 3.
    above = diep_row(
        "43.1",
        "0",
        "5000",
        aiip_additions="2500",
        diep_additions="5000",
        immediate_expensing="3000",
    )

    with pytest.raises(InvalidRecordError) as raised:
        claim_total(above)

    assert str(raised.value) == "item 1: columns 11 and 12 (2500) are above column 10 (2000)"


# --- columns 14, 18 and 19 on columns 10 and 13 ------------------------------------------------


def test_columns_14_18_and_19_follow_columns_10_and_13() -> None:
    # Class 43.1 (30%, AIIP factor 3/2): column 2 0, column 3 10,000, column 5 3,000, column 4
    # 10,000, column 6 0, column 11 4,000, column 9 4,000. Column 7 7,000; column 8 7,000; column
    # 10 6,000; column 13 3,000; column 14 3,000 - 6,000 + 4,000 = 1,000 (on column 3 it would be
    # 0); column 15 (4,000 - 1,000) x 3/2 = 4,500; column 16 0; column 17 0; column 18 one half
    # of (6,000 - 4,000 - 3,000) < 0 = 0; column 19 3,000 + 4,500 = 7,500; maximum 30% =
    # 2,250.00; column 21 2,250 + 4,000 = 6,250; column 24 750.
    aiip = diep_row(
        "43.1",
        "0",
        "10000",
        "3000",
        aiip_additions="4000",
        diep_additions="10000",
        immediate_expensing="4000",
        claimed="6250",
    )

    assert claim_trace(aiip) == (
        CcaClaimLine(
            output=CCA_CLAIM,
            position=1,
            class_rate=CLASS_43_1,
            no_property_left=0,
            column_7=D("7000"),
            column_14=D("1000"),
            column_15=D("4500"),
            column_16=D("0"),
            column_17=D("0"),
            column_18=D("0"),
            column_19=D("7500"),
            zero_reason=CcaZeroReason.NONE,
            maximum=D("2250.00"),
            rounding=CENT,
            claim=D("6250"),
            column_9=D("4000"),
        ),
        ItemsTotalLine(CCA_CLAIM, ((1, D("6250")),), D("6250")),
    )
    assert closing(aiip) == [(D("43.1"), D("750"))]


def test_a_claim_above_the_maximum_of_a_row_with_aiip_additions_is_refused() -> None:
    aiip = diep_row(
        "43.1",
        "0",
        "10000",
        "3000",
        aiip_additions="4000",
        diep_additions="10000",
        immediate_expensing="4000",
        claimed="6250.01",
    )

    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 6250.01"):
        claim_total(aiip)


# --- two classes --------------------------------------------------------------------------------


def test_two_classes_are_worked_each_on_its_own() -> None:
    # Row A (claim 3,400) and a Class 12 row (100%, exempt from the half-year rule): column 3
    # 2,000, column 4 2,000, column 9 1,500; column 7 2,000; column 10 500; column 13 500;
    # column 18 0; column 19 500; maximum 500.00; column 21 2,000; column 24 0.
    twelve = diep_row(
        "12", "0", "2000", diep_additions="2000", immediate_expensing="1500", claimed="2000"
    )
    rows = (with_claim(A_ROW, "3400"), twelve)

    assert claim_total(*rows) == D("5400")
    assert closing(*rows) == [(D("8"), D("2600")), (D("12"), D("0"))]
    lines = claim_trace(*rows)
    assert [line.column_9 for line in lines[:2]] == [D("3000"), D("1500")]
    assert lines[1].class_rate == CLASS_12
    assert lines[1].maximum == D("500")


# --- column 22 ----------------------------------------------------------------------------------


def test_column_22_is_taken_from_the_claim_not_from_column_9() -> None:
    # Column 22 of 500 on row A: the most is 400 + 3,000 - 500 = 2,900 and the least 3,000 - 500
    # = 2,500.
    column_22 = non_compliant_cca(("8", "500"))

    assert after_column_22(column_22, with_claim(A_ROW, "2900")) == D("2900")
    assert after_column_22(column_22, with_claim(A_ROW, "2500")) == D("2500")
    with pytest.raises(InputAboveBoundError):
        after_column_22(column_22, with_claim(A_ROW, "2900.01"))
    with pytest.raises(InputBelowBoundError):
        after_column_22(column_22, with_claim(A_ROW, "2499.99"))


def test_a_column_22_above_column_21_allows_a_claim_of_0_only() -> None:
    # Column 21 is 3,400 and column 22 4,000: the claim (column 23) is 0, never negative, so the
    # least and the most are both 0 (to be confirmed: the form does not print this case).
    column_22 = non_compliant_cca(("8", "4000"))

    assert after_column_22(column_22, with_claim(A_ROW, "0")) == D("0")
    with pytest.raises(InputAboveBoundError):
        after_column_22(column_22, with_claim(A_ROW, "0.01"))


# --- recapture and terminal loss ----------------------------------------------------------------


def test_recapture_depends_only_on_column_7() -> None:
    # Column 7: 1,000 + 5,000 - 7,000 = -1,000, a recapture of 1,000 with or without the DIEP
    # columns.
    negative = diep_row("8", "1000", "5000", "7000", diep_additions="4000", diep_proceeds="4000")
    capability = RecapturedCca(class_rates(), DIEP_CLASSES, RECAPTURED_CCA)

    (output,) = capability.compute((diep_classes(negative),)).outputs

    assert output == Artifact(RECAPTURED_CCA, D("1000"))


def test_a_diep_does_not_cause_a_recapture_when_column_7_is_positive() -> None:
    capability = RecapturedCca(class_rates(), DIEP_CLASSES, RECAPTURED_CCA)

    (output,) = capability.compute((diep_classes(with_claim(A_ROW, "3400")),)).outputs

    assert output == Artifact(RECAPTURED_CCA, D("0"))


def last_row(
    number: str = "8", column_7: str = "4000", column_9: str = "0", additions: str | None = None
) -> dict[ArtifactKind[Any], Decimal | int]:
    """A row with nothing left in the class: column 7 `column_7` (all additions), column 9
    `column_9` of it expensed, and the claim of column 9 (column 21 = 0 + column 9)."""
    return diep_row(
        number,
        "0",
        additions or column_7,
        diep_additions=column_7 if column_9 != "0" else "0",
        immediate_expensing=column_9,
        claimed=column_9,
        no_property_left=1,
    )


def terminal_loss(*rows: dict[ArtifactKind[Any], Decimal | int]) -> Decimal:
    capability = TerminalLoss(class_rates(), DIEP_CLASSES, TERMINAL_LOSS)
    (output,) = capability.compute((diep_classes(*rows),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_terminal_loss_is_column_7_less_column_9() -> None:
    # Column 7 4,000 with no property left and all of it expensed (column 9 4,000, so the claim
    # is 4,000): nothing was left undeducted, so no terminal loss. Guide T4036: "an amount you have
    # not deducted as CCA"; Regulation 1100(0.2).
    assert terminal_loss(last_row(column_7="4000", column_9="4000")) == D("0")


def test_a_class_bought_expensed_and_emptied_in_the_same_year_has_no_terminal_loss() -> None:
    # Opening UCC 0, additions 4,000 all DIEP, column 9 4,000, then the property is disposed of for
    # 0 proceeds: column 7 4,000, nothing left, nothing undeducted.
    same_year = diep_row(
        "8",
        "0",
        "4000",
        diep_additions="4000",
        immediate_expensing="4000",
        claimed="4000",
        no_property_left=1,
    )

    assert terminal_loss(same_year) == D("0")


def test_a_partly_expensed_class_has_a_terminal_loss_of_column_7_less_column_9() -> None:
    assert terminal_loss(last_row(column_7="4000", column_9="1000")) == D("3000")


def test_a_terminal_loss_without_immediate_expensing_is_column_7() -> None:
    assert terminal_loss(last_row(column_7="4000", column_9="0")) == D("4000")
    assert terminal_loss(diep_row("8", "20000", "0", "15000", no_property_left=1)) == D("5000")


def test_the_column_9_is_taken_off_each_class_before_the_losses_are_added() -> None:
    other = diep_row("12", "0", "1000", no_property_left=1)

    assert terminal_loss(last_row(column_9="1000"), other, last_row(column_9="4000")) == D("4000")


def test_the_terminal_loss_line_records_column_9() -> None:
    capability = TerminalLoss(class_rates(), DIEP_CLASSES, TERMINAL_LOSS)

    lines = capability.compute((diep_classes(last_row(column_9="1000")),)).trace
    (line, total) = lines

    assert isinstance(line, TerminalLossLine)
    assert (line.column_7, line.column_9, line.result) == (D("4000"), D("1000"), D("3000"))
    assert line.zero_reason is CcaZeroReason.NO_PROPERTY_LEFT
    assert isinstance(total, ItemsTotalLine)
    assert total.total == D("3000")


def test_the_terminal_loss_line_records_a_column_9_of_0_without_immediate_expensing() -> None:
    capability = TerminalLoss(class_rates(), DIEP_CLASSES, TERMINAL_LOSS)

    (line, _total) = capability.compute((diep_classes(last_row(column_9="0")),)).trace

    assert isinstance(line, TerminalLossLine)
    assert line.column_9 == D("0")


def test_a_class_10_1_row_with_a_diep_has_a_recapture() -> None:
    # Note 3: "Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP". Column 7 is 0 + 10,000 - 12,000 = -2,000: a recapture of 2,000.
    row_10_1 = diep_row(
        "10.1", "0", "10000", "12000", diep_additions="10000", diep_proceeds="10000"
    )
    capability = RecapturedCca(class_rates(), DIEP_CLASSES, RECAPTURED_CCA)

    (output,) = capability.compute((diep_classes(row_10_1),)).outputs

    assert output == Artifact(RECAPTURED_CCA, D("2000"))


def test_a_class_10_1_row_without_a_diep_has_no_recapture_or_terminal_loss() -> None:
    row_10_1 = diep_row("10.1", "0", "10000", "12000")
    last = diep_row("10.1", "0", "4000", no_property_left=1)

    (recapture,) = (
        RecapturedCca(class_rates(), DIEP_CLASSES, RECAPTURED_CCA)
        .compute((diep_classes(row_10_1),))
        .outputs
    )
    (loss,) = (
        TerminalLoss(class_rates(), DIEP_CLASSES, TERMINAL_LOSS)
        .compute((diep_classes(last),))
        .outputs
    )

    assert recapture == Artifact(RECAPTURED_CCA, D("0"))
    assert loss == Artifact(TERMINAL_LOSS, D("0"))


def test_a_class_10_1_row_with_a_diep_and_no_property_left_has_a_terminal_loss() -> None:
    last = diep_row("10.1", "0", "4000", diep_additions="4000", no_property_left=1)

    assert terminal_loss(last) == D("4000")


def test_a_class_10_1_diep_row_has_a_terminal_loss_of_column_7_less_column_9() -> None:
    assert terminal_loss(last_row("10.1", column_7="4000", column_9="1000")) == D("3000")
    assert terminal_loss(last_row("10.1", column_7="4000", column_9="4000")) == D("0")
