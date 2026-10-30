"""Unit tests for the T776 Areas B and C additions total (`ca/rental_additions_total`).

Form T776 Area B "Equipment additions in the year" and Area C "Building additions in the year": for
each addition, "Column 5: Rental portion (column 3 minus column 4)", and then "Line 9925: Total
equipment additions in the year: Total of column 5" or "Line 9927: Total building additions in the
year: Total of column 5". The capability has no parameter slot, one consumed slot `additions` (a
record list with a record for each addition: the class number, column 3 "Total cost" and column 4
"Personal portion (if applicable)") and one produced slot `total`. For each addition, column 5 is
the total cost less the personal portion; a personal portion above the total cost is not capped but
an input error, `InputAboveBoundError`, naming the item by its position from 1. The output is the
sum of every addition's column 5, exact: it never rounds. It records one `RentalAdditionLine` for
each addition, named by its position, and then one `ItemsTotalLine`.

The figures are the form's own: Teresa's refrigerator, the equipment of Class 8, is in Area B.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca.capabilities as canada
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.rental_additions_total import RentalAdditionsTotal
from tax_engine.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    RENTAL_ADDITION_PERSONAL_PORTION,
    RENTAL_ADDITION_TOTAL_COST,
    RENTAL_BUILDING_ADDITIONS,
    RENTAL_EQUIPMENT_ADDITIONS,
)
from tax_engine.jurisdictions.ca.trace import RentalAdditionLine

D = Decimal

# Made up for this test and not registered: the total the capability produces.
TOTAL = ArtifactKind("ex/rental_additions_total", Decimal)
MESSAGE = r"the personal portion \(250\) is above the total cost \(200\)"


def addition(class_number: str = "8", cost: str = "0", personal: str = "0") -> dict[Any, Any]:
    return {
        CCA_CLASS_NUMBER: D(class_number),
        RENTAL_ADDITION_TOTAL_COST: D(cost),
        RENTAL_ADDITION_PERSONAL_PORTION: D(personal),
    }


def additions(
    *rows: dict[Any, Any], kind: RecordListKind = RENTAL_EQUIPMENT_ADDITIONS
) -> Artifact[Any]:
    return Artifact(kind, RecordList(kind.fields, rows))


def capability(kind: RecordListKind = RENTAL_EQUIPMENT_ADDITIONS) -> RentalAdditionsTotal:
    return RentalAdditionsTotal(kind, TOTAL)


def total(*rows: dict[Any, Any], kind: RecordListKind = RENTAL_EQUIPMENT_ADDITIONS) -> Decimal:
    (output,) = capability(kind).compute((additions(*rows, kind=kind),)).outputs
    assert output.kind == TOTAL
    value: Decimal = output.value
    return value


def test_is_registered_as_ca_rental_additions_total() -> None:
    assert tax_engine.jurisdictions.ca.capabilities is canada
    assert CapabilityRegistry.shared().get("ca/rental_additions_total") is RentalAdditionsTotal


def test_is_exported_from_the_canada_capabilities_package() -> None:
    assert canada.NAMESPACE == "ca"
    assert "rental_additions_total" in canada.__all__
    assert canada.rental_additions_total.RentalAdditionsTotal is RentalAdditionsTotal


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({RENTAL_EQUIPMENT_ADDITIONS})
    assert capability().produces == frozenset({TOTAL})
    assert "consumes" not in vars(RentalAdditionsTotal)
    assert "produces" not in vars(RentalAdditionsTotal)


def test_declares_its_slots() -> None:
    assert RentalAdditionsTotal.PARAMETERS == {}
    assert RentalAdditionsTotal.CONSUMES == {"additions": RecordList}
    assert RentalAdditionsTotal.PRODUCES == {"total": Decimal}
    assert not RentalAdditionsTotal.is_list_slot("additions")
    for slots in (
        RentalAdditionsTotal.PARAMETERS,
        RentalAdditionsTotal.CONSUMES,
        RentalAdditionsTotal.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(RentalAdditionsTotal.CONSUMES, Mapping[str, type])
    assert_type(RentalAdditionsTotal.PRODUCES, Mapping[str, type])


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RentalAdditionsTotal)
    assert "produces" not in vars(RentalAdditionsTotal)


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = RentalAdditionsTotal(additions=RENTAL_EQUIPMENT_ADDITIONS, total=TOTAL)

    (output,) = wired.compute((additions(addition("8", "1000")),)).outputs

    assert output == Artifact(TOTAL, D("1000"))


def test_takes_no_parameter_argument() -> None:
    with pytest.raises(TypeError):
        RentalAdditionsTotal(  # type: ignore[call-arg]
            RENTAL_EQUIPMENT_ADDITIONS, TOTAL, TOTAL
        )


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(RentalAdditionsTotal, "__type_params__", ())
    assert not getattr(RentalAdditionsTotal, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_no_additions_total_nothing() -> None:
    result = capability().compute((additions(),))

    assert result.outputs == (Artifact(TOTAL, D("0")),)
    assert result.trace == (ItemsTotalLine(output=TOTAL, items=(), total=D("0")),)


def test_teresas_refrigerator_is_its_full_cost_with_no_personal_portion() -> None:
    assert total(addition("8", "1000", "0")) == D("1000")


def test_the_rental_portion_is_the_cost_less_the_personal_portion() -> None:
    assert total(addition("8", "1000", "250")) == D("750")


def test_two_additions_add() -> None:
    assert total(addition("8", "1000", "250"), addition("50", "2500.50", "0.50")) == D("3250")


def test_a_personal_portion_equal_to_the_cost_gives_nothing() -> None:
    assert total(addition("8", "1000", "1000")) == D("0")


def test_refuses_a_personal_portion_above_the_cost_as_an_input_error_naming_the_item() -> None:
    with pytest.raises(InputAboveBoundError, match=rf"item 1: {MESSAGE}"):
        total(addition("8", "200", "250"))


def test_refuses_the_second_additions_personal_portion_naming_its_position() -> None:
    with pytest.raises(InputAboveBoundError, match=rf"item 2: {MESSAGE}"):
        total(addition("8", "1000", "0"), addition("8", "200", "250"))


def test_has_one_output() -> None:
    (output,) = capability().compute((additions(addition("8", "5")),)).outputs

    assert output == Artifact(TOTAL, D("5"))


def test_compute_is_repeatable() -> None:
    inputs = (additions(addition("8", "1000", "250")),)

    assert capability().compute(inputs) == capability().compute(inputs)


def test_works_with_the_building_additions_kind_too() -> None:
    rows = (addition("1", "300000", "0"), addition("1", "1000", "250"))

    assert total(*rows, kind=RENTAL_BUILDING_ADDITIONS) == D("300750")


# --- trace --------------------------------------------------------------------------------------


def test_the_last_trace_line_amount_is_the_output() -> None:
    result = capability().compute((additions(addition("8", "400"), addition("50", "500")),))

    assert result.trace[-1].amount == D("900")


def test_records_each_addition_by_its_position_then_the_total() -> None:
    rows = (addition("8", "1000", "0"), addition("50", "1000", "250"))

    result = capability().compute((additions(*rows),))

    assert result.trace == (
        RentalAdditionLine(
            output=TOTAL,
            position=1,
            class_number=D("8"),
            total_cost=D("1000"),
            personal_portion=D("0"),
            result=D("1000"),
        ),
        RentalAdditionLine(
            output=TOTAL,
            position=2,
            class_number=D("50"),
            total_cost=D("1000"),
            personal_portion=D("250"),
            result=D("750"),
        ),
        ItemsTotalLine(
            output=TOTAL,
            items=((1, D("1000")), (2, D("750"))),
            total=D("1750"),
        ),
    )


def test_refuses_a_money_kind_for_its_record_list() -> None:
    with pytest.raises(InvalidCapabilityError, match="RentalAdditionsTotal") as raised:
        RentalAdditionsTotal(ArtifactKind("ex/not_a_list", Decimal), TOTAL)  # type: ignore[arg-type]

    assert "'additions'" in str(raised.value)


def test_refuses_a_count_kind_for_its_total() -> None:
    with pytest.raises(InvalidCapabilityError, match="RentalAdditionsTotal") as raised:
        RentalAdditionsTotal(RENTAL_EQUIPMENT_ADDITIONS, ArtifactKind("ex/a_count", int))  # type: ignore[arg-type]

    assert "'total'" in str(raised.value)


def test_needs_its_record_list() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())
