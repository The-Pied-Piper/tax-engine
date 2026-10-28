"""Unit tests for LesserOfWhenPositive and LesserOfWhenPositiveInBrackets, with made-up kinds.

`ca/lesser_of_when_positive` is `core/lesser_of` behind a gate: the least of its amounts, but only
if every amount is above zero, else a plain `Decimal(0)`. `ca/lesser_of_when_positive_in_brackets`
(a sibling sharing the implementation, both in the module `lesser_of_when_positive`) gives the
negative of that least ("show in brackets"), and a plain `Decimal(0)` when the gate fails.

Their slots, the same for both: a consumed list slot `amounts` (at least one `Decimal` kind) and
one produced slot `output`; no parameter slots, no dataset, no flag. The least is exact, the first
listed wins a tie and keeps its scale. Each records one `LesserOfWhenPositiveLine`, its `bracket`
field set by which class records it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.trace import LesserOfWhenPositiveLine
from tax_calculator.jurisdictions.ca.capabilities.lesser_of_when_positive import (
    LesserOfWhenPositive,
    LesserOfWhenPositiveInBrackets,
)

D = Decimal
Wired = LesserOfWhenPositive | LesserOfWhenPositiveInBrackets

FIRST = ArtifactKind("ex/first_amount", Decimal)
SECOND = ArtifactKind("ex/second_amount", Decimal)
THIRD = ArtifactKind("ex/third_amount", Decimal)
OUTPUT = ArtifactKind("ex/limited_amount", Decimal)
KINDS = {"first": FIRST, "second": SECOND, "third": THIRD}

BOTH = [LesserOfWhenPositive, LesserOfWhenPositiveInBrackets]


def given(**values: str) -> tuple[Artifact[Any], ...]:
    return tuple(Artifact(KINDS[name], D(value)) for name, value in values.items())


def plain(*amounts: ArtifactKind[Decimal]) -> LesserOfWhenPositive:
    return LesserOfWhenPositive(amounts=amounts or (FIRST, SECOND), output=OUTPUT)


def bracketed(*amounts: ArtifactKind[Decimal]) -> LesserOfWhenPositiveInBrackets:
    return LesserOfWhenPositiveInBrackets(amounts=amounts or (FIRST, SECOND), output=OUTPUT)


def compute(wired: Wired, **values: str) -> Artifact[Any]:
    (output,) = wired.compute(given(**values)).outputs
    return output


# --- registration and wiring --------------------------------------------------------------------


def test_are_registered_under_their_federal_names() -> None:
    registry = CapabilityRegistry.shared()

    assert registry.get("ca/lesser_of_when_positive") is LesserOfWhenPositive
    assert registry.get("ca/lesser_of_when_positive_in_brackets") is LesserOfWhenPositiveInBrackets
    assert LesserOfWhenPositive is not LesserOfWhenPositiveInBrackets


def test_are_exported_from_the_federal_capabilities_package() -> None:
    assert "lesser_of_when_positive" in ca_capabilities.__all__
    module = ca_capabilities.lesser_of_when_positive
    assert module.LesserOfWhenPositive is LesserOfWhenPositive
    assert module.LesserOfWhenPositiveInBrackets is LesserOfWhenPositiveInBrackets


@pytest.mark.parametrize("cls", BOTH)
def test_declares_its_slots(cls: type[Wired]) -> None:
    assert cls.PARAMETERS == {}
    assert cls.CONSUMES == {"amounts": list[Decimal]}
    assert cls.PRODUCES == {"output": Decimal}
    assert cls.is_list_slot("amounts")


@pytest.mark.parametrize("cls", BOTH)
def test_its_slots_are_read_only(cls: type[Wired]) -> None:
    for slots in (cls.PARAMETERS, cls.CONSUMES, cls.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(LesserOfWhenPositive.CONSUMES, Mapping[str, type])
    assert_type(LesserOfWhenPositive.PRODUCES, Mapping[str, type])


@pytest.mark.parametrize("cls", BOTH)
def test_declares_its_contract(cls: type[Wired]) -> None:
    wired = cls(amounts=(FIRST, SECOND, THIRD), output=OUTPUT)

    assert wired.consumes == frozenset({FIRST, SECOND, THIRD})
    assert wired.produces == frozenset({OUTPUT})
    assert "consumes" not in vars(cls)
    assert "produces" not in vars(cls)


@pytest.mark.parametrize("cls", BOTH)
def test_takes_no_flag_or_dataset(cls: type[Wired]) -> None:
    with pytest.raises(TypeError):
        cls(amounts=(FIRST,), output=OUTPUT, bracket=True)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        cls(amounts=(FIRST,), output=OUTPUT, positive=())  # type: ignore[call-arg]


@pytest.mark.parametrize("cls", BOTH)
def test_rejects_no_amounts(cls: type[Wired]) -> None:
    with pytest.raises(InvalidCapabilityError, match=f"{cls.__name__}.*'amounts'"):
        cls(amounts=(), output=OUTPUT)


@pytest.mark.parametrize("cls", BOTH)
def test_rejects_one_kind_listed_twice(cls: type[Wired]) -> None:
    with pytest.raises(InvalidCapabilityError, match=f"{cls.__name__}.*'amounts'"):
        cls(amounts=(FIRST, FIRST), output=OUTPUT)


@pytest.mark.parametrize("cls", BOTH)
def test_rejects_the_output_kind_as_an_amount(cls: type[Wired]) -> None:
    with pytest.raises(InvalidCapabilityError, match=cls.__name__) as raised:
        cls(amounts=(FIRST, OUTPUT), output=OUTPUT)

    assert "'output'" in str(raised.value)


@pytest.mark.parametrize("cls", BOTH)
def test_rejects_a_single_kind_where_a_tuple_is_wanted(cls: type[Wired]) -> None:
    with pytest.raises(InvalidCapabilityError, match=f"{cls.__name__}.*'amounts'"):
        cls(amounts=FIRST, output=OUTPUT)  # type: ignore[arg-type]


@pytest.mark.parametrize("cls", BOTH)
def test_rejects_a_kind_of_another_value_type(cls: type[Wired]) -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match=f"{cls.__name__}.*'amounts'"):
        cls(amounts=(count,), output=OUTPUT)  # type: ignore[arg-type]


def test_are_not_generic_over_artifacts() -> None:
    for cls in BOTH:
        assert not getattr(cls, "__type_params__", ())
        assert not getattr(cls, "__parameters__", ())


# --- computing: the least when every amount is above zero ---------------------------------------


def test_is_the_lesser_of_the_amounts_when_every_amount_is_positive() -> None:
    output = compute(plain(), first="30000.00", second="28500.50")

    assert output == Artifact(OUTPUT, D("28500.50"))
    assert type(output.value) is Decimal


def test_the_least_of_three_amounts() -> None:
    wired = plain(FIRST, SECOND, THIRD)

    assert compute(wired, first="5", second="2", third="3") == Artifact(OUTPUT, D("2"))


def test_a_single_positive_amount_is_produced_unchanged() -> None:
    assert compute(plain(FIRST), first="12.50") == Artifact(OUTPUT, D("12.50"))


def test_the_least_keeps_its_scale_and_is_not_rounded() -> None:
    assert str(compute(plain(), first="2.50", second="9").value) == "2.50"
    assert compute(plain(), first="0.123456789", second="1") == Artifact(OUTPUT, D("0.123456789"))


def test_equal_amounts_produce_the_first_listed_keeping_its_scale() -> None:
    assert str(compute(plain(), first="2.0", second="2.00").value) == "2.0"
    assert str(compute(plain(), first="2.00", second="2.0").value) == "2.00"


@pytest.mark.parametrize(
    "values",
    [
        {"first": "0", "second": "5"},
        {"first": "5", "second": "0.00"},
        {"first": "-1", "second": "5"},
        {"first": "5", "second": "-0.01"},
        {"first": "-1", "second": "-4"},
    ],
)
def test_an_amount_at_or_below_zero_gives_a_plain_zero(values: dict[str, str]) -> None:
    output = compute(plain(), **values)

    assert output == Artifact(OUTPUT, D("0"))
    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_one_amount_at_or_below_zero_gates_off_a_single_amount_wiring() -> None:
    assert compute(plain(FIRST), first="0") == Artifact(OUTPUT, D("0"))


def test_the_smallest_positive_amount_passes() -> None:
    assert compute(plain(), first="0.0000000000000000000000000001", second="3") == Artifact(
        OUTPUT, D("0.0000000000000000000000000001")
    )


# --- computing: in brackets ---------------------------------------------------------------------


def test_in_brackets_the_least_is_negated() -> None:
    output = compute(bracketed(), first="3.50", second="2.25")

    assert output == Artifact(OUTPUT, D("-2.25"))
    assert str(output.value) == "-2.25"
    assert type(output.value) is Decimal


def test_in_brackets_a_single_amount_is_negated() -> None:
    assert compute(bracketed(FIRST), first="12.50") == Artifact(OUTPUT, D("-12.50"))


@pytest.mark.parametrize("values", [{"first": "0", "second": "5"}, {"first": "-1", "second": "5"}])
def test_in_brackets_a_failed_gate_gives_a_plain_zero_not_a_negated_one(
    values: dict[str, str],
) -> None:
    output = compute(bracketed(), **values)

    assert str(output.value) == "0"
    assert not output.value.is_signed()


def test_the_plain_one_never_negates() -> None:
    assert compute(plain(), first="3.50", second="2.25") == Artifact(OUTPUT, D("2.25"))


# --- computing: inputs --------------------------------------------------------------------------


@pytest.mark.parametrize("cls", BOTH)
def test_ignores_artifacts_it_does_not_consume(cls: type[Wired]) -> None:
    wired = cls(amounts=(FIRST, SECOND), output=OUTPUT)

    result = wired.compute(given(first="3", second="2", third="1"))

    assert len(result.outputs) == 1


@pytest.mark.parametrize("cls", BOTH)
def test_a_missing_amount_is_a_missing_artifact(cls: type[Wired]) -> None:
    wired = cls(amounts=(FIRST, SECOND), output=OUTPUT)

    with pytest.raises(MissingArtifactError, match="second_amount"):
        wired.compute(given(first="3"))


@pytest.mark.parametrize("cls", BOTH)
def test_compute_is_repeatable(cls: type[Wired]) -> None:
    wired = cls(amounts=(FIRST, SECOND), output=OUTPUT)

    assert wired.compute(given(first="3", second="2")) == wired.compute(
        given(first="3", second="2")
    )


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_line_with_the_parts_and_the_gate() -> None:
    trace = plain().compute(given(first="3.00", second="2")).trace

    assert trace == (
        LesserOfWhenPositiveLine(
            output=OUTPUT,
            parts=((FIRST, D("3.00")), (SECOND, D("2"))),
            all_positive=True,
            bracket=False,
            result=D("2"),
        ),
    )


def test_traces_a_failed_gate_with_a_zero_result() -> None:
    trace = plain().compute(given(first="3", second="0")).trace

    assert trace == (
        LesserOfWhenPositiveLine(OUTPUT, ((FIRST, D("3")), (SECOND, D("0"))), False, False, D("0")),
    )


def test_the_in_brackets_class_records_the_bracket_flag_and_the_negated_result() -> None:
    trace = bracketed().compute(given(first="3", second="2")).trace

    assert trace == (
        LesserOfWhenPositiveLine(OUTPUT, ((FIRST, D("3")), (SECOND, D("2"))), True, True, D("-2")),
    )


def test_the_in_brackets_class_traces_a_failed_gate() -> None:
    trace = bracketed().compute(given(first="-3", second="2")).trace

    assert trace == (
        LesserOfWhenPositiveLine(OUTPUT, ((FIRST, D("-3")), (SECOND, D("2"))), False, True, D("0")),
    )


def test_trace_amount_is_the_result() -> None:
    trace = bracketed().compute(given(first="3", second="2")).trace

    assert [line.amount for line in trace] == [D("-2")]


@pytest.mark.parametrize("cls", BOTH)
def test_trace_holds_no_text(cls: type[Wired]) -> None:
    wired = cls(amounts=(FIRST, SECOND), output=OUTPUT)

    for line in wired.compute(given(first="3", second="2")).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
