"""Unit tests for the half-year rule that differs from a class's own, T776 and T2125 Area A column
18, through the CCA table (`CcaTable`).

Guide T4002 2025, "Column 18": "as well as most of those in Class 12, such as small tools" and
"Class 12 tools that are subject to the half-year rule include dies, jigs, patterns, moulds, and
lasts, as well as the cutting or shaping part of a machine."

Column 18 is one half of column 10 minus columns 11, 12 and 5, or 0 for a class exempt from the
half-year rule, each "If negative, enter "0"", rounded once with the dataset's rule. The caller's
row `ca/cca_half_year_rule_differs` (1 when the row's additions are treated the opposite way from
its class) turns the class's treatment over: an exempt class (Class 12) is then subject, and a
subject class (Class 8) is then exempt. 0 and an absent field (a list kind that does not list it)
leave the class's own treatment. A value above 1 is refused, as `ca/yes_or_no_count` refuses one
(`InputAboveBoundError`, "item N: ca/cca_half_year_rule_differs 2 is above a yes or no answer
of 1").
Column 19 is column 13 plus columns 15 and 17 minus column 18, so the flag reaches the maximum in
every capability that works the rows: the claim, the closing UCC, the claims and closing UCCs after
column 22 and the prorated ones. The terminal loss is column 7 alone and does not change. The
Class 10.1 half-year rule on sale is a separate mechanism (column 19), unaffected by the flag.

Worked rows, by hand:
K, Class 12 (100%) flagged: column 2 0, column 3 1,000. Column 7 1,000; column 13 1,000; column 18
one half of 1,000 = 500 (the class is exempt, so the flag makes it subject); column 19 500; maximum
100% of 500 = 500.00. Unflagged, column 18 0, column 19 1,000, maximum 1,000.00.
K2, the same row with the flag 2: refused, since a value above 1 is not a yes or no answer.
E, Class 8 (20%) flagged: column 2 10,000, column 3 3,000. Column 7 13,000; column 18 0 (the class
is subject, so the flag makes it exempt); column 19 13,000; maximum 2,600.00. Unflagged, column 18
1,500, column 19 11,500, maximum 2,300.00.
M, Class 12 flagged, odd cents: column 3 1,000.01. Column 18 one half of 1,000.01 = 500.005, rounded
half up to 500.01; column 19 1,000.01 - 500.01 = 500.00; maximum 500.00.
N, Class 12 flagged, netted: column 3 1,000, column 5 200, column 11 100, column 12 100. Column
7 800; column 10 1,000; column 14 0; columns 15 and 17 0 (the factors of Class 12 are 0); column
16 0; column 18 one half of 1,000 - 100 - 100 - 200 = 300; column 19 800 - 300 = 500; maximum
500.00.
Z, Class 12 flagged, negative net additions: column 2 10,000, column 3 1,000, column 5 3,000.
Column 7 8,000; column 18 one half of 1,000 - 3,000 < 0, so 0; column 19 8,000; maximum 8,000.00.
P, Class 12 flagged, prorated over 214 days: K's column 19 500 times 100% times 214 / 365 =
293.1506..., so 293.15; the flag does not change the proration, which is worked on column 19.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_after_column_22_prorated import (
    CcaClaimAfterColumn22Prorated,
)
from tax_calculator.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
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
    CCA_HALF_YEAR_RULE_DIFFERS,
    CCA_UCC_AT_END,
)
from tax_calculator.jurisdictions.ca.trace import CcaClaimLine, CcaZeroReason
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CENT,
    CLASS_12,
    CLASSES,
    CLOSING_UCC,
    NON_COMPLIANT,
    TERMINAL_LOSS,
    class_rates,
    classes,
    non_compliant_cca,
    row,
)
from tests.jurisdictions.ca.capabilities.cca_table_half_year_differs import (
    HALF_YEAR_CLASSES,
    half_year_classes,
    half_year_row,
)
from tests.jurisdictions.ca.capabilities.cca_table_sale import sale_class_rates

D = Decimal

FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)

Row = dict[Any, Decimal | int]

# Row K: Class 12 flagged, additions 1,000.
K = half_year_row("12", additions="1000", differs=1)
# Row K with no flag.
K_PLAIN = half_year_row("12", additions="1000", differs=0)
# Row E: Class 8 flagged, column 2 10,000 and additions 3,000; and the same unflagged.
E = half_year_row("8", "10000", "3000", differs=1)
E_PLAIN = half_year_row("8", "10000", "3000", differs=0)
# Row M: Class 12 flagged, additions 1,000.01.
M = half_year_row("12", additions="1000.01", differs=1)
# Row N: Class 12 flagged, netted against proceeds and the AIIP and RIIP additions.
N = half_year_row(
    "12", additions="1000", proceeds="200", aiip_additions="100", riip_additions="100", differs=1
)
# Row Z: Class 12 flagged, negative net additions.
Z = half_year_row("12", "10000", "1000", proceeds="3000", differs=1)
# Row TL: Class 12 flagged, a terminal loss of column 7 (600) with no property left.
TL = half_year_row("12", "1000", proceeds="400", no_property_left=1, differs=1)


def with_claim(base: Row, claimed: str) -> Row:
    """`base` with the claim `claimed` (column 23)."""
    return {**base, CCA_CLAIMED: D(claimed)}


def claim_trace(*rows: Row) -> tuple[Any, ...]:
    return (
        CcaClaim(class_rates(), HALF_YEAR_CLASSES, CCA_CLAIM)
        .compute((half_year_classes(*rows),))
        .trace
    )


def claim_total(*rows: Row) -> Decimal:
    (output,) = (
        CcaClaim(class_rates(), HALF_YEAR_CLASSES, CCA_CLAIM)
        .compute((half_year_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, Decimal)
    return output.value


def claim_after_column_22(column_22: Artifact[Any], *rows: Row) -> Decimal:
    capability = CcaClaimAfterColumn22(class_rates(), HALF_YEAR_CLASSES, NON_COMPLIANT, CCA_CLAIM)
    (output,) = capability.compute((column_22, half_year_classes(*rows))).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def claim_prorated(count: int, *rows: Row) -> Decimal:
    capability = CcaClaimProrated(
        class_rates(), HALF_YEAR_CLASSES, fiscal_period_days=FISCAL_PERIOD_DAYS, output=CCA_CLAIM
    )
    (output,) = capability.compute((half_year_classes(*rows), days(count))).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def claim_prorated_after_column_22(count: int, column_22: Artifact[Any], *rows: Row) -> Decimal:
    capability = CcaClaimAfterColumn22Prorated(
        class_rates(),
        HALF_YEAR_CLASSES,
        non_compliant=NON_COMPLIANT,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CCA_CLAIM,
    )
    (output,) = capability.compute((half_year_classes(*rows), days(count), column_22)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def figures(value: RecordList) -> list[tuple[Decimal | int, Decimal | int]]:
    return [(record[CCA_CLASS_NUMBER], record[CCA_UCC_AT_END]) for record in value.records]


def closing(*rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    (output,) = (
        ClosingUcc(class_rates(), HALF_YEAR_CLASSES, CLOSING_UCC)
        .compute((half_year_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_after_column_22(
    column_22: Artifact[Any], *rows: Row
) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccAfterColumn22(
        class_rates(), HALF_YEAR_CLASSES, NON_COMPLIANT, CLOSING_UCC
    )
    (output,) = capability.compute((column_22, half_year_classes(*rows))).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_prorated(count: int, *rows: Row) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccProrated(
        class_rates(),
        HALF_YEAR_CLASSES,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CLOSING_UCC,
    )
    (output,) = capability.compute((half_year_classes(*rows), days(count))).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def closing_prorated_after_column_22(
    count: int, column_22: Artifact[Any], *rows: Row
) -> list[tuple[Decimal | int, Decimal | int]]:
    capability = ClosingUccAfterColumn22Prorated(
        class_rates(),
        HALF_YEAR_CLASSES,
        non_compliant=NON_COMPLIANT,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=CLOSING_UCC,
    )
    (output,) = capability.compute((half_year_classes(*rows), days(count), column_22)).outputs
    assert isinstance(output.value, RecordList)
    return figures(output.value)


def terminal_loss(*rows: Row) -> Decimal:
    (output,) = (
        TerminalLoss(class_rates(), HALF_YEAR_CLASSES, TERMINAL_LOSS)
        .compute((half_year_classes(*rows),))
        .outputs
    )
    assert isinstance(output.value, Decimal)
    return output.value


def days(count: int) -> Artifact[Any]:
    return Artifact(FISCAL_PERIOD_DAYS, count)


def column_22_of(*amounts: tuple[str, str]) -> Artifact[Any]:
    return non_compliant_cca(*amounts)


def line_of(trace: tuple[Any, ...]) -> CcaClaimLine:
    """The one claim line of a trace of one row, before its total."""
    (line, _total) = trace
    assert isinstance(line, CcaClaimLine)
    return line


# --- column 18 of a class exempt from the half-year rule -------------------------------------


def test_a_flagged_class_12_row_takes_one_half_of_its_additions_as_column_18() -> None:
    # Row K: column 18 500, column 19 500, maximum 500.00, the claim 500 of column 9 0.
    assert claim_trace(with_claim(K, "500")) == (
        CcaClaimLine(
            output=CCA_CLAIM,
            position=1,
            class_rate=CLASS_12,
            no_property_left=0,
            column_7=D("1000"),
            column_14=D("0"),
            column_15=D("0"),
            column_16=D("0"),
            column_17=D("0"),
            column_18=D("500"),
            column_19=D("500"),
            zero_reason=CcaZeroReason.NONE,
            maximum=D("500"),
            rounding=CENT,
            claim=D("500"),
            column_9=D("0"),
        ),
        ItemsTotalLine(CCA_CLAIM, ((1, D("500")),), D("500")),
    )


def test_the_claim_of_a_flagged_class_12_row_is_at_most_the_half() -> None:
    assert claim_total(with_claim(K, "500")) == D("500")
    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 500.01 is above the"):
        claim_total(with_claim(K, "500.01"))


def test_a_flagged_class_12_row_is_not_allowed_its_unflagged_maximum() -> None:
    # Unflagged, Class 12 is exempt and its maximum is 1,000; flagged it is 500.
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 500"):
        claim_total(with_claim(K, "1000"))


def test_a_flag_of_0_leaves_class_12_exempt() -> None:
    assert line_of(claim_trace(with_claim(K_PLAIN, "1000"))).column_18 == D("0")
    assert claim_total(with_claim(K_PLAIN, "1000")) == D("1000")


def test_an_absent_flag_leaves_class_12_exempt() -> None:
    # `ex/cca_classes` does not list the field: the row is worked as its class's own treatment.
    plain = CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute(
        (classes(row("12", additions="1000", claimed="1000")),)
    )
    (output,) = plain.outputs

    assert line_of(plain.trace).column_18 == D("0")
    assert output.value == D("1000")


@pytest.mark.parametrize("value", [2, 13])
def test_a_flag_above_1_is_refused_by_the_claim(value: int) -> None:
    # Not read as 1: a value above 1 is refused, as `ca/yes_or_no_count` refuses one.
    flagged = half_year_row("12", additions="1000", differs=value)

    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_half_year_rule_differs {value} is above a yes or no answer of 1$",
    ):
        claim_trace(with_claim(flagged, "500"))


def test_a_flag_above_1_names_its_item_at_position_2() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^item 2: ca/cca_half_year_rule_differs 2 is above a yes or no answer of 1$",
    ):
        claim_trace(with_claim(K, "500"), half_year_row("8", "10000", "3000", differs=2))


@pytest.mark.parametrize("value", [2, 13])
def test_a_flag_above_1_is_refused_by_the_closing_ucc(value: int) -> None:
    flagged = half_year_row("12", additions="1000", differs=value)

    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_half_year_rule_differs {value} is above a yes or no answer of 1$",
    ):
        closing(flagged)


@pytest.mark.parametrize("value", [2, 13])
def test_a_flag_above_1_is_refused_by_the_terminal_loss(value: int) -> None:
    flagged = half_year_row("12", "1000", proceeds="400", no_property_left=1, differs=value)

    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_half_year_rule_differs {value} is above a yes or no answer of 1$",
    ):
        terminal_loss(flagged)


def test_column_18_of_odd_cents_is_rounded_half_up_to_the_cent() -> None:
    # Row M: one half of 1,000.01 is 500.005, which rounds half up to 500.01; column 19 is 500.00.
    line = line_of(claim_trace(with_claim(M, "500")))

    assert line.column_18 == D("500.01")
    assert line.column_19 == D("500.00")
    assert line.maximum == D("500.00")
    assert claim_total(with_claim(M, "500")) == D("500")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 500"):
        claim_total(with_claim(M, "500.01"))


def test_column_18_nets_proceeds_and_the_aiip_and_riip_additions_as_column_18_does() -> None:
    # Row N: net additions 1,000 - 100 - 100 - 200 = 600, one half 300; column 7 800, column 19
    # 800 - 300 = 500, maximum 500.
    line = line_of(claim_trace(with_claim(N, "500")))

    assert line.column_7 == D("800")
    assert (line.column_14, line.column_16) == (D("0"), D("0"))
    assert (line.column_15, line.column_17) == (D("0"), D("0"))
    assert line.column_18 == D("300")
    assert line.column_19 == D("500")
    assert line.maximum == D("500")


def test_negative_net_additions_give_column_18_of_0() -> None:
    # Row Z: net additions 1,000 - 3,000 are below 0, so column 18 is 0 and column 19 is column 7.
    line = line_of(claim_trace(with_claim(Z, "8000")))

    assert line.column_18 == D("0")
    assert line.column_19 == D("8000")
    assert line.maximum == D("8000")
    assert claim_total(with_claim(Z, "8000")) == D("8000")


# --- column 18 of a class subject to the half-year rule --------------------------------------


def test_a_flagged_class_8_row_is_exempt_and_takes_its_full_maximum() -> None:
    # Row E: column 18 0, column 19 13,000, maximum 20% of 13,000 = 2,600.00.
    line = line_of(claim_trace(with_claim(E, "2600")))

    assert line.column_18 == D("0")
    assert line.column_19 == D("13000")
    assert line.maximum == D("2600.00")
    assert claim_total(with_claim(E, "2600")) == D("2600")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2600"):
        claim_total(with_claim(E, "2600.01"))


def test_an_unflagged_class_8_row_keeps_one_half_of_its_additions() -> None:
    # Row E unflagged: column 18 1,500, column 19 11,500, maximum 2,300.00.
    line = line_of(claim_trace(with_claim(E_PLAIN, "2300")))

    assert line.column_18 == D("1500")
    assert line.column_19 == D("11500")
    assert line.maximum == D("2300.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2300"):
        claim_total(with_claim(E_PLAIN, "2600"))


# --- rows without additions, and rows on their own -------------------------------------------


@pytest.mark.parametrize(("number", "claimed"), [("8", "800"), ("12", "4000")])
def test_the_flag_on_a_row_with_no_additions_changes_nothing(number: str, claimed: str) -> None:
    # No additions and a proceeds of 1,000: the net additions are below 0 whichever way the class
    # is treated, so column 18 is 0 and the claim and its trace are the same.
    flagged = half_year_row(number, "5000", proceeds="1000", claimed=claimed, differs=1)
    plain = half_year_row(number, "5000", proceeds="1000", claimed=claimed, differs=0)

    assert claim_trace(flagged) == claim_trace(plain)
    assert line_of(claim_trace(flagged)).column_18 == D("0")


def test_each_row_takes_its_own_flag() -> None:
    # K with the flag and K_PLAIN without, in the same list: 500 and 1,000.
    assert claim_total(with_claim(K, "500"), with_claim(K_PLAIN, "1000")) == D("1500")
    with pytest.raises(InputAboveBoundError, match=r"item 1: ca/cca_claimed 1000 is above"):
        claim_total(with_claim(K, "1000"), with_claim(K_PLAIN, "1000"))


# --- the flag reaches every capability that works the rows -----------------------------------


def test_the_flag_reaches_the_claim_after_column_22() -> None:
    # Maximum 500 less column 22 100: 400.
    assert claim_after_column_22(column_22_of(("12", "100")), with_claim(K, "400")) == D("400")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 400"):
        claim_after_column_22(column_22_of(("12", "100")), with_claim(K, "400.01"))


def test_the_flag_reaches_the_prorated_claim() -> None:
    # Column 19 500 times 214 / 365 = 293.15 (rounded once); the flag does not prorate column 19.
    assert claim_prorated(214, with_claim(K, "293.15")) == D("293.15")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 293.15"):
        claim_prorated(214, with_claim(K, "293.16"))


def test_the_flag_reaches_the_prorated_claim_after_column_22() -> None:
    # 293.15 less column 22 100: 193.15.
    column = column_22_of(("12", "100"))

    assert claim_prorated_after_column_22(214, column, with_claim(K, "193.15")) == D("193.15")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 193.15"):
        claim_prorated_after_column_22(214, column, with_claim(K, "193.16"))


def test_the_flag_reaches_the_closing_ucc() -> None:
    # Column 7 1,000 less the claim 500; and a flagged Class 8 at its maximum 2,600 of 13,000.
    assert closing(with_claim(K, "500")) == [(D("12"), D("500"))]
    assert closing(with_claim(E, "2600")) == [(D("8"), D("10400"))]
    with pytest.raises(InputAboveBoundError):
        closing(with_claim(K, "500.01"))


def test_the_flag_reaches_the_closing_ucc_after_column_22() -> None:
    assert closing_after_column_22(column_22_of(("12", "100")), with_claim(K, "400")) == [
        (D("12"), D("600"))
    ]
    with pytest.raises(InputAboveBoundError):
        closing_after_column_22(column_22_of(("12", "100")), with_claim(K, "400.01"))


def test_the_flag_reaches_the_prorated_closing_ucc() -> None:
    # 1,000 less 293.15.
    assert closing_prorated(214, with_claim(K, "293.15")) == [(D("12"), D("706.85"))]
    with pytest.raises(InputAboveBoundError):
        closing_prorated(214, with_claim(K, "293.16"))


def test_the_flag_reaches_the_prorated_closing_ucc_after_column_22() -> None:
    # 1,000 less 193.15.
    assert closing_prorated_after_column_22(
        214, column_22_of(("12", "100")), with_claim(K, "193.15")
    ) == [(D("12"), D("806.85"))]
    with pytest.raises(InputAboveBoundError):
        closing_prorated_after_column_22(214, column_22_of(("12", "100")), with_claim(K, "193.16"))


def test_the_flag_does_not_change_a_terminal_loss_of_column_7() -> None:
    # Row TL: column 7 600 with no property left is the terminal loss, flagged or not.
    plain = half_year_row("12", "1000", proceeds="400", no_property_left=1, differs=0)

    assert terminal_loss(TL) == D("600")
    assert terminal_loss(TL) == terminal_loss(plain)


# --- the Class 10.1 half-year rule on sale is unaffected -------------------------------------


def test_the_flag_does_not_change_the_half_year_rule_on_sale() -> None:
    # Class 10.1 with the rule on sale: column 19 is one half of column 2, 5,000, and the flag
    # changes neither column 19 nor the maximum, 30% of 5,000 (1,500).
    flagged = half_year_row("10.1", "10000", proceeds="9990", no_property_left=1, differs=1)
    plain = half_year_row("10.1", "10000", proceeds="9990", no_property_left=1, differs=0)
    capability = CcaClaim(sale_class_rates(), HALF_YEAR_CLASSES, CCA_CLAIM)

    flagged_trace = capability.compute((half_year_classes(with_claim(flagged, "10")),)).trace
    plain_trace = capability.compute((half_year_classes(with_claim(plain, "10")),)).trace

    assert flagged_trace == plain_trace
    assert line_of(flagged_trace).column_19 == D("5000")
    assert line_of(flagged_trace).maximum == D("1500")


# --- the wiring ------------------------------------------------------------------------------


def test_the_flag_is_the_last_field_of_the_half_year_list() -> None:
    assert HALF_YEAR_CLASSES.fields[-1] is CCA_HALF_YEAR_RULE_DIFFERS
    assert CCA_HALF_YEAR_RULE_DIFFERS.value_type is int
