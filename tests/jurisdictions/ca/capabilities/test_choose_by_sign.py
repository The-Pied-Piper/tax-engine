"""Unit tests for the ChooseBySign capability (`ca/choose_by_sign`), with made-up kinds.

It is `core/choose_by_count` for the sign of an amount. Its slots: a consumed `sign` (a `Decimal`
kind, only its sign is read), five optional consumed list slots, each a tuple of at most one
`Decimal` kind (an empty tuple, the default, leaves the branch uncovered): `when_positive`,
`when_zero`, `when_negative`, `when_non_positive` (sign at most 0) and `when_non_negative` (sign
at least 0), and one produced slot `output`. No parameter slots and no dataset; every wiring
parameter is a keyword.

Each sign branch (positive, zero, negative) may be covered at most once: positive with
non-positive, non-negative with negative, or positive, zero and negative are fine; positive with
non-negative (or any other overlap) raises `InvalidCapabilityError` when the capability is built.

The output is the candidate of the branch the sign falls in, unchanged with its scale kept; only
the chosen candidate is read. An uncovered branch gives a plain `Decimal(0)`. It records one
`ChosenBySignLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.trace import ChosenBySignLine
from tax_calculator.jurisdictions.ca.capabilities.choose_by_sign import ChooseBySign

D = Decimal
Kinds = tuple[ArtifactKind[Decimal], ...]

SIGN = ArtifactKind("ex/net_change", Decimal)
GAIN = ArtifactKind("ex/gain_amount", Decimal)
EVEN = ArtifactKind("ex/even_amount", Decimal)
LOSS = ArtifactKind("ex/loss_amount", Decimal)
NOT_UP = ArtifactKind("ex/not_up_amount", Decimal)
NOT_DOWN = ArtifactKind("ex/not_down_amount", Decimal)
OUTPUT = ArtifactKind("ex/chosen_amount", Decimal)

KINDS = {"gain": GAIN, "even": EVEN, "loss": LOSS, "not_up": NOT_UP, "not_down": NOT_DOWN}


def build(
    *,
    positive: Kinds = (),
    zero: Kinds = (),
    negative: Kinds = (),
    non_positive: Kinds = (),
    non_negative: Kinds = (),
) -> ChooseBySign:
    return ChooseBySign(
        sign=SIGN,
        when_positive=positive,
        when_zero=zero,
        when_negative=negative,
        when_non_positive=non_positive,
        when_non_negative=non_negative,
        output=OUTPUT,
    )


def three_way() -> ChooseBySign:
    return build(positive=(GAIN,), zero=(EVEN,), negative=(LOSS,))


def inputs(sign: str, **candidates: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(SIGN, D(sign)), *(Artifact(KINDS[k], D(v)) for k, v in candidates.items()))


FULL = {"gain": "100.50", "even": "7.00", "loss": "-3.25"}


def compute(wired: ChooseBySign, sign: str, **candidates: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(sign, **candidates)).outputs
    return output


def test_is_registered_as_ca_choose_by_sign() -> None:
    assert CapabilityRegistry.shared().get("ca/choose_by_sign") is ChooseBySign


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "choose_by_sign" in ca_capabilities.__all__
    assert ca_capabilities.choose_by_sign.ChooseBySign is ChooseBySign


def test_declares_its_contract() -> None:
    assert three_way().consumes == frozenset({SIGN, GAIN, EVEN, LOSS})
    assert three_way().produces == frozenset({OUTPUT})


def test_the_contract_lists_only_the_wired_candidates() -> None:
    assert build(positive=(GAIN,)).consumes == frozenset({SIGN, GAIN})
    assert build().consumes == frozenset({SIGN})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ChooseBySign)
    assert "produces" not in vars(ChooseBySign)


def test_declares_its_slots() -> None:
    assert ChooseBySign.PARAMETERS == {}
    assert ChooseBySign.CONSUMES == {
        "sign": Decimal,
        "when_positive": list[Decimal],
        "when_zero": list[Decimal],
        "when_negative": list[Decimal],
        "when_non_positive": list[Decimal],
        "when_non_negative": list[Decimal],
    }
    assert ChooseBySign.PRODUCES == {"output": Decimal}
    assert not ChooseBySign.is_list_slot("sign")
    for slot in list(ChooseBySign.CONSUMES)[1:]:
        assert ChooseBySign.is_list_slot(slot)


def test_its_slots_are_read_only() -> None:
    for slots in (ChooseBySign.PARAMETERS, ChooseBySign.CONSUMES, ChooseBySign.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ChooseBySign.CONSUMES, Mapping[str, type])
    assert_type(ChooseBySign.PRODUCES, Mapping[str, type])


def test_every_candidate_slot_is_optional_when_built_by_keyword() -> None:
    wired = ChooseBySign(sign=SIGN, when_positive=(GAIN,), output=OUTPUT)

    assert wired.consumes == frozenset({SIGN, GAIN})


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        ChooseBySign(sign=SIGN, output=OUTPUT, rounding=object())  # type: ignore[call-arg]


# --- wiring: coverage ---------------------------------------------------------------------------


def test_positive_with_non_positive_is_accepted() -> None:
    build(positive=(GAIN,), non_positive=(NOT_UP,))


def test_non_negative_with_negative_is_accepted() -> None:
    build(non_negative=(NOT_DOWN,), negative=(LOSS,))


def test_positive_zero_and_negative_are_accepted() -> None:
    build(positive=(GAIN,), zero=(EVEN,), negative=(LOSS,))


def test_a_single_branch_is_accepted() -> None:
    for slot in ("positive", "zero", "negative", "non_positive", "non_negative"):
        build(**{slot: (GAIN,)})


@pytest.mark.parametrize(
    "overlap",
    [
        {"positive": (GAIN,), "non_negative": (NOT_DOWN,)},
        {"zero": (EVEN,), "non_negative": (NOT_DOWN,)},
        {"zero": (EVEN,), "non_positive": (NOT_UP,)},
        {"negative": (LOSS,), "non_positive": (NOT_UP,)},
        {"non_positive": (NOT_UP,), "non_negative": (NOT_DOWN,)},
        {"positive": (GAIN,), "zero": (EVEN,), "non_negative": (NOT_DOWN,)},
    ],
)
def test_a_wiring_covering_a_sign_branch_twice_is_rejected(overlap: dict[str, Kinds]) -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseBySign"):
        build(**overlap)


def test_rejects_the_sign_kind_as_a_candidate() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseBySign") as raised:
        build(positive=(SIGN,))

    assert "'sign'" in str(raised.value)
    assert "'when_positive'" in str(raised.value)


def test_rejects_one_kind_in_two_candidate_slots() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseBySign"):
        build(positive=(GAIN,), non_positive=(GAIN,))


def test_rejects_the_output_kind_as_a_candidate() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseBySign") as raised:
        build(positive=(OUTPUT,))

    assert "'output'" in str(raised.value)


def test_rejects_more_than_one_kind_for_a_branch() -> None:
    other = ArtifactKind("ex/other_gain", Decimal)

    with pytest.raises(InvalidCapabilityError, match="ChooseBySign.*'when_positive'"):
        build(positive=(GAIN, other))


def test_rejects_a_kind_of_another_value_type_as_a_candidate() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="ChooseBySign.*'when_zero'"):
        build(zero=(count,))  # type: ignore[arg-type]


def test_rejects_a_single_kind_where_a_tuple_is_wanted() -> None:
    with pytest.raises(InvalidCapabilityError, match="ChooseBySign.*'when_positive'"):
        ChooseBySign(sign=SIGN, when_positive=GAIN, output=OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_kind_of_another_value_type_as_the_sign() -> None:
    count = ArtifactKind("ex/count", int)

    with pytest.raises(InvalidCapabilityError, match="ChooseBySign.*'sign'"):
        ChooseBySign(sign=count, output=OUTPUT)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ChooseBySign, "__type_params__", ())
    assert not getattr(ChooseBySign, "__parameters__", ())


# --- computing: the three branches --------------------------------------------------------------


def test_a_positive_sign_chooses_the_positive_candidate() -> None:
    output = compute(three_way(), "0.01", **FULL)

    assert output == Artifact(OUTPUT, D("100.50"))
    assert type(output.value) is Decimal


def test_a_zero_sign_chooses_the_zero_candidate() -> None:
    assert compute(three_way(), "0", **FULL) == Artifact(OUTPUT, D("7.00"))


def test_a_negative_zero_sign_and_a_scaled_zero_sign_choose_the_zero_candidate() -> None:
    assert compute(three_way(), "-0", **FULL) == Artifact(OUTPUT, D("7.00"))
    assert compute(three_way(), "0.000", **FULL) == Artifact(OUTPUT, D("7.00"))


def test_a_negative_sign_chooses_the_negative_candidate() -> None:
    assert compute(three_way(), "-0.01", **FULL) == Artifact(OUTPUT, D("-3.25"))


def test_only_the_sign_decides_not_its_size() -> None:
    assert compute(three_way(), "1000000", **FULL) == compute(three_way(), "0.0001", **FULL)


def test_the_chosen_candidate_keeps_its_scale() -> None:
    assert str(compute(three_way(), "1", **FULL).value) == "100.50"
    assert str(compute(three_way(), "0", **FULL).value) == "7.00"
    assert str(compute(three_way(), "-1", **FULL).value) == "-3.25"


def test_the_chosen_candidate_is_not_rounded() -> None:
    assert compute(three_way(), "1", gain="0.123456789", even="0", loss="0") == Artifact(
        OUTPUT, D("0.123456789")
    )


def test_only_the_chosen_candidate_is_read() -> None:
    assert compute(three_way(), "1", gain="4") == Artifact(OUTPUT, D("4"))
    assert compute(three_way(), "0", even="5") == Artifact(OUTPUT, D("5"))
    assert compute(three_way(), "-1", loss="-6") == Artifact(OUTPUT, D("-6"))


def test_a_missing_chosen_candidate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="gain_amount"):
        three_way().compute(inputs("1", even="5", loss="-6"))


def test_a_missing_sign_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="net_change"):
        three_way().compute((Artifact(GAIN, D("1")),))


# --- computing: the two-way branches ------------------------------------------------------------


def test_positive_and_non_positive() -> None:
    wired = build(positive=(GAIN,), non_positive=(NOT_UP,))
    values = {"gain": "10.0", "not_up": "2.50"}

    assert compute(wired, "1", **values) == Artifact(OUTPUT, D("10.0"))
    assert compute(wired, "0", **values) == Artifact(OUTPUT, D("2.50"))
    assert compute(wired, "-1", **values) == Artifact(OUTPUT, D("2.50"))


def test_non_negative_and_negative() -> None:
    wired = build(non_negative=(NOT_DOWN,), negative=(LOSS,))
    values = {"not_down": "4.0", "loss": "-8"}

    assert compute(wired, "1", **values) == Artifact(OUTPUT, D("4.0"))
    assert compute(wired, "0", **values) == Artifact(OUTPUT, D("4.0"))
    assert compute(wired, "-1", **values) == Artifact(OUTPUT, D("-8"))


def test_non_positive_alone_gives_zero_for_a_positive_sign() -> None:
    wired = build(non_positive=(NOT_UP,))

    assert compute(wired, "1", not_up="9") == Artifact(OUTPUT, D("0"))
    assert compute(wired, "0", not_up="9") == Artifact(OUTPUT, D("9"))
    assert compute(wired, "-1", not_up="9") == Artifact(OUTPUT, D("9"))


def test_non_negative_alone_gives_zero_for_a_negative_sign() -> None:
    wired = build(non_negative=(NOT_DOWN,))

    assert compute(wired, "1", not_down="9") == Artifact(OUTPUT, D("9"))
    assert compute(wired, "0", not_down="9") == Artifact(OUTPUT, D("9"))
    assert compute(wired, "-1", not_down="9") == Artifact(OUTPUT, D("0"))


# --- computing: uncovered branches --------------------------------------------------------------


@pytest.mark.parametrize(
    ("covered", "sign"),
    [("zero", "5"), ("negative", "5"), ("positive", "0"), ("negative", "0"), ("positive", "-5")],
)
def test_an_uncovered_branch_gives_a_plain_zero(covered: str, sign: str) -> None:
    kinds = {"positive": GAIN, "zero": EVEN, "negative": LOSS}
    wired = build(**{covered: (kinds[covered],)})

    output = compute(wired, sign)

    assert output == Artifact(OUTPUT, D("0"))
    assert str(output.value) == "0"
    assert type(output.value) is Decimal


def test_every_branch_uncovered_always_gives_zero() -> None:
    for sign in ("5", "0", "-5"):
        assert compute(build(), sign) == Artifact(OUTPUT, D("0"))


def test_a_plain_gated_amount_is_one_candidate() -> None:
    gated = build(positive=(GAIN,))

    assert compute(gated, "9", gain="12.30") == Artifact(OUTPUT, D("12.30"))
    assert compute(gated, "0") == Artifact(OUTPUT, D("0"))
    assert compute(gated, "-9") == Artifact(OUTPUT, D("0"))


# --- computing: inputs --------------------------------------------------------------------------


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("9"))

    result = three_way().compute((other, *inputs("1", **FULL)))

    assert result.outputs == (Artifact(OUTPUT, D("100.50")),)


def test_has_one_output() -> None:
    assert len(three_way().compute(inputs("1", **FULL)).outputs) == 1


def test_compute_is_repeatable() -> None:
    wired = three_way()

    assert wired.compute(inputs("1", **FULL)) == wired.compute(inputs("1", **FULL))


# --- trace --------------------------------------------------------------------------------------


def test_traces_one_chosen_by_sign_line_naming_the_chosen_candidate() -> None:
    trace = three_way().compute(inputs("-2.5", **FULL)).trace

    assert trace == (
        ChosenBySignLine(
            output=OUTPUT,
            sign_kind=SIGN,
            sign=D("-2.5"),
            chosen_kind=LOSS,
            chosen_value=D("-3.25"),
        ),
    )


def test_traces_the_positive_and_zero_candidates() -> None:
    wired = three_way()

    assert wired.compute(inputs("3", **FULL)).trace == (
        ChosenBySignLine(OUTPUT, SIGN, D("3"), GAIN, D("100.50")),
    )
    assert wired.compute(inputs("0", **FULL)).trace == (
        ChosenBySignLine(OUTPUT, SIGN, D("0"), EVEN, D("7.00")),
    )


def test_traces_a_two_way_candidate_chosen_for_a_zero_sign() -> None:
    wired = build(positive=(GAIN,), non_positive=(NOT_UP,))

    assert wired.compute(inputs("0", gain="1", not_up="2")).trace == (
        ChosenBySignLine(OUTPUT, SIGN, D("0"), NOT_UP, D("2")),
    )


def test_traces_no_chosen_kind_for_an_uncovered_branch() -> None:
    trace = build(positive=(GAIN,)).compute(inputs("0", gain="1")).trace

    assert trace == (ChosenBySignLine(OUTPUT, SIGN, D("0"), None, D("0")),)


def test_trace_amount_is_the_chosen_value() -> None:
    trace = three_way().compute(inputs("-1", **FULL)).trace

    assert [line.amount for line in trace] == [D("-3.25")]


def test_trace_holds_no_text() -> None:
    for line in three_way().compute(inputs("1", **FULL)).trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))
