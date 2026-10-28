"""Unit tests for the AmountForCount capability (`core/amount_by_count`), made-up values.

Its slots: one parameter slot `table` (an `amount_by_count` dataset, the amounts a form prints
against counts), one consumed slot `count` (an `int` artifact) and one produced slot `output`.
The output is `rounding.apply(row)`: the figure of the table's row for the count, rounded once
with the `table` dataset's rule, which defaults to no rounding. A count with no row is not
guessed at, floored or carried over from the nearest row: it is a `NoAmountForCountError`, an
input error naming the count. It records one `AmountByCountLine` holding the count's kind, the
count, the row's figure, the rounding rule and the result.

The class is `AmountForCount`, not `AmountByCount`, so it does not share a name with the
`AmountByCount` value object it reads.
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
from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import (
    DomainError,
    InvalidAmountByCountError,
    InvalidCapabilityError,
    MissingArtifactError,
    NoAmountForCountError,
    ValidationError,
)
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import AmountByCountLine

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


MONTHS = ArtifactKind("ex/month_count", int)
MONTHLY_AMOUNT = ArtifactKind("ex/monthly_amount", Decimal)


def values() -> AmountByCount:
    """The made-up table: counts 1 to 4, the amount growing with the count."""
    return AmountByCount(((1, D("100")), (2, D("200.50")), (3, D("300")), (4, D("400.255"))))


def table(
    table_values: AmountByCount | None = None, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[AmountByCount]:
    return ParameterDataset(
        "ex/some_amount_by_count",
        2025,
        AMOUNT_BY_COUNT,
        table_values or values(),
        rounding,
        ("https://example.org/t",),
    )


def capability(table_data: ParameterDataset[AmountByCount] | None = None) -> AmountForCount:
    """By default the made-up months under the default table, exact."""
    return AmountForCount(table_data or table(), MONTHS, MONTHLY_AMOUNT)


def compute(wired: AmountForCount, count: int) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(MONTHS, count),)).outputs
    return output


def test_is_registered_as_core_amount_by_count() -> None:
    assert CapabilityRegistry.shared().get("core/amount_by_count") is AmountForCount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "amount_by_count" in core.__all__
    assert core.amount_by_count.AmountForCount is AmountForCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({MONTHS})
    assert capability().produces == frozenset({MONTHLY_AMOUNT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(AmountForCount)
    assert "produces" not in vars(AmountForCount)


def test_declares_its_slots() -> None:
    assert AmountForCount.PARAMETERS == {"table": AMOUNT_BY_COUNT}
    assert AmountForCount.PARAMETERS["table"] is AMOUNT_BY_COUNT
    assert AmountForCount.CONSUMES == {"count": int}
    assert AmountForCount.CONSUMES["count"] is int
    assert AmountForCount.PRODUCES == {"output": Decimal}
    assert not AmountForCount.is_list_slot("count")


def test_its_slots_are_read_only() -> None:
    for slots in (AmountForCount.PARAMETERS, AmountForCount.CONSUMES, AmountForCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(AmountForCount.PARAMETERS, Mapping[str, ParameterKind[AmountByCount]])
    assert_type(AmountForCount.CONSUMES, Mapping[str, type])
    assert_type(AmountForCount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (AmountForCount.PARAMETERS, AmountForCount.CONSUMES, AmountForCount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = AmountForCount(table=table(), count=MONTHS, output=MONTHLY_AMOUNT)

    assert compute(wired, 2) == Artifact(MONTHLY_AMOUNT, D("200.50"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        AmountForCount(table(), MONTHS, MONTHLY_AMOUNT, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountForCount.*'count'"):
        AmountForCount(table(), (MONTHS,), MONTHLY_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_its_count() -> None:
    money = ArtifactKind("ex/money_count", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="AmountForCount.*'count'"):
        AmountForCount(table(), money, MONTHLY_AMOUNT)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_int_kind_for_its_output() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="AmountForCount.*'output'"):
        AmountForCount(table(), MONTHS, other_count)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # An amount dataset is not a ParameterDataset[AmountByCount]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        amount = ParameterDataset(
            "ex/some_amount", 2025, AMOUNT, Amount(D("5")), NO_ROUNDING, ("https://example.org/a",)
        )
        AmountForCount(amount, MONTHS, MONTHLY_AMOUNT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(AmountForCount, "__type_params__", ())
    assert not getattr(AmountForCount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_produces_the_row_for_the_count() -> None:
    output = compute(capability(), 1)

    assert output == Artifact(MONTHLY_AMOUNT, D("100"))
    assert type(output.value) is Decimal


@pytest.mark.parametrize(
    ("count", "amount"),
    [(1, "100"), (2, "200.50"), (3, "300"), (4, "400.255")],
)
def test_produces_each_row_of_the_table(count: int, amount: str) -> None:
    assert compute(capability(), count) == Artifact(MONTHLY_AMOUNT, D(amount))


def test_the_rows_are_looked_up_by_count_not_by_position() -> None:
    wired = capability(table(AmountByCount(((5, D("50")), (2, D("20")), (9, D("90"))))))

    assert compute(wired, 9) == Artifact(MONTHLY_AMOUNT, D("90"))
    assert compute(wired, 5) == Artifact(MONTHLY_AMOUNT, D("50"))
    assert compute(wired, 2) == Artifact(MONTHLY_AMOUNT, D("20"))


def test_a_count_of_zero_has_a_row_only_if_the_table_lists_it() -> None:
    wired = capability(table(AmountByCount(((0, D("0")), (1, D("100"))))))

    assert compute(wired, 0) == Artifact(MONTHLY_AMOUNT, D("0"))


def test_keeps_the_amount_exact_without_rounding() -> None:
    assert compute(capability(), 4) == Artifact(MONTHLY_AMOUNT, D("400.255"))


def test_keeps_the_scale_of_the_row_without_rounding() -> None:
    wired = capability(table(AmountByCount(((1, D("100.00")), (2, D("5E+2"))))))

    assert str(compute(wired, 1).value) == "100.00"
    assert str(compute(wired, 2).value) == "5E+2"


def test_does_not_interpolate_between_rows() -> None:
    # No row is the average, the next lower or the next higher one: a gap is a gap.
    wired = capability(table(AmountByCount(((1, D("100")), (3, D("300"))))))

    with pytest.raises(NoAmountForCountError):
        compute(wired, 2)


def test_rounds_the_row_with_the_datasets_rule() -> None:
    wired = capability(table(rounding=CENT))

    # 400.255 half-up to 400.26; a row already at the cent is unchanged but carries the scale.
    assert compute(wired, 4) == Artifact(MONTHLY_AMOUNT, D("400.26"))
    assert str(compute(wired, 4).value) == "400.26"
    assert str(compute(wired, 1).value) == "100.00"
    assert str(compute(wired, 2).value) == "200.50"


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(table(rounding=RoundTo(D("1"), RoundingMode.FLOOR)))

    assert compute(wired, 2) == Artifact(MONTHLY_AMOUNT, D("200"))
    assert compute(wired, 4) == Artifact(MONTHLY_AMOUNT, D("400"))


def test_a_zero_row_is_a_plain_zero_under_a_rounding_rule() -> None:
    wired = capability(table(AmountByCount(((1, D("0")), (2, D("5")))), CENT))

    assert compute(wired, 1) == Artifact(MONTHLY_AMOUNT, D("0"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), Artifact(MONTHS, 3)))

    assert result.outputs == (Artifact(MONTHLY_AMOUNT, D("300")),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="month_count"):
        capability().compute(())


# --- a count without a row ---------------------------------------------------------------------


def test_a_count_below_the_first_row_is_refused() -> None:
    with pytest.raises(NoAmountForCountError, match="count 0"):
        compute(capability(), 0)


def test_a_count_above_the_last_row_is_refused() -> None:
    with pytest.raises(NoAmountForCountError, match="count 5"):
        compute(capability(), 5)


def test_a_negative_count_is_refused() -> None:
    with pytest.raises(NoAmountForCountError, match="count -1"):
        compute(capability(), -1)


def test_the_refusal_names_the_count_kind() -> None:
    with pytest.raises(NoAmountForCountError, match="ex/month_count") as raised:
        compute(capability(), 13)

    assert "13" in str(raised.value)


def test_the_refusal_is_an_input_error_of_its_own() -> None:
    assert issubclass(NoAmountForCountError, DomainError)
    # A validation error is already a 422 problem response, so no status mapping is added.
    assert issubclass(NoAmountForCountError, ValidationError)
    assert not issubclass(NoAmountForCountError, InvalidAmountByCountError)
    assert not issubclass(InvalidAmountByCountError, NoAmountForCountError)


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_amount_by_count_line() -> None:
    trace = capability().compute((Artifact(MONTHS, 2),)).trace

    assert trace == (
        AmountByCountLine(
            output=MONTHLY_AMOUNT,
            count_kind=MONTHS,
            count=2,
            row=D("200.50"),
            rounding=NO_ROUNDING,
            result=D("200.50"),
        ),
    )


def test_traces_the_row_and_the_rounded_result() -> None:
    trace = capability(table(rounding=CENT)).compute((Artifact(MONTHS, 4),)).trace

    assert trace == (AmountByCountLine(MONTHLY_AMOUNT, MONTHS, 4, D("400.255"), CENT, D("400.26")),)


def test_traces_the_count_as_an_int() -> None:
    (line,) = capability().compute((Artifact(MONTHS, 3),)).trace

    assert isinstance(line, AmountByCountLine)
    assert type(line.count) is int
    assert line.count_kind is MONTHS


def test_trace_amount_is_the_result() -> None:
    trace = capability(table(rounding=CENT)).compute((Artifact(MONTHS, 4),)).trace

    assert [line.amount for line in trace] == [D("400.26")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute((Artifact(MONTHS, 1),))

    assert [line.amount for line in result.trace] == [output.value for output in result.outputs]


def test_trace_holds_no_text() -> None:
    trace = capability().compute((Artifact(MONTHS, 1),)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
