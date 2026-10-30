"""Unit tests for the DispositionGains capability (`ca/disposition_gains`), Schedule 3 Part 3
(form 5000-S3).

Schedule 3, Part 3: "For each Gain or loss enter as many lines as necessary." Each property type
lists one row per disposition: "(Column 2): Proceeds of disposition", "(Column 3): Adjusted cost
base", "(Column 4): Outlays and expenses", "(Column 5): Gain or loss (column 2 minus columns 3 and
4)". Lines 1 to 8 are each "Total gain or loss (add all the amounts under column 5)"; the listed
personal property rows are added the same way (line 10 takes its "Net gain only" from them).
"Report all negative amounts (losses) using brackets."

It totals the rows' column 5, signed: a loss is a negative figure and offsets the gains of the
other rows. Slots: no parameter slot, one consumed slot `dispositions` (a record list of the
form's columns 2 to 4) and one produced slot `output`. It records one `DispositionGainLine` per
row, by position from 1, then an `ItemsTotalLine`. The total is 0 when there are no rows. It
shares the unregistered parent class `DispositionRows` with `DispositionGainsOnly`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.capability import Capability, CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine, TraceLine
from tax_engine.jurisdictions.ca.capabilities.disposition_gains import DispositionGains
from tax_engine.jurisdictions.ca.capabilities.disposition_gains_only import DispositionGainsOnly
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    LISTED_PERSONAL_PROPERTY_DISPOSITIONS,
    LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS,
    SHARE_DISPOSITIONS,
    SHARE_GAIN_OR_LOSS,
)
from tax_engine.jurisdictions.ca.trace import DispositionGainLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    Row,
    personal_use,
    rows,
    shares,
)


def gains() -> DispositionGains:
    return DispositionGains(SHARE_DISPOSITIONS, SHARE_GAIN_OR_LOSS)


def total(*given: Row) -> Decimal:
    (output,) = gains().compute((shares(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_disposition_gains() -> None:
    assert CapabilityRegistry.shared().get("ca/disposition_gains") is DispositionGains


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "disposition_gains" in ca_capabilities.__all__
    assert ca_capabilities.disposition_gains.DispositionGains is DispositionGains


def test_shares_an_unregistered_parent_class_with_the_gain_only_capability() -> None:
    assert issubclass(DispositionGains, DispositionRows)
    assert issubclass(DispositionGainsOnly, DispositionRows)
    assert issubclass(DispositionRows, Capability)
    assert not issubclass(DispositionGains, DispositionGainsOnly)
    assert not issubclass(DispositionGainsOnly, DispositionGains)
    assert CapabilityRegistry.shared().identifier_of(DispositionRows) is None


def test_declares_its_slots() -> None:
    assert dict(DispositionGains.PARAMETERS) == {}
    assert DispositionGains.CONSUMES == {"dispositions": RecordList}
    assert DispositionGains.PRODUCES == {"output": Decimal}
    assert not DispositionGains.is_list_slot("dispositions")
    for slots in (
        DispositionGains.PARAMETERS,
        DispositionGains.CONSUMES,
        DispositionGains.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(DispositionGains.CONSUMES, Mapping[str, type])
    assert_type(DispositionGains.PRODUCES, Mapping[str, type])


def test_declares_its_contract_from_the_wired_kinds() -> None:
    assert gains().consumes == frozenset({SHARE_DISPOSITIONS})
    assert gains().produces == frozenset({SHARE_GAIN_OR_LOSS})
    assert "consumes" not in vars(DispositionGains)
    assert "produces" not in vars(DispositionGains)


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = DispositionGains(dispositions=SHARE_DISPOSITIONS, output=SHARE_GAIN_OR_LOSS)

    assert wired.compute((shares(GAIN),)).outputs == (Artifact(SHARE_GAIN_OR_LOSS, D("450.00")),)


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="DispositionGains.*'dispositions'"):
        DispositionGains(CAREGIVER_AMOUNT, SHARE_GAIN_OR_LOSS)  # type: ignore[arg-type]


def test_one_wiring_serves_every_property_type() -> None:
    wired = DispositionGains(
        LISTED_PERSONAL_PROPERTY_DISPOSITIONS, LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS
    )
    given = rows(LISTED_PERSONAL_PROPERTY_DISPOSITIONS, GAIN, LOSS)

    (output,) = wired.compute((given,)).outputs

    assert output == Artifact(LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS, D("220.00"))


# --- column 5 and the total --------------------------------------------------------------------


def test_no_rows_give_zero() -> None:
    (output,) = gains().compute((shares(),)).outputs

    assert output == Artifact(SHARE_GAIN_OR_LOSS, D("0"))
    assert type(output.value) is Decimal


def test_one_gain_row_is_proceeds_less_cost_base_and_outlays() -> None:
    # Column 5 = column 2 minus columns 3 and 4: 1500.00 - 1000.00 - 50.00.
    assert total(GAIN) == D("450.00")


def test_a_loss_row_is_a_negative_figure() -> None:
    assert total(LOSS) == D("-230.00")
    assert total(LOSS).is_signed()


def test_the_rows_are_added_and_a_loss_offsets_a_gain() -> None:
    assert total(GAIN, LOSS) == D("220.00")
    assert total(GAIN, GAIN) == D("900.00")


def test_losses_larger_than_the_gains_give_a_net_loss() -> None:
    # A net capital loss is reported in brackets: taxable capital gains are 0 further on.
    assert total(GAIN, LOSS, LOSS) == D("-10.00")


def test_a_row_with_proceeds_equal_to_the_cost_base_and_outlays_adds_nothing() -> None:
    assert total(NOTHING) == D("0.00")
    assert total(GAIN, NOTHING) == D("450.00")


def test_the_outlays_reduce_the_gain() -> None:
    without: Row = ("1500.00", "1000.00", "0.00")

    assert total(without) - total(GAIN) == D("50.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(LOSS, GAIN, NOTHING) == total(GAIN, NOTHING, LOSS)


def test_the_figures_are_exact_and_unrounded() -> None:
    odd: Row = ("1.005", "0.001", "0.002")

    assert total(odd) == D("1.002")


# --- inputs ------------------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    assert gains().compute((other, shares(GAIN))).outputs == (
        Artifact(SHARE_GAIN_OR_LOSS, D("450.00")),
    )


def test_reads_only_the_list_it_is_wired_to() -> None:
    other_list = personal_use(LOSS)

    assert gains().compute((other_list, shares(GAIN))).outputs == (
        Artifact(SHARE_GAIN_OR_LOSS, D("450.00")),
    )


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="share_dispositions"):
        gains().compute(())


def test_has_one_output_of_the_output_kind() -> None:
    (output,) = gains().compute((shares(GAIN, LOSS),)).outputs

    assert output.kind is SHARE_GAIN_OR_LOSS
    assert type(output.value) is Decimal


def test_compute_is_repeatable() -> None:
    wired = gains()
    given = (shares(GAIN, LOSS),)

    assert wired.compute(given) == wired.compute(given)


# --- trace -------------------------------------------------------------------------------------


def gain_line(position: int, row: Row, result: str) -> DispositionGainLine:
    proceeds, cost_base, outlays = row
    return DispositionGainLine(
        output=SHARE_GAIN_OR_LOSS,
        position=position,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        result=D(result),
    )


def test_traces_one_line_per_row_then_the_total() -> None:
    trace = gains().compute((shares(GAIN, LOSS),)).trace

    assert trace == (
        gain_line(1, GAIN, "450.00"),
        gain_line(2, LOSS, "-230.00"),
        ItemsTotalLine(SHARE_GAIN_OR_LOSS, ((1, D("450.00")), (2, D("-230.00"))), D("220.00")),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = gains().compute((shares(LOSS, GAIN),)).trace

    assert [line.position for line in trace[:-1] if isinstance(line, DispositionGainLine)] == [1, 2]
    assert trace[0] == gain_line(1, LOSS, "-230.00")


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert gains().compute((shares(),)).trace == (ItemsTotalLine(SHARE_GAIN_OR_LOSS, (), D("0")),)


def test_the_line_keeps_the_signed_gain_of_a_loss() -> None:
    (line, _) = gains().compute((shares(LOSS),)).trace

    assert isinstance(line, DispositionGainLine)
    assert line.result == D("-230.00")
    assert line.amount == D("-230.00")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = gains().compute((shares(GAIN, LOSS),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value


def test_the_total_is_the_sum_of_its_items() -> None:
    *_, total_line = gains().compute((shares(GAIN, LOSS, NOTHING),)).trace

    assert isinstance(total_line, ItemsTotalLine)
    assert total_line.total == sum((amount for _, amount in total_line.items), D("0"))


# --- the hook a subclass overrides -------------------------------------------------------------


class Recording(DispositionRows):
    """A parent subclass that records what its `_row` is given."""

    def __init__(self, dispositions: ArtifactKind[RecordList], output: Money) -> None:
        super().__init__(dispositions, output)
        self.seen: list[tuple[int, Decimal, Decimal, Decimal]] = []

    def _row(
        self, position: int, proceeds: Decimal, cost_base: Decimal, outlays: Decimal
    ) -> tuple[TraceLine, Decimal]:
        self.seen.append((position, proceeds, cost_base, outlays))
        return ItemsTotalLine(SHARE_GAIN_OR_LOSS, (), D("0")), D("1")


def test_the_record_row_hook_reads_the_three_figures_and_calls_row() -> None:
    (record,) = shares(GAIN).value.records
    parent = Recording(SHARE_DISPOSITIONS, SHARE_GAIN_OR_LOSS)

    line, added = parent._record_row(3, record)

    assert parent.seen == [(3, D("1500.00"), D("1000.00"), D("50.00"))]
    assert line == ItemsTotalLine(SHARE_GAIN_OR_LOSS, (), D("0"))
    assert added == D("1")


def test_compute_goes_through_the_record_row_hook() -> None:
    parent = Recording(SHARE_DISPOSITIONS, SHARE_GAIN_OR_LOSS)

    parent.compute((shares(GAIN, LOSS),))

    assert parent.seen == [
        (1, D("1500.00"), D("1000.00"), D("50.00")),
        (2, D("800.00"), D("1000.00"), D("30.00")),
    ]
