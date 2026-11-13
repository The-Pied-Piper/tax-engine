"""The 2026 `ca-ab/supplemental_credit_rate` dataset, provisional until Worksheet AB428 2026 exists.

The 2026 figure is taken from the 2025 Worksheet AB428 text named in `sources`; the dataset header
says so and records that the rate is carried forward unchanged. The rate is a statutory percentage,
not a printed amount, so the file carries no replacement note. Rounding is half-up to the cent like
2025.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/supplemental_credit_rate"
CRA_WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from"
    " the 2025 file; the 2026 form is not yet published."
)


def _file_text() -> str:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    return (root / "parameters" / "supplemental_credit_rate" / "2026.yaml").read_text()


def test_2026_supplemental_credit_rate_is_25_percent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.25"))


def test_2026_supplemental_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_supplemental_credit_rate_cites_the_2025_worksheet_ab428_text_only() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == (CRA_WORKSHEET_TEXT,)


def test_2026_supplemental_credit_rate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_supplemental_credit_rate_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))
