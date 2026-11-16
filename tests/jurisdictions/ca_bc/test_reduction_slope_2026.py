"""The 2026 `ca-bc/reduction_slope` dataset: a two-band chart that is 0 where BC428 line 78 is 0.00
and the printed 3.56% from one cent, read with no rounding.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 77: Applicable rate 3.56%" and "Line 78: Line 76
multiplied by the percentage from line 77". The return summary reads line 78 through this chart
(`core/amount_by_band_rate`), so that the slope of the tax reduction counts in the marginal tax rate
only above a net income of 25,020.00 (where line 76, and so line 78, is above zero). The rate is the
same printed 3.56% as `ca-bc/tax_reduction_rate`, which rounds half-up to the cent (a rate of 0.0356
would read 0.04), so the chart carries it with `rounding: none`. A base of 0.00 gives 0 and a base
of 0.01 or more gives 0.0356; a base exactly at the second row's `over` (0.005) is in the lower
band.
The 2026 file carries the 2025 rows forward (the British Columbia manifest runs 2026 on the same
steps, and an absent year is never carried forward)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.core.capabilities.amount_by_band_rate import AmountByBandRate
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/reduction_slope"
YEAR = 2026
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)

# Made up for this test and not registered: the tax read, and the slope.
TAX = AmountKind("ex/tax")
SLOPE = AmountKind("ex/slope")


def _slope(base: str) -> Decimal:
    capability = AmountByBandRate(SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND), TAX, SLOPE)

    (output,) = capability.compute((Artifact(TAX, D(base)),)).outputs

    assert output.kind is SLOPE
    assert isinstance(output.value, Decimal)
    return output.value


def test_the_chart_is_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == YEAR


def test_the_chart_has_two_bands_the_first_from_0_and_the_second_above_half_a_cent() -> None:
    bands = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values.bands

    assert len(bands) == 2
    assert bands[0].over == 0
    assert bands[0].amount == 0
    assert bands[1].over == D("0.005")
    assert bands[1].minus == 0
    assert bands[1].plus == 0
    assert bands[1].rate is not None
    assert bands[1].rate.value == D("0.0356")


def test_the_chart_band_for_0_is_not_the_band_for_one_cent() -> None:
    values = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).values

    assert values.band_for(D("0.00")) is values.bands[0]
    assert values.band_for(D("0.01")) is values.bands[1]


@pytest.mark.parametrize(
    ("base", "rate"),
    [
        ("0.00", "0"),
        ("0", "0"),
        ("0.005", "0"),
        ("0.01", "0.0356"),
        ("0.02", "0.0356"),
        ("1", "0.0356"),
        ("561.99", "0.0356"),
        ("1577.61", "0.0356"),
        ("1000000", "0.0356"),
    ],
)
def test_the_slope_is_0_at_0_00_and_0_0356_from_one_cent(base: str, rate: str) -> None:
    assert _slope(base) == D(rate)


def test_the_chart_rounds_nothing() -> None:
    assert SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND).rounding == NO_ROUNDING


def test_the_chart_names_a_source() -> None:
    data = SOURCE.get(FAMILY, YEAR, AMOUNT_BY_BAND)

    assert data.sources


def test_the_chart_has_the_same_rows_and_sources_as_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, AMOUNT_BY_BAND)
    original = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert carried.values == original.values
    assert carried.sources == original.sources


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / "reduction_slope" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_provisional_line_is_the_one_of_the_ontario_2026_files() -> None:
    british_columbia = british_columbia_packages().roots()[Namespace("ca-bc")]
    ontario = Path(tax_engine.jurisdictions.ca_on.__file__).parent
    british_columbia_first = (
        (british_columbia / "parameters" / "reduction_slope" / "2026.yaml")
        .read_text()
        .splitlines()[0]
    )
    ontario_first = (
        (ontario / "parameters" / "marginal_rate_gate" / "2026.yaml").read_text().splitlines()[0]
    )

    assert british_columbia_first == ontario_first
