"""The 2026 `ca-nb/marginal_rate_gate` dataset: a two-band gate that is 0 where a base is 0.00 and
1 where it is at least one cent. Not a printed form figure; the New Brunswick return summary reads
the tax after credits and the low-income reduction left through it. The 2026 rows are the 2025
rows carried forward."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-nb/marginal_rate_gate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against t"
    "he 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: not a CRA figure; the two rows are the same switch every province's gate u"
    "ses and are the same in 2025 and 2026. The form is listed as a source only because the g"
    "ated figures are on it; the rows are not from it."
)


@pytest.mark.parametrize(
    ("base", "gate"),
    [
        ("0.00", "0"),
        ("0.005", "0"),
        ("0.01", "1"),
        ("1", "1"),
        ("5676.89", "1"),
    ],
)
def test_the_gate_is_0_at_0_00_and_1_from_one_cent(base: str, gate: str) -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    band = data.values.band_for(D(base))

    assert (band.amount if band.rate is None else band.rate.value) == D(gate)


def test_the_gate_names_a_source_and_the_year() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.sources == SOURCES
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    path = NEW_BRUNSWICK_DIR / "parameters" / "marginal_rate_gate" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
