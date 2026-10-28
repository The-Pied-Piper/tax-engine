"""Unit tests for the ChooseByRange capability (`ca-on/choose_by_range`), with made-up kinds.

Its slots: six consumed single slots, `amount` (the `Decimal` artifact that is tested),
`first_limit` and `second_limit` (two `Decimal` artifacts, the upper ends of the first and second
ranges) and `first`, `second` and `third` (three `Decimal` artifacts, the candidates), one produced
slot `output`, no parameter slots. The output is `first` when the amount is at most `first_limit`,
`second` when it is more than `first_limit` but at most `second_limit`, and `third` when it is more
than `second_limit`: each limit belongs to the range below it. The chosen value is unchanged with
its scale; it has no dataset, so it never rounds. It records one `ChosenByRangeLine` holding the
tested amount's kind and value and the chosen candidate's kind and value.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca_on.capabilities as ontario
import tax_calculator.registrations
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.trace import ChosenByCountLine, ChosenByRangeLine
from tax_calculator.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange

D = Decimal


TESTED = ArtifactKind("ex/amount_tested", Decimal)
FIRST_LIMIT = ArtifactKind("ex/first_limit", Decimal)
SECOND_LIMIT = ArtifactKind("ex/second_limit", Decimal)
FIRST = ArtifactKind("ex/amount_first", Decimal)
SECOND = ArtifactKind("ex/amount_second", Decimal)
THIRD = ArtifactKind("ex/amount_third", Decimal)
CHOSEN = ArtifactKind("ex/amount_chosen", Decimal)

SLOTS = ("amount", "first_limit", "second_limit", "first", "second", "third")


def capability() -> ChooseByRange:
    """By default the made-up amounts first, second or third, chosen by the made-up tested amount
    against the made-up limits."""
    return ChooseByRange(TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD, CHOSEN)


def inputs(
    amount: str,
    first_limit: str = "500.05",
    second_limit: str = "1666.82",
    first: str = "10",
    second: str = "20",
    third: str = "30",
) -> tuple[Artifact[Any], ...]:
    return (
        Artifact(TESTED, D(amount)),
        Artifact(FIRST_LIMIT, D(first_limit)),
        Artifact(SECOND_LIMIT, D(second_limit)),
        Artifact(FIRST, D(first)),
        Artifact(SECOND, D(second)),
        Artifact(THIRD, D(third)),
    )


def compute(amount: str, **candidates: str) -> Artifact[Any]:
    (output,) = capability().compute(inputs(amount, **candidates)).outputs
    return output


def test_is_registered_as_ca_on_choose_by_range() -> None:
    assert (
        tax_calculator.registrations.CORE_PACKAGES
    )  # importing registrations imports the packages
    assert CapabilityRegistry.shared().get("ca-on/choose_by_range") is ChooseByRange


def test_is_exported_from_the_ontario_capabilities_package() -> None:
    assert ontario.NAMESPACE == "ca-on"
    assert "choose_by_range" in ontario.__all__
    assert ontario.choose_by_range.ChooseByRange is ChooseByRange


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset(
        {TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD}
    )
    assert capability().produces == frozenset({CHOSEN})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ChooseByRange)
    assert "produces" not in vars(ChooseByRange)


def test_declares_its_slots() -> None:
    assert ChooseByRange.PARAMETERS == {}
    assert ChooseByRange.CONSUMES == {
        "amount": Decimal,
        "first_limit": Decimal,
        "second_limit": Decimal,
        "first": Decimal,
        "second": Decimal,
        "third": Decimal,
    }
    assert ChooseByRange.PRODUCES == {"output": Decimal}
    for slot in (*SLOTS, "output"):
        assert not ChooseByRange.is_list_slot(slot)


def test_its_slots_are_read_only() -> None:
    for slots in (ChooseByRange.PARAMETERS, ChooseByRange.CONSUMES, ChooseByRange.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ChooseByRange.PARAMETERS, Mapping[str, ParameterKind[Any]])
    assert_type(ChooseByRange.CONSUMES, Mapping[str, type])
    assert_type(ChooseByRange.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ChooseByRange.PARAMETERS, ChooseByRange.CONSUMES, ChooseByRange.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ChooseByRange(
        amount=TESTED,
        first_limit=FIRST_LIMIT,
        second_limit=SECOND_LIMIT,
        first=FIRST,
        second=SECOND,
        third=THIRD,
        output=CHOSEN,
    )

    result = wired.compute(inputs("1000"))

    assert result.outputs == (Artifact(CHOSEN, D("20")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        ChooseByRange(  # type: ignore[call-arg]
            TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD, CHOSEN, object()
        )


def test_rejects_one_kind_as_both_limits() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange") as raised:
        ChooseByRange(TESTED, FIRST_LIMIT, FIRST_LIMIT, FIRST, SECOND, THIRD, CHOSEN)

    message = str(raised.value)
    assert "'first_limit'" in message
    assert "'second_limit'" in message


def test_rejects_one_kind_as_both_the_first_and_second_candidates() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange") as raised:
        ChooseByRange(TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, FIRST, THIRD, CHOSEN)

    message = str(raised.value)
    assert "'first'" in message
    assert "'second'" in message


def test_rejects_one_kind_as_both_the_second_and_third_candidates() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange") as raised:
        ChooseByRange(TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, SECOND, CHOSEN)

    message = str(raised.value)
    assert "'second'" in message
    assert "'third'" in message


def test_rejects_one_kind_as_both_a_candidate_and_the_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange") as raised:
        ChooseByRange(TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD, THIRD)

    message = str(raised.value)
    assert "'third'" in message
    assert "'output'" in message


def test_rejects_one_kind_as_both_the_tested_amount_and_a_limit() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange") as raised:
        ChooseByRange(TESTED, TESTED, SECOND_LIMIT, FIRST, SECOND, THIRD, CHOSEN)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'first_limit'" in message


@pytest.mark.parametrize("slot", SLOTS)
def test_rejects_a_list_of_kinds_for_each_consumed_slot(slot: str) -> None:
    kinds: dict[str, Any] = {
        "amount": TESTED,
        "first_limit": FIRST_LIMIT,
        "second_limit": SECOND_LIMIT,
        "first": FIRST,
        "second": SECOND,
        "third": THIRD,
        "output": CHOSEN,
    }
    kinds[slot] = (kinds[slot],)

    with pytest.raises(InvalidCapabilityError, match=f"ChooseByRange.*'{slot}'"):
        ChooseByRange(**kinds)


@pytest.mark.parametrize("slot", (*SLOTS, "output"))
def test_rejects_a_count_kind_for_each_slot(slot: str) -> None:
    # An ArtifactKind[int] is not Money. At run time, building it fails.
    kinds: dict[str, Any] = {
        "amount": TESTED,
        "first_limit": FIRST_LIMIT,
        "second_limit": SECOND_LIMIT,
        "first": FIRST,
        "second": SECOND,
        "third": THIRD,
        "output": CHOSEN,
    }
    kinds[slot] = ArtifactKind("ex/some_count", int)

    with pytest.raises(InvalidCapabilityError, match=f"ChooseByRange.*'{slot}'"):
        ChooseByRange(**kinds)


def test_mypy_rejects_wiring_a_count_kind_for_its_tested_amount() -> None:
    count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange.*'amount'"):
        ChooseByRange(count, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD, CHOSEN)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_a_count_kind_for_its_output() -> None:
    count = ArtifactKind("ex/other_count", int)
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if it
    # is ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="ChooseByRange.*'output'"):
        ChooseByRange(TESTED, FIRST_LIMIT, SECOND_LIMIT, FIRST, SECOND, THIRD, count)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ChooseByRange, "__type_params__", ())
    assert not getattr(ChooseByRange, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_an_amount_below_the_first_limit_chooses_the_first_candidate() -> None:
    output = compute("300")

    assert output == Artifact(CHOSEN, D("10"))
    assert type(output.value) is Decimal


def test_an_amount_of_zero_chooses_the_first_candidate() -> None:
    assert compute("0") == Artifact(CHOSEN, D("10"))


def test_a_negative_amount_chooses_the_first_candidate() -> None:
    # Only the limits choose; the amount is not floored first.
    assert compute("-5") == Artifact(CHOSEN, D("10"))


def test_an_amount_equal_to_the_first_limit_chooses_the_first_candidate() -> None:
    assert compute("500.05") == Artifact(CHOSEN, D("10"))


def test_an_amount_a_cent_over_the_first_limit_chooses_the_second_candidate() -> None:
    assert compute("500.06") == Artifact(CHOSEN, D("20"))


def test_an_amount_between_the_limits_chooses_the_second_candidate() -> None:
    output = compute("1000")

    assert output == Artifact(CHOSEN, D("20"))
    assert type(output.value) is Decimal


def test_an_amount_equal_to_the_second_limit_chooses_the_second_candidate() -> None:
    assert compute("1666.82") == Artifact(CHOSEN, D("20"))


def test_an_amount_a_cent_over_the_second_limit_chooses_the_third_candidate() -> None:
    assert compute("1666.83") == Artifact(CHOSEN, D("30"))


def test_an_amount_above_the_second_limit_chooses_the_third_candidate() -> None:
    output = compute("3000")

    assert output == Artifact(CHOSEN, D("30"))
    assert type(output.value) is Decimal


def test_an_amount_equal_to_a_limit_with_more_digits_is_still_at_most_it() -> None:
    assert compute("500.050") == Artifact(CHOSEN, D("10"))
    assert compute("500.0500001") == Artifact(CHOSEN, D("20"))


def test_the_limits_come_from_the_artifacts_not_from_the_code() -> None:
    assert compute("50", first_limit="100", second_limit="200") == Artifact(CHOSEN, D("10"))
    assert compute("150", first_limit="100", second_limit="200") == Artifact(CHOSEN, D("20"))
    assert compute("250", first_limit="100", second_limit="200") == Artifact(CHOSEN, D("30"))


def test_the_amount_only_chooses_and_does_not_scale() -> None:
    assert compute("3000", first="1", second="2", third="3") == Artifact(CHOSEN, D("3"))


def test_keeps_the_chosen_candidates_scale() -> None:
    assert str(compute("300", first="1633.00").value) == "1633.00"
    assert str(compute("1000", second="4319.40").value) == "4319.40"
    assert str(compute("3000", third="0.0").value) == "0.0"


def test_keeps_fractions_of_a_cent_exactly() -> None:
    assert str(compute("300", first="0.333").value) == "0.333"
    assert str(compute("3000", third="1234567.0000000000000001").value) == (
        "1234567.0000000000000001"
    )


def test_a_negative_candidate_is_chosen_as_is_without_a_floor() -> None:
    assert compute("300", first="-250.75") == Artifact(CHOSEN, D("-250.75"))
    assert compute("1000", second="-250.75") == Artifact(CHOSEN, D("-250.75"))
    assert compute("3000", third="-250.75") == Artifact(CHOSEN, D("-250.75"))


def test_a_zero_candidate_is_chosen_as_is() -> None:
    assert str(compute("300", first="0.00").value) == "0.00"


def test_the_candidates_not_chosen_do_not_matter() -> None:
    assert compute("300", second="-99999.99", third="-99999.99") == Artifact(CHOSEN, D("10"))
    assert compute("1000", first="-99999.99", third="-99999.99") == Artifact(CHOSEN, D("20"))
    assert compute("3000", first="-99999.99", second="-99999.99") == Artifact(CHOSEN, D("30"))


def test_equal_candidates_give_that_value_for_any_amount() -> None:
    candidates = {"first": "500", "second": "500", "third": "500"}

    assert compute("300", **candidates) == Artifact(CHOSEN, D("500"))
    assert compute("1000", **candidates) == Artifact(CHOSEN, D("500"))
    assert compute("3000", **candidates) == Artifact(CHOSEN, D("500"))


def test_the_order_of_the_inputs_does_not_matter() -> None:
    result = capability().compute(tuple(reversed(inputs("1000"))))

    assert result.outputs == (Artifact(CHOSEN, D("20")),)


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("300")))

    assert result.outputs == (Artifact(CHOSEN, D("10")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_tested"):
        capability().compute(inputs("300")[1:])


def test_a_missing_first_limit_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="first_limit"):
        capability().compute(inputs("300")[:1] + inputs("300")[2:])


def test_a_missing_second_limit_for_an_amount_above_the_first_limit_is_a_missing_artifact() -> None:
    everything = inputs("1000")

    with pytest.raises(MissingArtifactError, match="second_limit"):
        capability().compute(everything[:2] + everything[3:])


def test_a_missing_first_candidate_when_it_is_chosen_is_a_missing_artifact() -> None:
    everything = inputs("300")

    with pytest.raises(MissingArtifactError, match="amount_first"):
        capability().compute(everything[:3] + everything[4:])


def test_a_missing_second_candidate_when_it_is_chosen_is_a_missing_artifact() -> None:
    everything = inputs("1000")

    with pytest.raises(MissingArtifactError, match="amount_second"):
        capability().compute(everything[:4] + everything[5:])


def test_a_missing_third_candidate_when_it_is_chosen_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="amount_third"):
        capability().compute(inputs("3000")[:5])


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_chosen_by_range_line_for_the_first_range() -> None:
    trace = capability().compute(inputs("300")).trace

    assert trace == (
        ChosenByRangeLine(
            output=CHOSEN,
            tested_kind=TESTED,
            tested_value=D("300"),
            chosen_kind=FIRST,
            chosen_value=D("10"),
        ),
    )


def test_traces_one_chosen_by_range_line_for_the_second_range() -> None:
    trace = capability().compute(inputs("1000")).trace

    assert trace == (ChosenByRangeLine(CHOSEN, TESTED, D("1000"), SECOND, D("20")),)


def test_traces_one_chosen_by_range_line_for_the_third_range() -> None:
    trace = capability().compute(inputs("3000")).trace

    assert trace == (ChosenByRangeLine(CHOSEN, TESTED, D("3000"), THIRD, D("30")),)


def test_traces_the_amount_on_a_limit_as_choosing_the_range_below_it() -> None:
    (first_line,) = capability().compute(inputs("500.05")).trace
    (second_line,) = capability().compute(inputs("1666.82")).trace

    assert first_line == ChosenByRangeLine(CHOSEN, TESTED, D("500.05"), FIRST, D("10"))
    assert second_line == ChosenByRangeLine(CHOSEN, TESTED, D("1666.82"), SECOND, D("20"))


def test_traces_the_chosen_value_and_the_tested_amount_with_their_own_scale() -> None:
    (line,) = capability().compute(inputs("1000.50", second="4319.40")).trace

    assert isinstance(line, ChosenByRangeLine)
    assert str(line.chosen_value) == "4319.40"
    assert str(line.tested_value) == "1000.50"


def test_trace_amount_is_the_chosen_value() -> None:
    trace = capability().compute(inputs("300")).trace

    assert [line.amount for line in trace] == [D("10")]


def test_trace_chosen_value_is_the_output() -> None:
    result = capability().compute(inputs("1000", second="4319.40"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ChosenByRangeLine)
    assert line.chosen_value == output.value
    assert str(line.chosen_value) == str(output.value)


def test_traces_no_chosen_by_count_line() -> None:
    (line,) = capability().compute(inputs("300")).trace

    assert not isinstance(line, ChosenByCountLine)


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("300")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
