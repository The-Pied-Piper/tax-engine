"""Unit tests for the SurtaxFactor capability (`ca-on/surtax_factor`), with made-up kinds.

Its slots: two parameter slots `line_66` and `line_67` (each a `surcharge_tiers` dataset), one
consumed slot `base` and one produced slot `output`. The output is the plain factor
1 plus the rate of each tier, of either dataset, whose threshold the base is strictly over: a base
exactly at a threshold is not over it (that tier's charge is 0), so the factor stays lower. The
factor is exact: no rounding rule is applied to it. It records one `SurtaxFactorLine`, holding the
tiers the base is over, in the order of the slots and of each dataset. The tests use the printed
figures of ON428 lines 66 and 67 (thresholds 5,710 and 7,307, rates 20% and 36%) for the datasets.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca_on.trace_english  # noqa: F401  (registers the renderers)
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
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)
from tax_engine.jurisdictions.ca_on.capabilities.surtax_factor import SurtaxFactor
from tax_engine.jurisdictions.ca_on.trace import SurtaxFactorLine
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

TAX_AFTER_CREDITS = AmountKind("ex/tax_after_credits", non_negative=True)
FACTOR = AmountKind("ex/factor", non_negative=True)

# ON428 line 66: 20% of line 65 over 5,710. Line 67: 36% of line 65 over 7,307.
TIER_66 = SurchargeTier(D("5710"), Rate(D("0.20")))
TIER_67 = SurchargeTier(D("7307"), Rate(D("0.36")))


def tiers(
    *given: SurchargeTier, family: str = "ex/line_66", rounding: RoundingRule = CENT
) -> ParameterDataset[SurchargeTiers]:
    return ParameterDataset(
        family,
        2025,
        SURCHARGE_TIERS,
        SurchargeTiers(given),
        rounding,
        ("https://example.org/s",),
    )


def capability(
    line_66: ParameterDataset[SurchargeTiers] | None = None,
    line_67: ParameterDataset[SurchargeTiers] | None = None,
) -> SurtaxFactor:
    """By default the printed tiers of lines 66 and 67 on the made-up tax after credits."""
    return SurtaxFactor(
        line_66 or tiers(TIER_66),
        line_67 or tiers(TIER_67, family="ex/line_67"),
        TAX_AFTER_CREDITS,
        FACTOR,
    )


def compute(wired: SurtaxFactor, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(TAX_AFTER_CREDITS, D(base)),)).outputs
    return output


def trace_of(wired: SurtaxFactor, base: str) -> tuple[Any, ...]:
    return wired.compute((Artifact(TAX_AFTER_CREDITS, D(base)),)).trace


def test_is_registered_as_ca_on_surtax_factor() -> None:
    assert bundled_capabilities().get("ca-on/surtax_factor") is SurtaxFactor


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TAX_AFTER_CREDITS})
    assert capability().produces == frozenset({FACTOR})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(SurtaxFactor)
    assert "produces" not in vars(SurtaxFactor)


def test_declares_its_slots() -> None:
    assert SurtaxFactor.PARAMETERS == {"line_66": SURCHARGE_TIERS, "line_67": SURCHARGE_TIERS}
    assert SurtaxFactor.PARAMETERS["line_66"] is SURCHARGE_TIERS
    assert SurtaxFactor.PARAMETERS["line_67"] is SURCHARGE_TIERS
    assert SurtaxFactor.CONSUMES == {"base": Decimal}
    assert SurtaxFactor.PRODUCES == {"output": Decimal}
    assert not SurtaxFactor.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (SurtaxFactor.PARAMETERS, SurtaxFactor.CONSUMES, SurtaxFactor.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(SurtaxFactor.PARAMETERS, Mapping[str, ParameterKind[SurchargeTiers]])
    assert_type(SurtaxFactor.CONSUMES, Mapping[str, type])
    assert_type(SurtaxFactor.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (SurtaxFactor.PARAMETERS, SurtaxFactor.CONSUMES, SurtaxFactor.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = SurtaxFactor(
        line_66=tiers(TIER_66),
        line_67=tiers(TIER_67, family="ex/line_67"),
        base=TAX_AFTER_CREDITS,
        output=FACTOR,
    )

    assert compute(wired, "8000") == Artifact(FACTOR, D("1.56"))


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="SurtaxFactor") as raised:
        SurtaxFactor(tiers(TIER_66), tiers(TIER_67), TAX_AFTER_CREDITS, TAX_AFTER_CREDITS)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="SurtaxFactor.*'base'"):
        SurtaxFactor(tiers(TIER_66), tiers(TIER_67), count, FACTOR)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[SurchargeTiers]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        SurtaxFactor(rate, tiers(TIER_67), TAX_AFTER_CREDITS, FACTOR)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(SurtaxFactor, "__type_params__", ())
    assert not getattr(SurtaxFactor, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "factor"),
    [
        pytest.param("0", "1", id="zero"),
        pytest.param("3311.45", "1", id="at-70000-below-both-thresholds"),
        pytest.param("5709.99", "1", id="a-cent-under-the-first-threshold"),
        pytest.param("5710", "1", id="at-the-first-threshold"),
        pytest.param("5710.01", "1.20", id="a-cent-over-the-first-threshold"),
        pytest.param("6015.78", "1.20", id="at-100000-between-the-thresholds"),
        pytest.param("7306.99", "1.20", id="a-cent-under-the-second-threshold"),
        pytest.param("7307", "1.20", id="at-the-second-threshold"),
        pytest.param("7307.01", "1.56", id="a-cent-over-the-second-threshold"),
        pytest.param("11458.12", "1.56", id="at-150000-above-both-thresholds"),
        pytest.param("1000000", "1.56", id="far-above"),
    ],
)
def test_is_1_plus_the_rate_of_each_tier_the_base_is_strictly_over(base: str, factor: str) -> None:
    output = compute(capability(), base)

    assert output == Artifact(FACTOR, D(factor))
    assert type(output.value) is Decimal


def test_a_base_exactly_at_a_threshold_is_not_over_it() -> None:
    # The tier's charge at its threshold is 0, so the factor is the one below.
    assert compute(capability(), "5710").value == D("1")
    assert compute(capability(), "7307").value == D("1.20")


def test_is_exact_and_ignores_the_datasets_rounding() -> None:
    # 1 plus 12.5% is 1.125; the datasets round to the cent, the factor is not a charge.
    wired = capability(tiers(SurchargeTier(D("100"), Rate(D("0.125")))))

    assert compute(wired, "200").value == D("1.125")


def test_adds_every_tier_of_a_dataset() -> None:
    wired = capability(
        tiers(TIER_66, SurchargeTier(D("6000"), Rate(D("0.05")))), tiers(TIER_67, family="ex/b")
    )

    assert compute(wired, "5800").value == D("1.20")
    assert compute(wired, "6500").value == D("1.25")
    assert compute(wired, "7500").value == D("1.61")


def test_takes_the_thresholds_and_rates_from_the_datasets() -> None:
    wired = capability(
        tiers(SurchargeTier(D("1000"), Rate(D("0.10")))),
        tiers(SurchargeTier(D("2000"), Rate(D("0.50"))), family="ex/b"),
    )

    assert compute(wired, "1000").value == D("1")
    assert compute(wired, "1500").value == D("1.10")
    assert compute(wired, "2500").value == D("1.60")


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute(
        (Artifact(other, D("9000")), Artifact(TAX_AFTER_CREDITS, D("6000")))
    )

    assert result.outputs == (Artifact(FACTOR, D("1.20")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="tax_after_credits"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_line_holding_no_tier_below_the_first_threshold() -> None:
    assert trace_of(capability(), "3311.45") == (
        SurtaxFactorLine(
            output=FACTOR,
            base=TAX_AFTER_CREDITS,
            base_amount=D("3311.45"),
            tiers=(),
            factor=D("1"),
        ),
    )


def test_traces_the_one_tier_the_base_is_over() -> None:
    assert trace_of(capability(), "6015.78") == (
        SurtaxFactorLine(FACTOR, TAX_AFTER_CREDITS, D("6015.78"), (TIER_66,), D("1.20")),
    )


def test_traces_both_tiers_in_the_order_of_the_slots() -> None:
    assert trace_of(capability(), "11458.12") == (
        SurtaxFactorLine(FACTOR, TAX_AFTER_CREDITS, D("11458.12"), (TIER_66, TIER_67), D("1.56")),
    )


def test_traces_no_tier_for_a_base_at_a_threshold() -> None:
    (line,) = trace_of(capability(), "5710")

    assert line.tiers == ()
    assert line.factor == D("1")


def test_the_line_fields_are_in_this_order() -> None:
    assert [field.name for field in fields(SurtaxFactorLine)] == [
        "output",
        "base",
        "base_amount",
        "tiers",
        "factor",
    ]


def test_trace_amount_is_the_factor_and_its_label_is_the_outputs() -> None:
    (line,) = trace_of(capability(), "8000")

    assert isinstance(line, SurtaxFactorLine)
    assert line.amount == D("1.56")
    assert line.label == FACTOR.label


def test_trace_factor_is_the_output() -> None:
    result = capability().compute((Artifact(TAX_AFTER_CREDITS, D("6000")),))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, SurtaxFactorLine)
    assert line.factor == output.value


def test_trace_holds_no_text() -> None:
    for line in trace_of(capability(), "8000"):
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- English trace ----------------------------------------------------------------------------
#
# Every sentence ends "gives <factor>", the factor and the base shown in cents like every figure
# of the form, the thresholds as the form prints them and the rates as percentages.


def test_the_english_sentence_for_a_base_under_every_threshold() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(capability(), "3311.45")) == (
        "Tax after credits (3311.45) is over no surtax threshold, "
        "so no rate is added to 1.00, gives 1.00.",
    )


def test_the_english_sentence_for_a_base_at_a_threshold_is_not_over_it() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(capability(), "5710")) == (
        "Tax after credits (5710.00) is over no surtax threshold, "
        "so no rate is added to 1.00, gives 1.00.",
    )


def test_the_english_sentence_for_a_base_over_the_first_threshold() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(capability(), "6015.78")) == (
        "Tax after credits (6015.78) is over the surtax threshold of 5710.00, "
        "so its rate 20% is added to 1.00, gives 1.20.",
    )


def test_the_english_sentence_for_a_base_over_both_thresholds() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(capability(), "11458.12")) == (
        "Tax after credits (11458.12) is over the surtax thresholds of 5710.00 and 7307.00, "
        "so their rates 20% and 36% are added to 1.00, gives 1.56.",
    )
