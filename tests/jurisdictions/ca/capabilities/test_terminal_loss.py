"""Unit tests for the TerminalLoss capability (`ca/terminal_loss`), the terminal loss of Area A.

T776 Area A, "Column 7: UCC after additions and dispositions (column 2 plus column 3 minus
column 5)", and Note 3: "If no property is left in the class and there is a positive amount in
this column, deduct the amount from your income as a terminal loss under "Terminal loss" on line
9948. Recapture and terminal loss do not apply to a Class 10.1 property unless it is a DIEP."
T2125 Note 3 sends it to line 9270.

Its slots: one parameter slot `class_rates` (a `class_rates` dataset), one consumed slot `classes`
(a record list of the Area A rows) and one produced slot `output`. Each class is worked on its
own: its terminal loss is column 7 when column 7 is positive and no property is left in the
class, and 0 otherwise or for a class the dataset marks as excluded. A class the dataset does not
list, or a row whose columns 11 and 12 are above its column 3, is refused (`InvalidRecordError`).
The output is the total of the terminal losses. It records one `TerminalLossLine` per class, then
an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    InvalidRecordError,
    MissingArtifactError,
)
from tax_calculator.domain.jurisdiction_code import JurisdictionCode
from tax_calculator.domain.parameters.class_rates import CLASS_RATES, ClassRate, ClassRates
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_calculator.jurisdictions.ca.trace import CcaZeroReason, TerminalLossLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CENT,
    CLASS_1,
    CLASS_8,
    CLASS_10,
    CLASS_10_1,
    CLASSES,
    TERMINAL_LOSS,
    WITH_ADDITIONS,
    WITH_RECAPTURE,
    WITH_TERMINAL_LOSS,
    class_rates,
    classes,
    row,
    service,
)

D = Decimal


def capability(dataset: ParameterDataset[ClassRates] | None = None) -> TerminalLoss:
    return TerminalLoss(dataset or class_rates(), CLASSES, TERMINAL_LOSS)


def compute(*rows: dict[Any, Decimal | int]) -> Artifact[Any]:
    (output,) = capability().compute((classes(*rows),)).outputs
    return output


def total(*rows: dict[Any, Decimal | int]) -> Decimal:
    value = compute(*rows).value
    assert isinstance(value, Decimal)
    return value


def loss(
    position: int,
    class_rate: ClassRate,
    no_property_left: int,
    column_7: str,
    result: str,
    zero_reason: CcaZeroReason,
    column_7_positive: bool,
) -> TerminalLossLine:
    return TerminalLossLine(
        TERMINAL_LOSS,
        position,
        class_rate,
        no_property_left,
        D(column_7),
        zero_reason,
        column_7_positive,
        D(result),
    )


def test_is_registered_as_ca_terminal_loss() -> None:
    assert CapabilityRegistry.shared().get("ca/terminal_loss") is TerminalLoss


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "terminal_loss" in ca_capabilities.__all__
    assert ca_capabilities.terminal_loss.TerminalLoss is TerminalLoss


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({TERMINAL_LOSS})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TerminalLoss)
    assert "produces" not in vars(TerminalLoss)


def test_declares_its_slots() -> None:
    assert TerminalLoss.PARAMETERS == {"class_rates": CLASS_RATES}
    assert TerminalLoss.CONSUMES == {"classes": RecordList}
    assert TerminalLoss.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for each in (TerminalLoss.PARAMETERS, TerminalLoss.CONSUMES, TerminalLoss.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TerminalLoss.PARAMETERS, Mapping[str, ParameterKind[ClassRates]])
    assert_type(TerminalLoss.CONSUMES, Mapping[str, type])
    assert_type(TerminalLoss.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TerminalLoss(class_rates=class_rates(), classes=CLASSES, output=TERMINAL_LOSS)

    (output,) = wired.compute((classes(WITH_TERMINAL_LOSS),)).outputs
    assert output == Artifact(TERMINAL_LOSS, D("5000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        TerminalLoss(class_rates(), CLASSES, TERMINAL_LOSS, CENT)  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_classes() -> None:
    with pytest.raises(InvalidCapabilityError, match="TerminalLoss.*'classes'"):
        TerminalLoss(class_rates(), TERMINAL_LOSS, TERMINAL_LOSS)  # type: ignore[arg-type]


# --- computing ----------------------------------------------------------------------------------


def test_a_class_closing_with_a_terminal_loss_gives_the_tables_figure() -> None:
    # Column 7: 20,000 - 15,000 = 5,000, positive, with no property left: a terminal loss of 5,000.
    assert total(WITH_TERMINAL_LOSS) == D("5000")


def test_the_same_class_with_property_left_has_no_terminal_loss() -> None:
    value = total(row("1", "20000", proceeds="15000", no_property_left=0))

    assert value == D("0")
    assert not value.is_signed()


def test_a_class_with_additions_has_no_terminal_loss() -> None:
    assert total(WITH_ADDITIONS) == D("0")


def test_a_class_with_a_recapture_has_no_terminal_loss() -> None:
    assert total(WITH_RECAPTURE) == D("0")
    assert total(row("10", "5000", proceeds="8000", no_property_left=1)) == D("0")


def test_a_column_7_of_zero_with_no_property_left_has_no_terminal_loss() -> None:
    assert total(row("1", "1000", proceeds="1000", no_property_left=1)) == D("0")


def test_a_cent_above_zero_with_no_property_left_is_a_cent_of_terminal_loss() -> None:
    assert total(row("1", "1000", proceeds="999.99", no_property_left=1)) == D("0.01")


def test_additions_in_the_year_count_in_column_7() -> None:
    # Column 7: 1,000 + 500 - 600 = 900.
    assert total(row("8", "1000", "500", "600", no_property_left=1)) == D("900")


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_is_refused_not_read_as_a_terminal_loss(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 1: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        compute(row("1", "20000", proceeds="15000", no_property_left=value))


@pytest.mark.parametrize("value", [2, 13])
def test_a_no_property_left_flag_above_1_names_its_item_at_position_2(value: int) -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=rf"^item 2: ca/cca_no_property_left {value} is above a yes or no answer of 1$",
    ):
        compute(WITH_TERMINAL_LOSS, row("8", "1000", proceeds="400", no_property_left=value))


def test_a_class_excluded_from_terminal_loss_has_none() -> None:
    # Note 3: "Recapture and terminal loss do not apply to a Class 10.1 property unless it is a
    # DIEP."
    value = total(row("10.1", "10000", proceeds="4000", no_property_left=1))

    assert value == D("0")
    assert not value.is_signed()


def test_the_terminal_losses_of_several_classes_are_added() -> None:
    other = row("8", "1000", proceeds="400", no_property_left=1)

    assert total(WITH_TERMINAL_LOSS, WITH_ADDITIONS, other) == D("5600")


def test_no_classes_give_zero() -> None:
    output = compute()

    assert output == Artifact(TERMINAL_LOSS, D("0"))
    assert not output.value.is_signed()


@pytest.mark.parametrize("number", ["13", "14"])
def test_a_class_the_dataset_does_not_list_is_refused(number: str) -> None:
    with pytest.raises(
        InvalidRecordError, match=f"^item 1: class {number} is not in the class rates"
    ):
        compute(row(number, "1000", no_property_left=1))


def test_missing_classes_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="cca_classes"):
        capability().compute(())


def test_a_row_whose_columns_11_and_12_are_above_column_3_is_refused() -> None:
    # Columns 11 and 12 are "Cost of remaining additions from column 10".
    with pytest.raises(InvalidRecordError) as raised:
        compute(row("43.1", "0", "100", aiip_additions="60000", riip_additions="40000"))

    assert str(raised.value) == "item 1: columns 11 and 12 (100000) are above column 3 (100)"


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_terminal_loss_line_per_class_then_the_total() -> None:
    excluded = row("10.1", "10000", proceeds="4000", no_property_left=1)
    trace = (
        capability()
        .compute((classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS, excluded),))
        .trace
    )

    assert trace == (
        loss(1, CLASS_8, 0, "13000", "0", CcaZeroReason.NONE, True),
        loss(2, CLASS_10, 0, "-3000", "0", CcaZeroReason.COLUMN_7_NEGATIVE, False),
        loss(3, CLASS_1, 1, "5000", "5000", CcaZeroReason.NO_PROPERTY_LEFT, True),
        loss(4, CLASS_10_1, 1, "6000", "0", CcaZeroReason.NO_PROPERTY_LEFT, True),
        ItemsTotalLine(
            TERMINAL_LOSS, ((1, D("0")), (2, D("0")), (3, D("5000")), (4, D("0"))), D("5000")
        ),
    )


def test_traces_a_column_7_of_zero_as_neither_positive_nor_a_reason() -> None:
    # Column 7 of 0 with no property left: no reason the maximum is 0 by T4036's rule, and column
    # 7 not positive, so the line reads "is not positive" rather than "with property left".
    (line, _total) = (
        capability()
        .compute((classes(row("1", "1000", proceeds="1000", no_property_left=1)),))
        .trace
    )

    assert line == loss(1, CLASS_1, 1, "0", "0", CcaZeroReason.NONE, False)


def test_traces_a_positive_column_7_with_property_left() -> None:
    (line, _total) = capability().compute((classes(row("1", "20000", proceeds="15000")),)).trace

    assert line == loss(1, CLASS_1, 0, "5000", "0", CcaZeroReason.NONE, True)


def test_traces_no_classes_as_only_an_empty_total() -> None:
    assert capability().compute((classes(),)).trace == (ItemsTotalLine(TERMINAL_LOSS, (), D("0")),)


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_gives_the_total_terminal_loss() -> None:
    worksheet = service("ca/terminal_loss", TERMINAL_LOSS).compute(
        JurisdictionCode("CA-ON"), 2025, classes(WITH_ADDITIONS, WITH_RECAPTURE, WITH_TERMINAL_LOSS)
    )["ca-on/return"][0]

    assert worksheet.get(TERMINAL_LOSS).value == D("5000")
    assert isinstance(worksheet.producer_of(TERMINAL_LOSS), TerminalLoss)
