"""Unit tests for the CcaVehicleClassChecks capability (`ca/cca_vehicle_class_checks`), the check
of the class condition of a passenger vehicle of Form T777 Part B.

Guide T4044 2025, "Class 10.1": "Include your passenger vehicle in Class 10.1 if it meets one of
the following conditions: - You acquired it after December 31, 2000, and before January 1, 2022,
and it cost you more than $30,000 - ... - You acquired it after December 31, 2024, and it cost you
more than $38,000. If your passenger vehicle does not meet any of these conditions, then it belongs
in Class 10." and "do not include the GST and PST or HST when calculating the cost of the vehicle."

The cost of vehicle (before tax) of a Class 10.1 row, with its date acquired (its year), must be
more than the `minimum_cost` of the row of the dataset for that year; a cost equal to it, or a
year with no row (before 2001), is refused (`InvalidRecordError`, naming the item). A row with no
date acquired (year 0) is refused on every row, whatever its class (the date is printed on every
row); a row of another class is not checked for the condition.

Its slots: one parameter, `class_conditions` (a `year_amounts` dataset), one consumed slot,
`classes` (a record list of the Part B rows), and one produced slot, `output`, a record list of the
same fields. It records one `CcaVehicleClassCheckLine` for each row, by position, whether it was
checked, its year, cost and minimum (0 when it was not checked).
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
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.year_amounts import (
    YEAR_AMOUNTS,
    YearAmounts,
    YearAmountsRow,
)
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.capabilities.cca_vehicle_class_checks import (
    CcaVehicleClassChecks,
)
from tax_engine.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_COST,
    T777_PART_B_ADDITIONS_CHECKED_ROWS,
    T777_PART_B_CLASS_CHECKED_ROWS,
)
from tax_engine.jurisdictions.ca.trace import CcaVehicleClassCheckLine
from tests.jurisdictions.ca.capabilities.test_cca_part_b_checks import row as part_b_row

D = Decimal
CLASSES: RecordListKind = T777_PART_B_ADDITIONS_CHECKED_ROWS
CHECKED: RecordListKind = T777_PART_B_CLASS_CHECKED_ROWS
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Guide T4044 "Class 10.1": 38,000 for 2025, 37,000 for 2024, 36,000 for 2023, 34,000 for 2022 and
# 30,000 for a vehicle acquired after December 31, 2000 and before January 1, 2022 (the oldest row).
CONDITIONS = (
    (2025, "38000"),
    (2024, "37000"),
    (2023, "36000"),
    (2022, "34000"),
    (2001, "30000"),
)


def class_conditions(
    rows: tuple[tuple[int, str], ...] = CONDITIONS,
) -> ParameterDataset[YearAmounts]:
    """The minimum costs by year acquired, newest first: (from_year, the `minimum_cost`)."""
    table = YearAmounts(
        tuple(YearAmountsRow(year, {"minimum_cost": D(amount)}) for year, amount in rows)
    )
    return ParameterDataset(
        "ca/cca_class_10_1_conditions",
        2025,
        YEAR_AMOUNTS,
        table,
        CENT,
        ("https://example.org/t4044",),
    )


def capability() -> CcaVehicleClassChecks:
    return CcaVehicleClassChecks(class_conditions(), CLASSES, CHECKED)


def vehicle(year: int, cost: str, *, number: str = "10.1") -> dict[Any, Any]:
    """A Part B row of the class `number` with the date acquired's `year` and the `cost`."""
    record = part_b_row(additions="30000")
    record[CCA_VEHICLE_ACQUIRED_YEAR] = year
    record[CCA_VEHICLE_COST] = D(cost)
    record[CCA_CLASS_NUMBER] = D(number)
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


def test_a_vehicle_that_cost_more_than_the_minimum_of_its_year_passes_unchanged() -> None:
    passing = vehicle(2025, "38000.01")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_a_cost_equal_to_the_minimum_is_refused_naming_the_item() -> None:
    # The Guide's own example (2024-12-31, $37,000.00) is not "more than $37,000".
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(vehicle(2024, "37000.00"))

    assert str(error.value) == (
        "item 1: a vehicle acquired in 2024 that cost 37000.00 before tax is not more than "
        "37000.00, so it belongs in Class 10, not Class 10.1"
    )


@pytest.mark.parametrize(
    ("year", "minimum"),
    [
        (2030, "38000"),
        (2025, "38000"),
        (2024, "37000"),
        (2023, "36000"),
        (2022, "34000"),
        (2021, "30000"),
        (2001, "30000"),
    ],
)
def test_the_minimum_is_the_one_printed_for_the_year_acquired(year: int, minimum: str) -> None:
    just_over = D(minimum) + D("0.01")

    assert len(checked(vehicle(year, str(just_over))).records) == 1
    with pytest.raises(InvalidRecordError, match=rf"not more than {minimum}\.00"):
        run(vehicle(year, minimum))


def test_a_vehicle_acquired_before_2001_meets_none_of_the_conditions() -> None:
    with pytest.raises(InvalidRecordError, match="item 1: a vehicle acquired in 2000 meets none"):
        run(vehicle(2000, "99999.00"))


@pytest.mark.parametrize("number", ["10.1", "10"])
def test_a_row_with_no_date_acquired_is_refused_whatever_its_class(number: str) -> None:
    with pytest.raises(InvalidRecordError, match="item 1: the date acquired is required"):
        run(vehicle(0, "0", number=number))


def test_a_row_with_no_date_acquired_is_named_by_its_position() -> None:
    with pytest.raises(InvalidRecordError, match="item 2: the date acquired is required"):
        run(vehicle(2025, "40000.00"), vehicle(0, "40000.00"))


def test_a_row_of_another_class_is_not_checked_whatever_its_cost() -> None:
    result = run(vehicle(2025, "100.00", number="10"))

    (line,) = result.trace
    assert line.applied is False


def test_a_refused_row_is_named_by_its_position_in_the_list() -> None:
    with pytest.raises(InvalidRecordError, match="item 2"):
        run(vehicle(2025, "40000.00"), vehicle(2025, "30000.00"))


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_row_gives_one_line_by_position_with_its_year_cost_and_minimum() -> None:
    result = run(vehicle(2024, "37000.01"), vehicle(2025, "50000", number="10"))

    lines = result.trace
    assert all(isinstance(line, CcaVehicleClassCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2]
    assert lines[0] == CcaVehicleClassCheckLine(CHECKED, 1, True, 2024, D("37000.01"), D("37000"))
    assert lines[1] == CcaVehicleClassCheckLine(CHECKED, 2, False, 2025, D("50000"), D("0"))


def test_a_check_line_amount_is_the_cost_as_entered() -> None:
    (line,) = run(vehicle(2025, "38000.01")).trace

    assert line.amount == D("38000.01")
    assert line.output_kind is CHECKED


def test_the_output_holds_the_same_fields_as_the_classes_in_the_callers_order() -> None:
    output = checked(vehicle(2025, "40000"), vehicle(2025, "10", number="10"))

    assert output.fields == CHECKED.fields == CLASSES.fields
    assert [record[CCA_ADDITIONS] for record in output.records] == [D("30000"), D("30000")]


def test_is_registered_as_ca_cca_vehicle_class_checks() -> None:
    assert CapabilityRegistry.shared().get("ca/cca_vehicle_class_checks") is CcaVehicleClassChecks


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_vehicle_class_checks" in ca_capabilities.__all__
    assert ca_capabilities.cca_vehicle_class_checks.CcaVehicleClassChecks is CcaVehicleClassChecks


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaVehicleClassChecks)
    assert "produces" not in vars(CcaVehicleClassChecks)


def test_declares_its_parameter_and_its_slots() -> None:
    assert CcaVehicleClassChecks.PARAMETERS == {"class_conditions": YEAR_AMOUNTS}
    assert CcaVehicleClassChecks.CONSUMES == {"classes": RecordList}
    assert CcaVehicleClassChecks.PRODUCES == {"output": RecordList}


def test_its_slots_are_read_only() -> None:
    for each in (CcaVehicleClassChecks.CONSUMES, CcaVehicleClassChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaVehicleClassChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaVehicleClassChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaVehicleClassChecks(
        class_conditions=class_conditions(), classes=CLASSES, output=CHECKED
    )

    assert wired.consumes == frozenset({CLASSES})


def test_needs_the_class_conditions() -> None:
    with pytest.raises(TypeError):
        CcaVehicleClassChecks(classes=CLASSES, output=CHECKED)  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaVehicleClassChecks.*'output'"):
        CcaVehicleClassChecks(
            class_conditions(),
            CLASSES,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )
