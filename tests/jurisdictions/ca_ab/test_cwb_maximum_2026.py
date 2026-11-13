"""The 2026 `ca-ab/cwb_maximum` dataset, provisional until Schedule 6 2026 appears.

The 2026 figure is taken from the 2025 Schedule 6 form text named in `sources`; the dataset header
says so and the file carries a replacement note. Rounding is half-up to the cent like 2025.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/cwb_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-s6/5009-s6-25e.txt"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 1,750 x 1.02 (the "
    "federal 2026 factor) = 1,785 exactly, so no rounding step applies."
)


def _file_text() -> str:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    return (root / "parameters" / "cwb_maximum" / "2026.yaml").read_text()


def test_2026_cwb_maximum_is_1785() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("1785"))


def test_2026_cwb_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_cwb_maximum_cites_the_2025_schedule_6_form_text_only() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2026_cwb_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_the_2026_file_carries_a_replacement_note_after_the_derivation() -> None:
    lines = _file_text().splitlines()

    assert any("MUST BE REPLACED" in line for line in lines[2:])


def test_2025_cwb_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1750"))


def test_the_2026_maximum_is_the_2025_amount_times_the_federal_factor_exactly() -> None:
    indexed = D("1750") * D("1.02")

    assert indexed == D("1785.00")
    assert indexed == D("1785")
