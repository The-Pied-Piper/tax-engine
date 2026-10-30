"""Unit tests for the CountAtMost capability (`ca/count_at_most`), with made-up kinds.

It is `ca/count_at_least` the other way round. Its slots: two consumed single slots, `count` and
`maximum` (both `int` kinds), one produced slot `output` (an `int` kind), no parameter slots and no
dataset. The output is the count, unchanged, when it is at most the maximum; a count above the
maximum is an input error, `InputAboveBoundError`, naming both kinds and their values. It records
one `CountAtMostLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    DomainError,
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.trace import CountAtMostLine
from tax_engine.jurisdictions.ca.capabilities.count_at_most import CountAtMost

COUNT = ArtifactKind("ex/widget_count", int)
MAXIMUM = ArtifactKind("ex/widget_maximum", int)
OUTPUT = ArtifactKind("ex/widget_checked", int)


def capability() -> CountAtMost:
    return CountAtMost(COUNT, MAXIMUM, OUTPUT)


def inputs(count: int, maximum: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(COUNT, count), Artifact(MAXIMUM, maximum))


def compute(count: int, maximum: int) -> Artifact[Any]:
    (output,) = capability().compute(inputs(count, maximum)).outputs
    return output


def test_is_registered_as_ca_count_at_most() -> None:
    assert CapabilityRegistry.shared().get("ca/count_at_most") is CountAtMost


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "count_at_most" in ca_capabilities.__all__
    assert ca_capabilities.count_at_most.CountAtMost is CountAtMost


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({COUNT, MAXIMUM})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CountAtMost)
    assert "produces" not in vars(CountAtMost)


def test_declares_its_slots() -> None:
    assert CountAtMost.PARAMETERS == {}
    assert CountAtMost.CONSUMES == {"count": int, "maximum": int}
    assert CountAtMost.PRODUCES == {"output": int}
    assert not CountAtMost.is_list_slot("count")
    assert not CountAtMost.is_list_slot("maximum")


def test_its_slots_are_read_only() -> None:
    for slots in (CountAtMost.PARAMETERS, CountAtMost.CONSUMES, CountAtMost.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CountAtMost.CONSUMES, Mapping[str, type])
    assert_type(CountAtMost.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CountAtMost.CONSUMES, CountAtMost.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CountAtMost(count=COUNT, maximum=MAXIMUM, output=OUTPUT)

    assert wired.compute(inputs(3, 4)).outputs == (Artifact(OUTPUT, 3),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        CountAtMost(COUNT, MAXIMUM, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((COUNT, COUNT, OUTPUT), ("'count'", "'maximum'")),
        ((COUNT, MAXIMUM, COUNT), ("'count'", "'output'")),
        ((COUNT, MAXIMUM, MAXIMUM), ("'maximum'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[int], ArtifactKind[int], ArtifactKind[int]], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="CountAtMost") as raised:
        CountAtMost(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountAtMost.*'count'"):
        CountAtMost((COUNT,), MAXIMUM, OUTPUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_a_maximum() -> None:
    money = ArtifactKind("ex/money", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="CountAtMost.*'maximum'"):
        CountAtMost(COUNT, money, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CountAtMost, "__type_params__", ())
    assert not getattr(CountAtMost, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_a_count_below_the_maximum_is_produced_unchanged() -> None:
    output = compute(2, 5)

    assert output == Artifact(OUTPUT, 2)
    assert type(output.value) is int


def test_a_count_equal_to_the_maximum_is_produced() -> None:
    assert compute(2, 2) == Artifact(OUTPUT, 2)


def test_a_zero_count_with_a_zero_maximum_is_produced() -> None:
    assert compute(0, 0) == Artifact(OUTPUT, 0)


def test_a_negative_count_is_compared_like_any_other() -> None:
    assert compute(-3, -1) == Artifact(OUTPUT, -3)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", int), 9)

    assert capability().compute((other, *inputs(1, 4))).outputs == (Artifact(OUTPUT, 1),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_count"):
        capability().compute((Artifact(MAXIMUM, 1),))


def test_a_missing_maximum_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_maximum"):
        capability().compute((Artifact(COUNT, 1),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs(2, 3)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs(2, 3)) == wired.compute(inputs(2, 3))


# --- a count above the maximum ------------------------------------------------------------------


def test_a_count_above_the_maximum_is_an_input_above_bound_error() -> None:
    with pytest.raises(InputAboveBoundError):
        compute(5, 4)


def test_the_error_names_both_kinds_and_their_values() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(5, 4)

    assert str(raised.value) == "ex/widget_count 5 is above ex/widget_maximum 4"


def test_a_zero_count_above_a_maximum_of_negative_one_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/widget_count 0 .*ex/widget_maximum -1"):
        compute(0, -1)


def test_a_count_of_one_above_a_zero_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/widget_count 1 .*ex/widget_maximum 0"):
        compute(1, 0)


def test_an_input_above_bound_error_is_a_domain_error() -> None:
    assert issubclass(InputAboveBoundError, DomainError)


def test_an_input_above_bound_error_is_not_an_input_below_bound_error() -> None:
    assert not issubclass(InputAboveBoundError, InputBelowBoundError)
    assert not issubclass(InputBelowBoundError, InputAboveBoundError)


def test_an_input_above_bound_error_is_not_a_wiring_error() -> None:
    assert not issubclass(InputAboveBoundError, InvalidCapabilityError)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_count_at_most_line() -> None:
    assert capability().compute(inputs(3, 4)).trace == (
        CountAtMostLine(output=OUTPUT, count_kind=COUNT, count=3, maximum_kind=MAXIMUM, maximum=4),
    )


def test_trace_amount_is_the_count() -> None:
    trace = capability().compute(inputs(3, 4)).trace

    assert [line.amount for line in trace] == [Decimal(3)]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs(3, 4)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
