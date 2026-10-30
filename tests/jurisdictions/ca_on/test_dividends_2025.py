"""The 2025 dividend gross-ups and the federal and Ontario credit rates, checked against CRA.

2025 Federal Worksheet (form 5000-D1), "Lines 12000 and 12010 - Taxable amount of dividends from
taxable Canadian corporations": "Taxable amount of dividends if you did not receive an information
slip"; line 11 "Actual amount of eligible dividends received"; line 12 "Applicable rate 138%"; line
13 "Line 11 multiplied by the percentage from line 12"; line 14 "Actual amount of dividends other
than eligible dividends received"; line 15 "Applicable rate 115%"; line 16 "Line 14 multiplied by
the percentage from line 15 Include this amount on line 12010 of your return."; line 17 "Line 13
plus line 16. Include this amount on line 12000 of your return.". "Line 40425 - Federal dividend
tax credit": "Line 6: Amount from line 12010 of your return (Note 1) Line B" "Multiplied by
9.0301%"; "Line 2: Amount A minus amount B Line C" "multiplied by 15.0198%" (printed "Line 2"
where line 7 is meant). 138% and 115% are above one, which the `rate` kind refuses, so the two
gross-ups are `fraction` datasets (138/100 and 115/100, kept as given); the two credit rates are
`rate` datasets. Lines 13 and 16 and the two credit lines (6 and 7) are dollars-and-cents boxes,
so each product is rounded half-up to the cent.

2025 Worksheet ON428 (form 5006-D), "Line 61520 - Ontario dividend tax credit": "Line 1: Amount from
line 12010 of your return Line B" "multiplied by 2.9863% ="; "Line 2: Amount A minus amount B Line C
=" "multiplied by 10% =". Both percentages are `rate` datasets and both products are
dollars-and-cents boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
ELIGIBLE_GROSS_UP = "ca/eligible_dividend_gross_up"
OTHER_GROSS_UP = "ca/other_dividend_gross_up"
OTHER_CREDIT_RATE = "ca/dividend_credit_rate_other_than_eligible"
ELIGIBLE_CREDIT_RATE = "ca/dividend_credit_rate_eligible"
FEDERAL_WORKSHEET_TEXT = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
)
ON_OTHER_CREDIT_RATE = "ca-on/dividend_credit_rate_other_than_eligible"
ON_ELIGIBLE_CREDIT_RATE = "ca-on/dividend_credit_rate_eligible"
ON428_WORKSHEET_TEXT = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the actual dividends received (Federal Worksheet lines
# 11 and 14) and their grossed-up amount (lines 13 and 16), and the amount a credit rate is
# applied to (lines B and C) and its credit.
RECEIVED = ArtifactKind("ex/received", Decimal)
GROSSED_UP = ArtifactKind("ex/grossed_up", Decimal)
BASE = ArtifactKind("ex/base", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)


def test_2025_eligible_dividend_gross_up_is_138_over_100() -> None:
    data = SOURCE.get(ELIGIBLE_GROSS_UP, 2025, FRACTION)

    assert data.values == Fraction(138, 100)
    # Worksheet line 13, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_other_dividend_gross_up_is_115_over_100() -> None:
    data = SOURCE.get(OTHER_GROSS_UP, 2025, FRACTION)

    assert data.values == Fraction(115, 100)
    # Worksheet line 16, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_credit_rate_on_dividends_other_than_eligible_is_9_0301_percent() -> None:
    data = SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.090301"))
    # Federal dividend tax credit line 6, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_credit_rate_on_eligible_dividends_is_15_0198_percent() -> None:
    data = SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.150198"))
    # Federal dividend tax credit line 7, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_the_federal_worksheet_text() -> None:
    for family in (ELIGIBLE_GROSS_UP, OTHER_GROSS_UP):
        assert FEDERAL_WORKSHEET_TEXT in SOURCE.get(family, 2025, FRACTION).sources, family
    for family in (OTHER_CREDIT_RATE, ELIGIBLE_CREDIT_RATE):
        assert FEDERAL_WORKSHEET_TEXT in SOURCE.get(family, 2025, RATE).sources, family


@pytest.mark.parametrize(
    ("received", "grossed_up"),
    [
        # The worked example (Return K): eligible dividends received of 1,000, line 13 of 1,380.00.
        ("1000", "1380"),
        ("200", "276"),
        ("0", "0"),
        # 0.30 x 138/100 = 0.414, down to 0.41.
        ("0.30", "0.41"),
        # 0.50 x 138/100 = 0.69, already in cents.
        ("0.50", "0.69"),
    ],
)
def test_eligible_dividends_are_grossed_up_by_138_percent(received: str, grossed_up: str) -> None:
    capability = ApplyFraction(SOURCE.get(ELIGIBLE_GROSS_UP, 2025, FRACTION), RECEIVED, GROSSED_UP)

    result = capability.compute((Artifact(RECEIVED, D(received)),))

    assert result.outputs == (Artifact(GROSSED_UP, D(grossed_up)),)


@pytest.mark.parametrize(
    ("received", "grossed_up"),
    [
        # The worked example (Return K): dividends other than eligible of 500, line 16 of 575.00.
        ("500", "575"),
        ("1000", "1150"),
        ("0", "0"),
        # Rounded half-up to the cent: 0.30 x 115/100 is 0.345, a tie, up to 0.35.
        ("0.30", "0.35"),
        # 0.10 x 115/100 = 0.115, a tie, up to 0.12.
        ("0.10", "0.12"),
    ],
)
def test_other_dividends_are_grossed_up_by_115_percent(received: str, grossed_up: str) -> None:
    capability = ApplyFraction(SOURCE.get(OTHER_GROSS_UP, 2025, FRACTION), RECEIVED, GROSSED_UP)

    result = capability.compute((Artifact(RECEIVED, D(received)),))

    assert result.outputs == (Artifact(GROSSED_UP, D(grossed_up)),)


@pytest.mark.parametrize(
    ("base", "credit"),
    [
        # The worked example (Return K): line B of 575.00 x 9.0301% = 51.923075.
        ("575", "51.92"),
        ("0", "0"),
        # Rounded half-up to the cent: 5000 x 9.0301% is 451.505, a tie, up to 451.51.
        ("5000", "451.51"),
    ],
)
def test_the_credit_on_dividends_other_than_eligible_is_9_0301_percent(
    base: str, credit: str
) -> None:
    capability = ApplyRate(SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE), BASE, CREDIT)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


@pytest.mark.parametrize(
    ("base", "credit"),
    [
        # The worked example (Return K): line C of 1,380.00 x 15.0198% = 207.27324.
        ("1380", "207.27"),
        ("0", "0"),
        # Rounded half-up to the cent: 7500 x 15.0198% is 1126.485, a tie, up to 1126.49.
        ("7500", "1126.49"),
    ],
)
def test_the_credit_on_eligible_dividends_is_15_0198_percent(base: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE), BASE, CREDIT)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


def test_2025_ontario_credit_rate_on_dividends_other_than_eligible_is_2_9863_percent() -> None:
    data = SOURCE.get(ON_OTHER_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.029863"))
    # Worksheet ON428 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_credit_rate_on_eligible_dividends_is_10_percent() -> None:
    data = SOURCE.get(ON_ELIGIBLE_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.1"))
    # Worksheet ON428 line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ontario_datasets_cite_the_on428_worksheet_text() -> None:
    for family in (ON_OTHER_CREDIT_RATE, ON_ELIGIBLE_CREDIT_RATE):
        assert ON428_WORKSHEET_TEXT in SOURCE.get(family, 2025, RATE).sources, family


@pytest.mark.parametrize(
    ("base", "credit"),
    [
        # The worked example (Return K): line B of 775.00 x 2.9863% = 23.143825.
        ("775", "23.14"),
        # The no-slip example: line B of 575.00 x 2.9863% = 17.171225.
        ("575", "17.17"),
        ("0", "0"),
        # Rounded half-up to the cent: 5000 x 2.9863% is 149.315, a tie, up to 149.32.
        ("5000", "149.32"),
    ],
)
def test_the_ontario_credit_on_dividends_other_than_eligible_is_2_9863_percent(
    base: str, credit: str
) -> None:
    capability = ApplyRate(SOURCE.get(ON_OTHER_CREDIT_RATE, 2025, RATE), BASE, CREDIT)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)


@pytest.mark.parametrize(
    ("base", "credit"),
    [
        # The worked example (Return K): line C of 1,680.00 x 10% = 168.00.
        ("1680", "168.00"),
        # The no-slip example: line C of 1,380.00 x 10% = 138.00.
        ("1380", "138"),
        ("0", "0"),
        # Rounded half-up to the cent: 0.05 x 10% is 0.005, a tie, up to 0.01.
        ("0.05", "0.01"),
    ],
)
def test_the_ontario_credit_on_eligible_dividends_is_10_percent(base: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(ON_ELIGIBLE_CREDIT_RATE, 2025, RATE), BASE, CREDIT)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)
