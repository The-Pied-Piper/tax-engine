"""The 2025 `ca-on/health_premium_rows` dataset: every printed row of ON428 line 89, checked against
CRA's form.

2025 ON428 (form 5006-C), line 89 "Ontario health premium (complete the chart below)"; the chart's
line 1 is "Enter your taxable income from line 26000 of your return", and by taxable income:
$20,000 or less: $0; more than $20,000 but not more than $25,000: (taxable income minus $20,000) x
6%; more than $25,000 but not more than $36,000: $300; more than $36,000 but not more than $38,500:
(taxable income minus $36,000) x 6% plus $300; more than $38,500 but not more than $48,000: $450;
more than $48,000 but not more than $48,600: (taxable income minus $48,000) x 25% plus $450; more
than $48,600 but not more than $72,000: $600; more than $72,000 but not more than $72,600: (taxable
income minus $72,000) x 25% plus $600; more than $72,600 but not more than $200,000: $750; more than
$200,000 but not more than $200,600: (taxable income minus $200,000) x 25% plus $750; more than
$200,600: $900.

The rows are the chart as printed: each row is a flat `amount` or a sloped `minus`, `rate`, `plus`,
never a tier with a maximum. Line 89 is a dollars-and-cents box, so the output rounds half-up to
the cent. The figures below are the chart's, and the ticket's worked figures (line 89 at taxable
income 19,835.00, 69,335.00 and 148,926.00) are among them.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from tax_engine.domain.parameters.amount_by_band import (
    AMOUNT_BY_BAND,
    AmountBand,
    AmountByBand,
)
from tax_engine.jurisdictions.core.capabilities.amount_by_band import AmountFromBand

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/health_premium_rows"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the taxable income the premium is on, and the premium.
INCOME = AmountKind("ex/income")
PREMIUM = AmountKind("ex/premium")


def test_2025_rows_are_the_chart_rows_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.values == AmountByBand(
        (
            # $20,000 or less: $0.
            AmountBand(D("0"), amount=D("0")),
            # More than $20,000 but not more than $25,000: (income - $20,000) x 6%.
            AmountBand(D("20000"), minus=D("20000"), rate=Rate(D("0.06")), plus=D("0")),
            # More than $25,000 but not more than $36,000: $300.
            AmountBand(D("25000"), amount=D("300")),
            # More than $36,000 but not more than $38,500: (income - $36,000) x 6% + $300.
            AmountBand(D("36000"), minus=D("36000"), rate=Rate(D("0.06")), plus=D("300")),
            # More than $38,500 but not more than $48,000: $450.
            AmountBand(D("38500"), amount=D("450")),
            # More than $48,000 but not more than $48,600: (income - $48,000) x 25% + $450.
            AmountBand(D("48000"), minus=D("48000"), rate=Rate(D("0.25")), plus=D("450")),
            # More than $48,600 but not more than $72,000: $600.
            AmountBand(D("48600"), amount=D("600")),
            # More than $72,000 but not more than $72,600: (income - $72,000) x 25% + $600.
            AmountBand(D("72000"), minus=D("72000"), rate=Rate(D("0.25")), plus=D("600")),
            # More than $72,600 but not more than $200,000: $750.
            AmountBand(D("72600"), amount=D("750")),
            # More than $200,000 but not more than $200,600: (income - $200,000) x 25% + $750.
            AmountBand(D("200000"), minus=D("200000"), rate=Rate(D("0.25")), plus=D("750")),
            # More than $200,600: $900.
            AmountBand(D("200600"), amount=D("900")),
        )
    )


def test_2025_rows_round_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    # ON428 line 89 is a dollars-and-cents box.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rows_cite_only_the_on428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.sources == (ON428_TEXT,)


def test_2025_rows_are_the_amount_by_band_kind() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND)

    assert data.kind is AMOUNT_BY_BAND
    assert data.family == FAMILY
    assert data.tax_year == 2025


@pytest.mark.parametrize(
    ("income", "premium"),
    [
        # The ticket's worked figures: taxable income 19,835.00, 69,335.00 and 148,926.00.
        ("19835.00", "0.00"),
        ("69335.00", "600.00"),
        ("148926.00", "750"),
        # "$20,000 or less": $0, at the boundary and below it.
        ("0", "0"),
        ("1", "0"),
        ("20000", "0"),
        # A cent over: (20000.01 - 20000) x 6% = 0.0006, rounded half-up to 0.00.
        ("20000.01", "0.00"),
        # (20000.25 - 20000) x 6% = 0.015, a tie: up to 0.02.
        ("20000.25", "0.02"),
        # (20000.75 - 20000) x 6% = 0.045, a tie: up to 0.05.
        ("20000.75", "0.05"),
        # Inside the first sloped row: (22000 - 20000) x 6% = 120.
        ("22000", "120"),
        # At the row's top, (25000 - 20000) x 6% = 300, the same as the $300 row above it.
        ("25000", "300.00"),
        ("25001", "300"),
        ("30000", "300"),
        ("36000", "300"),
        # (37000 - 36000) x 6% + 300 = 360; at 38500, 150 + 300 = 450.
        ("37000", "360"),
        ("38500", "450"),
        ("40000", "450"),
        ("48000", "450"),
        # (48300 - 48000) x 25% + 450 = 525; at 48600, 150 + 450 = 600.
        ("48300", "525"),
        ("48600", "600"),
        ("49535", "600"),
        ("69335", "600"),
        ("72000", "600"),
        # (72300 - 72000) x 25% + 600 = 675; at 72600, 150 + 600 = 750.
        ("72300", "675"),
        ("72600", "750"),
        ("115000", "750"),
        ("200000", "750"),
        # (200300 - 200000) x 25% + 750 = 825; at 200600 and above, $900.
        ("200300", "825"),
        ("200600", "900"),
        ("1000000", "900"),
    ],
)
def test_charges_the_chart_premium_on_taxable_income(income: str, premium: str) -> None:
    capability = AmountFromBand(SOURCE.get(FAMILY, 2025, AMOUNT_BY_BAND), INCOME, PREMIUM)

    result = capability.compute((Artifact(INCOME, D(income)),))

    assert result.outputs == (Artifact(PREMIUM, D(premium)),)
