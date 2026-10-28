"""The 2025 net capital losses of other years figures, checked against CRA's forms.

Form T1436 (Capital Gains Worksheet, 2025; CRA publishes no .txt, so the quotes are from the text
extracted from the PDF), "Line 25300 - Net capital loss of other years (if you have pre-1986
capital loss balance)", "Chart A - Adjustment calculation for carry-forward losses": a row for each
printed period, with column (B) "Adjustment factor (for the inclusion rate)" and column (F)
"Adjustment factor (for carry-forward losses)". The rows wired are "Before May 23, 1985" (1 and
1), "After May 22, 1985, and before 1988" (1 and 1), "In 1988 and 1989" (0.75 and 1.33), "After
1989 and before 2000" (0.6667 and 1.5) and "After 2000 and before 2025" (1 and 1). The
form prints 0.75, 0.6667, 1.33 and 1.5 for 3/4, 2/3, 4/3 and 3/2 rounded for print, so each factor
is a `fraction` dataset holding the exact fraction (3/4 times 4/3 is 1, where 0.75 times 1.33 is
0.9975) and a factor of 1 is 1/1. Columns (C) and (G) are dollars-and-cents boxes, so each
dataset's rule rounds half-up to the cent, the owner's decision, as the form states no rounding
rule. Guide T4037 (2025): "You have to apply net capital losses of earlier years before you apply
net capital losses of later years."

The line 4 to 7 and column D, E and G steps are the manifest's, from existing capabilities and
without a dataset: this module builds them from the same datasets with made-up kinds and pins the
chain, the way the form prints it: column C is column A multiplied by column B, line 4 their sum,
line 6 the lesser of line 4 and the taxable capital gains (line 5), line 7 the claim, refused when
above line 6, column D the lesser of column C and what is left of line 13 (the claim) after the
older rows, column E column C less column D, column G column E multiplied by column F.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FORM = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1436/t1436-25e.pdf"
ROWS = ("before_may_23_1985", "1985_to_1987", "1988_and_1989", "1990_to_1999", "2001_to_2024")


def factor(column: str, row: str) -> str:
    """The family of the row's column B ("inclusion_rate") or column F ("carry_forward") factor."""
    return f"ca/net_capital_loss_{column}_factor_{row}"


# Made up for this test and not registered: column A to G per row, lines 4 and 6, the claim and
# line 7, and what is left of line 13 after each row.
def kind(name: str) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/{name}", Decimal)


TAXABLE_GAINS = kind("taxable_gains")
TOTAL = kind("line_4")
AVAILABLE = kind("line_6")
CLAIM = kind("claim")
LINE_7 = kind("line_7")


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def chart_a(losses: dict[str, str], taxable_gains: str, claim: str) -> dict[str, Decimal]:
    """Chart A's columns C, D, E and G per row, and lines 4, 6 and 7, from the real datasets.

    `losses` is column A by row (a row left out is 0); the rows are applied oldest first.
    """
    column_c: dict[str, Artifact[Decimal]] = {}
    for row in ROWS:
        column_a = Artifact(kind(f"a_{row}"), D(losses.get(row, "0")))
        column_c[row] = only(
            ApplyFraction(
                SOURCE.get(factor("inclusion_rate", row), 2025, FRACTION),
                kind(f"a_{row}"),
                kind(f"c_{row}"),
            ).compute((column_a,))
        )
    line_4 = only(
        Sum(tuple(kind(f"c_{row}") for row in ROWS), TOTAL).compute(tuple(column_c.values()))
    )
    line_6 = only(
        LesserOf((TOTAL, TAXABLE_GAINS), AVAILABLE).compute(
            (line_4, Artifact(TAXABLE_GAINS, D(taxable_gains)))
        )
    )
    line_7 = only(AtMost(CLAIM, AVAILABLE, LINE_7).compute((Artifact(CLAIM, D(claim)), line_6)))
    result: dict[str, Decimal] = {"line_4": line_4.value, "line_6": line_6.value}
    result["line_7"] = line_7.value
    left = line_7
    for row in ROWS:
        applied = only(
            LesserOf((kind(f"c_{row}"), left.kind), kind(f"d_{row}")).compute((column_c[row], left))
        )
        left = only(
            Subtract(left.kind, kind(f"d_{row}"), kind(f"left_{row}")).compute((left, applied))
        )
        column_e = only(
            Subtract(kind(f"c_{row}"), kind(f"d_{row}"), kind(f"e_{row}")).compute(
                (column_c[row], applied)
            )
        )
        column_g = only(
            ApplyFraction(
                SOURCE.get(factor("carry_forward", row), 2025, FRACTION),
                kind(f"e_{row}"),
                kind(f"g_{row}"),
            ).compute((column_e,))
        )
        result[f"c_{row}"] = column_c[row].value
        result[f"d_{row}"] = applied.value
        result[f"e_{row}"] = column_e.value
        result[f"g_{row}"] = column_g.value
    return result


@pytest.mark.parametrize(
    ("row", "numerator", "denominator"),
    [
        ("before_may_23_1985", 1, 1),
        ("1985_to_1987", 1, 1),
        ("1988_and_1989", 3, 4),
        ("1990_to_1999", 2, 3),
        ("2001_to_2024", 1, 1),
    ],
)
def test_2025_column_b_is_the_exact_fraction_of_the_printed_factor(
    row: str, numerator: int, denominator: int
) -> None:
    # Column (B) prints 1, 0.75, 0.6667 and 1.
    data = SOURCE.get(factor("inclusion_rate", row), 2025, FRACTION)

    assert data.values == Fraction(numerator, denominator)
    # Column (C), a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (FORM,)


@pytest.mark.parametrize(
    ("row", "numerator", "denominator"),
    [
        ("before_may_23_1985", 1, 1),
        ("1985_to_1987", 1, 1),
        ("1988_and_1989", 4, 3),
        ("1990_to_1999", 3, 2),
        ("2001_to_2024", 1, 1),
    ],
)
def test_2025_column_f_is_the_exact_fraction_of_the_printed_factor(
    row: str, numerator: int, denominator: int
) -> None:
    # Column (F) prints 1, 1.33, 1.5 and 1.
    data = SOURCE.get(factor("carry_forward", row), 2025, FRACTION)

    assert data.values == Fraction(numerator, denominator)
    # Column (G), a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (FORM,)


def test_the_worked_example_of_the_chart() -> None:
    # A 1995 loss of 3000 (row "After 1989 and before 2000", factor 2/3) gives column C 2000.00; a
    # 2010 loss of 1000 (row "After 2000 and before 2025", factor 1) gives 1000.00. Column C total
    # 3000.00; the taxable capital gains (line 12700) are 2500, so line 6 is 2500.00. A claim of
    # 2500 takes 2000.00 from the 1995 row and 500.00 from the 2010 row: column E is 0.00 and
    # 500.00 and column G is 0.00 and 500.00.
    chart = chart_a({"1990_to_1999": "3000", "2001_to_2024": "1000"}, "2500", "2500")

    assert chart["c_1990_to_1999"] == D("2000.00")
    assert chart["c_2001_to_2024"] == D("1000.00")
    assert chart["line_4"] == D("3000.00")
    assert chart["line_6"] == D("2500.00")
    assert chart["line_7"] == D("2500")
    assert chart["d_1985_to_1987"] == D("0.00")
    assert chart["d_1988_and_1989"] == D("0.00")
    assert chart["d_1990_to_1999"] == D("2000.00")
    assert chart["d_2001_to_2024"] == D("500.00")
    assert chart["e_1990_to_1999"] == D("0.00")
    assert chart["e_2001_to_2024"] == D("500.00")
    assert chart["g_1990_to_1999"] == D("0.00")
    assert chart["g_2001_to_2024"] == D("500.00")


def test_the_total_of_column_d_is_line_13_the_claim() -> None:
    # Note (4): "The total for column D must equal the amount from line 13." Line 13 is line 7.
    chart = chart_a(
        {
            "1985_to_1987": "100",
            "1988_and_1989": "400",
            "1990_to_1999": "600",
            "2001_to_2024": "500",
        },
        "2500",
        "700",
    )

    applied = [chart[f"d_{row}"] for row in ROWS]
    # The row "Before May 23, 1985" has no loss: 0.00.
    assert applied == [D("0.00"), D("100.00"), D("300.00"), D("300.00"), D("0.00")]
    assert sum(applied) == chart["line_7"] == D("700")


@pytest.mark.parametrize(
    ("row", "loss", "column_c", "column_g"),
    [
        # 0.75 x 1.33 is 0.9975 on the form's printed factors; 3/4 x 4/3 is exactly 1.
        ("1988_and_1989", "900", "675.00", "900.00"),
        # 2/3 x 3/2 is exactly 1 where 0.6667 x 1.5 is 1.00005.
        ("1990_to_1999", "900", "600.00", "900.00"),
        # Half-up to the cent at C (0.015 up to 0.02) and at G (0.02666... up to 0.03).
        ("1988_and_1989", "0.02", "0.02", "0.03"),
        # 1.01 x 2/3 is 0.67333..., down to 0.67; 0.67 x 3/2 is 1.005, up to 1.01.
        ("1990_to_1999", "1.01", "0.67", "1.01"),
        ("before_may_23_1985", "1234.56", "1234.56", "1234.56"),
        ("1985_to_1987", "1234.56", "1234.56", "1234.56"),
        ("2001_to_2024", "1234.56", "1234.56", "1234.56"),
    ],
)
def test_columns_c_and_g_round_half_up_to_the_cent_from_exact_fractions(
    row: str, loss: str, column_c: str, column_g: str
) -> None:
    # Nothing claimed (taxable capital gains of 0, claim 0), so column D is 0.00 and column E is
    # column C.
    chart = chart_a({row: loss}, "0", "0")

    assert chart[f"c_{row}"] == D(column_c)
    assert chart[f"e_{row}"] == D(column_c)
    assert chart[f"g_{row}"] == D(column_g)


@pytest.mark.parametrize(
    ("gains", "claim", "line_6"),
    [
        # The lesser of line 4 (3000.00) and line 5.
        ("2500", "2500", "2500.00"),
        ("3000", "3000", "3000.00"),
        ("10000", "3000", "3000.00"),
    ],
)
def test_line_6_is_the_lesser_of_the_total_of_column_c_and_the_taxable_capital_gains(
    gains: str, claim: str, line_6: str
) -> None:
    chart = chart_a({"1990_to_1999": "3000", "2001_to_2024": "1000"}, gains, claim)

    assert chart["line_6"] == D(line_6)
    assert chart["line_7"] == D(claim)


@pytest.mark.parametrize(("gains", "claim"), [("2500", "2500.01"), ("10000", "3000.01")])
def test_a_claim_above_line_6_is_refused_naming_both_kinds(gains: str, claim: str) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        chart_a({"1990_to_1999": "3000", "2001_to_2024": "1000"}, gains, claim)

    assert str(raised.value).startswith(f"ex/claim {claim} is above ex/line_6 ")
