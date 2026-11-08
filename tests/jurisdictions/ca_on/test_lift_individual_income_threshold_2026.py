"""The 2026 `ca-on/lift_individual_income_threshold` dataset (provisional)."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/lift_individual_income_threshold"
PROVISIONAL_HEADER = (
    "# Provisional: indexed from the 2025 form text by T4127's Ontario index rate; "
    "to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
SOURCES = (T4127_URL,)


def test_2026_lift_individual_income_threshold() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("33118"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_2026_lift_individual_income_threshold_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "lift_individual_income_threshold" / "2026.yaml")
        .read_text()
        .splitlines()
    )

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")
    assert "least certain" in lines[1] + lines[2]
    assert "1.9%" in "".join(lines[1:6])
    assert "Table 8.2" in "".join(lines[1:6])
    assert "nearest dollar" in "".join(lines[1:6])


def test_2025_lift_individual_income_threshold_is_unchanged() -> None:
    assert SOURCE.get(FAMILY, 2025, CREDIT).values == Credit(amount=D("32500.00"))
