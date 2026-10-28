"""The 2025 Ontario political contribution tax credit figures, checked against CRA's ON479 forms.

2025 Form ON479 (form 5006-TC), "Ontario political contribution tax credit": "Line 15 and line
63100: Ontario political contributions made in 2025"; "Line 16: Enter $1,666.82 if your total
contributions are $3,793 or more. If not, use Worksheet ON479. (maximum $1,666.82)". 2025 Worksheet
ON479 (form 5006-D1), "Line 16 - Ontario political contribution tax credit": three alternative
columns, "Column 1: Line 63110 is $500.05 or less", "Column 2: Line 63110 is more than $500.05 but
not more than $1,666.82" and "Column 3: Line 63110 is more than $1,666.82", each with line 1 "Enter
your total political contributions from line 63110 of your Form ON479."; line 2 a printed constant
(0.00, 500.05, 1,666.82); line 3 "Line 1 minus line 2 (cannot be negative)"; line 4 "Rate" (75%,
50%, 33.33%); line 5 "Line 3 multiplied by the percentage from line 4"; line 6 a printed constant
(0.00, 375.03, 958.41); line 7 "Line 5 plus line 6 Enter this amount on line 16 of your Form
ON479.".

Every printed figure is a dataset as printed, none derived: each line 2 and line 6 a constant (the
`credit` kind, claimed whole), each line 4 a rate, and the form's maximum a plain cap (the `amount`
kind). Lines 5 and 16 are dollars-and-cents boxes, so each is rounded half-up to the cent. The
constants are cut, not rounded, by the form (75% x 500.05 = 375.0375 is printed 375.03), so line 6
is not the sum of the bands below it. The column that applies is picked by the contributions
(line 1): column 1 when they are at most the column 2 line 2 constant, column 2 when they are over
that but at most the column 3 line 2 constant, column 3 otherwise; the maximum then caps the pick.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.capped_amount import CappedAmount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
ON479_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tc/5006-tc-25e.txt"
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d1/5006-d1-25e.txt"
MAXIMUM = "ca-on/political_credit_maximum"


def family(column: int, line: int) -> str:
    return f"ca-on/political_credit_column_{column}_line_{line}"


# Made up for this test and not registered: the contributions (line 1), each column's lines 2, 3,
# 5, 6 and 7, the pick (before the maximum) and line 16.
CONTRIBUTIONS = ArtifactKind("ex/contributions", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/credit_before_maximum", Decimal)
LINE_16 = ArtifactKind("ex/credit", Decimal)


def line(column: int, number: int) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/column_{column}_line_{number}", Decimal)


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def column_line_7(column: int, contributions: str) -> Decimal:
    """The column's line 7 from the real datasets: lines 2 to 6 as the form prints them."""
    line_2 = only(
        CreditAmount(SOURCE.get(family(column, 2), 2025, CREDIT), line(column, 2)).compute(())
    )
    line_6 = only(
        CreditAmount(SOURCE.get(family(column, 6), 2025, CREDIT), line(column, 6)).compute(())
    )
    line_3 = only(
        SubtractNotBelowZero(CONTRIBUTIONS, line(column, 2), line(column, 3)).compute(
            (Artifact(CONTRIBUTIONS, D(contributions)), line_2)
        )
    )
    line_5 = only(
        ApplyRate(
            SOURCE.get(family(column, 4), 2025, RATE), line(column, 3), line(column, 5)
        ).compute((line_3,))
    )
    return only(
        Sum((line(column, 5), line(column, 6)), line(column, 7)).compute((line_5, line_6))
    ).value


def line_16(contributions: str) -> Decimal:
    """Line 16 for the contributions: the pick of the three columns, capped by the maximum."""
    columns = tuple(Artifact(line(c, 7), column_line_7(c, contributions)) for c in (1, 2, 3))
    limits = tuple(
        only(CreditAmount(SOURCE.get(family(c, 2), 2025, CREDIT), line(c, 2)).compute(()))
        for c in (2, 3)
    )
    picked = only(
        ChooseByRange(
            CONTRIBUTIONS,
            line(2, 2),
            line(3, 2),
            line(1, 7),
            line(2, 7),
            line(3, 7),
            BEFORE_MAXIMUM,
        ).compute((Artifact(CONTRIBUTIONS, D(contributions)), *limits, *columns))
    )
    return only(
        CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, LINE_16).compute((picked,))
    ).value


@pytest.mark.parametrize(
    ("column", "constant"),
    [(1, "0.00"), (2, "500.05"), (3, "1666.82")],
)
def test_2025_line_2_is_the_printed_constant(column: int, constant: str) -> None:
    data = SOURCE.get(family(column, 2), 2025, CREDIT)

    assert data.values == Credit(amount=D(constant))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


@pytest.mark.parametrize(
    ("column", "rate"),
    [(1, "0.75"), (2, "0.5"), (3, "0.3333")],
)
def test_2025_line_4_is_the_printed_rate(column: int, rate: str) -> None:
    data = SOURCE.get(family(column, 4), 2025, RATE)

    assert data.values == Rate(D(rate))
    # Line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


@pytest.mark.parametrize(
    ("column", "constant"),
    [(1, "0.00"), (2, "375.03"), (3, "958.41")],
)
def test_2025_line_6_is_the_printed_constant(column: int, constant: str) -> None:
    data = SOURCE.get(family(column, 6), 2025, CREDIT)

    assert data.values == Credit(amount=D(constant))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_maximum_is_1666_82() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("1666.82"))
    # ON479 line 16, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (ON479_TEXT,)


@pytest.mark.parametrize(
    ("contributions", "column_1", "column_2", "column_3"),
    [
        # Column 1: 75% of the contributions; columns 2 and 3 on 0 over their line 2: only line 6.
        ("300", "225.00", "375.03", "958.41"),
        # 1,000: column 2 line 3 = 499.95, line 5 = 249.975, up to 249.98, line 7 = 625.01.
        ("1000", "750.00", "625.01", "958.41"),
        # 3,000: column 3 line 3 = 1,333.18, line 5 = 444.3494, down to 444.35, line 7 = 1,402.76.
        ("3000", "2250.00", "1625.01", "1402.76"),
        ("0", "0.00", "375.03", "958.41"),
    ],
)
def test_each_column_is_built_as_the_form_prints_it(
    contributions: str, column_1: str, column_2: str, column_3: str
) -> None:
    assert column_line_7(1, contributions) == D(column_1)
    assert column_line_7(2, contributions) == D(column_2)
    assert column_line_7(3, contributions) == D(column_3)


@pytest.mark.parametrize(
    ("contributions", "credit"),
    [
        # The acceptance figures.
        ("0", "0.00"),
        ("300", "225.00"),
        ("1000", "625.01"),
        ("3000", "1402.76"),
        ("3793", "1666.82"),
        ("4000", "1666.82"),
        # Column 1 at its upper end: 75% x 500.05 = 375.0375, up to 375.04 (the form prints the
        # cut 375.03 as column 2's line 6, but column 1's own line 5 is rounded).
        ("500.05", "375.04"),
        # A cent over: column 2 line 3 = 0.01, line 5 = 0.005, up to 0.01, line 7 = 375.04.
        ("500.06", "375.04"),
        # Column 2 at its upper end: line 3 = 1,166.77, line 5 = 583.385, up to 583.39, line 7 =
        # 958.42; a cent over, column 3 gives 958.41, as its printed constant is cut.
        ("1666.82", "958.42"),
        ("1666.83", "958.41"),
        # Just under the $3,793 the form names: column 3 line 3 = 2,125.18, line 5 = 708.32, line 7
        # = 1,666.73, a cent under the maximum.
        ("3792", "1666.73"),
    ],
)
def test_line_16_is_the_applicable_column_capped_at_the_maximum(
    contributions: str, credit: str
) -> None:
    assert line_16(contributions) == D(credit)
