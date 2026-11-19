"""The 2026 `ca-nl/medical_expense_dollar_limit` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    newfoundland_packages().roots(),
    newfoundland_parameter_parsers(),
    newfoundland_units(),
)
FAMILY = "ca-nl/medical_expense_dollar_limit"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 2410 x 1.011 (Newfoundland and Labrador's index rate "
    "in T4127 (Jan 2026) Table 8.2; applied to the 2025 basic amount 11,067 it gives "
    "the printed 11,188) = 2436.51, rounded to the nearest dollar, a half going up, "
    "to 2437 (NL Income Tax Act, 2000 s.6.1(3)(c)); unconfirmed, as the 2026 NL428 is"
    " not yet published."
)


def test_2026_medical_expense_dollar_limit_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("2437"))


def test_2026_medical_expense_dollar_limit_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_medical_expense_dollar_limit_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == SOURCES


def test_2026_medical_expense_dollar_limit_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "medical_expense_dollar_limit" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_medical_expense_dollar_limit_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("2410"))
    assert data.sources != SOURCES
