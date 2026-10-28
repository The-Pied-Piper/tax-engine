"""Unit tests for the CcaPartBChecks capability (`ca/cca_part_b_checks`), the checks of the Part B
rows of Form T777, the Class 10.1 passenger vehicles.

T777 (2025), Part B "List each passenger vehicle on a separate line", and note (11): "If you owned
the vehicle in the previous year and still owned it at the end of the current year, enter the
amount from column 2 in column 5." Note (12): "Recapture and terminal loss rules do not apply."
Column 4 is the proceeds of dispositions in the year, entered for a vehicle sold in the year, the
tick "no property left" of the table.

The capability refuses (`InvalidRecordError`, naming the item) a row that has both a UCC at the
start of the year and additions, proceeds without the tick, and the tick without proceeds. A row
that passes is passed on unchanged, and it records one `CcaPartBCheckLine` for each row, by
position and with no total.

Its slots: one consumed slot, `classes` (a record list of the Part B rows), and one produced slot,
`output`, a record list of the same fields. The layout follows the `CcaVehicleProceeds` tests.
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
from tax_calculator.jurisdictions.ca.capabilities.cca_part_b_checks import CcaPartBChecks
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_NO_PROPERTY_LEFT,
    CCA_PROCEEDS,
    CCA_RIIP_ADDITIONS,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
    T777_PART_B_CHECKED_ROWS,
    T777_PART_B_ROWS,
)
from tax_calculator.jurisdictions.ca.trace import CcaPartBCheckLine

D = Decimal
CLASSES: RecordListKind = T777_PART_B_ROWS
CHECKED: RecordListKind = T777_PART_B_CHECKED_ROWS


def row(
    ucc_at_start: str = "0",
    additions: str = "0",
    proceeds: str = "0",
    sold: int = 0,
    claimed: str = "0",
) -> dict[Any, Any]:
    """A Part B row of Class 10.1, with the fields the table reads: the class number, the UCC at
    the start, the additions, the proceeds, the claim and the sold tick."""
    return {
        CCA_VEHICLE_ACQUIRED_YEAR: 0,
        CCA_VEHICLE_COST: D("0"),
        CCA_VEHICLE_FROM_NON_ARMS_LENGTH: 0,
        CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE: D("0"),
        CCA_VEHICLE_SELLER_COST: D("0"),
        CCA_VEHICLE_CHANGE_IN_USE: 0,
        CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE: D("0"),
        CCA_CLASS_NUMBER: D("10.1"),
        CCA_UCC_AT_START: D(ucc_at_start),
        CCA_ADDITIONS: D(additions),
        CCA_AIIP_ADDITIONS: D("0"),
        CCA_RIIP_ADDITIONS: D("0"),
        CCA_PROCEEDS: D(proceeds),
        CCA_CLAIMED: D(claimed),
        CCA_NO_PROPERTY_LEFT: sold,
    }


def capability() -> CcaPartBChecks:
    return CcaPartBChecks(CLASSES, CHECKED)


def run(*rows: dict[Any, Any]) -> Any:
    """The capability's result for `rows`, as the `CapabilityResult`."""
    artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    return capability().compute((artifact,))


def checked(*rows: dict[Any, Any]) -> RecordList:
    (output,) = run(*rows).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def test_a_row_owned_from_the_previous_year_passes_unchanged() -> None:
    # Note (11): owned in the previous year and still owned at the end of the year.
    passing = row(ucc_at_start="20000", claimed="6000")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_a_row_bought_in_the_year_passes() -> None:
    records = checked(row(additions="15000", claimed="2500")).records

    assert records[0][CCA_ADDITIONS] == D("15000")


def test_a_vehicle_sold_in_the_year_with_proceeds_and_its_tick_passes() -> None:
    records = checked(row(ucc_at_start="20000", proceeds="12000", sold=1)).records

    assert records[0][CCA_PROCEEDS] == D("12000")
    assert records[0][CCA_NO_PROPERTY_LEFT] == 1


def test_a_row_with_a_ucc_at_the_start_and_additions_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(row(ucc_at_start="20000", additions="15000"))

    assert "not both" in str(error.value)


def test_a_row_with_proceeds_and_no_tick_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 2") as error:
        run(row(ucc_at_start="20000"), row(ucc_at_start="20000", proceeds="12000"))

    assert "without the sold in the year tick" in str(error.value)


def test_a_tick_without_proceeds_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(row(ucc_at_start="20000", sold=1))

    assert "without proceeds" in str(error.value)


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_passing_row_gives_one_line_by_position_and_no_total() -> None:
    result = run(
        row(ucc_at_start="20000", claimed="6000"),
        row(ucc_at_start="10000", proceeds="4000", sold=1, claimed="1000"),
    )

    lines = result.trace
    assert all(isinstance(line, CcaPartBCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2]
    assert lines[1] == CcaPartBCheckLine(CHECKED, 2, D("10000"), D("0"), D("4000"), True)
    assert lines[0].sold_in_year is False


def test_a_check_line_amount_is_the_row_proceeds() -> None:
    (line,) = run(row(ucc_at_start="20000", proceeds="12000", sold=1)).trace

    assert line.amount == D("12000")
    assert line.output is CHECKED


def test_is_registered_as_ca_cca_part_b_checks() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_part_b_checks") is CcaPartBChecks


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_part_b_checks" in ca_capabilities.__all__
    assert ca_capabilities.cca_part_b_checks.CcaPartBChecks is CcaPartBChecks


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaPartBChecks)
    assert "produces" not in vars(CcaPartBChecks)


def test_declares_its_slots() -> None:
    assert CcaPartBChecks.CONSUMES == {"classes": RecordList}
    assert CcaPartBChecks.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (CcaPartBChecks.CONSUMES, CcaPartBChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaPartBChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaPartBChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaPartBChecks(classes=CLASSES, output=CHECKED)

    assert wired.consumes == frozenset({CLASSES})


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaPartBChecks.*'output'"):
        CcaPartBChecks(CLASSES, ArtifactKind("ex/other_amount", Decimal))  # type: ignore[arg-type]
