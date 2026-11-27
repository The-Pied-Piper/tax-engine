"""The 2026 `ca-nb/low_income_reduction_maximum` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import UnitRegistry

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PACKAGES = JurisdictionPackages((tax_engine.jurisdictions.core, tax_engine.jurisdictions.ca))
PARAMETER_PARSERS = ParameterParserRegistry()
PACKAGES.register_parameter_parsers(PARAMETER_PARSERS)
UNITS = UnitRegistry()
PACKAGES.register_units(UNITS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS, UNITS)
FAMILY = "ca-nb/low_income_reduction_maximum"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: indexed from the 2025 form text named in sources; to be confirmed aga"
    "inst the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: NB indexes this figure every year (NB428 2016 to 2025); the 2026 index"
    " factor is 2.0%, the same factor that takes the 2025 basic personal amount 13,396 to"
    " the 13,664 printed in T4127 (Jan 2026) Table 8.2: 2 x the indexed basic reduction 8"
    "18 (the 2025 maximum 1,604 is 2 x 802 and every year 2016 to 2025 is 2 x the basic r"
    "eduction) = 1,636; unconfirmed, as no 2026 NB428 is published and T4127 (Jan and Jul"
    " 2026) does not print it."
)


def test_2026_low_income_reduction_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("1636"))


def test_2026_low_income_reduction_maximum_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_low_income_reduction_maximum_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == SOURCES


def test_2026_low_income_reduction_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = NEW_BRUNSWICK_DIR / "parameters" / "low_income_reduction_maximum" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
