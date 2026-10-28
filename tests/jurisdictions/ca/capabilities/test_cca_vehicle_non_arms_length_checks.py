"""Unit tests for the CcaVehicleNonArmsLengthChecks capability
(`ca/cca_vehicle_non_arms_length_checks`), the check of the cost of additions of a Class 10.1
passenger vehicle of Form T777 Part B bought from a non-arm's-length person.

Guide T4044 2025, Part B column 3: "There is a limit on the capital cost of a Class 10.1 vehicle
you buy from a person with whom you have a non-arm's length relationship. [...] In this case, the
capital cost is the least of the following three amounts: - the fair market value of the vehicle
when you acquired it - $38,000 plus the GST and PST or HST that you would have paid on $38,000 if
you had acquired the vehicle in 2025 - the seller's cost of the vehicle just before you acquired
it."

The additions (column 3) of a Class 10.1 row with additions that is answered as bought from such a
person must be the least of the three (the limit with tax is $42,940 at 13 percent); any other
figure is refused (`InvalidRecordError`, naming the item). A row not answered as bought from such a
person, a row with no additions and a row of another class are not checked; an answer other than
0 or 1 is refused.

Its slots: one parameter, `prescribed_amounts` (a `year_amounts` dataset), two consumed slots,
`classes` (a record list of the Part B rows) and `sales_tax_rate`, and one produced slot, `output`,
a record list of the same fields. It records one `CcaVehicleNonArmsLengthCheckLine` for each row.
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
from tax_calculator.domain.parameters.year_amounts import YEAR_AMOUNTS
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_non_arms_length_checks import (
    CcaVehicleNonArmsLengthChecks,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
    T777_PART_B_CLASS_CHECKED_ROWS,
    T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS,
    T777_VEHICLE_SALES_TAX_RATE,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleNonArmsLengthCheckLine
from tests.jurisdictions.ca.capabilities.cca_vehicle_proceeds import prescribed_amounts
from tests.jurisdictions.ca.capabilities.test_cca_part_b_checks import row as part_b_row

D = Decimal
CLASSES: RecordListKind = T777_PART_B_CLASS_CHECKED_ROWS
CHECKED: RecordListKind = T777_PART_B_NON_ARMS_LENGTH_CHECKED_ROWS
SALES_TAX_RATE = T777_VEHICLE_SALES_TAX_RATE

# $38,000 plus 13 percent (the caller's rate) is $42,940, the limit with tax.
LIMIT_2025 = "42940.00"


def capability() -> CcaVehicleNonArmsLengthChecks:
    return CcaVehicleNonArmsLengthChecks(prescribed_amounts(), CLASSES, SALES_TAX_RATE, CHECKED)


def vehicle(
    additions: str,
    market: str = "50000",
    seller: str = "60000",
    *,
    answer: int = 1,
    number: str = "10.1",
) -> dict[Any, Any]:
    """A Part B row of the class `number` with `additions`, answered `answer` as bought from a
    non-arm's-length person, with its fair market value `market` and the seller's cost `seller`."""
    record = part_b_row(additions=additions)
    record[CCA_CLASS_NUMBER] = D(number)
    record[CCA_VEHICLE_FROM_NON_ARMS_LENGTH] = answer
    record[CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE] = D(market)
    record[CCA_VEHICLE_SELLER_COST] = D(seller)
    return record


def run(*rows: dict[Any, Any], rate: str = "13") -> Any:
    """The result for `rows` at the sales tax rate `rate`, as the `CapabilityResult`."""
    classes_artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    return capability().compute((classes_artifact, Artifact(SALES_TAX_RATE, D(rate))))


def checked(*rows: dict[Any, Any], rate: str = "13") -> RecordList:
    (output,) = run(*rows, rate=rate).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def test_additions_equal_to_the_limit_when_it_is_the_least_pass_unchanged() -> None:
    passing = vehicle(LIMIT_2025, market="50000", seller="60000")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_additions_equal_to_the_fair_market_value_when_it_is_the_least_pass() -> None:
    assert len(checked(vehicle("30000", market="30000", seller="40000")).records) == 1


def test_additions_equal_to_the_sellers_cost_when_it_is_the_least_pass() -> None:
    assert len(checked(vehicle("25000.50", market="30000", seller="25000.50")).records) == 1


def test_additions_above_the_least_are_refused_naming_the_item_and_the_three_amounts() -> None:
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(vehicle("42940.00", market="30000", seller="40000"))

    assert str(error.value) == (
        "item 1: additions (42940.00) of a vehicle bought from a non-arm's-length person are not "
        "the least of its fair market value (30000.00), the limit with tax (42940.00) at a sales "
        "tax rate of 13% and the seller's cost (40000.00), which is 30000.00"
    )


def test_additions_below_the_least_are_refused_too() -> None:
    # The form has the filer enter the least of the three, not any amount at or under it.
    with pytest.raises(InvalidRecordError, match=r"which is 30000\.00"):
        run(vehicle("29999.99", market="30000", seller="40000"))


def test_the_limit_with_tax_follows_the_callers_rate() -> None:
    # $38,000 at 5 percent (GST only) is $39,900.
    assert len(checked(vehicle("39900.00"), rate="5").records) == 1
    with pytest.raises(InvalidRecordError, match=r"limit with tax \(39900\.00\)"):
        run(vehicle("42940.00"), rate="5")


def test_a_row_not_answered_as_bought_from_such_a_person_is_not_checked() -> None:
    result = run(vehicle("12345.67", answer=0))

    assert len(checked(vehicle("12345.67", answer=0)).records) == 1
    (line,) = result.trace
    assert line.applied is False
    assert line.limit == D("0")


def test_a_row_with_no_additions_is_not_checked() -> None:
    (line,) = run(vehicle("0")).trace

    assert line.applied is False


def test_a_row_of_another_class_is_not_checked() -> None:
    (line,) = run(vehicle("12345.67", number="10")).trace

    assert line.applied is False


def test_an_answer_other_than_0_or_1_is_refused() -> None:
    with pytest.raises(
        InvalidRecordError, match="item 1: bought from a non-arm's-length person is 2"
    ):
        run(vehicle(LIMIT_2025, answer=2))


def test_a_refused_row_is_named_by_its_position_in_the_list() -> None:
    with pytest.raises(InvalidRecordError, match="item 2"):
        run(vehicle(LIMIT_2025), vehicle("1", market="50000"))


def test_a_missing_prescribed_amount_for_the_tax_year_is_refused() -> None:
    without_2025 = CcaVehicleNonArmsLengthChecks(
        prescribed_amounts(rows=((2026, "40000"),)), CLASSES, SALES_TAX_RATE, CHECKED
    )
    classes_artifact = Artifact(CLASSES, RecordList(CLASSES.fields, [vehicle(LIMIT_2025)]))

    with pytest.raises(InvalidRecordError, match="no prescribed amount for 2025"):
        without_2025.compute((classes_artifact, Artifact(SALES_TAX_RATE, D("13"))))


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_row_gives_one_line_by_position_with_its_figures() -> None:
    result = run(vehicle(LIMIT_2025), vehicle("5", answer=0), vehicle("0"))

    lines = result.trace
    assert all(isinstance(line, CcaVehicleNonArmsLengthCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2, 3]
    assert lines[0] == CcaVehicleNonArmsLengthCheckLine(
        CHECKED, 1, True, D(LIMIT_2025), D("50000"), D(LIMIT_2025), D("60000"), D(LIMIT_2025)
    )
    assert lines[1] == CcaVehicleNonArmsLengthCheckLine(
        CHECKED, 2, False, D("5"), D("0"), D("0"), D("0"), D("0")
    )
    assert lines[2].applied is False


def test_a_check_line_amount_is_the_additions_as_entered() -> None:
    (line,) = run(vehicle(LIMIT_2025)).trace

    assert line.amount == D(LIMIT_2025)
    assert line.output_kind is CHECKED


def test_the_output_holds_the_same_fields_as_the_classes_in_the_callers_order() -> None:
    output = checked(vehicle(LIMIT_2025), vehicle("7", number="10"))

    assert output.fields == CHECKED.fields == CLASSES.fields
    assert [record[CCA_ADDITIONS] for record in output.records] == [D(LIMIT_2025), D("7")]


def test_is_registered_as_ca_cca_vehicle_non_arms_length_checks() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/cca_vehicle_non_arms_length_checks")
        is CcaVehicleNonArmsLengthChecks
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_vehicle_non_arms_length_checks" in ca_capabilities.__all__
    assert (
        ca_capabilities.cca_vehicle_non_arms_length_checks.CcaVehicleNonArmsLengthChecks
        is CcaVehicleNonArmsLengthChecks
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES, SALES_TAX_RATE})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaVehicleNonArmsLengthChecks)
    assert "produces" not in vars(CcaVehicleNonArmsLengthChecks)


def test_declares_its_parameter_and_its_slots() -> None:
    assert CcaVehicleNonArmsLengthChecks.PARAMETERS == {"prescribed_amounts": YEAR_AMOUNTS}
    assert CcaVehicleNonArmsLengthChecks.CONSUMES == {
        "classes": RecordList,
        "sales_tax_rate": Decimal,
    }
    assert CcaVehicleNonArmsLengthChecks.PRODUCES == {"output": RecordList}
    assert list(CcaVehicleNonArmsLengthChecks.CONSUMES) == ["classes", "sales_tax_rate"]


def test_its_slots_are_read_only() -> None:
    for each in (CcaVehicleNonArmsLengthChecks.CONSUMES, CcaVehicleNonArmsLengthChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaVehicleNonArmsLengthChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaVehicleNonArmsLengthChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaVehicleNonArmsLengthChecks(
        prescribed_amounts=prescribed_amounts(),
        classes=CLASSES,
        sales_tax_rate=SALES_TAX_RATE,
        output=CHECKED,
    )

    assert wired.consumes == frozenset({CLASSES, SALES_TAX_RATE})


def test_needs_the_prescribed_amounts() -> None:
    with pytest.raises(TypeError):
        CcaVehicleNonArmsLengthChecks(  # type: ignore[call-arg]
            classes=CLASSES, sales_tax_rate=SALES_TAX_RATE, output=CHECKED
        )


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaVehicleNonArmsLengthChecks.*'output'"):
        CcaVehicleNonArmsLengthChecks(
            prescribed_amounts(),
            CLASSES,
            SALES_TAX_RATE,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )
