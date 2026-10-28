"""The 2025 datasets of Form RC381, checked against CRA's form.

Form RC381 (2025), "Inter-Provincial Calculation for CPP and QPP Contributions and
Overpayments" (`docs/cra-forms-2025/rc381-25e.pdf`; no .txt is published). Part 2: the "Monthly
proration for 2025" table, "Enter the corresponding amounts from the monthly proration table
above using the number of months from lines A and B.", lines G to J for the QPP. Part 3: "Line
4 divided by line 5 (calculated to the fifth decimal place without rounding)" (line 6); "Amount
from line E of Part 2 multiplied by the rate at line 6" (lines 7 to 10); "amount from line 19 x
83.1933%" (line 20); "amount from line 18 x 4.95% = (maximum $3,356.10)" (line 22), "amount from
line 18 x 1% = (maximum $678.00)" (line 23) and "amount from line 15 x 4% = (maximum
$396.00)" (line 26). The QPP side of Part 3: "amount from line 39 x 84.375%" (line 40),
"amount from line 38 x 5.4% = (maximum $3,661.20)" (line 42), "amount from line 38 x 1% =
(maximum $678.00)" (line 43) and "amount from line 35 x 4% = (maximum $396.00)" (line 46). Part 4:
"Amount from line 26 × 16.80672 = 27" (line 27), the CPP contributions grossed up to the
self-employed rate (twice the employee's 4.95% and 1%, 1 / 0.0595 to five decimal places), and
"Amount from line 40 × 15.625 = 41" (line 41), the QPP contributions grossed up the same way
(1 / 0.064, which is exactly 15.625: the QPP rate of 5.4% and 1% is 6.4%), "Amount from line 56 ÷
4% =" (line 76), "amount from line 70 × 9.9% = (maximum $6,712.20)" (line 84), "amount from line
70 × 2% = (maximum $1,356.00)" (line 85), "amount from line 83 × 8% = (maximum $792.00)" (line
86), "Amount from line 69 of Part 3 (if positive) × 2 = 89" (line 89) and "amount from line 90
entered as a positive amount × 50% = 91" (line 91).

The form prints no "upper" of its own for lines 22, 23, 26, 42, 43 and 46: the tiers run from 0
to the maximum the printed maximum implies (67,800.00 at 4.95%, 5.4% and 1% and 9,900.00 at 4%).
Lines 43 and 46 print the same rate and maximum as lines 23 and 26, so they read the same
datasets. Lines 84, 85 and 86 print the figures of Schedule 8 Part 4's lines 10, 11 and 12 (9.9%
up to $6,712.20, 2% up to $1,356.00, 8% up to $792.00, on earnings that are already net of the
basic exemption), and line 91 the 50% of its line 15, so they read those datasets
(`cpp_self_employed_*`). Lines 111, 112 and 125 print "× 50%" as line 91 does, so they read the
same dataset (`test_part_4_line_91_is_50_percent_of_line_90_to_the_cent` pins it, with a tie), and
line 116 prints "× 83.1933%", the rate of line 20, so it reads that dataset
(`test_line_20_is_83_1933_percent_of_line_19`); no dataset is added for lines 111 to 129 or for
the final selection.

The dataset of each line is checked with the rounding rule or the capability that reads it, on
made-up kinds; the lines together are in the `end_to_end` tests and
`returns/2025_return_bo.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from fractions import Fraction as ExactFraction
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.contribution_tier import TieredContribution
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT
from tax_calculator.domain.parameters.contribution_tier import CONTRIBUTION_TIER, ContributionTier
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FIVE_DECIMALS_DOWN = RoundTo(D("0.00001"), RoundingMode.DOWN)
RC381_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/rc381/rc381-25e.pdf"

RATIO_TRUNCATION = "ca/rc381_ratio_truncation"
CENTS_ROUNDING = "ca/rc381_cents_rounding"
CPP_BASE_SHARE_RATE = "ca/rc381_cpp_base_share_rate"
REQUIRED_CPP_BASE = "ca/rc381_required_cpp_base"
REQUIRED_FIRST_ADDITIONAL = "ca/rc381_required_first_additional"
REQUIRED_SECOND_ADDITIONAL = "ca/rc381_required_second_additional"
QPP_BASE_SHARE_RATE = "ca/rc381_qpp_base_share_rate"
REQUIRED_QPP_BASE = "ca/rc381_required_qpp_base"
CPP_GROSS_UP_FRACTION = "ca/rc381_cpp_gross_up_fraction"
QPP_GROSS_UP_FRACTION = "ca/rc381_qpp_gross_up_fraction"
SECOND_ADDITIONAL_RATE = "ca/rc381_second_additional_rate"
DOUBLE_FRACTION = "ca/rc381_double_fraction"
# Schedule 8 Part 4's datasets, read by lines 84, 85, 86 and 91 of this form's Part 4.
SELF_EMPLOYED_BASE = "ca/cpp_self_employed_base_contribution"
SELF_EMPLOYED_FIRST_ADDITIONAL = "ca/cpp_self_employed_first_additional_contribution"
SELF_EMPLOYED_SECOND_ADDITIONAL = "ca/cpp_self_employed_second_additional_contribution"
SELF_EMPLOYED_CREDIT_RATE = "ca/cpp_self_employed_base_credit_rate"

# Made up for this test and not registered.
EARNINGS = ArtifactKind("ex/earnings", Decimal)
CONTRIBUTION = ArtifactKind("ex/contribution", Decimal)

# Part 2's "Monthly proration for 2025" table as printed, by number of months: maximum
# pensionable earnings, maximum amount subject to second additional contributions, additional
# maximum pensionable earnings and maximum basic exemption.
PRORATION_TABLE = {
    1: ("5941.67", "825.00", "6766.67", "291.67"),
    2: ("11883.33", "1650.00", "13533.33", "583.33"),
    3: ("17825.00", "2475.00", "20300.00", "875.00"),
    4: ("23766.67", "3300.00", "27066.67", "1166.67"),
    5: ("29708.33", "4125.00", "33833.33", "1458.33"),
    6: ("35650.00", "4950.00", "40600.00", "1750.00"),
    7: ("41591.67", "5775.00", "47366.67", "2041.67"),
    8: ("47533.33", "6600.00", "54133.33", "2333.33"),
    9: ("53475.00", "7425.00", "60900.00", "2625.00"),
    10: ("59416.67", "8250.00", "67666.67", "2916.67"),
    11: ("65358.33", "9075.00", "74433.33", "3208.33"),
    12: ("71300.00", "9900.00", "81200.00", "3500.00"),
}
PRORATION_FAMILIES = (
    "ca/cpp_maximum_pensionable_earnings",
    "ca/cpp_second_additional_earnings_maximum",
    "ca/cpp_additional_maximum_pensionable_earnings",
    "ca/cpp_basic_exemption",
)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


# Line 6.


def test_2025_line_6_is_cut_at_the_fifth_decimal_place_without_rounding() -> None:
    data = SOURCE.get(RATIO_TRUNCATION, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # "calculated to the fifth decimal place without rounding": increment 0.00001, mode down.
    assert data.rounding == FIVE_DECIMALS_DOWN


@pytest.mark.parametrize(
    ("dividend", "divisor", "line_6"),
    [
        # The ticket's example: 30,000 / 70,000 = 0.4285714..., cut, not rounded up to 0.42857.
        ("30000", "70000", "0.42857"),
        # 2 / 3 = 0.66666..., which rounding would make 0.66667.
        ("2", "3", "0.66666"),
        ("1", "1", "1.00000"),
        ("0", "5", "0.00000"),
    ],
)
def test_line_6_truncates_the_quotient(dividend: str, divisor: str, line_6: str) -> None:
    rule = SOURCE.get(RATIO_TRUNCATION, 2025, ROUNDING_ONLY).rounding

    assert rule.apply(ExactFraction(D(dividend)) / ExactFraction(D(divisor))) == D(line_6)


# Lines 7 to 10.


def test_2025_lines_7_to_10_round_half_up_to_the_cent() -> None:
    data = SOURCE.get(CENTS_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("base", "line_6", "line"),
    [
        # The ticket's example, line 6 = 0.42857: line 7 = 81,200.00 x 0.42857 = 34,799.884.
        ("81200.00", "0.42857", "34799.88"),
        # Line 8 = 71,300.00 x 0.42857 = 30,557.0410.
        ("71300.00", "0.42857", "30557.04"),
        # Line 9 = 3,500.00 x 0.42857 = 1,499.995, a tie that goes up: 1,500.00.
        ("3500.00", "0.42857", "1500.00"),
        # Line 10 = 9,900.00 x 0.42857 = 4,242.843.
        ("9900.00", "0.42857", "4242.84"),
    ],
)
def test_lines_7_to_10_multiply_by_line_6_and_round_half_up(
    base: str, line_6: str, line: str
) -> None:
    rule = SOURCE.get(CENTS_ROUNDING, 2025, ROUNDING_ONLY).rounding

    assert rule.apply(ExactFraction(D(base)) * ExactFraction(D(line_6))) == D(line)


# Line 20.


def test_2025_line_20_is_83_1933_percent_to_the_cent() -> None:
    data = SOURCE.get(CPP_BASE_SHARE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.831933"))
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_19", "line_20"),
    [
        # The ticket's example: 1,800.00 x 83.1933% = 1,497.4794.
        ("1800.00", "1497.48"),
        ("0", "0.00"),
        # The maximum base and first additional contributions on 67,800.00 x 5.95%.
        ("4034.10", "3356.10"),
    ],
)
def test_line_20_is_83_1933_percent_of_line_19(line_19: str, line_20: str) -> None:
    capability = ApplyRate(SOURCE.get(CPP_BASE_SHARE_RATE, 2025, RATE), EARNINGS, CONTRIBUTION)

    result = capability.compute((Artifact(EARNINGS, D(line_19)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(line_20)),)


# Line 40.


def test_2025_line_40_is_84_375_percent_to_the_cent() -> None:
    data = SOURCE.get(QPP_BASE_SHARE_RATE, 2025, RATE)

    assert data.values == Rate(D("0.84375"))
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_39", "line_40"),
    [
        # The ticket's example: 2,500.00 x 84.375% = 2,109.375, a tie that rounds up.
        ("2500.00", "2109.38"),
        ("0", "0.00"),
        ("1.00", "0.84"),
        ("0.60", "0.51"),
        # The maximum base and first additional contributions on 67,800.00 x 6.4%.
        ("4339.20", "3661.20"),
    ],
)
def test_line_40_is_84_375_percent_of_line_39(line_39: str, line_40: str) -> None:
    capability = ApplyRate(SOURCE.get(QPP_BASE_SHARE_RATE, 2025, RATE), EARNINGS, CONTRIBUTION)

    result = capability.compute((Artifact(EARNINGS, D(line_39)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(line_40)),)


# Lines 22, 23 and 26, and 42, 43 and 46.


@pytest.mark.parametrize(
    ("family", "tier"),
    [
        # Line 22: "x 4.95% = (maximum $3,356.10)"; 67,800.00 x 4.95% is 3,356.10.
        (REQUIRED_CPP_BASE, ContributionTier(Rate(D("0.0495")), D("0"), D("67800"), D("3356.10"))),
        # Line 23: "x 1% = (maximum $678.00)"; 67,800.00 x 1% is 678.00.
        (
            REQUIRED_FIRST_ADDITIONAL,
            ContributionTier(Rate(D("0.01")), D("0"), D("67800"), D("678.00")),
        ),
        # Line 26: "x 4% = (maximum $396.00)"; 9,900.00 x 4% is 396.00.
        (
            REQUIRED_SECOND_ADDITIONAL,
            ContributionTier(Rate(D("0.04")), D("0"), D("9900"), D("396.00")),
        ),
        # Line 42: "x 5.4% = (maximum $3,661.20)"; 67,800.00 x 5.4% is 3,661.20. Lines 43 and 46
        # print the figures of lines 23 and 26, so they read those two datasets.
        (REQUIRED_QPP_BASE, ContributionTier(Rate(D("0.054")), D("0"), D("67800"), D("3661.20"))),
    ],
)
def test_2025_required_contribution_tiers_are_the_printed_rate_and_maximum(
    family: str, tier: ContributionTier
) -> None:
    data = SOURCE.get(family, 2025, CONTRIBUTION_TIER)

    assert data.values == tier
    # The earnings on lines 18, 15, 38 and 35 are already net of the exemption, so the band starts
    # at 0, and the printed maximum is the whole band at the rate.
    assert (tier.upper - tier.lower) * tier.rate.value == tier.maximum
    # Lines 22, 23, 26, 42, 43 and 46 are dollars-and-cents boxes.
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("family", "earnings", "contribution"),
    [
        # The ticket's example: line 18 = 28,500.00, so line 22 = 1,410.75, line 23 = 285.00.
        (REQUIRED_CPP_BASE, "28500.00", "1410.75"),
        (REQUIRED_FIRST_ADDITIONAL, "28500.00", "285.00"),
        # No earnings, and earnings at and above the band's top.
        (REQUIRED_CPP_BASE, "0", "0.00"),
        (REQUIRED_CPP_BASE, "67800.00", "3356.10"),
        (REQUIRED_CPP_BASE, "80000.00", "3356.10"),
        (REQUIRED_FIRST_ADDITIONAL, "67800.00", "678.00"),
        (REQUIRED_FIRST_ADDITIONAL, "80000.00", "678.00"),
        # Line 26: 4% of the earnings subject to second additional contributions, at most 396.00.
        (REQUIRED_SECOND_ADDITIONAL, "0", "0.00"),
        (REQUIRED_SECOND_ADDITIONAL, "1000.00", "40.00"),
        (REQUIRED_SECOND_ADDITIONAL, "9900.00", "396.00"),
        (REQUIRED_SECOND_ADDITIONAL, "12000.00", "396.00"),
        # Rounded half up to the cent: 4.95% of 0.10 is 0.00495, of 0.11 is 0.005445; 1% of
        # 0.50 is 0.005, a tie that goes up.
        (REQUIRED_CPP_BASE, "0.10", "0.00"),
        (REQUIRED_CPP_BASE, "0.11", "0.01"),
        (REQUIRED_FIRST_ADDITIONAL, "0.50", "0.01"),
        # Line 42: 5.4% of the QPP earnings on line 38, at most 3,661.20. The ticket's example:
        # line 38 = 38,000.00, so line 42 = 2,052.00 and line 43 = 380.00.
        (REQUIRED_QPP_BASE, "38000.00", "2052.00"),
        (REQUIRED_QPP_BASE, "0", "0.00"),
        (REQUIRED_QPP_BASE, "67800.00", "3661.20"),
        (REQUIRED_QPP_BASE, "80000.00", "3661.20"),
        # 5.4% of 0.09 is 0.00486, of 0.10 is 0.0054.
        (REQUIRED_QPP_BASE, "0.09", "0.00"),
        (REQUIRED_QPP_BASE, "0.10", "0.01"),
        # Line 43 reads the dataset of line 23, and line 46 that of line 26.
        (REQUIRED_FIRST_ADDITIONAL, "38000.00", "380.00"),
        (REQUIRED_SECOND_ADDITIONAL, "4400.05", "176.00"),
    ],
)
def test_the_required_contributions_are_the_rate_of_the_earnings_up_to_the_maximum(
    family: str, earnings: str, contribution: str
) -> None:
    capability = TieredContribution(
        SOURCE.get(family, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(earnings)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)


# Part 2 lines G to J read the four existing Schedule 8 tables.


@pytest.mark.parametrize("column", range(4), ids=lambda column: PRORATION_FAMILIES[column])
def test_the_monthly_proration_table_is_the_one_rc381_prints(column: int) -> None:
    data = SOURCE.get(PRORATION_FAMILIES[column], 2025, AMOUNT_BY_COUNT)

    assert dict(data.values.rows) == {
        months: D(row[column]) for months, row in PRORATION_TABLE.items()
    }


@pytest.mark.parametrize("family", PRORATION_FAMILIES)
def test_the_monthly_proration_tables_cite_rc381_beside_schedule_8(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert RC381_PDF in data.sources
    assert "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt" in (
        data.sources
    )


# Part 4 line 27.


def test_2025_part_4_line_27_is_16_80672_over_100000_to_the_cent() -> None:
    data = SOURCE.get(CPP_GROSS_UP_FRACTION, 2025, FRACTION)

    # "× 16.80672" kept as printed, not reduced and not turned into a rate: 16.80672 is above 1,
    # which a rate refuses, as the dividend gross-up of 138% is.
    assert data.values == Fraction(1680672, 100000)
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_26", "line_27"),
    [
        # Return BO's line 26 of 1,695.75 (the CPP contributions that the employment income
        # alone requires): 1,695.75 x 16.80672 = 28,499.9954..., so 28,500.00, which is
        # 1,695.75 / 5.95%.
        ("1695.75", "28500.00"),
        ("0", "0.00"),
        ("1.00", "16.81"),
        # 0.01 x 16.80672 = 0.1680672, up to 0.17; 0.03 x 16.80672 = 0.5042016, down to 0.50.
        ("0.01", "0.17"),
        ("0.03", "0.50"),
        # 100.00 x 16.80672 = 1,680.672, down to 1,680.67; 2.00 x 16.80672 = 33.61344, to 33.61.
        ("100.00", "1680.67"),
        ("2.00", "33.61"),
        # Line 26 may be a negative amount (line 25A is): -1.00 x 16.80672 = -16.80672.
        ("-1.00", "-16.81"),
    ],
)
def test_part_4_line_27_is_line_26_times_16_80672(line_26: str, line_27: str) -> None:
    capability = ApplyFraction(
        SOURCE.get(CPP_GROSS_UP_FRACTION, 2025, FRACTION), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(line_26)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(line_27)),)


# Part 4 line 41.


def test_2025_part_4_line_41_is_15625_over_1000_to_the_cent() -> None:
    data = SOURCE.get(QPP_GROSS_UP_FRACTION, 2025, FRACTION)

    # "× 15.625" kept as printed, not reduced and not turned into a rate: 15.625 is above 1, which
    # a rate refuses, as line 27's 16.80672 is.
    assert data.values == Fraction(15625, 1000)
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_40", "line_41"),
    [
        # Return BO's line 40 of 2,432.00 (line 28 less line 31 when line 61 of Part 3 is
        # positive): 2,432.00 x 15.625 = 38,000.00, which is 2,432.00 / 6.4%.
        ("2432.00", "38000.00"),
        ("0", "0.00"),
        # 1.00 x 15.625 = 15.625, up to 15.63 (half up); 0.01 x 15.625 = 0.15625, up to 0.16;
        # 0.02 x 15.625 = 0.3125, down to 0.31; 0.03 x 15.625 = 0.46875, up to 0.47.
        ("1.00", "15.63"),
        ("0.01", "0.16"),
        ("0.02", "0.31"),
        ("0.03", "0.47"),
        # A tie: 0.04 x 15.625 = 0.625, up to 0.63 (half even would give 0.62); 0.12 x 15.625 =
        # 1.875, up to 1.88.
        ("0.04", "0.63"),
        ("0.12", "1.88"),
        # 100.00 x 15.625 = 1,562.50; 1,568.00 x 15.625 = 24,500.00.
        ("100.00", "1562.50"),
        ("1568.00", "24500.00"),
        # Line 40 may be a negative amount (line 35A's second sentence is, in brackets): -1.00 x
        # 15.625 = -15.625, half up (away from zero) to -15.63.
        ("-1.00", "-15.63"),
        ("-0.03", "-0.47"),
    ],
)
def test_part_4_line_41_is_line_40_times_15_625(line_40: str, line_41: str) -> None:
    capability = ApplyFraction(
        SOURCE.get(QPP_GROSS_UP_FRACTION, 2025, FRACTION), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(line_40)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(line_41)),)


# Part 4 line 76.


def test_2025_part_4_line_76_is_the_4_percent_rate_to_the_cent() -> None:
    data = SOURCE.get(SECOND_ADDITIONAL_RATE, 2025, RATE)

    assert data.values == Rate(D("0.04"))
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_56", "line_76"),
    [
        # 396.00 (the maximum second additional contributions) / 4% = 9,900.00, line D.
        ("396.00", "9900.00"),
        ("0", "0.00"),
        # Return BO-like figures: 62.50 / 4% = 1,562.50; 100.00 / 4% = 2,500.00.
        ("62.50", "1562.50"),
        ("100.00", "2500.00"),
        # Every cent is 25 cents: 0.01 / 4% = 0.25, 1.07 / 4% = 26.75.
        ("0.01", "0.25"),
        ("1.07", "26.75"),
        # Line 56 may be a negative amount: -1.00 / 4% = -25.00.
        ("-1.00", "-25.00"),
    ],
)
def test_part_4_line_76_is_line_56_divided_by_4_percent(line_56: str, line_76: str) -> None:
    capability = DividedByRate(
        SOURCE.get(SECOND_ADDITIONAL_RATE, 2025, RATE), CONTRIBUTION, EARNINGS
    )

    result = capability.compute((Artifact(CONTRIBUTION, D(line_56)),))

    assert result.outputs == (Artifact(EARNINGS, D(line_76)),)


# Part 4 line 89.


def test_2025_part_4_line_89_is_2_over_1_to_the_cent() -> None:
    data = SOURCE.get(DOUBLE_FRACTION, 2025, FRACTION)

    # "× 2" kept as printed, not reduced and not turned into a rate: 2 is above 1, which a rate
    # refuses.
    assert data.values == Fraction(2, 1)
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("line_69", "line_89"),
    [
        # Return BO's line 69 of Part 3 of 172.25 (if positive): twice it is 344.50.
        ("172.25", "344.50"),
        ("0", "0.00"),
        ("0.01", "0.02"),
        ("1234.56", "2469.12"),
    ],
)
def test_part_4_line_89_is_twice_line_69_of_part_3(line_69: str, line_89: str) -> None:
    capability = ApplyFraction(SOURCE.get(DOUBLE_FRACTION, 2025, FRACTION), EARNINGS, CONTRIBUTION)

    result = capability.compute((Artifact(EARNINGS, D(line_69)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(line_89)),)


# Part 4 lines 84 to 86 and 91, which read Schedule 8 Part 4's datasets.


@pytest.mark.parametrize(
    ("family", "tier"),
    [
        # Line 84 "amount from line 70 × 9.9% = (maximum $6,712.20)": 67,800.00 x 9.9% = 6,712.20.
        (
            SELF_EMPLOYED_BASE,
            ContributionTier(Rate(D("0.099")), D("0"), D("67800"), D("6712.20")),
        ),
        # Line 85 "amount from line 70 × 2% = (maximum $1,356.00)": 67,800.00 x 2% = 1,356.00.
        (
            SELF_EMPLOYED_FIRST_ADDITIONAL,
            ContributionTier(Rate(D("0.02")), D("0"), D("67800"), D("1356.00")),
        ),
        # Line 86 "amount from line 83 × 8% = (maximum $792.00)": 9,900.00 x 8% = 792.00.
        (
            SELF_EMPLOYED_SECOND_ADDITIONAL,
            ContributionTier(Rate(D("0.08")), D("0"), D("9900"), D("792.00")),
        ),
    ],
)
def test_part_4_lines_84_to_86_print_the_figures_of_schedule_8_part_4(
    family: str, tier: ContributionTier
) -> None:
    data = SOURCE.get(family, 2025, CONTRIBUTION_TIER)

    assert data.values == tier
    assert data.rounding == CENT


@pytest.mark.parametrize(
    ("family", "line_70", "contribution"),
    [
        # Return BO's line 70 of 1,300.00: 9.9% = 128.70, 2% = 26.00; line 83 of 9,900.00: 792.00.
        (SELF_EMPLOYED_BASE, "1300.00", "128.70"),
        (SELF_EMPLOYED_FIRST_ADDITIONAL, "1300.00", "26.00"),
        (SELF_EMPLOYED_SECOND_ADDITIONAL, "9900.00", "792.00"),
        # A tie: 15.00 x 9.9% = 1.485 rounds half up to 1.49 (half even gives 1.48).
        (SELF_EMPLOYED_BASE, "15.00", "1.49"),
        # The printed maximums: 67,800.00 and more stop at 6,712.20 and 1,356.00, 9,900.00 and
        # more at 792.00.
        (SELF_EMPLOYED_BASE, "67800.00", "6712.20"),
        (SELF_EMPLOYED_BASE, "68039.41", "6712.20"),
        (SELF_EMPLOYED_FIRST_ADDITIONAL, "68039.41", "1356.00"),
        (SELF_EMPLOYED_SECOND_ADDITIONAL, "12499.99", "792.00"),
        # Earnings below zero (line 70 has no floor) contribute nothing.
        (SELF_EMPLOYED_BASE, "-3500.00", "0.00"),
        (SELF_EMPLOYED_SECOND_ADDITIONAL, "0", "0.00"),
    ],
)
def test_part_4_lines_84_to_86_are_the_tiers_of_lines_70_and_83(
    family: str, line_70: str, contribution: str
) -> None:
    capability = TieredContribution(
        SOURCE.get(family, 2025, CONTRIBUTION_TIER), EARNINGS, CONTRIBUTION
    )

    result = capability.compute((Artifact(EARNINGS, D(line_70)),))

    assert result.outputs == (Artifact(CONTRIBUTION, D(contribution)),)


def test_part_4_line_91_is_50_percent_of_line_90_to_the_cent() -> None:
    data = SOURCE.get(SELF_EMPLOYED_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == CENT
    for line_90, line_91 in (
        ("344.50", "172.25"),
        ("0", "0.00"),
        # 344.37 x 50% = 172.185, up to 172.19 (half even gives 172.18).
        ("344.37", "172.19"),
        ("0.01", "0.01"),
    ):
        capability = ApplyRate(data, EARNINGS, CONTRIBUTION)

        result = capability.compute((Artifact(EARNINGS, D(line_90)),))

        assert result.outputs == (Artifact(CONTRIBUTION, D(line_91)),)


# Sources and headers.


@pytest.mark.parametrize(
    ("family", "kind"),
    [
        (RATIO_TRUNCATION, ROUNDING_ONLY),
        (CENTS_ROUNDING, ROUNDING_ONLY),
        (CPP_BASE_SHARE_RATE, RATE),
        (REQUIRED_CPP_BASE, CONTRIBUTION_TIER),
        (REQUIRED_FIRST_ADDITIONAL, CONTRIBUTION_TIER),
        (REQUIRED_SECOND_ADDITIONAL, CONTRIBUTION_TIER),
        (QPP_BASE_SHARE_RATE, RATE),
        (REQUIRED_QPP_BASE, CONTRIBUTION_TIER),
        (CPP_GROSS_UP_FRACTION, FRACTION),
        (QPP_GROSS_UP_FRACTION, FRACTION),
        (SECOND_ADDITIONAL_RATE, RATE),
        (DOUBLE_FRACTION, FRACTION),
    ],
)
def test_2025_rc381_datasets_cite_only_the_rc381_pdf(family: str, kind: ParameterKind[Any]) -> None:
    assert SOURCE.get(family, 2025, kind).sources == (RC381_PDF,)


@pytest.mark.parametrize(
    ("family", "quotes"),
    [
        (
            RATIO_TRUNCATION,
            ("Line 4 divided by line 5 (calculated to the fifth decimal place without rounding)",),
        ),
        (
            CENTS_ROUNDING,
            ("Amount from line E of Part 2 multiplied by the rate at line 6",),
        ),
        (CPP_BASE_SHARE_RATE, ("amount from line 19", "83.1933%")),
        (REQUIRED_CPP_BASE, ("amount from line 18", "4.95%", "(maximum $3,356.10)")),
        (REQUIRED_FIRST_ADDITIONAL, ("amount from line 18", "1%", "(maximum $678.00)")),
        (REQUIRED_SECOND_ADDITIONAL, ("amount from line 15", "4%", "(maximum $396.00)")),
        (QPP_BASE_SHARE_RATE, ("amount from line 39", "84.375%")),
        (REQUIRED_QPP_BASE, ("amount from line 38", "5.4%", "(maximum $3,661.20)")),
        (CPP_GROSS_UP_FRACTION, ("Amount from line 26", "16.80672", "Part 4", "line 27")),
        (QPP_GROSS_UP_FRACTION, ("Amount from line 40", "15.625", "Part 4", "line 41")),
        (SECOND_ADDITIONAL_RATE, ("Amount from line 56", "÷ 4%", "Part 4", "line 76")),
        (
            DOUBLE_FRACTION,
            ("Amount from line 69 of Part 3 (if positive)", "× 2", "Part 4", "line 89"),
        ),
    ],
)
def test_the_dataset_header_quotes_rc381_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family)

    assert "RC381" in header
    for quote in quotes:
        assert quote in header, quote


@pytest.mark.parametrize(
    ("family", "quotes"),
    [
        # Line 43 prints the figures of line 23, and line 46 those of line 26, so the header of
        # the shared dataset quotes both lines.
        (
            REQUIRED_FIRST_ADDITIONAL,
            ("line 43", "amount from line 38", "1%", "(maximum $678.00)"),
        ),
        (
            REQUIRED_SECOND_ADDITIONAL,
            ("line 46", "amount from line 35", "4%", "(maximum $396.00)"),
        ),
    ],
)
def test_the_shared_dataset_header_also_quotes_the_qpp_line(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family)

    for quote in quotes:
        assert quote in header, quote


@pytest.mark.parametrize(
    "family",
    [
        RATIO_TRUNCATION,
        CENTS_ROUNDING,
        CPP_BASE_SHARE_RATE,
        REQUIRED_CPP_BASE,
        REQUIRED_FIRST_ADDITIONAL,
        REQUIRED_SECOND_ADDITIONAL,
        QPP_BASE_SHARE_RATE,
        REQUIRED_QPP_BASE,
        CPP_GROSS_UP_FRACTION,
        QPP_GROSS_UP_FRACTION,
        SECOND_ADDITIONAL_RATE,
        DOUBLE_FRACTION,
    ],
)
def test_the_dataset_header_states_its_rounding_decision(family: str) -> None:
    assert "round" in dataset_header(family).lower()
