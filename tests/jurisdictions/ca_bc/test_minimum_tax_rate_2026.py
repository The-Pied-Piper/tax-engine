"""The 2026 `ca-bc/minimum_tax_rate` dataset, carried from 2025 (provisional).

No 2026 source states a change and the 2026 British Columbia forms are not yet published, so the
2026 file repeats the 2025 figure and rounding, cites the 2025 form text, and says so in its header.
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

# British Columbia is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/minimum_tax_rate"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; "
    "the 2026 form is not yet published."
)


def test_2026_minimum_tax_rate_is_the_2025_rate() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(Decimal("0.349"))


def test_2026_minimum_tax_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2026_minimum_tax_rate_cites_the_2025_form_text() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt",
    )


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "minimum_tax_rate" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, RATE)
    original = SOURCE.get(FAMILY, 2025, RATE)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
