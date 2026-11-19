"""The 2026 `ca-nl/low_income_reduction_line_86_gate` dataset, provisional.

Pins the 2026 rows, rounding, sources, tax year and the two header comment lines of the file. The
2026 file carries the 2025 rows forward (an absent year is never carried forward).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_reduction_line_86_gate"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is not yet "
    "published."
)


def test_2026_line_86_gate_rows() -> None:
    bands = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].amount == 1
    assert bands[1].over == D("0.005")
    assert bands[1].amount == 0


def test_2026_line_86_gate_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.rounding.apply(D("0.123")) == D("0.123")


def test_2026_line_86_gate_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.sources == SOURCES


def test_2026_line_86_gate_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "low_income_reduction_line_86_gate" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
