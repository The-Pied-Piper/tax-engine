"""Unit tests for the PersonalUsePropertyGains capability (`ca/personal_use_property_gains`),
Schedule 3 (form 5000-S3) Part 3, personal-use property, with the $1,000 minimum of Guide T4037.

Guide T4037 2025, p.24, the "Personal-use property" example, prints "Proceeds of disposition
(whichever is more: selling price or $1,000)" and "Minus: ACB (whichever is more: cost or $1,000)
plus outlays and expenses". So each row's proceeds and adjusted cost base are raised to the
`minimum` dataset's amount when they are lower, and the outlays are not. The row's gain is the
proceeds used less the cost base used less the outlays, and a loss counts 0, as in
`DispositionGainsOnly` (Guide T4037 p.22: "you cannot use the loss to decrease capital gains on
other personal-use property").

Slots: one parameter slot `minimum` (an `amount` dataset, 1,000), one consumed slot `dispositions`
and one produced slot `output`. It records one `PersonalUsePropertyGainLine` per row, by position
from 1, then an `ItemsTotalLine`. The total is 0 when there are no rows.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.disposition_rows import DispositionRows
from tax_engine.jurisdictions.ca.capabilities.personal_use_property_gains import (
    PersonalUsePropertyGains,
)
from tax_engine.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    SHARE_DISPOSITIONS,
)
from tax_engine.jurisdictions.ca.trace import PersonalUsePropertyGainLine
from tests.jurisdictions.ca.capabilities.disposition_rows import (
    GAIN,
    LOSS,
    NOTHING,
    D,
    Row,
    personal_use,
    shares,
)

T4037_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4037/t4037-25e.pdf"

# The Guide T4037 example, p.24 (the figures as printed): China cabinet, boat, personal computer.
CHINA_CABINET: Row = ("900.00", "500.00", "0.00")  # gain 0 once both floors apply
BOAT: Row = ("1200.00", "850.00", "50.00")  # cost floored to 1,000: gain 150
PERSONAL_COMPUTER: Row = ("1500.00", "3200.00", "30.00")  # a loss, counts 0


def minimum_of(value: str = "1000") -> ParameterDataset[Amount]:
    """The `ca/personal_use_property_minimum` dataset: 1,000 by default, not rounded."""
    return ParameterDataset(
        "ca/personal_use_property_minimum",
        2025,
        AMOUNT,
        Amount(D(value)),
        NO_ROUNDING,
        (T4037_PDF,),
    )


def gains(minimum: ParameterDataset[Amount] | None = None) -> PersonalUsePropertyGains:
    return PersonalUsePropertyGains(
        minimum or minimum_of(),
        PERSONAL_USE_PROPERTY_DISPOSITIONS,
        PERSONAL_USE_PROPERTY_GAIN_ROWS,
    )


def total_only(*given: Row) -> Decimal:
    (output,) = gains().compute((personal_use(*given),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


# --- registration and contract -----------------------------------------------------------------


def test_is_registered_as_ca_personal_use_property_gains() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/personal_use_property_gains")
        is PersonalUsePropertyGains
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "personal_use_property_gains" in ca_capabilities.__all__
    assert (
        ca_capabilities.personal_use_property_gains.PersonalUsePropertyGains
        is PersonalUsePropertyGains
    )


def test_declares_its_slots_and_contract() -> None:
    assert dict(PersonalUsePropertyGains.PARAMETERS) == {"minimum": AMOUNT}
    assert PersonalUsePropertyGains.CONSUMES == {"dispositions": RecordList}
    assert PersonalUsePropertyGains.PRODUCES == {"output": Decimal}
    assert gains().consumes == frozenset({PERSONAL_USE_PROPERTY_DISPOSITIONS})
    assert gains().produces == frozenset({PERSONAL_USE_PROPERTY_GAIN_ROWS})
    assert "consumes" not in vars(PersonalUsePropertyGains)
    assert issubclass(PersonalUsePropertyGains, DispositionRows)


def test_rejects_a_money_kind_for_its_dispositions() -> None:
    with pytest.raises(InvalidCapabilityError, match="PersonalUsePropertyGains.*'dispositions'"):
        PersonalUsePropertyGains(
            minimum_of(),
            CAREGIVER_AMOUNT,  # type: ignore[arg-type]
            PERSONAL_USE_PROPERTY_GAIN_ROWS,
        )


# --- the $1,000 minimum on each row ------------------------------------------------------------


def test_no_rows_give_zero() -> None:
    assert total_only() == D("0")


def test_a_row_above_the_minimum_on_both_sides_counts_its_gain() -> None:
    assert total_only(GAIN) == D("450.00")


def test_the_guide_china_cabinet_row_gives_0() -> None:
    # Guide T4037 p.24: proceeds 900 and ACB 500 are both less than $1,000, so 1,000 - 1,000 = 0.
    assert total_only(CHINA_CABINET) == D("0")


def test_the_guide_boat_row_gives_150() -> None:
    # Guide T4037 p.24: the ACB 850 is less than $1,000, so it is 1,000: 1,200 - 1,000 - 50 = 150.
    assert total_only(BOAT) == D("150.00")


def test_a_cost_of_850_with_outlays_of_50_gives_150_on_its_own() -> None:
    assert total_only(("1200.00", "850.00", "50.00")) == D("150.00")


def test_the_guide_personal_computer_loss_counts_0() -> None:
    # Guide T4037 p.24: "Your capital loss is not deductible." 1,500 - 3,200 - 30 is a loss.
    assert total_only(PERSONAL_COMPUTER) == D("0")


def test_the_guide_example_totals_150() -> None:
    assert total_only(CHINA_CABINET, BOAT, PERSONAL_COMPUTER) == D("150.00")


def test_a_loss_row_does_not_offset_another_rows_gain() -> None:
    assert total_only(GAIN, LOSS) == D("450.00")
    assert total_only(LOSS, GAIN) == D("450.00")


def test_adds_every_gain_row() -> None:
    assert total_only(GAIN, LOSS, GAIN, NOTHING) == D("900.00")


def test_is_never_negative() -> None:
    assert not total_only(LOSS, LOSS).is_signed()


def test_the_minimum_is_the_dataset_amount_not_a_constant() -> None:
    # With a $2,000 minimum the boat's cost and proceeds both floor to 2,000: 2,000 - 2,000 - 50.
    wired = gains(minimum_of("2000"))
    (output,) = wired.compute((personal_use(BOAT),)).outputs

    assert output.value == D("0")


# --- inputs ------------------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(CAREGIVER_AMOUNT, D("9"))

    assert gains().compute((other, personal_use(GAIN))).outputs == (
        Artifact(PERSONAL_USE_PROPERTY_GAIN_ROWS, D("450.00")),
    )


def test_reads_only_the_list_it_is_wired_to() -> None:
    assert gains().compute((shares(GAIN), personal_use(LOSS))).outputs == (
        Artifact(PERSONAL_USE_PROPERTY_GAIN_ROWS, D("0")),
    )
    assert SHARE_DISPOSITIONS is not PERSONAL_USE_PROPERTY_DISPOSITIONS


def test_missing_dispositions_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="personal_use_property_dispositions"):
        gains().compute(())


def test_compute_is_repeatable() -> None:
    wired = gains()
    given = (personal_use(GAIN, LOSS),)

    assert wired.compute(given) == wired.compute(given)


# --- trace -------------------------------------------------------------------------------------


def floored_line(
    position: int,
    row: Row,
    minimum: str,
    proceeds_used: str,
    cost_base_used: str,
    gain: str,
    result: str,
) -> PersonalUsePropertyGainLine:
    proceeds, cost_base, outlays = row
    return PersonalUsePropertyGainLine(
        output=PERSONAL_USE_PROPERTY_GAIN_ROWS,
        position=position,
        proceeds=D(proceeds),
        adjusted_cost_base=D(cost_base),
        outlays=D(outlays),
        minimum=D(minimum),
        proceeds_used=D(proceeds_used),
        cost_base_used=D(cost_base_used),
        gain=D(gain),
        result=D(result),
    )


def test_traces_each_row_with_its_floors_and_the_figure_counted() -> None:
    trace = gains().compute((personal_use(GAIN, LOSS),)).trace

    assert trace == (
        floored_line(1, GAIN, "1000", "1500.00", "1000.00", "450.00", "450.00"),
        # The loss row's proceeds 800 are raised to 1,000; its ACB 1,000 is already at the floor.
        floored_line(2, LOSS, "1000", "1000", "1000", "-30", "0"),
        ItemsTotalLine(
            PERSONAL_USE_PROPERTY_GAIN_ROWS, ((1, D("450.00")), (2, D("0"))), D("450.00")
        ),
    )


def test_traces_the_guide_example_rows() -> None:
    trace = gains().compute((personal_use(CHINA_CABINET, BOAT, PERSONAL_COMPUTER),)).trace

    assert trace[:3] == (
        floored_line(1, CHINA_CABINET, "1000", "1000", "1000", "0", "0"),
        floored_line(2, BOAT, "1000", "1200.00", "1000", "150.00", "150.00"),
        floored_line(3, PERSONAL_COMPUTER, "1000", "1500.00", "3200.00", "-1730.00", "0"),
    )
    assert trace[3] == ItemsTotalLine(
        PERSONAL_USE_PROPERTY_GAIN_ROWS,
        ((1, D("0")), (2, D("150.00")), (3, D("0"))),
        D("150.00"),
    )


def test_traces_no_rows_as_only_an_empty_total() -> None:
    assert gains().compute((personal_use(),)).trace == (
        ItemsTotalLine(PERSONAL_USE_PROPERTY_GAIN_ROWS, (), D("0")),
    )


def test_the_counted_figure_of_a_loss_is_not_signed() -> None:
    (line, total_line) = gains().compute((personal_use(LOSS),)).trace

    assert isinstance(line, PersonalUsePropertyGainLine)
    assert line.gain == D("-30")
    assert line.result == D("0")
    assert not line.result.is_signed()
    assert line.amount == D("0")
    assert isinstance(total_line, ItemsTotalLine)
    assert not total_line.total.is_signed()


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = gains().compute((personal_use(GAIN, LOSS, NOTHING),))

    (output,) = result.outputs
    assert result.trace[-1].amount == output.value
