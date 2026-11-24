"""Unit tests for the RateFigure capability (`ca/rate_figure`): a `rate` dataset's rate as a figure
of its own, exactly. The dataset's rounding rule (a credit rate prints to the cent) is not applied.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.rate_figure import RateFigure
from tax_engine.jurisdictions.ca.trace.marginal_rate import RateFigureLine
from tests.capabilities import bundled_capabilities

D = Decimal
OUT = AmountKind("ex/rate")


def test_is_registered_as_ca_rate_figure() -> None:
    assert bundled_capabilities().get("ca/rate_figure") is RateFigure
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
