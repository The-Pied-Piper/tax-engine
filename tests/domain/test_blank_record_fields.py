"""Unit tests for a blank field inside the records of a record list (`BLANK_RECORD_FIELDS`).

A class names the record-list slots whose records may have a blank field; the manifest gives each
field its own rule (a fallback, `PASS_ON` or `COMPUTE`), applied to that field in every record
before `compute` runs. A blank field with no rule is refused naming the field, the record and the
list. A whole record list left blank is the slot's own rule, as for any artifact.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, Money
from tax_engine.domain.blank import BLANK, COMPUTE, PASS_ON
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.errors import BlankNotAllowedError, BlankValueError, InvalidCapabilityError
from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace.blank import BlankField, BlankFieldFallbackLine, BlankPassedOnLine

D = Decimal

SALES = AmountKind("ex/sales")
COSTS = AmountKind("ex/costs", non_negative=True)
COPIES = CountKind("ex/copies", non_negative=True)
LINES = RecordListKind("ex/lines", fields=(SALES, COSTS))
OTHER_LINES = RecordListKind("ex/other_lines", fields=(SALES, COSTS))
COUNTED = RecordListKind("ex/counted", fields=(COPIES,))
NET = AmountKind("ex/net")
OTHER_NET = AmountKind("ex/other_net")


class SalesLessCosts(Capability):
    """`net` is the sales less the costs over the records of `lines`, either field may be blank."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"lines": RecordList}
    PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"lines"})
    BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"lines"})

    def __init__(self, lines: RecordListKind, net: Money) -> None:
        super().__init__(lines=lines, net=net)
        self._lines = lines
        self._net = net

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._lines).value.records
        total = sum((record[SALES] - record[COSTS] for record in records), D(0))
        return CapabilityResult(outputs=(Artifact(self._net, total),), trace=())


class Reads(SalesLessCosts):
    """Reads the sales of each record, or 0 where it is blank, so it may be given `COMPUTE`."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        records = self._input(inputs, self._lines).value.records
        total = sum((D(0) if r.is_blank(SALES) else r[SALES] for r in records), D(0))
        return CapabilityResult(outputs=(Artifact(self._net, total),), trace=())


def lines(*records: Mapping[Any, Any]) -> Artifact[RecordList]:
    return Artifact(LINES, RecordList(LINES.fields, records))


def built(rules: Mapping[Any, Any], cls: type[SalesLessCosts] = SalesLessCosts) -> Capability:
    return cls(LINES, NET).with_blank_rules({}, None, {"lines": rules})


def test_a_fallback_replaces_the_blank_field_in_every_record_and_is_traced_by_record() -> None:
    capability = built({SALES: D(0)})

    result = capability.run(
        (
            lines(
                {SALES: BLANK, COSTS: D(2)},
                {SALES: D(10), COSTS: D(1)},
                {SALES: BLANK, COSTS: D(0)},
            ),
        )
    )

    assert result.outputs == (Artifact(NET, D(7)),)
    assert result.trace == (
        BlankFieldFallbackLine(BlankField(SALES, LINES, 1), D(0)),
        BlankFieldFallbackLine(BlankField(SALES, LINES, 3), D(0)),
    )


def test_a_blank_field_with_no_rule_is_refused_naming_the_field_record_and_list() -> None:
    capability = built({SALES: D(0)})

    with pytest.raises(BlankNotAllowedError, match="'costs' was left blank in item 2 of 'lines'"):
        capability.run((lines({SALES: D(1), COSTS: D(1)}, {SALES: D(1), COSTS: BLANK}),))


def test_a_blank_field_in_a_slot_the_class_does_not_open_is_still_a_value_error() -> None:
    class Closed(SalesLessCosts):
        BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset()

    with pytest.raises(BlankValueError, match="was left blank"):
        Closed(LINES, NET).run((lines({SALES: BLANK, COSTS: D(1)}),))


def test_pass_on_makes_every_output_blank_and_the_trace_names_every_record() -> None:
    capability = built({SALES: D(0), COSTS: PASS_ON})

    result = capability.run(
        (
            lines(
                {SALES: D(1), COSTS: BLANK},
                {SALES: D(1), COSTS: D(1)},
                {SALES: BLANK, COSTS: BLANK},
            ),
        )
    )

    assert result.outputs == (Artifact(NET, BLANK),)
    assert result.trace == (
        BlankPassedOnLine(NET, (), (BlankField(COSTS, LINES, 1), BlankField(COSTS, LINES, 3))),
    )


def test_pass_on_in_a_field_wins_over_a_fallback_in_another_and_the_fallback_is_not_traced() -> (
    None
):
    capability = built({SALES: D(0), COSTS: PASS_ON})

    result = capability.run((lines({SALES: BLANK, COSTS: BLANK}),))

    (line,) = result.trace
    assert isinstance(line, BlankPassedOnLine)
    assert line.because_fields == (BlankField(COSTS, LINES, 1),)


def test_a_slot_pass_on_and_a_field_pass_on_are_both_named() -> None:
    class TwoSlots(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"lines": RecordList, "base": Decimal}
        PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}
        BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"base"})
        BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"lines"})

        def __init__(self, lines: RecordListKind, base: Money, net: Money) -> None:
            super().__init__(lines=lines, base=base, net=net)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            raise NotImplementedError

    capability = TwoSlots(LINES, OTHER_NET, NET).with_blank_rules(
        {"base": PASS_ON}, None, {"lines": {COSTS: PASS_ON, SALES: D(0)}}
    )

    result = capability.run((lines({SALES: D(1), COSTS: BLANK}), Artifact(OTHER_NET, BLANK)))

    assert result.trace == (BlankPassedOnLine(NET, (OTHER_NET,), (BlankField(COSTS, LINES, 1),)),)


def test_compute_hands_the_blank_field_to_the_class_to_decide() -> None:
    capability = built({SALES: COMPUTE, COSTS: D(0)}, Reads)

    result = capability.run((lines({SALES: BLANK, COSTS: D(0)}, {SALES: D(4), COSTS: BLANK}),))

    assert result.outputs == (Artifact(NET, D(4)),)


def test_with_no_blank_field_the_records_are_unchanged_and_nothing_is_traced() -> None:
    result = built({}).run((lines({SALES: D(5), COSTS: D(2)}),))

    assert result.outputs == (Artifact(NET, D(3)),)
    assert result.trace == ()


def test_a_whole_list_left_blank_takes_the_slot_rule_not_the_field_rules() -> None:
    capability = SalesLessCosts(LINES, NET).with_blank_rules(
        {"lines": PASS_ON}, None, {"lines": {SALES: D(0)}}
    )

    result = capability.run((Artifact(LINES, BLANK),))

    assert result.outputs == (Artifact(NET, BLANK),)
    assert result.trace == (BlankPassedOnLine(NET, (LINES,)),)


def test_a_whole_list_left_blank_with_no_slot_rule_is_refused_whatever_the_field_rules() -> None:
    capability = built({SALES: D(0), COSTS: D(0)})

    with pytest.raises(BlankNotAllowedError, match="'lines' was left blank"):
        capability.run((Artifact(LINES, BLANK),))


def test_a_field_rule_holds_in_every_list_of_a_list_slot() -> None:
    class Many(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"lines": list[RecordList]}
        PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}
        BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"lines"})

        def __init__(self, lines: tuple[RecordListKind, ...], net: Money) -> None:
            super().__init__(lines=lines, net=net)
            self._lines = lines

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            total = sum(
                (
                    record[SALES] - record[COSTS]
                    for kind in self._lines
                    for record in self._input(inputs, kind).value.records
                ),
                D(0),
            )
            return CapabilityResult(outputs=(Artifact(NET, total),), trace=())

    capability = Many((LINES, OTHER_LINES), NET).with_blank_rules(
        {}, None, {"lines": {SALES: D(0), COSTS: D(0)}}
    )

    result = capability.run(
        (
            lines({SALES: BLANK, COSTS: D(1)}),
            Artifact(OTHER_LINES, RecordList(OTHER_LINES.fields, [{SALES: D(5), COSTS: BLANK}])),
        )
    )

    assert result.outputs == (Artifact(NET, D(4)),)
    assert [
        line.field.records for line in result.trace if isinstance(line, BlankFieldFallbackLine)
    ] == [
        LINES,
        OTHER_LINES,
    ]


def test_the_trace_reads_in_english_with_the_record_named() -> None:
    capability = built({SALES: D(0), COSTS: PASS_ON})
    taken = built({SALES: D(0), COSTS: D(0)}).run((lines({SALES: BLANK, COSTS: D(1)}),))
    passed = capability.run((lines({SALES: D(1), COSTS: BLANK}),))
    renderer = EnglishTraceRenderer()

    assert renderer.render(taken.trace[0]) == "sales (item 1 of lines): left blank, taken as 0"
    assert renderer.render(passed.trace[0]) == (
        "net: blank because costs (item 1 of lines) was blank"
    )


def test_the_rules_are_checked_when_given() -> None:
    plain = SalesLessCosts(LINES, NET)

    with pytest.raises(InvalidCapabilityError, match="is not a field of a record list in slot"):
        plain.with_blank_rules({}, None, {"lines": {NET: D(0)}})
    with pytest.raises(InvalidCapabilityError, match="may not have a blank field"):
        SalesLessCosts(LINES, NET).with_blank_rules({}, None, {"net": {SALES: D(0)}})
    with pytest.raises(
        InvalidCapabilityError, match="must be PASS_ON, COMPUTE or a finite Decimal"
    ):
        SalesLessCosts(LINES, NET).with_blank_rules({}, None, {"lines": {SALES: 0}})
    with pytest.raises(InvalidCapabilityError, match="not valid for 'ex/costs'"):
        SalesLessCosts(LINES, NET).with_blank_rules({}, None, {"lines": {COSTS: D(-1)}})


def test_a_count_field_takes_an_int_fallback_and_a_record_list_field_cannot_take_one() -> None:
    class Counts(Capability):
        CONSUMES: ClassVar[Mapping[str, type]] = {"counted": RecordList}
        PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}
        BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"counted"})

        def __init__(self, counted: RecordListKind, net: Money) -> None:
            super().__init__(counted=counted, net=net)

        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            raise NotImplementedError

    Counts(COUNTED, NET).with_blank_rules({}, None, {"counted": {COPIES: 1}})
    with pytest.raises(InvalidCapabilityError, match="must be PASS_ON, COMPUTE or a finite int"):
        Counts(COUNTED, NET).with_blank_rules({}, None, {"counted": {COPIES: D(1)}})

    nested = RecordListKind("ex/nested", fields=(COUNTED,))
    with pytest.raises(InvalidCapabilityError, match="can only be passed on"):
        Counts(nested, NET).with_blank_rules({}, None, {"counted": {COUNTED: 0}})


def test_blank_record_fields_must_name_consumed_record_list_slots() -> None:
    with pytest.raises(InvalidCapabilityError, match="BLANK_RECORD_FIELDS slot 'net'"):

        class NotConsumed(SalesLessCosts):
            BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"net"})

    with pytest.raises(InvalidCapabilityError, match="BLANK_RECORD_FIELDS slot 'base'"):

        class NotRecords(Capability):
            CONSUMES: ClassVar[Mapping[str, type]] = {"base": Decimal}
            PRODUCES: ClassVar[Mapping[str, type]] = {"net": Decimal}
            BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = frozenset({"base"})

            def __init__(self, base: Money, net: Money) -> None:
                super().__init__(base=base, net=net)

            def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
                raise NotImplementedError

    with pytest.raises(InvalidCapabilityError, match="BLANK_RECORD_FIELDS must be a set"):

        class NotASet(SalesLessCosts):
            BLANK_RECORD_FIELDS: ClassVar[frozenset[str]] = 5  # type: ignore[assignment]


def test_blank_record_fields_is_a_frozen_set_inherited_and_empty_on_the_base() -> None:
    assert Capability.BLANK_RECORD_FIELDS == frozenset()
    assert SalesLessCosts.BLANK_RECORD_FIELDS == frozenset({"lines"})
    assert Reads.BLANK_RECORD_FIELDS == frozenset({"lines"})


def test_record_total_adds_the_amount_field_taking_a_blank_as_given() -> None:
    amount = AmountKind("ex/amount")
    items = RecordListKind("ex/amounts", fields=(amount,))
    capability = RecordTotal(items, NET).with_blank_rules({}, None, {"records": {amount: D(0)}})

    result = capability.run(
        (Artifact(items, RecordList(items.fields, [{amount: BLANK}, {amount: D(3)}])),)
    )

    assert result.outputs == (Artifact(NET, D(3)),)
    assert result.trace[0] == BlankFieldFallbackLine(BlankField(amount, items, 1), D(0))
