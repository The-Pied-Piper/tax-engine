"""The 2026 `ca-nb/cent_rounding` dataset, provisional.

Pins the 2026 rule, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-nb/cent_rounding"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against t"
    "he 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 form; T4127 (Jan 2026) does not pr"
    "int this figure and the 2026 form is not yet published, so it is unconfirmed."
)


def test_2026_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_cent_rounding_is_the_2025_rule_carried_forward() -> None:
    carried = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)
    original = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_2026_cent_rounding_sources_and_year() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = NEW_BRUNSWICK_DIR / "parameters" / "cent_rounding" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
