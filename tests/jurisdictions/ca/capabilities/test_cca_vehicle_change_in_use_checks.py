"""Unit tests for the CcaVehicleChangeInUseChecks capability
(`ca/cca_vehicle_change_in_use_checks`), the check of the cost of additions of a Class 10.1
passenger vehicle of Form T777 Part B that started being used for employment in the year.

Guide T4044 2025, Part B column 3: "If you owned a passenger vehicle for personal use and then
started using it for employment in 2025, there is a change in use. In most cases when this happens,
the amount you will enter in column 3 is the fair market value of the property at the time you
start using the property for employment."

The additions (column 3) of a Class 10.1 row with additions that is answered as a change in use
must be its fair market value; any other figure is refused (`InvalidRecordError`, naming the
item). A row not answered as a change in use, a row with no additions and a row of another class
are not checked; an answer other than 0 or 1 is refused.

Its slots: one consumed slot, `classes` (a record list of the Part B rows), and one produced slot,
`output`, a record list of the same fields. It records one `CcaVehicleChangeInUseCheckLine` for
each row, by position, whether it was checked, its additions and its fair market value.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, InvalidRecordError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_change_in_use_checks import (
    CcaVehicleChangeInUseChecks,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS,
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleChangeInUseCheckLine
from tests.jurisdictions.ca.capabilities.test_cca_part_b_checks import row as part_b_row

D = Decimal
CLASSES: RecordListKind = T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS
CHECKED: RecordListKind = T777_PART_B_CHANGE_IN_USE_CHECKED_ROWS


def capability() -> CcaVehicleChangeInUseChecks:
    return CcaVehicleChangeInUseChecks(CLASSES, CHECKED)


def vehicle(
    additions: str, market: str = "11000", *, answer: int = 1, number: str = "10.1"
) -> dict[Any, Any]:
    """A Part B row of the class `number` with `additions`, answered `answer` as a change in use,
    with its fair market value `market` (the Guide's car worth $11,000)."""
    record = part_b_row(additions=additions)
    record[CCA_CLASS_NUMBER] = D(number)
    record[CCA_VEHICLE_CHANGE_IN_USE] = answer
    record[CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE] = D(market)
    return record


def run(*rows: dict[Any, Any]) -> Any:
    """The result for `rows`, as the `CapabilityResult`."""
    artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    return capability().compute((artifact,))


def checked(*rows: dict[Any, Any]) -> RecordList:
    (output,) = run(*rows).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def test_additions_equal_to_the_fair_market_value_pass_unchanged() -> None:
    # The Guide's example: bought in 2018 for $19,000, worth $11,000 when it started being used.
    passing = vehicle("11000")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_additions_that_are_not_the_fair_market_value_are_refused_naming_the_item() -> None:
    # The original $19,000 entered in column 3 instead of the $11,000 is refused.
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(vehicle("19000"))

    assert str(error.value) == (
        "item 1: additions (19000.00) of a vehicle with a change in use are not its fair market "
        "value (11000.00) when it started being used for employment"
    )


def test_additions_a_cent_either_side_of_the_fair_market_value_are_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1"):
        run(vehicle("11000.01"))
    with pytest.raises(InvalidRecordError, match="item 1"):
        run(vehicle("10999.99"))


def test_a_row_not_answered_as_a_change_in_use_is_not_checked() -> None:
    result = run(vehicle("19000", answer=0))

    assert len(checked(vehicle("19000", answer=0)).records) == 1
    (line,) = result.trace
    assert line.applied is False
    assert line.fair_market_value == D("0")


def test_a_row_with_no_additions_is_not_checked() -> None:
    (line,) = run(vehicle("0")).trace

    assert line.applied is False


def test_a_row_of_another_class_is_not_checked() -> None:
    (line,) = run(vehicle("19000", number="10")).trace

    assert line.applied is False


def test_an_answer_other_than_0_or_1_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1: change in use is 2"):
        run(vehicle("11000", answer=2))


def test_a_refused_row_is_named_by_its_position_in_the_list() -> None:
    with pytest.raises(InvalidRecordError, match="item 2"):
        run(vehicle("11000"), vehicle("19000"))


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_row_gives_one_line_by_position_with_its_additions_and_fair_market_value() -> None:
    result = run(vehicle("11000"), vehicle("19000", answer=0), vehicle("0"))

    lines = result.trace
    assert all(isinstance(line, CcaVehicleChangeInUseCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2, 3]
    assert lines[0] == CcaVehicleChangeInUseCheckLine(CHECKED, 1, True, D("11000"), D("11000"))
    assert lines[1] == CcaVehicleChangeInUseCheckLine(CHECKED, 2, False, D("19000"), D("0"))
    assert lines[2].applied is False


def test_a_check_line_amount_is_the_additions_as_entered() -> None:
    (line,) = run(vehicle("11000")).trace

    assert line.amount == D("11000")
    assert line.output_kind is CHECKED


def test_the_output_holds_the_same_fields_as_the_classes_in_the_callers_order() -> None:
    output = checked(vehicle("11000"), vehicle("7", number="10"))

    assert output.fields == CHECKED.fields == CLASSES.fields
    assert [record[CCA_ADDITIONS] for record in output.records] == [D("11000"), D("7")]


def test_is_registered_as_ca_cca_vehicle_change_in_use_checks() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/cca_vehicle_change_in_use_checks")
        is CcaVehicleChangeInUseChecks
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_vehicle_change_in_use_checks" in ca_capabilities.__all__
    assert (
        ca_capabilities.cca_vehicle_change_in_use_checks.CcaVehicleChangeInUseChecks
        is CcaVehicleChangeInUseChecks
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaVehicleChangeInUseChecks)
    assert "produces" not in vars(CcaVehicleChangeInUseChecks)


def test_declares_its_slots() -> None:
    assert CcaVehicleChangeInUseChecks.CONSUMES == {"classes": RecordList}
    assert CcaVehicleChangeInUseChecks.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (CcaVehicleChangeInUseChecks.CONSUMES, CcaVehicleChangeInUseChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaVehicleChangeInUseChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaVehicleChangeInUseChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaVehicleChangeInUseChecks(classes=CLASSES, output=CHECKED)

    assert wired.consumes == frozenset({CLASSES})


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaVehicleChangeInUseChecks.*'output'"):
        CcaVehicleChangeInUseChecks(
            CLASSES,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )
