"""The 2025 Work Chart 414 datasets, taken from Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart 414
(tax credit for contributions to authorized Québec political parties).

Form text: line 1 "Contributions to authorized Québec municipal political parties (maximum
$200)"; line 2 "Enter the amount from line 1 or $50, whichever is less." x 85% = 10; line 3
"Subtract line 2 from line 1." x 75% = 11; line 14 "Add lines 10 and 11. Carry the result to line
414 of your return (maximum $155)."

Each printed figure is a dataset held as printed: the three maximums (200, 50 and 155) the `amount`
kind, the two percentages (85% and 75%) the `rate` kind as fractions. Every line is a
dollars-and-cents line, so each rounds half-up to the cent, the project's choice, as the form states
no rounding rule. The capabilities that apply them are tested with the lines that use them.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
SOURCE_FORM = "Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart 414"
AMOUNTS = {
    "ca-qc/work_chart_414_line_1_maximum": D("200"),
    "ca-qc/work_chart_414_line_2_limit": D("50"),
    "ca-qc/work_chart_414_line_14_maximum": D("155"),
}
RATES = {
    "ca-qc/work_chart_414_line_10_rate": D("0.85"),
    "ca-qc/work_chart_414_line_11_rate": D("0.75"),
}
HALF_UP_CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize("family", list(AMOUNTS))
def test_2025_amount_is_the_printed_figure(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT)

    assert data.values == Amount(value=AMOUNTS[family])
    assert data.rounding == HALF_UP_CENT
    assert data.sources == (SOURCE_FORM,)


@pytest.mark.parametrize("family", list(RATES))
def test_2025_rate_is_the_printed_percentage_as_a_fraction(family: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(RATES[family])
    assert data.rounding == HALF_UP_CENT
    assert data.sources == (SOURCE_FORM,)
