"""Unit tests for the CountWithoutRecords capability (`ca/count_without_records`), made-up kinds.

It is a guard, the mirror of `CountAtLeast`. Its slots: two consumed single slots, `count` (an
`int` kind) and `records` (a record-list kind), one produced slot `output` (an `int` kind), no
parameter slots and no dataset. The output is the count, unchanged, when the count is 0 or the
record list holds no records. When the count is above 0 and the list holds at least one record, it
is an input error, `InputAboveBoundError` (an existing error), naming both kinds and their values.
It records one `CountWithoutRecordsLine`, and none when it raises.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    DomainError,
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import CountWithoutRecordsLine
from tax_engine.jurisdictions.ca.capabilities.count_without_records import CountWithoutRecords

D = Decimal

WIDGET_AMOUNT = ArtifactKind("ex/widget_amount", Decimal, non_negative=True)
COUNT = ArtifactKind("ex/widget_count", int)
RECORDS = RecordListKind("ex/widget_records", fields=(WIDGET_AMOUNT,))
OUTPUT = ArtifactKind("ex/widget_checked", int)
MONEY = ArtifactKind("ex/money", Decimal)


def capability() -> CountWithoutRecords:
    return CountWithoutRecords(COUNT, RECORDS, OUTPUT)


def records(*amounts: str) -> Artifact[RecordList]:
    """An `ex/widget_records` artifact of one record per amount, in order."""
    return Artifact(RECORDS, RecordList(RECORDS.fields, [{WIDGET_AMOUNT: D(a)} for a in amounts]))


def inputs(count: int, *amounts: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(COUNT, count), records(*amounts))


def compute(count: int, *amounts: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(count, *amounts)).outputs
    return output


def test_is_registered_as_ca_count_without_records() -> None:
    assert CapabilityRegistry.shared().get("ca/count_without_records") is CountWithoutRecords


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "count_without_records" in ca_capabilities.__all__
    assert ca_capabilities.count_without_records.CountWithoutRecords is CountWithoutRecords


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({COUNT, RECORDS})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CountWithoutRecords)
    assert "produces" not in vars(CountWithoutRecords)


def test_declares_its_slots() -> None:
    assert CountWithoutRecords.PARAMETERS == {}
    assert CountWithoutRecords.CONSUMES == {"count": int, "records": RecordList}
    assert CountWithoutRecords.PRODUCES == {"output": int}
    assert not CountWithoutRecords.is_list_slot("count")
    assert not CountWithoutRecords.is_list_slot("records")


def test_its_slots_are_read_only() -> None:
    for slots in (
        CountWithoutRecords.PARAMETERS,
        CountWithoutRecords.CONSUMES,
        CountWithoutRecords.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CountWithoutRecords.CONSUMES, Mapping[str, type])
    assert_type(CountWithoutRecords.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CountWithoutRecords.CONSUMES, CountWithoutRecords.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CountWithoutRecords(count=COUNT, records=RECORDS, output=OUTPUT)

    assert wired.compute(inputs(0)).outputs == (Artifact(OUTPUT, 0),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        CountWithoutRecords(COUNT, RECORDS, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [((COUNT, RECORDS, COUNT), ("'count'", "'output'"))],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[int], RecordListKind, ArtifactKind[int]], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords") as raised:
        CountWithoutRecords(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'count'"):
        CountWithoutRecords((COUNT,), RECORDS, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_money_kind_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'count'"):
        CountWithoutRecords(MONEY, RECORDS, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_its_records() -> None:
    # An `int` kind is not a record list, so the slot refuses it at wiring time.
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'records'"):
        CountWithoutRecords(COUNT, COUNT, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_money_kind_for_its_records() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'records'"):
        CountWithoutRecords(COUNT, MONEY, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'count'"):
        CountWithoutRecords(RECORDS, RECORDS, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_money_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountWithoutRecords.*'output'"):
        CountWithoutRecords(COUNT, RECORDS, MONEY)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CountWithoutRecords, "__type_params__", ())
    assert not getattr(CountWithoutRecords, "__parameters__", ())


# --- computing: the output is the count when the guard holds ------------------------------------


def test_a_zero_count_with_no_records_is_produced() -> None:
    output = compute(0)

    assert output == Artifact(OUTPUT, 0)
    assert type(output.value) is int


def test_a_zero_count_is_produced_whatever_the_records() -> None:
    assert compute(0, "1") == Artifact(OUTPUT, 0)
    assert compute(0, "1", "2") == Artifact(OUTPUT, 0)


def test_a_count_with_no_records_is_produced_unchanged() -> None:
    output = compute(3)

    assert output == Artifact(OUTPUT, 3)
    assert type(output.value) is int


def test_a_count_of_one_with_no_records_is_produced() -> None:
    assert compute(1) == Artifact(OUTPUT, 1)


def test_a_record_of_zero_amount_is_still_a_record_and_refuses_a_count() -> None:
    with pytest.raises(InputAboveBoundError):
        compute(1, "0")


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", int), 9)

    assert capability().compute((other, *inputs(4))).outputs == (Artifact(OUTPUT, 4),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_count"):
        capability().compute((records(),))


def test_a_missing_records_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_records"):
        capability().compute((Artifact(COUNT, 1),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs(3)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs(3)) == wired.compute(inputs(3))


# --- a count above 0 with a record is an input error --------------------------------------------


def test_a_count_with_a_record_is_an_input_above_bound_error() -> None:
    with pytest.raises(InputAboveBoundError):
        compute(1, "8000")


def test_a_count_with_several_records_is_an_input_above_bound_error() -> None:
    with pytest.raises(InputAboveBoundError):
        compute(2, "8000", "15000", "1")


def test_the_error_names_both_kinds_and_their_values() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(1, "8000")

    message = str(raised.value)
    assert "ex/widget_count" in message
    assert "ex/widget_records" in message
    assert "1" in message


def test_an_input_above_bound_error_is_a_domain_error() -> None:
    assert issubclass(InputAboveBoundError, DomainError)


def test_an_input_above_bound_error_is_not_an_input_below_bound_error() -> None:
    assert not issubclass(InputAboveBoundError, InputBelowBoundError)


def test_an_input_above_bound_error_is_not_a_wiring_error() -> None:
    assert not issubclass(InputAboveBoundError, InvalidCapabilityError)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_count_without_records_line_when_no_records() -> None:
    assert capability().compute(inputs(3)).trace == (
        CountWithoutRecordsLine(
            output=OUTPUT, count_kind=COUNT, count=3, records_kind=RECORDS, record_count=0
        ),
    )


def test_traces_the_record_count_when_the_count_is_zero() -> None:
    assert capability().compute(inputs(0, "1", "2")).trace == (
        CountWithoutRecordsLine(
            output=OUTPUT, count_kind=COUNT, count=0, records_kind=RECORDS, record_count=2
        ),
    )


def test_trace_amount_is_the_count() -> None:
    trace = capability().compute(inputs(3)).trace

    assert [line.amount for line in trace] == [Decimal(3)]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs(3)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
