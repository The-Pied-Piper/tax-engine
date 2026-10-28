"""The 2025 federal logging tax credit rates of Schedule 5 of the General Income Tax and Benefit
Guide, against CRA's guide.

5000-G 2025, "Federal logging tax credit": "To calculate your credit for each province where you
operated, use the lower of the following amounts for each province you had a logging operation in:
66.6667% of the logging tax that you paid to that province for the year; 6.6667% of your net
logging income in that province for the year." The first percentage is the `logging_tax_rate`
dataset, 0.666667 (the rate of the logging tax paid); the second is the `logging_income_rate`
dataset, 0.066667 (the rate of the net logging income, and the rate of the cap of line 133, which
is also 6.6667% of taxable income). Each is a rate (the `rate` kind), and each product rounds
half-up to the cent, as every dollars-and-cents box on the forms is: the guide states no rounding
rule, so that is the owner's decision. The guide is published as text, so the datasets cite it.

The datasets are tested as rates on their own; the lines together, from the province records to
line 133, are in the capability and `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
GUIDE_5000_G = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# (dataset, the rate the guide prints)
RATES: tuple[tuple[str, str], ...] = (
    ("ca/logging_tax_rate", "0.666667"),
    ("ca/logging_income_rate", "0.066667"),
)


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_is_the_percentage_the_guide_prints(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(rate))


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_rounds_half_up_to_the_cent(family: str, rate: str) -> None:
    # The guide states no rounding rule; each credit is a dollars-and-cents amount, so the product
    # rounds half-up to the cent, the owner's decision.
    data = SOURCE.get(family, 2025, RATE)

    assert data.rounding == CENT


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_cites_the_5000_g_guide(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert GUIDE_5000_G in data.sources


def test_the_two_rates_are_not_the_same_dataset() -> None:
    # The tax side is 66.6667% and the income side 6.6667%: a tenth of the first, not one figure.
    tax = SOURCE.get("ca/logging_tax_rate", 2025, RATE).values
    income = SOURCE.get("ca/logging_income_rate", 2025, RATE).values

    assert tax != income
    assert tax.value == D("0.666667")
    assert income.value == D("0.066667")
