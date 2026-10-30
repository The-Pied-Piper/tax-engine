"""Unit tests for the CcaPartAChecks capability (`ca/cca_part_a_checks`), the checks of the Part A
rows of Form T777, the classes 8, 10, 54 and 55.

T777 (2025), Part A "Part A - Classes 8, 10, 54, and 55", with the printed class column "8 / 10 /
54 / 55": one row for each class. A class listed twice would start two rows from their own UCC and
claim the CCA of the class twice, so the capability refuses (`InvalidRecordError`, naming both
items) a row whose class number is already listed in an earlier row. Part B (Class 10.1) is one row
for each vehicle and is not checked here; T776, T2125, T2042 and T2121 take any number of rows of a
class, so the check is a T777 capability and not a change to the shared CCA table.

A row that passes is passed on unchanged, and it records one `CcaPartACheckLine` for each row, by
position and with the row's class number, and no amount.

Its slots: one consumed slot, `classes` (a record list of the Part A rows), and one produced slot,
`output`, a record list of the same fields. The layout follows the `CcaPartBChecks` tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, InvalidRecordError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.capabilities.cca_part_a_checks import CcaPartAChecks
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    T777_CLASS_8_CHECKED_ROWS,
    T777_CLASS_8_ROWS,
    T777_VEHICLE_CHECKED_ROWS,
    T777_VEHICLE_ROWS,
)
from tax_engine.jurisdictions.ca.trace import CcaPartACheckLine

D = Decimal
CLASSES: RecordListKind = T777_CLASS_8_ROWS
CHECKED: RecordListKind = T777_CLASS_8_CHECKED_ROWS
VEHICLE_CLASSES: RecordListKind = T777_VEHICLE_ROWS
VEHICLE_CHECKED: RecordListKind = T777_VEHICLE_CHECKED_ROWS


def row(kind: RecordListKind, class_number: str, **amounts: str) -> dict[Any, Any]:
    """A Part A row of `kind`, of the class `class_number`: every column of the list is given,
    the amounts named by their kind as text, the others 0, and the nested list of sold vehicles
    (of a vehicle list) is empty."""
    values: dict[Any, Any] = {}
    for field in kind.fields:
        if isinstance(field, RecordListKind):
            values[field] = RecordList(field.fields, [])
        elif field.value_type is int:
            values[field] = 0
        else:
            values[field] = D(0)
    values[CCA_CLASS_NUMBER] = D(class_number)
    named = {each.identifier: each for each in kind.fields}
    for name, value in amounts.items():
        values[named[f"ca/cca_{name}"]] = D(value)
    return values


def capability() -> CcaPartAChecks:
    return CcaPartAChecks(CLASSES, CHECKED)


def run(*rows: dict[Any, Any]) -> Any:
    """The capability's result for `rows` of the Class 8 list, as the `CapabilityResult`."""
    artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    return capability().compute((artifact,))


def checked(*rows: dict[Any, Any]) -> RecordList:
    (output,) = run(*rows).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def test_a_class_listed_once_passes_unchanged() -> None:
    passing = row(CLASSES, "8", ucc_at_start="1000", additions="500", claimed="250")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_each_vehicle_class_listed_once_passes() -> None:
    (output,) = run_vehicles(
        row(VEHICLE_CLASSES, "10", ucc_at_start="20000"),
        row(VEHICLE_CLASSES, "54", additions="40000", claimed="30000"),
        row(VEHICLE_CLASSES, "55", ucc_at_start="5000"),
    ).outputs

    assert output.kind is VEHICLE_CHECKED
    assert isinstance(output.value, RecordList)
    assert [record[CCA_CLASS_NUMBER] for record in output.value.records] == [
        D("10"),
        D("54"),
        D("55"),
    ]


def run_vehicles(*rows: dict[Any, Any]) -> Any:
    """The capability's result for `rows` of the vehicle list (Classes 10, 54 and 55)."""
    artifact = Artifact(VEHICLE_CLASSES, RecordList(VEHICLE_CLASSES.fields, list(rows)))
    return CcaPartAChecks(VEHICLE_CLASSES, VEHICLE_CHECKED).compute((artifact,))


def test_a_class_listed_twice_is_refused_naming_both_items() -> None:
    with pytest.raises(
        InvalidRecordError, match=r"item 2: class 8 is already listed in item 1"
    ) as (error):
        run(row(CLASSES, "8", ucc_at_start="1000"), row(CLASSES, "8", ucc_at_start="1000"))

    assert "one row for each class" in str(error.value)


def test_a_class_listed_again_after_other_classes_names_the_first_item() -> None:
    with pytest.raises(InvalidRecordError, match=r"item 3: class 54 is already listed in item 1"):
        run_vehicles(
            row(VEHICLE_CLASSES, "54", additions="40000", claimed="30000"),
            row(VEHICLE_CLASSES, "55", ucc_at_start="5000"),
            row(VEHICLE_CLASSES, "54", claimed="0"),
        )


def test_a_repeated_class_with_a_zero_claim_is_still_refused() -> None:
    # A second Class 54 row claiming nothing still lists the class a second time.
    with pytest.raises(InvalidRecordError, match=r"item 2: class 54 is already listed in item 1"):
        run_vehicles(
            row(VEHICLE_CLASSES, "54", additions="40000", claimed="30000"),
            row(VEHICLE_CLASSES, "54", claimed="0"),
        )


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_passing_row_gives_one_line_by_position_and_its_class() -> None:
    result = run(row(CLASSES, "8", ucc_at_start="1000"))

    lines = result.trace
    assert all(isinstance(line, CcaPartACheckLine) for line in lines)
    assert [line.position for line in lines] == [1]
    assert lines[0] == CcaPartACheckLine(CHECKED, 1, D("8"))


def test_a_check_line_has_no_amount() -> None:
    (line,) = run(row(CLASSES, "8", ucc_at_start="1000")).trace

    assert line.amount == D("0")
    assert line.output is CHECKED


def test_is_registered_as_ca_cca_part_a_checks() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_part_a_checks") is CcaPartAChecks


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_part_a_checks" in ca_capabilities.__all__
    assert ca_capabilities.cca_part_a_checks.CcaPartAChecks is CcaPartAChecks


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaPartAChecks)
    assert "produces" not in vars(CcaPartAChecks)


def test_declares_its_slots() -> None:
    assert CcaPartAChecks.CONSUMES == {"classes": RecordList}
    assert CcaPartAChecks.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (CcaPartAChecks.CONSUMES, CcaPartAChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaPartAChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaPartAChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaPartAChecks(classes=CLASSES, output=CHECKED)

    assert wired.consumes == frozenset({CLASSES})


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaPartAChecks.*'output'"):
        CcaPartAChecks(CLASSES, ArtifactKind("ex/other_amount", Decimal))  # type: ignore[arg-type]
