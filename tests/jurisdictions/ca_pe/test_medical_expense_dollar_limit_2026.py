"""The 2026 `ca-pe/medical_expense_dollar_limit` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
    prince_edward_island_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(),
    prince_edward_island_parameter_parsers(),
    prince_edward_island_units(),
)
FAMILY = "ca-pe/medical_expense_dollar_limit"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against "
    "the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; T4127 (Jan and Jul 2026) does"
    " not print this figure and the 2026 form is not yet published, so it is unconfirmed."
)


def test_2026_medical_expense_dollar_limit_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("1678"))


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
    root = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    path = root / "parameters" / "medical_expense_dollar_limit" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_medical_expense_dollar_limit_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1678"))
