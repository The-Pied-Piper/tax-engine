"""Unit tests for the QbtBeforeQcc capability (`ca/qbt_before_qcc`), with made-up kinds.

Form T2048, "You must claim any deduction under a QBT before any deduction under a QCC." The form
is run once for each disposition, in the order the filer designates; this capability checks the
order of one run against the earlier runs. Its slots: two consumed slots, `is_qbt` (an `int` kind,
1 for a QBT and 0 for a QCC) and `earlier` (a record-list kind of exactly one `int` field: the
answers of the earlier runs, in order), one produced slot `output` (an `int` kind), no parameter
slots and no dataset. The output is the `is_qbt` answer, unchanged. A QCC (0) is always in order;
a QBT (1) is in order when every earlier answer is 1, and is an input error, a `ValidationError`
naming the first earlier QCC, when one of them is 0. It records one `QbtBeforeQccLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    DomainError,
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
from tax_calculator.domain.record_list import RecordList, RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.qbt_before_qcc import QbtBeforeQcc
from tax_calculator.jurisdictions.ca.trace import QbtBeforeQccLine

IS_QBT = ArtifactKind("ex/election_is_qbt", int)
ANSWER = ArtifactKind("ex/earlier_answer", int)
EARLIER = RecordListKind("ex/run.earlier_answer", fields=(ANSWER,))
OUTPUT = ArtifactKind("ex/election_in_order", int)


def capability() -> QbtBeforeQcc:
    return QbtBeforeQcc(IS_QBT, EARLIER, OUTPUT)


def earlier(*answers: int) -> Artifact[Any]:
    return Artifact(EARLIER, RecordList(EARLIER.fields, [{ANSWER: each} for each in answers]))


def inputs(is_qbt: int, *answers: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(IS_QBT, is_qbt), earlier(*answers))


def compute(is_qbt: int, *answers: int) -> Artifact[Any]:
    (output,) = capability().compute(inputs(is_qbt, *answers)).outputs
    return output


def test_is_registered_as_ca_qbt_before_qcc() -> None:
    assert CapabilityRegistry.shared().get("ca/qbt_before_qcc") is QbtBeforeQcc


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "qbt_before_qcc" in ca_capabilities.__all__
    assert ca_capabilities.qbt_before_qcc.QbtBeforeQcc is QbtBeforeQcc


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({IS_QBT, EARLIER})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(QbtBeforeQcc)
    assert "produces" not in vars(QbtBeforeQcc)


def test_declares_its_slots() -> None:
    assert QbtBeforeQcc.PARAMETERS == {}
    assert QbtBeforeQcc.CONSUMES == {"is_qbt": int, "earlier": RecordList}
    assert QbtBeforeQcc.PRODUCES == {"output": int}
    assert not QbtBeforeQcc.is_list_slot("is_qbt")
    assert not QbtBeforeQcc.is_list_slot("earlier")


def test_its_slots_are_read_only() -> None:
    for slots in (QbtBeforeQcc.PARAMETERS, QbtBeforeQcc.CONSUMES, QbtBeforeQcc.PRODUCES):
        assert isinstance(slots, MappingProxyType)
    with pytest.raises(TypeError):
        cast(Any, QbtBeforeQcc.CONSUMES)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = QbtBeforeQcc(is_qbt=IS_QBT, earlier=EARLIER, output=OUTPUT)

    assert wired.compute(inputs(1, 1)).outputs == (Artifact(OUTPUT, 1),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        QbtBeforeQcc(IS_QBT, EARLIER, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((IS_QBT, EARLIER, IS_QBT), ("'is_qbt'", "'output'")),
        ((OUTPUT, EARLIER, OUTPUT), ("'is_qbt'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[int], RecordListKind, ArtifactKind[int]], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="QbtBeforeQcc") as raised:
        QbtBeforeQcc(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_an_earlier_kind_that_is_not_a_record_list() -> None:
    with pytest.raises(InvalidCapabilityError, match="QbtBeforeQcc.*'earlier'"):
        QbtBeforeQcc(IS_QBT, ANSWER, OUTPUT)  # type: ignore[arg-type]


def test_rejects_an_earlier_list_of_more_than_one_field() -> None:
    other = ArtifactKind("ex/other_answer", int)
    two = RecordListKind("ex/run.two", fields=(ANSWER, other))

    with pytest.raises(InvalidCapabilityError, match="QbtBeforeQcc.*'earlier'"):
        QbtBeforeQcc(IS_QBT, two, OUTPUT)


def test_rejects_an_earlier_list_of_an_amount_field() -> None:
    money = RecordListKind("ex/run.money", fields=(ArtifactKind("ex/money", Decimal),))

    with pytest.raises(InvalidCapabilityError, match="QbtBeforeQcc.*'earlier'"):
        QbtBeforeQcc(IS_QBT, money, OUTPUT)


def test_rejects_a_money_kind_for_the_answer() -> None:
    money = ArtifactKind("ex/money", Decimal)

    with pytest.raises(InvalidCapabilityError, match="QbtBeforeQcc.*'is_qbt'"):
        QbtBeforeQcc(money, EARLIER, OUTPUT)  # type: ignore[arg-type]


# --- computing ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("is_qbt", "answers"),
    [
        (1, ()),
        (0, ()),
        (1, (1,)),
        (1, (1, 1, 1)),
        (0, (1,)),
        (0, (0,)),
        (0, (1, 1, 0, 0)),
        (0, (0, 1)),
    ],
)
def test_an_answer_in_order_is_produced_unchanged(is_qbt: int, answers: tuple[int, ...]) -> None:
    output = compute(is_qbt, *answers)

    assert output == Artifact(OUTPUT, is_qbt)
    assert type(output.value) is int


def test_the_first_run_sees_an_empty_list_and_is_in_order_whatever_its_answer() -> None:
    assert compute(1) == Artifact(OUTPUT, 1)
    assert compute(0) == Artifact(OUTPUT, 0)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", int), 9)

    assert capability().compute((other, *inputs(1, 1))).outputs == (Artifact(OUTPUT, 1),)


def test_a_missing_answer_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="election_is_qbt"):
        capability().compute((earlier(1),))


def test_missing_earlier_answers_are_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="earlier_answer"):
        capability().compute((Artifact(IS_QBT, 1),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs(1, 1)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs(1, 1, 1)) == wired.compute(inputs(1, 1, 1))


# --- a QBT after a QCC --------------------------------------------------------------------------


def test_a_qbt_after_a_qcc_is_a_validation_error() -> None:
    with pytest.raises(ValidationError):
        compute(1, 0)


def test_the_error_says_the_qbt_must_come_before_the_qcc_and_names_the_first_qcc() -> None:
    with pytest.raises(ValidationError) as raised:
        compute(1, 1, 0, 0)

    assert str(raised.value) == (
        "ex/election_is_qbt is 1 but disposition 2 before it is a QCC: "
        "the QBT must come before the QCC"
    )


def test_the_error_names_disposition_1_when_the_first_run_is_the_qcc() -> None:
    with pytest.raises(ValidationError, match=r"disposition 1 before it is a QCC"):
        compute(1, 0)


def test_a_validation_error_is_a_domain_error() -> None:
    assert issubclass(ValidationError, DomainError)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_qbt_before_qcc_line_with_the_run_s_answer_and_the_earlier_counts() -> None:
    assert capability().compute(inputs(1, 1, 1)).trace == (
        QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=2, earlier_qbts=2),
    )


def test_traces_a_qcc_after_a_qbt_and_a_qcc() -> None:
    assert capability().compute(inputs(0, 1, 0)).trace == (
        QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=0, earlier=2, earlier_qbts=1),
    )


def test_traces_the_first_run_with_nothing_before_it() -> None:
    assert capability().compute(inputs(1)).trace == (
        QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=0, earlier_qbts=0),
    )


def test_the_trace_line_fields_are_in_order_and_its_amount_is_the_answer() -> None:
    line = QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=2, earlier_qbts=2)

    assert [f.name for f in fields(line)] == [
        "output",
        "is_qbt_kind",
        "is_qbt",
        "earlier",
        "earlier_qbts",
    ]
    assert line.amount == Decimal(1)


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs(1, 1)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_the_line_reads_in_english() -> None:
    (line,) = capability().compute(inputs(1, 1, 1)).trace

    assert EnglishTraceRenderer().render_all((line,)) == (
        "election_in_order: election_is_qbt 1, after 2 earlier dispositions, 2 of them QBTs",
    )


def test_the_line_reads_in_english_for_a_qcc_among_the_earlier_runs() -> None:
    (line,) = capability().compute(inputs(0, 1, 0, 0)).trace

    assert EnglishTraceRenderer().render_all((line,)) == (
        "election_in_order: election_is_qbt 0, after 3 earlier dispositions, 1 of them QBTs",
    )


def test_a_trace_line_is_hashable_and_differs_by_its_counts() -> None:
    one = QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=2, earlier_qbts=2)
    two = QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=3, earlier_qbts=3)

    assert hash(one) == hash(
        QbtBeforeQccLine(output=OUTPUT, is_qbt_kind=IS_QBT, is_qbt=1, earlier=2, earlier_qbts=2)
    )
    assert one != two


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    consumes: Mapping[str, type] = QbtBeforeQcc.CONSUMES
    assert set(consumes) == {"is_qbt", "earlier"}
