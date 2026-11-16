"""The 2026 `ca-bc/credit_rate` dataset, provisional until Form BC428 2026 appears.

From 2026 British Columbia's lowest personal income tax rate rises from 5.06% to 5.60%, announced on
17 February 2026 and printed in the July 2026 T4127 (the January edition still shows 5.06%). The
credit rate is that lowest rate; the dataset header says where it comes from. Rounding is half-up to
the cent like 2025.
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
FAMILY = "ca-bc/credit_rate"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)


def _file_text() -> str:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    return (root / "parameters" / "credit_rate" / "2026.yaml").read_text()


def test_2026_credit_rate_is_5_point_6_percent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.056"))


def test_2026_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_credit_rate_cites_the_july_t4127_only() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == (T4127_URL,)


def test_2026_credit_rate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation:")


def test_2025_credit_rate_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.0506"))
