"""Unit tests for the QffpGains capability (`ca/qffp_gains`), Schedule 3 (form 5000-S3) Part 3,
line 2 "Qualified farm or fishing property (QFFP)".

Each row is a disposition with "(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost
base", "(Column 4): Outlays and expenses" and "(Column 5): Gain or loss (column 2 minus columns 3
and 4)"; line 2 is "Total gain or loss (add all the amounts under column 5)". A row may add some
of the filer's restricted farm loss to its cost base: Guide T4037 p.34 "Reduce your capital gain by
adding these amounts to the adjusted cost base (ACB) of your farmland.", "The amount of RFLs that
you can apply cannot be more than the property taxes and interest on money you borrowed to buy the
farmland that were included in the calculation of the RFLs for each year." and p.36 "You cannot
use it to create or increase a capital loss." Slots: no parameter slot, one consumed slot
`dispositions` and one produced slot `output`. It records one `QffpGainLine` per row, by position
from 1, then an `ItemsTotalLine`. The total is 0 when there are no rows. Its parent class is
`DispositionRows`.
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
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.capabilities.qffp_gains import QffpGains
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    OTHER_FORECLOSURE_DISPOSITIONS,
    OTHER_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_DISPOSITIONS,
    QFFP_GAIN_OR_LOSS,
)
from tax_engine.jurisdictions.ca.trace import QffpGainLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    QffpRow,
    Row,
    qffp,
    shares,
)

# Guide T4037 p.34 Example: farmland sold for 200,000, ACB 160,000, an unapplied restricted farm
# loss of 20,000 of which 5,000 is property taxes and 5,000 is interest: gain 30,000.
FARMLAND: QffpRow = ("200000", "160000", "0", "10000", "5000", "5000")


def wired() -> QffpGains:
    return QffpGains(QFFP_DISPOSITIONS, QFFP_GAIN_OR_LOSS)


def total(*given: Row | QffpRow) -> Decimal:
    (output,) = wired().compute((qffp(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_qffp_gains() -> None:
    assert CapabilityRegistry.shared().get("ca/qffp_gains") is QffpGains


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "qffp_gains" in ca_capabilities.__all__
    assert ca_capabilities.qffp_gains.QffpGains is QffpGains


def test_declares_its_slots_and_contract() -> None:
    assert dict(QffpGains.PARAMETERS) == {}
    assert QffpGains.CONSUMES == {"dispositions": RecordList}
    assert QffpGains.PRODUCES == {"output": Decimal}
    assert wired().consumes == frozenset({QFFP_DISPOSITIONS})
    assert wired().produces == frozenset({QFFP_GAIN_OR_LOSS})
    assert "consumes" not in vars(QffpGains)
    assert issubclass(QffpGains, DispositionRows)


def test_is_built_from_its_slot_names_as_keywords() -> None:
    built = QffpGains(dispositions=QFFP_DISPOSITIONS, output=QFFP_GAIN_OR_LOSS)

    assert built.compute((qffp(GAIN),)).outputs == (Artifact(QFFP_GAIN_OR_LOSS, D("450")),)


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="QffpGains.*'dispositions'"):
        QffpGains(CAREGIVER_AMOUNT, QFFP_GAIN_OR_LOSS)  # type: ignore[arg-type]


# --- rows without a restricted farm loss add as DispositionGains does --------------------------


def test_no_rows_give_zero() -> None:
    (output,) = wired().compute((qffp(),)).outputs

    assert output == Artifact(QFFP_GAIN_OR_LOSS, D("0"))
    assert type(output.value) is Decimal


def test_a_row_without_a_farm_loss_gives_proceeds_less_cost_base_and_outlays() -> None:
    assert total(GAIN) == D("450")


def test_a_loss_offsets_a_gain() -> None:
    assert total(GAIN, LOSS) == D("220")


def test_a_loss_is_signed() -> None:
    assert total(LOSS) == D("-230")
    assert total(LOSS).is_signed()


def test_a_row_with_nothing_gained_or_lost_adds_nothing() -> None:
    assert total(NOTHING) == D("0")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(GAIN, LOSS, FARMLAND) == total(FARMLAND, LOSS, GAIN)


# --- a restricted farm loss applied to farmland -------------------------------------------------


def test_the_farm_loss_applied_is_added_to_the_cost_base_guide_t4037_example() -> None:
    assert total(FARMLAND) == D("30000")


def test_applying_nothing_leaves_the_gain_at_the_typed_cost_base() -> None:
    assert total(("200000", "160000", "0", "10000", "0", "0")) == D("40000")


def test_an_amount_applied_equal_to_the_part_is_allowed() -> None:
    assert total(("200000", "160000", "0", "10000", "5000", "5000")) == D("30000")


def test_an_amount_applied_above_the_taxes_and_interest_part_is_refused_not_capped() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^item 1: ca/disposition_farm_loss_property_taxes plus "
        r"ca/disposition_farm_loss_interest 10000.01 is above the property taxes "
        r"and interest part of the restricted farm loss 10000$",
    ):
        total(("200000", "160000", "0", "10000", "5000", "5000.01"))


def test_an_amount_applied_equal_to_the_gain_brings_the_gain_to_zero() -> None:
    assert total(("170000", "160000", "0", "10000", "5000", "5000")) == D("0")


def test_an_amount_applied_above_the_gain_is_refused_not_capped() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"^item 1: ca/disposition_farm_loss_property_taxes plus "
        r"ca/disposition_farm_loss_interest 10000 is above the gain 9999: a "
        r"restricted farm loss cannot create or increase a capital loss$",
    ):
        total(("169999", "160000", "0", "10000", "5000", "5000"))


def test_the_gain_the_amount_is_bounded_by_is_after_outlays() -> None:
    with pytest.raises(InputAboveBoundError, match="is above the gain 5000"):
        total(("200000", "160000", "35000", "10000", "3000", "3000"))


def test_an_amount_applied_to_a_row_that_is_a_loss_is_refused_with_a_gain_of_0() -> None:
    with pytest.raises(InputAboveBoundError, match="is above the gain 0:"):
        total(("150000", "160000", "0", "10000", "0", "1"))


def test_the_part_bound_is_checked_row_by_row() -> None:
    with pytest.raises(InputAboveBoundError, match="^item 2: "):
        total(FARMLAND, ("200000", "160000", "0", "0", "0", "1"))


# --- Schedule 3 line 8, other mortgage foreclosures and conditional sales repossessions ---------


def test_serves_the_other_foreclosures_list_with_the_same_rows_and_refusals() -> None:
    other = QffpGains(OTHER_FORECLOSURE_DISPOSITIONS, OTHER_FORECLOSURE_GAIN_OR_LOSS)
    rows = Artifact(
        OTHER_FORECLOSURE_DISPOSITIONS,
        RecordList(OTHER_FORECLOSURE_DISPOSITIONS.fields, qffp(FARMLAND).value.records),
    )

    assert other.consumes == frozenset({OTHER_FORECLOSURE_DISPOSITIONS})
    assert other.compute((rows,)).outputs == (Artifact(OTHER_FORECLOSURE_GAIN_OR_LOSS, D("30000")),)
    too_much = qffp(("200000", "160000", "0", "9999", "5000", "5000"))
    with pytest.raises(InputAboveBoundError, match="above the property taxes and interest part"):
        other.compute(
            (
                Artifact(
                    OTHER_FORECLOSURE_DISPOSITIONS,
                    RecordList(OTHER_FORECLOSURE_DISPOSITIONS.fields, too_much.value.records),
                ),
            )
        )


# --- inputs the capability does not consume -----------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    result = wired().compute((shares(GAIN), qffp(GAIN)))

    assert result.outputs == (Artifact(QFFP_GAIN_OR_LOSS, D("450")),)


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError):
        wired().compute(())


def test_compute_is_repeatable() -> None:
    given = (qffp(GAIN, FARMLAND),)

    assert wired().compute(given) == wired().compute(given)


# --- trace ----------------------------------------------------------------------------------


def line(
    position: int, row: Row, result: str, taxes: str = "0", interest: str = "0"
) -> QffpGainLine:
    proceeds, cost_base, outlays = row
    return QffpGainLine(
        output=QFFP_GAIN_OR_LOSS,
        position=position,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        farm_loss_property_taxes=D(taxes),
        farm_loss_interest=D(interest),
        farm_loss_applied=D(taxes) + D(interest),
        result=D(result),
    )


def test_traces_one_line_per_row_then_the_total() -> None:
    trace = wired().compute((qffp(GAIN, FARMLAND, LOSS),)).trace

    assert trace == (
        line(1, GAIN, "450"),
        line(2, ("200000", "160000", "0"), "30000", "5000", "5000"),
        line(3, LOSS, "-230"),
        ItemsTotalLine(
            QFFP_GAIN_OR_LOSS,
            ((1, D("450")), (2, D("30000")), (3, D("-230"))),
            D("30220"),
        ),
    )


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert wired().compute((qffp(),)).trace == (ItemsTotalLine(QFFP_GAIN_OR_LOSS, (), D("0")),)


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = wired().compute((qffp(GAIN, FARMLAND, LOSS),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
