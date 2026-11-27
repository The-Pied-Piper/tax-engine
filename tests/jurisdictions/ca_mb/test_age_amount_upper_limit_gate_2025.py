"""The 2025 `ca-mb/age_amount_upper_limit_gate` dataset: a two-band gate, 0 where its
base is 0.00 and 1 where it is at least one cent. Not a printed form figure; the base is the limit
of $52,602 minus net income (Worksheet MB428 age amount line 2), not below 0, so the gate is 1
exactly when net income is below the limit."""

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
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace

D = Decimal
MANITOBA_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_mb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-mb"): MANITOBA_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-mb/age_amount_upper_limit_gate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt",)


@pytest.mark.parametrize(
    ("base", "gate"),
    [
        ("0.00", "0"),
        ("0.005", "0"),
        ("0.01", "1"),
        ("1", "1"),
        ("52602", "1"),
    ],
)
def test_the_gate_is_0_at_0_00_and_1_from_one_cent(base: str, gate: str) -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    band = data.values.band_for(D(base))

    assert band.amount == D(gate)


def test_the_gate_names_a_source() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.sources == SOURCES


def test_the_gate_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.tax_year == 2025


def test_the_gate_has_two_flat_rows_zero_then_one() -> None:
    bands = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values.bands

    assert [(b.over, b.amount, b.rate, b.minus, b.plus) for b in bands] == [
        (D("0"), D("0"), None, None, None),
        (D("0.005"), D("1"), None, None, None),
    ]


def test_the_gate_has_no_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.rounding == NO_ROUNDING
