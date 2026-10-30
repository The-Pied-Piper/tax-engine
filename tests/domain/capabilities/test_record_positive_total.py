"""Unit tests for the RecordPositiveTotal capability (`core/record_positive_total`), with made-up
kinds.

Its slots: no parameter slot, one consumed slot `records` (a record list whose kind has exactly
one field, an amount) and one produced slot `output`. It adds the positive amounts over the records
in order, exactly, with no rounding (it has no dataset): a zero or negative amount counts 0, and an
empty list, or a list with no positive amount, totals 0. It records one `RecordPositiveTotalLine`
naming the field, each record's amount in order as read, and the total. A list kind with more than
one field, or whose one field is itself a record list, is refused when the capability is built.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

import tax_engine.domain.capabilities as core
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.record_positive_total import RecordPositiveTotal
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import RecordPositiveTotalLine

D = Decimal

AMOUNT = ArtifactKind("ex/item_amount", Decimal)
COUNT = ArtifactKind("ex/item_count", int)
ITEMS = RecordListKind("ex/items", fields=(AMOUNT,))
TWO_FIELDS = RecordListKind("ex/pairs", fields=(AMOUNT, COUNT))
COUNTS_ONLY = RecordListKind("ex/counts", fields=(COUNT,))
TOTAL = ArtifactKind("ex/items_total", Decimal)


def capability() -> RecordPositiveTotal:
    return RecordPositiveTotal(records=ITEMS, output=TOTAL)


def items(*amounts: str) -> Artifact[Any]:
    return Artifact(ITEMS, RecordList(ITEMS.fields, [{AMOUNT: D(a)} for a in amounts]))


def total_of(*amounts: str) -> Decimal:
    (artifact,) = capability().compute((items(*amounts),)).outputs
    assert artifact.kind == TOTAL
    assert isinstance(artifact.value, Decimal)
    return artifact.value


def test_is_registered_as_core_record_positive_total() -> None:
    assert CapabilityRegistry.shared().get("core/record_positive_total") is RecordPositiveTotal


def test_is_exported_from_the_capabilities_package() -> None:
    assert "record_positive_total" in core.__all__
    assert core.record_positive_total.RecordPositiveTotal is RecordPositiveTotal


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({ITEMS})
    assert capability().produces == frozenset({TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RecordPositiveTotal)
    assert "produces" not in vars(RecordPositiveTotal)


def test_declares_its_slots() -> None:
    assert RecordPositiveTotal.PARAMETERS == {}
    assert RecordPositiveTotal.CONSUMES == {"records": RecordList}
    assert RecordPositiveTotal.PRODUCES == {"output": Decimal}
    assert not RecordPositiveTotal.is_list_slot("records")


def test_its_slots_are_read_only() -> None:
    for slots in (
        RecordPositiveTotal.PARAMETERS,
        RecordPositiveTotal.CONSUMES,
        RecordPositiveTotal.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        RecordPositiveTotal(ITEMS, TOTAL, object())  # type: ignore[call-arg]


# --- building ---------------------------------------------------------------------------------


def test_rejects_an_amount_kind_for_its_records() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordPositiveTotal.*'records'"):
        RecordPositiveTotal(records=AMOUNT, output=TOTAL)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordPositiveTotal.*'output'"):
        RecordPositiveTotal(records=ITEMS, output=ITEMS)  # type: ignore[arg-type]


def test_rejects_a_list_kind_of_more_than_one_field() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordPositiveTotal.*'records'"):
        RecordPositiveTotal(records=TWO_FIELDS, output=TOTAL)


def test_rejects_a_list_kind_whose_one_field_is_a_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="RecordPositiveTotal.*'records'"):
        RecordPositiveTotal(records=COUNTS_ONLY, output=TOTAL)


def test_rejects_a_list_kind_whose_one_field_is_a_record_list() -> None:
    inner = RecordListKind("ex/inner", fields=(AMOUNT,))
    nested = RecordListKind("ex/nested", fields=(inner,))

    with pytest.raises(InvalidCapabilityError, match="RecordPositiveTotal.*'records'"):
        RecordPositiveTotal(records=nested, output=TOTAL)


def test_rejects_a_plain_kind_of_record_lists_as_records() -> None:
    plain = ArtifactKind("ex/plain_list", RecordList)

    with pytest.raises(InvalidCapabilityError, match=r"RecordPositiveTotal.*'records'"):
        RecordPositiveTotal(records=plain, output=TOTAL)  # type: ignore[arg-type]


# --- computing --------------------------------------------------------------------------------


def test_no_records_total_zero() -> None:
    assert total_of() == D("0")


def test_one_positive_record_is_its_own_total() -> None:
    assert total_of("24000") == D("24000")


def test_positive_records_add_up_with_cents() -> None:
    assert total_of("24000", "6000", "1250.75") == D("31250.75")


def test_a_negative_record_counts_zero() -> None:
    assert total_of("100", "-30") == D("100")


def test_a_negative_record_between_positives_counts_zero() -> None:
    assert total_of("6000", "-4000", "250.25") == D("6250.25")


def test_a_zero_record_counts_zero() -> None:
    assert total_of("6000", "0", "4000") == D("10000")


def test_only_zero_records_total_zero() -> None:
    assert total_of("0", "0") == D("0")


def test_only_negative_records_total_zero() -> None:
    assert total_of("-4000", "-0.5") == D("0")


def test_a_negative_cent_record_counts_zero() -> None:
    assert total_of("-0.01") == D("0")


def test_the_total_is_exact_and_never_rounded() -> None:
    assert str(total_of("1000.005", "0.001")) == "1000.006"
    assert total_of("0.1", "0.2") == D("0.3")


def test_the_total_keeps_the_scale_of_its_records() -> None:
    assert str(total_of("6000.00", "4000")) == "10000.00"


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute((items("1", "-2", "2"),))

    assert result.outputs == (Artifact(TOTAL, D("3")),)


def test_a_missing_records_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_records_one_trace_line_naming_the_field_and_each_amount_as_read() -> None:
    result = capability().compute((items("6000", "-4000", "0"),))

    assert result.trace == (
        RecordPositiveTotalLine(
            output=TOTAL,
            field=AMOUNT,
            amounts=(D("6000"), D("-4000"), D("0")),
            total=D("6000"),
        ),
    )


def test_an_empty_list_records_a_line_with_no_amounts() -> None:
    result = capability().compute((items(),))

    assert result.trace == (
        RecordPositiveTotalLine(output=TOTAL, field=AMOUNT, amounts=(), total=D("0")),
    )


def test_the_trace_renders_each_item_then_the_total_and_the_positive_only_rule() -> None:
    result = capability().compute((items("6000", "-4000", "0"),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "items_total: item 1 item_amount 6000 + item 2 item_amount -4000 counts 0"
        " + item 3 item_amount 0 counts 0 = 6000."
        " Only positive amounts are added; a zero or negative amount counts 0.",
    )


def test_the_trace_for_no_records_says_no_items() -> None:
    result = capability().compute((items(),))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "items_total: no items = 0."
        " Only positive amounts are added; a zero or negative amount counts 0.",
    )
