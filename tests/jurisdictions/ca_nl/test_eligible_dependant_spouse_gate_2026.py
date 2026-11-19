"""The 2026 `ca-nl/eligible_dependant_spouse_gate` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/eligible_dependant_spouse_gate"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    "https://assembly.nl.ca/legislation/sr/statutes/i01-1.htm",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: the 2026 maximum of `ca-nl/eligible_dependant_amount_maximum`, 9142.00 "
    "(2025 amount 9043.00 x 1.011, rounded to the nearest dollar, a half going up, NL Income "
    "Tax Act, 2000 s.6.1(3)(c)); unconfirmed, as the 2026 NL428 is not yet published."
)


def test_2026_eligible_dependant_spouse_gate_rows() -> None:
    bands = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0
    assert bands[0].amount == D("9142")
    assert bands[1].over == D("0.005")
    assert bands[1].amount == 0


def test_2026_eligible_dependant_spouse_gate_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_eligible_dependant_spouse_gate_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.sources == SOURCES


def test_2026_eligible_dependant_spouse_gate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "eligible_dependant_spouse_gate" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_the_gate_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.005")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


def test_the_gate_maximum_is_the_eligible_dependant_maximum() -> None:
    maximum = SOURCE.get("ca-nl/eligible_dependant_amount_maximum", 2026, CREDIT).values.amount

    assert SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND).values.bands[0].amount == maximum


def test_2025_eligible_dependant_spouse_gate_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.values.bands[0].amount == D("9043")
    assert data.sources != SOURCES
