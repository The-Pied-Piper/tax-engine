"""Unit tests for the RateFigure capability (`core/rate_figure`): a `rate` dataset's rate as a
figure of its own, exactly. The dataset's rounding rule (a credit rate prints to the cent) is not
applied."""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.trace import RateFigureLine
from tax_engine.jurisdictions.core.capabilities.rate_figure import RateFigure
from tests.capabilities import bundled_capabilities

D = Decimal
OUT = AmountKind("ex/rate")


def test_is_registered_as_ca_rate_figure() -> None:
    assert bundled_capabilities().get("core/rate_figure") is RateFigure
    assert RateFigure.PARAMETERS == {"rate": RATE}
    assert RateFigure.CONSUMES == {}
    assert RateFigure.PRODUCES == {"output": Decimal}


def test_produces_the_rate_without_the_datasets_rounding() -> None:
    dataset = ParameterDataset(
        "ex/credit_rate",
        2025,
        RATE,
        Rate(D("0.145")),
        RoundTo(D("0.01"), RoundingMode.HALF_UP),
        ("https://example.org/t",),
    )

    result = RateFigure(dataset, OUT).compute(())

    assert result.outputs == (Artifact(OUT, D("0.145")),)
    (line,) = result.trace
    assert isinstance(line, RateFigureLine)
    assert line.amount == D("0.145")


# --- the contract -----------------------------------------------------------------------------

DATASET = ParameterDataset(
    "ex/rate", 2025, RATE, Rate(D("0.2")), RoundTo(D("0.01"), RoundingMode.HALF_UP), ("https://x",)
)


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(RateFigure)
    assert "produces" not in vars(RateFigure)


def test_its_slots_are_read_only() -> None:
    for slots in (RateFigure.PARAMETERS, RateFigure.CONSUMES, RateFigure.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_cannot_be_changed() -> None:
    for slots in (RateFigure.PARAMETERS, RateFigure.CONSUMES, RateFigure.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = RateFigure(rate=DATASET, output=OUT)

    assert wired.compute(()).outputs == (Artifact(OUT, D("0.2")),)


def test_mypy_rejects_wiring_an_artifact_kind_of_another_value_type() -> None:
    count = CountKind("ex/count")
    # The ignore fails under mypy (warn_unused_ignores) if wiring a kind of another value type is
    # ever accepted. At run time, building it fails too.
    with pytest.raises(InvalidCapabilityError, match="RateFigure"):
        RateFigure(DATASET, count)  # type: ignore[arg-type]


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(RateFigure, "__type_params__", ())
    assert not getattr(RateFigure, "__parameters__", ())
