"""The 2025 `ca-nl/low_income_reduction_line_86_gate` dataset: a two-band switch giving 1 where
NL428 line 86 is 0.00 and 0 where an amount is claimed on it (NL428 under line 87, 5001-C 2025: "If
you are claiming an amount on line 86, enter the amount from line 87 on line 94, enter "0" on line
104, and continue on line 105.").

No figure is printed on the form; the rows are a switch. A base of 0.00 gives 1 and a base of 0.01
or more gives 0; a base exactly at the second row's `over` (0.005) is in the lower band, so no cent
amount but 0.00 is in the first band.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.jurisdictions.core.capabilities.amount_by_band import AmountFromBand
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_reduction_line_86_gate"
YEAR = 2025

# Made up for this test and not registered: the amount claimed, and the gate.
CLAIMED = AmountKind("ex/claimed")
GATE = AmountKind("ex/gate")


def _gate(base: str) -> Decimal:
    capability = AmountFromBand(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), CLAIMED, GATE)

    (output,) = capability.compute((Artifact(CLAIMED, D(base)),)).outputs

    assert output.kind is GATE
    assert isinstance(output.value, Decimal)
    return output.value


def test_the_gate_is_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR


def test_the_gate_has_two_bands_the_first_from_0_and_the_second_above_half_a_cent() -> None:
    bands = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0
    assert bands[0].amount == 1
    assert bands[1].over == D("0.005")
    assert bands[1].amount == 0


@pytest.mark.parametrize(
    ("base", "expected"),
    [("0", "1"), ("0.00", "1"), ("0.005", "1"), ("0.01", "0"), ("5000.00", "0")],
)
def test_the_gate_gives_1_at_nothing_claimed_and_0_from_one_cent(base: str, expected: str) -> None:
    assert _gate(base) == D(expected)


def test_the_gate_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.005")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


def test_the_gate_names_the_form_as_its_source() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.sources
