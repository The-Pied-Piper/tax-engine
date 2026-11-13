"""The 2026 `ca-ab/cwb_reduction_threshold` dataset, provisional until Schedule 6 2026 appears.

The 2026 figure is taken from the 2025 Schedule 6 form text named in `sources`; the dataset header
says so and the file carries a replacement note. Rounding is half-up to the cent like 2025.
"""

from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/cwb_reduction_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-s6/5009-s6-25e.txt"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 26,159 x 1.02 (the"
    " federal 2026 factor) = 26,682.18, rounded down to 26,682 as in 2025."
)


def _file_text() -> str:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    return (root / "parameters" / "cwb_reduction_threshold" / "2026.yaml").read_text()


def test_2026_cwb_reduction_threshold_is_26682() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("26682"))


def test_2026_cwb_reduction_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_cwb_reduction_threshold_cites_the_2025_schedule_6_form_text_only() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2026_cwb_reduction_threshold_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_the_2026_file_carries_a_replacement_note_after_the_derivation() -> None:
    lines = _file_text().splitlines()

    assert any("MUST BE REPLACED" in line for line in lines[2:])


def test_2025_cwb_reduction_threshold_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("26159"))


def test_the_2026_threshold_is_the_2025_amount_times_the_federal_factor_rounded_down() -> None:
    indexed = D("26159") * D("1.02")

    assert indexed == D("26682.18")
    assert indexed.to_integral_value(rounding=ROUND_DOWN) == D("26682")
