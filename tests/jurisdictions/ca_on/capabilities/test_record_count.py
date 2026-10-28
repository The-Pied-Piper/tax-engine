"""Unit tests for the RecordCount capability (`ca-on/record_count`), with made-up kinds.

Form ON479 line 63260 is the "Number of eligible work placements" claimed. The capability consumes
a record list and produces the number of its records as a count (an `int` artifact), whatever the
records hold; an empty list gives 0. It has no dataset and records one `RecordCountLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

import pytest

import tax_calculator.jurisdictions.ca_on
import tax_calculator.jurisdictions.ca_on.capabilities
import tax_calculator.registrations
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import RecordCountLine
from tax_calculator.jurisdictions.ca_on.capabilities.record_count import RecordCount

D = Decimal

ITEM_AMOUNT = ArtifactKind("ex/item_amount", Decimal, non_negative=True)
ITEM_MONTHS = ArtifactKind("ex/item_months", int, non_negative=True)
ITEMS = RecordListKind("ex/items", fields=(ITEM_AMOUNT,))
TWO_FIELD_ITEMS = RecordListKind("ex/two_field_items", fields=(ITEM_AMOUNT, ITEM_MONTHS))
COUNT = ArtifactKind("ex/item_count", int, non_negative=True)


def capability(records: RecordListKind = ITEMS) -> RecordCount:
    return RecordCount(records=records, output=COUNT)


def items(*amounts: str) -> Artifact[RecordList]:
    """An `ex/items` artifact of one record per amount, in order."""
    return Artifact(ITEMS, RecordList(ITEMS.fields, [{ITEM_AMOUNT: D(a)} for a in amounts]))


def count_of(*amounts: str) -> int:
    (artifact,) = capability().compute((items(*amounts),)).outputs
    assert artifact.kind == COUNT
    value = artifact.value
    assert isinstance(value, int)
    return value


def test_is_registered_as_ca_on_record_count() -> None:
    assert (
        tax_calculator.registrations.CORE_PACKAGES
    )  # importing registrations imports the packages

    assert CapabilityRegistry.shared().get("ca-on/record_count") is RecordCount


def test_its_package_declares_the_ca_on_namespace_and_exports_the_module() -> None:
    package = tax_calculator.jurisdictions.ca_on.capabilities

    assert package.NAMESPACE == tax_calculator.jurisdictions.ca_on.NAMESPACE == "ca-on"
    assert "record_count" in package.__all__
    assert package.record_count.RecordCount is RecordCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ITEMS})
    assert capability().produces == frozenset({COUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RecordCount)
    assert "produces" not in vars(RecordCount)


def test_declares_its_slots() -> None:
    assert RecordCount.PARAMETERS == {}
    assert RecordCount.CONSUMES == {"records": RecordList}
    assert RecordCount.PRODUCES == {"output": int}
    assert not RecordCount.is_list_slot("records")


def test_its_slots_are_read_only() -> None:
    for slots in (RecordCount.PARAMETERS, RecordCount.CONSUMES, RecordCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        RecordCount(ITEMS, COUNT, object())  # type: ignore[call-arg]


def test_rejects_a_money_kind_for_its_records() -> None:
    other = ArtifactKind("ex/not_a_list", Decimal)

    with pytest.raises(InvalidCapabilityError, match="RecordCount.*'records'"):
        RecordCount(records=other, output=COUNT)  # type: ignore[arg-type]


def test_rejects_a_money_kind_for_its_output() -> None:
    other = ArtifactKind("ex/not_a_count", Decimal)

    with pytest.raises(InvalidCapabilityError, match="RecordCount.*'output'"):
        RecordCount(records=ITEMS, output=other)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordCount.*'output'"):
        RecordCount(records=ITEMS, output=TWO_FIELD_ITEMS)  # type: ignore[arg-type]


# --- computing --------------------------------------------------------------------------------


def test_an_empty_list_counts_zero() -> None:
    assert count_of() == 0


def test_one_record_counts_one() -> None:
    assert count_of("8000") == 1


def test_two_records_count_two() -> None:
    # The worked example's two work placements.
    assert count_of("8000", "15000") == 2


def test_many_records_count_each() -> None:
    assert count_of(*["1"] * 12) == 12


def test_equal_records_are_each_counted() -> None:
    assert count_of("8000", "8000", "8000") == 3


def test_a_record_of_zero_is_still_a_record() -> None:
    assert count_of("0", "0") == 2


def test_the_count_does_not_depend_on_the_values() -> None:
    assert count_of("1", "2") == count_of("100000.50", "0.01") == 2


def test_the_count_is_an_int_and_not_a_bool_or_decimal() -> None:
    assert type(count_of("8000")) is int
    assert type(count_of()) is int


def test_counts_records_of_a_list_with_several_fields() -> None:
    records = Artifact(
        TWO_FIELD_ITEMS,
        RecordList(
            TWO_FIELD_ITEMS.fields,
            [{ITEM_AMOUNT: D("1"), ITEM_MONTHS: 3}, {ITEM_AMOUNT: D("2"), ITEM_MONTHS: 4}],
        ),
    )

    result = capability(TWO_FIELD_ITEMS).compute((records,))

    assert result.outputs == (Artifact(COUNT, 2),)


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((items("8000", "15000"),))

    assert result.outputs == (Artifact(COUNT, 2),)


def test_records_one_trace_line_with_the_list_and_its_count() -> None:
    result = capability().compute((items("8000", "15000"),))

    assert result.trace == (RecordCountLine(output=COUNT, records=ITEMS, count=2),)


def test_records_one_trace_line_for_an_empty_list() -> None:
    result = capability().compute((items(),))

    assert result.trace == (RecordCountLine(COUNT, ITEMS, 0),)


def test_records_one_trace_line_whatever_the_number_of_records() -> None:
    for amounts in ((), ("1",), ("1", "2"), ("1", "2", "3", "4")):
        assert len(capability().compute((items(*amounts),)).trace) == 1


def test_its_trace_reads_in_english() -> None:
    result = capability().compute((items("8000", "15000"),))

    assert EnglishTraceRenderer().render_all(result.trace) == ("item_count: 2 items in items = 2",)


def test_its_trace_for_one_record_is_singular_in_english() -> None:
    result = capability().compute((items("8000"),))

    assert EnglishTraceRenderer().render_all(result.trace) == ("item_count: 1 item in items = 1",)


def test_its_trace_for_an_empty_list_says_no_items() -> None:
    result = capability().compute((items(),))

    assert EnglishTraceRenderer().render_all(result.trace) == ("item_count: no items in items = 0",)


def test_needs_its_list() -> None:
    with pytest.raises(MissingArtifactError, match="RecordCount"):
        capability().compute(())


def test_does_not_consume_anything_else() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("1"))

    result = capability().compute((other, items("8000")))

    assert result.outputs == (Artifact(COUNT, 1),)
