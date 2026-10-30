"""Unit tests for the DepreciablePropertyGains capability (`ca/depreciable_property_gains`),
Schedule 3 (form 5000-S3) Part 3, line 5 "Real estate, depreciable property and other properties".

Each row is a disposition with "(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost
base", "(Column 4): Outlays and expenses" and "(Column 5): Gain or loss (column 2 minus columns 3
and 4)"; line 5 is "Total gain or loss (add all the amounts under column 5)". Form 5000-S3 prints
no line for a loss on depreciable property; Guide T4037 2025 p.19 says (confirmed 2026-10-25 from
the PDF; no .txt published): "A loss from the sale of depreciable property is not considered to be
a capital loss. However, you may be able to claim a terminal loss." Guide T4036 p.44: "You cannot
have a capital loss when you sell depreciable property" (same confirmation).

The filer says so on each row with a 0 or 1 "depreciable property" answer (the fourth field of
`ca/real_estate_dispositions`). A row answered 1 counts its gain not below 0; a row answered 0
counts its signed gain, as `DispositionGains` does. An answer above 1 is an `InputAboveBoundError`
naming the item. Slots: no parameter slot, one consumed slot `dispositions` and one produced slot
`output`. It records one `DepreciablePropertyGainLine` per row, by position from 1, then an
`ItemsTotalLine`. The total is 0 when there are no rows. Its parent class is `DispositionRows`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.depreciable_property_gains import (
    DepreciablePropertyGains,
)
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    REAL_ESTATE_DISPOSITIONS,
    REAL_ESTATE_GAIN_OR_LOSS,
    SHARE_DISPOSITIONS,
)
from tax_engine.jurisdictions.ca.trace import DepreciablePropertyGainLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    FarmLossRow,
    FlaggedRow,
    real_estate,
    shares,
)

# Guide T4037 p.20: a machine bought for $10,000, UCC $6,000, sold alone for $4,000 (A), $8,000 (B)
# or $12,000 (C), as depreciable property (answer 1).
SITUATION_A: FlaggedRow = ("4000", "10000", "0", 1)  # column 5: -6000, counts 0
SITUATION_B: FlaggedRow = ("8000", "10000", "0", 1)  # column 5: -2000, counts 0
SITUATION_C: FlaggedRow = ("12000", "10000", "0", 1)  # column 5: 2000, counts 2000
ORDINARY_LOSS: FlaggedRow = ("9500", "10000", "0", 0)  # column 5: -500, counts -500


def flagged(row: tuple[str, str, str], answer: int) -> FlaggedRow:
    return (*row, answer)


def wired() -> DepreciablePropertyGains:
    return DepreciablePropertyGains(REAL_ESTATE_DISPOSITIONS, REAL_ESTATE_GAIN_OR_LOSS)


def total(*given: FlaggedRow | FarmLossRow) -> Decimal:
    (output,) = wired().compute((real_estate(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_depreciable_property_gains() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/depreciable_property_gains") is DepreciablePropertyGains
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "depreciable_property_gains" in ca_capabilities.__all__
    assert (
        ca_capabilities.depreciable_property_gains.DepreciablePropertyGains
        is DepreciablePropertyGains
    )


def test_declares_its_slots_and_contract() -> None:
    assert dict(DepreciablePropertyGains.PARAMETERS) == {}
    assert DepreciablePropertyGains.CONSUMES == {"dispositions": RecordList}
    assert DepreciablePropertyGains.PRODUCES == {"output": Decimal}
    assert wired().consumes == frozenset({REAL_ESTATE_DISPOSITIONS})
    assert wired().produces == frozenset({REAL_ESTATE_GAIN_OR_LOSS})
    assert "consumes" not in vars(DepreciablePropertyGains)
    assert issubclass(DepreciablePropertyGains, DispositionRows)


def test_is_built_from_its_slot_names_as_keywords() -> None:
    built = DepreciablePropertyGains(
        dispositions=REAL_ESTATE_DISPOSITIONS, output=REAL_ESTATE_GAIN_OR_LOSS
    )

    assert built.compute((real_estate(SITUATION_C),)).outputs == (
        Artifact(REAL_ESTATE_GAIN_OR_LOSS, D("2000")),
    )


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="DepreciablePropertyGains.*'dispositions'"):
        DepreciablePropertyGains(CAREGIVER_AMOUNT, REAL_ESTATE_GAIN_OR_LOSS)  # type: ignore[arg-type]


# --- a loss on depreciable property counts 0 ---------------------------------------------------


def test_no_rows_give_zero() -> None:
    (output,) = wired().compute((real_estate(),)).outputs

    assert output == Artifact(REAL_ESTATE_GAIN_OR_LOSS, D("0"))
    assert type(output.value) is Decimal


def test_a_flagged_loss_row_counts_0_situation_a() -> None:
    # Guide T4037 p.20 A: terminal loss $2,000, no capital gain.
    assert total(SITUATION_A) == D("0")
    assert not total(SITUATION_A).is_signed()


def test_a_flagged_row_sold_below_cost_but_above_ucc_counts_0_situation_b() -> None:
    # Guide T4037 p.20 B: recapture $2,000, no capital gain.
    assert total(SITUATION_B) == D("0")
    assert not total(SITUATION_B).is_signed()


def test_a_flagged_row_sold_above_cost_counts_its_gain_situation_c() -> None:
    # Guide T4037 p.20 C: recapture $4,000 and capital gain $2,000.
    assert total(SITUATION_C) == D("2000")


def test_a_flagged_gain_row_counts_its_gain_less_outlays() -> None:
    assert total(flagged(GAIN, 1)) == D("450.00")


def test_a_flagged_row_with_nothing_gained_or_lost_adds_nothing() -> None:
    assert total(flagged(NOTHING, 1)) == D("0.00")


def test_a_flagged_loss_does_not_offset_another_rows_gain() -> None:
    assert total(flagged(LOSS, 1), flagged(GAIN, 1)) == D("450.00")
    assert total(flagged(GAIN, 1), flagged(LOSS, 1)) == D("450.00")


def test_the_three_situations_together_count_only_the_gain_of_c() -> None:
    assert total(SITUATION_A, SITUATION_B, SITUATION_C) == D("2000")


# --- an ordinary row counts as DispositionGains does -------------------------------------------


def test_an_unflagged_loss_row_counts_its_signed_loss() -> None:
    assert total(flagged(LOSS, 0)) == D("-230.00")
    assert total(flagged(LOSS, 0)).is_signed()


def test_an_unflagged_loss_offsets_a_gain() -> None:
    assert total(flagged(GAIN, 0), flagged(LOSS, 0)) == D("220.00")


def test_unflagged_losses_larger_than_the_gains_give_a_net_loss() -> None:
    assert total(flagged(GAIN, 0), flagged(LOSS, 0), flagged(LOSS, 0)) == D("-10.00")


def test_the_return_it_rows_give_1500() -> None:
    # Situations A, B and C (flag 1) count 0, 0 and 2000; the ordinary property row counts -500.
    # Without the flag the total would be -6000 - 2000 + 2000 - 500 = -6500.
    assert total(SITUATION_A, SITUATION_B, SITUATION_C, ORDINARY_LOSS) == D("1500")


def test_the_figures_are_exact_and_unrounded() -> None:
    assert total(("1.005", "0.001", "0.002", 0)) == D("1.002")
    assert total(("1.005", "0.001", "0.002", 1)) == D("1.002")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(SITUATION_A, ORDINARY_LOSS, SITUATION_C) == total(
        SITUATION_C, SITUATION_A, ORDINARY_LOSS
    )


# --- the answer ---------------------------------------------------------------------------------


@pytest.mark.parametrize("value", [2, 13])
def test_an_answer_above_1_is_refused_not_read_as_depreciable_property(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/disposition_depreciable_property {value} is above a yes or no "
        r"answer of 1$",
    ):
        total(("4000", "10000", "0", value))


@pytest.mark.parametrize("value", [2, 13])
def test_an_answer_above_1_names_its_item_at_position_2(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 2: ca/disposition_depreciable_property {value} is above a yes or no "
        r"answer of 1$",
    ):
        total(SITUATION_C, ("4000", "10000", "0", value))


# --- inputs ------------------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    assert wired().compute((other, real_estate(SITUATION_C))).outputs == (
        Artifact(REAL_ESTATE_GAIN_OR_LOSS, D("2000")),
    )


def test_reads_only_the_list_it_is_wired_to() -> None:
    assert wired().compute((shares(GAIN), real_estate(SITUATION_C))).outputs == (
        Artifact(REAL_ESTATE_GAIN_OR_LOSS, D("2000")),
    )
    assert SHARE_DISPOSITIONS is not REAL_ESTATE_DISPOSITIONS


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="real_estate_dispositions"):
        wired().compute(())


def test_compute_is_repeatable() -> None:
    given = (real_estate(SITUATION_A, SITUATION_C),)

    assert wired().compute(given) == wired().compute(given)


# --- trace -------------------------------------------------------------------------------------


def depreciable_line(
    position: int,
    row: FlaggedRow,
    gain: str,
    result: str,
    taxes: str = "0",
    interest: str = "0",
) -> DepreciablePropertyGainLine:
    proceeds, cost_base, outlays, answer = row
    return DepreciablePropertyGainLine(
        output=REAL_ESTATE_GAIN_OR_LOSS,
        position=position,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        farm_loss_property_taxes=D(taxes),
        farm_loss_interest=D(interest),
        farm_loss_applied=D(taxes) + D(interest),
        depreciable=answer,
        gain=D(gain),
        result=D(result),
    )


def test_traces_one_line_per_row_then_the_total() -> None:
    trace = wired().compute((real_estate(SITUATION_A, SITUATION_C, ORDINARY_LOSS),)).trace

    assert trace == (
        depreciable_line(1, SITUATION_A, "-6000", "0"),
        depreciable_line(2, SITUATION_C, "2000", "2000"),
        depreciable_line(3, ORDINARY_LOSS, "-500", "-500"),
        ItemsTotalLine(
            REAL_ESTATE_GAIN_OR_LOSS,
            ((1, D("0")), (2, D("2000")), (3, D("-500"))),
            D("1500"),
        ),
    )


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert wired().compute((real_estate(),)).trace == (
        ItemsTotalLine(REAL_ESTATE_GAIN_OR_LOSS, (), D("0")),
    )


def test_the_counted_figure_of_a_flagged_loss_is_not_signed() -> None:
    (line, total_line) = wired().compute((real_estate(SITUATION_A),)).trace

    assert isinstance(line, DepreciablePropertyGainLine)
    assert line.gain == D("-6000")
    assert line.depreciable == 1
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert line.amount == D("0")
    assert isinstance(total_line, ItemsTotalLine)
    assert not total_line.total.is_signed()


def test_the_counted_figure_of_an_unflagged_loss_is_the_signed_loss() -> None:
    (line, _) = wired().compute((real_estate(ORDINARY_LOSS),)).trace

    assert isinstance(line, DepreciablePropertyGainLine)
    assert line.depreciable == 0
    assert line.gain == D("-500")
    assert line.result == D("-500")
    assert line.amount == D("-500")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = wired().compute((real_estate(SITUATION_A, SITUATION_C, ORDINARY_LOSS),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value


# --- a restricted farm loss applied to farmland -------------------------------------------------

# Guide T4037 p.34 Example: farmland sold for 200,000, ACB 160,000, an unapplied restricted farm
# loss of 20,000 of which 5,000 is property taxes and 5,000 is interest: gain 30,000.
FARMLAND: FarmLossRow = ("200000", "160000", "0", 0, "10000", "5000", "5000")


def test_the_farm_loss_applied_is_added_to_the_cost_base_guide_t4037_example() -> None:
    assert total(FARMLAND) == D("30000")


def test_applying_nothing_leaves_the_gain_at_the_typed_cost_base() -> None:
    assert total(("200000", "160000", "0", 0, "10000", "0", "0")) == D("40000")


def test_the_farm_loss_applied_is_traced_on_the_row() -> None:
    (line, _) = wired().compute((real_estate(FARMLAND),)).trace

    assert line == depreciable_line(
        1, ("200000", "160000", "0", 0), "30000", "30000", "5000", "5000"
    )


def test_an_amount_applied_equal_to_the_part_is_allowed() -> None:
    assert total(("200000", "160000", "0", 0, "10000", "5000", "5000")) == D("30000")


def test_an_amount_applied_above_the_taxes_and_interest_part_is_refused_not_capped() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^item 1: ca/disposition_farm_loss_property_taxes plus "
        r"ca/disposition_farm_loss_interest 10000.01 is above the property taxes "
        r"and interest part of the restricted farm loss 10000$",
    ):
        total(("200000", "160000", "0", 0, "10000", "5000", "5000.01"))


def test_an_amount_applied_equal_to_the_gain_brings_the_gain_to_zero() -> None:
    assert total(("170000", "160000", "0", 0, "10000", "5000", "5000")) == D("0")


def test_an_amount_applied_above_the_gain_is_refused_not_capped() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^item 1: ca/disposition_farm_loss_property_taxes plus "
        r"ca/disposition_farm_loss_interest 10000 is above the gain 9999: a "
        r"restricted farm loss cannot create or increase a capital loss$",
    ):
        total(("169999", "160000", "0", 0, "10000", "5000", "5000"))


def test_the_gain_the_amount_is_bounded_by_is_after_outlays() -> None:
    with pytest.raises(InputAboveBoundError, match="is above the gain 5000"):
        total(("200000", "160000", "35000", 0, "10000", "3000", "3000"))


def test_an_amount_applied_to_a_row_that_is_a_loss_is_refused_with_a_gain_of_0() -> None:
    with pytest.raises(InputAboveBoundError, match="is above the gain 0:"):
        total(("150000", "160000", "0", 0, "10000", "0", "1"))


def test_the_part_bound_is_checked_row_by_row() -> None:
    with pytest.raises(InputAboveBoundError, match="^item 2: "):
        total(FARMLAND, ("200000", "160000", "0", 0, "0", "0", "1"))
