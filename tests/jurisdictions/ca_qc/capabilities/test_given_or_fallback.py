"""Unit tests for the GivenOrFallback capability (`ca-qc/given_or_fallback`), with made-up kinds.

Schedule 10 line 13 "Enter the amount from box 56 of all of your T4 slips where Quebec is the
province of employment (if box 56 is blank, enter the amount from box 14 of the T4 slip)". Its
slots: two consumed slots `given` and `fallback` (money artifacts), one produced slot `output` (a
money artifact), no parameter slots and no dataset. A given figure is produced unchanged; a blank
`given` produces the `fallback`. It records one `GivenOrFallbackLine`.

The `given` slot may be blank (`BLANK_ALLOWED`); the manifest's `compute` rule lets the blank
reach `compute`, which takes the fallback. A blank `fallback` is always refused.
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
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, COMPUTE, PASS_ON
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.jurisdictions.ca_qc.capabilities.given_or_fallback import GivenOrFallback
from tax_engine.jurisdictions.ca_qc.trace import GivenOrFallbackLine
from tests.jurisdictions.ca_qc.support import quebec_capabilities

D = Decimal
GIVEN = AmountKind("ex/given")
FALLBACK = AmountKind("ex/fallback")
OTHER = AmountKind("ex/other")
OUTPUT = AmountKind("ex/output")


def capability() -> GivenOrFallback:
    return GivenOrFallback(given=GIVEN, fallback=FALLBACK, output=OUTPUT)


def computing() -> GivenOrFallback:
    """The capability as a manifest with the `compute` rule on `given` wires it."""
    return capability().with_blank_rules({"given": COMPUTE})


def test_is_registered_as_ca_qc_given_or_fallback() -> None:
    assert quebec_capabilities().get("ca-qc/given_or_fallback") is GivenOrFallback


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GIVEN, FALLBACK})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(GivenOrFallback)
    assert "produces" not in vars(GivenOrFallback)


def test_declares_its_slots() -> None:
    assert GivenOrFallback.PARAMETERS == {}
    assert GivenOrFallback.CONSUMES == {"given": Decimal, "fallback": Decimal}
    assert GivenOrFallback.PRODUCES == {"output": Decimal}
    assert not GivenOrFallback.is_list_slot("given")
    assert not GivenOrFallback.is_list_slot("fallback")


def test_its_slots_are_read_only() -> None:
    for slots in (GivenOrFallback.PARAMETERS, GivenOrFallback.CONSUMES, GivenOrFallback.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(GivenOrFallback.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(GivenOrFallback.CONSUMES, Mapping[str, type])
    assert_type(GivenOrFallback.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (GivenOrFallback.PARAMETERS, GivenOrFallback.CONSUMES, GivenOrFallback.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        GivenOrFallback(GIVEN, FALLBACK, OUTPUT, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_given_and_fallback() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrFallback"):
        GivenOrFallback(GIVEN, GIVEN, OUTPUT)


def test_rejects_the_output_as_an_input() -> None:
    with pytest.raises(InvalidCapabilityError, match="GivenOrFallback"):
        GivenOrFallback(GIVEN, FALLBACK, GIVEN)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(GivenOrFallback, "__type_params__", ())
    assert not getattr(GivenOrFallback, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def compute(wired: GivenOrFallback, given: Decimal | Any, fallback: Decimal) -> Artifact[Any]:
    inputs = (Artifact(GIVEN, given), Artifact(FALLBACK, fallback))
    (output,) = wired.compute(inputs).outputs
    return output


def test_a_given_figure_is_produced_unchanged() -> None:
    assert compute(computing(), D("1500.25"), D("50000")) == Artifact(OUTPUT, D("1500.25"))


def test_a_given_zero_is_a_figure_not_a_blank() -> None:
    assert compute(computing(), D("0"), D("50000")) == Artifact(OUTPUT, D("0"))


def test_a_blank_given_produces_the_fallback() -> None:
    assert compute(computing(), BLANK, D("50000")) == Artifact(OUTPUT, D("50000"))


def test_the_fallback_is_not_read_when_a_figure_is_given_but_must_still_be_present() -> None:
    with pytest.raises(MissingArtifactError, match="fallback"):
        computing().compute((Artifact(GIVEN, D("1")),))


def test_ignores_artifacts_it_does_not_consume() -> None:
    inputs = (Artifact(OTHER, D("9")), Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("3")))

    assert computing().compute(inputs).outputs == (Artifact(OUTPUT, D("3")),)


def test_a_blank_fallback_is_refused_whatever_is_given() -> None:
    with pytest.raises(BlankNotAllowedError, match="'fallback'"):
        computing().run((Artifact(GIVEN, D("1")), Artifact(FALLBACK, BLANK)))


def test_compute_is_repeatable() -> None:
    wired = computing()
    inputs = (Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("7")))

    assert wired.compute(inputs) == wired.compute(inputs)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_for_a_given_figure() -> None:
    trace = computing().compute((Artifact(GIVEN, D("1500")), Artifact(FALLBACK, D("50000")))).trace

    assert trace == (
        GivenOrFallbackLine(
            output=OUTPUT,
            given=GIVEN,
            fallback=FALLBACK,
            given_was_blank=False,
            result=D("1500"),
        ),
    )


def test_traces_one_line_for_the_fallback() -> None:
    trace = computing().compute((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("50000")))).trace

    assert trace == (
        GivenOrFallbackLine(
            output=OUTPUT,
            given=GIVEN,
            fallback=FALLBACK,
            given_was_blank=True,
            result=D("50000"),
        ),
    )


def test_trace_amount_is_the_result_and_label_is_the_output_label() -> None:
    (line,) = computing().compute((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("50000")))).trace

    assert line.amount == D("50000")
    assert line.label == OUTPUT.label


def test_trace_holds_no_text() -> None:
    trace = computing().compute((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("50000")))).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_a_given_figure_reads_in_english() -> None:
    trace = computing().compute((Artifact(GIVEN, D("1500")), Artifact(FALLBACK, D("50000")))).trace

    assert EnglishTraceRenderer().render_all(trace) == ("given (1500.00), as given",)


def test_the_fallback_reads_in_english() -> None:
    trace = computing().compute((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("50000")))).trace

    assert EnglishTraceRenderer().render_all(trace) == (
        "given was left blank, so fallback (50000.00) is used",
    )


# --- a blank given figure ---------------------------------------------------------------------


def test_declares_that_only_the_given_figure_may_be_blank() -> None:
    assert GivenOrFallback.BLANK_ALLOWED == frozenset({"given"})


def test_without_a_rule_a_blank_given_figure_is_refused_naming_the_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'given'"):
        capability().run((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("1"))))


def test_pass_on_blanks_the_output() -> None:
    result = (
        capability()
        .with_blank_rules({"given": PASS_ON})
        .run((Artifact(GIVEN, BLANK), Artifact(FALLBACK, D("1"))))
    )

    assert result.outputs == (Artifact(OUTPUT, BLANK),)


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="'output'"):
        capability().with_blank_rules({"output": PASS_ON})
