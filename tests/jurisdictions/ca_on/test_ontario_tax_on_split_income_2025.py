"""The 2025 Ontario tax on split income rates (Form T1206 Part 3), checked against CRA.

Form T1206 2025 (docs/cra-forms-2025/t1206-25e.pdf, confirmed 2026-10-19 from the PDF; no .txt
published), Chart C, Ontario's row: "ON 20.53% 5.05% 10% 2.9863% Not applicable" (column 2, the
high tax rate; column 3, the low tax rate; column 5, the eligible dividend tax credit rate;
column 6, the dividend other than eligible dividend tax credit rate); Part 3: "The amount from
line 31 multiplied by the tax rate you entered on line 32. Enter this amount on the line of your
Form 428 shown in column 4 in Chart C on page 5." (line 33); "Line 34 plus line 35" (line 36)
"Tax rate that applies to your province or territory from column 3 in Chart C" (line 37), "Amount
from line 36 multiplied by the tax rate you entered on line 37" (line 38); "Line 33 minus line
38" (line 39); "Amount from line 18" (line 40) "Eligible dividend tax credit rate" (line 41),
"Amount from line 40 multiplied by the rate you entered on line 41" (line 42); "Amount from line
17" (line 43) "Dividend other than eligible dividend tax credit rate" (line 44), "Amount from
line 43 multiplied by the rate you entered on line 44" (line 45); "Line 42 plus line 45" (line
46); "Line 39 minus line 46" (line 47).

Each printed percentage is a `rate` dataset of its own, not the Ontario form ON428's: the 20.53% of
line 33 (ON428 line 54, 61510), the 5.05% of line 37, the 10% of line 41 and the 2.9863% of line
44 (the Ontario dividend tax credit rates of Worksheet ON428, the same percentages on another
form). Lines 33, 38, 42 and 45 are dollars-and-cents boxes, so each product is rounded half-up to
the cent, the owner's decision, as the form states no rounding rule.

The datasets are tested with the capabilities that read them, on made-up kinds for the form's
lines; the lines together, from the federal lines 4, 17 and 18 and the disability amounts to line
47, are tested against the cases the form's text settles.
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
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T1206_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/t1206-25e.pdf"
SPLIT_INCOME_RATE = "ca-on/split_income_rate"
DISABILITY_CREDIT_RATE = "ca-on/split_income_disability_credit_rate"
ELIGIBLE_CREDIT_RATE = "ca-on/split_income_dividend_credit_rate_eligible"
OTHER_CREDIT_RATE = "ca-on/split_income_dividend_credit_rate_other_than_eligible"

# Made up for this test and not registered: the form's lines, by number.
LINE_4 = ArtifactKind("ex/line_4", Decimal)
LINE_17 = ArtifactKind("ex/line_17", Decimal)
LINE_18 = ArtifactKind("ex/line_18", Decimal)
LINE_33 = ArtifactKind("ex/line_33", Decimal)
LINE_34 = ArtifactKind("ex/line_34", Decimal)
LINE_35 = ArtifactKind("ex/line_35", Decimal)
LINE_36 = ArtifactKind("ex/line_36", Decimal)
LINE_38 = ArtifactKind("ex/line_38", Decimal)
LINE_39 = ArtifactKind("ex/line_39", Decimal)
LINE_42 = ArtifactKind("ex/line_42", Decimal)
LINE_45 = ArtifactKind("ex/line_45", Decimal)
LINE_46 = ArtifactKind("ex/line_46", Decimal)
LINE_47 = ArtifactKind("ex/line_47", Decimal)
LINE_51 = ArtifactKind("ex/line_51", Decimal)
LINE_52 = ArtifactKind("ex/line_52", Decimal)


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
    line_4: str, line_17: str, line_18: str, line_34: str, line_35: str = "0"
) -> dict[str, Decimal]:
    """Lines 33 to 47 from the real datasets: the figures Part 3 takes from Parts 1 and 2."""
    a4 = Artifact(LINE_4, D(line_4))
    a17 = Artifact(LINE_17, D(line_17))
    a18 = Artifact(LINE_18, D(line_18))
    a34 = Artifact(LINE_34, D(line_34))
    a35 = Artifact(LINE_35, D(line_35))
    line_33 = only(
        ApplyRate(SOURCE.get(SPLIT_INCOME_RATE, 2025, RATE), LINE_4, LINE_33).compute((a4,))
    )
    line_36 = only(Sum((LINE_34, LINE_35), LINE_36).compute((a34, a35)))
    line_38 = only(
        ApplyRate(SOURCE.get(DISABILITY_CREDIT_RATE, 2025, RATE), LINE_36, LINE_38).compute(
            (line_36,)
        )
    )
    line_39 = only(Subtract(LINE_33, LINE_38, LINE_39).compute((line_33, line_38)))
    line_42 = only(
        ApplyRate(SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE), LINE_18, LINE_42).compute((a18,))
    )
    line_45 = only(
        ApplyRate(SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE), LINE_17, LINE_45).compute((a17,))
    )
    line_46 = only(Sum((LINE_42, LINE_45), LINE_46).compute((line_42, line_45)))
    line_47 = only(Subtract(LINE_39, LINE_46, LINE_47).compute((line_39, line_46)))
    return {
        "33": line_33.value,
        "36": line_36.value,
        "38": line_38.value,
        "39": line_39.value,
        "42": line_42.value,
        "45": line_45.value,
        "46": line_46.value,
        "47": line_47.value,
    }


def test_2025_line_33_rate_is_the_printed_20_53_percent() -> None:
    data = SOURCE.get(SPLIT_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.2053"))
    # Line 33, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_37_rate_is_the_printed_5_05_percent() -> None:
    data = SOURCE.get(DISABILITY_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.0505"))
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_41_rate_is_the_printed_10_percent() -> None:
    data = SOURCE.get(ELIGIBLE_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.1"))
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_2025_line_44_rate_is_the_printed_2_9863_percent() -> None:
    data = SOURCE.get(OTHER_CREDIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.029863"))
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


def test_the_ontario_t1206_rates_are_datasets_of_their_own_beside_on428s_and_the_federal_ones() -> (
    None
):
    # The same percentages appear on ON428 and Worksheet ON428 (5.05%, 10%, 2.9863%); T1206's
    # lines read their own families, so a change to one form's rate cannot move the other's, and
    # the Ontario families are not the federal T1206 ones.
    assert SOURCE.get("ca-on/credit_rate", 2025, RATE).sources != (T1206_PDF,)
    assert SOURCE.get("ca-on/dividend_credit_rate_eligible", 2025, RATE).sources != (T1206_PDF,)
    for family in (
        SPLIT_INCOME_RATE,
        DISABILITY_CREDIT_RATE,
        ELIGIBLE_CREDIT_RATE,
        OTHER_CREDIT_RATE,
    ):
        assert T1206_PDF in SOURCE.get(family, 2025, RATE).sources, family
    assert (
        SOURCE.get("ca/split_income_rate", 2025, RATE).values
        != SOURCE.get(SPLIT_INCOME_RATE, 2025, RATE).values
    )


@pytest.mark.parametrize(
    ("line_31", "line_33"),
    [
        # The worked example: 20.53% of 11,500 is 2,360.95.
        ("11500", "2360.95"),
        ("0", "0.00"),
        ("1000", "205.30"),
        # 20.53% of 1,150 is 236.095, a tie, up to 236.10.
        ("1150", "236.10"),
        # 20.53% of 11,500.01 is 2,360.952053, down to 2,360.95.
        ("11500.01", "2360.95"),
    ],
)
def test_line_33_is_20_53_percent_of_line_31_to_the_cent(line_31: str, line_33: str) -> None:
    assert rate_of(SPLIT_INCOME_RATE, LINE_4, LINE_33, line_31) == D(line_33)


@pytest.mark.parametrize(
    ("line_36", "line_38"),
    [
        # 5.05% of the $10,138 disability amount is 511.969, up to 511.97.
        ("10138", "511.97"),
        ("0", "0.00"),
        ("1000", "50.50"),
        # 5.05% of 0.10 is 0.00505, a tie, up to 0.01.
        ("0.10", "0.01"),
    ],
)
def test_line_38_is_5_05_percent_of_line_36_to_the_cent(line_36: str, line_38: str) -> None:
    assert rate_of(DISABILITY_CREDIT_RATE, LINE_36, LINE_38, line_36) == D(line_38)


@pytest.mark.parametrize(
    ("line_40", "line_42"),
    [
        ("6000", "600.00"),
        ("0", "0.00"),
        # 10% of 0.05 is 0.005, a tie, up to 0.01.
        ("0.05", "0.01"),
        ("11500", "1150.00"),
    ],
)
def test_line_42_is_10_percent_of_line_40_to_the_cent(line_40: str, line_42: str) -> None:
    assert rate_of(ELIGIBLE_CREDIT_RATE, LINE_18, LINE_42, line_40) == D(line_42)


@pytest.mark.parametrize(
    ("line_43", "line_45"),
    [
        # The worked example: 2.9863% of 11,500 is 343.4245, to 343.42.
        ("11500", "343.42"),
        ("0", "0.00"),
        ("1000", "29.86"),
        ("1150", "34.34"),
    ],
)
def test_line_45_is_2_9863_percent_of_line_43_to_the_cent(line_43: str, line_45: str) -> None:
    assert rate_of(OTHER_CREDIT_RATE, LINE_17, LINE_45, line_43) == D(line_45)


def test_the_worked_example_gives_line_33_of_2360_95_and_line_47_of_2017_53() -> None:
    # Line 4 and line 17 are 11,500 and line 18 is 0: line 33 is 20.53% x 11,500 = 2,360.95, line
    # 45 is 2.9863% x 11,500 = 343.42 and line 47 is 2,360.95 - 343.42 = 2,017.53.
    result = lines("11500", "11500", "0", "0")

    assert result["33"] == D("2360.95")
    assert result["36"] == D("0")
    assert result["38"] == D("0.00")
    assert result["39"] == D("2360.95")
    assert result["42"] == D("0.00")
    assert result["45"] == D("343.42")
    assert result["46"] == D("343.42")
    assert result["47"] == D("2017.53")


@pytest.mark.parametrize(
    ("line_4", "line_17", "line_18", "line_34", "line_35", "line_47"),
    [
        # All eligible dividends: line 17 is 0, line 18 is 11,500 and line 42 is 1,150.00:
        # 2,360.95 - 1,150.00.
        ("11500", "0", "11500", "0", "0", "1210.95"),
        # Mixed: line 4 is 12,000, line 33 is 2,463.60, line 42 is 10% x 6,000 = 600.00 and line
        # 45 is 2.9863% x 4,000 = 119.45: 2,463.60 - 719.45.
        ("12000", "4000", "6000", "0", "0", "1744.15"),
        # The disability amount for self takes 5.05% x 10,138 = 511.97 off line 33.
        ("12000", "4000", "6000", "10138", "0", "1232.18"),
        # Line 35 (the amount transferred from a dependant) adds to line 34 before the rate.
        ("12000", "4000", "6000", "10138", "2000", "1131.18"),
        # Only other split income: no dividends, so no credit.
        ("5000", "0", "0", "0", "0", "1026.50"),
    ],
)
def test_line_47_from_the_cases_the_form_settles(
    line_4: str, line_17: str, line_18: str, line_34: str, line_35: str, line_47: str
) -> None:
    assert lines(line_4, line_17, line_18, line_34, line_35)["47"] == D(line_47)


def test_line_47_is_negative_when_the_disability_credit_is_more_than_the_tax() -> None:
    # Line 33 is 236.10 (a tie, up), line 38 is 511.97, so line 39, which prints no floor, is
    # -275.87; line 45 is 34.34 and line 47 is -310.21.
    result = lines("1150", "1150", "0", "10138")

    assert result["33"] == D("236.10")
    assert result["38"] == D("511.97")
    assert result["39"] == D("-275.87")
    assert result["45"] == D("34.34")
    assert result["47"] == D("-310.21")


@pytest.mark.parametrize(
    ("line_50", "line_51", "line_52"),
    [
        # The worked example: line 50 is 2,017.53 and line 88 (line 51) is 2,017.53.
        ("2017.53", "2017.53", "2017.53"),
        # A negative line 50 leaves line 88 as line 52.
        ("-310.21", "400.00", "400.00"),
        ("3000.00", "400.00", "3000.00"),
        ("0", "0", "0"),
    ],
)
def test_line_52_is_the_more_of_lines_50_and_51(line_50: str, line_51: str, line_52: str) -> None:
    capability = GreaterOf((LINE_47, LINE_51), LINE_52)

    result = capability.compute((Artifact(LINE_47, D(line_50)), Artifact(LINE_51, D(line_51))))

    assert only(result).value == D(line_52)
