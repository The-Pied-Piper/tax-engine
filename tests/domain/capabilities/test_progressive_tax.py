"""Unit tests for the ProgressiveTax capability, with made-up brackets.

Its slots: parameter `schedule` (a brackets dataset, whose rounding rule it applies to the total),
consumed `base` and produced `output`. It computes the form's two lines for the bracket the base
falls in: the rate on the excess over the bracket's lower, plus the tax at the bracket's start,
which the schedule computes by its own rule. Its trace is one line for that bracket, then the
rounded total.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.progressive_tax import ProgressiveTax
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.trace import BracketColumnLine, RoundedTotalLine

D = Decimal


TAXABLE_BASE = ArtifactKind("ex/taxable_base", Decimal)
BASIC_TAX = ArtifactKind("ex/basic_tax", Decimal)
OTHER_BASE = ArtifactKind("ex/other_base", Decimal)
OTHER_TAX = ArtifactKind("ex/other_tax", Decimal)


SCHEDULE = BracketSchedule(
    (
        Bracket(D(0), D("0.10")),
        Bracket(D(100), D("0.20")),
        Bracket(D(300), D("0.30")),
    )
)

# 10.5% of 105 is 11.025, rounded half-up to the cent at the bracket's start: 11.03; plus 20.5% of
# 105 is 32.55.
ROUNDED = BracketSchedule(
    (
        Bracket(D(0), D("0.105")),
        Bracket(D(105), D("0.205")),
        Bracket(D(210), D("0.30")),
    ),
    RoundTo(D("0.01"), RoundingMode.HALF_UP),
)


def schedule(
    rounding: RoundingRule = NO_ROUNDING, values: BracketSchedule = SCHEDULE
) -> ParameterDataset[BracketSchedule]:
    return ParameterDataset(
        "ex/brackets", 2025, BRACKETS, values, rounding, ("https://example.org/rates",)
    )


def capability(
    rounding: RoundingRule = NO_ROUNDING, values: BracketSchedule = SCHEDULE
) -> ProgressiveTax:
    return ProgressiveTax(TAXABLE_BASE, BASIC_TAX, schedule(rounding, values))


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TAXABLE_BASE})
    assert capability().produces == frozenset({BASIC_TAX})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ProgressiveTax)
    assert "produces" not in vars(ProgressiveTax)


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ProgressiveTax") as raised:
        ProgressiveTax(TAXABLE_BASE, TAXABLE_BASE, schedule())

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_produces_tax_on_the_base() -> None:
    result = capability().compute((Artifact(TAXABLE_BASE, D(250)),))

    assert result.outputs == (Artifact(BASIC_TAX, D("40.0")),)


def test_the_same_capability_serves_different_wiring() -> None:
    wired = ProgressiveTax(OTHER_BASE, OTHER_TAX, schedule())

    result = wired.compute((Artifact(OTHER_BASE, D(50)),))

    assert result.outputs == (Artifact(OTHER_TAX, D("5.0")),)


def test_adds_the_tax_at_the_brackets_start_to_the_rate_on_the_excess() -> None:
    # 20.5% of (150 - 105) = 9.225, plus the rounded 11.03, not the exact 11.025.
    result = capability(values=ROUNDED).compute((Artifact(TAXABLE_BASE, D(150)),))

    assert result.outputs == (Artifact(BASIC_TAX, D("20.255")),)


def test_a_base_at_a_threshold_is_taxed_in_the_lower_bracket() -> None:
    # 10.5% of 105 + 0 = 11.025, not the next bracket's 11.03.
    result = capability(values=ROUNDED).compute((Artifact(TAXABLE_BASE, D(105)),))

    assert result.outputs == (Artifact(BASIC_TAX, D("11.025")),)


def test_a_base_in_the_open_top_bracket_uses_its_tax_at_start() -> None:
    result = capability(values=ROUNDED).compute((Artifact(TAXABLE_BASE, D(310)),))

    assert result.outputs == (Artifact(BASIC_TAX, D("62.55")),)


def test_a_zero_base_is_taxed_nothing() -> None:
    result = capability().compute((Artifact(TAXABLE_BASE, D(0)),))

    assert result.outputs == (Artifact(BASIC_TAX, D(0)),)


def test_rounds_once_at_the_end_with_the_schedules_rule() -> None:
    cent = RoundTo(D("0.01"), RoundingMode.HALF_UP)
    # 20.5% of 45.01 = 9.22705, plus the rounded 11.03 = 20.25705 -> 20.26.
    result = capability(cent, ROUNDED).compute((Artifact(TAXABLE_BASE, D("150.01")),))

    assert result.outputs == (Artifact(BASIC_TAX, D("20.26")),)


def test_rounds_the_line_sum_not_the_product() -> None:
    cent = RoundTo(D("0.01"), RoundingMode.HALF_UP)
    # 20% of 0.025 = 0.005, plus 10.00 = 10.005 -> 10.01; rounding the product first gives 10.00.
    result = capability(cent).compute((Artifact(TAXABLE_BASE, D("100.025")),))

    assert result.outputs == (Artifact(BASIC_TAX, D("10.01")),)


def test_without_a_rule_the_tax_stays_exact() -> None:
    result = capability().compute((Artifact(TAXABLE_BASE, D("100.025")),))

    assert result.outputs == (Artifact(BASIC_TAX, D("10.0050")),)


def test_traces_the_bracket_the_base_falls_in_and_the_total() -> None:
    cent = RoundTo(D("0.01"), RoundingMode.HALF_UP)

    trace = capability(cent).compute((Artifact(TAXABLE_BASE, D(250)),)).trace

    assert trace == (
        BracketColumnLine(
            lower=D(100), rate=D("0.20"), excess=D(150), tax_at_start=D("10.00"), tax=D("40.00")
        ),
        RoundedTotalLine(
            output=BASIC_TAX,
            base=TAXABLE_BASE,
            base_amount=D(250),
            rounding=cent,
            total=D("40.00"),
        ),
    )


def test_traces_one_bracket_line_however_many_brackets_the_base_spans() -> None:
    trace = capability().compute((Artifact(TAXABLE_BASE, D(1000)),)).trace

    assert [type(line) for line in trace] == [BracketColumnLine, RoundedTotalLine]


def test_trace_records_the_computed_tax_at_start() -> None:
    trace = capability(values=ROUNDED).compute((Artifact(TAXABLE_BASE, D(150)),)).trace

    assert trace[0] == BracketColumnLine(D(105), D("0.205"), D(45), D("11.03"), D("20.255"))


def test_trace_records_the_open_top_bracket() -> None:
    trace = capability().compute((Artifact(TAXABLE_BASE, D(400)),)).trace

    assert trace == (
        BracketColumnLine(D(300), D("0.30"), D(100), D("50.00"), D("80.00")),
        RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(400), NO_ROUNDING, D("80.0")),
    )


def test_trace_records_a_zero_base_in_the_first_bracket() -> None:
    trace = capability().compute((Artifact(TAXABLE_BASE, D(0)),)).trace

    assert trace == (
        BracketColumnLine(D(0), D("0.10"), D(0), D(0), D(0)),
        RoundedTotalLine(BASIC_TAX, TAXABLE_BASE, D(0), NO_ROUNDING, D(0)),
    )


def test_trace_records_the_wired_kinds() -> None:
    wired = ProgressiveTax(OTHER_BASE, OTHER_TAX, schedule())

    trace = wired.compute((Artifact(OTHER_BASE, D(50)),)).trace

    assert trace == (
        BracketColumnLine(D(0), D("0.10"), D(50), D(0), D("5.0")),
        RoundedTotalLine(OTHER_TAX, OTHER_BASE, D(50), NO_ROUNDING, D("5.0")),
    )


def test_trace_amounts_are_the_brackets_tax_and_the_total() -> None:
    cent = RoundTo(D("0.01"), RoundingMode.HALF_UP)

    trace = capability(cent, ROUNDED).compute((Artifact(TAXABLE_BASE, D(150)),)).trace

    assert [line.amount for line in trace] == [D("20.255"), D("20.26")]


def test_the_traced_bracket_line_holds_no_upper_bound() -> None:
    (line, _) = capability().compute((Artifact(TAXABLE_BASE, D(250)),)).trace

    assert "upper" not in [f.name for f in fields(line)]


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(TAXABLE_BASE, D(400)),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_rejects_negative_base() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        capability().compute((Artifact(TAXABLE_BASE, D(-1)),))


def test_declares_its_slots() -> None:
    assert ProgressiveTax.PARAMETERS == {"schedule": BRACKETS}
    assert ProgressiveTax.PARAMETERS["schedule"] is BRACKETS
    assert ProgressiveTax.CONSUMES == {"base": Decimal}
    assert ProgressiveTax.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for slots in (ProgressiveTax.PARAMETERS, ProgressiveTax.CONSUMES, ProgressiveTax.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ProgressiveTax.PARAMETERS, Mapping[str, ParameterKind[BracketSchedule]])
    assert_type(ProgressiveTax.CONSUMES, Mapping[str, type])
    assert_type(ProgressiveTax.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ProgressiveTax.PARAMETERS, ProgressiveTax.CONSUMES, ProgressiveTax.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ProgressiveTax(base=TAXABLE_BASE, output=BASIC_TAX, schedule=schedule())

    result = wired.compute((Artifact(TAXABLE_BASE, D(250)),))

    assert result.outputs == (Artifact(BASIC_TAX, D("40.0")),)


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ProgressiveTax(TAXABLE_BASE, BASIC_TAX, schedule(), NO_ROUNDING)  # type: ignore[call-arg]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ProgressiveTax, "__type_params__", ())
    assert not getattr(ProgressiveTax, "__parameters__", ())


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="ProgressiveTax.*'base'"):
        ProgressiveTax(count, BASIC_TAX, schedule())  # type: ignore[arg-type]


class Cents(Decimal):
    """A made-up Decimal subtype, to probe ArtifactKind's variance."""


CENTS = ArtifactKind("ex/cents", Cents)  # bound to a name: built inline it would infer Decimal


def test_mypy_rejects_wiring_an_artifact_kind_of_a_value_subtype() -> None:
    # `ArtifactKind` is invariant, so an ArtifactKind[Cents] is not Money; if `ArtifactKind` ever
    # became covariant this ignore would be unused and mypy (strict) would fail. At run time,
    # building it fails too: the value type must match the slot's exactly.
    with pytest.raises(InvalidCapabilityError, match="ProgressiveTax.*'base'"):
        ProgressiveTax(CENTS, BASIC_TAX, schedule())  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_kind_for_the_schedule() -> None:
    credit = ParameterDataset("ex/credit", 2025, CREDIT, Credit(D(1)), NO_ROUNDING, ("src",))

    def wire() -> None:  # type-checked, never run
        # A credit dataset is not a ParameterDataset[BracketSchedule]; the ignore fails under
        # mypy (warn_unused_ignores) if it is ever accepted.
        ProgressiveTax(TAXABLE_BASE, BASIC_TAX, credit)  # type: ignore[arg-type]

    assert callable(wire)


def test_mypy_rejects_a_bare_schedule_without_its_dataset() -> None:
    def wire() -> None:  # type-checked, never run
        # Parameter slots take the dataset, which carries the rounding rule; never bare values.
        ProgressiveTax(TAXABLE_BASE, BASIC_TAX, SCHEDULE)  # type: ignore[arg-type]

    assert callable(wire)
