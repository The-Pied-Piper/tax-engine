"""Unit tests for the LesserOf capability (`core/lesser_of`), with made-up kinds and values.

Its slots: one consumed list slot `amounts` (a tuple of money kinds, at least one, since there is
no lesser of nothing), one produced slot `output`, no parameter slots. The output is the minimum
of the amounts' values, exact, with no rounding (it has no dataset); when two amounts are equal
the first listed is produced, keeping its scale. It records one `LesserOfLine` holding each
amount in the order it was wired.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.domain.capabilities as core
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import LesserOfLine

D = Decimal


PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
PART_THREE = ArtifactKind("ex/part_three", Decimal)
LESSER_AMOUNT = ArtifactKind("ex/lesser_amount", Decimal)


def capability() -> LesserOf:
    """By default the first and second made-up amounts, in that order."""
    return LesserOf((PART_ONE, PART_TWO), LESSER_AMOUNT)


def compute(wired: LesserOf, *values: tuple[ArtifactKind[Decimal], str]) -> Artifact[Any]:
    (output,) = wired.compute(tuple(Artifact(kind, D(value)) for kind, value in values)).outputs
    return output


def test_is_registered_as_core_lesser_of() -> None:
    assert CapabilityRegistry.shared().get("core/lesser_of") is LesserOf


def test_is_exported_from_the_capabilities_package() -> None:
    assert "lesser_of" in core.__all__
    assert core.lesser_of.LesserOf is LesserOf


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PART_ONE, PART_TWO})
    assert capability().produces == frozenset({LESSER_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(LesserOf)
    assert "produces" not in vars(LesserOf)


def test_declares_its_slots() -> None:
    assert LesserOf.PARAMETERS == {}
    assert LesserOf.CONSUMES == {"amounts": list[Decimal]}
    assert LesserOf.PRODUCES == {"output": Decimal}
    assert LesserOf.is_list_slot("amounts")
    assert not LesserOf.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (LesserOf.PARAMETERS, LesserOf.CONSUMES, LesserOf.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(LesserOf.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(LesserOf.CONSUMES, Mapping[str, type])
    assert_type(LesserOf.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (LesserOf.PARAMETERS, LesserOf.CONSUMES, LesserOf.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = LesserOf(amounts=(PART_ONE, PART_TWO), output=LESSER_AMOUNT)

    assert compute(wired, (PART_ONE, "100"), (PART_TWO, "40")) == Artifact(LESSER_AMOUNT, D("40"))


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        LesserOf((PART_ONE,), LESSER_AMOUNT, object())  # type: ignore[call-arg]


def test_rejects_an_empty_list_of_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOf.*'amounts'"):
        LesserOf((), LESSER_AMOUNT)


def test_rejects_one_kind_as_both_an_amount_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOf") as raised:
        LesserOf((PART_ONE, LESSER_AMOUNT), LESSER_AMOUNT)

    message = str(raised.value)
    assert "'amounts'" in message
    assert "'output'" in message


def test_rejects_an_amount_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOf.*'amounts'"):
        LesserOf((PART_ONE, PART_TWO, PART_ONE), LESSER_AMOUNT)


def test_rejects_a_single_kind_for_its_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="LesserOf.*'amounts'"):
        LesserOf(PART_ONE, LESSER_AMOUNT)  # type: ignore[arg-type]


def test_rejects_an_amount_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="LesserOf.*'amounts'"):
        LesserOf((PART_ONE, count), LESSER_AMOUNT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(LesserOf, "__type_params__", ())
    assert not getattr(LesserOf, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_part_one_when_it_is_less() -> None:
    assert compute(capability(), (PART_ONE, "40"), (PART_TWO, "100")) == Artifact(
        LESSER_AMOUNT, D("40")
    )


def test_produces_the_part_two_when_it_is_less() -> None:
    assert compute(capability(), (PART_ONE, "100"), (PART_TWO, "40")) == Artifact(
        LESSER_AMOUNT, D("40")
    )


def test_the_order_of_the_inputs_does_not_matter() -> None:
    output = compute(capability(), (PART_TWO, "40"), (PART_ONE, "100"))

    assert output == Artifact(LESSER_AMOUNT, D("40"))


def test_produces_the_least_of_three_amounts() -> None:
    wired = LesserOf((PART_ONE, PART_TWO, PART_THREE), LESSER_AMOUNT)

    output = compute(wired, (PART_ONE, "100.25"), (PART_TWO, "9.75"), (PART_THREE, "40"))

    assert output == Artifact(LESSER_AMOUNT, D("9.75"))


@pytest.mark.parametrize("least", [PART_ONE, PART_TWO, PART_THREE])
def test_produces_the_least_of_three_wherever_it_is_listed(least: ArtifactKind[Decimal]) -> None:
    wired = LesserOf((PART_ONE, PART_TWO, PART_THREE), LESSER_AMOUNT)
    values = [(kind, "1.5" if kind is least else "2") for kind in (PART_ONE, PART_TWO, PART_THREE)]

    assert compute(wired, *values) == Artifact(LESSER_AMOUNT, D("1.5"))


def test_one_amount_is_its_own_lesser() -> None:
    wired = LesserOf((PART_TWO,), LESSER_AMOUNT)

    output = compute(wired, (PART_TWO, "40.50"))

    assert output == Artifact(LESSER_AMOUNT, D("40.50"))
    assert str(output.value) == "40.50"


def test_equal_amounts_produce_that_amount() -> None:
    assert compute(capability(), (PART_ONE, "75"), (PART_TWO, "75")) == Artifact(
        LESSER_AMOUNT, D("75")
    )


def test_equal_amounts_produce_the_first_listed_keeping_its_scale() -> None:
    output = compute(capability(), (PART_ONE, "40.50"), (PART_TWO, "40.5"))

    assert str(output.value) == "40.50"


def test_equal_amounts_produce_the_first_as_wired_not_as_given() -> None:
    wired = LesserOf((PART_TWO, PART_ONE), LESSER_AMOUNT)

    output = compute(wired, (PART_ONE, "40.50"), (PART_TWO, "40.5"))

    assert str(output.value) == "40.5"


def test_the_lesser_keeps_its_scale() -> None:
    output = compute(capability(), (PART_ONE, "200"), (PART_TWO, "100.10"))

    assert str(output.value) == "100.10"


def test_keeps_the_lesser_exact_without_rounding() -> None:
    output = compute(
        capability(), (PART_ONE, "1234567.0000000000000001"), (PART_TWO, "1234567.0000000000000002")
    )

    assert str(output.value) == "1234567.0000000000000001"


def test_does_not_round_the_lesser() -> None:
    output = compute(capability(), (PART_ONE, "0.005"), (PART_TWO, "0.0049"))

    assert str(output.value) == "0.0049"


def test_a_zero_amount_produces_zero() -> None:
    assert compute(capability(), (PART_ONE, "250"), (PART_TWO, "0")) == Artifact(
        LESSER_AMOUNT, D(0)
    )


def test_a_negative_amount_is_the_lesser() -> None:
    output = compute(capability(), (PART_ONE, "0"), (PART_TWO, "-15.5"))

    assert output == Artifact(LESSER_AMOUNT, D("-15.5"))


def test_produces_a_decimal() -> None:
    output = compute(capability(), (PART_ONE, "1"), (PART_TWO, "2"))

    assert type(output.value) is Decimal


def test_ignores_artifacts_it_does_not_consume() -> None:
    output = compute(capability(), (PART_ONE, "100"), (PART_THREE, "1"), (PART_TWO, "40"))

    assert output == Artifact(LESSER_AMOUNT, D("40"))


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="part_two"):
        capability().compute((Artifact(PART_ONE, D("100")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_amount_and_the_result() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    assert trace == (
        LesserOfLine(
            output=LESSER_AMOUNT,
            parts=((PART_ONE, D("100")), (PART_TWO, D("40"))),
            result=D("40"),
        ),
    )


def test_traces_the_amounts_in_the_order_they_were_wired() -> None:
    wired = LesserOf((PART_THREE, PART_ONE, PART_TWO), LESSER_AMOUNT)
    inputs = (
        Artifact(PART_ONE, D("100.25")),
        Artifact(PART_TWO, D("9.75")),
        Artifact(PART_THREE, D("40")),
    )

    trace = wired.compute(inputs).trace

    assert trace == (
        LesserOfLine(
            LESSER_AMOUNT,
            ((PART_THREE, D("40")), (PART_ONE, D("100.25")), (PART_TWO, D("9.75"))),
            D("9.75"),
        ),
    )


def test_traces_the_first_of_equal_amounts_as_the_result() -> None:
    trace = (
        capability().compute((Artifact(PART_ONE, D("40.50")), Artifact(PART_TWO, D("40.5")))).trace
    )

    (line,) = trace
    assert isinstance(line, LesserOfLine)
    assert str(line.result) == "40.50"
    assert line.parts == ((PART_ONE, D("40.50")), (PART_TWO, D("40.5")))


def test_traces_one_amount() -> None:
    trace = LesserOf((PART_TWO,), LESSER_AMOUNT).compute((Artifact(PART_TWO, D("40.5")),)).trace

    assert trace == (LesserOfLine(LESSER_AMOUNT, ((PART_TWO, D("40.5")),), D("40.5")),)


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    assert [line.amount for line in trace] == [D("40")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute((Artifact(PART_ONE, D("7.25")), Artifact(PART_TWO, D("8"))))

    (output,) = result.outputs
    (line,) = result.trace
    assert isinstance(line, LesserOfLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
