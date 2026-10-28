"""Unit tests for the ClaimAtMost capability (`ca/claim_at_most`), with made-up kinds and values.

It is `core/at_most` for a maximum the form carries with its sign. Its slots: two consumed single
slots, `claim` and `maximum` (both money kinds), one produced slot `output` (a money kind), no
parameter slots and no dataset. The output is the claim, unchanged and exact, when it is at most
the maximum, and also when it is 0 against a negative maximum; a claim above the maximum and above
0 is an input error, `InputAboveBoundError`, naming both kinds and their values, not capped. It
records one `ClaimAtMostLine`.
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
from tax_calculator.domain.trace import ClaimAtMostLine
from tax_calculator.jurisdictions.ca.capabilities.claim_at_most import ClaimAtMost

D = Decimal

CLAIM = ArtifactKind("ex/widget_claim", Decimal)
MAXIMUM = ArtifactKind("ex/widget_maximum", Decimal)
OUTPUT = ArtifactKind("ex/widget_claimed", Decimal)


def capability() -> ClaimAtMost:
    return ClaimAtMost(CLAIM, MAXIMUM, OUTPUT)


def inputs(claim: str, maximum: str) -> tuple[Artifact[Decimal], ...]:
    return (Artifact(CLAIM, D(claim)), Artifact(MAXIMUM, D(maximum)))


def compute(claim: str, maximum: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(claim, maximum)).outputs
    return output


def test_is_registered_as_ca_claim_at_most() -> None:
    assert CapabilityRegistry.shared().get("ca/claim_at_most") is ClaimAtMost


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "claim_at_most" in ca_capabilities.__all__
    assert ca_capabilities.claim_at_most.ClaimAtMost is ClaimAtMost


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CLAIM, MAXIMUM})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ClaimAtMost)
    assert "produces" not in vars(ClaimAtMost)


def test_declares_its_slots() -> None:
    assert ClaimAtMost.PARAMETERS == {}
    assert ClaimAtMost.CONSUMES == {"claim": Decimal, "maximum": Decimal}
    assert ClaimAtMost.PRODUCES == {"output": Decimal}
    assert not ClaimAtMost.is_list_slot("claim")
    assert not ClaimAtMost.is_list_slot("maximum")


def test_its_slots_are_read_only() -> None:
    for slots in (ClaimAtMost.PARAMETERS, ClaimAtMost.CONSUMES, ClaimAtMost.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ClaimAtMost.CONSUMES, Mapping[str, type])
    assert_type(ClaimAtMost.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ClaimAtMost.CONSUMES, ClaimAtMost.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ClaimAtMost(claim=CLAIM, maximum=MAXIMUM, output=OUTPUT)

    assert wired.compute(inputs("3", "4")).outputs == (Artifact(OUTPUT, D("3")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        ClaimAtMost(CLAIM, MAXIMUM, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((CLAIM, CLAIM, OUTPUT), ("'claim'", "'maximum'")),
        ((CLAIM, MAXIMUM, CLAIM), ("'claim'", "'output'")),
        ((CLAIM, MAXIMUM, MAXIMUM), ("'maximum'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[Decimal], ArtifactKind[Decimal], ArtifactKind[Decimal]],
    slots: tuple[str, str],
) -> None:
    with pytest.raises(InvalidCapabilityError, match="ClaimAtMost") as raised:
        ClaimAtMost(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_claim() -> None:
    with pytest.raises(InvalidCapabilityError, match="ClaimAtMost.*'claim'"):
        ClaimAtMost((CLAIM,), MAXIMUM, OUTPUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_a_maximum() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not an ArtifactKind[Decimal]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ClaimAtMost.*'maximum'"):
        ClaimAtMost(CLAIM, count, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ClaimAtMost, "__type_params__", ())
    assert not getattr(ClaimAtMost, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_a_claim_below_the_maximum_is_produced_unchanged_and_exact() -> None:
    assert compute("1500.25", "1926.00") == Artifact(OUTPUT, D("1500.25"))


def test_a_claim_equal_to_the_maximum_is_produced() -> None:
    assert compute("1926.00", "1926.00") == Artifact(OUTPUT, D("1926.00"))


def test_a_zero_claim_with_a_zero_maximum_is_produced() -> None:
    assert compute("0", "0") == Artifact(OUTPUT, D("0"))


def test_a_zero_claim_against_a_negative_maximum_is_produced() -> None:
    output = compute("0", "-9500.00")

    assert output == Artifact(OUTPUT, D("0"))


def test_a_zero_claim_keeps_its_scale_against_a_negative_maximum() -> None:
    assert str(compute("0.00", "-1").value) == "0.00"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("9"))

    assert capability().compute((other, *inputs("1", "4"))).outputs == (Artifact(OUTPUT, D("1")),)


def test_a_missing_claim_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_claim"):
        capability().compute((Artifact(MAXIMUM, D("1")),))


def test_a_missing_maximum_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="widget_maximum"):
        capability().compute((Artifact(CLAIM, D("1")),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs("2", "3")).outputs) == 1


# --- a claim above the maximum ------------------------------------------------------------------


def test_a_claim_above_the_maximum_is_an_input_above_bound_error() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute("1926.01", "1926.00")

    assert str(raised.value) == "ex/widget_claim 1926.01 is above ex/widget_maximum 1926.00"


def test_a_claim_above_a_zero_maximum_is_rejected() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/widget_claim 0.01 .*ex/widget_maximum 0"):
        compute("0.01", "0")


def test_a_positive_claim_against_a_negative_maximum_is_rejected_not_capped() -> None:
    with pytest.raises(InputAboveBoundError, match=r"ex/widget_claim 1 .*ex/widget_maximum -9500"):
        compute("1", "-9500")


def test_a_negative_claim_equal_to_a_negative_maximum_is_produced() -> None:
    assert compute("-5", "-5") == Artifact(OUTPUT, D("-5"))


def test_an_input_above_bound_error_is_a_domain_error_only() -> None:
    assert issubclass(InputAboveBoundError, DomainError)
    assert not issubclass(InputAboveBoundError, InputBelowBoundError)
    assert not issubclass(InputAboveBoundError, InvalidCapabilityError)


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs("2", "3")) == wired.compute(inputs("2", "3"))


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_claim_at_most_line() -> None:
    assert capability().compute(inputs("3", "4")).trace == (
        ClaimAtMostLine(
            output=OUTPUT,
            claim_kind=CLAIM,
            claim_value=D("3"),
            maximum_kind=MAXIMUM,
            maximum_value=D("4"),
        ),
    )


def test_traces_the_negative_maximum_a_zero_claim_was_allowed_against() -> None:
    assert capability().compute(inputs("0", "-9500")).trace == (
        ClaimAtMostLine(
            output=OUTPUT,
            claim_kind=CLAIM,
            claim_value=D("0"),
            maximum_kind=MAXIMUM,
            maximum_value=D("-9500"),
        ),
    )


def test_trace_amount_is_the_claim() -> None:
    trace = capability().compute(inputs("3", "4")).trace

    assert [line.amount for line in trace] == [D("3")]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs("3", "4")).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
