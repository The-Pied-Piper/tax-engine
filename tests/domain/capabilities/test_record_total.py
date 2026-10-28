"""Unit tests for the RecordTotal capability (`core/record_total`), with made-up kinds.

Its slots: no parameter slot, one consumed slot `records` (a record list whose kind has exactly
one field, an amount) and one produced slot `output`. It adds that field over the records in
order, exactly, with no rounding (it has no dataset); an empty list totals 0. It records one
`RecordTotalLine` naming the field and each record's amount in order. A list kind with more than
one field, or whose one field is itself a record list, is refused when the capability is built.
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
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.domain.trace import RecordTotalLine

D = Decimal

AMOUNT = ArtifactKind("ex/item_amount", Decimal)
COUNT = ArtifactKind("ex/item_count", int)
ITEMS = RecordListKind("ex/items", fields=(AMOUNT,))
TWO_FIELDS = RecordListKind("ex/pairs", fields=(AMOUNT, COUNT))
COUNTS_ONLY = RecordListKind("ex/counts", fields=(COUNT,))
TOTAL = ArtifactKind("ex/items_total", Decimal)


def capability() -> RecordTotal:
    return RecordTotal(records=ITEMS, output=TOTAL)


def items(*amounts: str) -> Artifact[Any]:
    return Artifact(ITEMS, RecordList(ITEMS.fields, [{AMOUNT: D(a)} for a in amounts]))


def total_of(*amounts: str) -> Decimal:
    (artifact,) = capability().compute((items(*amounts),)).outputs
    assert artifact.kind == TOTAL
    assert isinstance(artifact.value, Decimal)
    return artifact.value


def test_is_registered_as_core_record_total() -> None:
    assert CapabilityRegistry.shared().get("core/record_total") is RecordTotal


def test_is_exported_from_the_capabilities_package() -> None:
    assert "record_total" in core.__all__
    assert core.record_total.RecordTotal is RecordTotal


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ITEMS})
    assert capability().produces == frozenset({TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RecordTotal)
    assert "produces" not in vars(RecordTotal)


def test_declares_its_slots() -> None:
    assert RecordTotal.PARAMETERS == {}
    assert RecordTotal.CONSUMES == {"records": RecordList}
    assert RecordTotal.PRODUCES == {"output": Decimal}
    assert not RecordTotal.is_list_slot("records")


def test_its_slots_are_read_only() -> None:
    for slots in (RecordTotal.PARAMETERS, RecordTotal.CONSUMES, RecordTotal.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        RecordTotal(ITEMS, TOTAL, object())  # type: ignore[call-arg]


# --- building ---------------------------------------------------------------------------------


def test_rejects_an_amount_kind_for_its_records() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordTotal.*'records'"):
        RecordTotal(records=AMOUNT, output=TOTAL)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordTotal.*'output'"):
        RecordTotal(records=ITEMS, output=ITEMS)  # type: ignore[arg-type]


def test_rejects_a_list_kind_of_more_than_one_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordTotal.*'records'"):
        RecordTotal(records=TWO_FIELDS, output=TOTAL)


def test_rejects_a_list_kind_whose_one_field_is_a_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordTotal.*'records'"):
        RecordTotal(records=COUNTS_ONLY, output=TOTAL)


def test_rejects_a_list_kind_whose_one_field_is_a_record_list() -> None:
    inner = RecordListKind("ex/inner", fields=(AMOUNT,))
    nested = RecordListKind("ex/nested", fields=(inner,))

    with pytest.raises(InvalidCapabilityError, match="RecordTotal.*'records'"):
        RecordTotal(records=nested, output=TOTAL)


# --- computing --------------------------------------------------------------------------------


def test_no_records_total_zero() -> None:
    assert total_of() == D("0")


def test_one_record_is_its_own_total() -> None:
    assert total_of("24000") == D("24000")


def test_records_add_up_with_cents() -> None:
    assert total_of("24000", "6000", "1250.75") == D("31250.75")


def test_a_negative_amount_is_added_as_it_is() -> None:
    assert total_of("100", "-30") == D("70")


def test_the_total_is_exact_and_never_rounded() -> None:
    assert str(total_of("1000.005", "0.001")) == "1000.006"
    assert total_of("0.1", "0.2") == D("0.3")


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((items("1", "2"),))

    assert result.outputs == (Artifact(TOTAL, D("3")),)


def test_a_missing_records_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_records_one_trace_line_naming_the_field_and_each_amount_in_order() -> None:
    result = capability().compute((items("24000", "6000"),))

    assert result.trace == (
        RecordTotalLine(
            output=TOTAL, field=AMOUNT, amounts=(D("24000"), D("6000")), total=D("30000")
        ),
    )


def test_an_empty_list_records_a_line_with_no_amounts() -> None:
    result = capability().compute((items(),))

    assert result.trace == (RecordTotalLine(output=TOTAL, field=AMOUNT, amounts=(), total=D("0")),)


def test_the_trace_renders_one_item_per_record_then_the_total() -> None:
    result = capability().compute((items("24000", "6000"),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "items_total: item 1 item_amount 24000 + item 2 item_amount 6000 = 30000",
    )


def test_the_trace_for_no_records_says_no_items() -> None:
    result = capability().compute((items(),))

    assert EnglishTraceRenderer().render_all(result.trace) == ("items_total: no items = 0",)


def test_rejects_a_plain_kind_of_record_lists_as_records() -> None:
    plain = ArtifactKind("ex/plain_list", RecordList)

    with pytest.raises(InvalidCapabilityError, match=r"RecordTotal.*'records'"):
        RecordTotal(records=plain, output=TOTAL)  # type: ignore[arg-type]
