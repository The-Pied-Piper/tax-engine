"""Unit tests for the AmountByBandRate capability (`core/amount_by_band_rate`), made-up figures.

Its slots: one parameter slot `table` (an `amount_by_band` dataset), one consumed slot `base` and
one produced slot `output`. The output is the `rate` of the chart's band the base falls in, or 0
for a flat band (which has no rate). It is a rate, never rounded: the dataset's rounding rule, which
rounds amounts, does not apply. The band is chosen as `AmountByBand.band_for` chooses it: a base at
a boundary falls in the lower band. It records one `AmountByBandRateLine` for the band it used.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.amount_by_band import (
    AMOUNT_BY_BAND,
    AmountBand,
    AmountByBand,
)
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.trace import AmountByBandRateLine, TraceLine
from tax_engine.domain.trace import rate_tables as trace_rate_tables
from tax_engine.jurisdictions.core.capabilities.amount_by_band_rate import AmountByBandRate
from tests.capabilities import bundled_capabilities

D = Decimal
WHOLE = RoundTo(D("1"), RoundingMode.HALF_UP)

INCOME = AmountKind("ex/income")
SLOPE = AmountKind("ex/slope")

TEN_PERCENT = Rate(D("0.10"))
QUARTER = Rate(D("0.25"))
ODD = Rate(D("0.123456"))

# A flat 0 from 0; 10% of the income over 100 from 100; a flat 12 from 200; 15 plus 25% of the
# income over 300 from 300 (open at the top). The boundaries 100, 200 and 300 each fall in the
# lower band.
BANDS = (
    AmountBand(D(0), amount=D(0)),
    AmountBand(D(100), minus=D(100), rate=TEN_PERCENT, plus=D(0)),
    AmountBand(D(200), amount=D(12)),
    AmountBand(D(300), minus=D(300), rate=QUARTER, plus=D(15)),
)


def table(
    bands: tuple[AmountBand, ...] = BANDS, *, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[AmountByBand]:
    return ParameterDataset(
        "ex/amount_by_band",
        2025,
        AMOUNT_BY_BAND,
        AmountByBand(bands),
        rounding,
        ("https://example.org/b",),
    )


def capability(data: ParameterDataset[AmountByBand] | None = None) -> AmountByBandRate:
    """By default the made-up bands above."""
    return AmountByBandRate(data or table(), INCOME, SLOPE)


def compute(wired: AmountByBandRate, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(INCOME, D(base)),)).outputs
    return output


def trace_of(wired: AmountByBandRate, base: str) -> tuple[Any, ...]:
    return wired.compute((Artifact(INCOME, D(base)),)).trace


def test_is_registered_as_core_amount_by_band_rate() -> None:
    assert bundled_capabilities().get("core/amount_by_band_rate") is AmountByBandRate
    assert AmountByBandRate.IDENTIFIER == "core/amount_by_band_rate"


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({INCOME})
    assert capability().produces == frozenset({SLOPE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(AmountByBandRate)
    assert "produces" not in vars(AmountByBandRate)


def test_declares_its_slots() -> None:
    assert AmountByBandRate.PARAMETERS == {"table": AMOUNT_BY_BAND}
    assert AmountByBandRate.PARAMETERS["table"] is AMOUNT_BY_BAND
    assert AmountByBandRate.CONSUMES == {"base": Decimal}
    assert AmountByBandRate.PRODUCES == {"output": Decimal}
    assert not AmountByBandRate.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    slots_of = (AmountByBandRate.PARAMETERS, AmountByBandRate.CONSUMES, AmountByBandRate.PRODUCES)
    for slots in slots_of:
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(AmountByBandRate.PARAMETERS, Mapping[str, ParameterKind[AmountByBand]])
    assert_type(AmountByBandRate.CONSUMES, Mapping[str, type])
    assert_type(AmountByBandRate.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    slots_of = (AmountByBandRate.PARAMETERS, AmountByBandRate.CONSUMES, AmountByBandRate.PRODUCES)
    for slots in slots_of:
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = AmountByBandRate(table=table(), base=INCOME, output=SLOPE)

    assert compute(wired, "150") == Artifact(SLOPE, D("0.10"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        AmountByBandRate(table(), INCOME, SLOPE, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountByBandRate") as raised:
        AmountByBandRate(table(), INCOME, INCOME)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountByBandRate.*'base'"):
        AmountByBandRate(table(), (INCOME,), SLOPE)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="AmountByBandRate.*'base'"):
        AmountByBandRate(table(), count, SLOPE)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[AmountByBand]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        AmountByBandRate(rate, INCOME, SLOPE)  # type: ignore[arg-type]

    assert callable(wire)


def test_mypy_rejects_bare_bands_without_their_dataset() -> None:
    def wire() -> None:  # type-checked, never run
        # Parameter slots take the dataset, which carries the rounding rule; never bare values.
        AmountByBandRate(AmountByBand(BANDS), INCOME, SLOPE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(AmountByBandRate, "__type_params__", ())
    assert not getattr(AmountByBandRate, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "slope"),
    [
        pytest.param("0", "0", id="zero-base"),
        pytest.param("0.01", "0", id="just-above-zero"),
        pytest.param("50", "0", id="inside-the-flat-zero-band"),
        pytest.param("100", "0", id="at-the-first-boundary"),  # the lower band, flat
        pytest.param("100.01", "0.10", id="just-above-the-first-boundary"),
        pytest.param("150", "0.10", id="inside-the-sloped-band"),
        pytest.param("200", "0.10", id="at-the-second-boundary"),  # the lower, sloped band
        pytest.param("200.01", "0", id="just-above-the-second-boundary"),
        pytest.param("250", "0", id="inside-the-flat-band"),
        pytest.param("300", "0", id="at-the-third-boundary"),  # the lower, flat band
        pytest.param("300.01", "0.25", id="just-above-the-third-boundary"),
        pytest.param("100000", "0.25", id="far-above-in-the-open-top-band"),
    ],
)
def test_gives_the_rate_of_the_band_the_base_falls_in(base: str, slope: str) -> None:
    output = compute(capability(), base)

    assert output == Artifact(SLOPE, D(slope))
    assert type(output.value) is Decimal


def test_a_base_at_a_boundary_falls_in_the_lower_band() -> None:
    assert compute(capability(), "100") == Artifact(SLOPE, D("0"))
    assert compute(capability(), "200") == Artifact(SLOPE, D("0.10"))
    assert compute(capability(), "300") == Artifact(SLOPE, D("0"))


def test_a_flat_band_gives_a_rate_of_zero() -> None:
    assert compute(capability(), "250").value == D("0")


def test_a_zero_base_gives_the_first_bands_rate() -> None:
    assert compute(capability(), "0").value == D("0")


def test_a_zero_base_in_a_chart_whose_first_band_is_sloped_gives_that_rate() -> None:
    bands = (AmountBand(D(0), minus=D(0), rate=TEN_PERCENT, plus=D(0)),)

    assert compute(capability(table(bands)), "0") == Artifact(SLOPE, D("0.10"))


def test_the_top_band_is_open_ended() -> None:
    assert compute(capability(), "1000000000").value == D("0.25")


def test_a_chart_of_one_flat_band_gives_zero_everywhere() -> None:
    wired = capability(table((AmountBand(D(0), amount=D(5)),)))

    assert compute(wired, "0").value == D("0")
    assert compute(wired, "999999").value == D("0")


def test_the_rate_is_not_rounded() -> None:
    bands = (AmountBand(D(0), amount=D(0)), AmountBand(D(100), minus=D(100), rate=ODD, plus=D(0)))

    assert compute(capability(table(bands)), "150") == Artifact(SLOPE, D("0.123456"))


def test_the_datasets_rounding_rule_does_not_apply_to_the_rate() -> None:
    # A rule that rounds to the whole unit would turn 0.10 into 0.
    for rounding in (WHOLE, RoundTo(D("0.01"), RoundingMode.HALF_UP)):
        wired = capability(table(rounding=rounding))

        assert compute(wired, "150") == Artifact(SLOPE, D("0.10"))
        assert str(compute(wired, "150").value) == "0.10"
        assert str(compute(wired, "250").value) == "0"


def test_a_flat_band_gives_exactly_the_integer_zero_decimal() -> None:
    assert str(compute(capability(), "250").value) == "0"


def test_a_negative_base_is_refused_as_the_band_lookup_refuses_it() -> None:
    with pytest.raises(ValueError, match="negative"):
        compute(capability(), "-0.01")


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), Artifact(INCOME, D("150"))))

    assert result.outputs == (Artifact(SLOPE, D("0.10")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="income"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_the_trace_fields_are_in_their_order() -> None:
    assert [field.name for field in fields(AmountByBandRateLine)] == [
        "output",
        "base",
        "base_amount",
        "over",
        "rate",
        "result",
    ]


def test_traces_one_line_for_a_sloped_band() -> None:
    assert trace_of(capability(), "150") == (
        AmountByBandRateLine(
            output=SLOPE,
            base=INCOME,
            base_amount=D("150"),
            over=D("100"),
            rate=TEN_PERCENT,
            result=D("0.10"),
        ),
    )


def test_traces_one_line_for_a_flat_band_with_no_rate() -> None:
    assert trace_of(capability(), "250") == (
        AmountByBandRateLine(
            output=SLOPE,
            base=INCOME,
            base_amount=D("250"),
            over=D("200"),
            rate=None,
            result=D("0"),
        ),
    )


def test_the_trace_names_the_band_a_base_at_a_boundary_falls_in() -> None:
    (line,) = trace_of(capability(), "200")

    assert line.over == D("100")
    assert line.rate == TEN_PERCENT
    assert line.result == D("0.10")


def test_the_trace_records_the_base_not_the_part_over_the_boundary() -> None:
    (line,) = trace_of(capability(), "300.01")

    assert line.base_amount == D("300.01")
    assert line.over == D("300")


def test_the_trace_result_is_the_output_and_the_lines_amount() -> None:
    result = capability().compute((Artifact(INCOME, D("150")),))

    (output,) = result.outputs
    (line,) = result.trace
    assert isinstance(line, AmountByBandRateLine)
    assert line.amount == output.value
    assert line.result == output.value


def test_the_trace_line_labels_its_output_figure() -> None:
    (line,) = trace_of(capability(), "150")

    assert line.label == SLOPE.label


def test_the_trace_holds_no_text() -> None:
    for line in trace_of(capability(), "150"):
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_the_trace_line_is_frozen_and_compares_by_value() -> None:
    line = AmountByBandRateLine(SLOPE, INCOME, D("150"), D("100"), TEN_PERCENT, D("0.10"))

    assert line == AmountByBandRateLine(SLOPE, INCOME, D("150"), D("100"), TEN_PERCENT, D("0.10"))
    with pytest.raises(FrozenInstanceError):
        line.result = D("0")  # type: ignore[misc]


def test_the_trace_line_is_exported_by_its_module_and_the_package() -> None:
    from tax_engine.domain import trace as trace_package

    assert "AmountByBandRateLine" in trace_rate_tables.__all__
    assert trace_package.AmountByBandRateLine is AmountByBandRateLine
    assert issubclass(AmountByBandRateLine, TraceLine)
