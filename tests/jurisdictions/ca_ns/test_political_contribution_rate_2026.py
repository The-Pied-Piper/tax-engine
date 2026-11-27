"""The 2026 `ca-ns/political_contribution_rate` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(nova_scotia_packages().roots(), nova_scotia_parameter_parsers())
FAMILY = "ca-ns/political_contribution_rate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; T4127 (Jan and Jul 2026)"
    " does not print this figure and the 2026 form is not yet published, so it is "
    "unconfirmed."
)


def test_2026_political_contribution_rate_value() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.75"))


def test_2026_political_contribution_rate_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_political_contribution_rate_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == SOURCES


def test_2026_political_contribution_rate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = nova_scotia_packages().roots()[Namespace("ca-ns")]
    path = root / "parameters" / "political_contribution_rate" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_political_contribution_rate_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.75"))
