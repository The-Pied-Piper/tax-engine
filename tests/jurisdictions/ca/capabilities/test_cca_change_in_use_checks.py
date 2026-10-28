"""Unit tests for the CcaChangeInUseChecks capability (`ca/cca_change_in_use_checks`), the check of
the cost of additions of a row of Form T777 Part A (the classes 8, 10, 54 and 55) that started
being used for employment in the year.

Guide T4044 2025, Part A column 3: "If you owned property for personal use and then started using it
for employment in 2025, there is a change in use. In most cases when this happens, the amount you
will enter in this column is the fair market value of the property at the time you start using the
property for employment."

The additions (column 3) of a Part A row with additions that is answered as a change in use must be
its fair market value; any other figure is refused (`InvalidRecordError`, naming the item). Unlike
Part B, there is no class condition: a row of any class of Part A is checked. A row not answered as
a change in use and a row with no additions are not checked; an answer other than 0 or 1 is refused.

Its slots: one consumed slot, `classes` (a record list of the Part A rows), and one produced slot,
`output`, a record list of the same fields as the output kind. The Class 8 rows and the vehicle rows
each have their own checks; the vehicle output keeps the year, cost, government assistance and sold
vehicles, which the proceeds read. It
records one `CcaChangeInUseCheckLine` for each row, by position, whether it was checked, its
additions and its fair market value.
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
from tax_calculator.jurisdictions.ca.capabilities.cca_change_in_use_checks import (
    CcaChangeInUseChecks,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_CLASS_NUMBER,
    CCA_SOLD_ZEPVS,
    CCA_VEHICLE_ACQUIRED_YEAR,
    T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS,
    T777_CLASS_8_CHECKED_ROWS,
    T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS,
    T777_VEHICLE_CHECKED_ROWS,
)
from tax_calculator.jurisdictions.ca.trace import CcaChangeInUseCheckLine

D = Decimal
CLASSES: RecordListKind = T777_CLASS_8_CHECKED_ROWS
CHECKED: RecordListKind = T777_CLASS_8_CHANGE_IN_USE_CHECKED_ROWS
VEHICLE_CLASSES: RecordListKind = T777_VEHICLE_CHECKED_ROWS
VEHICLE_CHECKED: RecordListKind = T777_VEHICLE_CHANGE_IN_USE_CHECKED_ROWS
CHANGE_IN_USE_FIELDS = {CCA_CHANGE_IN_USE, CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE}


def row(
    kind: RecordListKind,
    class_number: str,
    additions: str,
    *,
    answer: int = 1,
    market: str = "11000",
) -> dict[Any, Any]:
    """A Part A row of `kind` of the class `class_number` with `additions`, answered `answer` as a
    change in use, with its fair market value `market` (the Guide's car worth $11,000). Every other
    column of the list is 0, and the nested list of sold vehicles (of a vehicle list) is empty."""
    values: dict[Any, Any] = {}
    for field in kind.fields:
        if isinstance(field, RecordListKind):
            values[field] = RecordList(field.fields, [])
        elif field.value_type is int:
            values[field] = 0
        else:
            values[field] = D(0)
    values[CCA_CLASS_NUMBER] = D(class_number)
    values[CCA_ADDITIONS] = D(additions)
    values[CCA_CHANGE_IN_USE] = answer
    values[CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE] = D(market)
    return values


def capability() -> CcaChangeInUseChecks:
    return CcaChangeInUseChecks(CLASSES, CHECKED)


def run(*rows: dict[Any, Any]) -> Any:
    """The result for `rows` of the Class 8 list, as the `CapabilityResult`."""
    artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    return capability().compute((artifact,))


def run_vehicles(*rows: dict[Any, Any]) -> Any:
    """The result for `rows` of the vehicle list (Classes 10, 54 and 55), as a result."""
    artifact = Artifact(VEHICLE_CLASSES, RecordList(VEHICLE_CLASSES.fields, list(rows)))
    return CcaChangeInUseChecks(VEHICLE_CLASSES, VEHICLE_CHECKED).compute((artifact,))


def checked(*rows: dict[Any, Any]) -> RecordList:
    (output,) = run(*rows).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def test_additions_equal_to_the_fair_market_value_pass_unchanged() -> None:
    # Bought in 2018 and worth $11,000 when it started being used for employment: the Class 8 row
    # passes with its fields as the output holds them.
    passing = row(CLASSES, "8", "11000")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_a_vehicle_with_a_change_in_use_whose_additions_are_its_fair_market_value_passes() -> None:
    # The Guide's example: a car bought in 2018 for $19,000, worth $11,000 when it started being
    # used for employment, so $11,000 goes in column 3.
    (output,) = run_vehicles(row(VEHICLE_CLASSES, "10", "11000")).outputs

    assert output.kind is VEHICLE_CHECKED
    assert isinstance(output.value, RecordList)
    assert [record[CCA_ADDITIONS] for record in output.value.records] == [D("11000")]


def test_the_original_cost_of_a_vehicle_with_a_change_in_use_is_refused_naming_the_item() -> None:
    # The original $19,000 entered in column 3 instead of the $11,000 is refused.
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run_vehicles(row(VEHICLE_CLASSES, "10", "19000"))

    assert str(error.value) == (
        "item 1: additions (19000.00) of property with a change in use are not its fair market "
        "value (11000.00) when it started being used for employment"
    )


def test_a_class_8_row_with_a_change_in_use_is_refused_when_the_additions_differ() -> None:
    # Part A has no class condition: a Class 8 row is checked as a vehicle row is.
    with pytest.raises(InvalidRecordError) as error:
        run(row(CLASSES, "8", "2000", market="1500"))

    assert str(error.value) == (
        "item 1: additions (2000.00) of property with a change in use are not its fair market "
        "value (1500.00) when it started being used for employment"
    )


@pytest.mark.parametrize("number", ["54", "55"])
def test_a_vehicle_of_class_54_or_55_with_a_change_in_use_is_checked(number: str) -> None:
    # The vehicle classes 54 and 55 are checked as Class 10 is, with no class condition.
    with pytest.raises(InvalidRecordError, match="item 1: additions \\(19000.00\\)"):
        run_vehicles(row(VEHICLE_CLASSES, number, "19000"))


def test_additions_a_cent_either_side_of_the_fair_market_value_are_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1"):
        run(row(CLASSES, "8", "11000.01"))
    with pytest.raises(InvalidRecordError, match="item 1"):
        run(row(CLASSES, "8", "10999.99"))


def test_a_row_not_answered_as_a_change_in_use_is_not_checked() -> None:
    result = run(row(CLASSES, "8", "19000", answer=0))

    assert len(checked(row(CLASSES, "8", "19000", answer=0)).records) == 1
    (line,) = result.trace
    assert line.applied is False
    assert line.fair_market_value == D("0")


def test_a_row_with_no_additions_is_not_checked() -> None:
    (line,) = run(row(CLASSES, "8", "0")).trace

    assert line.applied is False


def test_an_answer_other_than_0_or_1_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1: change in use is 2"):
        run(row(CLASSES, "8", "11000", answer=2))


def test_a_refused_row_is_named_by_its_position_in_the_list() -> None:
    with pytest.raises(InvalidRecordError, match="item 2"):
        run(row(CLASSES, "8", "11000"), row(CLASSES, "8", "19000"))


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_row_gives_one_line_by_position_with_its_additions_and_fair_market_value() -> None:
    result = run(
        row(CLASSES, "8", "11000"),
        row(CLASSES, "8", "19000", answer=0),
        row(CLASSES, "8", "0"),
    )

    lines = result.trace
    assert all(isinstance(line, CcaChangeInUseCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2, 3]
    assert lines[0] == CcaChangeInUseCheckLine(CHECKED, 1, True, D("11000"), D("11000"))
    assert lines[1] == CcaChangeInUseCheckLine(CHECKED, 2, False, D("19000"), D("0"))
    assert lines[2].applied is False


def test_a_check_line_amount_is_the_additions_as_entered() -> None:
    (line,) = run(row(CLASSES, "8", "11000")).trace

    assert line.amount == D("11000")
    assert line.output_kind is CHECKED


def test_the_class_8_output_holds_the_fields_of_the_rows() -> None:
    output = checked(row(CLASSES, "8", "11000"))

    assert output.fields == CHECKED.fields
    assert CHANGE_IN_USE_FIELDS <= set(CHECKED.fields)
    assert [record[CCA_ADDITIONS] for record in output.records] == [D("11000")]


def test_the_vehicle_output_keeps_the_fields_of_the_rows() -> None:
    (output,) = run_vehicles(row(VEHICLE_CLASSES, "10", "11000")).outputs

    assert isinstance(output.value, RecordList)
    assert output.value.fields == VEHICLE_CHECKED.fields
    assert CHANGE_IN_USE_FIELDS <= set(VEHICLE_CHECKED.fields)
    assert CCA_VEHICLE_ACQUIRED_YEAR in VEHICLE_CHECKED.fields
    assert CCA_SOLD_ZEPVS in VEHICLE_CHECKED.fields


def test_is_registered_as_ca_cca_change_in_use_checks() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_change_in_use_checks") is CcaChangeInUseChecks


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_change_in_use_checks" in ca_capabilities.__all__
    assert ca_capabilities.cca_change_in_use_checks.CcaChangeInUseChecks is CcaChangeInUseChecks


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaChangeInUseChecks)
    assert "produces" not in vars(CcaChangeInUseChecks)


def test_declares_its_slots() -> None:
    assert CcaChangeInUseChecks.CONSUMES == {"classes": RecordList}
    assert CcaChangeInUseChecks.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (CcaChangeInUseChecks.CONSUMES, CcaChangeInUseChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaChangeInUseChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaChangeInUseChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaChangeInUseChecks(classes=CLASSES, output=CHECKED)

    assert wired.consumes == frozenset({CLASSES})


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaChangeInUseChecks.*'output'"):
        CcaChangeInUseChecks(
            CLASSES,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )
