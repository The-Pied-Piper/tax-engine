"""The 2025 Canada workers benefit basic amount and reduction, checked against CRA's Schedule 6.

2025 Schedule 6 (form 5000-S6), Step 2: line 16 "Family working income from line 6"; line 17 "Base
amount 3,000.00"; line 18 "Line 16 minus line 17 (if negative, enter "0")"; line 19 "Rate 27%";
line 20 "Line 18 multiplied by the percentage from line 19"; line 21 "If you had an eligible
spouse or an eligible dependant, enter $2,813. If not, enter $1,633."; line 22 "Enter whichever is
less: amount from line 20 or line 21."; line 23 "Adjusted family net income from line 15"; line 24
"If you had an eligible spouse or an eligible dependant, enter $30,639. If not, enter $26,855.";
line 25 "Line 23 minus line 24 (if negative, enter "0")"; line 26 "Rate 15%"; line 27 "Line 25
multiplied by the percentage from line 26"; line 28 "Line 22 minus line 27 (if negative, enter
"0")". Lines 17 to 22 are one tier over the base amount with a maximum, and lines 24 to 27 one tier
over the threshold with none (the `surcharge_tiers` kind), once for each family status: a pair of
datasets for a filer with no eligible spouse and no eligible dependant ($1,633 and $26,855) and a
pair for a filer with one ($2,813 and $30,639). The chart's limits are not datasets: they follow
from the arithmetic, as 1,633 less 15% of (37,742 - 26,855) and 2,813 less 15% of (49,393 -
30,639) are below zero ("You did not have an eligible spouse or an eligible dependant Basic CWB:
$37,742"; "You had an eligible spouse or an eligible dependant Basic CWB: $49,393"). Lines 22
and 27 are dollars-and-cents boxes, so each tier is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.tiered_surcharge import TieredSurcharge
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASIC_FAMILY = "ca/cwb_basic"
REDUCTION_FAMILY = "ca/cwb_reduction"
BASIC_WITH_DEPENDANT_FAMILY = "ca/cwb_basic_with_dependant"
REDUCTION_WITH_DEPENDANT_FAMILY = "ca/cwb_reduction_with_dependant"
SCHEDULE_6_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"

# Made up for this test and not registered: the working income the basic amount is on (line 16),
# the basic amount (line 22), the adjusted family net income the reduction is on (line 23) and the
# reduction (line 27).
WORKING_INCOME = ArtifactKind("ex/working_income", Decimal)
BASIC = ArtifactKind("ex/basic", Decimal)
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)


def test_2025_basic_amount_is_27_percent_over_3000_at_most_1633() -> None:
    data = SOURCE.get(BASIC_FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("3000"), Rate(D("0.27")), D("1633")),))
    # Schedule 6 line 22, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_reduction_is_15_percent_over_26855() -> None:
    data = SOURCE.get(REDUCTION_FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("26855"), Rate(D("0.15"))),))
    # Schedule 6 line 27, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_basic_amount_with_a_dependant_is_27_percent_over_3000_at_most_2813() -> None:
    data = SOURCE.get(BASIC_WITH_DEPENDANT_FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("3000"), Rate(D("0.27")), D("2813")),))
    # Schedule 6 line 22, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_reduction_with_a_dependant_is_15_percent_over_30639() -> None:
    data = SOURCE.get(REDUCTION_WITH_DEPENDANT_FAMILY, 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("30639"), Rate(D("0.15"))),))
    # Schedule 6 line 27, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize(
    "family",
    [BASIC_FAMILY, REDUCTION_FAMILY, BASIC_WITH_DEPENDANT_FAMILY, REDUCTION_WITH_DEPENDANT_FAMILY],
)
def test_2025_datasets_cite_only_the_schedule_6_text(family: str) -> None:
    assert SOURCE.get(family, 2025, SURCHARGE_TIERS).sources == (SCHEDULE_6_TEXT,)


@pytest.mark.parametrize(
    ("working_income", "basic"),
    [
        # Return B: (30000 - 3000) x 27% = 7290.00, more than 1633.
        ("30000", "1633"),
        # The low-income return of the worked-return tests: (10000 - 3000) x 27% = 1890.00,
        # more than 1633.
        ("10000", "1633"),
        # Below the maximum: (8000 - 3000) x 27%, already in cents.
        ("8000", "1350.00"),
        # Returns C and A, far above it.
        ("50000", "1633"),
        ("110000", "1633"),
        # At the base amount nothing is over it; a cent above, 27% of the cent is 0.0027,
        # rounded half-up to 0.00; 27% of 1.50 is 0.405, a tie, up to 0.41.
        ("3000", "0"),
        ("3000.01", "0.00"),
        ("3001.50", "0.41"),
        ("0", "0"),
    ],
)
def test_27_percent_of_working_income_over_3000_at_most_1633(
    working_income: str, basic: str
) -> None:
    capability = TieredSurcharge(
        SOURCE.get(BASIC_FAMILY, 2025, SURCHARGE_TIERS), WORKING_INCOME, BASIC
    )

    result = capability.compute((Artifact(WORKING_INCOME, D(working_income)),))

    assert result.outputs == (Artifact(BASIC, D(basic)),)


@pytest.mark.parametrize(
    ("net_income", "reduction"),
    [
        # Return B: (29735.00 - 26855) x 15% = 2880.00 x 15%.
        ("29735.00", "432.00"),
        # Return C: (49535.00 - 26855) x 15% = 22680.00 x 15%, more than 1633.
        ("49535.00", "3402.00"),
        # The low-income return: 9935.00 is below the threshold, so line 25 is 0.
        ("9935.00", "0"),
        # Return A: (115000 - 26855) x 15%.
        ("115000", "13221.75"),
        # The chart's limit: (37742 - 26855) x 15% = 1633.05, more than the 1633 maximum.
        ("37742", "1633.05"),
        # At the threshold nothing is over it; a cent above, 15% of the cent is 0.0015, rounded
        # half-up to 0.00; 15% of 0.30 is 0.045, a tie, up to 0.05.
        ("26855", "0"),
        ("26855.01", "0.00"),
        ("26855.30", "0.05"),
        ("0", "0"),
    ],
)
def test_15_percent_of_net_income_over_26855(net_income: str, reduction: str) -> None:
    capability = TieredSurcharge(
        SOURCE.get(REDUCTION_FAMILY, 2025, SURCHARGE_TIERS), NET_INCOME, REDUCTION
    )

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(REDUCTION, D(reduction)),)


@pytest.mark.parametrize(
    ("working_income", "basic"),
    [
        # Return F: (60000 - 3000) x 27% = 15390.00, more than 2813.
        ("60000", "2813"),
        # The low-income return of the worked-return tests: (10000 - 3000) x 27% = 1890.00,
        # below 2813 though above the 1633 without an eligible dependant.
        ("10000", "1890.00"),
        ("8000", "1350.00"),
        # Either side of the maximum: 10418.52 x 27% = 2813.0004, more than 2813; 10418.51 x 27%
        # = 2812.9977, rounded half-up to 2813.00; 10418.48 x 27% = 2812.9896, to 2812.99.
        ("13418.52", "2813"),
        ("13418.51", "2813.00"),
        ("13418.48", "2812.99"),
        ("3000", "0"),
        ("3000.01", "0.00"),
        ("0", "0"),
    ],
)
def test_with_a_dependant_27_percent_of_working_income_over_3000_at_most_2813(
    working_income: str, basic: str
) -> None:
    capability = TieredSurcharge(
        SOURCE.get(BASIC_WITH_DEPENDANT_FAMILY, 2025, SURCHARGE_TIERS), WORKING_INCOME, BASIC
    )

    result = capability.compute((Artifact(WORKING_INCOME, D(working_income)),))

    assert result.outputs == (Artifact(BASIC, D(basic)),)


@pytest.mark.parametrize(
    ("net_income", "reduction"),
    [
        # Return F: (54435.00 - 30639) x 15% = 23796.00 x 15%, more than 2813.
        ("54435.00", "3569.40"),
        # Return B's net income: 29735.00 is below the threshold, so line 25 is 0.
        ("29735.00", "0"),
        # The chart's limit: (49393 - 30639) x 15% = 2813.10, more than the 2813 maximum; a
        # dollar below it, (49392 - 30639) x 15% = 2812.95, less.
        ("49393", "2813.10"),
        ("49392", "2812.95"),
        ("30639", "0"),
        ("30639.01", "0.00"),
        ("0", "0"),
    ],
)
def test_with_a_dependant_15_percent_of_net_income_over_30639(
    net_income: str, reduction: str
) -> None:
    capability = TieredSurcharge(
        SOURCE.get(REDUCTION_WITH_DEPENDANT_FAMILY, 2025, SURCHARGE_TIERS), NET_INCOME, REDUCTION
    )

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(REDUCTION, D(reduction)),)


def test_2025_disability_supplement_is_27_percent_over_1150_at_most_843() -> None:
    data = SOURCE.get("ca/cwb_disability_supplement", 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("1150"), Rate(D("0.27")), D("843")),))
    # Schedule 6 line 34, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_disability_reduction_is_15_percent_over_37740() -> None:
    data = SOURCE.get("ca/cwb_disability_reduction", 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("37740"), Rate(D("0.15"))),))
    # Schedule 6 line 39, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_disability_reduction_with_a_dependant_is_15_percent_over_49389() -> None:
    data = SOURCE.get("ca/cwb_disability_reduction_with_dependant", 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("49389"), Rate(D("0.15"))),))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_disability_reduction_with_a_dtc_spouse_is_7_point_5_percent_over_49389() -> None:
    data = SOURCE.get("ca/cwb_disability_reduction_with_dtc_spouse", 2025, SURCHARGE_TIERS)

    assert data.values == SurchargeTiers((SurchargeTier(D("49389"), Rate(D("0.075"))),))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
