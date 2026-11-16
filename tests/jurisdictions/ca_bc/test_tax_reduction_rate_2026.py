"""The 2026 `ca-bc/tax_reduction_rate` dataset (provisional):
3.56%, carried forward from 2025.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/tax_reduction_rate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation: "


def _file_lines() -> list[str]:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    return (root / "parameters" / "tax_reduction_rate" / "2026.yaml").read_text().splitlines()


def test_2026_tax_reduction_rate_is_0_0356() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.0356"))


def test_2026_tax_reduction_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_tax_reduction_rate_cites_its_source() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_lines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)


def test_2025_tax_reduction_rate_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.0356"))
