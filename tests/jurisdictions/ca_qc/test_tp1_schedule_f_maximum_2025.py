"""The 2025 `ca-qc/tp1_schedule_f_maximum` dataset, checked against Revenu Quebec Schedule F
(TP-1.D.F-V, 2025-12), Part B, line 82.

Form text: "Maximum: $150 | Maximum: $1,000", under the columns "If $63,060 or less" and "If more
than $63,060". The take-home step reads line 77, the column's printed lower bound (18,130 or
63,060), so the band bounds put 18,130 in the first row and 63,060 in the second. The figures are
printed and kept whole; the cent rounding only gives them the scale of a dollars-and-cents box.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND, AmountByBand
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.amount_by_band import AmountFromBand
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/tp1_schedule_f_maximum"
# Made up for this test and not registered: the column's lower bound read, and the maximum.
LOWER_BOUND = AmountKind("ex/lower_bound")
MAXIMUM = AmountKind("ex/maximum")
FORM = "Revenu Quebec TP-1.D.F-V (2025-12), Schedule F, Part B"


def _bands() -> AmountByBand:
    return SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).values


def test_2025_maximums_are_150_and_1000_as_printed() -> None:
    assert [(band.over, band.amount) for band in _bands().bands] == [
        (D("0"), D("150")),
        (D("18130"), D("1000")),
    ]


def test_2025_maximums_round_half_up_to_the_cent() -> None:
    assert SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).rounding == RoundTo(
        D("0.01"), RoundingMode.HALF_UP
    )


def test_2025_maximums_cite_the_schedule() -> None:
    assert SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND).sources == (FORM,)


@pytest.mark.parametrize(("lower_bound", "maximum"), [("18130.00", "150"), ("63060.00", "1000")])
def test_each_columns_lower_bound_takes_its_own_maximum(lower_bound: str, maximum: str) -> None:
    assert _bands().band_for(D(lower_bound)).amount == D(maximum)


def test_2025_maximums_are_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == 2025


@pytest.mark.parametrize(
    ("lower_bound", "maximum"), [("18130.00", "150.00"), ("63060.00", "1000.00")]
)
def test_the_capability_gives_each_column_its_printed_maximum(
    lower_bound: str, maximum: str
) -> None:
    capability = AmountFromBand(SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND), LOWER_BOUND, MAXIMUM)

    result = capability.compute((Artifact(LOWER_BOUND, D(lower_bound)),))

    assert result.outputs == (Artifact(MAXIMUM, D(maximum)),)
    assert str(result.outputs[0].value) == maximum
