"""Unit tests for the CountRefusedByConditions capability (`ca/count_refused_by_conditions`).

An int code that names one option of a form (a line, a province) must be one of the printed codes;
a code the form does not list is refused, never sent quietly to no option. Its slots: one parameter
slot `conditions` (a `conditions` dataset, the same kind `ca/count_by_conditions` reads), one
consumed single slot `count` (an `int` kind), one produced slot `output` (an `int` kind).

The dataset lists the conditions under which the count is REFUSED, in the form's order and
wording. Only the count (position 1) may be read: a test of an amount, or a comparison with
`against`, is refused by the constructor (`InvalidCapabilityError`). A condition applies when every
one of its parts holds and a part holds when any of its tests holds, as for
`ca/count_by_conditions`; `count_when_any_applies` is a field of the shared kind and is not read
here. When any condition applies the count is an input error, `InputOutOfRangeError`, naming the
kind, the value and the text of the first condition that applies. Otherwise the output is the count
unchanged, and one `CountNotRefusedLine` is recorded.

The artifact kinds and the dataset family are made up; the codes are those of Form T2125's line
choice (1 business, 2 professional, 3 commission). The wiring comes later.
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
    InputOutOfRangeError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.domain.trace import CountNotRefusedLine
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)

D = Decimal

# --- made-up kinds -----------------------------------------------------------------------------

LINE_CODE = ArtifactKind("ex/line_code", int)
LINE_CODE_CHECKED = ArtifactKind("ex/line_code_checked", int)
OTHER_COUNT = ArtifactKind("ex/other_count", int)
AMOUNT = ArtifactKind("ex/amount", Decimal)

# --- made-up datasets ---------------------------------------------------------------------------


def a_test(relation: str, than: int) -> ConditionTest:
    return ConditionTest("count", 1, relation, D(than), None)


def dataset(values: ConditionList, family: str = "ex/refused") -> ParameterDataset[ConditionList]:
    return ParameterDataset(
        family, 2025, CONDITIONS, values, NO_ROUNDING, ("https://example.org/refused",)
    )


NOT_1_2_OR_3_TEXT = "the line code is not 1, 2 or 3"

# One condition of three parts, each one test: the code is refused when it is none of 1, 2 and 3.
NOT_1_2_OR_3 = dataset(
    ConditionList(
        1,
        (
            Condition(
                NOT_1_2_OR_3_TEXT,
                tuple(ConditionPart((a_test("not_equal_to", code),)) for code in (1, 2, 3)),
            ),
        ),
    ),
    "ex/line_code_refused",
)

# Two conditions, the second of one part of two tests (any holds): refused when the code is 7, or
# when it is 0 or above 20.
TWO_CONDITIONS = dataset(
    ConditionList(
        1,
        (
            Condition("the code is 7", (ConditionPart((a_test("equal_to", 7),)),)),
            Condition(
                "the code is 0 or above 20",
                (ConditionPart((a_test("equal_to", 0), a_test("more_than", 20))),),
            ),
        ),
    ),
    "ex/two_refused",
)


def capability(values: ParameterDataset[ConditionList] = NOT_1_2_OR_3) -> CountRefusedByConditions:
    return CountRefusedByConditions(values, LINE_CODE, LINE_CODE_CHECKED)


def inputs(count: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(LINE_CODE, count),)


def compute(count: int, values: ParameterDataset[ConditionList] = NOT_1_2_OR_3) -> Artifact[Any]:
    (output,) = capability(values).compute(inputs(count)).outputs
    return output


# --- contract -----------------------------------------------------------------------------------


def test_is_registered_as_ca_count_refused_by_conditions() -> None:
    registered = CapabilityRegistry.shared().get("ca/count_refused_by_conditions")

    assert registered is CountRefusedByConditions


def test_is_exported_from_the_ca_capabilities_package() -> None:
    assert "count_refused_by_conditions" in ca_capabilities.__all__
    module = ca_capabilities.count_refused_by_conditions
    assert module.CountRefusedByConditions is CountRefusedByConditions


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LINE_CODE})
    assert capability().produces == frozenset({LINE_CODE_CHECKED})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(CountRefusedByConditions)
    assert "produces" not in vars(CountRefusedByConditions)


def test_declares_its_slots() -> None:
    assert CountRefusedByConditions.PARAMETERS == {"conditions": CONDITIONS}
    assert CountRefusedByConditions.CONSUMES == {"count": int}
    assert CountRefusedByConditions.PRODUCES == {"output": int}
    assert not CountRefusedByConditions.is_list_slot("count")


def test_its_slots_are_read_only() -> None:
    for slots in (
        CountRefusedByConditions.PARAMETERS,
        CountRefusedByConditions.CONSUMES,
        CountRefusedByConditions.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(CountRefusedByConditions.CONSUMES, Mapping[str, type])
    assert_type(CountRefusedByConditions.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (CountRefusedByConditions.CONSUMES, CountRefusedByConditions.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = int


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = CountRefusedByConditions(
        conditions=NOT_1_2_OR_3, count=LINE_CODE, output=LINE_CODE_CHECKED
    )

    assert wired.compute(inputs(2)).outputs == (Artifact(LINE_CODE_CHECKED, 2),)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(CountRefusedByConditions, "__type_params__", ())
    assert not getattr(CountRefusedByConditions, "__parameters__", ())


# --- what the constructor refuses ---------------------------------------------------------------


def test_refuses_one_kind_in_two_slots() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions") as raised:
        CountRefusedByConditions(NOT_1_2_OR_3, LINE_CODE, LINE_CODE)

    assert "'count'" in str(raised.value)
    assert "'output'" in str(raised.value)


def test_refuses_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions.*'count'"):
        CountRefusedByConditions(NOT_1_2_OR_3, (LINE_CODE,), LINE_CODE_CHECKED)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_a_count() -> None:
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions.*'count'"):
        CountRefusedByConditions(NOT_1_2_OR_3, AMOUNT, LINE_CODE_CHECKED)  # type: ignore[arg-type]


def test_refuses_a_money_kind_as_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions.*'output'"):
        CountRefusedByConditions(NOT_1_2_OR_3, LINE_CODE, AMOUNT)  # type: ignore[arg-type]


def test_refuses_a_test_of_an_amount() -> None:
    reads_an_amount = dataset(
        ConditionList(
            1,
            (
                Condition(
                    "there is an amount",
                    (ConditionPart((ConditionTest("amount", 1, "not_equal_to", D(0), None),)),),
                ),
            ),
        )
    )

    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions.*amount"):
        capability(reads_an_amount)


def test_refuses_a_comparison_with_another_figure() -> None:
    compares = dataset(
        ConditionList(
            1,
            (
                Condition(
                    "the code is above the other",
                    (ConditionPart((ConditionTest("amount", 1, "more_than", None, 2),)),),
                ),
            ),
        )
    )

    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions"):
        capability(compares)


def test_refuses_a_second_count_position() -> None:
    second = dataset(
        ConditionList(
            1,
            (
                Condition(
                    "the second code is 3",
                    (ConditionPart((ConditionTest("count", 2, "equal_to", D(3), None),)),),
                ),
            ),
        )
    )

    with pytest.raises(InvalidCapabilityError, match="CountRefusedByConditions.*position 2"):
        capability(second)


# --- computing: a code that is not refused ------------------------------------------------------


@pytest.mark.parametrize("code", [1, 2, 3])
def test_a_listed_code_is_produced_unchanged(code: int) -> None:
    output = compute(code)

    assert output == Artifact(LINE_CODE_CHECKED, code)
    assert type(output.value) is int


def test_the_output_is_the_count_whatever_value_count_when_any_applies_holds() -> None:
    zero = dataset(ConditionList(0, NOT_1_2_OR_3.values.conditions), "ex/zero")

    assert compute(2, zero) == Artifact(LINE_CODE_CHECKED, 2)
    with pytest.raises(InputOutOfRangeError):
        compute(9, zero)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(OTHER_COUNT, 9)

    assert capability().compute((other, *inputs(1))).outputs == (Artifact(LINE_CODE_CHECKED, 1),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="line_code"):
        capability().compute(())


def test_has_one_output() -> None:
    assert len(capability().compute(inputs(1)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = capability()

    assert wired.compute(inputs(3)) == wired.compute(inputs(3))


def test_a_code_not_listed_by_any_condition_passes() -> None:
    assert compute(8, TWO_CONDITIONS) == Artifact(LINE_CODE_CHECKED, 8)
    assert compute(20, TWO_CONDITIONS) == Artifact(LINE_CODE_CHECKED, 20)


# --- computing: a code that is refused ----------------------------------------------------------


@pytest.mark.parametrize("code", [0, 4, 5, 99])
def test_a_code_outside_the_listed_ones_is_an_input_out_of_range_error(code: int) -> None:
    with pytest.raises(InputOutOfRangeError):
        compute(code)


def test_the_error_names_the_kind_the_value_and_the_condition() -> None:
    with pytest.raises(
        InputOutOfRangeError,
        match=r"^ex/line_code 0 is refused: the line code is not 1, 2 or 3$",
    ):
        compute(0)


def test_the_error_names_the_value_that_was_given() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"ex/line_code 4 is refused"):
        compute(4)


def test_a_part_with_two_tests_holds_when_any_of_them_does() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"ex/line_code 0 is refused: the code is 0 or"):
        compute(0, TWO_CONDITIONS)
    with pytest.raises(InputOutOfRangeError, match=r"ex/line_code 21 is refused: the code is 0 or"):
        compute(21, TWO_CONDITIONS)


def test_the_error_names_the_first_condition_that_applies() -> None:
    with pytest.raises(InputOutOfRangeError, match=r"ex/line_code 7 is refused: the code is 7$"):
        compute(7, TWO_CONDITIONS)


def test_a_condition_applies_only_when_every_part_holds() -> None:
    # 1 differs from 2 and 3 but is 1: the part for 1 does not hold, so the code is not refused.
    assert compute(1) == Artifact(LINE_CODE_CHECKED, 1)


def test_an_input_out_of_range_error_is_a_domain_error_of_its_own() -> None:
    with pytest.raises(InputOutOfRangeError) as raised:
        compute(0)

    assert issubclass(InputOutOfRangeError, DomainError)
    assert not isinstance(raised.value, InputAboveBoundError)
    assert not isinstance(raised.value, InputBelowBoundError)
    assert not issubclass(InputOutOfRangeError, InvalidCapabilityError)


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_count_not_refused_line() -> None:
    assert capability().compute(inputs(2)).trace == (
        CountNotRefusedLine(output=LINE_CODE_CHECKED, count_kind=LINE_CODE, count=2),
    )


def test_trace_amount_is_the_count() -> None:
    trace = capability().compute(inputs(3)).trace

    assert [line.amount for line in trace] == [D(3)]


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs(1)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
