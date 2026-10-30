"""Unit tests for the StatementAmountsTotal capability (`ca/statement_amounts_total`), made-up
kinds.

Form T1139 amounts A, H and I are "the net income (loss)" of the statement or statements of one
business, the amount found on line 9946 of the form that applies to its type of business income;
"if you have more than one fiscal period ... amount A is the total of the net income (loss) of
these fiscal periods". Its slots: no parameter slot; three consumed slots, `records` (a list slot:
the record lists of the statements, one amount field each, one for each type of business income in
line order), `line` (an int naming one of them, from 1) and `positions` (a record list of one count
field: the positions of the statements, from 1); one produced `Decimal` slot `total`. The total is
the statements at those positions added, signed; no positions give 0. A line outside the lists, a
position that is not a statement or a position named twice is refused (`InputOutOfRangeError`).
It records one `ItemsTotalLine` naming each statement by its position.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    InputOutOfRangeError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.statement_amounts_total import (
    StatementAmountsTotal,
)

D = Decimal

BUSINESS_NET = ArtifactKind("ex/business_net", Decimal)
FISHING_NET = ArtifactKind("ex/fishing_net", Decimal)
BUSINESS = RecordListKind("ex/business_statements", fields=(BUSINESS_NET,))
FISHING = RecordListKind("ex/fishing_statements", fields=(FISHING_NET,))
STATEMENT = ArtifactKind("ex/statement_number", int)
STATEMENTS = RecordListKind("ex/named_statements", fields=(STATEMENT,))
LINE = ArtifactKind("ex/line_code", int)
TOTAL = ArtifactKind("ex/statements_total", Decimal)
TWO_FIELDS = RecordListKind("ex/pairs", fields=(BUSINESS_NET, STATEMENT))
AMOUNT_POSITIONS = RecordListKind("ex/amount_positions", fields=(BUSINESS_NET,))


def capability() -> StatementAmountsTotal:
    return StatementAmountsTotal(
        records=(BUSINESS, FISHING), line=LINE, positions=STATEMENTS, total=TOTAL
    )


def amounts(kind: RecordListKind, *values: str) -> Artifact[Any]:
    (field,) = kind.fields
    return Artifact(kind, RecordList(kind.fields, [{field: D(v)} for v in values]))


def named(*positions: int) -> Artifact[Any]:
    return Artifact(STATEMENTS, RecordList(STATEMENTS.fields, [{STATEMENT: p} for p in positions]))


def inputs(line: int, *positions: int) -> tuple[Artifact[Any], ...]:
    return (
        amounts(BUSINESS, "45000.00", "30000.00", "-500.25"),
        amounts(FISHING, "100.00"),
        Artifact(LINE, line),
        named(*positions),
    )


def total_of(line: int, *positions: int) -> Decimal:
    (artifact,) = capability().compute(inputs(line, *positions)).outputs
    assert artifact.kind == TOTAL
    assert isinstance(artifact.value, Decimal)
    return artifact.value


def test_is_registered_as_ca_statement_amounts_total() -> None:
    assert CapabilityRegistry.shared().get("ca/statement_amounts_total") is StatementAmountsTotal


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "statement_amounts_total" in ca_capabilities.__all__


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({BUSINESS, FISHING, LINE, STATEMENTS})
    assert capability().produces == frozenset({TOTAL})


def test_declares_its_slots() -> None:
    assert StatementAmountsTotal.PARAMETERS == {}
    assert StatementAmountsTotal.CONSUMES == {
        "records": list[RecordList],
        "line": int,
        "positions": RecordList,
    }
    assert StatementAmountsTotal.is_list_slot("records")
    assert not StatementAmountsTotal.is_list_slot("positions")
    assert set(StatementAmountsTotal.PRODUCES) == {"total"}


def test_its_slots_are_read_only() -> None:
    for slots in (
        StatementAmountsTotal.PARAMETERS,
        StatementAmountsTotal.CONSUMES,
        StatementAmountsTotal.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


# --- building ---------------------------------------------------------------------------------


def test_rejects_a_list_of_statements_with_a_count_field() -> None:
    with pytest.raises(
        InvalidCapabilityError, match=r"StatementAmountsTotal.*'ex/named_statements'"
    ):
        StatementAmountsTotal(records=(STATEMENTS,), line=LINE, positions=STATEMENTS, total=TOTAL)


def test_rejects_a_list_of_statements_with_more_than_one_field() -> None:
    with pytest.raises(InvalidCapabilityError, match=r"StatementAmountsTotal.*'ex/pairs'"):
        StatementAmountsTotal(records=(TWO_FIELDS,), line=LINE, positions=STATEMENTS, total=TOTAL)


def test_rejects_positions_that_are_not_one_count_field() -> None:
    with pytest.raises(
        InvalidCapabilityError, match=r"StatementAmountsTotal.*'ex/amount_positions'"
    ):
        StatementAmountsTotal(
            records=(BUSINESS,), line=LINE, positions=AMOUNT_POSITIONS, total=TOTAL
        )


# --- computing --------------------------------------------------------------------------------


def test_one_statement_is_its_own_net_income() -> None:
    assert total_of(1, 1) == D("45000.00")


def test_several_statements_of_one_business_are_added() -> None:
    assert total_of(1, 1, 2) == D("75000.00")


def test_a_loss_keeps_its_sign() -> None:
    assert total_of(1, 3) == D("-500.25")
    assert total_of(1, 1, 3) == D("44499.75")


def test_the_positions_name_the_statements_in_any_order() -> None:
    assert total_of(1, 3, 1) == D("44499.75")


def test_the_line_names_the_list_the_positions_read() -> None:
    assert total_of(2, 1) == D("100.00")


def test_no_positions_add_up_to_zero() -> None:
    assert total_of(1) == D("0")


def test_produces_one_artifact_of_the_output_kind() -> None:
    assert capability().compute(inputs(1, 2)).outputs == (Artifact(TOTAL, D("30000.00")),)


def test_a_line_below_the_first_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match="ex/line_code 0 is not one of the 2 lines"):
        total_of(0, 1)


def test_a_line_past_the_last_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match="ex/line_code 3 is not one of the 2 lines"):
        total_of(3)


def test_a_position_of_zero_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match="ex/statement_number 0 names no statement"):
        total_of(1, 0)


def test_a_position_past_the_end_of_its_list_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match="ex/statement_number 2.*fishing.*which has 1"):
        total_of(2, 2)


def test_a_position_named_twice_is_refused() -> None:
    with pytest.raises(InputOutOfRangeError, match="ex/statement_number 1.*business.*twice"):
        total_of(1, 1, 2, 1)


def test_a_missing_list_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute(inputs(1, 1)[1:])


# --- trace ------------------------------------------------------------------------------------


def test_records_one_items_total_line_naming_each_statement_by_its_position() -> None:
    assert capability().compute(inputs(1, 3, 1)).trace == (
        ItemsTotalLine(TOTAL, ((3, D("-500.25")), (1, D("45000.00"))), D("44499.75")),
    )


def test_the_trace_renders_each_statement_and_the_total() -> None:
    result = capability().compute(inputs(1, 1, 2))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "statements_total: item 1 45000 + item 2 30000 = 75000",
    )


def test_the_trace_of_no_statement_says_no_items() -> None:
    result = capability().compute(inputs(1))

    assert EnglishTraceRenderer().render_all(result.trace) == ("statements_total: no items = 0",)
