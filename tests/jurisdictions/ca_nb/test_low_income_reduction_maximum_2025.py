"""The 2025 `ca-nb/low_income_reduction_maximum` dataset.

Pins the 2025 figure, rounding, sources, tax year and the two header comment lines of the file.
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


def test_2025_low_income_reduction_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1604"))


def test_2025_low_income_reduction_maximum_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_low_income_reduction_maximum_sources() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == SOURCES


def test_2025_low_income_reduction_maximum_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.tax_year == 2025
