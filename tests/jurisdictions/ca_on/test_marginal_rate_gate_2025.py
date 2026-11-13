"""The 2025 `ca-on/marginal_rate_gate` dataset: a two-band gate that is 0 where a tax is 0.00 and 1
where it is at least one cent.

Not a printed form figure: no CRA text is quoted. The Ontario return summary reads T1 line 42900
"Basic federal tax" and ON428 line 81 through it (two `core/amount_by_band_rate` steps), so that the
bracket-rate part of the marginal tax rate counts only where its own tax is above zero. A base of
0.00 gives the rate 0 and a base of 0.01 or more gives the rate 1. The rate is the band's `rate`,
as the health premium slope is (`ca-on/health_premium_rows`).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.jurisdictions.core.capabilities.amount_by_band_rate import AmountByBandRate

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/marginal_rate_gate"

# Made up for this test and not registered: the tax read, and the gate rate.
TAX = AmountKind("ex/tax")
GATE = AmountKind("ex/gate")


def _gate(base: str) -> Decimal:
    capability = AmountByBandRate(SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND), TAX, GATE)

    (output,) = capability.compute((Artifact(TAX, D(base)),)).outputs

    assert output.kind is GATE
    assert isinstance(output.value, Decimal)
    return output.value


def test_2025_gate_is_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == 2025


def test_2025_gate_has_two_bands_the_first_from_0() -> None:
    bands = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0


def test_2025_gate_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0.00", "0"),
        ("0", "0"),
        ("0.01", "1"),
        ("0.02", "1"),
        ("1", "1"),
        ("2706.72", "1"),
        ("14102.14", "1"),
        ("1000000", "1"),
    ],
)
def test_2025_gate_is_0_at_0_00_and_1_from_one_cent(base: str, rate: str) -> None:
    assert _gate(base) == D(rate)
