"""The 2025 `ca-nl/low_income_reduction_dependant_gate` dataset: a two-band switch giving 0 where
NL428 line 23 (the amount claimed on line 58160) is 0.00 and the printed 557 where it is at least
one cent (NL428 line 97, 5001-C 2025: "Reduction for an eligible dependant claimed on line 58160
Claim $557").

Only the 557 is a printed form figure; the rows are a switch. A base of 0.00 gives 0 and a base of
0.01 or more gives 557; a base exactly at the second row's `over` (0.005) is in the lower band, so
no cent amount but 0.00 is in the first band.
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
FAMILY = "ca-nl/low_income_reduction_dependant_gate"
YEAR = 2025

# Made up for this test and not registered: the amount claimed, and the reduction.
CLAIMED = AmountKind("ex/claimed")
REDUCTION = AmountKind("ex/reduction")


def _reduction(base: str) -> Decimal:
    capability = AmountFromBand(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), CLAIMED, REDUCTION)

    (output,) = capability.compute((Artifact(CLAIMED, D(base)),)).outputs

    assert output.kind is REDUCTION
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
    assert bands[1].amount == 557


@pytest.mark.parametrize(
    ("base", "expected"),
    [("0.00", "0"), ("0.01", "557"), ("9043.00", "557")],
)
def test_the_gate_gives_0_at_nothing_claimed_and_557_from_one_cent(
    base: str, expected: str
) -> None:
    assert _reduction(base) == D(expected)
