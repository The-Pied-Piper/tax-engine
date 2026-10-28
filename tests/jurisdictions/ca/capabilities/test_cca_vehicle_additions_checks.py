"""Unit tests for the CcaVehicleAdditionsChecks capability (`ca/cca_vehicle_additions_checks`), the
check of the cost of additions of a Class 10.1 passenger vehicle against its limit, for the CCA
table of Form T2125 Area A (and T2042 and T2121, which share the table).

Guide T4002 2025, "Class 10.1 (30%)": "Include your passenger vehicle in Class 10.1 if you bought it
in 2025 and it cost more than $38,000 before tax. List each Class 10.1 vehicle separately. The
capital cost limits of a Class 10.1 passenger vehicle are the following prescribed amounts: ...
$38,000 for vehicles acquired in 2025, plus the GST/HST or PST." and "Use the GST rate of 5% and the
appropriate PST rate for your province or territory. If your province is a participating province,
use the appropriate HST rate."

The limit of a row is the prescribed amount of the tax year (the additions of the year are the
vehicles acquired in it) plus the same amount times the consumed `sales_tax_rate`, in
percent, rounded
once with the dataset's rule. Additions above the limit are refused (`InvalidRecordError`, naming
the item, the additions and the limit); additions equal to the limit pass. A Class 10.1 row with no
additions (a vehicle owned from the previous year) and a row of another class are not checked.

Its slots: one parameter, `prescribed_amounts` (a `year_amounts` dataset), two consumed slots,
`classes` (a record list of the Area A rows) and `sales_tax_rate` (the caller's rate, in
percent), and
one produced slot, `output`, a record list of the same fields. It records one
`CcaVehicleAdditionsCheckLine` for each row, by position, whether it was checked, its additions and
its limit (0 when it was not checked).
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
from tax_calculator.jurisdictions.ca.capabilities.cca_vehicle_additions_checks import (
    CcaVehicleAdditionsChecks,
)
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_CCA_CLASSES,
    BUSINESS_CCA_CLASSES_CHECKED,
    BUSINESS_VEHICLE_SALES_TAX_RATE,
    CCA_ADDITIONS,
    CCA_CLASS_NUMBER,
    CCA_UCC_AT_START,
)
from tax_calculator.jurisdictions.ca.trace import CcaVehicleAdditionsCheckLine
from tests.jurisdictions.ca.capabilities.cca_vehicle_proceeds import (
    CcaRow,
    prescribed_amounts,
    row,
)

D = Decimal
CLASSES: RecordListKind = BUSINESS_CCA_CLASSES
CHECKED: RecordListKind = BUSINESS_CCA_CLASSES_CHECKED
SALES_TAX_RATE = BUSINESS_VEHICLE_SALES_TAX_RATE

# Guide T4002 2025: $38,000 for a vehicle acquired in 2025, plus 13 percent (the caller's rate)
# is $42,940, the limit of Vivienne's Class 10.1 vehicle (her $44,070 with tax is refused).
LIMIT_2025 = "42940.00"


def capability() -> CcaVehicleAdditionsChecks:
    return CcaVehicleAdditionsChecks(prescribed_amounts(), CLASSES, SALES_TAX_RATE, CHECKED)


def run(*rows: CcaRow, rate: str = "13") -> Any:
    """The result for `rows` at the sales tax rate `rate`, as the `CapabilityResult`."""
    classes_artifact = Artifact(CLASSES, RecordList(CLASSES.fields, list(rows)))
    rate_artifact = Artifact(SALES_TAX_RATE, D(rate))
    return capability().compute((classes_artifact, rate_artifact))


def checked(*rows: CcaRow, rate: str = "13") -> RecordList:
    (output,) = run(*rows, rate=rate).outputs
    assert output.kind is CHECKED
    value = output.value
    assert isinstance(value, RecordList)
    return value


def vehicle(additions: str, *, number: str = "10.1", ucc_at_start: str = "0") -> CcaRow:
    """An Area A row of the class `number` with `additions` (the vehicle is bought in the year)."""
    return row(number, ucc_at_start=ucc_at_start, additions=additions)


def test_a_class_10_1_row_with_additions_at_the_limit_passes_unchanged() -> None:
    # Vivienne's first vehicle at the capped amount the form asks for (Guide T4002 2025).
    passing = vehicle("42940.00")

    records = checked(passing).records

    assert len(records) == 1
    assert {field: records[0][field] for field in CHECKED.fields} == {
        field: passing[field] for field in CHECKED.fields
    }


def test_a_class_10_1_row_with_additions_above_the_limit_is_refused_naming_the_item() -> None:
    # Vivienne's $44,070 (the vehicle with its tax) entered in column 3 of Class 10.1 is refused.
    with pytest.raises(InvalidRecordError, match="item 1") as error:
        run(vehicle("44070.00"))

    assert str(error.value) == (
        "item 1: additions (44070.00) are more than the Class 10.1 limit with tax (42940.00) "
        "at a sales tax rate of 13%, which is GST plus PST, or HST"
    )


def test_a_rate_of_zero_gives_the_printed_amount_as_the_limit() -> None:
    assert len(checked(vehicle("38000.00"), rate="0").records) == 1
    with pytest.raises(InvalidRecordError, match=r"limit with tax \(38000\.00\)"):
        run(vehicle("38000.01"), rate="0")


def test_the_tax_on_the_limit_is_rounded_once_to_the_cent_half_up() -> None:
    # 38000 x 13.00125% = 4940.475, rounded to 4940.48.
    assert len(checked(vehicle("42940.48"), rate="13.00125").records) == 1
    with pytest.raises(InvalidRecordError, match=r"limit with tax \(42940\.48\)"):
        run(vehicle("42940.49"), rate="13.00125")


def test_a_cent_above_the_limit_is_refused() -> None:
    with pytest.raises(InvalidRecordError, match="item 1"):
        run(vehicle("42940.01"))


def test_a_cent_under_the_limit_passes() -> None:
    records = checked(vehicle("42939.99")).records

    assert records[0][CCA_ADDITIONS] == D("42939.99")


def test_the_limit_is_the_prescribed_amount_plus_the_rate_on_it() -> None:
    # $38,000 at 5 percent (GST only) is $39,900: that amount passes and a cent more is refused.
    assert checked(vehicle("39900.00"), rate="5").records[0][CCA_ADDITIONS] == D("39900.00")
    with pytest.raises(InvalidRecordError, match=r"\(39900\.00\)"):
        run(vehicle("39900.01"), rate="5")


def test_a_refused_row_is_named_by_its_position_in_the_list() -> None:
    with pytest.raises(InvalidRecordError, match="item 2") as error:
        run(vehicle("20000.00"), vehicle("44070.00"))

    assert "(44070.00)" in str(error.value)


def test_a_class_10_1_row_with_no_additions_is_not_checked() -> None:
    # A vehicle owned from the previous year (UCC at the start, no additions) needs no check, even
    # with a UCC above the limit.
    result = run(vehicle("0", ucc_at_start="50000.00"))

    assert len(checked(vehicle("0", ucc_at_start="50000.00")).records) == 1
    (line,) = result.trace
    assert line.applied is False
    assert line.limit == D("0")


def test_a_row_of_another_class_is_not_checked_whatever_its_additions() -> None:
    # Class 10 is not the passenger vehicle's class 10.1: its additions are not limited here.
    passing = vehicle("60000.00", number="10")

    records = checked(passing).records

    assert records[0][CCA_ADDITIONS] == D("60000.00")
    (line,) = run(passing).trace
    assert line.applied is False


def test_a_missing_prescribed_amount_for_the_tax_year_is_refused() -> None:
    # The dataset has no row for 2025 (its only row is from 2026): the limit cannot be found.
    capability_without_2025 = CcaVehicleAdditionsChecks(
        prescribed_amounts(rows=((2026, "40000"),)), CLASSES, SALES_TAX_RATE, CHECKED
    )
    classes_artifact = Artifact(CLASSES, RecordList(CLASSES.fields, [vehicle("42940.00")]))

    with pytest.raises(InvalidRecordError, match="no prescribed amount for 2025"):
        capability_without_2025.compute((classes_artifact, Artifact(SALES_TAX_RATE, D("13"))))


def test_an_empty_list_passes_with_no_lines() -> None:
    result = run()

    assert len(checked().records) == 0
    assert result.trace == ()


def test_each_row_gives_one_line_by_position_with_its_additions_and_limit() -> None:
    result = run(vehicle("42940.00"), vehicle("31640.00", number="10"), vehicle("0"))

    lines = result.trace
    assert all(isinstance(line, CcaVehicleAdditionsCheckLine) for line in lines)
    assert [line.position for line in lines] == [1, 2, 3]
    assert lines[0] == CcaVehicleAdditionsCheckLine(CHECKED, 1, True, D("42940.00"), D(LIMIT_2025))
    assert lines[1] == CcaVehicleAdditionsCheckLine(CHECKED, 2, False, D("31640.00"), D("0"))
    assert lines[2] == CcaVehicleAdditionsCheckLine(CHECKED, 3, False, D("0"), D("0"))


def test_a_check_line_amount_is_the_additions_as_entered() -> None:
    (line,) = run(vehicle("42940.00")).trace

    assert line.amount == D("42940.00")
    assert line.output_kind is CHECKED


def test_the_output_holds_the_same_fields_as_the_classes_in_the_callers_order() -> None:
    first = vehicle("42940.00")
    second = vehicle("31640.00", number="10")

    output = checked(first, second)

    assert output.fields == CHECKED.fields == CLASSES.fields
    assert [record[CCA_CLASS_NUMBER] for record in output.records] == [D("10.1"), D("10")]


def test_is_registered_as_ca_cca_vehicle_additions_checks() -> None:
    assert (
        CapabilityRegistry.shared().get("ca/cca_vehicle_additions_checks")
        is CcaVehicleAdditionsChecks
    )


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "cca_vehicle_additions_checks" in ca_capabilities.__all__
    assert (
        ca_capabilities.cca_vehicle_additions_checks.CcaVehicleAdditionsChecks
        is CcaVehicleAdditionsChecks
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLASSES, SALES_TAX_RATE})
    assert capability().produces == frozenset({CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CcaVehicleAdditionsChecks)
    assert "produces" not in vars(CcaVehicleAdditionsChecks)


def test_declares_its_parameter_and_its_slots() -> None:
    assert CcaVehicleAdditionsChecks.PARAMETERS == {"prescribed_amounts": YEAR_AMOUNTS}
    assert CcaVehicleAdditionsChecks.CONSUMES == {"classes": RecordList, "sales_tax_rate": Decimal}
    assert CcaVehicleAdditionsChecks.PRODUCES == {"output": RecordList}
    assert list(CcaVehicleAdditionsChecks.CONSUMES) == ["classes", "sales_tax_rate"]


def test_its_slots_are_read_only() -> None:
    for each in (CcaVehicleAdditionsChecks.CONSUMES, CcaVehicleAdditionsChecks.PRODUCES):
        assert isinstance(each, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, each)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CcaVehicleAdditionsChecks.CONSUMES, Mapping[str, type])
    assert_type(CcaVehicleAdditionsChecks.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CcaVehicleAdditionsChecks(
        prescribed_amounts=prescribed_amounts(),
        classes=CLASSES,
        sales_tax_rate=SALES_TAX_RATE,
        output=CHECKED,
    )

    assert wired.consumes == frozenset({CLASSES, SALES_TAX_RATE})


def test_needs_the_prescribed_amounts() -> None:
    with pytest.raises(TypeError):
        CcaVehicleAdditionsChecks(  # type: ignore[call-arg]
            classes=CLASSES, sales_tax_rate=SALES_TAX_RATE, output=CHECKED
        )


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaVehicleAdditionsChecks.*'output'"):
        CcaVehicleAdditionsChecks(
            prescribed_amounts(),
            CLASSES,
            SALES_TAX_RATE,
            ArtifactKind("ex/other_amount", Decimal),  # type: ignore[arg-type]
        )


def test_its_contract_names_the_checked_kind_not_the_adjusted_kind() -> None:
    # The checks run before the proceeds adjustment, so the list they produce is the checked one.
    assert CHECKED.identifier == "ca/business_cca_classes_checked"
    assert CHECKED.identifier != "ca/business_cca_classes_adjusted"
    assert CCA_UCC_AT_START in CHECKED.fields
