"""Unit tests for the Subtract capability (`core/subtract`), with made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its rounding
rule), two consumed single slots, `amount` and `less`, and one produced slot `output`. The output is
amount − less, formed exactly on `Fraction`s and rounded once with the dataset's rule, which
defaults to no rounding; there is no floor, so a negative difference stays negative. It records
one `SubtractedLine` holding the rounding. Either consumed slot may be blank (`BLANK_ALLOWED`); the
rules the manifest gives decide what a blank does there.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import SubtractedLine
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.subtract import Subtract
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

GROSS = AmountKind("ex/gross_amount")
REDUCTION = AmountKind("ex/reduction")
NET = AmountKind("ex/net_amount")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/net_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> Subtract:
    """By default the made-up gross amount less the made-up reduction, exactly."""
    return Subtract(rounding_data or rounding(), GROSS, REDUCTION, NET)


def cents() -> Subtract:
    """The made-up difference with the dataset's rounding half-up to the cent."""
    return capability(rounding(CENT))


def inputs(amount: str, less: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(GROSS, D(amount)), Artifact(REDUCTION, D(less)))


def compute(amount: str, less: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, less)).outputs
    return output


def test_is_registered_as_core_subtract() -> None:
    assert bundled_capabilities().get("core/subtract") is Subtract


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({GROSS, REDUCTION})
    assert capability().produces == frozenset({NET})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Subtract)
    assert "produces" not in vars(Subtract)


def test_declares_its_slots() -> None:
    assert Subtract.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert Subtract.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert Subtract.CONSUMES == {"amount": Decimal, "less": Decimal}
    assert Subtract.PRODUCES == {"output": Decimal}
    assert not Subtract.is_list_slot("amount")
    assert not Subtract.is_list_slot("less")
    assert not Subtract.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (Subtract.PARAMETERS, Subtract.CONSUMES, Subtract.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(Subtract.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(Subtract.CONSUMES, Mapping[str, type])
    assert_type(Subtract.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (Subtract.PARAMETERS, Subtract.CONSUMES, Subtract.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = Subtract(rounding=rounding(), amount=GROSS, less=REDUCTION, output=NET)

    result = wired.compute(inputs("100", "30"))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_takes_its_rounding_dataset_first_then_the_amount_the_less_and_the_output() -> None:
    wired = Subtract(rounding(CENT), GROSS, REDUCTION, NET)

    result = wired.compute(inputs("0.015", "0.005"))

    assert result.outputs == (Artifact(NET, D("0.01")),)


def test_the_rounding_dataset_is_required() -> None:
    with pytest.raises(TypeError):
        Subtract(GROSS, REDUCTION, NET)  # type: ignore[call-arg]


def test_the_rounding_dataset_cannot_be_left_out_by_keyword() -> None:
    with pytest.raises(TypeError, match="rounding"):
        Subtract(amount=GROSS, less=REDUCTION, output=NET)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_less() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(rounding(), GROSS, GROSS, NET)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'less'" in message


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(rounding(), GROSS, REDUCTION, GROSS)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_less_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract") as raised:
        Subtract(rounding(), GROSS, REDUCTION, REDUCTION)

    message = str(raised.value)
    assert "'less'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'amount'"):
        Subtract(rounding(), (GROSS,), REDUCTION, NET)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_what_it_takes_off() -> None:
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'less'"):
        Subtract(rounding(), GROSS, (REDUCTION,), NET)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="Subtract.*'less'"):
        Subtract(rounding(), GROSS, count, NET)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(Subtract, "__type_params__", ())
    assert not getattr(Subtract, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_amount_less_the_other() -> None:
    assert compute("100.25", "40") == Artifact(NET, D("60.25"))


def test_equal_amounts_produce_zero() -> None:
    output = compute("40.50", "40.50")

    assert output == Artifact(NET, D("0"))
    assert type(output.value) is Decimal


def test_taking_off_zero_produces_the_amount() -> None:
    assert compute("1234.56", "0") == Artifact(NET, D("1234.56"))


def test_a_larger_less_produces_a_negative_result_without_a_floor() -> None:
    output = compute("10", "25.5")

    assert output == Artifact(NET, D("-15.5"))
    assert output.value < 0


def test_takes_a_negative_amount_off_as_is() -> None:
    assert compute("100", "-20") == Artifact(NET, D("120"))


def test_subtracts_exactly_with_many_decimals() -> None:
    output = compute("1234567.0000000000000003", "0.0000000000000001")

    assert output == Artifact(NET, D("1234567.0000000000000002"))
    assert type(output.value) is Decimal


def test_subtracts_decimals_float_would_not() -> None:
    assert compute("0.3", "0.1") == Artifact(NET, D("0.2"))


def test_does_not_round_the_difference() -> None:
    assert compute("0.005", "0.0049") == Artifact(NET, D("0.0001"))


def test_keeps_the_scale_of_the_exact_difference() -> None:
    assert str(compute("100.00", "40").value) == "60.00"


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("100", "30"))))

    assert result.outputs == (Artifact(NET, D("70")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("10", "4")))

    assert result.outputs == (Artifact(NET, D("6")),)


# --- computing, under the dataset's rounding rule -----------------------------------------------


def test_a_difference_is_rounded_half_up_to_the_cent_by_the_dataset() -> None:
    (output,) = cents().compute(inputs("0.015", "0.005")).outputs

    assert output == Artifact(NET, D("0.01"))
    assert str(output.value) == "0.01"


def test_a_difference_on_a_half_cent_rounds_up() -> None:
    (output,) = cents().compute(inputs("100.00", "99.995")).outputs

    assert str(output.value) == "0.01"


def test_a_whole_dollar_difference_takes_the_cent_scale() -> None:
    (output,) = cents().compute(inputs("70000", "665")).outputs

    assert output == Artifact(NET, D("69335.00"))
    assert str(output.value) == "69335.00"
    assert output.value.as_tuple().exponent == -2


def test_the_difference_is_rounded_once_not_each_input() -> None:
    # Rounded first, 0.014 and 0.005 are 0.01 and 0.01 and the difference is 0.00; the exact
    # difference 0.009 is 0.01.
    (output,) = cents().compute(inputs("0.014", "0.005")).outputs

    assert output == Artifact(NET, D("0.01"))


def test_a_sub_cent_difference_under_the_half_rounds_down() -> None:
    (output,) = cents().compute(inputs("0.0149", "0.01")).outputs

    assert str(output.value) == "0.00"


def test_a_difference_exactly_on_a_half_cent_is_rounded_by_the_rule_alone() -> None:
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert capability(rounding(CENT)).compute(inputs("0.015", "0.01")).outputs == (
        Artifact(NET, D("0.01")),
    )
    assert capability(rounding(half_even)).compute(inputs("0.015", "0.01")).outputs == (
        Artifact(NET, D("0.00")),
    )


def test_a_negative_difference_is_rounded_without_a_floor() -> None:
    (output,) = cents().compute(inputs("10", "25.5")).outputs

    assert output == Artifact(NET, D("-15.50"))
    assert str(output.value) == "-15.50"
    assert output.value < 0


def test_a_negative_sub_cent_difference_rounds_away_from_zero_on_the_half() -> None:
    # -0.015 is on the tie: half-up here means away from zero, as the rule does for any amount.
    (output,) = cents().compute(inputs("0.005", "0.02")).outputs

    assert output == Artifact(NET, D("-0.02"))


def test_a_negative_difference_under_half_a_cent_is_never_a_signed_zero() -> None:
    (output,) = cents().compute(inputs("0.001", "0.004")).outputs

    assert str(output.value) == "0.00"
    assert not output.value.is_signed()


def test_equal_amounts_under_the_cent_rule_give_0_00() -> None:
    (output,) = cents().compute(inputs("40.5", "40.5")).outputs

    assert str(output.value) == "0.00"
    assert output.value.as_tuple().exponent == -2


def test_rounds_with_another_rule_of_the_dataset() -> None:
    ceiling = capability(rounding(RoundTo(D("1"), RoundingMode.CEILING)))

    assert ceiling.compute(inputs("10.5", "0.2")).outputs == (Artifact(NET, D("11")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gross_amount"):
        capability().compute((Artifact(REDUCTION, D("1")),))


def test_a_missing_less_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="reduction"):
        capability().compute((Artifact(GROSS, D("1")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_subtracted_line() -> None:
    trace = capability().compute(inputs("100.25", "40")).trace

    assert trace == (
        SubtractedLine(
            output=NET,
            minuend=GROSS,
            minuend_amount=D("100.25"),
            subtrahend=REDUCTION,
            subtrahend_amount=D("40"),
            rounding=NO_ROUNDING,
            result=D("60.25"),
        ),
    )


def test_traces_the_cent_rounding_and_the_rounded_result() -> None:
    trace = cents().compute(inputs("100.25", "40")).trace

    assert trace == (
        SubtractedLine(
            output=NET,
            minuend=GROSS,
            minuend_amount=D("100.25"),
            subtrahend=REDUCTION,
            subtrahend_amount=D("40"),
            rounding=CENT,
            result=D("60.25"),
        ),
    )
    (line,) = trace
    assert isinstance(line, SubtractedLine)
    assert str(line.result) == "60.25"
    assert line.rounding == CENT


def test_traces_a_negative_result() -> None:
    trace = capability().compute(inputs("10", "25.5")).trace

    assert trace == (
        SubtractedLine(NET, GROSS, D("10"), REDUCTION, D("25.5"), NO_ROUNDING, D("-15.5")),
    )


def test_trace_amount_is_the_result() -> None:
    trace = cents().compute(inputs("10", "25.5")).trace

    assert [line.amount for line in trace] == [D("-15.50")]


def test_the_trace_reads_in_english_with_the_rounding_named() -> None:
    result = cents().compute(inputs("100.25", "40"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "net_amount: gross_amount 100.25 less reduction 40 = 60.25 (half-up to 0.01)",
    )


def test_the_trace_reads_in_english_with_no_rounding_named() -> None:
    result = capability().compute(inputs("10", "25.5"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "net_amount: gross_amount 10 less reduction 25.5 = -15.5 (no rounding)",
    )


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("100", "30")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- a blank in either slot ---------------------------------------------------------------------


def blank_input(kind: ArtifactKind[Decimal]) -> Artifact[Any]:
    return Artifact(kind, BLANK)


def test_declares_that_either_slot_may_be_blank() -> None:
    assert Subtract.BLANK_ALLOWED == frozenset({"amount", "less"})


def test_without_rules_a_blank_amount_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'gross_amount'.*'amount'"):
        capability().run((blank_input(GROSS), Artifact(REDUCTION, D(1))))


def test_without_rules_a_blank_less_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'reduction'.*'less'"):
        capability().run((Artifact(GROSS, D(1)), blank_input(REDUCTION)))


def test_pass_on_in_either_slot_blanks_the_difference() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "less": PASS_ON})

    for given in (
        (blank_input(GROSS), Artifact(REDUCTION, D(1))),
        (Artifact(GROSS, D(1)), blank_input(REDUCTION)),
    ):
        result = passing.run(given)
        assert result.outputs == (Artifact(NET, BLANK),)
        assert isinstance(result.trace[0], BlankPassedOnLine)


def test_a_declared_zero_for_less_reads_zero_and_the_trace_says_so() -> None:
    carried = capability().with_blank_rules({"less": D(0)})

    result = carried.run((Artifact(GROSS, D(508418)), blank_input(REDUCTION)))

    assert result.outputs == (Artifact(NET, D(508418)),)
    assert result.trace == (
        BlankFallbackLine(REDUCTION, D(0)),
        SubtractedLine(NET, GROSS, D(508418), REDUCTION, D(0), NO_ROUNDING, D(508418)),
    )


def test_a_zero_for_less_does_not_cover_a_blank_amount() -> None:
    carried = capability().with_blank_rules({"less": D(0)})

    with pytest.raises(BlankNotAllowedError, match="'amount'"):
        carried.run((blank_input(GROSS), Artifact(REDUCTION, D(1))))


def test_one_class_serves_both_uses_with_different_rules() -> None:
    given = (Artifact(GROSS, D(10)), blank_input(REDUCTION))

    assert capability().with_blank_rules({"less": D(0)}).run(given).outputs == (
        Artifact(NET, D(10)),
    )
    assert capability().with_blank_rules({"less": PASS_ON}).run(given).outputs == (
        Artifact(NET, BLANK),
    )


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="'output'"):
        capability().with_blank_rules({"output": PASS_ON})
