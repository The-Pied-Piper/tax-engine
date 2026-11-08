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
    "# Provisional: taken from the 2025 form text named in sources; "
    "to be confirmed against the 2026 form text when CRA publishes it."
)
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-a/5006-a-25e.txt",
    "https://www.ontario.ca/page/low-income-individuals-and-families-tax-credit",
    "https://www.budget.ontario.ca/2025/fallstatement/provisions.html",
)


def test_2026_lift_individual_income_threshold() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("32500"))
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
    assert "carried forward unchanged from the 2025 file, not indexed" in lines[1]
