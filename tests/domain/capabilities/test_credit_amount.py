"""Unit tests for the CreditAmount capability (`core/credit_amount`), with made-up kinds and values.

Its slots: one parameter slot `amount` (a `credit` dataset), no consumed slots and one produced
slot `output`. The output is the dataset's credit amount, rounded only with that dataset's rule
(which defaults to no rounding); it records one `CreditAmountLine`. Having no consumed slots, it
has no incoming edges in a composition, and it is not an orphan while something consumes its
output.
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
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.composition import Composition
from tax_calculator.domain.errors import InvalidCapabilityError, InvalidCompositionError
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import CreditAmountLine, SumLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


PERSONAL_AMOUNT = ArtifactKind("ex/personal_amount", Decimal)
OTHER_AMOUNT = ArtifactKind("ex/other_amount", Decimal)
TOTAL_AMOUNTS = ArtifactKind("ex/total_amounts", Decimal)


def amount(value: str = "1000", rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[Credit]:
    return ParameterDataset(
        "ex/personal_credit", 2025, CREDIT, Credit(D(value)), rounding, ("https://example.org/c",)
    )


def capability(amount_data: ParameterDataset[Credit] | None = None) -> CreditAmount:
    """By default the made-up credit dataset's amount of 1000, exact."""
    return CreditAmount(amount_data or amount(), PERSONAL_AMOUNT)


def compute(wired: CreditAmount) -> Artifact[Any]:
    (output,) = wired.compute(()).outputs
    return output


def test_is_registered_as_core_credit_amount() -> None:
    assert CapabilityRegistry.shared().get("core/credit_amount") is CreditAmount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "credit_amount" in core.__all__
    assert core.credit_amount.CreditAmount is CreditAmount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset()
    assert capability().produces == frozenset({PERSONAL_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CreditAmount)
    assert "produces" not in vars(CreditAmount)


def test_declares_its_slots() -> None:
    assert CreditAmount.PARAMETERS == {"amount": CREDIT}
    assert CreditAmount.PARAMETERS["amount"] is CREDIT
    assert CreditAmount.CONSUMES == {}
    assert CreditAmount.PRODUCES == {"output": Decimal}


def test_its_slots_are_read_only() -> None:
    for slots in (CreditAmount.PARAMETERS, CreditAmount.CONSUMES, CreditAmount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CreditAmount.PARAMETERS, Mapping[str, ParameterKind[Credit]])
    assert_type(CreditAmount.CONSUMES, Mapping[str, type])
    assert_type(CreditAmount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CreditAmount.PARAMETERS, CreditAmount.CONSUMES, CreditAmount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CreditAmount(amount=amount(), output=PERSONAL_AMOUNT)

    assert compute(wired) == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        CreditAmount(amount(), PERSONAL_AMOUNT, NO_ROUNDING)  # type: ignore[call-arg]


def test_takes_no_consumed_kind() -> None:
    with pytest.raises(TypeError):
        CreditAmount(amount(), OTHER_AMOUNT, PERSONAL_AMOUNT)  # type: ignore[call-arg]


def test_rejects_a_list_of_kinds_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CreditAmount.*'output'"):
        CreditAmount(amount(), (PERSONAL_AMOUNT,))  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = ArtifactKind("ex/count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="CreditAmount.*'output'"):
        CreditAmount(amount(), count)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[Credit]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.1")), NO_ROUNDING, ("https://example.org/r",)
        )
        CreditAmount(rate, PERSONAL_AMOUNT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CreditAmount, "__type_params__", ())
    assert not getattr(CreditAmount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_credit_datasets_amount() -> None:
    output = compute(capability())

    assert output == Artifact(PERSONAL_AMOUNT, D("1000"))
    assert type(output.value) is Decimal


def test_the_credit_dataset_supplies_the_amount() -> None:
    assert compute(capability(amount("16129"))) == Artifact(PERSONAL_AMOUNT, D("16129"))


def test_keeps_the_amount_exact_without_rounding() -> None:
    output = compute(capability(amount("1000.005")))

    assert output == Artifact(PERSONAL_AMOUNT, D("1000.005"))
    assert str(output.value) == "1000.005"


def test_keeps_many_decimals_exact_without_rounding() -> None:
    output = compute(capability(amount("1234567.0000000000000001")))

    assert output == Artifact(PERSONAL_AMOUNT, D("1234567.0000000000000001"))


def test_rounds_with_the_credit_datasets_rule() -> None:
    assert compute(capability(amount("1000.005", CENT))) == Artifact(PERSONAL_AMOUNT, D("1000.01"))


def test_rounds_with_another_rule_of_the_credit_dataset() -> None:
    wired = capability(amount("1000.99", RoundTo(D("1"), RoundingMode.FLOOR)))

    assert compute(wired) == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    assert str(compute(capability(amount("1000", CENT))).value) == "1000.00"


def test_a_zero_amount_produces_zero() -> None:
    output = compute(capability(amount("0")))

    assert output == Artifact(PERSONAL_AMOUNT, D("0"))
    assert type(output.value) is Decimal


def test_ignores_artifacts_it_does_not_consume() -> None:
    result = capability().compute((Artifact(OTHER_AMOUNT, D("9")),))

    assert result.outputs == (Artifact(PERSONAL_AMOUNT, D("1000")),)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_credit_amount_line() -> None:
    trace = capability().compute(()).trace

    assert trace == (
        CreditAmountLine(
            output=PERSONAL_AMOUNT,
            basis=Credit(D("1000")),
            rounding=NO_ROUNDING,
            value=D("1000"),
        ),
    )


def test_traces_the_credit_datasets_rounding_rule_and_the_rounded_amount() -> None:
    trace = capability(amount("1000.005", CENT)).compute(()).trace

    assert trace == (CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000.005")), CENT, D("1000.01")),)


def test_trace_value_and_amount_are_the_rounded_amount() -> None:
    (line,) = capability(amount("1000.005", CENT)).compute(()).trace

    assert isinstance(line, CreditAmountLine)
    assert line.value == D("1000.01")
    assert line.amount == line.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(()).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- in a composition: no incoming edges ------------------------------------------------------


def credit_and_sum() -> tuple[CreditAmount, Sum, Composition]:
    """The credit amount and an input summed into `ex/total_amounts`, given in the wrong order."""
    credit = capability(amount("1000.005", CENT))
    total = Sum((OTHER_AMOUNT, PERSONAL_AMOUNT), TOTAL_AMOUNTS)
    composition = Composition(
        [total, credit], inputs=frozenset({OTHER_AMOUNT}), outputs=frozenset({TOTAL_AMOUNTS})
    )
    return credit, total, composition


def test_a_composition_accepts_it_while_something_consumes_its_output() -> None:
    credit, total, composition = credit_and_sum()

    assert composition.order == (credit, total)


def test_its_output_is_a_part_of_a_sum() -> None:
    credit, total, composition = credit_and_sum()

    worksheet = composition.compute(Artifact(OTHER_AMOUNT, D("250.5")))

    assert worksheet.get(PERSONAL_AMOUNT) == Artifact(PERSONAL_AMOUNT, D("1000.01"))
    assert worksheet.producer_of(PERSONAL_AMOUNT) is credit
    assert worksheet.get(TOTAL_AMOUNTS) == Artifact(TOTAL_AMOUNTS, D("1250.51"))
    assert worksheet.trace == (
        CreditAmountLine(PERSONAL_AMOUNT, Credit(D("1000.005")), CENT, D("1000.01")),
        SumLine(
            TOTAL_AMOUNTS,
            ((OTHER_AMOUNT, D("250.5")), (PERSONAL_AMOUNT, D("1000.01"))),
            D("1250.51"),
        ),
    )


def test_its_output_may_be_a_declared_output() -> None:
    credit = capability()
    composition = Composition([credit], inputs=frozenset(), outputs=frozenset({PERSONAL_AMOUNT}))

    worksheet = composition.compute()

    assert composition.order == (credit,)
    assert worksheet.get(PERSONAL_AMOUNT) == Artifact(PERSONAL_AMOUNT, D("1000"))


def test_its_output_consumed_by_nothing_is_an_orphan() -> None:
    total = Sum((OTHER_AMOUNT,), TOTAL_AMOUNTS)

    with pytest.raises(InvalidCompositionError, match="orphan output 'personal_amount'"):
        Composition(
            [capability(), total],
            inputs=frozenset({OTHER_AMOUNT}),
            outputs=frozenset({TOTAL_AMOUNTS}),
        )
