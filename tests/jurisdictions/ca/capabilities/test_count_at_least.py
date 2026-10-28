"""Unit tests for the CountAtLeast capability (`ca/count_at_least`), with made-up kinds.

It is `core/at_most` for whole numbers, the other way round. Its slots: two consumed single slots,
`count` and `minimum` (both `int` kinds), one produced slot `output` (an `int` kind), no
parameter slots and no dataset. The output is the count, unchanged, when it is at least the
minimum; a count below the minimum is an input error, `InputBelowBoundError` (a new error beside
`InputAboveBoundError`), naming both kinds and their values. It records one `CountAtLeastLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    DomainError,
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_calculator.domain.trace import CountAtLeastLine
from tax_calculator.jurisdictions.ca.capabilities.count_at_least import CountAtLeast

COUNT = ArtifactKind("ex/widget_count", int)
MINIMUM = ArtifactKind("ex/widget_minimum", int)
OUTPUT = ArtifactKind("ex/widget_checked", int)


def capability() -> CountAtLeast:
    return CountAtLeast(COUNT, MINIMUM, OUTPUT)


def inputs(count: int, minimum: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(COUNT, count), Artifact(MINIMUM, minimum))


def compute(count: int, minimum: int) -> Artifact[Any]:
    (output,) = capability().compute(inputs(count, minimum)).outputs
    return output


def test_is_registered_as_ca_count_at_least() -> None:
    assert CapabilityRegistry.shared().get("ca/count_at_least") is CountAtLeast


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "count_at_least" in ca_capabilities.__all__
    assert ca_capabilities.count_at_least.CountAtLeast is CountAtLeast


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({COUNT, MINIMUM})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CountAtLeast)
    assert "produces" not in vars(CountAtLeast)


def test_declares_its_slots() -> None:
    assert CountAtLeast.PARAMETERS == {}
    assert CountAtLeast.CONSUMES == {"count": int, "minimum": int}
    assert CountAtLeast.PRODUCES == {"output": int}
    assert not CountAtLeast.is_list_slot("count")
    assert not CountAtLeast.is_list_slot("minimum")


def test_its_slots_are_read_only() -> None:
    for slots in (CountAtLeast.PARAMETERS, CountAtLeast.CONSUMES, CountAtLeast.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CountAtLeast.CONSUMES, Mapping[str, type])
    assert_type(CountAtLeast.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CountAtLeast.CONSUMES, CountAtLeast.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CountAtLeast(count=COUNT, minimum=MINIMUM, output=OUTPUT)

    assert wired.compute(inputs(3, 2)).outputs == (Artifact(OUTPUT, 3),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        CountAtLeast(COUNT, MINIMUM, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((COUNT, COUNT, OUTPUT), ("'count'", "'minimum'")),
        ((COUNT, MINIMUM, COUNT), ("'count'", "'output'")),
        ((COUNT, MINIMUM, MINIMUM), ("'minimum'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[int], ArtifactKind[int], ArtifactKind[int]], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="CountAtLeast") as raised:
        CountAtLeast(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountAtLeast.*'count'"):
        CountAtLeast((COUNT,), MINIMUM, OUTPUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_a_count() -> None:
    money = ArtifactKind("ex/money", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="CountAtLeast.*'minimum'"):
        CountAtLeast(COUNT, money, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CountAtLeast, "__type_params__", ())
    assert not getattr(CountAtLeast, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_a_count_above_the_minimum_is_produced_unchanged() -> None:
    output = compute(5, 2)

    assert output == Artifact(OUTPUT, 5)
    assert type(output.value) is int


def test_a_count_equal_to_the_minimum_is_produced() -> None:
    assert compute(2, 2) == Artifact(OUTPUT, 2)


def test_a_zero_count_with_a_zero_minimum_is_produced() -> None:
    assert compute(0, 0) == Artifact(OUTPUT, 0)


def test_a_negative_count_is_compared_like_any_other() -> None:
    assert compute(-1, -3) == Artifact(OUTPUT, -1)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", int), 9)

    assert capability().compute((other, *inputs(4, 1))).outputs == (Artifact(OUTPUT, 4),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_count"):
        capability().compute((Artifact(MINIMUM, 1),))


def test_a_missing_minimum_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_minimum"):
        capability().compute((Artifact(COUNT, 1),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs(3, 2)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs(3, 2)) == wired.compute(inputs(3, 2))


# --- a count below the minimum ------------------------------------------------------------------


def test_a_count_below_the_minimum_is_an_input_below_bound_error() -> None:
    with pytest.raises(InputBelowBoundError):
        compute(1, 2)


def test_the_error_names_both_kinds_and_their_values() -> None:
    with pytest.raises(InputBelowBoundError) as raised:
        compute(1, 2)

    assert str(raised.value) == "ex/widget_count 1 is below ex/widget_minimum 2"


def test_a_zero_count_below_a_minimum_of_one_is_rejected() -> None:
    with pytest.raises(InputBelowBoundError, match=r"ex/widget_count 0 .*ex/widget_minimum 1"):
        compute(0, 1)


def test_a_negative_count_below_a_zero_minimum_is_rejected() -> None:
    with pytest.raises(InputBelowBoundError, match=r"ex/widget_count -1 .*ex/widget_minimum 0"):
        compute(-1, 0)


def test_an_input_below_bound_error_is_a_domain_error() -> None:
    assert issubclass(InputBelowBoundError, DomainError)


def test_an_input_below_bound_error_is_not_an_input_above_bound_error() -> None:
    assert not issubclass(InputBelowBoundError, InputAboveBoundError)
    assert not issubclass(InputAboveBoundError, InputBelowBoundError)


def test_an_input_below_bound_error_is_not_a_wiring_error() -> None:
    assert not issubclass(InputBelowBoundError, InvalidCapabilityError)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_count_at_least_line() -> None:
    assert capability().compute(inputs(3, 2)).trace == (
        CountAtLeastLine(output=OUTPUT, count_kind=COUNT, count=3, minimum_kind=MINIMUM, minimum=2),
    )


def test_trace_amount_is_the_count() -> None:
    trace = capability().compute(inputs(3, 2)).trace

    assert [line.amount for line in trace] == [Decimal(3)]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs(3, 2)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
