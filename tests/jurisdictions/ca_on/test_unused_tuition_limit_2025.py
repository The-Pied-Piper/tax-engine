"""The 2025 Ontario unused tuition limit, checked against CRA's Schedule ON(S11).

2025 Schedule ON(S11) (form 5006-S11), line 2 "Enter the amount from line 26000 of your return on
line 2 if it is $52,886 or less. If it is more than $52,886, enter the result of the following
calculation:" "Line 2: Amount from line 8 of your Form ON428" "divided by 5.05% =". So the taxable
income passes through at or below $52,886 (an amount equal to the threshold passes), and over it the
Ontario tax on taxable income (ON428 line 8) is divided by 5.05%. The form states no rounding rule
for line 2; the quotient is rounded half-up to the cent, as every dollars-and-cents box is.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
FAMILY = "ca-on/unused_tuition_limit"
S11_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-s11/5006-s11-25e.txt"

# Made up for this test and not registered: the taxable income the limit is tested on, the Ontario
# tax it is divided by, and the figure the capability produces.
TAXABLE_INCOME = ArtifactKind("ex/taxable_income", Decimal)
ONTARIO_TAX = ArtifactKind("ex/ontario_tax", Decimal)
INCOME_CAP = ArtifactKind("ex/income_cap", Decimal)


def test_2025_limit_is_the_52886_threshold_and_the_5_05_percent_rate() -> None:
    data = SOURCE.get(FAMILY, 2025, THRESHOLD_RATE)

    assert data.values == ThresholdRate(Rate(D("0.0505")), D("52886"))
    # S11 line 2, a dollars-and-cents quotient: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_limit_cites_only_the_schedule_on_s11_text() -> None:
    data = SOURCE.get(FAMILY, 2025, THRESHOLD_RATE)

    assert data.sources == (S11_TEXT,)


@pytest.mark.parametrize(
    ("taxable_income", "ontario_tax", "income_cap"),
    [
        # "$52,886 or less": the taxable income passes through, whatever the Ontario tax is.
        ("50000", "2000.00", "50000"),
        ("0", "0", "0"),
        # At the threshold, the amount passes through ("or less").
        ("52886", "2670.74", "52886"),
        # A cent over, the Ontario tax is divided by 5.05%: 2670.74 x 2000 / 101 = 52885.9406,
        # rounded half-up to 52885.94.
        ("52886.01", "2670.74", "52885.94"),
        # Schedule ON(S11) example: the Ontario tax of 3,269.97 (ON428 line 8) divided by 5.05%,
        # 3269.97 x 2000 / 101 = 64751.8812, rounded to 64751.88; the taxable income is not used.
        ("59435", "3269.97", "64751.88"),
        # 3321.67 x 2000 / 101 = 65775.6436, rounded to 65775.64 (taxable income 60000).
        ("60000", "3321.67", "65775.64"),
    ],
)
def test_the_income_cap_is_the_taxable_income_or_the_ontario_tax_over_the_rate(
    taxable_income: str, ontario_tax: str, income_cap: str
) -> None:
    capability = AmountOrDividedByRate(
        SOURCE.get(FAMILY, 2025, THRESHOLD_RATE), TAXABLE_INCOME, ONTARIO_TAX, INCOME_CAP
    )

    result = capability.compute(
        (Artifact(TAXABLE_INCOME, D(taxable_income)), Artifact(ONTARIO_TAX, D(ontario_tax)))
    )

    assert result.outputs == (Artifact(INCOME_CAP, D(income_cap)),)
