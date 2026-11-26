"""The 2026 `ca-nb/low_income_reduction_basic` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-nb/low_income_reduction_basic"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against t"
    "he 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 form; T4127 (Jan 2026) does not pr"
    "int this figure and the 2026 form is not yet published, so it is unconfirmed."
)


def test_2026_low_income_reduction_basic_value_and_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("802"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_low_income_reduction_basic_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_low_income_reduction_basic_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = NEW_BRUNSWICK_DIR / "parameters" / "low_income_reduction_basic" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
