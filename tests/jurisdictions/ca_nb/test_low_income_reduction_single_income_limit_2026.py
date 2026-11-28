"""The 2026 `ca-nb/low_income_reduction_single_income_limit` dataset, provisional.

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
FAMILY = "ca-nb/low_income_reduction_single_income_limit"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: indexed from the 2025 form text named in sources; to be confirmed aga"
    "inst the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: NB raised this figure every year (NB428 2016 to 2025), by the index fa"
    "ctor except that the base amount rose more than the factor in 2021 and 2022 (and the"
    " limit with it); the 2026 index factor is 2.0%, the factor T4127 (Jan 2026) Table 8."
    "2 prints for New Brunswick (it takes the 2025 basic personal amount 13,396 to the pr"
    "inted 13,664): the indexed base amount 22,358 plus the indexed basic reduction 818 d"
    "ivided by the 3% rate (27,266.67) = 49,624.67, rounded to the nearest dollar, a half"
    " going up (the project's rounding for indexed amounts; the forms print none), to 49,"
    "625 (the 2025 limit 48,653 is its 2025 base amount 21,920 plus 802 / 0.03 = 26,733.3"
    "3, and every year 2016 to 2025 matches this to within a dollar); unconfirmed, as no "
    "2026 NB428 is published and T4127 (Jan and Jul 2026) does not print it."
)


def test_2026_low_income_reduction_single_income_limit_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("49625"))


def test_2026_low_income_reduction_single_income_limit_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_low_income_reduction_single_income_limit_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_low_income_reduction_single_income_limit_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = (
        NEW_BRUNSWICK_DIR / "parameters" / "low_income_reduction_single_income_limit" / "2026.yaml"
    )
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
