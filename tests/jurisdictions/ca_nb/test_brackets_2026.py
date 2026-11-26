"""The 2026 `ca-nb/brackets` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-nb/brackets"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text w"
    "hen CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds 52,333, 104,666 and 193,861 and rates 9.4%, 14%, 16%, 19.5% as "
    "printed in T4127 (Jan 2026) Table 8.1, New Brunswick row; tax_at_start calculated as the"
    " cumulative tax on the earlier brackets, rounded half-up to the cent (4,919.30; 12,245.9"
    "2; 26,517.12; the same method reproduces the 2025 printed line 7 constants 4,822.76, 12,"
    "005.88 and 25,997.24 from the 2025 thresholds), because the 2026 line 7 constants are no"
    "t yet published. T4127 prints the payroll constants KP 0 / 2,407 / 4,501 / 11,286, which"
    " agree with these to the dollar."
)


def test_2026_brackets_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.094"), D("0.00")),
        (D("52333.00"), D("0.14"), D("4919.30")),
        (D("104666.00"), D("0.16"), D("12245.92")),
        (D("193861.00"), D("0.195"), D("26517.12")),
    ]
    assert data.values.up_to is None


def test_2026_tax_at_start_is_the_cumulative_tax_on_the_earlier_columns() -> None:
    brackets = SOURCE.get(FAMILY, 2026, BRACKETS).values.brackets

    assert brackets[1].tax_at_start == D("4919.30")
    assert brackets[2].tax_at_start == D("12245.92")
    assert brackets[3].tax_at_start == D("26517.12")
    assert D("52333") * D("0.094") == D("4919.302")
    assert (D("104666") - D("52333")) * D("0.14") + D("4919.302") == D("12245.922")
    assert (D("193861") - D("104666")) * D("0.16") + D("12245.922") == D("26517.122")


def test_2026_brackets_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("52333.00", "0.00"),
        ("52333.01", "52333.00"),
        ("104666.00", "52333.00"),
        ("104666.01", "104666.00"),
        ("193861.00", "104666.00"),
        ("193861.01", "193861.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2026, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)


def test_2026_brackets_sources_and_year() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = NEW_BRUNSWICK_DIR / "parameters" / "brackets" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
