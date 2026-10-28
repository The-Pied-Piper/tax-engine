"""Unit tests for the AmountWhenMore capability (`ca/amount_when_more`), with made-up kinds.

For a line that reads "if the amount on line A is more than the amount on line B, complete this
line". Its slots: four consumed single slots `amount`, `more` and `than` (`Decimal` kinds) and
the produced slot `output`; no parameter slots, no dataset. The output is the `amount`, unchanged
with its scale kept, when `more` is above `than`, else a plain `Decimal(0)`. It records one
`AmountWhenMoreLine`.
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
from tax_calculator.domain.trace import AmountWhenMoreLine
from tax_calculator.jurisdictions.ca.capabilities.amount_when_more import AmountWhenMore

D = Decimal

AMOUNT = ArtifactKind("ex/claimed_amount", Decimal)
MORE = ArtifactKind("ex/tested_amount", Decimal)
THAN = ArtifactKind("ex/limit_amount", Decimal)
OUTPUT = ArtifactKind("ex/passed_amount", Decimal)


def capability() -> AmountWhenMore:
    return AmountWhenMore(AMOUNT, MORE, THAN, OUTPUT)


def inputs(amount: str, more: str, than: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(AMOUNT, D(amount)), Artifact(MORE, D(more)), Artifact(THAN, D(than)))


def compute(amount: str, more: str, than: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, more, than)).outputs
    return output


def test_is_registered_as_ca_amount_when_more() -> None:
    assert CapabilityRegistry.shared().get("ca/amount_when_more") is AmountWhenMore


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "amount_when_more" in ca_capabilities.__all__
    assert ca_capabilities.amount_when_more.AmountWhenMore is AmountWhenMore


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({AMOUNT, MORE, THAN})
    assert capability().produces == frozenset({OUTPUT})
    assert "consumes" not in vars(AmountWhenMore)
    assert "produces" not in vars(AmountWhenMore)


def test_declares_its_slots() -> None:
    assert AmountWhenMore.PARAMETERS == {}
    assert AmountWhenMore.CONSUMES == {"amount": Decimal, "more": Decimal, "than": Decimal}
    assert AmountWhenMore.PRODUCES == {"output": Decimal}
    for slot in AmountWhenMore.CONSUMES:
        assert not AmountWhenMore.is_list_slot(slot)


def test_its_slots_are_read_only() -> None:
    for slots in (AmountWhenMore.PARAMETERS, AmountWhenMore.CONSUMES, AmountWhenMore.PRODUCES):
        assert isinstance(slots, MappingProxyType)
    with pytest.raises(TypeError):
        cast(Any, AmountWhenMore.CONSUMES)["extra"] = Decimal


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(AmountWhenMore.CONSUMES, Mapping[str, type])
    assert_type(AmountWhenMore.PRODUCES, Mapping[str, type])


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = AmountWhenMore(amount=AMOUNT, more=MORE, than=THAN, output=OUTPUT)

    assert wired.compute(inputs("5", "2", "1")).outputs == (Artifact(OUTPUT, D("5")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        AmountWhenMore(AMOUNT, MORE, THAN, OUTPUT, object())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((AMOUNT, AMOUNT, THAN, OUTPUT), ("'amount'", "'more'")),
        ((AMOUNT, MORE, MORE, OUTPUT), ("'more'", "'than'")),
        ((AMOUNT, MORE, THAN, AMOUNT), ("'amount'", "'output'")),
        ((AMOUNT, MORE, THAN, THAN), ("'than'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[Decimal], ...], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountWhenMore") as raised:
        AmountWhenMore(*kinds)

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_amount() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountWhenMore.*'amount'"):
        AmountWhenMore((AMOUNT,), MORE, THAN, OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="AmountWhenMore.*'more'"):
        AmountWhenMore(AMOUNT, count, THAN, OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(AmountWhenMore, "__type_params__", ())
    assert not getattr(AmountWhenMore, "__parameters__", ())


# --- computing ----------------------------------------------------------------------------------


def test_the_amount_passes_when_more_is_above_than() -> None:
    output = compute("1500.50", "70000.01", "70000")

    assert output == Artifact(OUTPUT, D("1500.50"))
    assert type(output.value) is Decimal


def test_the_amount_keeps_its_scale_and_is_not_rounded() -> None:
    assert str(compute("1500.50", "2", "1").value) == "1500.50"
    assert compute("0.123456789", "2", "1") == Artifact(OUTPUT, D("0.123456789"))


def test_the_amount_is_gated_off_when_more_equals_than() -> None:
    output = compute("1500.50", "70000", "70000")

    assert output == Artifact(OUTPUT, D("0"))
    assert str(output.value) == "0"


def test_the_amount_is_gated_off_when_more_is_below_than() -> None:
    assert compute("1500.50", "69999.99", "70000") == Artifact(OUTPUT, D("0"))


def test_negative_figures_compare_like_any_other() -> None:
    assert compute("4", "-1", "-2") == Artifact(OUTPUT, D("4"))
    assert compute("4", "-2", "-1") == Artifact(OUTPUT, D("0"))


def test_a_zero_amount_that_passes_stays_zero_with_its_scale() -> None:
    assert str(compute("0.00", "2", "1").value) == "0.00"


def test_a_negative_amount_passes_unchanged() -> None:
    assert compute("-7.25", "2", "1") == Artifact(OUTPUT, D("-7.25"))


def test_a_comparison_is_exact_not_rounded() -> None:
    assert compute("4", "1.0000000000000000000000000001", "1") == Artifact(OUTPUT, D("4"))


def test_a_gated_off_result_is_a_plain_zero() -> None:
    value = compute("4.50", "0", "1").value

    assert str(value) == "0"
    assert not value.is_signed()


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("9"))

    assert capability().compute((other, *inputs("5", "2", "1"))).outputs == (
        Artifact(OUTPUT, D("5")),
    )


@pytest.mark.parametrize(
    ("missing", "label"), [(0, "claimed_amount"), (1, "tested_amount"), (2, "limit_amount")]
)
def test_a_missing_input_is_a_missing_artifact(missing: int, label: str) -> None:
    given = tuple(a for i, a in enumerate(inputs("5", "2", "1")) if i != missing)

    with pytest.raises(MissingArtifactError, match=label):
        capability().compute(given)


def test_has_one_output() -> None:
    assert len(capability().compute(inputs("5", "2", "1")).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs("5", "2", "1")) == wired.compute(inputs("5", "2", "1"))


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_amount_when_more_line() -> None:
    trace = capability().compute(inputs("1500.50", "70000.01", "70000")).trace

    assert trace == (
        AmountWhenMoreLine(
            output=OUTPUT,
            amount_kind=AMOUNT,
            amount_value=D("1500.50"),
            more_kind=MORE,
            more_value=D("70000.01"),
            than_kind=THAN,
            than_value=D("70000"),
            result=D("1500.50"),
        ),
    )


def test_traces_a_gated_off_amount_with_a_zero_result() -> None:
    trace = capability().compute(inputs("1500.50", "70000", "70000")).trace

    assert trace == (
        AmountWhenMoreLine(
            OUTPUT, AMOUNT, D("1500.50"), MORE, D("70000"), THAN, D("70000"), D("0")
        ),
    )


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute(inputs("5", "2", "1")).trace

    assert [line.amount for line in trace] == [D("5")]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs("5", "2", "1")).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
