"""The 2025 `ca-nl/low_income_reduction_dependant_gate`: 0 at 0.00 and 557 from one cent (NL428
line 97, 5001-C 2025). A switch, not a printed table; the 557 is the printed figure."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_reduction_dependant_gate"


def test_2025_gate_gives_0_at_zero_and_557_from_one_cent() -> None:
    table = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values

    assert table.band_for(D("0.00")).amount_at(D("0.00")) == D("0")
    assert table.band_for(D("0.01")).amount_at(D("0.01")) == D("557")
    assert table.band_for(D("9043")).amount_at(D("9043")) == D("557")
