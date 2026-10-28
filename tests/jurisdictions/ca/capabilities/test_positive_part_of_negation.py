"""Unit tests for the PositivePartOfNegation capability (`ca/positive_part_of_negation`).

Uses made-up kinds. For a line that reads "enter ... as a positive amount" of an earlier line
that may be negative. Its slots: one consumed slot `amount` (a `Decimal` kind) and one produced
slot `output`; no parameter slots and no dataset. The output is `max(-amount, 0)`, exact and with
the amount's scale kept; anything else is a plain `Decimal(0)` (never a signed zero, and without
a scale). It records one `PositivePartOfNegationLine`.
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
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.trace import PositivePartOfNegationLine
from tax_calculator.jurisdictions.ca.capabilities.positive_part_of_negation import (
    PositivePartOfNegation,
)

D = Decimal

AMOUNT = ArtifactKind("ex/net_result", Decimal)
OUTPUT = ArtifactKind("ex/shortfall", Decimal)


def capability() -> PositivePartOfNegation:
    return PositivePartOfNegation(AMOUNT, OUTPUT)


def compute(amount: str) -> Artifact[Any]:
    (output,) = capability().compute((Artifact(AMOUNT, D(amount)),)).outputs
    return output


def test_is_registered_as_ca_positive_part_of_negation() -> None:
    assert CapabilityRegistry.shared().get("ca/positive_part_of_negation") is PositivePartOfNegation


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "positive_part_of_negation" in ca_capabilities.__all__
    assert (
        ca_capabilities.positive_part_of_negation.PositivePartOfNegation is PositivePartOfNegation
    )


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({AMOUNT})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(PositivePartOfNegation)
    assert "produces" not in vars(PositivePartOfNegation)


def test_declares_its_slots() -> None:
    assert PositivePartOfNegation.PARAMETERS == {}
    assert PositivePartOfNegation.CONSUMES == {"amount": Decimal}
    assert PositivePartOfNegation.PRODUCES == {"output": Decimal}
    assert not PositivePartOfNegation.is_list_slot("amount")


def test_its_slots_are_read_only() -> None:
    for slots in (
        PositivePartOfNegation.PARAMETERS,
        PositivePartOfNegation.CONSUMES,
        PositivePartOfNegation.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(PositivePartOfNegation.CONSUMES, Mapping[str, type])
    assert_type(PositivePartOfNegation.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (PositivePartOfNegation.CONSUMES, PositivePartOfNegation.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = PositivePartOfNegation(amount=AMOUNT, output=OUTPUT)

    assert wired.compute((Artifact(AMOUNT, D("-4")),)).outputs == (Artifact(OUTPUT, D("4")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        PositivePartOfNegation(AMOUNT, OUTPUT, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="PositivePartOfNegation") as raised:
        PositivePartOfNegation(AMOUNT, AMOUNT)

    assert "'amount'" in str(raised.value)
    assert "'output'" in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="PositivePartOfNegation.*'amount'"):
        PositivePartOfNegation((AMOUNT,), OUTPUT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="PositivePartOfNegation.*'amount'"):
        PositivePartOfNegation(count, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(PositivePartOfNegation, "__type_params__", ())
    assert not getattr(PositivePartOfNegation, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_a_negative_amount_is_produced_as_a_positive_amount() -> None:
    output = compute("-1234.56")

    assert output == Artifact(OUTPUT, D("1234.56"))
    assert type(output.value) is Decimal


def test_a_positive_amount_gives_zero() -> None:
    output = compute("1234.56")

    assert output == Artifact(OUTPUT, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_amount_gives_zero() -> None:
    assert compute("0") == Artifact(OUTPUT, D("0"))


def test_a_negative_amount_keeps_its_scale() -> None:
    assert str(compute("-1.50").value) == "1.50"
    assert str(compute("-7").value) == "7"


def test_a_negative_amount_is_not_rounded() -> None:
    assert compute("-0.0000000000000000000000000001") == Artifact(
        OUTPUT, D("0.0000000000000000000000000001")
    )


def test_a_large_negative_amount_is_exact() -> None:
    assert compute("-12345678901234567890123456789.01") == Artifact(
        OUTPUT, D("12345678901234567890123456789.01")
    )


@pytest.mark.parametrize("amount", ["5", "0", "0.00", "-0", "-0.00", "3.50"])
def test_anything_but_a_negative_amount_gives_a_plain_zero(amount: str) -> None:
    value = compute(amount).value

    assert str(value) == "0"
    assert not value.is_signed()


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("9"))

    result = capability().compute((other, Artifact(AMOUNT, D("-2"))))

    assert result.outputs == (Artifact(OUTPUT, D("2")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="net_result"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute((Artifact(AMOUNT, D("-1")),)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()
    given = (Artifact(AMOUNT, D("-1.5")),)

    assert wired.compute(given) == wired.compute(given)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_positive_part_of_negation_line() -> None:
    trace = capability().compute((Artifact(AMOUNT, D("-1234.56")),)).trace

    assert trace == (
        PositivePartOfNegationLine(
            output=OUTPUT,
            amount_kind=AMOUNT,
            amount_value=D("-1234.56"),
            result=D("1234.56"),
        ),
    )


def test_traces_a_positive_amount_with_a_zero_result() -> None:
    trace = capability().compute((Artifact(AMOUNT, D("10")),)).trace

    assert trace == (PositivePartOfNegationLine(OUTPUT, AMOUNT, D("10"), D("0")),)


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute((Artifact(AMOUNT, D("-3")),)).trace

    assert [line.amount for line in trace] == [D("3")]


def test_trace_holds_no_text() -> None:
    for line in capability().compute((Artifact(AMOUNT, D("-3")),)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
