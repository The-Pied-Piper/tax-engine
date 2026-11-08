"""The 2026 `ca-on/tax_reduction_multiplier` dataset (provisional)."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/tax_reduction_multiplier"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against "
    "the 2026 form text when CRA publishes it."
)
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt",)


def test_2026_tax_reduction_multiplier() -> None:
    data = SOURCE.get(FAMILY, 2026, FRACTION)

    assert data.values == Fraction(2, 1)
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_2026_tax_reduction_multiplier_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "tax_reduction_multiplier" / "2026.yaml").read_text().splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_2025_tax_reduction_multiplier_is_unchanged() -> None:
    assert SOURCE.get(FAMILY, 2025, FRACTION).values == Fraction(2, 1)
