"""The 2025 pre-1986 capital loss balance figures, checked against CRA's Form T1436.

Form T1436 (Capital Gains Worksheet, 2025; CRA publishes no .txt, so the quotes are from the text
extracted from the PDF: confirmed from the PDF; no .txt published), "Line 25300 - Net capital loss
of other years (if you have pre-1986 capital loss balance)", "Calculating your pre-1986 capital
loss balance available for 2025, if any":

    Balance of unapplied net capital losses you had before May 23, 1985 ........ 1
    Capital gains deductions you claimed:
     Before 1988 ........................................................ A
     In 1988 and 1989           x 0.75        = + B
     From 1990 to 1999          x 0.6667      = + C
     In 2000                    x 1/(IR x 2)  = + D
     From 2001 to 2024                          + E
     Total capital gains deductions after adjustment: add amounts A to E. = - 2
    Pre-1986 capital loss balance available for 2025: line 1 minus line 2 = 3

and, after line 8, "Enter whichever is less: amount from line 3, line 8, or $2,000. + 9". The form
prints 0.75 and 0.6667 for 3/4 and 2/3 rounded for print, so each factor is a `fraction` dataset
holding the exact fraction, as Chart A's. The row "In 2000" (D) is the amount divided by 2 x IR,
the same factor as Chart A's row "In 2000" column (B), where IR is the inclusion rate for 2000.
Line 2 is a dollars-and-cents box, so each product rounds half-up to the cent, the owner's
decision, as the form states no rounding rule; so does the $2,000, an `amount` dataset.

This module builds the chain from the same datasets with made-up kinds: B and C multiplied by
their factors, D divided by 2 x IR, line 2 the sum of A, B, C, D and E, line 3 line 1 minus line 2,
line 9 the lesser of line 3, line 8 and the maximum.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero
from tax_calculator.jurisdictions.ca.capabilities.lesser_of_with_maximum import LesserOfWithMaximum

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FORM = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1436/t1436-25e.pdf"


def kind(name: str) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/{name}", Decimal)


LINE_1 = kind("line_1")
A = kind("a")
B = kind("b")
C = kind("c")
D_2000 = kind("d_2000")
E = kind("e")
RATE = kind("inclusion_rate")
TWICE = kind("twice_ir")
NUMERATOR = kind("numerator_one")
B_ADJUSTED = kind("b_adjusted")
C_ADJUSTED = kind("c_adjusted")
D_ADJUSTED = kind("d_adjusted")
LINE_2 = kind("line_2")
LINE_3 = kind("line_3")
LINE_8 = kind("line_8")
LINE_9 = kind("line_9")


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def pre_1986(
    line_1: str,
    a: str = "0",
    b: str = "0",
    c: str = "0",
    d: str = "0",
    ir: str = "0",
    e: str = "0",
    line_8: str = "0",
) -> dict[str, Decimal]:
    """Lines 2, 3 and 9 from the real datasets, for the given line 1, amounts A to E (D at the
    2000 inclusion rate `ir`) and line 8."""
    b_adjusted = only(
        ApplyFraction(
            SOURCE.get("ca/pre_1986_deductions_factor_1988_and_1989", 2025, FRACTION), B, B_ADJUSTED
        ).compute((Artifact(B, D(b)),))
    )
    c_adjusted = only(
        ApplyFraction(
            SOURCE.get("ca/pre_1986_deductions_factor_1990_to_1999", 2025, FRACTION), C, C_ADJUSTED
        ).compute((Artifact(C, D(c)),))
    )
    twice_ir = only(
        ApplyFraction(
            SOURCE.get("ca/net_capital_loss_twice_ir_fraction_2000", 2025, FRACTION), RATE, TWICE
        ).compute((Artifact(RATE, D(ir)),))
    )
    numerator = only(
        CreditAmount(
            SOURCE.get("ca/net_capital_loss_numerator_one_2000", 2025, CREDIT), NUMERATOR
        ).compute(())
    )
    d_adjusted = only(
        ApplyRatioOrZero(
            SOURCE.get("ca/pre_1986_deductions_adjusted_2000_rounding", 2025, ROUNDING_ONLY),
            D_2000,
            NUMERATOR,
            TWICE,
            D_ADJUSTED,
        ).compute((Artifact(D_2000, D(d)), numerator, twice_ir))
    )
    line_2 = only(
        Sum((A, B_ADJUSTED, C_ADJUSTED, D_ADJUSTED, E), LINE_2).compute(
            (Artifact(A, D(a)), b_adjusted, c_adjusted, d_adjusted, Artifact(E, D(e)))
        )
    )
    line_3 = only(Subtract(LINE_1, LINE_2, LINE_3).compute((Artifact(LINE_1, D(line_1)), line_2)))
    line_9 = only(
        LesserOfWithMaximum(
            SOURCE.get("ca/net_capital_losses_additional_deduction_maximum", 2025, AMOUNT),
            (LINE_3, LINE_8),
            LINE_9,
        ).compute((line_3, Artifact(LINE_8, D(line_8))))
    )
    return {
        "b_adjusted": b_adjusted.value,
        "c_adjusted": c_adjusted.value,
        "d_adjusted": d_adjusted.value,
        "line_2": line_2.value,
        "line_3": line_3.value,
        "line_9": line_9.value,
    }


@pytest.mark.parametrize(
    ("family", "numerator", "denominator"),
    [
        # "In 1988 and 1989 x 0.75".
        ("ca/pre_1986_deductions_factor_1988_and_1989", 3, 4),
        # "From 1990 to 1999 x 0.6667".
        ("ca/pre_1986_deductions_factor_1990_to_1999", 2, 3),
    ],
)
def test_2025_the_deduction_factors_are_the_exact_fractions_of_the_printed_factors(
    family: str, numerator: int, denominator: int
) -> None:
    data = SOURCE.get(family, 2025, FRACTION)

    assert data.values == Fraction(numerator, denominator)
    # Line 2 is a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (FORM,)


def test_2025_the_maximum_of_line_9_is_2000_as_printed() -> None:
    # "Enter whichever is less: amount from line 3, line 8, or $2,000."
    data = SOURCE.get("ca/net_capital_losses_additional_deduction_maximum", 2025, AMOUNT)

    assert data.values == Amount(D("2000"))
    # Line 9 is a dollars-and-cents box: half-up to the cent, as the medical expenses ceiling.
    assert data.rounding == CENT
    assert data.sources == (FORM,)


def test_2025_the_row_before_may_23_1985_has_factors_of_one() -> None:
    # Chart A, row "Before May 23, 1985": column B 1 and column F 1.
    for column in ("inclusion_rate", "carry_forward"):
        data = SOURCE.get(f"ca/net_capital_loss_{column}_factor_before_may_23_1985", 2025, FRACTION)

        assert data.values == Fraction(1, 1)
        assert data.rounding == CENT
        assert data.sources == (FORM,)


def test_line_2_adds_amounts_a_to_e_and_line_3_takes_it_off_line_1() -> None:
    # A 500; B 400 x 0.75 = 300.00; C 600 x 2/3 = 400.00; E 100. Line 2 is 500 + 300.00 + 400.00 +
    # 100 = 1300.00 and line 3 is 6000 - 1300.00 = 4700.00.
    figures = pre_1986("6000", a="500", b="400", c="600", e="100")

    assert figures["b_adjusted"] == D("300.00")
    assert figures["c_adjusted"] == D("400.00")
    assert figures["line_2"] == D("1300.00")
    assert figures["line_3"] == D("4700.00")


def test_amounts_a_and_e_are_added_as_they_are() -> None:
    # No multiplier is printed for A (before 1988) or E (2001 to 2024).
    figures = pre_1986("6000", a="500", e="1234.56")

    assert figures["line_2"] == D("1734.56")
    assert figures["line_3"] == D("4265.44")


@pytest.mark.parametrize(
    ("b", "c", "b_adjusted", "c_adjusted"),
    [
        # 0.02 x 3/4 = 0.015, up to 0.02 (half-up); 1.01 x 2/3 = 0.67333..., down to 0.67.
        ("0.02", "1.01", "0.02", "0.67"),
        # 900 x 3/4 = 675.00 and 900 x 2/3 = 600.00 exactly (0.6667 would give 600.03).
        ("900", "900", "675.00", "600.00"),
        # 0.01 x 3/4 = 0.0075, up to 0.01; 0.01 x 2/3 = 0.00666..., up to 0.01.
        ("0.01", "0.01", "0.01", "0.01"),
        # 0.005 x 3/4 = 0.00375, down to 0.00; 0.0075 x 2/3 = 0.005, up to 0.01.
        ("0.005", "0.0075", "0.00", "0.01"),
    ],
)
def test_amounts_b_and_c_round_half_up_to_the_cent_from_exact_fractions(
    b: str, c: str, b_adjusted: str, c_adjusted: str
) -> None:
    figures = pre_1986("1000", b=b, c=c)

    assert figures["b_adjusted"] == D(b_adjusted)
    assert figures["c_adjusted"] == D(c_adjusted)
    assert figures["line_2"] == D(b_adjusted) + D(c_adjusted)


def test_line_3_is_line_1_when_no_capital_gains_deduction_was_claimed() -> None:
    figures = pre_1986("6000")

    assert figures["line_2"] == D("0.00")
    assert figures["line_3"] == D("6000.00")


@pytest.mark.parametrize(
    ("line_1", "a", "line_8", "line_9"),
    [
        # Line 3 is 5500.00 and line 8 is 3000: the $2,000 is the least.
        ("6000", "500", "3000", "2000"),
        # Line 3 is 5500.00 and line 8 is 800: line 8 is the least.
        ("6000", "500", "800", "800"),
        # Line 3 is 1500.00, under line 8 (3000) and the $2,000: line 3 is the least.
        ("2000", "500", "3000", "1500.00"),
        # Line 3 is 0.00: nothing is added, whatever line 8 is.
        ("500", "500", "3000", "0.00"),
        # Line 3 is exactly 2000.00: it is the least, and also the maximum.
        ("2500", "500", "3000", "2000.00"),
    ],
)
def test_line_9_is_the_least_of_line_3_line_8_and_2000(
    line_1: str, a: str, line_8: str, line_9: str
) -> None:
    figures = pre_1986(line_1, a=a, line_8=line_8)

    assert figures["line_9"] == D(line_9)


@pytest.mark.parametrize(
    ("d", "ir", "d_adjusted"),
    [
        # Guide T4037's Example 2: 300 claimed in 2000 at an inclusion rate of 2/3 (66.6666%):
        # 300 x 1/(0.666666 x 2) = 225.000225, 225.00.
        ("300", "0.666666", "225.00"),
        # IR 0.75 (3/4): 1/(0.75 x 2) = 2/3, so 900 x 2/3 = 600.00.
        ("900", "0.75", "600.00"),
        # IR 0.5: 1/(0.5 x 2) = 1, so the amount as it is.
        ("1234.56", "0.5", "1234.56"),
        # IR 0.6667: 300 / 1.3334 = 224.98875..., half-up 224.99.
        ("300", "0.6667", "224.99"),
        # The rate is not entered (0): nothing is added, as the step yields 0.
        ("300", "0", "0.00"),
    ],
)
def test_amount_d_is_the_amount_over_twice_the_2000_inclusion_rate_rounded_half_up_once(
    d: str, ir: str, d_adjusted: str
) -> None:
    figures = pre_1986("6000", d=d, ir=ir)

    assert figures["d_adjusted"] == D(d_adjusted)
    assert figures["line_2"] == D(d_adjusted)
    assert figures["line_3"] == D("6000") - D(d_adjusted)


def test_line_2_adds_amounts_a_to_e_in_the_order_the_form_prints_them() -> None:
    # A 500; B 400 x 0.75 = 300.00; C 600 x 2/3 = 400.00; D 300 x 1/(0.666666 x 2) = 225.00; E 100.
    # Line 2 is 500 + 300.00 + 400.00 + 225.00 + 100 = 1525.00 and line 3 is 6000 - 1525.00 =
    # 4475.00.
    figures = pre_1986("6000", a="500", b="400", c="600", d="300", ir="0.666666", e="100")

    assert figures["line_2"] == D("1525.00")
    assert figures["line_3"] == D("4475.00")


def test_2025_amount_d_rounds_half_up_to_the_cent_with_no_values() -> None:
    # Row "In 2000" (D) x 1/(IR x 2): the one rounding of the cell.
    data = SOURCE.get("ca/pre_1986_deductions_adjusted_2000_rounding", 2025, ROUNDING_ONLY)

    assert data.rounding == CENT
    assert data.sources == (FORM,)
