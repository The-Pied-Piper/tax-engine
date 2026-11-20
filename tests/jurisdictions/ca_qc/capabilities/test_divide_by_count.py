"""Unit tests for the DivideByCount capability (`ca-qc/divide_by_count`), with made-up kinds.

Its slots: one parameter slot `rounding` (a rounding-only dataset), two consumed slots `amount` (a
money artifact) and `count` (a count artifact) and one produced slot `output`. The output is the
exact quotient of the amount by the count, rounded once by the dataset's rule (with no rounding an
inexact quotient raises); a count of 0 gives 0 and the trace line still records the rule. It
records one `DivideByCountLine`. The tests use the printed 906 of the solidarity tax credit's
basic housing amount for multiple owners or tenants.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal, Inexact
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca_qc.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca_qc.capabilities.divide_by_count import DivideByCount
from tax_engine.jurisdictions.ca_qc.trace import DivideByCountLine
from tests.jurisdictions.ca_qc.support import quebec_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

HOUSING = AmountKind("ex/housing_multiple_amount", non_negative=True)
OCCUPANTS = CountKind("ex/occupants", non_negative=True)
SHARE = AmountKind("ex/housing_share", non_negative=True)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    return ParameterDataset(
        "ex/cent_rounding", 2025, ROUNDING_ONLY, RoundingOnly(), rule, ("https://example.org/s",)
    )


def capability(rule: RoundingRule = CENT) -> DivideByCount:
    return DivideByCount(rounding(rule), HOUSING, OCCUPANTS, SHARE)


def inputs(amount: str, count: int) -> tuple[Artifact[Any], ...]:
    return (Artifact(HOUSING, D(amount)), Artifact(OCCUPANTS, count))


def compute(wired: DivideByCount, amount: str, count: int) -> Artifact[Any]:
    (output,) = wired.compute(inputs(amount, count)).outputs
    return output


def test_is_registered_as_ca_qc_divide_by_count() -> None:
    assert quebec_capabilities().get("ca-qc/divide_by_count") is DivideByCount


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({HOUSING, OCCUPANTS})
    assert capability().produces == frozenset({SHARE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(DivideByCount)
    assert "produces" not in vars(DivideByCount)


def test_declares_its_slots() -> None:
    assert DivideByCount.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert DivideByCount.CONSUMES == {"amount": Decimal, "count": int}
    assert DivideByCount.PRODUCES == {"output": Decimal}
    assert DivideByCount.BLANK_ALLOWED == frozenset({"amount", "count"})
    assert not DivideByCount.is_list_slot("amount")
    assert not DivideByCount.is_list_slot("count")


def test_its_slots_are_read_only() -> None:
    for slots in (DivideByCount.PARAMETERS, DivideByCount.CONSUMES, DivideByCount.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(DivideByCount.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(DivideByCount.CONSUMES, Mapping[str, type])
    assert_type(DivideByCount.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (DivideByCount.PARAMETERS, DivideByCount.CONSUMES, DivideByCount.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = DivideByCount(rounding=rounding(), amount=HOUSING, count=OCCUPANTS, output=SHARE)

    assert compute(wired, "906", 3) == Artifact(SHARE, D("302.00"))


def test_rejects_one_kind_as_both_amount_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="DivideByCount") as raised:
        DivideByCount(rounding(), HOUSING, OCCUPANTS, HOUSING)

    message = str(raised.value)
    assert "'amount'" in message
    assert "'output'" in message


def test_mypy_rejects_wiring_a_count_as_the_amount() -> None:
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="DivideByCount.*'amount'"):
        DivideByCount(rounding(), OCCUPANTS, OCCUPANTS, SHARE)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RoundingOnly]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        DivideByCount(rate, HOUSING, OCCUPANTS, SHARE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(DivideByCount, "__type_params__", ())
    assert not getattr(DivideByCount, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "count", "share"),
    [
        pytest.param("906", 1, "906.00", id="one"),
        pytest.param("906", 2, "453.00", id="two"),
        pytest.param("906", 3, "302.00", id="three"),
        pytest.param("906", 4, "226.50", id="four-is-exact-at-the-half-cent-place"),
        pytest.param("906", 7, "129.43", id="seven-rounds-129.428571-half-up"),
        pytest.param("906", 8, "113.25", id="eight"),
        pytest.param("0", 3, "0.00", id="a-zero-amount"),
    ],
)
def test_is_the_exact_quotient_rounded_once(amount: str, count: int, share: str) -> None:
    output = compute(capability(), amount, count)

    assert output == Artifact(SHARE, D(share))
    assert type(output.value) is Decimal


def test_a_count_of_zero_gives_zero_not_an_error() -> None:
    output = compute(capability(), "906", 0)

    assert output == Artifact(SHARE, D("0"))
    assert type(output.value) is Decimal


def test_rounds_half_up_at_the_rule_not_before() -> None:
    # 1 / 8 is exactly 0.125: half-up to the cent is 0.13, and rounding twice (0.12 then) would not.
    assert compute(capability(), "1", 8).value == D("0.13")


def test_with_no_rounding_an_exact_quotient_is_kept_and_an_inexact_one_raises() -> None:
    assert compute(capability(NO_ROUNDING), "906", 4).value == D("226.5")
    with pytest.raises(Inexact):
        compute(capability(NO_ROUNDING), "906", 7)


def test_with_no_rounding_a_count_of_zero_is_still_zero() -> None:
    assert compute(capability(NO_ROUNDING), "906", 0).value == D("0")


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9000")), *inputs("906", 3)))

    assert result.outputs == (Artifact(SHARE, D("302.00")),)


def test_a_missing_amount_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="housing_multiple_amount"):
        capability().compute((Artifact(OCCUPANTS, 3),))


def test_a_missing_count_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="occupants"):
        capability().compute((Artifact(HOUSING, D("906")),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_with_the_rule_and_the_result() -> None:
    assert capability().compute(inputs("906", 7)).trace == (
        DivideByCountLine(
            output=SHARE,
            amount_kind=HOUSING,
            amount_value=D("906"),
            count_kind=OCCUPANTS,
            count=7,
            rounding=CENT,
            result=D("129.43"),
        ),
    )


def test_a_count_of_zero_still_records_the_rounding_rule() -> None:
    (line,) = capability().compute(inputs("906", 0)).trace

    assert isinstance(line, DivideByCountLine)
    assert line.rounding == CENT
    assert line.result == D("0")


def test_the_line_fields_are_in_this_order() -> None:
    assert [field.name for field in fields(DivideByCountLine)] == [
        "output",
        "amount_kind",
        "amount_value",
        "count_kind",
        "count",
        "rounding",
        "result",
    ]


def test_trace_amount_is_the_result_and_its_label_is_the_outputs() -> None:
    (line,) = capability().compute(inputs("906", 3)).trace

    assert isinstance(line, DivideByCountLine)
    assert line.amount == D("302.00")
    assert line.label == SHARE.label


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("906", 7))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, DivideByCountLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    for line in capability().compute(inputs("906", 7)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- English trace ----------------------------------------------------------------------------


def test_the_english_sentence_for_a_count_of_three() -> None:
    assert EnglishTraceRenderer().render_all(capability().compute(inputs("906", 3)).trace) == (
        "Housing multiple amount (906.00) shared among occupants (3) gives 302.00 "
        "(rounded to the nearest cent).",
    )


def test_the_english_sentence_for_a_count_of_zero_says_so() -> None:
    (sentence,) = EnglishTraceRenderer().render_all(capability().compute(inputs("906", 0)).trace)

    assert ", which is zero, gives " in sentence
