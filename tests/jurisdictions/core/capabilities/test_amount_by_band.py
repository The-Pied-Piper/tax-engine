"""Unit tests for the AmountFromBand capability (`core/amount_by_band`), with made-up figures.

Its slots: one parameter slot `table` (an `amount_by_band` dataset), one consumed slot `base` and
one produced slot `output`. The output is the amount of the chart's band the base falls in,
`AmountBand.amount_at(base)`, unrounded there, rounded once by the dataset's rule (no rounding by
default). The band is chosen as `AmountByBand.band_for` chooses it: an income at a boundary falls
in the lower band. It records one `AmountByBandLine` for the band it used.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
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
from tax_engine.domain.trace import AmountByBandLine
from tax_engine.domain.trace import rate_tables as trace_rate_tables
from tax_engine.jurisdictions.core.capabilities.amount_by_band import AmountFromBand
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
HALF_TO_THE_UNIT = RoundTo(D("1"), RoundingMode.FLOOR)

INCOME = AmountKind("ex/income")
PREMIUM = AmountKind("ex/premium")

TEN_PERCENT = Rate(D("0.10"))
QUARTER = Rate(D("0.25"))

# A flat 0 from 0; 10% of the income over 100 from 100; a flat 12 from 200; 15 plus 25% of the
# income over 300 from 300. The boundaries 100, 200 and 300 each fall in the lower band.
BANDS = (
    AmountBand(D(0), amount=D(0)),
    AmountBand(D(100), minus=D(100), rate=TEN_PERCENT, plus=D(0)),
    AmountBand(D(200), amount=D(12)),
    AmountBand(D(300), minus=D(300), rate=QUARTER, plus=D(15)),
)


def table(*, rounding: RoundingRule = NO_ROUNDING) -> ParameterDataset[AmountByBand]:
    return ParameterDataset(
        "ex/amount_by_band",
        2025,
        AMOUNT_BY_BAND,
        AmountByBand(BANDS),
        rounding,
        ("https://example.org/b",),
    )


def capability(data: ParameterDataset[AmountByBand] | None = None) -> AmountFromBand:
    """By default the made-up bands above, exact."""
    return AmountFromBand(data or table(), INCOME, PREMIUM)


def compute(wired: AmountFromBand, base: str) -> Artifact[Any]:
    (output,) = wired.compute((Artifact(INCOME, D(base)),)).outputs
    return output


def trace_of(wired: AmountFromBand, base: str) -> tuple[Any, ...]:
    return wired.compute((Artifact(INCOME, D(base)),)).trace


def test_is_registered_as_core_amount_by_band() -> None:
    assert bundled_capabilities().get("core/amount_by_band") is AmountFromBand


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({INCOME})
    assert capability().produces == frozenset({PREMIUM})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(AmountFromBand)
    assert "produces" not in vars(AmountFromBand)


def test_declares_its_slots() -> None:
    assert AmountFromBand.PARAMETERS == {"table": AMOUNT_BY_BAND}
    assert AmountFromBand.PARAMETERS["table"] is AMOUNT_BY_BAND
    assert AmountFromBand.CONSUMES == {"base": Decimal}
    assert AmountFromBand.PRODUCES == {"output": Decimal}
    assert not AmountFromBand.is_list_slot("base")


def test_its_slots_are_read_only() -> None:
    for slots in (AmountFromBand.PARAMETERS, AmountFromBand.CONSUMES, AmountFromBand.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(AmountFromBand.PARAMETERS, Mapping[str, ParameterKind[AmountByBand]])
    assert_type(AmountFromBand.CONSUMES, Mapping[str, type])
    assert_type(AmountFromBand.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (AmountFromBand.PARAMETERS, AmountFromBand.CONSUMES, AmountFromBand.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = AmountFromBand(table=table(), base=INCOME, output=PREMIUM)

    assert compute(wired, "250") == Artifact(PREMIUM, D("12"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        AmountFromBand(table(), INCOME, PREMIUM, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountFromBand") as raised:
        AmountFromBand(table(), INCOME, INCOME)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_list_of_kinds_for_its_base() -> None:
    with pytest.raises(InvalidCapabilityError, match="AmountFromBand.*'base'"):
        AmountFromBand(table(), (INCOME,), PREMIUM)  # type: ignore[arg-type]


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # An ArtifactKind[int] is not Money; the ignore fails under mypy (warn_unused_ignores) if
    # wiring an artifact kind of another value type is ever accepted. At run time, building it
    # fails too.
    with pytest.raises(InvalidCapabilityError, match="AmountFromBand.*'base'"):
        AmountFromBand(table(), count, PREMIUM)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[AmountByBand]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        AmountFromBand(rate, INCOME, PREMIUM)  # type: ignore[arg-type]

    assert callable(wire)


def test_mypy_rejects_bare_bands_without_their_dataset() -> None:
    def wire() -> None:  # type-checked, never run
        # Parameter slots take the dataset, which carries the rounding rule; never bare values.
        AmountFromBand(AmountByBand(BANDS), INCOME, PREMIUM)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(AmountFromBand, "__type_params__", ())
    assert not getattr(AmountFromBand, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "premium"),
    [
        pytest.param("0", "0", id="zero-income"),
        pytest.param("0.01", "0", id="just-above-zero"),
        pytest.param("50", "0", id="inside-the-flat-zero-band"),
        pytest.param("100", "0", id="at-the-first-boundary"),
        pytest.param("150", "5", id="inside-the-sloped-band"),  # (150 - 100) x 10%
        pytest.param("200", "10", id="at-the-second-boundary"),  # (200 - 100) x 10%, not 12
        pytest.param("200.01", "12", id="just-above-the-second-boundary"),
        pytest.param("250", "12", id="inside-the-flat-band"),
        pytest.param("300", "12", id="at-the-third-boundary"),  # not 15, the upper band
        pytest.param("300.01", "15.0025", id="just-above-the-third-boundary"),  # 15 + 0.01 x 25%
        pytest.param("400", "40", id="far-above"),  # (400 - 300) x 25% + 15
    ],
)
def test_gives_the_amount_of_the_band_the_base_falls_in(base: str, premium: str) -> None:
    output = compute(capability(), base)

    assert output == Artifact(PREMIUM, D(premium))
    assert type(output.value) is Decimal


def test_an_income_at_a_boundary_falls_in_the_lower_band() -> None:
    assert compute(capability(), "200") == Artifact(PREMIUM, D("10"))
    assert compute(capability(), "300") == Artifact(PREMIUM, D("12"))


def test_zero_income_gives_the_first_band_unrounded() -> None:
    assert compute(capability(), "0") == Artifact(PREMIUM, D("0"))


def test_zero_income_gives_the_first_band_rounded_to_the_cent() -> None:
    wired = capability(table(rounding=CENT))

    assert str(compute(wired, "0").value) == "0.00"


def test_is_exact_without_rounding() -> None:
    # (150.03 - 100) x 10% = 5.003: nothing rounded.
    assert compute(capability(), "150.03") == Artifact(PREMIUM, D("5.003"))


def test_rounds_half_up_to_the_cent() -> None:
    wired = capability(table(rounding=CENT))

    # (150.05 - 100) x 10% = 5.005, a tie: half-up gives 5.01.
    assert compute(wired, "150.05") == Artifact(PREMIUM, D("5.01"))


def test_rounds_a_flat_amount_with_the_datasets_rule() -> None:
    wired = capability(table(rounding=CENT))

    assert compute(wired, "250") == Artifact(PREMIUM, D("12.00"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    wired = capability(table(rounding=CENT))

    assert str(compute(wired, "250").value) == "12.00"


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(table(rounding=HALF_TO_THE_UNIT))

    # (159.95 - 100) x 10% = 5.995: floored to the unit gives 5, where half-up would give 6.
    assert compute(wired, "159.95") == Artifact(PREMIUM, D("5"))


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), Artifact(INCOME, D("250"))))

    assert result.outputs == (Artifact(PREMIUM, D("12")),)


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="income"):
        capability().compute(())


# --- trace ------------------------------------------------------------------------------------


def test_the_trace_fields_are_in_their_order() -> None:
    assert [field.name for field in fields(AmountByBandLine)] == [
        "output",
        "base",
        "base_amount",
        "over",
        "flat_amount",
        "minus",
        "rate",
        "plus",
        "rounding",
        "result",
    ]


def test_traces_one_line_for_a_flat_band() -> None:
    assert trace_of(capability(), "250") == (
        AmountByBandLine(
            output=PREMIUM,
            base=INCOME,
            base_amount=D("250"),
            over=D("200"),
            flat_amount=D("12"),
            minus=None,
            rate=None,
            plus=None,
            rounding=NO_ROUNDING,
            result=D("12"),
        ),
    )


def test_traces_one_line_for_a_sloped_band() -> None:
    assert trace_of(capability(), "150") == (
        AmountByBandLine(
            PREMIUM,
            INCOME,
            D("150"),
            D("100"),
            None,
            D("100"),
            TEN_PERCENT,
            D("0"),
            NO_ROUNDING,
            D("5"),
        ),
    )


def test_a_flat_band_line_has_no_sloped_figures() -> None:
    (line,) = trace_of(capability(), "250")

    assert (line.minus, line.rate, line.plus) == (None, None, None)
    assert line.flat_amount == D("12")


def test_a_sloped_band_line_has_no_flat_amount() -> None:
    (line,) = trace_of(capability(), "150")

    assert line.flat_amount is None
    assert (line.minus, line.rate, line.plus) == (D("100"), TEN_PERCENT, D("0"))


def test_the_trace_names_the_band_an_income_at_a_boundary_falls_in() -> None:
    (line,) = trace_of(capability(), "200")

    assert line.over == D("100")
    assert line.result == D("10")


def test_the_trace_records_the_datasets_rounding_rule_and_the_rounded_result() -> None:
    (line,) = trace_of(capability(table(rounding=CENT)), "150.05")

    assert line == AmountByBandLine(
        PREMIUM,
        INCOME,
        D("150.05"),
        D("100"),
        None,
        D("100"),
        TEN_PERCENT,
        D("0"),
        CENT,
        D("5.01"),
    )


def test_the_trace_result_is_the_output() -> None:
    wired = capability(table(rounding=CENT))
    result = wired.compute((Artifact(INCOME, D("150.05")),))

    (output,) = result.outputs
    (line,) = result.trace
    assert line.amount == output.value


def test_the_trace_records_the_income_as_the_base_amount_not_the_part_over_the_boundary() -> None:
    (line,) = trace_of(capability(), "300.01")

    assert line.base_amount == D("300.01")
    assert line.over == D("300")


def test_the_trace_holds_no_text() -> None:
    for line in trace_of(capability(), "150"):
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


def test_the_trace_line_is_exported_by_its_module_and_the_package() -> None:
    from tax_engine.domain import trace as trace_package

    assert "AmountByBandLine" in trace_rate_tables.__all__
    assert trace_package.AmountByBandLine is AmountByBandLine
    assert issubclass(AmountByBandLine, trace_package.TraceLine)
