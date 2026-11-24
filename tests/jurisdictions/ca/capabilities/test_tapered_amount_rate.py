"""Unit tests for the TaperedAmountRate capability (`ca/tapered_amount_rate`).

The output is the taper's supplement over its range while the base is over the threshold and under
the end of the range, 0 on either edge and outside, rounded once with the rounding dataset.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.jurisdictions.ca.capabilities.tapered_amount_rate import TaperedAmountRate
from tax_engine.jurisdictions.ca.parameter_shapes.taper import TAPER, Taper
from tax_engine.jurisdictions.ca.trace.marginal_rate import TaperedAmountRateLine
from tests.capabilities import bundled_capabilities

D = Decimal
BASE = AmountKind("ex/base")
OUT = AmountKind("ex/rate")
TAPER_DATA = ParameterDataset(
    "ex/taper",
    2025,
    TAPER,
    Taper(D("14538"), D("1591"), D("177882"), D("75532")),
    RoundTo(D("0.01"), RoundingMode.HALF_UP),
    ("https://example.org/t",),
)
ROUNDING = ParameterDataset(
    "ex/rounding",
    2025,
    ROUNDING_ONLY,
    RoundingOnly(),
    RoundTo(D("0.0000001"), RoundingMode.HALF_UP),
    ("https://example.org/t",),
)


def compute(base: str):  # type: ignore[no-untyped-def]
    return TaperedAmountRate(TAPER_DATA, ROUNDING, BASE, OUT).compute((Artifact(BASE, D(base)),))


def test_is_registered_as_ca_tapered_amount_rate() -> None:
    assert bundled_capabilities().get("ca/tapered_amount_rate") is TaperedAmountRate
    assert TaperedAmountRate.PARAMETERS == {"taper": TAPER, "rounding": ROUNDING_ONLY}
    assert TaperedAmountRate.CONSUMES == {"base": Decimal}
    assert TaperedAmountRate.PRODUCES == {"output": Decimal}


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0", "0"),
        ("177882", "0"),
        ("177882.01", "0.0210639"),
        ("200000", "0.0210639"),
        ("253413.99", "0.0210639"),
        ("253414", "0"),
        ("300000", "0"),
    ],
)
def test_is_the_supplement_over_the_range_strictly_inside_the_taper(base: str, rate: str) -> None:
    result = compute(base)

    assert result.outputs == (Artifact(OUT, D(rate)),)


def test_records_one_line_and_explains_it_in_english() -> None:
    (line,) = compute("200000").trace

    assert isinstance(line, TaperedAmountRateLine)
    text = EnglishTraceRenderer().render(line)
    assert "1591.00 falls over 75532.00" in text
    assert "between 177882.00 and 253414.00" in text
