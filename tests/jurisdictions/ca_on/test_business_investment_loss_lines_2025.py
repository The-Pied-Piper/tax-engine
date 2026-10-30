"""The 2025 printed multipliers of Form T1436 lines 1 to 6 (the capital gains deductions claimed),
checked against CRA's Form T1436, Capital Gains Worksheet.

Form T1436 (2025), "Line 21700 - Allowable business investment loss", "Calculating your business
investment loss reduction, if any", each line the amount from an earlier return times a printed
figure:

    For 1985 to 1987: Total amounts from line 254 of your income tax and benefit returns for these
        years x 2 = 1
    For 1988 and 1989 (other than for eligible capital property gains): ... (a) x 1.5 = 2
    For 1988 and 1989 (for eligible capital property gains): ... x 1.3333 = 3
    For 1990 to 1999: Total amounts from line 254 of your returns for these years x 1.3333 = 4
    For 2000: Amount from line 254 of your return x 1/IR (1) = 5
    For 2001 to 2024: ... x 2 = 6

Each printed figure is its own `fraction` dataset, held as the printed fraction: 2 is 2/1, 1.5 is
15/10 and 1.3333 is 13333/10000, kept as given (never reduced), as the cpp multiplier is. The line
is a dollars-and-cents box, so each product rounds half-up to the cent, the owner's decision, as the
form states no rounding rule. Line 5's "x 1/IR" is the ratio of the amount to the 2000 inclusion
rate, a `rounding_only` dataset rounding the quotient half-up to the cent, and 0 when the rate is 0.

The lines are tested with the capability that reads each dataset, on made-up kinds; the worksheet's
lines together, with the Schedule 3 lines 543 and 544 of lines 2 and 3, are in the `end_to_end`
tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_fraction import ApplyFraction
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FORM = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1436/t1436-25e.pdf"


def kind(name: str) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/{name}", Decimal)


BASE = kind("base")
PRODUCT = kind("product")
AMOUNT = kind("amount")
NUMERATOR = kind("numerator")
INCLUSION_RATE = kind("inclusion_rate")
QUOTIENT = kind("quotient")


@pytest.mark.parametrize(
    ("family", "numerator", "denominator"),
    [
        # "For 1985 to 1987 ... x 2".
        ("ca/t1436_line_1_multiplier", 2, 1),
        # "(a) x 1.5", kept as printed.
        ("ca/t1436_line_2_multiplier", 15, 10),
        # "For 1988 and 1989 (for eligible capital property gains) ... x 1.3333", kept as printed.
        ("ca/t1436_line_3_multiplier", 13333, 10000),
        # "For 1990 to 1999 ... x 1.3333", kept as printed.
        ("ca/t1436_line_4_multiplier", 13333, 10000),
        # "For 2001 to 2024 ... x 2".
        ("ca/t1436_line_6_multiplier", 2, 1),
    ],
)
def test_2025_the_printed_multipliers_are_kept_as_the_printed_fractions(
    family: str, numerator: int, denominator: int
) -> None:
    data = SOURCE.get(family, 2025, FRACTION)

    assert data.values == Fraction(numerator, denominator)
    # Each line is a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (FORM,)


def test_2025_the_1_3333_multiplier_is_not_the_exact_four_thirds() -> None:
    # The printed 1.3333 is 13333/10000 as the worked example's figures need (10000 x 1.3333 is
    # 13333.00, where 4/3 would give 13333.33): the exact fraction is not taken.
    for family in ("ca/t1436_line_3_multiplier", "ca/t1436_line_4_multiplier"):
        assert SOURCE.get(family, 2025, FRACTION).values != Fraction(4, 3), family


def test_2025_the_line_5_rounding_is_half_up_to_the_cent() -> None:
    # Line 5 "x 1/IR (1)": the quotient is a dollars-and-cents box, rounded half-up to the cent
    # once.
    data = SOURCE.get("ca/t1436_line_5_rounding", 2025, ROUNDING_ONLY)

    assert data.rounding == CENT
    assert data.sources == (FORM,)


@pytest.mark.parametrize(
    ("family", "amount", "expected"),
    [
        # Line 1: 137 x 2.
        ("ca/t1436_line_1_multiplier", "137", "274.00"),
        # Line 2: 100 x 1.5.
        ("ca/t1436_line_2_multiplier", "100", "150.00"),
        # Line 3 and line 4: 137 x 1.3333 = 182.6621, to the cent 182.66.
        ("ca/t1436_line_3_multiplier", "137", "182.66"),
        ("ca/t1436_line_4_multiplier", "137", "182.66"),
        # Line 6: 137 x 2.
        ("ca/t1436_line_6_multiplier", "137", "274.00"),
        # A tie, half-up: 50 x 1.3333 is 66.665, up to 66.67.
        ("ca/t1436_line_3_multiplier", "50", "66.67"),
    ],
)
def test_each_multiplier_applies_to_the_amount_and_rounds_half_up_to_the_cent(
    family: str, amount: str, expected: str
) -> None:
    capability = ApplyFraction(SOURCE.get(family, 2025, FRACTION), BASE, PRODUCT)

    result = capability.compute((Artifact(BASE, D(amount)),))

    assert result.outputs == (Artifact(PRODUCT, D(expected)),)


@pytest.mark.parametrize(
    ("amount", "inclusion_rate", "expected"),
    [
        # Line 5: 300 x 1/0.5 = 600.
        ("300", "0.5", "600.00"),
        # 100 x 1/0.3 = 333.3333..., to the cent 333.33.
        ("100", "0.3", "333.33"),
        # With an inclusion rate of 0 the line is 0, not a division by 0.
        ("300", "0", "0.00"),
    ],
)
def test_line_5_divides_the_amount_by_the_inclusion_rate_or_is_0_when_it_is_0(
    amount: str, inclusion_rate: str, expected: str
) -> None:
    numerator = Artifact(NUMERATOR, D("1"))
    capability = ApplyRatioOrZero(
        SOURCE.get("ca/t1436_line_5_rounding", 2025, ROUNDING_ONLY),
        AMOUNT,
        NUMERATOR,
        INCLUSION_RATE,
        QUOTIENT,
    )

    result = capability.compute(
        (Artifact(AMOUNT, D(amount)), numerator, Artifact(INCLUSION_RATE, D(inclusion_rate)))
    )

    assert result.outputs == (Artifact(QUOTIENT, D(expected)),)
