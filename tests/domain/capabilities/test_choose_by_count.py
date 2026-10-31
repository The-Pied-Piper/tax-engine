"""Unit tests for the ChooseByCount capability (`core/choose_by_count`), with made-up kinds.

Its slots: three consumed single slots, `count` (an `int` artifact, the number of persons),
`when_none` and `when_any` (two `Decimal` artifacts, the candidates), one produced slot `output`,
no parameter slots. The output is `when_none` when the count is 0 and `when_any` for any other
count, the chosen value unchanged with its scale; it has no dataset, so it never rounds. It records
one `ChosenByCountLine` holding the count's kind, the count, and the chosen candidate's kind and
value.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.domain.capabilities as core
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK, PASS_ON, BlankRule
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
)
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.trace import (
    BlankFallbackLine,
    BlankPassedOnLine,
    ChosenByCountLine,
    TimesCountLine,
)

D = Decimal


DEPENDANTS = ArtifactKind("ex/dependant_count", int)
ALONE = ArtifactKind("ex/amount_alone", Decimal)
WITH_FAMILY = ArtifactKind("ex/amount_with_family", Decimal)
CHOSEN = ArtifactKind("ex/amount_chosen", Decimal)


def capability() -> ChooseByCount:
    """By default the made-up amount alone or with family, chosen by the made-up dependant count."""
    return ChooseByCount(DEPENDANTS, ALONE, WITH_FAMILY, CHOSEN)


def inputs(
    count: int, when_none: str = "1633", when_any: str = "2813"
) -> tuple[Artifact[Any], ...]:
    return (
        Artifact(DEPENDANTS, count),
        Artifact(ALONE, D(when_none)),
        Artifact(WITH_FAMILY, D(when_any)),
    )


def compute(count: int, when_none: str = "1633", when_any: str = "2813") -> Artifact[Any]:
    (output,) = capability().compute(inputs(count, when_none, when_any)).outputs
    return output


def test_is_registered_as_core_choose_by_count() -> None:
    assert CapabilityRegistry.shared().get("core/choose_by_count") is ChooseByCount


def test_is_exported_from_the_capabilities_package() -> None:
    assert "choose_by_count" in core.__all__
    assert core.choose_by_count.ChooseByCount is ChooseByCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({DEPENDANTS, ALONE, WITH_FAMILY})
    assert capability().produces == frozenset({CHOSEN})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ChooseByCount)
    assert "produces" not in vars(ChooseByCount)


def test_declares_its_slots() -> None:
    assert ChooseByCount.PARAMETERS == {}
    assert ChooseByCount.CONSUMES == {"count": int, "when_none": Decimal, "when_any": Decimal}
    assert ChooseByCount.CONSUMES["count"] is int
    assert ChooseByCount.PRODUCES == {"output": Decimal}
    assert not ChooseByCount.is_list_slot("count")
    assert not ChooseByCount.is_list_slot("when_none")
    assert not ChooseByCount.is_list_slot("when_any")
    assert not ChooseByCount.is_list_slot("output")


def test_its_slots_are_read_only() -> None:
    for slots in (ChooseByCount.PARAMETERS, ChooseByCount.CONSUMES, ChooseByCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ChooseByCount.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(ChooseByCount.CONSUMES, Mapping[str, type])
    assert_type(ChooseByCount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ChooseByCount.PARAMETERS, ChooseByCount.CONSUMES, ChooseByCount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ChooseByCount(count=DEPENDANTS, when_none=ALONE, when_any=WITH_FAMILY, output=CHOSEN)

    result = wired.compute(inputs(1))

    assert result.outputs == (Artifact(CHOSEN, D("2813")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        ChooseByCount(DEPENDANTS, ALONE, WITH_FAMILY, CHOSEN, object())  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_candidates() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount") as raised:
        ChooseByCount(DEPENDANTS, ALONE, ALONE, CHOSEN)

    message = str(raised.value)
    assert "'when_none'" in message
    assert "'when_any'" in message


def test_rejects_one_kind_as_both_a_candidate_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount") as raised:
        ChooseByCount(DEPENDANTS, ALONE, WITH_FAMILY, WITH_FAMILY)

    message = str(raised.value)
    assert "'when_any'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_count() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'count'"):
        ChooseByCount((DEPENDANTS,), ALONE, WITH_FAMILY, CHOSEN)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_first_candidate() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'when_none'"):
        ChooseByCount(DEPENDANTS, (ALONE,), WITH_FAMILY, CHOSEN)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_second_candidate() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'when_any'"):
        ChooseByCount(DEPENDANTS, ALONE, (WITH_FAMILY,), CHOSEN)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_money_kind_for_its_count() -> None:
    money = ArtifactKind("ex/money_count", Decimal)
    # An ArtifactKind[Decimal] is not an ArtifactKind[int]; the ignore fails under mypy
    # (warn_unused_ignores) if it is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'count'"):
        ChooseByCount(money, ALONE, WITH_FAMILY, CHOSEN)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_first_candidate() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'when_none'"):
        ChooseByCount(DEPENDANTS, other_count, WITH_FAMILY, CHOSEN)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_second_candidate() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'when_any'"):
        ChooseByCount(DEPENDANTS, ALONE, other_count, CHOSEN)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_output() -> None:
    other_count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByCount.*'output'"):
        ChooseByCount(DEPENDANTS, ALONE, WITH_FAMILY, other_count)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ChooseByCount, "__type_params__", ())
    assert not getattr(ChooseByCount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_a_count_of_zero_chooses_the_first_candidate() -> None:
    output = compute(0)

    assert output == Artifact(CHOSEN, D("1633"))
    assert type(output.value) is Decimal


def test_a_count_of_one_chooses_the_second_candidate() -> None:
    output = compute(1)

    assert output == Artifact(CHOSEN, D("2813"))
    assert type(output.value) is Decimal


def test_a_count_of_two_chooses_the_second_candidate() -> None:
    assert compute(2) == Artifact(CHOSEN, D("2813"))


def test_a_larger_count_chooses_the_second_candidate() -> None:
    assert compute(7) == Artifact(CHOSEN, D("2813"))


def test_a_negative_count_chooses_the_second_candidate() -> None:
    # Only a count of 0 chooses the first candidate; any other count, even one below zero on a
    # kind not declared non-negative, chooses the second. The count is not floored first.
    assert compute(-1) == Artifact(CHOSEN, D("2813"))


def test_the_count_only_chooses_and_does_not_scale() -> None:
    # A count of 3 chooses the second candidate as is, not three times it.
    assert compute(3, when_none="10", when_any="20") == Artifact(CHOSEN, D("20"))


def test_keeps_the_first_candidates_scale() -> None:
    assert str(compute(0, when_none="1633.00").value) == "1633.00"


def test_keeps_the_second_candidates_scale() -> None:
    assert str(compute(1, when_any="4319.40").value) == "4319.40"


def test_keeps_fractions_of_a_cent_exactly() -> None:
    assert str(compute(0, when_none="0.333").value) == "0.333"
    assert str(compute(2, when_any="1234567.0000000000000001").value) == "1234567.0000000000000001"


def test_a_negative_candidate_is_chosen_as_is_without_a_floor() -> None:
    assert compute(0, when_none="-250.75") == Artifact(CHOSEN, D("-250.75"))
    assert compute(1, when_any="-250.75") == Artifact(CHOSEN, D("-250.75"))


def test_a_zero_candidate_is_chosen_as_is() -> None:
    assert str(compute(0, when_none="0.00").value) == "0.00"


def test_the_candidate_not_chosen_does_not_matter() -> None:
    assert compute(0, when_any="-99999.99") == Artifact(CHOSEN, D("1633"))
    assert compute(1, when_none="-99999.99") == Artifact(CHOSEN, D("2813"))


def test_equal_candidates_give_that_value_for_any_count() -> None:
    assert compute(0, when_none="500", when_any="500") == Artifact(CHOSEN, D("500"))
    assert compute(1, when_none="500", when_any="500") == Artifact(CHOSEN, D("500"))


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs(1))))

    assert result.outputs == (Artifact(CHOSEN, D("2813")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs(0)))

    assert result.outputs == (Artifact(CHOSEN, D("1633")),)


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="dependant_count"):
        capability().compute((Artifact(ALONE, D("1633")), Artifact(WITH_FAMILY, D("2813"))))


def test_a_missing_first_candidate_when_it_is_chosen_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_alone"):
        capability().compute((Artifact(DEPENDANTS, 0), Artifact(WITH_FAMILY, D("2813"))))


def test_a_missing_second_candidate_when_it_is_chosen_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_with_family"):
        capability().compute((Artifact(DEPENDANTS, 1), Artifact(ALONE, D("1633"))))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_chosen_by_count_line_for_a_count_of_zero() -> None:
    trace = capability().compute(inputs(0)).trace

    assert trace == (
        ChosenByCountLine(
            output=CHOSEN,
            count_kind=DEPENDANTS,
            count=0,
            chosen_kind=ALONE,
            chosen_value=D("1633"),
        ),
    )


def test_traces_one_chosen_by_count_line_for_a_count_above_zero() -> None:
    trace = capability().compute(inputs(2)).trace

    assert trace == (ChosenByCountLine(CHOSEN, DEPENDANTS, 2, WITH_FAMILY, D("2813")),)


def test_traces_a_negative_count_as_choosing_the_second_candidate() -> None:
    trace = capability().compute(inputs(-1)).trace

    assert trace == (ChosenByCountLine(CHOSEN, DEPENDANTS, -1, WITH_FAMILY, D("2813")),)


def test_traces_the_chosen_value_with_its_own_scale() -> None:
    (line,) = capability().compute(inputs(1, when_any="4319.40")).trace

    assert isinstance(line, ChosenByCountLine)
    assert str(line.chosen_value) == "4319.40"


def test_traces_the_count_as_an_int() -> None:
    (line,) = capability().compute(inputs(3)).trace

    assert isinstance(line, ChosenByCountLine)
    assert type(line.count) is int
    assert line.count == 3


def test_trace_amount_is_the_chosen_value() -> None:
    trace = capability().compute(inputs(0)).trace

    assert [line.amount for line in trace] == [D("1633")]


def test_trace_chosen_value_is_the_output() -> None:
    result = capability().compute(inputs(1, when_any="4319.40"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ChosenByCountLine)
    assert line.chosen_value == output.value
    assert str(line.chosen_value) == str(output.value)


def test_traces_no_times_count_line() -> None:
    (line,) = capability().compute(inputs(1)).trace

    assert not isinstance(line, TimesCountLine)


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs(0)).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- blank ------------------------------------------------------------------------------------


def blank_inputs(
    count: int | None = 0, when_none: str | None = "1633", when_any: str | None = "2813"
) -> tuple[Artifact[Any], ...]:
    """The made-up inputs with None for a blank one."""
    return (
        Artifact(DEPENDANTS, BLANK if count is None else count),
        Artifact(ALONE, BLANK if when_none is None else D(when_none)),
        Artifact(WITH_FAMILY, BLANK if when_any is None else D(when_any)),
    )


def test_allows_a_blank_count_and_either_candidate_and_nothing_else() -> None:
    assert ChooseByCount.BLANK_ALLOWED == frozenset({"count", "when_none", "when_any"})


@pytest.mark.parametrize(
    "given",
    [blank_inputs(count=None), blank_inputs(when_none=None), blank_inputs(when_any=None)],
)
def test_refuses_a_blank_in_any_input_when_the_manifest_gives_no_rule(
    given: tuple[Artifact[Any], ...],
) -> None:
    with pytest.raises(BlankNotAllowedError):
        capability().run(given)


def test_refuses_a_blank_rule_on_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="output"):
        capability().with_blank_rules({"output": PASS_ON})


def test_a_blank_count_with_a_zero_fallback_chooses_the_first_candidate() -> None:
    result = capability().with_blank_rules({"count": 0}).run(blank_inputs(count=None))

    assert result.outputs == (Artifact(CHOSEN, D("1633")),)
    assert result.trace[0] == BlankFallbackLine(DEPENDANTS, 0)
    assert isinstance(result.trace[1], ChosenByCountLine)
    assert result.trace[1].chosen_kind == ALONE
    assert result.trace[1].count == 0


def test_a_blank_count_with_a_zero_fallback_does_not_read_a_blank_unchosen_candidate() -> None:
    rules: dict[str, BlankRule] = {"count": 0, "when_any": D("0")}

    result = capability().with_blank_rules(rules).run(blank_inputs(count=None, when_any=None))

    assert result.outputs == (Artifact(CHOSEN, D("1633")),)


def test_a_blank_chosen_candidate_passes_on_to_a_blank_output() -> None:
    rules: dict[str, BlankRule] = {"when_none": PASS_ON, "when_any": PASS_ON}

    result = capability().with_blank_rules(rules).run(blank_inputs(count=0, when_none=None))

    (output,) = result.outputs
    assert output.is_blank
    assert result.trace == (BlankPassedOnLine(CHOSEN, (ALONE,)),)


def test_a_blank_count_and_a_blank_chosen_candidate_give_a_blank_output() -> None:
    rules: dict[str, BlankRule] = {"count": 0, "when_none": PASS_ON, "when_any": PASS_ON}

    result = capability().with_blank_rules(rules).run(blank_inputs(count=None, when_none=None))

    (output,) = result.outputs
    assert output.is_blank
    assert result.trace[0] == BlankFallbackLine(DEPENDANTS, 0)
    assert result.trace[1] == BlankPassedOnLine(CHOSEN, (ALONE,))


def test_a_blank_second_candidate_is_chosen_by_a_count_of_one() -> None:
    rules: dict[str, BlankRule] = {"when_none": D("0"), "when_any": PASS_ON}

    result = capability().with_blank_rules(rules).run(blank_inputs(count=1, when_any=None))

    (output,) = result.outputs
    assert output.is_blank


def test_a_candidate_fallback_replaces_the_blank_by_the_fallback_value() -> None:
    result = (
        capability()
        .with_blank_rules({"when_any": D("0")})
        .run(blank_inputs(count=1, when_any=None))
    )

    assert result.outputs == (Artifact(CHOSEN, D("0")),)
    assert result.trace[0] == BlankFallbackLine(WITH_FAMILY, D("0"))
