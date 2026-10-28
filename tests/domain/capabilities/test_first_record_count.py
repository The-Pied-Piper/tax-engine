"""Unit tests for the FirstRecordCount capability (`core/first_record_count`), with made-up kinds.

Its slots: no parameter slot, one consumed slot `records` (a record list whose kind has exactly
one count field) and one produced slot `output`, a count. It takes the count in the first record
of the list (position 0, fixed); an empty list is refused. It records one `FirstRecordCountLine`
naming the field, the value and how many records the list has. A list kind without exactly one
count field is refused when the capability is built. It reads a form's export of one count
(`<form>.<export>`) as that one count.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

import tax_calculator.domain.capabilities as core
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.first_record_count import FirstRecordCount
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    UnknownRegistrationError,
    ValidationError,
)
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import FirstRecordCountLine

D = Decimal

AMOUNT = ArtifactKind("ex/item_amount", Decimal)
COUNT = ArtifactKind("ex/item_count", int)
FLAGS = RecordListKind("ex/flags", fields=(COUNT,))
ITEMS = RecordListKind("ex/items", fields=(AMOUNT,))
TWO_FIELDS = RecordListKind("ex/pairs", fields=(AMOUNT, COUNT))
NO_FIELDS = RecordListKind("ex/blanks", fields=())
FIRST_FLAG = ArtifactKind("ex/first_flag", int)


def capability() -> FirstRecordCount:
    return FirstRecordCount(records=FLAGS, output=FIRST_FLAG)


def flags(*counts: int) -> Artifact[Any]:
    return Artifact(FLAGS, RecordList(FLAGS.fields, [{COUNT: c} for c in counts]))


def first_of(*counts: int) -> int:
    (artifact,) = capability().compute((flags(*counts),)).outputs
    assert artifact.kind == FIRST_FLAG
    assert isinstance(artifact.value, int)
    return artifact.value


def test_is_registered_as_core_first_record_count() -> None:
    assert CapabilityRegistry.shared().get("core/first_record_count") is FirstRecordCount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "first_record_count" in core.__all__
    assert core.first_record_count.FirstRecordCount is FirstRecordCount


def test_the_count_total_capability_is_gone() -> None:
    assert "record_count_total" not in core.__all__
    with pytest.raises(UnknownRegistrationError):
        CapabilityRegistry.shared().get("core/record_count_total")


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({FLAGS})
    assert capability().produces == frozenset({FIRST_FLAG})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(FirstRecordCount)
    assert "produces" not in vars(FirstRecordCount)


def test_declares_its_slots() -> None:
    assert FirstRecordCount.PARAMETERS == {}
    assert FirstRecordCount.CONSUMES == {"records": RecordList}
    assert not FirstRecordCount.is_list_slot("records")
    assert set(FirstRecordCount.PRODUCES) == {"output"}


def test_its_slots_are_read_only() -> None:
    for slots in (
        FirstRecordCount.PARAMETERS,
        FirstRecordCount.CONSUMES,
        FirstRecordCount.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset_and_no_index() -> None:
    with pytest.raises(TypeError):
        FirstRecordCount(FLAGS, FIRST_FLAG, object())  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        FirstRecordCount(records=FLAGS, output=FIRST_FLAG, index=0)  # type: ignore[call-arg]


# --- building ---------------------------------------------------------------------------------


def test_builds_for_a_count_field() -> None:
    assert capability().produces == frozenset({FIRST_FLAG})


def test_rejects_a_count_kind_for_its_records() -> None:
    with pytest.raises(InvalidCapabilityError, match="FirstRecordCount.*'records'"):
        FirstRecordCount(records=COUNT, output=FIRST_FLAG)  # type: ignore[arg-type]


def test_rejects_a_plain_kind_of_record_lists_as_records() -> None:
    plain = ArtifactKind("ex/plain_list", RecordList)

    with pytest.raises(InvalidCapabilityError, match=r"FirstRecordCount.*'records'"):
        FirstRecordCount(records=plain, output=FIRST_FLAG)  # type: ignore[arg-type]


def test_rejects_a_list_kind_of_an_amount_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="FirstRecordCount.*'records'"):
        FirstRecordCount(records=ITEMS, output=FIRST_FLAG)


def test_rejects_a_list_kind_of_more_than_one_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="FirstRecordCount.*'records'"):
        FirstRecordCount(records=TWO_FIELDS, output=FIRST_FLAG)


def test_rejects_a_list_kind_of_no_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="FirstRecordCount.*'records'"):
        FirstRecordCount(records=NO_FIELDS, output=FIRST_FLAG)


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="FirstRecordCount.*'output'"):
        FirstRecordCount(records=FLAGS, output=FLAGS)  # type: ignore[arg-type]


# --- computing --------------------------------------------------------------------------------


def test_one_record_is_its_own_first_value() -> None:
    assert first_of(1) == 1


def test_the_first_record_of_several_is_taken_not_the_sum_or_the_last() -> None:
    assert first_of(3, 0, 4) == 3


def test_a_first_record_of_zero_is_zero_whatever_follows() -> None:
    assert first_of(0, 5, 6) == 0


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((flags(2, 5),))

    assert result.outputs == (Artifact(FIRST_FLAG, 2),)
    assert type(result.outputs[0].value) is int


def test_an_empty_list_is_refused() -> None:
    with pytest.raises(ValidationError):
        capability().compute((flags(),))


def test_a_missing_records_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_records_one_trace_line_naming_the_field_the_value_and_the_record_count() -> None:
    result = capability().compute((flags(4, 0, 2),))

    assert result.trace == (
        FirstRecordCountLine(output=FIRST_FLAG, field=COUNT, value=4, record_count=3),
    )


def test_the_trace_renders_the_first_item_and_how_many_there_are() -> None:
    result = capability().compute((flags(1, 0),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "first_flag: item 1 item_count 1 of 2 items",
    )


def test_the_trace_for_one_record_renders_the_count_of_items() -> None:
    result = capability().compute((flags(0),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "first_flag: item 1 item_count 0 of 1 items",
    )
