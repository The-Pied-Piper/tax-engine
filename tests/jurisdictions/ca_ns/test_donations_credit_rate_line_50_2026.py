"""The 2026 `ca-ns/donations_credit_rate_line_50` dataset, provisional.

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
FAMILY = "ca-ns/donations_credit_rate_line_50"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form "
    "text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jan 2026) Table 8.1, Nova Scotia row "
    "(highest rate 0.2100), and in T4127 (Jul 2026) Table 8.1 (0.2100); this is the T4127"
    " bracket rate (T4127 does not name the NS428 line), the 2025 NS428 line 50 prints "
    "the same 21%, and the 2026 form text is not yet published; no rounding applied here."
)


def test_2026_donations_credit_rate_line_50_value() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.21"))


def test_2026_donations_credit_rate_line_50_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_donations_credit_rate_line_50_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == SOURCES


def test_2026_donations_credit_rate_line_50_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = nova_scotia_packages().roots()[Namespace("ca-ns")]
    path = root / "parameters" / "donations_credit_rate_line_50" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_donations_credit_rate_line_50_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.21"))
    assert data.sources != SOURCES
