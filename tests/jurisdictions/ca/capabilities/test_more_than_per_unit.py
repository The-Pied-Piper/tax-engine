"""Unit tests for the MoreThanPerUnit capability (`ca/more_than_per_unit`), with made-up kinds.

For a form line that prints a total and a condition per unit, "fees for each institution must be
more than $100": the total is one caller input, and the caller's count of units is the second.
Its slots: one parameter slot `amount` (an `amount` dataset, the printed amount for each unit), two
consumed slots, `total` (a Decimal kind) and `count` (an `int` kind), and one produced slot
`output` (a Decimal kind). The minimum is `rounding.apply(amount x count)`, the same product
`core/per_unit_amount` takes, so the dataset's rule (half-up to the cent here) rounds it once.

With a count of 0 the total must be 0 (an input above it is `InputAboveBoundError`). With a count
above 0 the total must be strictly more than the minimum: a total equal to the minimum is refused
too, as `InputBelowBoundError`. The output is the total, unchanged. It records one
`MoreThanPerUnitLine` when it produces the output, and none when it raises.

This is a known limit, stated in the docstrings: the check refuses totals too small for the count
and nothing else: one total of $201 for two units passes though one unit paid $60.
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
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.trace import MoreThanPerUnitLine, PerUnitAmountLine
from tax_calculator.jurisdictions.ca.capabilities.more_than_per_unit import MoreThanPerUnit

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

TOTAL = ArtifactKind("ex/fee_total", Decimal)
COUNT = ArtifactKind("ex/fee_count", int)
OUTPUT = ArtifactKind("ex/fee_checked", Decimal)


def per_unit(value: str = "100.00", rounding: RoundingRule = CENT) -> ParameterDataset[Amount]:
    """By default a made-up $100.00 for each unit, rounded half-up to the cent."""
    return ParameterDataset(
        "ex/minimum_per_fee",
        2025,
        AMOUNT,
        Amount(D(value)),
        rounding,
        ("https://example.org/p",),
    )


def capability(amount: ParameterDataset[Amount] | None = None) -> MoreThanPerUnit:
    return MoreThanPerUnit(amount=amount or per_unit(), total=TOTAL, count=COUNT, output=OUTPUT)


def inputs(total: str, count: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(TOTAL, D(total)), Artifact(COUNT, count))


def compute(total: str, count: int) -> Artifact[Any]:
    (output,) = capability().compute(inputs(total, count)).outputs
    return output


def test_is_registered_as_ca_more_than_per_unit() -> None:
    assert CapabilityRegistry.shared().get("ca/more_than_per_unit") is MoreThanPerUnit


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "more_than_per_unit" in ca_capabilities.__all__
    assert ca_capabilities.more_than_per_unit.MoreThanPerUnit is MoreThanPerUnit


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TOTAL, COUNT})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(MoreThanPerUnit)
    assert "produces" not in vars(MoreThanPerUnit)


def test_declares_its_slots() -> None:
    assert MoreThanPerUnit.PARAMETERS == {"amount": AMOUNT}
    assert MoreThanPerUnit.CONSUMES == {"total": Decimal, "count": int}
    assert MoreThanPerUnit.PRODUCES == {"output": Decimal}
    assert not MoreThanPerUnit.is_list_slot("total")
    assert not MoreThanPerUnit.is_list_slot("count")


def test_its_slots_are_read_only() -> None:
    for slots in (MoreThanPerUnit.PARAMETERS, MoreThanPerUnit.CONSUMES, MoreThanPerUnit.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(MoreThanPerUnit.CONSUMES, Mapping[str, type])
    assert_type(MoreThanPerUnit.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (MoreThanPerUnit.CONSUMES, MoreThanPerUnit.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = MoreThanPerUnit(amount=per_unit(), total=TOTAL, count=COUNT, output=OUTPUT)

    assert wired.compute(inputs("101", 1)).outputs == (Artifact(OUTPUT, D("101")),)


@pytest.mark.parametrize(
    ("kinds", "slots"),
    [
        ((TOTAL, COUNT, TOTAL), ("'total'", "'output'")),
    ],
)
def test_rejects_one_kind_in_two_slots(
    kinds: tuple[ArtifactKind[Any], ArtifactKind[Any], ArtifactKind[Any]], slots: tuple[str, str]
) -> None:
    with pytest.raises(InvalidCapabilityError, match="MoreThanPerUnit") as raised:
        MoreThanPerUnit(amount=per_unit(), total=kinds[0], count=kinds[1], output=kinds[2])

    for slot in slots:
        assert slot in str(raised.value)


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="MoreThanPerUnit.*'count'"):
        MoreThanPerUnit(amount=per_unit(), total=TOTAL, count=(COUNT,), output=OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(MoreThanPerUnit, "__type_params__", ())
    assert not getattr(MoreThanPerUnit, "__parameters__", ())


# --- the minimum --------------------------------------------------------------------------------


def test_one_unit_at_100_needs_a_total_above_100() -> None:
    assert compute("100.01", 1) == Artifact(OUTPUT, D("100.01"))
    assert compute("101", 1) == Artifact(OUTPUT, D("101"))


def test_one_unit_at_exactly_its_minimum_is_refused() -> None:
    with pytest.raises(InputBelowBoundError):
        compute("100", 1)


def test_one_unit_below_its_minimum_is_refused() -> None:
    with pytest.raises(InputBelowBoundError):
        compute("60", 1)


def test_two_units_need_a_total_above_200() -> None:
    assert compute("201", 2) == Artifact(OUTPUT, D("201"))


def test_two_units_at_exactly_200_are_refused() -> None:
    with pytest.raises(InputBelowBoundError):
        compute("200", 2)


def test_two_units_with_a_total_of_120_are_refused_by_the_minimum_of_200() -> None:
    # Two institutions at $60 each, $120 in total, is not more than 2 x $100 = $200.
    with pytest.raises(InputBelowBoundError):
        compute("120", 2)


def test_the_known_limit_one_total_for_two_units_passes_when_it_clears_the_sum() -> None:
    # The check sees one total, not each unit's fees: $60 for one institution and $141 for the
    # other, $201 in total, is above the $200 minimum and passes, though $60 is below $100.
    assert compute("201", 2) == Artifact(OUTPUT, D("201"))


def test_the_minimum_is_rounded_once_with_the_datasets_rule() -> None:
    # 0.333 x 3 = 0.999, which rounds half-up to the cent as 1.00: a total of 1.00 is refused, and
    # 1.01 passes, so the per-unit amount itself is not rounded before the product.
    wired = capability(per_unit("0.333"))

    with pytest.raises(InputBelowBoundError):
        wired.compute(inputs("1.00", 3))
    assert wired.compute(inputs("1.01", 3)).outputs == (Artifact(OUTPUT, D("1.01")),)


def test_a_dataset_without_rounding_uses_the_exact_minimum() -> None:
    wired = capability(per_unit("0.333", NO_ROUNDING))

    assert wired.compute(inputs("1.0000", 3)).outputs == (Artifact(OUTPUT, D("1.0000")),)
    with pytest.raises(InputBelowBoundError):
        wired.compute(inputs("0.999", 3))


# --- no units ------------------------------------------------------------------------------------


def test_zero_units_with_a_total_of_zero_is_produced() -> None:
    output = compute("0", 0)

    assert output == Artifact(OUTPUT, D("0"))


def test_zero_units_with_a_total_of_zero_point_zero_zero_is_produced() -> None:
    assert compute("0.00", 0) == Artifact(OUTPUT, D("0"))


def test_zero_units_with_any_total_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        compute("101", 0)


def test_zero_units_with_a_cent_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        compute("0.01", 0)


def test_the_above_bound_error_names_the_total_its_value_the_count_and_zero() -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute("101", 0)

    message = str(raised.value)
    assert "ex/fee_total" in message
    assert "101" in message
    assert "ex/fee_count" in message
    assert "0" in message


def test_the_below_bound_error_names_the_total() -> None:
    with pytest.raises(InputBelowBoundError) as raised:
        compute("100", 1)

    assert "ex/fee_total" in str(raised.value)


def test_an_input_below_bound_error_is_not_an_input_above_bound_error() -> None:
    assert not issubclass(InputBelowBoundError, InputAboveBoundError)
    assert not issubclass(InputAboveBoundError, InputBelowBoundError)


def test_both_bound_errors_are_domain_errors() -> None:
    assert issubclass(InputBelowBoundError, DomainError)
    assert issubclass(InputAboveBoundError, DomainError)


# --- computing ----------------------------------------------------------------------------------


def test_the_output_is_the_total_unchanged() -> None:
    output = compute("250.50", 2)

    assert output == Artifact(OUTPUT, D("250.50"))
    assert type(output.value) is Decimal


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", int), 9)

    assert capability().compute((other, *inputs("101", 1))).outputs == (Artifact(OUTPUT, D("101")),)


def test_a_missing_total_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="fee_total"):
        capability().compute((Artifact(COUNT, 1),))


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="fee_count"):
        capability().compute((Artifact(TOTAL, D("101")),))


def test_has_one_output() -> None:
    assert len(capability().compute(inputs("101", 1)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs("101", 1)) == wired.compute(inputs("101", 1))


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_more_than_per_unit_line() -> None:
    assert capability().compute(inputs("101", 1)).trace == (
        MoreThanPerUnitLine(
            output=OUTPUT,
            total_kind=TOTAL,
            total=D("101"),
            count_kind=COUNT,
            count=1,
            per_unit=Amount(D("100.00")),
            rounding=CENT,
            minimum_total=D("100.00"),
        ),
    )


def test_the_line_holds_the_minimum_it_checked_the_total_against() -> None:
    (line,) = capability().compute(inputs("201", 2)).trace

    assert isinstance(line, MoreThanPerUnitLine)
    assert line.minimum_total == D("200.00")
    assert line.count == 2
    assert line.per_unit == Amount(D("100.00"))


def test_a_zero_count_line_holds_a_minimum_of_zero() -> None:
    (line,) = capability().compute(inputs("0", 0)).trace

    assert line == MoreThanPerUnitLine(
        output=OUTPUT,
        total_kind=TOTAL,
        total=D("0"),
        count_kind=COUNT,
        count=0,
        per_unit=Amount(D("100.00")),
        rounding=CENT,
        minimum_total=D("0.00"),
    )


def test_trace_amount_is_the_total() -> None:
    trace = capability().compute(inputs("101", 1)).trace

    assert [line.amount for line in trace] == [D("101")]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs("101", 1)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_lines_differ_by_total_and_count() -> None:
    (base,) = capability().compute(inputs("101", 1)).trace
    (more_total,) = capability().compute(inputs("102", 1)).trace
    (more_count,) = capability().compute(inputs("201", 2)).trace

    assert base != more_total
    assert base != more_count
    assert hash(base) == hash(capability().compute(inputs("101", 1)).trace[0])


def test_a_more_than_per_unit_line_is_not_a_per_unit_amount_line() -> None:
    (line,) = capability().compute(inputs("101", 1)).trace

    assert not isinstance(line, PerUnitAmountLine)
