"""Unit tests for the TimesCount capability (`core/times_count`), with made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its rounding
rule), two consumed single slots, `amount` (a `Decimal` artifact, the amount for each person) and
`count` (an `int` artifact, the number of persons), and one produced slot `output`. The output is
`rounding.apply(amount × count)`: the product is formed exactly, on `Fraction`s, and rounded once by
the dataset's rule, which defaults to no rounding. A count of 0 is not special: it gives the rule's
zero, so a cent rule gives 0.00. A zero is never a signed zero. It records one `TimesCountLine`
holding the amount's kind and value, the count's kind, the count, the rounding and the result.
Either consumed slot may be blank (`BLANK_ALLOWED`); the rules the manifest gives decide what a
blank does there.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
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
from tax_engine.domain.trace import PerUnitAmountLine, TimesCountLine
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.times_count import TimesCount
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

EACH = AmountKind("ex/amount_each")
PERSONS = CountKind("ex/person_count")
CLAIMED = AmountKind("ex/amount_claimed")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/claimed_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> TimesCount:
    """By default the made-up amount for each person, times the made-up count, exact."""
    return TimesCount(rounding_data or rounding(), EACH, PERSONS, CLAIMED)


def cents() -> TimesCount:
    """The made-up capability with its dataset rounding half-up to the cent."""
    return capability(rounding(CENT))


def inputs(amount: str, count: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(EACH, D(amount)), Artifact(PERSONS, count))


def compute(amount: str, count: int, wired: TimesCount | None = None) -> Artifact[Any]:
    (output,) = (wired or capability()).compute(inputs(amount, count)).outputs
    return output


def test_is_registered_as_core_times_count() -> None:
    assert bundled_capabilities().get("core/times_count") is TimesCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({EACH, PERSONS})
    assert capability().produces == frozenset({CLAIMED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TimesCount)
    assert "produces" not in vars(TimesCount)


def test_declares_its_slots() -> None:
    assert TimesCount.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert TimesCount.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert TimesCount.CONSUMES == {"amount": Decimal, "count": int}
    assert TimesCount.CONSUMES["count"] is int
    assert TimesCount.PRODUCES == {"output": Decimal}
    assert not TimesCount.is_list_slot("amount")
    assert not TimesCount.is_list_slot("count")
    assert not TimesCount.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (TimesCount.PARAMETERS, TimesCount.CONSUMES, TimesCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TimesCount.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(TimesCount.CONSUMES, Mapping[str, type])
    assert_type(TimesCount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (TimesCount.PARAMETERS, TimesCount.CONSUMES, TimesCount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TimesCount(rounding=rounding(), amount=EACH, count=PERSONS, output=CLAIMED)

    result = wired.compute(inputs("16129", 2))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_takes_its_rounding_dataset_first_then_the_amount_count_and_output() -> None:
    wired = TimesCount(rounding(CENT), EACH, PERSONS, CLAIMED)

    result = wired.compute(inputs("0.005", 1))

    assert result.outputs == (Artifact(CLAIMED, D("0.01")),)


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount") as raised:
        TimesCount(rounding(), EACH, PERSONS, EACH)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'amount'"):
        TimesCount(rounding(), (EACH,), PERSONS, CLAIMED)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'count'"):
        TimesCount(rounding(), EACH, (PERSONS,), CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_its_count() -> None:
    money = AmountKind("ex/money_count")
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'count'"):
        TimesCount(rounding(), EACH, money, CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_amount() -> None:
    other_count = CountKind("ex/other_count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'amount'"):
        TimesCount(rounding(), other_count, PERSONS, CLAIMED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_output() -> None:
    other_count = CountKind("ex/other_count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="TimesCount.*'output'"):
        TimesCount(rounding(), EACH, PERSONS, other_count)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(TimesCount, "__type_params__", ())
    assert not getattr(TimesCount, "__parameters__", ())


# --- computing, with no rounding --------------------------------------------------------------


def test_a_count_of_one_gets_the_amount() -> None:
    output = compute("16129", 1)

    assert output == Artifact(CLAIMED, D("16129"))
    assert type(output.value) is Decimal


def test_a_count_of_two_gets_twice_the_amount() -> None:
    # 16129 × 2 = 32258.
    assert compute("16129", 2) == Artifact(CLAIMED, D("32258"))


def test_a_larger_count_multiplies_the_amount() -> None:
    # 544 × 7 = 3808.
    assert compute("544", 7) == Artifact(CLAIMED, D("3808"))


def test_a_count_of_zero_gets_zero() -> None:
    output = compute("16129", 0)

    assert output == Artifact(CLAIMED, D("0"))
    assert type(output.value) is Decimal


def test_a_count_of_zero_gets_a_plain_zero_without_a_rule() -> None:
    output = compute("16129.50", 0)

    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_a_count_of_zero_of_a_negative_amount_is_never_a_signed_zero() -> None:
    output = compute("-250.75", 0)

    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_a_zero_amount_gets_zero_for_any_count() -> None:
    assert compute("0", 0) == Artifact(CLAIMED, D("0"))
    assert compute("0", 3) == Artifact(CLAIMED, D("0"))
    assert not compute("0", 3).value.is_signed()


def test_a_negative_amount_is_multiplied_as_is_without_a_floor() -> None:
    # -250.75 × 2 = -501.5: the amount is not floored at zero first, nor the product.
    assert compute("-250.75", 2) == Artifact(CLAIMED, D("-501.5"))


def test_keeps_fractions_of_a_cent_exactly_without_a_rule() -> None:
    # 0.333 × 3 = 0.999, not rounded.
    assert str(compute("0.333", 3).value) == "0.999"


def test_keeps_the_product_exact_without_a_rule() -> None:
    output = compute("1234567.0000000000000001", 3)

    assert str(output.value) == "3703701.0000000000000003"


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("16129", 2))))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("16129", 2)))

    assert result.outputs == (Artifact(CLAIMED, D("32258")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_each"):
        capability().compute((Artifact(PERSONS, 1),))


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="person_count"):
        capability().compute((Artifact(EACH, D("16129")),))


# --- computing, under the dataset's rounding rule ---------------------------------------------


def test_a_whole_dollar_amount_takes_the_cent_scale() -> None:
    output = compute("70000", 1, cents())

    assert output == Artifact(CLAIMED, D("70000.00"))
    assert str(output.value) == "70000.00"
    assert output.value.as_tuple().exponent == -2


def test_a_whole_dollar_amount_of_20000_takes_the_cent_scale() -> None:
    output = compute("20000", 1, cents())

    assert str(output.value) == "20000.00"
    assert output.value.as_tuple().exponent == -2


def test_a_count_of_zero_gets_the_rules_zero_not_a_plain_zero() -> None:
    # The old rule gave a plain 0 for a count of 0; the rule's zero is 0.00 under the cent rule.
    output = compute("16129", 0, cents())

    assert output == Artifact(CLAIMED, D("0.00"))
    assert str(output.value) == "0.00"
    assert output.value.as_tuple().exponent == -2


def test_a_count_of_zero_of_a_negative_amount_is_a_cent_zero_never_signed() -> None:
    output = compute("-250.75", 0, cents())

    assert str(output.value) == "0.00"
    assert not output.value.is_signed()


def test_a_zero_amount_under_the_cent_rule_gives_0_00_for_any_count() -> None:
    assert str(compute("0", 0, cents()).value) == "0.00"
    assert str(compute("0", 3, cents()).value) == "0.00"


def test_a_negative_product_is_rounded_half_up_to_the_cent_without_a_floor() -> None:
    # -250.75 × 2 = -501.50: the sign is kept, and the cent rule gives its scale.
    assert str(compute("-250.75", 2, cents()).value) == "-501.50"


def test_keeps_the_amounts_scale_under_the_cent_rule() -> None:
    assert str(compute("16129.50", 1, cents()).value) == "16129.50"
    assert str(compute("16129.50", 2, cents()).value) == "32259.00"


def test_rounds_the_product_once_not_each_amount() -> None:
    # 0.005 × 3 is 0.015, which sits on the half-cent and rounds up to 0.02; rounding the amount
    # first would give 0.01 × 3 = 0.03.
    assert compute("0.005", 3, cents()) == Artifact(CLAIMED, D("0.02"))


def test_a_sub_cent_product_rounds_half_up_to_the_cent() -> None:
    # 0.333 × 3 is 0.999, which rounds up to 1.00.
    assert str(compute("0.333", 3, cents()).value) == "1.00"


def test_a_sub_cent_product_under_the_half_rounds_down() -> None:
    assert str(compute("0.004", 1, cents()).value) == "0.00"


def test_the_cent_rule_is_applied_to_an_exact_product_with_many_decimals() -> None:
    assert str(compute("1234567.0000000000000001", 3, cents()).value) == "3703701.00"


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_times_count_line() -> None:
    trace = capability().compute(inputs("16129", 1)).trace

    assert trace == (
        TimesCountLine(
            output=CLAIMED,
            amount_kind=EACH,
            amount_value=D("16129"),
            count_kind=PERSONS,
            count=1,
            rounding=NO_ROUNDING,
            result=D("16129"),
        ),
    )


def test_traces_a_count_of_zero_under_the_cent_rule() -> None:
    trace = cents().compute(inputs("16129.50", 0)).trace

    assert trace == (
        TimesCountLine(
            output=CLAIMED,
            amount_kind=EACH,
            amount_value=D("16129.50"),
            count_kind=PERSONS,
            count=0,
            rounding=CENT,
            result=D("0.00"),
        ),
    )
    (line,) = trace
    assert isinstance(line, TimesCountLine)
    assert str(line.result) == "0.00"


def test_traces_the_amount_with_its_own_scale() -> None:
    (line,) = cents().compute(inputs("16129.50", 2)).trace

    assert isinstance(line, TimesCountLine)
    assert str(line.amount_value) == "16129.50"
    assert str(line.result) == "32259.00"


def test_traces_the_count_as_an_int() -> None:
    (line,) = capability().compute(inputs("16129", 3)).trace

    assert isinstance(line, TimesCountLine)
    assert type(line.count) is int
    assert line.count == 3


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute(inputs("16129", 2)).trace

    assert [line.amount for line in trace] == [D("32258")]


def test_trace_result_is_the_output() -> None:
    result = cents().compute(inputs("16129.50", 2))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, TimesCountLine)
    assert line.result == output.value
    assert str(line.result) == str(output.value)


def test_traces_no_per_unit_amount_line() -> None:
    (line,) = capability().compute(inputs("16129", 1)).trace

    assert not isinstance(line, PerUnitAmountLine)


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("16129", 1)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_the_trace_reads_in_english_with_the_rounding_named() -> None:
    result = cents().compute(inputs("16129", 2))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "amount_claimed: amount_each 16129 for each of 2 person_count = 32258 (half-up to 0.01)",
    )


def test_the_trace_reads_in_english_for_a_count_of_zero() -> None:
    result = cents().compute(inputs("16129.50", 0))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "amount_claimed: amount_each 16129.5 for each of 0 person_count = 0 (half-up to 0.01)",
    )


def test_the_trace_reads_in_english_with_no_rounding() -> None:
    result = capability().compute(inputs("16129", 2))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "amount_claimed: amount_each 16129 for each of 2 person_count = 32258 (no rounding)",
    )


# --- a blank in either slot ---------------------------------------------------------------------


def blank_amount() -> Artifact[Any]:
    return Artifact(EACH, BLANK)


def blank_count() -> Artifact[Any]:
    return Artifact(PERSONS, BLANK)


def test_declares_that_either_slot_may_be_blank() -> None:
    assert TimesCount.BLANK_ALLOWED == frozenset({"amount", "count"})


def test_without_rules_a_blank_count_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'person_count'.*'count'"):
        capability().run((Artifact(EACH, D(5)), blank_count()))


def test_without_rules_a_blank_amount_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'amount_each'.*'amount'"):
        capability().run((blank_amount(), Artifact(PERSONS, 1)))


def test_pass_on_in_either_slot_blanks_the_output() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "count": PASS_ON})

    for given in (
        (blank_amount(), Artifact(PERSONS, 1)),
        (Artifact(EACH, D(5)), blank_count()),
    ):
        result = passing.run(given)
        assert result.outputs == (Artifact(CLAIMED, BLANK),)
        assert isinstance(result.trace[0], BlankPassedOnLine)
        assert not any(isinstance(line, TimesCountLine) for line in result.trace)


def test_a_blank_count_is_not_a_count_of_zero() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "count": PASS_ON})

    assert passing.run((Artifact(EACH, D(5)), blank_count())).outputs == (Artifact(CLAIMED, BLANK),)
    assert passing.run((Artifact(EACH, D(5)), Artifact(PERSONS, 0))).outputs == (
        Artifact(CLAIMED, D(0)),
    )


def test_a_blank_in_both_slots_passes_on_once() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "count": PASS_ON})

    result = passing.run((blank_amount(), blank_count()))

    assert result.outputs == (Artifact(CLAIMED, BLANK),)
    assert result.trace == (BlankPassedOnLine(CLAIMED, (EACH, PERSONS)),)


def test_a_fallback_for_count_is_applied_and_the_product_formed() -> None:
    carried = capability().with_blank_rules({"count": 1})

    result = carried.run((Artifact(EACH, D(5)), blank_count()))

    assert result.outputs == (Artifact(CLAIMED, D(5)),)
    assert result.trace[0] == BlankFallbackLine(PERSONS, 1)
    assert isinstance(result.trace[1], TimesCountLine)


def test_a_fallback_for_count_under_the_cent_rule_takes_the_cent_scale() -> None:
    carried = cents().with_blank_rules({"count": 1})

    (output,) = carried.run((Artifact(EACH, D("70000")), blank_count())).outputs

    assert str(output.value) == "70000.00"


def test_a_fallback_for_count_does_not_cover_a_blank_amount() -> None:
    carried = capability().with_blank_rules({"count": 1})

    with pytest.raises(BlankNotAllowedError, match="'amount'"):
        carried.run((blank_amount(), Artifact(PERSONS, 1)))


def test_pass_on_wins_over_a_fallback_in_the_other_slot() -> None:
    mixed = capability().with_blank_rules({"amount": PASS_ON, "count": 0})

    result = mixed.run((blank_amount(), blank_count()))

    assert result.outputs == (Artifact(CLAIMED, BLANK),)


def test_filled_values_are_multiplied_as_before_when_pass_on_is_declared() -> None:
    passing = capability().with_blank_rules({"amount": PASS_ON, "count": PASS_ON})

    assert passing.run(inputs("5.25", 2)).outputs == (Artifact(CLAIMED, D("10.50")),)


def test_a_rule_for_a_slot_that_is_not_consumed_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="'output'"):
        capability().with_blank_rules({"output": PASS_ON})
