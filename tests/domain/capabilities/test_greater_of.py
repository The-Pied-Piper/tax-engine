"""Unit tests for the GreaterOf capability (`core/greater_of`), with made-up kinds and values.

Its slots: one consumed list slot `amounts` (a tuple of money kinds, at least one, since there is
no greater of nothing), one produced slot `output`, no parameter slots. The output is the maximum
of the amounts' values, exact, with no rounding (it has no dataset); when two amounts are equal
the first listed is produced, keeping its scale. It records one `GreaterOfLine` holding each
amount in the order it was wired.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.domain.capabilities as core
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.greater_of import GreaterOf
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import GreaterOfLine

D = Decimal


PART_ONE = ArtifactKind("ex/part_one", Decimal)
PART_TWO = ArtifactKind("ex/part_two", Decimal)
PART_THREE = ArtifactKind("ex/part_three", Decimal)
GREATER_AMOUNT = ArtifactKind("ex/greater_amount", Decimal)


def capability() -> GreaterOf:
    """By default the first and second made-up amounts, in that order."""
    return GreaterOf((PART_ONE, PART_TWO), GREATER_AMOUNT)


def compute(wired: GreaterOf, *values: tuple[ArtifactKind[Decimal], str]) -> Artifact[Any]:
    (output,) = wired.compute(tuple(Artifact(kind, D(value)) for kind, value in values)).outputs
    return output


def test_is_registered_as_core_greater_of() -> None:
    assert CapabilityRegistry.shared().get("core/greater_of") is GreaterOf


def test_is_exported_from_the_capabilities_package() -> None:
    assert "greater_of" in core.__all__
    assert core.greater_of.GreaterOf is GreaterOf


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({PART_ONE, PART_TWO})
    assert capability().produces == frozenset({GREATER_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(GreaterOf)
    assert "produces" not in vars(GreaterOf)


def test_declares_its_slots() -> None:
    assert GreaterOf.PARAMETERS == {}
    assert GreaterOf.CONSUMES == {"amounts": list[Decimal]}
    assert GreaterOf.PRODUCES == {"output": Decimal}
    assert GreaterOf.is_list_slot("amounts")
    assert not GreaterOf.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (GreaterOf.PARAMETERS, GreaterOf.CONSUMES, GreaterOf.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(GreaterOf.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(GreaterOf.CONSUMES, Mapping[str, type])
    assert_type(GreaterOf.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (GreaterOf.PARAMETERS, GreaterOf.CONSUMES, GreaterOf.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = GreaterOf(amounts=(PART_ONE, PART_TWO), output=GREATER_AMOUNT)

    assert compute(wired, (PART_ONE, "100"), (PART_TWO, "40")) == Artifact(GREATER_AMOUNT, D("100"))


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        GreaterOf((PART_ONE,), GREATER_AMOUNT, object())  # type: ignore[call-arg]


def test_rejects_an_empty_list_of_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="GreaterOf.*'amounts'"):
        GreaterOf((), GREATER_AMOUNT)


def test_rejects_one_kind_as_both_an_amount_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="GreaterOf") as raised:
        GreaterOf((PART_ONE, GREATER_AMOUNT), GREATER_AMOUNT)

    message = str(raised.value)
    assert "'amounts'" in message
    assert "'output'" in message


def test_rejects_an_amount_listed_twice() -> None:
    with pytest.raises(InvalidCapabilityError, match="GreaterOf.*'amounts'"):
        GreaterOf((PART_ONE, PART_TWO, PART_ONE), GREATER_AMOUNT)


def test_rejects_a_single_kind_for_its_amounts() -> None:
    with pytest.raises(InvalidCapabilityError, match="GreaterOf.*'amounts'"):
        GreaterOf(PART_ONE, GREATER_AMOUNT)  # type: ignore[arg-type]


def test_rejects_an_amount_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="GreaterOf.*'amounts'"):
        GreaterOf((PART_ONE, count), GREATER_AMOUNT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(GreaterOf, "__type_params__", ())
    assert not getattr(GreaterOf, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_part_one_when_it_is_more() -> None:
    assert compute(capability(), (PART_ONE, "100"), (PART_TWO, "40")) == Artifact(
        GREATER_AMOUNT, D("100")
    )


def test_produces_the_part_two_when_it_is_more() -> None:
    assert compute(capability(), (PART_ONE, "40"), (PART_TWO, "100")) == Artifact(
        GREATER_AMOUNT, D("100")
    )


def test_the_order_of_the_inputs_does_not_matter() -> None:
    output = compute(capability(), (PART_TWO, "100"), (PART_ONE, "40"))

    assert output == Artifact(GREATER_AMOUNT, D("100"))


def test_produces_the_greatest_of_three_amounts() -> None:
    wired = GreaterOf((PART_ONE, PART_TWO, PART_THREE), GREATER_AMOUNT)

    output = compute(wired, (PART_ONE, "9.75"), (PART_TWO, "100.25"), (PART_THREE, "40"))

    assert output == Artifact(GREATER_AMOUNT, D("100.25"))


@pytest.mark.parametrize("greatest", [PART_ONE, PART_TWO, PART_THREE])
def test_produces_the_greatest_of_three_wherever_it_is_listed(
    greatest: ArtifactKind[Decimal],
) -> None:
    wired = GreaterOf((PART_ONE, PART_TWO, PART_THREE), GREATER_AMOUNT)
    values = [
        (kind, "2.5" if kind is greatest else "2") for kind in (PART_ONE, PART_TWO, PART_THREE)
    ]

    assert compute(wired, *values) == Artifact(GREATER_AMOUNT, D("2.5"))


def test_one_amount_is_its_own_greater() -> None:
    wired = GreaterOf((PART_TWO,), GREATER_AMOUNT)

    output = compute(wired, (PART_TWO, "40.50"))

    assert output == Artifact(GREATER_AMOUNT, D("40.50"))
    assert str(output.value) == "40.50"


def test_equal_amounts_produce_that_amount() -> None:
    assert compute(capability(), (PART_ONE, "75"), (PART_TWO, "75")) == Artifact(
        GREATER_AMOUNT, D("75")
    )


def test_equal_amounts_produce_the_first_listed_keeping_its_scale() -> None:
    output = compute(capability(), (PART_ONE, "40.50"), (PART_TWO, "40.5"))

    assert str(output.value) == "40.50"


def test_equal_amounts_produce_the_first_as_wired_not_as_given() -> None:
    wired = GreaterOf((PART_TWO, PART_ONE), GREATER_AMOUNT)

    output = compute(wired, (PART_ONE, "40.50"), (PART_TWO, "40.5"))

    assert str(output.value) == "40.5"


def test_the_greater_keeps_its_scale() -> None:
    output = compute(capability(), (PART_ONE, "100.10"), (PART_TWO, "50"))

    assert str(output.value) == "100.10"


def test_keeps_the_greater_exact_without_rounding() -> None:
    output = compute(
        capability(), (PART_ONE, "1234567.0000000000000001"), (PART_TWO, "1234567.0000000000000002")
    )

    assert str(output.value) == "1234567.0000000000000002"


def test_does_not_round_the_greater() -> None:
    output = compute(capability(), (PART_ONE, "0.005"), (PART_TWO, "0.0049"))

    assert str(output.value) == "0.005"


def test_a_zero_amount_is_the_greater_of_negatives() -> None:
    assert compute(capability(), (PART_ONE, "-250"), (PART_TWO, "0")) == Artifact(
        GREATER_AMOUNT, D(0)
    )


def test_a_negative_amount_is_the_greater_only_when_all_are_negative() -> None:
    output = compute(capability(), (PART_ONE, "-20"), (PART_TWO, "-15.5"))

    assert output == Artifact(GREATER_AMOUNT, D("-15.5"))


def test_produces_a_decimal() -> None:
    output = compute(capability(), (PART_ONE, "1"), (PART_TWO, "2"))

    assert type(output.value) is Decimal


def test_ignores_artifacts_it_does_not_consume() -> None:
    output = compute(capability(), (PART_ONE, "40"), (PART_THREE, "1000"), (PART_TWO, "100"))

    assert output == Artifact(GREATER_AMOUNT, D("100"))


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="part_two"):
        capability().compute((Artifact(PART_ONE, D("100")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_each_amount_and_the_result() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    assert trace == (
        GreaterOfLine(
            output=GREATER_AMOUNT,
            parts=((PART_ONE, D("100")), (PART_TWO, D("40"))),
            result=D("100"),
        ),
    )


def test_traces_the_amounts_in_the_order_they_were_wired() -> None:
    wired = GreaterOf((PART_THREE, PART_ONE, PART_TWO), GREATER_AMOUNT)
    inputs = (
        Artifact(PART_ONE, D("100.25")),
        Artifact(PART_TWO, D("9.75")),
        Artifact(PART_THREE, D("40")),
    )

    trace = wired.compute(inputs).trace

    assert trace == (
        GreaterOfLine(
            GREATER_AMOUNT,
            ((PART_THREE, D("40")), (PART_ONE, D("100.25")), (PART_TWO, D("9.75"))),
            D("100.25"),
        ),
    )


def test_traces_the_first_of_equal_amounts_as_the_result() -> None:
    trace = (
        capability().compute((Artifact(PART_ONE, D("40.50")), Artifact(PART_TWO, D("40.5")))).trace
    )

    (line,) = trace
    assert isinstance(line, GreaterOfLine)
    assert str(line.result) == "40.50"
    assert line.parts == ((PART_ONE, D("40.50")), (PART_TWO, D("40.5")))


def test_traces_one_amount() -> None:
    trace = GreaterOf((PART_TWO,), GREATER_AMOUNT).compute((Artifact(PART_TWO, D("40.5")),)).trace

    assert trace == (GreaterOfLine(GREATER_AMOUNT, ((PART_TWO, D("40.5")),), D("40.5")),)


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    assert [line.amount for line in trace] == [D("100")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute((Artifact(PART_ONE, D("7.25")), Artifact(PART_TWO, D("8"))))

    (output,) = result.outputs
    (line,) = result.trace
    assert isinstance(line, GreaterOfLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(PART_ONE, D("100")), Artifact(PART_TWO, D("40")))).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
