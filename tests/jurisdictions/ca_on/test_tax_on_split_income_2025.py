"""The 2025 federal tax on split income rates (Form T1206 Part 2), checked against CRA.

Form T1206 2025 (docs/cra-forms-2025/t1206-25e.pdf, confirmed 2026-10-19 from the PDF; no .txt
published), Part 2 - Federal tax on split income: "Total split income from line 4" (line 7);
"Amount from line 7 multiplied by 33% Enter this amount on line 40424 of your return. Federal tax
on split income" (line 8); "Line 11 plus line 12" (line 13) "x 14.5%" (line 14); "Amount from line 1
of Part 1" (line 16); "Amount from line 2 of Part 1" (line 17) "x 9.0301%" (line 19); "Line 16 minus
line 17 (if negative, enter "0")" (line 18) "x 15.0198%" (line 20); "Line 19 plus line 20" (line
21); "Line 15 minus line 21" (line 22); "Line 22 minus line 23 (if negative, enter "0")" (line 24);
"Enter whichever is more: the amount from line 24 or line 29." (line 30).

Each printed percentage is a `rate` dataset of its own, not the T1's: the 33% of line 8, the 14.5%
of line 14, the 9.0301% of line 19 and the 15.0198% of line 20 (the federal dividend tax credit
rates of the Federal Worksheet's lines 6 and 7, the same percentages on another form). Lines 8, 14,
19 and 20 are dollars-and-cents boxes, so each product is rounded half-up to the cent, the owner's
decision, as the form states no rounding rule.

The datasets are tested with the capabilities that read them, on made-up kinds for the form's
lines; the lines together, from lines 1 to 3 and the disability amounts to line 22, line 24 and
line 30, are tested against the cases the form's text settles.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.greater_of import GreaterOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T1206_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/t1206-25e.pdf"
SPLIT_INCOME_RATE = "ca/split_income_rate"
DISABILITY_CREDIT_RATE = "ca/split_income_disability_credit_rate"
OTHER_CREDIT_RATE = "ca/split_income_dividend_credit_rate_other_than_eligible"
ELIGIBLE_CREDIT_RATE = "ca/split_income_dividend_credit_rate_eligible"

# Made up for this test and not registered: the form's lines, by number.
LINE_1 = ArtifactKind("ex/line_1", Decimal)
LINE_2 = ArtifactKind("ex/line_2", Decimal)
LINE_3 = ArtifactKind("ex/line_3", Decimal)
LINE_4 = ArtifactKind("ex/line_4", Decimal)
LINE_8 = ArtifactKind("ex/line_8", Decimal)
LINE_9 = ArtifactKind("ex/line_9", Decimal)
LINE_10 = ArtifactKind("ex/line_10", Decimal)
LINE_13 = ArtifactKind("ex/line_13", Decimal)
LINE_14 = ArtifactKind("ex/line_14", Decimal)
LINE_15 = ArtifactKind("ex/line_15", Decimal)
LINE_18 = ArtifactKind("ex/line_18", Decimal)
LINE_19 = ArtifactKind("ex/line_19", Decimal)
LINE_20 = ArtifactKind("ex/line_20", Decimal)
LINE_21 = ArtifactKind("ex/line_21", Decimal)
LINE_22 = ArtifactKind("ex/line_22", Decimal)
LINE_24 = ArtifactKind("ex/line_24", Decimal)
LINE_29 = ArtifactKind("ex/line_29", Decimal)
LINE_30 = ArtifactKind("ex/line_30", Decimal)


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def rate_of(
    family: str, base: ArtifactKind[Decimal], output: ArtifactKind[Decimal], amount: str
) -> Decimal:
    """`amount` taken at the family's rate, as the capability the manifest selects does."""
    capability = ApplyRate(SOURCE.get(family, 2025, RATE), base, output)
    return only(capability.compute((Artifact(base, D(amount)),))).value


def lines(
    line_1: str, line_2: str, line_3: str, disability: str, line_9: str = "0"
) -> dict[str, Decimal]:
    """Lines 4 to 24 from the real datasets: the figures a return takes from Part 1 and the T1."""
    a1, a2, a3 = (
        Artifact(kind, D(v)) for kind, v in ((LINE_1, line_1), (LINE_2, line_2), (LINE_3, line_3))
    )
    line_4 = only(Sum((LINE_1, LINE_3), LINE_4).compute((a1, a3)))
    line_8 = only(
        ApplyRate(SOURCE.get(SPLIT_INCOME_RATE, 2025, RATE), LINE_4, LINE_8).compute((line_4,))
    )
    line_10 = only(Sum((LINE_8, LINE_9), LINE_10).compute((line_8, Artifact(LINE_9, D(line_9)))))
    line_14 = only(
        ApplyRate(SOURCE.get(DISABILITY_CREDIT_RATE, 2025, RATE), LINE_13, LINE_14).compute(
            (Artifact(LINE_13, D(disability)),)
        )
    )
    line_15 = only(Subtract(LINE_10, LINE_14, LINE_15).compute((line_10, line_14)))
    line_18 = only(SubtractNotBelowZero(LINE_1, LINE_2, LINE_18).compute((a1, a2)))
    line_19 = only(
        ApplyRate(SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE), LINE_2, LINE_19).compute((a2,))
    )
    line_20 = only(
        ApplyRate(SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE), LINE_18, LINE_20).compute(
            (line_18,)
        )
    )
    line_21 = only(Sum((LINE_19, LINE_20), LINE_21).compute((line_19, line_20)))
    line_22 = only(Subtract(LINE_15, LINE_21, LINE_22).compute((line_15, line_21)))
    line_24 = only(SumNotBelowZero((LINE_22,), LINE_24).compute((line_22,)))
    return {
        "4": line_4.value,
        "8": line_8.value,
        "10": line_10.value,
        "14": line_14.value,
        "15": line_15.value,
        "18": line_18.value,
        "19": line_19.value,
        "20": line_20.value,
        "21": line_21.value,
        "22": line_22.value,
        "24": line_24.value,
    }


def test_2025_line_8_rate_is_the_printed_33_percent() -> None:
    data = SOURCE.get(SPLIT_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.33"))
    # Line 8, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_14_rate_is_the_printed_14_5_percent() -> None:
    data = SOURCE.get(DISABILITY_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.145"))
    # Line 14, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_19_rate_is_the_printed_9_0301_percent() -> None:
    data = SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.090301"))
    # Line 19, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_20_rate_is_the_printed_15_0198_percent() -> None:
    data = SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.150198"))
    # Line 20, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_the_t1206_rates_are_datasets_of_their_own_beside_the_t1s() -> None:
    # The same percentages appear on the T1 and the Federal Worksheet (14.5% and the two dividend
    # credit rates); T1206's lines read their own families, so a change to one form's rate cannot
    # move the other's.
    assert SOURCE.get("ca/credit_rate", 2025, RATE).sources != (T1206_PDF,)
    for family in (
        SPLIT_INCOME_RATE,
        DISABILITY_CREDIT_RATE,
        OTHER_CREDIT_RATE,
        ELIGIBLE_CREDIT_RATE,
    ):
        assert T1206_PDF in SOURCE.get(family, 2025, RATE).sources, family


@pytest.mark.parametrize(
    ("line_4", "line_8"),
    [
        # The worked example: 33% of 11,500 is 3,795.00.
        ("11500", "3795.00"),
        ("0", "0.00"),
        ("1000", "330.00"),
        # Half-up to the cent: 33% of 1.50 is 0.495, a tie, up to 0.50.
        ("1.50", "0.50"),
        # 33% of 11,500.01 is 3,795.0033, down to 3,795.00.
        ("11500.01", "3795.00"),
    ],
)
def test_line_8_is_33_percent_of_line_4_to_the_cent(line_4: str, line_8: str) -> None:
    assert rate_of(SPLIT_INCOME_RATE, LINE_4, LINE_8, line_4) == D(line_8)


@pytest.mark.parametrize(
    ("line_13", "line_14"),
    [
        # 14.5% of the $10,138 disability amount for self is 1,470.01 exactly.
        ("10138", "1470.01"),
        ("0", "0.00"),
        # Half-up to the cent: 14.5% of 1.00 is 0.145, a tie, up to 0.15; of 0.10, 0.0145, down.
        ("1.00", "0.15"),
        ("0.10", "0.01"),
        ("3.50", "0.51"),
    ],
)
def test_line_14_is_14_5_percent_of_line_13_to_the_cent(line_13: str, line_14: str) -> None:
    assert rate_of(DISABILITY_CREDIT_RATE, LINE_13, LINE_14, line_13) == D(line_14)


@pytest.mark.parametrize(
    ("line_17", "line_19"),
    [
        # The worked example: 9.0301% of 11,500 is 1,038.4615, to 1,038.46.
        ("11500", "1038.46"),
        ("0", "0.00"),
        ("1000", "90.30"),
        ("1150", "103.85"),
        ("11500.01", "1038.46"),
    ],
)
def test_line_19_is_9_0301_percent_of_line_17_to_the_cent(line_17: str, line_19: str) -> None:
    assert rate_of(OTHER_CREDIT_RATE, LINE_2, LINE_19, line_17) == D(line_19)


@pytest.mark.parametrize(
    ("line_18", "line_20"),
    [
        # 15.0198% of 11,500 is 1,727.277, up to 1,727.28.
        ("11500", "1727.28"),
        ("0", "0.00"),
        ("1000", "150.20"),
        ("6000", "901.19"),
    ],
)
def test_line_20_is_15_0198_percent_of_line_18_to_the_cent(line_18: str, line_20: str) -> None:
    assert rate_of(ELIGIBLE_CREDIT_RATE, LINE_18, LINE_20, line_18) == D(line_20)


def test_the_worked_example_gives_line_8_of_3795_and_line_22_of_2756_54() -> None:
    # Lines 1, 2 and 4 are 11,500 and line 3 is 0: line 8 is 33% x 11,500 = 3,795.00, line 19 is
    # 9.0301% x 11,500 = 1,038.46 and line 22 is 3,795.00 - 1,038.46 = 2,756.54.
    result = lines("11500", "11500", "0", "0")

    assert result["4"] == D("11500")
    assert result["8"] == D("3795.00")
    assert result["10"] == D("3795.00")
    assert result["14"] == D("0.00")
    assert result["15"] == D("3795.00")
    assert result["18"] == D("0")
    assert result["19"] == D("1038.46")
    assert result["20"] == D("0.00")
    assert result["21"] == D("1038.46")
    assert result["22"] == D("2756.54")
    assert result["24"] == D("2756.54")


@pytest.mark.parametrize(
    ("line_1", "line_2", "line_3", "disability", "line_9", "line_22"),
    [
        # All eligible dividends: line 2 is 0, so line 18 is 11,500 and line 20 is 1,727.28:
        # 3,795.00 - 1,727.28.
        ("11500", "0", "0", "0", "0", "2067.72"),
        # Mixed: line 4 is 10,000 + 2,000 = 12,000, line 8 is 3,960.00, line 18 is 6,000, line 19
        # is 361.20, line 20 is 901.19 and line 21 is 1,262.39.
        ("10000", "4000", "2000", "0", "0", "2697.61"),
        # The disability amount for self takes 14.5% x 10,138 = 1,470.01 off line 10.
        ("10000", "4000", "2000", "10138", "0", "1227.60"),
        # Line 9 (line 41500) is added to line 8 before the disability credit is taken off.
        ("10000", "4000", "2000", "0", "200", "2897.61"),
        # Only other split income: no dividends, so no credit.
        ("0", "0", "5000", "0", "0", "1650.00"),
        # Line 2 equals line 1: line 18 is 0, so line 20 is 0; line 19 is 9.0301% x 1,000 = 90.30.
        ("1000", "1000", "0", "0", "0", "239.70"),
    ],
)
def test_line_22_from_the_cases_the_form_settles(
    line_1: str, line_2: str, line_3: str, disability: str, line_9: str, line_22: str
) -> None:
    assert lines(line_1, line_2, line_3, disability, line_9)["22"] == D(line_22)


def test_line_22_is_negative_when_the_disability_credit_is_more_than_the_tax() -> None:
    # Line 10 (379.50) less line 14 (1,470.01) is -1,090.51: line 15 prints no floor. Line 21 is
    # 103.85, so line 22 is -1,194.36, and line 24 "(if negative, enter "0")" is 0.
    result = lines("1150", "1150", "0", "10138")

    assert result["8"] == D("379.50")
    assert result["14"] == D("1470.01")
    assert result["15"] == D("-1090.51")
    assert result["21"] == D("103.85")
    assert result["22"] == D("-1194.36")
    assert result["24"] == D("0")


@pytest.mark.parametrize(
    ("line_24", "line_29", "line_30"),
    [
        # The worked example: line 24 is 2,756.54 and line 29 (the T1's tax less credits) is 417.83.
        ("2756.54", "417.83", "2756.54"),
        # Line 24 is 0 when line 22 is negative: line 29 is the more.
        ("0", "1773.69", "1773.69"),
        ("0", "0", "0"),
        ("1000.00", "1000.00", "1000.00"),
    ],
)
def test_line_30_is_the_more_of_lines_24_and_29(line_24: str, line_29: str, line_30: str) -> None:
    capability = GreaterOf((LINE_24, LINE_29), LINE_30)

    result = capability.compute((Artifact(LINE_24, D(line_24)), Artifact(LINE_29, D(line_29))))

    assert only(result).value == D(line_30)
