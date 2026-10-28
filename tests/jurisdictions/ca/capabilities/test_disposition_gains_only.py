"""Unit tests for the DispositionGainsOnly capability (`ca/disposition_gains_only`), Schedule 3
(form 5000-S3) Part 3, personal-use property.

Schedule 3, Part 3, Personal-use property: "Line 9 and line 15800: Total gain only (add all the
amounts under column 5)", column 5 being "Gain or loss (column 2 minus columns 3 and 4)". Guide
T4037 p.22: "if you have a capital loss, you usually cannot deduct that loss ... you cannot use
the loss to decrease capital gains on other personal-use property".

It totals the same rows as `DispositionGains` with a row's loss counting 0. Slots: no parameter
slot, one consumed slot `dispositions` and one produced slot `output`. It records one
`DispositionGainOnlyLine` per row, by position from 1, then an `ItemsTotalLine`. The total is 0
when there are no rows. Its parent class `DispositionRows` is shared with `DispositionGains`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.disposition_gains_only import DispositionGainsOnly
from tax_calculator.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_calculator.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    SHARE_DISPOSITIONS,
)
from tax_calculator.jurisdictions.ca.trace import DispositionGainOnlyLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    Row,
    personal_use,
    shares,
)


def gains_only() -> DispositionGainsOnly:
    return DispositionGainsOnly(PERSONAL_USE_PROPERTY_DISPOSITIONS, PERSONAL_USE_PROPERTY_GAIN_ROWS)


def total_only(*given: Row) -> Decimal:
    (output,) = gains_only().compute((personal_use(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_disposition_gains_only() -> None:
    assert CapabilityRegistry.shared().get("ca/disposition_gains_only") is DispositionGainsOnly


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "disposition_gains_only" in ca_capabilities.__all__
    assert ca_capabilities.disposition_gains_only.DispositionGainsOnly is DispositionGainsOnly


def test_declares_its_slots_and_contract() -> None:
    assert dict(DispositionGainsOnly.PARAMETERS) == {}
    assert DispositionGainsOnly.CONSUMES == {"dispositions": RecordList}
    assert DispositionGainsOnly.PRODUCES == {"output": Decimal}
    assert gains_only().consumes == frozenset({PERSONAL_USE_PROPERTY_DISPOSITIONS})
    assert gains_only().produces == frozenset({PERSONAL_USE_PROPERTY_GAIN_ROWS})
    assert "consumes" not in vars(DispositionGainsOnly)
    assert issubclass(DispositionGainsOnly, DispositionRows)


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="DispositionGainsOnly.*'dispositions'"):
        DispositionGainsOnly(CAREGIVER_AMOUNT, PERSONAL_USE_PROPERTY_GAIN_ROWS)  # type: ignore[arg-type]


# --- a loss counts 0 ---------------------------------------------------------------------------


def test_gain_only_no_rows_give_zero() -> None:
    assert total_only() == D("0")


def test_gain_only_a_gain_row_counts_its_gain() -> None:
    assert total_only(GAIN) == D("450.00")


def test_gain_only_a_loss_row_counts_0() -> None:
    # Guide T4037 p.22: the loss on personal-use property cannot decrease the other gains.
    assert total_only(LOSS) == D("0")
    assert not total_only(LOSS).is_signed()


def test_gain_only_a_loss_row_does_not_offset_another_rows_gain() -> None:
    assert total_only(GAIN, LOSS) == D("450.00")
    assert total_only(LOSS, GAIN) == D("450.00")


def test_gain_only_adds_every_gain_row() -> None:
    assert total_only(GAIN, LOSS, GAIN, NOTHING) == D("900.00")


def test_gain_only_is_never_negative() -> None:
    assert not total_only(LOSS, LOSS).is_signed()


# --- inputs ------------------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    assert gains_only().compute((other, personal_use(GAIN))).outputs == (
        Artifact(PERSONAL_USE_PROPERTY_GAIN_ROWS, D("450.00")),
    )


def test_reads_only_the_list_it_is_wired_to() -> None:
    assert gains_only().compute((shares(GAIN), personal_use(LOSS))).outputs == (
        Artifact(PERSONAL_USE_PROPERTY_GAIN_ROWS, D("0")),
    )
    assert SHARE_DISPOSITIONS is not PERSONAL_USE_PROPERTY_DISPOSITIONS


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="personal_use_property_dispositions"):
        gains_only().compute(())


def test_compute_is_repeatable() -> None:
    wired = gains_only()
    given = (personal_use(GAIN, LOSS),)

    assert wired.compute(given) == wired.compute(given)


# --- trace -------------------------------------------------------------------------------------


def only_line(position: int, row: Row, gain: str, result: str) -> DispositionGainOnlyLine:
    proceeds, cost_base, outlays = row
    return DispositionGainOnlyLine(
        output=PERSONAL_USE_PROPERTY_GAIN_ROWS,
        position=position,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        gain=D(gain),
        result=D(result),
    )


def test_traces_the_gain_and_the_figure_counted() -> None:
    trace = gains_only().compute((personal_use(GAIN, LOSS),)).trace

    assert trace == (
        only_line(1, GAIN, "450.00", "450.00"),
        only_line(2, LOSS, "-230.00", "0"),
        ItemsTotalLine(
            PERSONAL_USE_PROPERTY_GAIN_ROWS, ((1, D("450.00")), (2, D("0"))), D("450.00")
        ),
    )


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert gains_only().compute((personal_use(),)).trace == (
        ItemsTotalLine(PERSONAL_USE_PROPERTY_GAIN_ROWS, (), D("0")),
    )


def test_the_counted_figure_of_a_loss_is_not_signed() -> None:
    (line, total_line) = gains_only().compute((personal_use(LOSS),)).trace

    assert isinstance(line, DispositionGainOnlyLine)
    assert line.gain == D("-230.00")
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert line.amount == D("0")
    assert isinstance(total_line, ItemsTotalLine)
    assert not total_line.total.is_signed()


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = gains_only().compute((personal_use(GAIN, LOSS, NOTHING),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
