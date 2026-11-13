"""The 2025 `ca-ab/marginal_rate_gate` dataset: a two-band gate that is 0 where a tax is 0.00 and
1 where it is at least one cent, Alberta's own copy of the Ontario gate (jurisdictions do not read
each other's datasets).

Not a printed form figure: no CRA text is quoted. The Alberta return summary reads T1 line 42900
"Basic federal tax" and AB428 line 68 through it (two `core/amount_by_band_rate` steps), so that the
bracket-rate part of the marginal tax rate counts only where its own tax is above zero. A base of
0.00 gives the rate 0 and a base of 0.01 or more gives the rate 1; a base exactly at the second
row's `over` (0.005) is in the lower band, so no cent amount but 0.00 is in the first band.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.jurisdictions.core.capabilities.amount_by_band_rate import AmountByBandRate
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/marginal_rate_gate"
YEAR = 2025

# Made up for this test and not registered: the tax read, and the gate rate.
TAX = AmountKind("ex/tax")
GATE = AmountKind("ex/gate")


def _gate(base: str) -> Decimal:
    capability = AmountByBandRate(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), TAX, GATE)

    (output,) = capability.compute((Artifact(TAX, D(base)),)).outputs

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
    assert bands[0].amount == 0
    assert bands[1].over == D("0.005")
    assert bands[1].minus == 0
    assert bands[1].plus == 0
    assert bands[1].rate is not None
    assert bands[1].rate.value == 1


def test_the_gate_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0.00", "0"),
        ("0", "0"),
        ("0.005", "0"),
        ("0.01", "1"),
        ("0.02", "1"),
        ("1", "1"),
        ("684.86", "1"),
        ("17680.36", "1"),
        ("1000000", "1"),
    ],
)
def test_the_gate_is_0_at_0_00_and_1_from_one_cent(base: str, rate: str) -> None:
    assert _gate(base) == D(rate)


def test_the_gate_names_a_source() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.sources
