"""The 2026 `ca-nl/low_income_reduction_maximum` dataset, provisional.

Pins the 2026 figures, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
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
FAMILY = "ca-nl/low_income_reduction_maximum"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be c"
    "onfirmed against the 2026 form text when CRA publishes it."
)


def _file(year: int) -> Path:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    return root / "parameters" / FAMILY.split("/")[1] / f"{year}.yaml"


def test_2026_low_income_reduction_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("1571"))
    assert data.tax_year == 2026
    assert data.rounding == SOURCE.get(FAMILY, 2025, AMOUNT).rounding


def test_2026_low_income_reduction_maximum_sources() -> None:
    assert SOURCE.get(FAMILY, 2026, AMOUNT).sources == SOURCES


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file(2026).read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_file_sits_beside_the_2025_file() -> None:
    assert _file(2025).is_file()
    assert _file(2026).is_file()
