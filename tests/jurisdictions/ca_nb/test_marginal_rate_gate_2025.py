"""The 2025 `ca-nb/marginal_rate_gate` dataset: a two-band gate that is 0 where a base is 0.00 and
1 where it is at least one cent. Not a printed form figure; the New Brunswick return summary reads
the tax after credits and the low-income reduction left through it. The 2026 file carries these
rows forward."""

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
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-nb/marginal_rate_gate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt",)


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
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    band = data.values.band_for(D(base))

    assert (band.amount if band.rate is None else band.rate.value) == D(gate)


def test_the_gate_names_a_source() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.sources == SOURCES


def test_the_gate_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.tax_year == 2025


def test_the_gate_has_two_rows_a_flat_zero_and_a_slope_of_one() -> None:
    bands = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values.bands

    assert [(b.over, b.amount, b.rate, b.minus, b.plus) for b in bands] == [
        (D("0"), D("0"), None, None, None),
        (D("0.005"), None, Rate(D("1")), D("0"), D("0")),
    ]


def test_the_gate_has_no_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.rounding == NO_ROUNDING
