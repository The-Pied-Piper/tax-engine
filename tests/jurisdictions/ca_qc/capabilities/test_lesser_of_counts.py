"""Unit tests for the LesserOfCounts capability (`ca-qc/lesser_of_counts`), with made-up kinds.

Schedule P Part D line 59 "Number from line 57 or line 58, whichever is less". Its slots: one
consumed list slot `counts` (a tuple of count kinds, at least one, since there is no lesser of
nothing), one produced slot `output` (a count kind), no parameter slots and no dataset. The output
is the minimum of the counts' values; when two counts are equal the first listed is produced. It
records one `LesserOfCountsLine` holding each count in the order it was wired.

The `counts` slot may be blank (`BLANK_ALLOWED`); the rule the manifest gives decides what a blank
does there.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca_qc.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tax_engine.jurisdictions.ca_qc.capabilities.lesser_of_counts import LesserOfCounts
from tax_engine.jurisdictions.ca_qc.trace import LesserOfCountsLine
from tests.jurisdictions.ca_qc.support import quebec_capabilities

MONTHS_ONE = CountKind("ex/months_one")
MONTHS_TWO = CountKind("ex/months_two")
MONTHS_THREE = CountKind("ex/months_three")
LESSER_MONTHS = CountKind("ex/lesser_months")


def capability() -> LesserOfCounts:
    """By default the first and second made-up counts, in that order."""
    return LesserOfCounts((MONTHS_ONE, MONTHS_TWO), LESSER_MONTHS)


def compute(wired: LesserOfCounts, *values: tuple[ArtifactKind[int], int]) -> Artifact[Any]:
    (output,) = wired.compute(tuple(Artifact(kind, value) for kind, value in values)).outputs
    return output


def test_is_registered_as_ca_qc_lesser_of_counts() -> None:
    assert quebec_capabilities().get("ca-qc/lesser_of_counts") is LesserOfCounts


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({MONTHS_ONE, MONTHS_TWO})
    assert capability().produces == frozenset({LESSER_MONTHS})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(LesserOfCounts)
    assert "produces" not in vars(LesserOfCounts)


def test_declares_its_slots() -> None:
    assert LesserOfCounts.PARAMETERS == {}
    assert LesserOfCounts.CONSUMES == {"counts": list[int]}
    assert LesserOfCounts.PRODUCES == {"output": int}
    assert LesserOfCounts.is_list_slot("counts")
    assert not LesserOfCounts.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (LesserOfCounts.PARAMETERS, LesserOfCounts.CONSUMES, LesserOfCounts.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(LesserOfCounts.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(LesserOfCounts.CONSUMES, Mapping[str, type])
    assert_type(LesserOfCounts.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (LesserOfCounts.PARAMETERS, LesserOfCounts.CONSUMES, LesserOfCounts.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = LesserOfCounts(counts=(MONTHS_ONE, MONTHS_TWO), output=LESSER_MONTHS)

    assert compute(wired, (MONTHS_ONE, 10), (MONTHS_TWO, 4)) == Artifact(LESSER_MONTHS, 4)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        LesserOfCounts((MONTHS_ONE,), LESSER_MONTHS, object())  # type: ignore[call-arg]


def test_rejects_an_empty_list_of_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfCounts.*'counts'"):
        LesserOfCounts((), LESSER_MONTHS)


def test_rejects_one_kind_as_both_a_count_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfCounts") as raised:
        LesserOfCounts((MONTHS_ONE, LESSER_MONTHS), LESSER_MONTHS)

    message = str(raised.value)
    assert "'counts'" in message
    assert "'output'" in message


def test_rejects_a_count_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfCounts.*'counts'"):
        LesserOfCounts((MONTHS_ONE, MONTHS_TWO, MONTHS_ONE), LESSER_MONTHS)


def test_rejects_a_single_kind_for_its_counts() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOfCounts.*'counts'"):
        LesserOfCounts(MONTHS_ONE, LESSER_MONTHS)  # type: ignore[arg-type]


def test_rejects_a_money_kind_for_a_count() -> None:
    money = AmountKind("ex/money")

    with pytest.raises(InvalidCapabilityError, match="LesserOfCounts.*'counts'"):
        LesserOfCounts((MONTHS_ONE, money), LESSER_MONTHS)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(LesserOfCounts, "__type_params__", ())
    assert not getattr(LesserOfCounts, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_first_count_when_it_is_less() -> None:
    assert compute(capability(), (MONTHS_ONE, 4), (MONTHS_TWO, 10)) == Artifact(LESSER_MONTHS, 4)


def test_produces_the_second_count_when_it_is_less() -> None:
    assert compute(capability(), (MONTHS_ONE, 10), (MONTHS_TWO, 4)) == Artifact(LESSER_MONTHS, 4)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    assert compute(capability(), (MONTHS_TWO, 4), (MONTHS_ONE, 10)) == Artifact(LESSER_MONTHS, 4)


def test_produces_the_least_of_three_counts() -> None:
    wired = LesserOfCounts((MONTHS_ONE, MONTHS_TWO, MONTHS_THREE), LESSER_MONTHS)

    output = compute(wired, (MONTHS_ONE, 9), (MONTHS_TWO, 3), (MONTHS_THREE, 7))

    assert output == Artifact(LESSER_MONTHS, 3)


@pytest.mark.parametrize("least", [MONTHS_ONE, MONTHS_TWO, MONTHS_THREE])
def test_produces_the_least_of_three_wherever_it_is_listed(least: ArtifactKind[int]) -> None:
    wired = LesserOfCounts((MONTHS_ONE, MONTHS_TWO, MONTHS_THREE), LESSER_MONTHS)
    values = [(kind, 1 if kind is least else 2) for kind in (MONTHS_ONE, MONTHS_TWO, MONTHS_THREE)]

    assert compute(wired, *values) == Artifact(LESSER_MONTHS, 1)


def test_one_count_is_its_own_lesser() -> None:
    wired = LesserOfCounts((MONTHS_TWO,), LESSER_MONTHS)

    assert compute(wired, (MONTHS_TWO, 5)) == Artifact(LESSER_MONTHS, 5)


def test_equal_counts_produce_that_count() -> None:
    assert compute(capability(), (MONTHS_ONE, 6), (MONTHS_TWO, 6)) == Artifact(LESSER_MONTHS, 6)


def test_a_zero_count_produces_zero() -> None:
    assert compute(capability(), (MONTHS_ONE, 12), (MONTHS_TWO, 0)) == Artifact(LESSER_MONTHS, 0)


def test_produces_an_int() -> None:
    assert type(compute(capability(), (MONTHS_ONE, 1), (MONTHS_TWO, 2)).value) is int


def test_ignores_artifacts_it_does_not_consume() -> None:
    output = compute(capability(), (MONTHS_ONE, 10), (MONTHS_THREE, 1), (MONTHS_TWO, 4))

    assert output == Artifact(LESSER_MONTHS, 4)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="months_two"):
        capability().compute((Artifact(MONTHS_ONE, 10),))


def test_compute_is_repeatable() -> None:
    wired = capability()
    inputs = (Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))

    assert wired.compute(inputs) == wired.compute(inputs)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_count_and_the_result() -> None:
    trace = capability().compute((Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))).trace

    assert trace == (
        LesserOfCountsLine(
            output=LESSER_MONTHS,
            parts=((MONTHS_ONE, 10), (MONTHS_TWO, 4)),
            result=4,
        ),
    )


def test_traces_the_counts_in_the_order_they_were_wired() -> None:
    wired = LesserOfCounts((MONTHS_THREE, MONTHS_ONE, MONTHS_TWO), LESSER_MONTHS)
    inputs = (Artifact(MONTHS_ONE, 9), Artifact(MONTHS_TWO, 3), Artifact(MONTHS_THREE, 7))

    assert wired.compute(inputs).trace == (
        LesserOfCountsLine(LESSER_MONTHS, ((MONTHS_THREE, 7), (MONTHS_ONE, 9), (MONTHS_TWO, 3)), 3),
    )


def test_traces_one_count() -> None:
    wired = LesserOfCounts((MONTHS_TWO,), LESSER_MONTHS)

    assert wired.compute((Artifact(MONTHS_TWO, 5),)).trace == (
        LesserOfCountsLine(LESSER_MONTHS, ((MONTHS_TWO, 5),), 5),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute((Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))).trace

    assert [line.amount for line in trace] == [Decimal(4)]


def test_trace_label_is_the_output_label() -> None:
    (line,) = capability().compute((Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))).trace

    assert line.label == LESSER_MONTHS.label


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_the_trace_reads_in_english() -> None:
    trace = capability().compute((Artifact(MONTHS_ONE, 10), Artifact(MONTHS_TWO, 4))).trace

    assert EnglishTraceRenderer().render_all(trace) == (
        "Lesser of months one (10) and months two (4) gives 4.",
    )


def test_the_trace_of_three_counts_reads_in_english() -> None:
    wired = LesserOfCounts((MONTHS_ONE, MONTHS_TWO, MONTHS_THREE), LESSER_MONTHS)
    inputs = (Artifact(MONTHS_ONE, 9), Artifact(MONTHS_TWO, 3), Artifact(MONTHS_THREE, 7))

    assert EnglishTraceRenderer().render_all(wired.compute(inputs).trace) == (
        "Least of months one (9), months two (3) and months three (7) gives 3.",
    )


# --- a blank count ----------------------------------------------------------------------------


def blank_input(kind: ArtifactKind[int]) -> Artifact[Any]:
    return Artifact(kind, BLANK)


def test_declares_that_the_counts_may_be_blank() -> None:
    assert LesserOfCounts.BLANK_ALLOWED == frozenset({"counts"})


def test_without_rules_a_blank_count_is_refused_naming_the_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'counts'"):
        capability().run((blank_input(MONTHS_ONE), Artifact(MONTHS_TWO, 1)))


def test_pass_on_blanks_the_output_whichever_count_is_blank() -> None:
    passing = capability().with_blank_rules({"counts": PASS_ON})

    for inputs in (
        (blank_input(MONTHS_ONE), Artifact(MONTHS_TWO, 1)),
        (Artifact(MONTHS_ONE, 1), blank_input(MONTHS_TWO)),
    ):
        result = passing.run(inputs)
        assert result.outputs == (Artifact(LESSER_MONTHS, BLANK),)
        assert isinstance(result.trace[0], BlankPassedOnLine)


def test_filled_counts_are_unchanged_when_pass_on_is_declared() -> None:
    passing = capability().with_blank_rules({"counts": PASS_ON})

    result = passing.run((Artifact(MONTHS_ONE, 5), Artifact(MONTHS_TWO, 3)))

    assert result.outputs == (Artifact(LESSER_MONTHS, 3),)
    assert isinstance(result.trace[0], LesserOfCountsLine)


def test_a_fallback_stands_in_for_a_blank_count_before_the_least_is_found() -> None:
    carried = capability().with_blank_rules({"counts": 0})

    result = carried.run((blank_input(MONTHS_ONE), Artifact(MONTHS_TWO, 7)))

    assert result.outputs == (Artifact(LESSER_MONTHS, 0),)
    assert result.trace == (
        BlankFallbackLine(MONTHS_ONE, 0),
        LesserOfCountsLine(LESSER_MONTHS, ((MONTHS_ONE, 0), (MONTHS_TWO, 7)), 0),
    )


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="'output'"):
        capability().with_blank_rules({"output": PASS_ON})
