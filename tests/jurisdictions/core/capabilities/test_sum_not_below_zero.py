"""Unit tests for the SumNotBelowZero capability (`core/sum_not_below_zero`), made-up kinds.

Its slots are those of `core/sum`: one parameter slot `rounding` (a `rounding_only` dataset), one
consumed list slot `parts` (a tuple of money kinds, possibly empty), one produced slot `output`.
The output is `rounding.apply(max(sum of the parts, 0))`, as `core/subtract_not_below_zero` does:
the parts are added on exact `Fraction`s, the total is floored at zero first, and the floored total
is rounded once with the dataset's rule (no rounding by default), so a floored zero takes the
rule's scale (0.00 under the cent rule). It records one `SumNotBelowZeroLine` holding each part in
the order it was wired, the rounding and the total, whether or not the floor applied.
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
from tax_engine.domain.trace import SumLine, SumNotBelowZeroLine
from tax_engine.domain.trace.blank import BlankFallbackLine, BlankPassedOnLine
from tax_engine.jurisdictions.core.capabilities.sum import Sum
from tax_engine.jurisdictions.core.capabilities.sum_not_below_zero import SumNotBelowZero
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


PART_ONE = AmountKind("ex/part_one")
PART_TWO = AmountKind("ex/part_two")
PART_THREE = AmountKind("ex/part_three")
TOTAL = AmountKind("ex/total")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/total_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> SumNotBelowZero:
    """By default the three made-up parts, in order one, two, three, summed exactly."""
    return SumNotBelowZero(rounding_data or rounding(), (PART_ONE, PART_TWO, PART_THREE), TOTAL)


def cents() -> SumNotBelowZero:
    """The made-up three parts with the dataset's rounding half-up to the cent."""
    return capability(rounding(CENT))


def parts(one: str, two: str, three: str) -> tuple[Artifact[Decimal], ...]:
    return (
        Artifact(PART_ONE, D(one)),
        Artifact(PART_TWO, D(two)),
        Artifact(PART_THREE, D(three)),
    )


def compute(one: str, two: str, three: str, wired: SumNotBelowZero | None = None) -> Artifact[Any]:
    (output,) = (wired or capability()).compute(parts(one, two, three)).outputs
    return output


def test_is_registered_as_core_sum_not_below_zero() -> None:
    assert bundled_capabilities().get("core/sum_not_below_zero") is SumNotBelowZero


def test_leaves_core_sum_registered_as_the_unfloored_sum() -> None:
    assert bundled_capabilities().get("core/sum") is Sum


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PART_ONE, PART_TWO, PART_THREE})
    assert capability().produces == frozenset({TOTAL})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(SumNotBelowZero)
    assert "produces" not in vars(SumNotBelowZero)


def test_declares_the_slots_of_core_sum() -> None:
    assert SumNotBelowZero.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert SumNotBelowZero.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert SumNotBelowZero.CONSUMES == {"parts": list[Decimal]}
    assert SumNotBelowZero.PRODUCES == {"output": Decimal}
    assert SumNotBelowZero.is_list_slot("parts")
    assert not SumNotBelowZero.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (
        SumNotBelowZero.PARAMETERS,
        SumNotBelowZero.CONSUMES,
        SumNotBelowZero.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(SumNotBelowZero.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(SumNotBelowZero.CONSUMES, Mapping[str, type])
    assert_type(SumNotBelowZero.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (
        SumNotBelowZero.PARAMETERS,
        SumNotBelowZero.CONSUMES,
        SumNotBelowZero.PRODUCES,
    ):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = SumNotBelowZero(
        rounding=rounding(),
        parts=(PART_ONE, PART_TWO, PART_THREE),
        output=TOTAL,
    )

    result = wired.compute(parts("100.25", "40", "9.75"))

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_takes_its_rounding_dataset_first_then_the_parts_and_the_output() -> None:
    wired = SumNotBelowZero(rounding(CENT), (PART_ONE,), TOTAL)

    result = wired.compute((Artifact(PART_ONE, D("0.005")),))

    assert result.outputs == (Artifact(TOTAL, D("0.01")),)


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        SumNotBelowZero(rounding(), (PART_ONE,), TOTAL, NO_ROUNDING)  # type: ignore[call-arg]


def test_cannot_be_wired_without_a_rounding_dataset() -> None:
    with pytest.raises(TypeError):
        SumNotBelowZero((PART_ONE,), TOTAL)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_a_part_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero") as raised:
        SumNotBelowZero(rounding(), (PART_ONE, TOTAL), TOTAL)

    message = str(raised.value)
    assert "'parts'" in message
    assert "'output'" in message


def test_rejects_a_part_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero(rounding(), (PART_ONE, PART_TWO, PART_ONE), TOTAL)


def test_rejects_a_single_kind_for_its_parts() -> None:
    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero(rounding(), PART_ONE, TOTAL)  # type: ignore[arg-type]


def test_rejects_a_part_of_another_value_type() -> None:
    count = CountKind("ex/count")

    with pytest.raises(InvalidCapabilityError, match="SumNotBelowZero.*'parts'"):
        SumNotBelowZero(rounding(), (PART_ONE, count), TOTAL)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(SumNotBelowZero, "__type_params__", ())
    assert not getattr(SumNotBelowZero, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_positive_total_is_produced_unchanged() -> None:
    assert compute("100.25", "40", "9.75") == Artifact(TOTAL, D("150.00"))


def test_a_positive_total_takes_the_scale_of_the_rule() -> None:
    value = compute("100.25", "40", "9.75", cents()).value

    assert str(value) == "150.00"
    assert value.as_tuple().exponent == -2


def test_negative_parts_are_added_as_they_are() -> None:
    assert compute("100", "-30", "-20.5") == Artifact(TOTAL, D("49.5"))


def test_one_part_is_its_own_total() -> None:
    wired = SumNotBelowZero(rounding(), (PART_TWO,), TOTAL)

    result = wired.compute((Artifact(PART_TWO, D("40.5")),))

    assert result.outputs == (Artifact(TOTAL, D("40.5")),)


def test_one_negative_part_is_floored_at_zero() -> None:
    wired = SumNotBelowZero(rounding(), (PART_TWO,), TOTAL)

    result = wired.compute((Artifact(PART_TWO, D("-40.5")),))

    assert result.outputs == (Artifact(TOTAL, D("0")),)


def test_a_negative_total_is_floored_at_zero() -> None:
    output = compute("10", "-25.5", "5")

    assert output == Artifact(TOTAL, D("0"))
    assert type(output.value) is Decimal


def test_the_floor_is_a_plain_decimal_zero() -> None:
    # Like `core/subtract_not_below_zero`: when the floor applies, the output is `Decimal(0)`,
    # not the sum's scale (no "0.00") and never a negative zero.
    value = compute("10.00", "-25.50", "5.00").value

    assert type(value) is Decimal
    assert str(value) == "0"
    assert not value.is_signed()


def test_a_total_of_exactly_zero_is_a_plain_zero() -> None:
    # A tie at zero is never signed: -0.00 + 0.00 style sums give a plain 0.
    value = compute("40.50", "-40.50", "0.00").value

    assert value == D("0")
    assert str(value) == "0"
    assert not value.is_signed()


def test_negative_zero_parts_give_a_plain_zero() -> None:
    value = compute("-0", "-0.00", "0").value

    assert str(value) == "0"
    assert not value.is_signed()


def test_a_total_just_below_zero_is_floored() -> None:
    assert compute("0.0000000000000001", "-0.0000000000000002", "0") == Artifact(TOTAL, D("0"))


def test_zero_parts_sum_to_zero() -> None:
    wired = SumNotBelowZero(rounding(), (), TOTAL)

    result = wired.compute(())

    assert result.outputs == (Artifact(TOTAL, D(0)),)
    assert type(result.outputs[0].value) is Decimal
    assert str(result.outputs[0].value) == "0"
    assert wired.consumes == frozenset()


def test_adds_exactly_with_many_decimals() -> None:
    output = compute("0.1", "0.2", "1234567.0000000000000001")

    assert output == Artifact(TOTAL, D("1234567.3000000000000001"))


def test_adds_decimals_float_would_not() -> None:
    assert compute("0.1", "0.2", "0") == Artifact(TOTAL, D("0.3"))


def test_does_not_round_the_total_without_a_rule() -> None:
    wired = SumNotBelowZero(rounding(), (PART_ONE, PART_TWO), TOTAL)

    result = wired.compute((Artifact(PART_ONE, D("0.005")), Artifact(PART_TWO, D("0.0049"))))

    assert result.outputs == (Artifact(TOTAL, D("0.0099")),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(parts("100.25", "40", "9.75"))))

    assert result.outputs == (Artifact(TOTAL, D("150.00")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *parts("1", "2", "3")))

    assert result.outputs == (Artifact(TOTAL, D("6")),)


def test_a_missing_part_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="part_three"):
        capability().compute(parts("1", "2", "3")[:2])


# --- computing, under the dataset's rounding rule ---------------------------------------------
# The total is floored at zero and then rounded once, as `core/subtract_not_below_zero` does.


def test_a_total_is_rounded_half_up_to_the_cent_by_the_dataset() -> None:
    wired = SumNotBelowZero(rounding(CENT), (PART_ONE,), TOTAL)

    output = wired.compute((Artifact(PART_ONE, D("0.005")),)).outputs[0]

    assert output == Artifact(TOTAL, D("0.01"))
    assert str(output.value) == "0.01"


def test_a_whole_dollar_total_takes_the_cent_scale() -> None:
    wired = SumNotBelowZero(rounding(CENT), (PART_ONE,), TOTAL)

    (output,) = wired.compute((Artifact(PART_ONE, D("69335")),)).outputs

    assert str(output.value) == "69335.00"
    assert output.value.as_tuple().exponent == -2


def test_the_total_is_rounded_once_not_each_part() -> None:
    # Each part is under half a cent and would round to 0.00; the exact total 0.008 is 0.01.
    wired = SumNotBelowZero(rounding(CENT), (PART_ONE, PART_TWO), TOTAL)

    (output,) = wired.compute(
        (Artifact(PART_ONE, D("0.004")), Artifact(PART_TWO, D("0.004")))
    ).outputs

    assert output == Artifact(TOTAL, D("0.01"))


def test_a_negative_total_is_floored_to_the_cent_zero() -> None:
    output = compute("10", "-25.5", "5", cents())

    assert output == Artifact(TOTAL, D("0"))
    assert str(output.value) == "0.00"
    assert output.value.as_tuple().exponent == -2
    assert not output.value.is_signed()


def test_a_total_of_exactly_zero_is_the_cent_zero() -> None:
    assert str(compute("40.50", "-40.50", "0.00", cents()).value) == "0.00"


def test_zero_parts_under_the_cent_rule_give_0_00() -> None:
    (output,) = SumNotBelowZero(rounding(CENT), (), TOTAL).compute(()).outputs

    assert str(output.value) == "0.00"
    assert output.value.as_tuple().exponent == -2


def test_a_total_just_below_zero_is_floored_before_the_rule_and_never_signed() -> None:
    # -0.004 is floored to 0 and then rounded: a zero, never -0.00.
    value = compute("0.00", "-0.004", "0", cents()).value

    assert str(value) == "0.00"
    assert not value.is_signed()


def test_a_total_exactly_on_a_half_cent_is_rounded_by_the_rule_alone() -> None:
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)
    given = (Artifact(PART_ONE, D("0.005")),)

    assert SumNotBelowZero(rounding(CENT), (PART_ONE,), TOTAL).compute(given).outputs == (
        Artifact(TOTAL, D("0.01")),
    )
    assert SumNotBelowZero(rounding(half_even), (PART_ONE,), TOTAL).compute(given).outputs == (
        Artifact(TOTAL, D("0.00")),
    )


def test_rounds_with_another_rule_of_the_dataset() -> None:
    ceiling = SumNotBelowZero(rounding(RoundTo(D("1"), RoundingMode.CEILING)), (PART_ONE,), TOTAL)

    assert ceiling.compute((Artifact(PART_ONE, D("10.2")),)).outputs == (Artifact(TOTAL, D("11")),)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_part_and_the_total() -> None:
    trace = capability().compute(parts("100.25", "40", "9.75")).trace

    assert trace == (
        SumNotBelowZeroLine(
            output=TOTAL,
            parts=((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
            rounding=NO_ROUNDING,
            total=D("150.00"),
        ),
    )


def test_traces_the_floored_total() -> None:
    trace = capability().compute(parts("10", "-25.5", "5")).trace

    assert trace == (
        SumNotBelowZeroLine(
            TOTAL,
            ((PART_ONE, D("10")), (PART_TWO, D("-25.5")), (PART_THREE, D("5"))),
            NO_ROUNDING,
            D("0"),
        ),
    )


def test_traces_the_parts_in_the_order_they_were_wired() -> None:
    wired = SumNotBelowZero(rounding(), (PART_THREE, PART_ONE, PART_TWO), TOTAL)

    trace = wired.compute(parts("100.25", "40", "9.75")).trace

    assert trace == (
        SumNotBelowZeroLine(
            TOTAL,
            ((PART_THREE, D("9.75")), (PART_ONE, D("100.25")), (PART_TWO, D("40"))),
            NO_ROUNDING,
            D("150.00"),
        ),
    )


def test_traces_zero_parts() -> None:
    trace = SumNotBelowZero(rounding(), (), TOTAL).compute(()).trace

    assert trace == (SumNotBelowZeroLine(TOTAL, (), NO_ROUNDING, D(0)),)


def test_traces_the_cent_rounding_and_the_rounded_total() -> None:
    trace = cents().compute(parts("100.25", "40", "9.75")).trace

    assert trace == (
        SumNotBelowZeroLine(
            output=TOTAL,
            parts=((PART_ONE, D("100.25")), (PART_TWO, D("40")), (PART_THREE, D("9.75"))),
            rounding=CENT,
            total=D("150.00"),
        ),
    )
    (line,) = trace
    assert isinstance(line, SumNotBelowZeroLine)
    assert str(line.total) == "150.00"


def test_traces_the_floored_cent_zero() -> None:
    (line,) = cents().compute(parts("10", "-25.5", "5")).trace

    assert isinstance(line, SumNotBelowZeroLine)
    assert line.rounding == CENT
    assert str(line.total) == "0.00"


def test_traces_a_floored_line_not_a_plain_sum_line() -> None:
    (line,) = capability().compute(parts("10", "-25.5", "5")).trace

    assert type(line) is SumNotBelowZeroLine
    assert cast(Any, line) != SumLine(
        TOTAL,
        ((PART_ONE, D("10")), (PART_TWO, D("-25.5")), (PART_THREE, D("5"))),
        NO_ROUNDING,
        D("0"),
    )


def test_trace_amount_is_the_floored_total() -> None:
    trace = cents().compute(parts("10", "-25.5", "5")).trace

    assert [line.amount for line in trace] == [D("0.00")]
    assert str(trace[0].amount) == "0.00"


def test_trace_total_is_the_output() -> None:
    result = capability().compute(parts("100.25", "40", "9.75"))

    assert [line.amount for line in result.trace] == [output.value for output in result.outputs]


def test_the_trace_reads_in_english_with_the_rounding_named() -> None:
    result = cents().compute(parts("100.25", "40", "9.75"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "part_one (100.25) plus part_two (40.00) plus part_three (9.75), not below 0, gives 150.00 "
        "(rounded to the nearest cent).",
    )


def test_the_floored_trace_reads_in_english_with_the_rounding_named() -> None:
    result = cents().compute(parts("10", "-25.5", "5"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "part_one (10.00) plus part_two (-25.50) plus part_three (5.00), not below 0, "
        "gives 0.00 "
        "(rounded to the nearest cent).",
    )


def test_the_trace_reads_in_english_for_no_parts_with_no_rounding() -> None:
    result = SumNotBelowZero(rounding(), (), TOTAL).compute(())

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "Nothing to add, not below 0, so 0.00.",
    )


def test_trace_holds_no_text() -> None:
    trace = capability().compute(parts("10", "-25.5", "5")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- a blank part ---------------------------------------------------------------------------
# As for `core/sum`: the list is one slot, `parts`; a rule for one part, by its kind, replaces the
# slot's rule for that part alone. A blank passed on is a blank total, never floored.


def with_blank(*blanked: AmountKind) -> tuple[Artifact[Any], ...]:
    """The made-up parts 100.25, 40 and 9.75, with each kind in `blanked` left blank."""
    return tuple(
        Artifact(artifact.kind, BLANK) if artifact.kind in blanked else artifact
        for artifact in parts("100.25", "40", "9.75")
    )


def test_declares_that_the_parts_may_be_blank_one_by_one() -> None:
    assert SumNotBelowZero.BLANK_ALLOWED == frozenset({"parts"})
    assert SumNotBelowZero.BLANK_PER_ITEM == frozenset({"parts"})


def test_without_rules_a_blank_part_is_refused_naming_the_line_and_slot() -> None:
    with pytest.raises(BlankNotAllowedError, match="'part_two'.*'parts'"):
        capability().run(with_blank(PART_TWO))


def test_a_rule_for_one_part_passes_its_blank_on_as_a_blank_total() -> None:
    one = capability().with_blank_rules({}, {PART_THREE: PASS_ON})

    result = one.run(with_blank(PART_THREE))

    assert result.outputs == (Artifact(TOTAL, BLANK),)
    assert result.trace == (BlankPassedOnLine(TOTAL, (PART_THREE,)),)


def test_a_rule_for_one_part_leaves_the_other_parts_refusing_a_blank() -> None:
    one = capability().with_blank_rules({}, {PART_THREE: PASS_ON})

    with pytest.raises(BlankNotAllowedError, match="'part_one'.*'parts'"):
        one.run(with_blank(PART_ONE))


def test_the_floor_is_not_applied_to_a_blank_total() -> None:
    passing = capability().with_blank_rules({"parts": PASS_ON})
    negative = (
        Artifact(PART_ONE, D("-50")),
        Artifact(PART_TWO, D("-10")),
        Artifact(PART_THREE, BLANK),
    )

    assert passing.run(negative).outputs == (Artifact(TOTAL, BLANK),)


def test_a_filled_sum_is_still_floored_when_rules_are_declared() -> None:
    passing = capability().with_blank_rules({}, {PART_THREE: PASS_ON})

    assert passing.run(parts("-50", "10", "9.75")).outputs == (Artifact(TOTAL, D(0)),)
    assert passing.run(parts("100.25", "40", "9.75")).outputs == (Artifact(TOTAL, D("150.00")),)


def test_a_fallback_adds_it_in_place_of_a_blank_part_and_the_floor_applies() -> None:
    zero = capability().with_blank_rules({}, {PART_THREE: D(0)})
    given = (Artifact(PART_ONE, D("-5")), Artifact(PART_TWO, D("2")), Artifact(PART_THREE, BLANK))

    result = zero.run(given)

    assert result.outputs == (Artifact(TOTAL, D(0)),)
    assert result.trace == (
        BlankFallbackLine(PART_THREE, D(0)),
        SumNotBelowZeroLine(
            TOTAL,
            ((PART_ONE, D("-5")), (PART_TWO, D("2")), (PART_THREE, D(0))),
            NO_ROUNDING,
            D(0),
        ),
    )


def test_a_typed_zero_is_not_a_blank() -> None:
    passing = capability().with_blank_rules({"parts": PASS_ON})
    given = (Artifact(PART_ONE, D(0)), *parts("0", "40", "9.75")[1:])

    assert passing.run(given).outputs == (Artifact(TOTAL, D("49.75")),)


def test_a_blank_part_under_the_cent_rule_takes_the_cent_scale_of_its_fallback() -> None:
    carried = cents().with_blank_rules({"parts": D(0)})

    (output,) = carried.run(with_blank(PART_TWO)).outputs

    assert str(output.value) == "110.00"
