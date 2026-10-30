"""Unit tests for the DispositionProceeds capability (`ca/disposition_proceeds`), Schedule 3
(form 5000-S3) Part 3.

Schedule 3, Part 3: "Total proceeds of disposition (add all the amounts under column 2)", column 2
being "Proceeds of disposition" (lines 10699, 10999, 12399, 13199, 13599, 15199, 15200 and 15499;
form text confirmed 2026-10-19).

It totals the same rows as `DispositionGains`, adding column 2 of each. Slots: no parameter slot,
one consumed slot `dispositions` and one produced slot `output`. It records one
`DispositionProceedsLine` per row, by position from 1, then an `ItemsTotalLine`. The total is 0
when there are no rows. Its parent class `DispositionRows` is shared with `DispositionGains`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.disposition_proceeds import DispositionProceeds
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    SHARE_DISPOSITIONS,
    SHARE_PROCEEDS,
)
from tax_engine.jurisdictions.ca.trace import DispositionProceedsLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    Row,
    personal_use,
    shares,
)


def proceeds() -> DispositionProceeds:
    return DispositionProceeds(SHARE_DISPOSITIONS, SHARE_PROCEEDS)


def total(*given: Row) -> Decimal:
    (output,) = proceeds().compute((shares(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_disposition_proceeds() -> None:
    assert CapabilityRegistry.shared().get("ca/disposition_proceeds") is DispositionProceeds


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "disposition_proceeds" in ca_capabilities.__all__
    assert ca_capabilities.disposition_proceeds.DispositionProceeds is DispositionProceeds


def test_declares_its_slots_and_contract() -> None:
    assert dict(DispositionProceeds.PARAMETERS) == {}
    assert DispositionProceeds.CONSUMES == {"dispositions": RecordList}
    assert DispositionProceeds.PRODUCES == {"output": Decimal}
    assert proceeds().consumes == frozenset({SHARE_DISPOSITIONS})
    assert proceeds().produces == frozenset({SHARE_PROCEEDS})
    assert "consumes" not in vars(DispositionProceeds)
    assert issubclass(DispositionProceeds, DispositionRows)


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="DispositionProceeds.*'dispositions'"):
        DispositionProceeds(CAREGIVER_AMOUNT, SHARE_PROCEEDS)  # type: ignore[arg-type]


# --- column 2 and the total --------------------------------------------------------------------


def test_no_rows_give_zero() -> None:
    assert total() == D("0")
    assert type(total()) is Decimal


def test_one_row_adds_its_proceeds() -> None:
    assert total(GAIN) == D("1500.00")


def test_a_loss_row_still_adds_its_proceeds() -> None:
    # Column 2 only: the cost base and the outlays play no part.
    assert total(LOSS) == D("800.00")


def test_the_rows_are_added() -> None:
    assert total(GAIN, LOSS, NOTHING) == D("2800.00")


def test_the_total_does_not_depend_on_the_order() -> None:
    assert total(LOSS, GAIN, NOTHING) == total(GAIN, NOTHING, LOSS)


def test_the_total_is_never_negative() -> None:
    assert not total(LOSS, LOSS).is_signed()


def test_the_figures_are_exact_and_unrounded() -> None:
    odd: Row = ("1.005", "0.001", "0.002")

    assert total(odd, odd) == D("2.010")


# --- inputs ------------------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    assert proceeds().compute((other, shares(GAIN))).outputs == (
        Artifact(SHARE_PROCEEDS, D("1500.00")),
    )


def test_reads_only_the_list_it_is_wired_to() -> None:
    assert proceeds().compute((personal_use(LOSS), shares(GAIN))).outputs == (
        Artifact(SHARE_PROCEEDS, D("1500.00")),
    )
    assert SHARE_DISPOSITIONS is not PERSONAL_USE_PROPERTY_DISPOSITIONS


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="share_dispositions"):
        proceeds().compute(())


def test_compute_is_repeatable() -> None:
    wired = proceeds()
    given = (shares(GAIN, LOSS),)

    assert wired.compute(given) == wired.compute(given)


# --- trace -------------------------------------------------------------------------------------


def proceeds_line(position: int, row: Row) -> DispositionProceedsLine:
    return DispositionProceedsLine(output=SHARE_PROCEEDS, position=position, proceeds=D(row[0]))


def test_traces_one_line_per_row_then_the_total() -> None:
    trace = proceeds().compute((shares(GAIN, LOSS),)).trace

    assert trace == (
        proceeds_line(1, GAIN),
        proceeds_line(2, LOSS),
        ItemsTotalLine(SHARE_PROCEEDS, ((1, D("1500.00")), (2, D("800.00"))), D("2300.00")),
    )


def test_traces_the_callers_order_with_positions_from_one() -> None:
    trace = proceeds().compute((shares(LOSS, GAIN),)).trace

    assert trace[0] == proceeds_line(1, LOSS)
    assert trace[1] == proceeds_line(2, GAIN)


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert proceeds().compute((shares(),)).trace == (ItemsTotalLine(SHARE_PROCEEDS, (), D("0")),)


def test_the_line_amount_is_the_proceeds() -> None:
    (line, _total_line) = proceeds().compute((shares(GAIN),)).trace

    assert isinstance(line, DispositionProceedsLine)
    assert line.amount == D("1500.00")


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = proceeds().compute((shares(GAIN, LOSS, NOTHING),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
