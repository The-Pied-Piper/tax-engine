"""The 2026 `ca-ab/medical_expense_rate` dataset, provisional until Form AB428 2026 appears.

The 2026 figure is carried forward unchanged from the 2025 file; the header says so. Rounding is
half-up to the cent like 2025.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/medical_expense_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; the 2026 AB428 is not yet "
    "published."
)


def test_2026_medical_expense_rate_is_3_percent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.03"))


def test_2026_medical_expense_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_medical_expense_rate_cites_the_2025_form_text_only() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2026_medical_expense_rate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (root / "parameters" / "medical_expense_rate" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, RATE)
    original = SOURCE.get(FAMILY, 2025, RATE)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources
