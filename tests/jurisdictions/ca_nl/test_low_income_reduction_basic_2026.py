"""The 2026 `ca-nl/low_income_reduction_basic` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_reduction_basic"
SOURCES = (
    "https://www.assembly.nl.ca/Legislation/sr/regulations/rc260018.htm",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
)
CONFIRMED_HEADER = (
    "# Confirmed from the regulation named in the next line; the 2026 NL428 is not yet published."
)
SOURCE_HEADER = (
    "# Source: Newfoundland and Labrador Regulation 18/26, Low Income Tax Reduction "
    "Regulations for the 2025 and 2026 Taxation Years (filed May 14, 2026; "
    'https://www.assembly.nl.ca/Legislation/sr/regulations/rc260018.htm), s.3(b)(i): "the '
    'amount referred to in paragraph 21.1(2.1)(a) of the Act is $842" for the 2026 taxation '
    "year, in force January 1, 2026 (s.5(2)); taken as printed, not indexed."
)


def test_2026_low_income_reduction_basic_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("842"))


def test_2026_low_income_reduction_basic_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_low_income_reduction_basic_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_low_income_reduction_basic_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_confirmed_and_states_its_source() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "low_income_reduction_basic" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == CONFIRMED_HEADER
    assert lines[1] == SOURCE_HEADER


def test_2025_low_income_reduction_basic_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("997"))
    assert data.sources != SOURCES
